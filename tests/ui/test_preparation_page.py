from pytestqt.qtbot import QtBot

from visual_ai_studio.domain.models import (
    Project,
)
from visual_ai_studio.ui.prompt_page import (
    PromptPage,
)


def test_prompt_is_required_before_continue(
    qtbot: QtBot,
) -> None:
    page = PromptPage()

    qtbot.addWidget(page)

    page.set_project(Project())

    assert not page.copy_button.isEnabled()
    assert not page.continue_button.isEnabled()


def test_ready_prompt_can_be_copied(
    qtbot: QtBot,
) -> None:
    page = PromptPage()

    qtbot.addWidget(page)

    page.set_project(
        Project(
            prompt_text=("AGENT CIBLE : Studio Visuel"),
            prompt_hash="abc",
        )
    )

    assert page.copy_button.isEnabled()
    assert page.continue_button.isEnabled()

    assert "Prompt prêt" in page.version_label.text()


def test_agent_link_is_optional(
    qtbot: QtBot,
) -> None:
    page = PromptPage()

    qtbot.addWidget(page)

    page.show()

    assert not page.open_agent.isVisible()

    page.set_agent_url("https://chatgpt.com/")

    assert page.open_agent.isVisible()
    assert page.open_agent.isEnabled()
