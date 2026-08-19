from __future__ import annotations

from pytestqt.qtbot import QtBot

from visual_ai_studio.domain.models import (
    HumanConfirmations,
    Project,
    ValidationIssue,
    ValidationReport,
)
from visual_ai_studio.ui.submission_page import SubmissionPage


def confirmed() -> HumanConfirmations:
    return HumanConfirmations(approved=True)


def test_webhook_button_only_activates_after_all_validations(qtbot: QtBot) -> None:
    page = SubmissionPage()
    qtbot.addWidget(page)
    project = Project()
    valid = ValidationReport()
    page.update_state(project, valid, confirmed(), configured=True)
    assert page.submit_button.isEnabled()
    invalid = ValidationReport(issues=[ValidationIssue(code="bad", message="Erreur bloquante")])
    page.update_state(project, invalid, confirmed(), configured=True)
    assert not page.submit_button.isEnabled()
    page.update_state(project, valid, HumanConfirmations(), configured=True)
    assert not page.submit_button.isEnabled()
    page.update_state(project, valid, confirmed(), configured=False)
    assert not page.submit_button.isEnabled()
