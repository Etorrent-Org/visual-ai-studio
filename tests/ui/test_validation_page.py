from pytestqt.qtbot import QtBot

from visual_ai_studio.ui.import_page import ImportPage


def test_validation_page_is_generic(
    qtbot: QtBot,
) -> None:
    page = ImportPage()
    qtbot.addWidget(page)

    assert page.approved.text() == (
        "Je valide ce résultat"
    )

    confirmations = page.confirmations()

    assert confirmations.approved is False

    page.approved.setChecked(True)

    confirmations = page.confirmations()

    assert confirmations.approved is True
    assert confirmations.all_confirmed is True