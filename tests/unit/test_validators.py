from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from PIL import Image

from visual_ai_studio.domain.statuses import (
    ArtifactType,
)
from visual_ai_studio.domain.validators import (
    sha256_file,
    validate_artifact_package,
)


def issue_codes(
    report: object,
) -> set[str]:
    return {issue.code for issue in report.issues}


def test_valid_generic_package_and_hash(
    artifact_package: object,
) -> None:
    paths = artifact_package()

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    assert report.automatic_checks_passed

    assert len(report.artifacts) == 4

    assert {item.artifact_type for item in report.artifacts} == {
        ArtifactType.IMAGE,
        ArtifactType.TEXT,
        ArtifactType.METADATA,
        ArtifactType.MANIFEST,
    }

    assert all(len(item.sha256) == 64 for item in report.artifacts)

    assert sha256_file(paths[0]) == report.artifacts[0].sha256


def test_dimensions_are_checked_only_when_requested(
    artifact_package: object,
) -> None:
    paths = artifact_package(size=(999, 1500))

    report = validate_artifact_package(
        uuid4(),
        paths,
        expected_width=1000,
        expected_height=1500,
    )

    assert "invalid_dimensions" in issue_codes(report)

    assert not report.automatic_checks_passed


def test_free_dimensions_are_allowed(
    artifact_package: object,
) -> None:
    paths = artifact_package(size=(321, 654))

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    assert "invalid_dimensions" not in issue_codes(report)

    assert report.automatic_checks_passed


def test_invalid_image_is_detected(
    artifact_package: object,
) -> None:
    paths = artifact_package()

    paths[0].write_text(
        "not an image",
        encoding="utf-8",
    )

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    assert "invalid_image" in issue_codes(report)


def test_invalid_json_is_detected(
    artifact_package: object,
) -> None:
    paths = artifact_package()

    metadata = next(path for path in paths if "metadata" in path.name)

    metadata.write_text(
        "{broken",
        encoding="utf-8",
    )

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    assert "invalid_json" in issue_codes(report)


def test_unknown_file_is_only_warning(
    artifact_package: object,
    tmp_path: Path,
) -> None:
    paths = artifact_package()

    unknown = tmp_path / "document.pdf"

    unknown.write_bytes(b"demo")

    paths.append(unknown)

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    assert "unknown_file" in issue_codes(report)

    assert report.automatic_checks_passed


def test_image_is_required(
    artifact_package: object,
) -> None:
    paths = artifact_package()

    paths = [
        path
        for path in paths
        if path.suffix.lower()
        not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }
    ]

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    assert "missing_image" in issue_codes(report)

    assert not report.automatic_checks_passed


def test_multiple_images_are_allowed(
    artifact_package: object,
    tmp_path: Path,
) -> None:
    paths = artifact_package()

    second = tmp_path / "second-image.webp"

    Image.new(
        "RGB",
        (640, 640),
        "white",
    ).save(
        second,
        format="WEBP",
    )

    paths.append(second)

    report = validate_artifact_package(
        uuid4(),
        paths,
    )

    image_count = sum(
        1 for artifact in report.artifacts if artifact.artifact_type is ArtifactType.IMAGE
    )

    assert image_count == 2
    assert report.automatic_checks_passed


def test_manifest_absence_is_only_warning(
    artifact_package: object,
) -> None:
    report = validate_artifact_package(
        uuid4(),
        artifact_package(include_manifest=False),
    )

    assert report.automatic_checks_passed

    assert "missing_manifest" in issue_codes(report)


def test_legacy_artifact_values_are_readable() -> None:
    assert ArtifactType("pinterest") is ArtifactType.IMAGE

    assert ArtifactType("synthese") is ArtifactType.IMAGE

    assert ArtifactType("notion") is ArtifactType.TEXT
