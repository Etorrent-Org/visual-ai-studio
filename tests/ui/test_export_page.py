from pytestqt.qtbot import QtBot

from visual_ai_studio.domain.models import (
    HumanConfirmations,
    Project,
    ValidationReport,
)
from visual_ai_studio.ui.submission_page import SubmissionPage


def test_local_export_does_not_require_webhook(
    qtbot: QtBot,
) -> None:
    page = SubmissionPage()
    qtbot.addWidget(page)

    project = Project()

    report = ValidationReport()

    confirmations = HumanConfirmations(
        approved=True,
    )

    page.update_state(
        project,
        report,
        confirmations,
        configured=False,
    )

    assert page.export_button.isEnabled()
    assert not page.submit_button.isEnabled()


def test_webhook_is_optional(
    qtbot: QtBot,
) -> None:
    page = SubmissionPage()
    qtbot.addWidget(page)

    project = Project()

    report = ValidationReport()

    confirmations = HumanConfirmations(
        approved=True,
    )

    page.update_state(
        project,
        report,
        confirmations,
        configured=True,
    )

    assert page.export_button.isEnabled()
    assert page.submit_button.isEnabled()
