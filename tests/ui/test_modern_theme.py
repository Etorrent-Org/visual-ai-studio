from importlib.resources import files

from pytestqt.qtbot import QtBot

from visual_ai_studio.domain.statuses import (
    ProjectStatus,
)
from visual_ai_studio.ui.dashboard import (
    DashboardPage,
)


def test_dashboard_keeps_business_statuses(
    qtbot: QtBot,
) -> None:
    page = DashboardPage()

    qtbot.addWidget(
        page
    )

    values = [
        page.status_filter.itemText(
            index
        )
        for index in range(
            page.status_filter.count()
        )
    ]

    assert values == [
        "Tous les statuts",
        *[
            status.value
            for status in ProjectStatus
        ],
    ]


def test_status_menu_is_compact(
    qtbot: QtBot,
) -> None:
    page = DashboardPage()

    qtbot.addWidget(
        page
    )

    assert (
        page.status_filter.maximumHeight()
        == 36
    )

    assert (
        page.status_filter.view().maximumHeight()
        == 150
    )


def test_dashboard_actions_keep_current_terms(
    qtbot: QtBot,
) -> None:
    page = DashboardPage()

    qtbot.addWidget(
        page
    )

    assert (
        page.new_button.text()
        == "Nouveau projet"
    )

    assert (
        page.open_button.text()
        == "Ouvrir"
    )

    assert (
        page.duplicate_button.text()
        == "Dupliquer"
    )

    assert (
        page.archive_button.text()
        == "Archiver"
    )


def test_design_system_contains_modern_tokens() -> None:
    qss = (
        files(
            "visual_ai_studio.resources"
        )
        .joinpath(
            "styles.qss"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        "Segoe UI Variable Text"
        in qss
    )

    assert "#7C3AED" in qss
    assert "#08111F" in qss
    assert "QFrame#metricCard" in qss
    assert "QPushButton#navButton" in qss