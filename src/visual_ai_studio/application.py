from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_data_dir

from visual_ai_studio.infrastructure.database import (
    ArtifactRepository,
    Database,
    ProjectRepository,
    ReferenceRepository,
)
from visual_ai_studio.infrastructure.settings import AppSettings, SettingsStore
from visual_ai_studio.services.artifact_service import ArtifactService
from visual_ai_studio.services.project_service import ProjectService


@dataclass
class ApplicationContext:
    database: Database
    settings_store: SettingsStore
    settings: AppSettings
    project_repository: ProjectRepository
    reference_repository: ReferenceRepository
    artifact_repository: ArtifactRepository
    project_service: ProjectService
    artifact_service: ArtifactService


def build_application(data_dir: Path | None = None) -> ApplicationContext:
    root = data_dir or Path(user_data_dir("Visual AI Studio", "Visual AI Studio"))
    root.mkdir(parents=True, exist_ok=True)
    settings_store = SettingsStore(root / "settings.json" if data_dir else None)
    settings = settings_store.load()
    database = Database(root / "visual-ai-studio.db")
    database.initialize()
    projects = ProjectRepository(database)
    references = ReferenceRepository(database)
    artifacts = ArtifactRepository(database)
    project_service = ProjectService(projects, references)
    project_service.seed_catalog()
    artifact_service = ArtifactService(
        artifacts,
        projects,
        settings.projects_dir,
        settings.max_file_size_mb,
    )
    return ApplicationContext(
        database=database,
        settings_store=settings_store,
        settings=settings,
        project_repository=projects,
        reference_repository=references,
        artifact_repository=artifacts,
        project_service=project_service,
        artifact_service=artifact_service,
    )
