from __future__ import annotations

import json
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from uuid import UUID

from visual_ai_studio.domain.models import Brief, Project, ReferenceValue
from visual_ai_studio.domain.normalization import (
    create_collection_reference,
    deduplicate_values,
    normalize_value,
    slugify,
)
from visual_ai_studio.domain.prompt_builder import brief_fingerprint, build_prompt
from visual_ai_studio.domain.statuses import ProjectStatus, SyncStatus
from visual_ai_studio.infrastructure.database import ProjectRepository, ReferenceRepository


class ProjectService:
    def __init__(self, projects: ProjectRepository, references: ReferenceRepository) -> None:
        self.projects = projects
        self.references = references

    def seed_catalog(self) -> None:
        data = json.loads(
            files("visual_ai_studio.resources").joinpath("references.json").read_text(encoding="utf-8")
        )
        values = [
            ReferenceValue(
                type=kind,
                value=value,
                normalized_value=normalize_value(value),
                source="notion",
                is_new=False,
                sync_status=SyncStatus.SYNCED,
            )
            for kind, key in (("collection", "collections"), ("style", "styles"))
            for value in data[key]
            if normalize_value(value) != normalize_value("modèle standard à dupliquer")
        ]
        self.references.seed(values)

    def create_project(self, title: str = "Nouveau projet") -> Project:
        title = title.strip() or "Nouveau projet"
        project = Project(title=title, slug=slugify(title), brief=Brief(title=title))
        return self.projects.save(project)

    def save_brief(self, project: Project, brief: Brief) -> Project:
        previous_hash = brief_fingerprint(project.brief)
        new_hash = brief_fingerprint(brief)
        project.brief = brief
        project.title = brief.title.strip() or project.title
        project.slug = slugify(project.title)
        project.updated_at = datetime.now(UTC)
        if project.prompt_text and previous_hash != new_hash:
            project.version += 1
            project.prompt_text = ""
            project.prompt_hash = ""
            project.prompt_brief_hash = ""
            project.status = ProjectStatus.BRIEF
        return self.projects.save(project)

    def generate_prompt(self, project: Project) -> Project:
        result = build_prompt(project.brief)
        project.prompt_text = result.text
        project.prompt_hash = result.sha256
        project.prompt_brief_hash = result.brief_sha256
        project.status = ProjectStatus.BRIEF
        project.updated_at = datetime.now(UTC)
        return self.projects.save(project)

    def mark_sent_to_agent(self, project: Project) -> Project:
        if not project.prompt_text:
            raise ValueError("Préparez le prompt Studio Visuel avant de continuer.")
        project.status = ProjectStatus.BRIEF
        project.updated_at = datetime.now(UTC)
        return self.projects.save(project)

    def archive(self, project: Project) -> Project:
        project.status = ProjectStatus.ARCHIVED
        project.archived_at = datetime.now(UTC)
        project.updated_at = project.archived_at
        return self.projects.save(project)

    def duplicate(self, project: Project) -> Project:
        title = f"{project.title} — copie"
        copy = Project(
            title=title,
            slug=slugify(title),
            brief=project.brief.model_copy(update={"title": title}, deep=True),
        )
        return self.projects.save(copy)

    def export_project(self, project: Project, path: Path) -> None:
        path.write_text(project.model_dump_json(indent=2), encoding="utf-8")

    def import_project(self, path: Path) -> Project:
        data = Project.model_validate_json(path.read_text(encoding="utf-8"))
        if self.projects.get(data.id) is not None:
            data.id = Project().id
            data.title = f"{data.title} — import"
            data.slug = slugify(data.title)
        data.updated_at = datetime.now(UTC)
        return self.projects.save(data)

    def add_collection(self, value: str) -> tuple[ReferenceValue, list[str]]:
        existing = [item.value for item in self.references.list("collection")]
        reference, similar = create_collection_reference(value, existing)
        self.references.add(reference)
        return reference, similar

    def collections(self) -> list[ReferenceValue]:
        return self.references.list("collection")

    def styles(self) -> list[str]:
        return deduplicate_values(
            [item.value for item in self.references.list("style")],
            excluded={"modèle standard à dupliquer"},
        )

    def get(self, project_id: UUID | str) -> Project | None:
        return self.projects.get(project_id)

    def list_projects(self, include_archived: bool = False) -> list[Project]:
        return self.projects.list(include_archived=include_archived)
