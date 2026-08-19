from pathlib import Path

from visual_ai_studio.infrastructure.settings import (
    AppSettings,
    SettingsStore,
)


def test_default_settings_are_generic() -> None:
    settings = AppSettings()

    assert (
        settings.auth_header_name
        == "X-Visual-AI-Token"
    )


def test_settings_round_trip(
    tmp_path: Path,
) -> None:
    path = tmp_path / "settings.json"

    store = SettingsStore(
        path
    )

    expected = AppSettings(
        auth_header_name="X-Demo-Token",
        timeout_seconds=45,
    )

    store.save(expected)

    loaded = store.load()

    assert (
        loaded.auth_header_name
        == "X-Demo-Token"
    )

    assert (
        loaded.timeout_seconds
        == 45
    )