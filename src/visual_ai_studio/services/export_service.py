from __future__ import annotations

import shutil
from pathlib import Path

from visual_ai_studio.domain.models import Artifact, Project


def export_project_bundle(
    project: Project,
    artifacts: list[Artifact],
    destination: Path,
) -> Path:
    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    target = destination / (f"{project.slug}-v{project.version}")

    target.mkdir(
        parents=True,
        exist_ok=True,
    )

    for artifact in artifacts:
        source = Path(artifact.local_path)

        if not source.is_file():
            continue

        filename = artifact.filename.strip()

        if not filename:
            filename = source.name

        shutil.copy2(
            source,
            target / filename,
        )

    metadata = target / "project.json"

    metadata.write_text(
        project.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return target
