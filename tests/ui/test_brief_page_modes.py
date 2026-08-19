from pytestqt.qtbot import QtBot

from visual_ai_studio.domain.models import (
    Project,
)
from visual_ai_studio.domain.output_modes import (
    OutputMode,
)
from visual_ai_studio.ui.brief_page import (
    BriefPage,
)


def test_brief_page_exposes_agent_modes_only(
    qtbot: QtBot,
) -> None:
    page = BriefPage()

    qtbot.addWidget(
        page
    )

    values = [
        page.mode_combo.itemData(index)
        for index in range(
            page.mode_combo.count()
        )
    ]

    assert values == [
        OutputMode.PINTEREST.value,
        OutputMode.INSTAGRAM.value,
        OutputMode.CUSTOM.value,
    ]


def test_pinterest_format_is_applied(
    qtbot: QtBot,
) -> None:
    page = BriefPage()

    qtbot.addWidget(
        page
    )

    index = page.mode_combo.findData(
        OutputMode.PINTEREST.value
    )

    page.mode_combo.setCurrentIndex(
        index
    )

    assert page.width.value() == 1000
    assert page.height.value() == 1500
    assert page.aspect_ratio.text() == "2:3"


def test_custom_format_is_editable(
    qtbot: QtBot,
) -> None:
    page = BriefPage()

    qtbot.addWidget(
        page
    )

    index = page.mode_combo.findData(
        OutputMode.CUSTOM.value
    )

    page.mode_combo.setCurrentIndex(
        index
    )

    assert page.width.isEnabled()
    assert page.height.isEnabled()
    assert page.aspect_ratio.isEnabled()


def test_project_mode_round_trip(
    qtbot: QtBot,
) -> None:
    page = BriefPage()

    qtbot.addWidget(
        page
    )

    project = Project()

    project.brief.mode = (
        OutputMode.INSTAGRAM
    )

    page.set_project(
        project
    )

    result = page.brief()

    assert (
        result.mode
        is OutputMode.INSTAGRAM
    )