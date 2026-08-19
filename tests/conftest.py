from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

import pytest
from PIL import Image

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)


@pytest.fixture
def artifact_package(
    tmp_path: Path,
) -> Callable[..., list[Path]]:
    def factory(
        slug: str = "demo-visual",
        size: tuple[int, int] = (
            1000,
            1500,
        ),
        include_manifest: bool = True,
    ) -> list[Path]:
        image = tmp_path / f"visual-ai-{slug}.png"

        Image.new(
            "RGB",
            size,
            "white",
        ).save(
            image,
            format="PNG",
        )

        text = tmp_path / f"visual-ai-{slug}.md"

        text.write_text(
            "# Résultat\n\nDescription du visuel généré.",
            encoding="utf-8",
        )

        metadata = tmp_path / f"visual-ai-{slug}-metadata.json"

        metadata.write_text(
            ('{"schema_version":"1.0","title":"Demo visual"}'),
            encoding="utf-8",
        )

        result = [
            image,
            text,
            metadata,
        ]

        if include_manifest:
            manifest = tmp_path / f"visual-ai-{slug}-manifest.json"

            manifest.write_text(
                '{"schema_version":"1.0"}',
                encoding="utf-8",
            )

            result.append(manifest)

        return result

    return factory
