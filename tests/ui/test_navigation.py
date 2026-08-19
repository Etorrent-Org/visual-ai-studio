from pathlib import Path

from pytestqt.qtbot import QtBot

from visual_ai_studio.application import build_application
from visual_ai_studio.ui.main_window import MainWindow


def test_main_navigation_is_simple(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    context = build_application(tmp_path / "data")

    window = MainWindow(context)
    qtbot.addWidget(window)

    labels = [button.text() for button in window.nav_buttons]

    assert labels == [
        "Projets",
        "Créer",
        "Paramètres",
    ]

    assert window.nav_page_indices == [
        0,
        1,
        5,
    ]

    assert window.pages.count() == 6
    assert window.webhook_indicator.isHidden()


def test_creation_flow_keeps_create_navigation_active(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    context = build_application(tmp_path / "data")

    window = MainWindow(context)
    qtbot.addWidget(window)

    window.current_project = context.project_service.create_project()

    window.show_page(2)

    assert window.nav_buttons[1].property("active") is True

    window.show_page(3)

    assert window.nav_buttons[1].property("active") is True

    window.show_page(4)

    assert window.nav_buttons[1].property("active") is True
