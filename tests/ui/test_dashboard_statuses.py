from pytestqt.qtbot import QtBot

from visual_ai_studio.ui.dashboard import DashboardPage


def test_dashboard_exposes_only_business_statuses(qtbot: QtBot) -> None:
    page = DashboardPage()
    qtbot.addWidget(page)

    labels = [
        page.status_filter.itemText(index)
        for index in range(page.status_filter.count())
    ]

    assert labels == [
        "Tous les statuts",
        "Brief",
        "Validé",
        "Archivé",
    ]