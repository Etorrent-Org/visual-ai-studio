from pytestqt.qtbot import QtBot

from visual_ai_studio.infrastructure.settings import (
    AppSettings,
)
from visual_ai_studio.ui.settings_page import (
    SettingsPage,
)


def test_settings_page_uses_generic_webhook(
    qtbot: QtBot,
) -> None:
    page = SettingsPage()
    qtbot.addWidget(page)

    settings = AppSettings()

    page.set_settings(
        settings,
        has_secret=False,
    )

    assert (
        page.header.text()
        == "X-Visual-AI-Token"
    )

    assert (
        page.values().auth_header_name
        == "X-Visual-AI-Token"
    )