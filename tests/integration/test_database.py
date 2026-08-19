from __future__ import annotations

from pathlib import Path

from visual_ai_studio.domain.models import Brief
from visual_ai_studio.infrastructure.database import Database, ProjectRepository, ReferenceRepository
from visual_ai_studio.services.project_service import ProjectService


def test_project_persists_and_resumes(tmp_path: Path) -> None:
    path = tmp_path / "visual-ai.db"
    database = Database(path)
    database.initialize()
    service = ProjectService(ProjectRepository(database), ReferenceRepository(database))
    project = service.create_project("Projet persistant")
    service.save_brief(
        project,
        Brief(
            title="Projet persistant",
            collection="Ink Minimal",
            style="sumi-e contemporain",
            raw_idea="Une branche au lavis",
        ),
    )
    reopened = ProjectService(
        ProjectRepository(Database(path)), ReferenceRepository(Database(path))
    ).get(project.id)
    assert reopened is not None
    assert reopened.title == "Projet persistant"
    assert reopened.brief.collection == "Ink Minimal"
    assert reopened.brief.raw_idea == "Une branche au lavis"


def test_catalog_seeding_contains_eight_collections(tmp_path: Path) -> None:
    database = Database(tmp_path / "catalog.db")
    database.initialize()
    service = ProjectService(ProjectRepository(database), ReferenceRepository(database))
    service.seed_catalog()
    assert len(service.collections()) == 8
    assert "modèle standard à dupliquer" not in service.styles()
