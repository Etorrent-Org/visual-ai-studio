from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from visual_ai_studio.domain.models import (
    Artifact,
    Brief,
    HumanConfirmations,
    Project,
    ValidationReport,
)
from visual_ai_studio.domain.statuses import (
    ArtifactType,
)
from visual_ai_studio.domain.validators import (
    sha256_file,
)
from visual_ai_studio.infrastructure.webhook_client import (
    WebhookClient,
    build_metadata,
    idempotency_key,
)


def submission_data(
    tmp_path: Path,
) -> tuple[
    Project,
    list[Artifact],
    ValidationReport,
    HumanConfirmations,
]:
    project = Project(
        title="Projet test",
        slug="projet-test",
        brief=Brief(
            title="Projet test",
            collection="Campagne demo",
            raw_idea="Une scène test",
        ),
    )

    definitions = [
        (
            ArtifactType.IMAGE,
            "result.png",
            b"synthetic-image",
        ),
        (
            ArtifactType.TEXT,
            "description.md",
            b"# Resultat",
        ),
        (
            ArtifactType.METADATA,
            "metadata.json",
            b'{"schema_version":"1.0"}',
        ),
    ]

    artifacts: list[Artifact] = []

    for kind, filename, content in definitions:
        path = tmp_path / filename
        path.write_bytes(content)

        artifacts.append(
            Artifact(
                project_id=project.id,
                artifact_type=kind,
                filename=filename,
                local_path=path,
                sha256=sha256_file(path),
            )
        )

    report = ValidationReport(
        artifacts=artifacts
    )

    confirmations = HumanConfirmations(
        approved=True
    )

    return (
        project,
        artifacts,
        report,
        confirmations,
    )


def test_metadata_is_generic(
    tmp_path: Path,
) -> None:
    data = submission_data(
        tmp_path
    )

    metadata = build_metadata(
        *data
    )

    assert (
        metadata["source"]
        == "visual-ai-studio"
    )

    assert "notion" not in metadata

    assert (
        metadata["output"]["mode"]
        == "pinterest"
    )


def test_multipart_payload_and_success(
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        captured["headers"] = (
            request.headers
        )
        captured["body"] = (
            request.read()
        )

        return httpx.Response(
            200,
            json={
                "status": "success",
                "execution_id": "exec-123",
                "remote_url": (
                    "https://example.test/result"
                ),
            },
        )

    project, artifacts, report, confirmations = (
        submission_data(tmp_path)
    )

    client = WebhookClient(
        "https://automation.test/webhook",
        "X-Token",
        "secret-value",
        transport=httpx.MockTransport(
            handler
        ),
    )

    outcome = client.submit(
        project,
        artifacts,
        report,
        confirmations,
    )

    assert outcome.status == "success"

    assert (
        outcome.execution_id
        == "exec-123"
    )

    assert (
        outcome.remote_url
        == "https://example.test/result"
    )

    assert (
        captured["headers"]["X-Token"]
        == "secret-value"
    )

    assert (
        captured["headers"]["Idempotency-Key"]
        == idempotency_key(
            project.id,
            1,
        )
    )

    assert (
        b'name="metadata"'
        in captured["body"]
    )

    assert (
        b'name="artifact_0"'
        in captured["body"]
    )

    assert (
        b'name="artifact_1"'
        in captured["body"]
    )

    assert (
        b"local_path"
        not in captured["body"]
    )


def test_business_error_is_not_retryable(
    tmp_path: Path,
) -> None:
    def handler(
        _request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            409,
            json={
                "status": "error",
                "message": "Refus métier",
                "retryable": False,
            },
        )

    data = submission_data(
        tmp_path
    )

    outcome = WebhookClient(
        "https://automation.test/webhook",
        "X-Token",
        "",
        transport=httpx.MockTransport(
            handler
        ),
    ).submit(*data)

    assert outcome.status == "error"
    assert outcome.retryable is False
    assert outcome.http_status == 409


def test_timeout_has_unknown_status(
    tmp_path: Path,
) -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        raise httpx.ReadTimeout(
            "timeout",
            request=request,
        )

    data = submission_data(
        tmp_path
    )

    outcome = WebhookClient(
        "https://automation.test/webhook",
        "X-Token",
        "",
        transport=httpx.MockTransport(
            handler
        ),
    ).submit(*data)

    assert outcome.unknown is True
    assert outcome.retryable is True


def test_invalid_json_is_explicit(
    tmp_path: Path,
) -> None:
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            text="not json",
        )
    )

    data = submission_data(
        tmp_path
    )

    outcome = WebhookClient(
        "https://automation.test/webhook",
        "X-Token",
        "",
        transport=transport,
    ).submit(*data)

    assert "JSON valide" in outcome.message


def test_idempotency_is_stable_per_project_version() -> None:
    project = Project()

    assert (
        idempotency_key(
            project.id,
            1,
        )
        == idempotency_key(
            project.id,
            1,
        )
    )

    assert (
        idempotency_key(
            project.id,
            1,
        )
        != idempotency_key(
            project.id,
            2,
        )
    )