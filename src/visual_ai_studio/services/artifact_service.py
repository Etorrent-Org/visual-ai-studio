from __future__ import annotations

import shutil
from pathlib import Path

from visual_ai_studio.domain.models import (
    Project,
    ValidationReport,
)
from visual_ai_studio.domain.statuses import (
    ProjectStatus,
)
from visual_ai_studio.domain.validators import (
    validate_artifact_package,
)
from visual_ai_studio.infrastructure.database import (
    ArtifactRepository,
    ProjectRepository,
)


class ArtifactService:
    def __init__(
        self,
        artifacts: ArtifactRepository,
        projects: ProjectRepository,
        projects_dir: Path,
        max_file_size_mb: int = 50,
    ) -> None:
        self.artifacts = artifacts
        self.projects = projects
        self.projects_dir = projects_dir
        self.max_bytes = (
            max_file_size_mb
            * 1024
            * 1024
        )

    def import_package(
        self,
        project: Project,
        source_paths: list[Path],
    ) -> ValidationReport:
        for path in source_paths:
            if (
                path.is_file()
                and path.stat().st_size
                > self.max_bytes
            ):
                raise ValueError(
                    f"{path.name} dépasse "
                    "la limite de taille autorisée."
                )

        target = (
            self.projects_dir
            / str(project.id)
            / f"v{project.version}"
            / "artifacts"
        )

        target.mkdir(
            parents=True,
            exist_ok=True,
        )

        copied: list[Path] = []

        for source in source_paths:
            if not source.is_file():
                continue

            destination = (
                target
                / source.name
            )

            shutil.copy2(
                source,
                destination,
            )

            copied.append(
                destination
            )

        report = validate_artifact_package(
            project.id,
            copied,
            expected_width=(
                project.brief.target_width
            ),
            expected_height=(
                project.brief.target_height
            ),
        )

        self.artifacts.replace_for_project(
            project.id,
            report.artifacts,
        )

        project.status = ProjectStatus.BRIEF

        self.projects.save(project)

        return report


def collect_package_paths(
    folder: Path,
) -> list[Path]:
    if not folder.is_dir():
        return []

    allowed = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".md",
        ".txt",
        ".json",
    }

    return sorted(
        path
        for path in folder.iterdir()
        if path.suffix.lower() in allowed
    )