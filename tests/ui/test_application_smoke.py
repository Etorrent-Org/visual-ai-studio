from __future__ import annotations

from pathlib import Path

from pytestqt.qtbot import QtBot

from visual_ai_studio.application import build_application
from visual_ai_studio.ui.main_window import MainWindow


def test_main_window_starts_with_seeded_catalog(qtbot: QtBot, tmp_path: Path) -> None:
    context = build_application(tmp_path / "data")
    window = MainWindow(context)
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == "Visual AI Studio"
    assert len(context.project_service.collections()) == 8
    assert window.pages.count() == 6
