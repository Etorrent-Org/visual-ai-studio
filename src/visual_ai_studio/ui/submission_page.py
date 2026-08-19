from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.domain.models import (
    HumanConfirmations,
    Project,
    SubmissionOutcome,
    ValidationReport,
)
from visual_ai_studio.services.submission_service import can_submit


class SubmissionPage(QWidget):
    export_requested = Signal()
    submit_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        title = QLabel("Export")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Exportez le résultat localement ou utilisez un webhook facultatif.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)

        self.summary = QLabel("Aucun projet validé.")

        self.files = QListWidget()

        self.validation = QLabel("Validez d'abord le résultat.")
        self.validation.setWordWrap(True)

        self.export_button = QPushButton("Exporter localement")
        self.export_button.setObjectName("primaryButton")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_requested)

        self.submit_button = QPushButton("Envoyer au webhook")
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit_requested)

        self.response = QLabel("")
        self.response.setWordWrap(True)

        actions = QHBoxLayout()
        actions.addWidget(self.export_button)
        actions.addWidget(self.submit_button)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.summary)
        layout.addWidget(self.files, 1)
        layout.addWidget(self.validation)
        layout.addLayout(actions)
        layout.addWidget(self.response)

    def update_state(
        self,
        project: Project | None,
        report: ValidationReport | None,
        confirmations: HumanConfirmations,
        configured: bool,
    ) -> None:
        self.files.clear()
        self.export_button.setEnabled(False)
        self.submit_button.setEnabled(False)

        if project is None:
            self.summary.setText("Aucun projet sélectionné.")
            self.validation.setText("Validez d'abord un résultat.")
            return

        self.summary.setText(f"{project.title} • version {project.version}")

        if report is not None:
            for artifact in report.artifacts:
                self.files.addItem(artifact.filename)

        ready = can_submit(
            report,
            confirmations,
        )

        if ready:
            self.export_button.setEnabled(True)
            self.validation.setText("Projet validé : export local disponible.")

        if ready and configured:
            self.submit_button.setEnabled(True)
            self.validation.setText("Projet validé : export local ou webhook disponible.")

    def set_local_export(
        self,
        path: str,
    ) -> None:
        self.response.setText(f"Export local créé : {path}")

    def set_outcome(
        self,
        outcome: SubmissionOutcome,
    ) -> None:
        details = [outcome.message]

        if outcome.execution_id:
            details.append(f"Exécution distante : {outcome.execution_id}")

        if outcome.remote_url:
            details.append(f"URL distante : {outcome.remote_url}")

        if outcome.unknown:
            details.append("Le statut distant est inconnu.")

        self.response.setText("\n".join(details))
