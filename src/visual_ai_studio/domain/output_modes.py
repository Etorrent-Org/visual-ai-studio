from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OutputMode(StrEnum):
    PINTEREST = "pinterest"
    INSTAGRAM = "instagram"
    CUSTOM = "custom"

    @classmethod
    def _missing_(
        cls,
        value: object,
    ) -> OutputMode | None:
        if value == "generic":
            return cls.CUSTOM

        return None


@dataclass(frozen=True)
class OutputModePreset:
    mode: OutputMode
    label: str
    width: int | None
    height: int | None
    aspect_ratio: str
    publication: bool


OutputPreset = OutputModePreset
ModePreset = OutputModePreset


OUTPUT_MODE_PRESETS = {
    OutputMode.PINTEREST: OutputModePreset(
        mode=OutputMode.PINTEREST,
        label="Pinterest",
        width=1000,
        height=1500,
        aspect_ratio="2:3",
        publication=True,
    ),
    OutputMode.INSTAGRAM: OutputModePreset(
        mode=OutputMode.INSTAGRAM,
        label="Instagram",
        width=1080,
        height=1350,
        aspect_ratio="4:5",
        publication=True,
    ),
    OutputMode.CUSTOM: OutputModePreset(
        mode=OutputMode.CUSTOM,
        label="Autre / personnalisé",
        width=None,
        height=None,
        aspect_ratio="",
        publication=False,
    ),
}


def preset_for(
    mode: OutputMode | str,
) -> OutputModePreset:
    resolved = OutputMode(mode)

    return OUTPUT_MODE_PRESETS[
        resolved
    ]