from pathlib import Path

from PySide6.QtWidgets import (
    QPushButton,
)
from pytestqt.qtbot import QtBot

from visual_ai_studio.infrastructure.settings import (
    AppSettings,
)
from visual_ai_studio.ui.settings_page import (
    SettingsPage,
)


def test_only_storage_is_exposed(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    page = SettingsPage()

    qtbot.addWidget(
        page
    )

    page.set_settings(
        AppSettings(
            projects_dir=tmp_path,
        ),
        False,
    )

    page.show()

    assert page.projects_dir.isVisible()

    assert not page.webhook.isVisible()
    assert not page.secret.isVisible()
    assert not page.header.isVisible()
    assert not page.timeout.isVisible()
    assert not page.agent_url.isVisible()
    assert not page.max_file.isVisible()
    assert not page.new_collection.isVisible()


def test_visible_actions_are_minimal(
    qtbot: QtBot,
) -> None:
    page = SettingsPage()

    qtbot.addWidget(
        page
    )

    page.show()

    labels = [
        button.text()
        for button in page.findChildren(
            QPushButton
        )
        if button.isVisible()
    ]

    assert labels == [
        "Choisir…",
        "Enregistrer",
    ]


def test_storage_change_preserves_internal_settings(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    page = SettingsPage()

    qtbot.addWidget(
        page
    )

    original = AppSettings(
        webhook_url=(
            "https://example.test/webhook"
        ),
        auth_header_name="X-Test",
        timeout_seconds=45,
        agent_url=(
            "https://example.test/agent"
        ),
        max_file_size_mb=80,
    )

    page.set_settings(
        original,
        False,
    )

    target = (
        tmp_path
        / "projects"
    )

    page.projects_dir.setText(
        str(target)
    )

    result = page.values()

    assert (
        result.projects_dir
        == target
    )

    assert (
        result.webhook_url
        == original.webhook_url
    )

    assert (
        result.auth_header_name
        == original.auth_header_name
    )

    assert (
        result.timeout_seconds
        == original.timeout_seconds
    )

    assert (
        result.agent_url
        == original.agent_url
    )

    assert (
        result.max_file_size_mb
        == original.max_file_size_mb
    )