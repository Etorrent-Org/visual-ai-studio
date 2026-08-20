from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTextEdit,
    QWidget,
)


def polish_widget_tree(
    root: QWidget,
) -> None:
    """
    Harmonise les contrôles natifs Windows avec le
    design system de Visual AI Studio.
    """

    for button in root.findChildren(QPushButton):
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    for combo in root.findChildren(QComboBox):
        combo.setMinimumHeight(36)
        combo.setMaximumHeight(36)
        combo.setMaxVisibleItems(8)

        view = combo.view()

        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        view.setMaximumHeight(260)

        view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    for field in root.findChildren(QLineEdit):
        field.setMinimumHeight(36)

    for int_spin in root.findChildren(QSpinBox):
        int_spin.setMinimumHeight(36)

    for double_spin in root.findChildren(QDoubleSpinBox):
        double_spin.setMinimumHeight(36)

    for text_editor in root.findChildren(QTextEdit):
        text_editor.setMinimumHeight(86)

    for plain_editor in root.findChildren(QPlainTextEdit):
        plain_editor.setMinimumHeight(86)

    for table in root.findChildren(QTableWidget):
        table.setShowGrid(False)

        table.setAlternatingRowColors(True)

        table.verticalHeader().setVisible(False)

        table.verticalHeader().setDefaultSectionSize(46)

        table.horizontalHeader().setMinimumHeight(40)

        table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    for scroll in root.findChildren(QScrollArea):
        scroll.setFrameShape(QFrame.Shape.NoFrame)
