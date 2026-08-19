from pathlib import Path

from visual_ai_studio.domain.models import (
    Artifact,
    Project,
)
from visual_ai_studio.domain.statuses import ArtifactType
from visual_ai_studio.services.export_service import (
    export_project_bundle,
)


def test_export_project_bundle(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"visual-ai")

    project = Project(
        title="Projet export",
        slug="projet-export",
    )

    artifact = Artifact(
        project_id=project.id,
        artifact_type=ArtifactType.MANIFEST,
        filename="resultat.png",
        local_path=source,
        sha256="abc123",
    )

    destination = tmp_path / "exports"

    target = export_project_bundle(
        project,
        [artifact],
        destination,
    )

    assert target.is_dir()

    assert (target / "resultat.png").read_bytes() == b"visual-ai"

    assert (target / "project.json").is_file()
