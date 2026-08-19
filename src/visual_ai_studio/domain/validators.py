from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from .models import Artifact, ValidationIssue, ValidationReport
from .statuses import ArtifactType

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for chunk in iter(
            lambda: stream.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def _classify(
    path: Path,
) -> ArtifactType | None:
    suffix = path.suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        return ArtifactType.IMAGE

    if suffix in TEXT_EXTENSIONS:
        return ArtifactType.TEXT

    if suffix == ".json":
        if "manifest" in path.stem.casefold():
            return ArtifactType.MANIFEST

        return ArtifactType.METADATA

    return None


def _validate_image(
    path: Path,
    expected_width: int | None,
    expected_height: int | None,
) -> tuple[
    int | None,
    int | None,
    list[ValidationIssue],
]:
    issues: list[ValidationIssue] = []

    try:
        with Image.open(path) as image:
            image.verify()

        with Image.open(path) as image:
            width, height = image.size

    except (
        OSError,
        UnidentifiedImageError,
    ):
        return (
            None,
            None,
            [
                ValidationIssue(
                    code="invalid_image",
                    message=(f"{path.name} n'est pas une image lisible."),
                    artifact=path.name,
                )
            ],
        )

    wrong_width = expected_width is not None and width != expected_width

    wrong_height = expected_height is not None and height != expected_height

    if wrong_width or wrong_height:
        width_target = "*"
        height_target = "*"

        if expected_width is not None:
            width_target = str(expected_width)

        if expected_height is not None:
            height_target = str(expected_height)

        issues.append(
            ValidationIssue(
                code="invalid_dimensions",
                message=(
                    f"{path.name} mesure "
                    f"{width} × {height}, "
                    f"attendu {width_target} × "
                    f"{height_target}."
                ),
                artifact=path.name,
            )
        )

    return width, height, issues


def _validate_text(
    path: Path,
) -> list[ValidationIssue]:
    try:
        text = path.read_text(encoding="utf-8")

    except (
        OSError,
        UnicodeError,
    ):
        return [
            ValidationIssue(
                code="invalid_text",
                message=(f"{path.name} n'est pas un fichier texte UTF-8 lisible."),
                artifact=path.name,
            )
        ]

    if not text.strip():
        return [
            ValidationIssue(
                code="empty_text",
                message=(f"{path.name} ne contient aucun texte exploitable."),
                artifact=path.name,
            )
        ]

    return []


def _validate_json(
    path: Path,
) -> list[ValidationIssue]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))

    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ):
        return [
            ValidationIssue(
                code="invalid_json",
                message=(f"{path.name} n'est pas un JSON valide."),
                artifact=path.name,
            )
        ]

    if not isinstance(payload, dict):
        return [
            ValidationIssue(
                code="invalid_json_object",
                message=(f"{path.name} doit contenir un objet JSON."),
                artifact=path.name,
            )
        ]

    return []


def validate_artifact_package(
    project_id: Any,
    paths: list[Path],
    expected_width: int | None = None,
    expected_height: int | None = None,
) -> ValidationReport:
    report = ValidationReport()

    for raw_path in paths:
        path = Path(raw_path)

        kind = _classify(path)

        if kind is None:
            report.issues.append(
                ValidationIssue(
                    code="unknown_file",
                    message=(f"{path.name} est ignoré : format non pris en charge."),
                    blocking=False,
                    artifact=path.name,
                )
            )
            continue

        if not path.is_file() or path.stat().st_size == 0:
            report.issues.append(
                ValidationIssue(
                    code="empty_or_unreadable",
                    message=(f"{path.name} est vide ou illisible."),
                    artifact=path.name,
                )
            )
            continue

        width: int | None = None
        height: int | None = None
        issues: list[ValidationIssue] = []

        if kind is ArtifactType.IMAGE:
            (
                width,
                height,
                issues,
            ) = _validate_image(
                path,
                expected_width,
                expected_height,
            )

        if kind is ArtifactType.TEXT:
            issues = _validate_text(path)

        if kind in {
            ArtifactType.METADATA,
            ArtifactType.MANIFEST,
        }:
            issues = _validate_json(path)

        report.issues.extend(issues)

        try:
            digest = sha256_file(path)

        except OSError:
            report.issues.append(
                ValidationIssue(
                    code="hash_failed",
                    message=(f"Impossible de calculer l'empreinte de {path.name}."),
                    artifact=path.name,
                )
            )
            continue

        validation_status = "valid"

        if any(issue.artifact == path.name for issue in report.blocking_issues):
            validation_status = "invalid"

        report.artifacts.append(
            Artifact(
                project_id=project_id,
                artifact_type=kind,
                filename=path.name,
                local_path=path,
                sha256=digest,
                width=width,
                height=height,
                validation_status=(validation_status),
            )
        )

    image_count = sum(
        1 for artifact in report.artifacts if artifact.artifact_type is ArtifactType.IMAGE
    )

    if image_count == 0:
        report.issues.append(
            ValidationIssue(
                code="missing_image",
                message=("Aucune image n'a été fournie."),
            )
        )

    has_manifest = any(
        artifact.artifact_type is ArtifactType.MANIFEST for artifact in report.artifacts
    )

    if not has_manifest:
        report.issues.append(
            ValidationIssue(
                code="missing_manifest",
                message=("Le manifeste facultatif est absent."),
                blocking=False,
            )
        )

    return report
