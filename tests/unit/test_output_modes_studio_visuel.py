import pytest

from visual_ai_studio.domain.output_modes import (
    OUTPUT_MODE_PRESETS,
    OutputMode,
    preset_for,
)


def test_only_two_active_modes() -> None:
    assert list(OutputMode) == [
        OutputMode.INSTAGRAM,
        OutputMode.CUSTOM,
    ]


def test_instagram_preset() -> None:
    preset = preset_for(OutputMode.INSTAGRAM)

    assert preset.width == 1080
    assert preset.height == 1350
    assert preset.aspect_ratio == "4:5"


def test_previous_generic_value_maps_to_custom() -> None:
    assert OutputMode("generic") is OutputMode.CUSTOM


def test_removed_pinterest_value_is_rejected() -> None:
    with pytest.raises(ValueError):
        OutputMode("pinterest")


def test_presets_cover_active_modes() -> None:
    assert set(OUTPUT_MODE_PRESETS) == set(OutputMode)
