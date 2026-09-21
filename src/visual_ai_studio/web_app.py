from __future__ import annotations

import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, ValidationError
from starlette.background import BackgroundTask

from visual_ai_studio.application import ApplicationContext, build_application
from visual_ai_studio.domain.models import (
    Artifact,
    Brief,
    HumanConfirmations,
    Project,
    ValidationReport,
)
from visual_ai_studio.domain.normalization import find_close_values, normalize_value
from visual_ai_studio.domain.output_modes import OUTPUT_MODE_PRESETS
from visual_ai_studio.domain.statuses import ArtifactType, ProjectStatus
from visual_ai_studio.domain.validators import validate_artifact_package
from visual_ai_studio.infrastructure.automation_runs import AutomationRunRepository
from visual_ai_studio.infrastructure.settings import AppSettings
from visual_ai_studio.infrastructure.webhook_client import WebhookClient
from visual_ai_studio.services.export_service import export_project_bundle
from visual_ai_studio.services.submission_service import SubmissionService, can_submit

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_UPLOAD_EXTENSIONS = IMAGE_EXTENSIONS | {".md", ".txt", ".json"}


class BriefRequest(BaseModel):
    brief: Brief
    confirm_new_collection: bool = False


class ApprovalRequest(BaseModel):
    approved: bool = False


class SettingsRequest(BaseModel):
    projects_dir: str | None = None
    webhook_url: str | None = None
    auth_header_name: str | None = None
    webhook_secret: str | None = None
    timeout_seconds: float | None = Field(default=None, ge=1.0, le=300.0)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _safe_filename(filename: str | None) -> str:
    cleaned = Path(filename or "fichier").name.strip()
    return cleaned or "fichier"


def _project_payload(project: Project) -> dict[str, Any]:
    return project.model_dump(mode="json")


def _artifact_payload(project: Project, artifact: Artifact) -> dict[str, Any]:
    payload = artifact.model_dump(mode="json", exclude={"local_path"})
    payload["preview_url"] = (
        f"/api/projects/{project.id}/artifacts/{artifact.id}/content"
        if artifact.artifact_type is ArtifactType.IMAGE
        else ""
    )
    return payload


def _report_payload(
    project: Project,
    report: ValidationReport,
    approved: bool = False,
) -> dict[str, Any]:
    confirmations = HumanConfirmations(approved=approved)
    return {
        "artifacts": [_artifact_payload(project, item) for item in report.artifacts],
        "issues": [item.model_dump(mode="json") for item in report.issues],
        "automatic_checks_passed": report.automatic_checks_passed,
        "ready": can_submit(report, confirmations),
    }


def _apply_environment_settings(context: ApplicationContext, data_root: Path) -> None:
    settings_file_exists = context.settings_store.path.exists()
    values = context.settings.model_dump(mode="python")

    # Un chemin Windows enregistré par l'ancienne application n'est pas utilisable
    # directement dans le conteneur. Le volume /data devient alors la racine locale.
    current_projects_dir = Path(str(values["projects_dir"]))
    if not _is_within(current_projects_dir, data_root):
        current_projects_dir = data_root / "projects"

    current_projects_dir.mkdir(parents=True, exist_ok=True)
    values["projects_dir"] = current_projects_dir

    env_mapping: dict[str, tuple[str, type[Any]]] = {
        "VISUAL_AI_WEBHOOK_URL": ("webhook_url", str),
        "VISUAL_AI_AUTH_HEADER": ("auth_header_name", str),
        "VISUAL_AI_AGENT_URL": ("agent_url", str),
        "VISUAL_AI_TIMEOUT_SECONDS": ("timeout_seconds", float),
        "VISUAL_AI_MAX_FILE_SIZE_MB": ("max_file_size_mb", int),
    }

    for env_name, (field_name, converter) in env_mapping.items():
        raw_value = os.getenv(env_name, "").strip()
        current_value = values.get(field_name)
        if raw_value and (
            not settings_file_exists
            or current_value in (None, "", AppSettings.model_fields[field_name].default)
        ):
            values[field_name] = converter(raw_value)

    context.settings = AppSettings.model_validate(values)
    context.artifact_service.projects_dir = context.settings.projects_dir
    context.artifact_service.max_bytes = context.settings.max_file_size_mb * 1024 * 1024

    # On persiste uniquement le chemin de stockage normalisé. Les variables
    # d'environnement restent des surcharges runtime et ne sont pas écrites.
    stored = context.settings_store.load().model_copy(
        update={"projects_dir": context.settings.projects_dir},
        deep=True,
    )
    context.settings_store.save(stored)


