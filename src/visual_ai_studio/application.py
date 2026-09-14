from __future__ import annotations

import shutil
import sqlite3
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

CURRENT_DATABASE_NAME = "visual-ai-studio.db"
LEGACY_DATABASE_NAME = "ia-art-studio.db"


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


def _database_contains_projects(path: Path) -> bool:
    if not path.exists():
        return False

    try:
        with sqlite3.connect(path) as connection:
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='projects'"
            ).fetchone()
            if table is None:
                return False
            return connection.execute("SELECT 1 FROM projects LIMIT 1").fetchone() is not None
    except sqlite3.DatabaseError:
        # Ne jamais écraser automatiquement une base existante qui paraît illisible.
        return True


def migrate_legacy_database(current_database: Path, legacy_database: Path) -> bool:
    """Copie la base IA-Art Studio uniquement si la base Visual AI Studio est vide."""
    if not legacy_database.exists() or _database_contains_projects(current_database):
        return False

    current_database.parent.mkdir(parents=True, exist_ok=True)

    if current_database.exists():
        backup = current_database.with_name("visual-ai-studio.pre-ia-art-migration.db")
        if not backup.exists():
            shutil.copy2(current_database, backup)

    with (
        sqlite3.connect(legacy_database) as source,
        sqlite3.connect(current_database) as target,
    ):
        source.backup(target)

    return True


def build_application(data_dir: Path | None = None) -> ApplicationContext:
    root = data_dir or Path(user_data_dir("Visual AI Studio", "Visual AI Studio"))
    root.mkdir(parents=True, exist_ok=True)

    database_path = root / CURRENT_DATABASE_NAME

    if data_dir is None:
        legacy_root = Path(user_data_dir("IA-Art Studio", "Etorrent-Org"))
        migrate_legacy_database(database_path, legacy_root / LEGACY_DATABASE_NAME)

    settings_store = SettingsStore(root / "settings.json" if data_dir else None)
    settings = settings_store.load()
    database = Database(database_path)
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
