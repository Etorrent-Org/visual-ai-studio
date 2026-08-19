from __future__ import annotations

from PySide6.QtCore import (
    QUrl,
    Signal,
)
from PySide6.QtGui import (
    QDesktopServices,
)
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.domain.models import (
    Project,
)


class PromptPage(QWidget):
    back_requested = Signal()
    mark_sent_requested = Signal()

    def __init__(
        self,
    ) -> None:
        super().__init__()

        self._agent_url = ""

        title = QLabel("Préparation Studio Visuel")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Visual AI Studio a préparé le prompt de lancement destiné à l'agent Studio Visuel."
        )
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)

        self.version_label = QLabel("Prompt non préparé")
        self.version_label.setObjectName("muted")

        prompt_group = QGroupBox("Prompt à copier dans Studio Visuel")

        prompt_layout = QVBoxLayout(prompt_group)

        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)

        self.preview.setPlaceholderText(
            "Complétez le brief puis cliquez sur « Préparer pour Studio Visuel »."
        )

        prompt_layout.addWidget(self.preview)

        workflow_group = QGroupBox("Mode d'emploi")

        workflow_layout = QVBoxLayout(workflow_group)

        workflow = QLabel(
            "1. Copiez le prompt.\n"
            "2. Ouvrez Studio Visuel dans ChatGPT.\n"
            "3. Collez le prompt dans la conversation.\n"
            "4. Suivez les étapes proposées par Studio Visuel "
            "et validez-les une par une.\n"
            "5. Lorsque le résultat est terminé, revenez ici "
            "pour importer les fichiers."
        )

        workflow.setWordWrap(True)

        workflow_layout.addWidget(workflow)

        self.back_button = QPushButton("Retour au brief")

        self.back_button.clicked.connect(self.back_requested)

        self.copy_button = QPushButton("Copier le prompt")

        self.copy_button.clicked.connect(self._copy)

        self.open_agent = QPushButton("Ouvrir Studio Visuel")

        self.open_agent.clicked.connect(self._open)

        self.continue_button = QPushButton("Résultat prêt — importer les fichiers")

        self.continue_button.setObjectName("primaryButton")

        self.continue_button.clicked.connect(self.mark_sent_requested)

        controls = QHBoxLayout()

        controls.addWidget(self.back_button)

        controls.addStretch()

        controls.addWidget(self.copy_button)

        controls.addWidget(self.open_agent)

        controls.addWidget(self.continue_button)

        layout = QVBoxLayout(self)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addWidget(self.version_label)

        layout.addWidget(
            prompt_group,
            1,
        )

        layout.addWidget(workflow_group)

        layout.addLayout(controls)

        self._update_actions()

    def set_project(
        self,
        project: Project,
    ) -> None:
        self.preview.setPlainText(project.prompt_text)

        if project.prompt_text:
            self.version_label.setText(f"Prompt prêt • version {project.version}")

        if not project.prompt_text:
            self.version_label.setText("Le prompt doit être préparé à partir du brief.")

        if project.prompt_hash:
            self.version_label.setToolTip(f"SHA-256 : {project.prompt_hash}")

        if not project.prompt_hash:
            self.version_label.setToolTip("")

        self._update_actions()

    def set_agent_url(
        self,
        url: str,
    ) -> None:
        self._agent_url = url.strip()

        self._update_actions()

    def _update_actions(
        self,
    ) -> None:
        has_prompt = bool(self.preview.toPlainText().strip())

        self.copy_button.setEnabled(has_prompt)

        self.continue_button.setEnabled(has_prompt)

        self.open_agent.setVisible(bool(self._agent_url))

        self.open_agent.setEnabled(bool(self._agent_url))

    def _copy(
        self,
    ) -> None:
        text = self.preview.toPlainText()

        if not text:
            return

        QApplication.clipboard().setText(text)

    def _open(
        self,
    ) -> None:
        if not self._agent_url:
            return

        QDesktopServices.openUrl(QUrl(self._agent_url))