def _webhook_secret(context: ApplicationContext) -> str:
    stored = context.settings_store.get_secret()
    if stored:
        return stored
    return os.getenv("VISUAL_AI_WEBHOOK_SECRET", "").strip()


def _settings_payload(context: ApplicationContext, root: Path) -> dict[str, Any]:
    return {
        "projects_dir": str(context.settings.projects_dir),
        "webhook_configured": bool(context.settings.webhook_url),
        "webhook_url": str(context.settings.webhook_url or ""),
        "auth_header_name": context.settings.auth_header_name,
        "webhook_secret_configured": bool(_webhook_secret(context)),
        "timeout_seconds": context.settings.timeout_seconds,
        "agent_url": str(context.settings.agent_url or ""),
        "max_file_size_mb": context.settings.max_file_size_mb,
        "storage_root": str(root),
    }


def _prepare_collection(
    context: ApplicationContext,
    brief: Brief,
    confirm_new_collection: bool,
) -> Brief:
    if not brief.collection:
        return brief

    values = context.project_service.collections()
    exact = next(
        (
            item
            for item in values
            if item.normalized_value == normalize_value(brief.collection)
        ),
        None,
    )
    if exact:
        brief.collection = exact.value
        brief.collection_is_new = exact.is_new
        return brief

    similar = find_close_values(brief.collection, [item.value for item in values])
    if similar and not confirm_new_collection:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "similar_collection",
                "message": "Une collection proche existe déjà.",
                "similar": similar,
            },
        )

    try:
        reference, _ = context.project_service.add_collection(brief.collection)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    brief.collection = reference.value
    brief.collection_is_new = True
    return brief


def _resolve_artifact_path(
    context: ApplicationContext,
    project: Project,
    artifact: Artifact,
) -> Path:
    stored = Path(artifact.local_path)
    if stored.is_file():
        return stored

    # Compatibilité avec les chemins absolus Windows présents dans la base
    # historique lorsque le dossier projects est monté dans Docker.
    fallback = (
        context.settings.projects_dir
        / str(project.id)
        / f"v{project.version}"
        / "artifacts"
        / artifact.filename
    )
    return fallback


def _report_from_storage(
    context: ApplicationContext,
    project: Project,
) -> ValidationReport | None:
    stored_artifacts = context.artifact_repository.list_for_project(project.id)
    if not stored_artifacts:
        return None

    paths = [_resolve_artifact_path(context, project, item) for item in stored_artifacts]
    validated = validate_artifact_package(
        project.id,
        paths,
        expected_width=project.brief.target_width,
        expected_height=project.brief.target_height,
    )
    resolved_artifacts = [
        item.model_copy(update={"local_path": path}, deep=True)
        for item, path in zip(stored_artifacts, paths, strict=True)
    ]
    return ValidationReport(
        artifacts=resolved_artifacts,
        issues=validated.issues,
        markdown_metadata=validated.markdown_metadata,
    )


async def _store_upload(upload: UploadFile, target: Path, max_bytes: int) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with target.open("wb") as stream:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                stream.close()
                target.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"{target.name} dépasse la limite de taille autorisée.",
                )
            stream.write(chunk)
    await upload.close()
    return target


