from pathlib import Path
from uuid import uuid4

from PIL import Image
from pytestqt.qtbot import QtBot

from visual_ai_studio.domain.models import (
    Artifact,
    ValidationReport,
)
from visual_ai_studio.domain.statuses import (
    ArtifactType,
)
from visual_ai_studio.domain.validators import (
    sha256_file,
)
from visual_ai_studio.ui.import_page import (
    ImportPage,
)


def make_image_artifact(
    path: Path,
) -> Artifact:
    Image.new(
        "RGB",
        (500, 700),
        "white",
    ).save(
        path,
        format="PNG",
    )

    return Artifact(
        project_id=uuid4(),
        artifact_type=ArtifactType.IMAGE,
        filename=path.name,
        local_path=path,
        sha256=sha256_file(path),
        width=500,
        height=700,
        validation_status="valid",
    )


def test_two_images_create_two_previews(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    page = ImportPage()

    qtbot.addWidget(
        page
    )

    first = make_image_artifact(
        tmp_path / "image-1.png"
    )

    second = make_image_artifact(
        tmp_path / "image-2.png"
    )

    report = ValidationReport(
        artifacts=[
            first,
            second,
        ]
    )

    page.set_report(
        report
    )

    assert (
        len(page.preview_labels)
        == 2
    )

    assert (
        page.preview_labels[0].pixmap()
        is not None
    )

    assert (
        page.preview_labels[1].pixmap()
        is not None
    )

    assert (
        not page.preview_labels[0]
        .pixmap()
        .isNull()
    )

    assert (
        not page.preview_labels[1]
        .pixmap()
        .isNull()
    )