from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import httpx

from visual_ai_studio.domain.models import (
    Artifact,
    HumanConfirmations,
    Project,
    SubmissionOutcome,
    ValidationReport,
)


def idempotency_key(
    project_id: Any,
    version: int,
) -> str:
    value = f"{project_id}:{version}"

    return hashlib.sha256(value.encode()).hexdigest()


def build_metadata(
    project: Project,
    artifacts: list[Artifact],
    report: ValidationReport,
    confirmations: HumanConfirmations,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "source": "visual-ai-studio",
        "project": {
            "id": str(project.id),
            "version": project.version,
            "title": project.title,
            "slug": project.slug,
        },
        "output": {
            "mode": project.brief.mode.value,
            "width": project.brief.target_width,
            "height": project.brief.target_height,
            "aspect_ratio": project.brief.aspect_ratio,
            "collection": project.brief.collection,
            "style": project.brief.style,
        },
        "artifacts": [
            {
                "type": item.artifact_type.value,
                "filename": item.filename,
                "sha256": item.sha256,
                "width": item.width,
                "height": item.height,
            }
            for item in artifacts
        ],
        "validation": {
            "automatic_checks_passed": (report.automatic_checks_passed),
            "human_approved": (confirmations.all_confirmed),
            "issues": [issue.model_dump() for issue in report.issues],
        },
    }


def _mime_type(
    filename: str,
) -> str:
    suffix = Path(filename).suffix.lower()

    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".md": "text/markdown; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".json": "application/json",
    }

    return mapping.get(
        suffix,
        "application/octet-stream",
    )


class WebhookClient:
    def __init__(
        self,
        webhook_url: str,
        auth_header_name: str,
        secret: str,
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.webhook_url = webhook_url
        self.auth_header_name = auth_header_name
        self.secret = secret
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    def submit(
        self,
        project: Project,
        artifacts: list[Artifact],
        report: ValidationReport,
        confirmations: HumanConfirmations,
    ) -> SubmissionOutcome:
        if not report.automatic_checks_passed or not confirmations.all_confirmed:
            return SubmissionOutcome(
                status="error",
                message=("Le résultat doit être validé avant l'envoi."),
            )

        key = idempotency_key(
            project.id,
            project.version,
        )

        metadata = build_metadata(
            project,
            artifacts,
            report,
            confirmations,
        )

        headers = {"Idempotency-Key": key}

        if self.secret:
            headers[self.auth_header_name] = self.secret

        opened: list[Any] = []

        files: dict[
            str,
            tuple[str, Any, str],
        ] = {}

        try:
            for index, artifact in enumerate(artifacts):
                stream = Path(artifact.local_path).open("rb")  # noqa: SIM115

                opened.append(stream)

                files[f"artifact_{index}"] = (
                    artifact.filename,
                    stream,
                    _mime_type(artifact.filename),
                )

            files["metadata"] = (
                "metadata.json",
                json.dumps(
                    metadata,
                    ensure_ascii=False,
                ).encode("utf-8"),
                "application/json; charset=utf-8",
            )

            with httpx.Client(
                timeout=self.timeout_seconds,
                transport=self.transport,
                follow_redirects=False,
            ) as client:
                response = client.post(
                    self.webhook_url,
                    headers=headers,
                    files=files,
                )

        except httpx.TimeoutException:
            return SubmissionOutcome(
                status="unknown",
                retryable=True,
                unknown=True,
                message=("Délai dépassé : le statut distant est inconnu."),
            )

        except (
            httpx.NetworkError,
            OSError,
        ) as exc:
            return SubmissionOutcome(
                status="error",
                retryable=True,
                message=str(exc),
            )

        finally:
            for stream in opened:
                stream.close()

        try:
            payload = response.json()

        except ValueError:
            return SubmissionOutcome(
                status="error",
                retryable=(response.status_code >= 500),
                message=("La réponse du webhook n'est pas un JSON valide."),
                http_status=(response.status_code),
            )

        if not isinstance(
            payload,
            dict,
        ):
            return SubmissionOutcome(
                status="error",
                message=("La réponse JSON du webhook n'est pas un objet."),
                http_status=(response.status_code),
            )

        remote_url = str(payload.get("remote_url") or "")

        success_status = response.is_success and payload.get("status") in {
            "success",
            "duplicate",
        }

        if success_status:
            return SubmissionOutcome(
                status="success",
                execution_id=str(
                    payload.get(
                        "execution_id",
                        "",
                    )
                ),
                remote_url=remote_url,
                message=str(
                    payload.get(
                        "message",
                        "Envoi terminé.",
                    )
                ),
                http_status=(response.status_code),
                duplicate_avoided=(
                    payload.get("status") == "duplicate" or bool(payload.get("duplicate_avoided"))
                ),
            )

        return SubmissionOutcome(
            status="error",
            retryable=bool(
                payload.get(
                    "retryable",
                    response.status_code >= 500,
                )
            ),
            execution_id=str(
                payload.get(
                    "execution_id",
                    "",
                )
            ),
            remote_url=remote_url,
            message=str(
                payload.get(
                    "message",
                    (f"Erreur webhook HTTP {response.status_code}."),
                )
            ),
            http_status=(response.status_code),
        )

    def test_connection(
        self,
    ) -> SubmissionOutcome:
        headers: dict[str, str] = {}

        if self.secret:
            headers[self.auth_header_name] = self.secret

        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.get(
                    self.webhook_url,
                    headers=headers,
                    params={"probe": "true"},
                )

            status = "error"

            if response.is_success:
                status = "success"

            return SubmissionOutcome(
                status=status,
                retryable=(response.status_code >= 500),
                http_status=(response.status_code),
                message=(f"Réponse webhook HTTP {response.status_code}."),
            )

        except httpx.HTTPError as exc:
            return SubmissionOutcome(
                status="error",
                retryable=True,
                message=str(exc),
            )