def create_app(data_root: Path | None = None, web_dist: Path | None = None) -> FastAPI:
    root = Path(data_root or os.getenv("VISUAL_AI_DATA_DIR", "").strip() or "/data").resolve()
    root.mkdir(parents=True, exist_ok=True)

    context = build_application(root)
    _apply_environment_settings(context, root)

    app = FastAPI(title="Visual AI Studio", version="0.3.0")
    app.state.context = context
    app.state.data_root = root
    app.state.reports: dict[str, ValidationReport] = {}

    def get_project(project_id: UUID) -> Project:
        project = context.project_service.get(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Projet introuvable.")
        return project

    def get_report(project: Project) -> ValidationReport | None:
        cached = app.state.reports.get(str(project.id))
        if cached is not None:
            return cached
        report = _report_from_storage(context, project)
        if report is not None:
            app.state.reports[str(project.id)] = report
        return report

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/bootstrap")
    def bootstrap() -> dict[str, Any]:
        return {
            "projects": [
                _project_payload(project)
                for project in context.project_service.list_projects()
            ],
            "collections": [
                item.model_dump(mode="json")
                for item in context.project_service.collections()
            ],
            "styles": context.project_service.styles(),
            "settings": _settings_payload(context, root),
            "statuses": [item.value for item in ProjectStatus],
            "modes": [
                {
                    "value": mode.value,
                    "label": preset.label,
                    "width": preset.width,
                    "height": preset.height,
                    "aspect_ratio": preset.aspect_ratio,
                }
                for mode, preset in OUTPUT_MODE_PRESETS.items()
            ],
        }

    @app.get("/api/projects")
    def projects() -> list[dict[str, Any]]:
        return [
            _project_payload(project)
            for project in context.project_service.list_projects()
        ]

    @app.post("/api/projects")
    def create_project() -> dict[str, Any]:
        project = context.project_service.create_project()
        return _project_payload(project)

    @app.get("/api/projects/{project_id}")
    def project(project_id: UUID) -> dict[str, Any]:
        return _project_payload(get_project(project_id))

    @app.post("/api/projects/{project_id}/duplicate")
    def duplicate_project(project_id: UUID) -> dict[str, Any]:
        duplicated = context.project_service.duplicate(get_project(project_id))
        return _project_payload(duplicated)

    @app.post("/api/projects/{project_id}/archive")
    def archive_project(project_id: UUID) -> dict[str, Any]:
        archived = context.project_service.archive(get_project(project_id))
        return _project_payload(archived)

    @app.put("/api/projects/{project_id}/brief")
    def save_brief(project_id: UUID, request: BriefRequest) -> dict[str, Any]:
        project = get_project(project_id)
        had_prompt = bool(project.prompt_text)
        brief = _prepare_collection(
            context,
            request.brief,
            request.confirm_new_collection,
        )
        try:
            saved = context.project_service.save_brief(project, brief)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "project": _project_payload(saved),
            "prompt_invalidated": bool(had_prompt and not saved.prompt_text),
        }

    @app.post("/api/projects/{project_id}/prompt")
    def prepare_prompt(project_id: UUID, request: BriefRequest) -> dict[str, Any]:
        project = get_project(project_id)
        brief = _prepare_collection(
            context,
            request.brief,
            request.confirm_new_collection,
        )
        try:
            saved = context.project_service.save_brief(project, brief)
            prepared = context.project_service.generate_prompt(saved)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _project_payload(prepared)

    @app.post("/api/projects/{project_id}/mark-sent")
    def mark_sent(project_id: UUID) -> dict[str, Any]:
        try:
            updated = context.project_service.mark_sent_to_agent(get_project(project_id))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _project_payload(updated)

    @app.post("/api/projects/{project_id}/reference")
    async def upload_reference(
        project_id: UUID,
        file: Annotated[UploadFile, File()],
    ) -> dict[str, str]:
        project = get_project(project_id)
        filename = _safe_filename(file.filename)
        if Path(filename).suffix.lower() not in IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Format d'image non pris en charge.")
        target = (
            context.settings.projects_dir
            / str(project.id)
            / f"v{project.version}"
            / "reference"
            / filename
        )
        await _store_upload(file, target, context.artifact_service.max_bytes)
        return {"path": str(target), "filename": filename}

    @app.post("/api/projects/{project_id}/artifacts")
    async def import_artifacts(
        project_id: UUID,
        files: Annotated[list[UploadFile], File()],
    ) -> dict[str, Any]:
        project = get_project(project_id)
        if not files:
            raise HTTPException(status_code=400, detail="Aucun fichier fourni.")

        temp_root = root / "_uploads" / uuid4().hex
        temp_root.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        try:
            for upload in files:
                filename = _safe_filename(upload.filename)
                suffix = Path(filename).suffix.lower()
                if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
                    # Le validateur historique ignore ces formats avec un avertissement.
                    # On les conserve ici pour reproduire exactement ce comportement.
                    pass
                paths.append(
                    await _store_upload(
                        upload,
                        temp_root / filename,
                        context.artifact_service.max_bytes,
                    )
                )

            try:
                report = context.artifact_service.import_package(project, paths)
            except (OSError, ValueError) as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)

        app.state.reports[str(project.id)] = report
        return _report_payload(project, report)

    @app.get("/api/projects/{project_id}/validation")
    def validation(project_id: UUID) -> dict[str, Any]:
        project = get_project(project_id)
        report = get_report(project)
        if report is None:
            return {
                "artifacts": [],
                "issues": [],
                "automatic_checks_passed": False,
                "ready": False,
            }
        return _report_payload(project, report)

    @app.post("/api/projects/{project_id}/approve")
    def approve(project_id: UUID, request: ApprovalRequest) -> dict[str, Any]:
        project = get_project(project_id)
        report = get_report(project)
        confirmations = HumanConfirmations(approved=request.approved)
        ready = can_submit(report, confirmations)
        if ready:
            project.status = ProjectStatus.VALIDATED
            context.project_repository.save(project)
        return {
            "project": _project_payload(project),
            "ready": ready,
        }

    @app.get("/api/projects/{project_id}/artifacts/{artifact_id}/content")
    def artifact_content(project_id: UUID, artifact_id: UUID) -> FileResponse:
        project = get_project(project_id)
        artifacts = context.artifact_repository.list_for_project(project.id)
        artifact = next((item for item in artifacts if item.id == artifact_id), None)
        if artifact is None:
            raise HTTPException(status_code=404, detail="Livrable introuvable.")
        path = _resolve_artifact_path(context, project, artifact)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Fichier introuvable.")
        media_type, _ = mimetypes.guess_type(path.name)
        return FileResponse(path, media_type=media_type)

    @app.post("/api/projects/{project_id}/export")
    def export_project(project_id: UUID, request: ApprovalRequest) -> FileResponse:
        project = get_project(project_id)
        report = get_report(project)
        confirmations = HumanConfirmations(approved=request.approved)
        if report is None or not can_submit(report, confirmations):
            raise HTTPException(
                status_code=400,
                detail="Le résultat doit être validé avant l'export.",
            )

        temp_dir = Path(tempfile.mkdtemp(prefix="visual-ai-export-", dir=root))
        export_root = temp_dir / "bundle"
        target = export_project_bundle(project, report.artifacts, export_root)
        archive_base = temp_dir / f"{project.slug}-v{project.version}"
        archive_path = Path(
            shutil.make_archive(
                str(archive_base),
                "zip",
                root_dir=export_root,
                base_dir=target.name,
            )
        )
        return FileResponse(
            archive_path,
            media_type="application/zip",
            filename=archive_path.name,
            background=BackgroundTask(shutil.rmtree, temp_dir, True),
        )

    @app.post("/api/projects/{project_id}/submit")
    def submit(project_id: UUID, request: ApprovalRequest) -> dict[str, Any]:
        project = get_project(project_id)
        report = get_report(project)
        if report is None:
            raise HTTPException(status_code=400, detail="Aucun résultat à envoyer.")
        if not context.settings.webhook_url:
            raise HTTPException(status_code=400, detail="Webhook non configuré.")

        confirmations = HumanConfirmations(approved=request.approved)
        client = WebhookClient(
            str(context.settings.webhook_url),
            context.settings.auth_header_name,
            _webhook_secret(context),
            context.settings.timeout_seconds,
        )
        service = SubmissionService(
            client,
            AutomationRunRepository(context.database),
            context.project_repository,
        )
        outcome = service.submit(project, report.artifacts, report, confirmations)
        return outcome.model_dump(mode="json")

    @app.get("/api/storage/directories")
    def storage_directories(path: str | None = None) -> dict[str, Any]:
        current = Path(path).resolve() if path else root
        if not _is_within(current, root):
            raise HTTPException(status_code=400, detail="Chemin hors du volume Docker autorisé.")
        if not current.is_dir():
            raise HTTPException(status_code=404, detail="Dossier introuvable.")
        children = sorted(
            [item for item in current.iterdir() if item.is_dir()],
            key=lambda item: item.name.casefold(),
        )
        parent = current.parent if current != root else current
        return {
            "root": str(root),
            "current": str(current),
            "parent": str(parent),
            "children": [
                {"name": item.name, "path": str(item)}
                for item in children
            ],
        }

    @app.put("/api/settings")
    def save_settings(request: SettingsRequest) -> dict[str, Any]:
        candidate = Path(request.projects_dir or context.settings.projects_dir)
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        if not _is_within(candidate, root):
            raise HTTPException(
                status_code=400,
                detail="Le dossier doit rester dans le volume Docker.",
            )
        if not candidate.is_dir():
            raise HTTPException(status_code=400, detail="Le dossier sélectionné n'existe pas.")

        updates: dict[str, Any] = {"projects_dir": candidate}
        if request.webhook_url is not None:
            raw_webhook_url = request.webhook_url.strip()
            if raw_webhook_url:
                try:
                    updates["webhook_url"] = TypeAdapter(HttpUrl).validate_python(
                        raw_webhook_url
                    )
                except ValidationError as exc:
                    raise HTTPException(
                        status_code=400,
                        detail="L’URL du webhook n’est pas valide.",
                    ) from exc
            else:
                updates["webhook_url"] = None

        if request.auth_header_name is not None:
            header_name = request.auth_header_name.strip()
            if not header_name or len(header_name) > 120 or any(
                character.isspace() for character in header_name
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Le nom du header d’authentification est invalide.",
                )
            updates["auth_header_name"] = header_name

        if request.timeout_seconds is not None:
            updates["timeout_seconds"] = request.timeout_seconds

        try:
            stored = context.settings_store.load().model_copy(
                update=updates,
                deep=True,
            )
            context.settings_store.save(stored)
            context.settings = context.settings.model_copy(
                update=updates,
                deep=True,
            )
            if request.webhook_secret is not None and request.webhook_secret.strip():
                context.settings_store.set_secret(request.webhook_secret)
        except (OSError, ValidationError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        context.artifact_service.projects_dir = candidate
        return {
            "projects_dir": str(candidate),
            "settings": _settings_payload(context, root),
        }

    @app.post("/api/settings/test-webhook")
    def test_webhook() -> dict[str, Any]:
        if not context.settings.webhook_url:
            raise HTTPException(status_code=400, detail="Webhook non configuré.")

        client = WebhookClient(
            str(context.settings.webhook_url),
            context.settings.auth_header_name,
            _webhook_secret(context),
            context.settings.timeout_seconds,
        )
        return client.test_connection().model_dump(mode="json")

    dist = Path(web_dist or os.getenv("VISUAL_AI_WEB_DIST", "").strip() or "/app/web-dist")
    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{path:path}", include_in_schema=False, response_model=None)
    def spa(path: str) -> FileResponse | HTMLResponse:
        index = dist / "index.html"
        if index.is_file():
            return FileResponse(index)
        return HTMLResponse(
            "<main style='font-family:sans-serif;padding:3rem'>"
            "<h1>Visual AI Studio</h1>"
            "<p>Le frontend web n'est pas compilé dans cette image.</p>"
            "</main>",
            status_code=503,
        )

    return app


app = create_app()
