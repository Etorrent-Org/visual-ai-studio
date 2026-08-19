from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.infrastructure.settings import (
    AppSettings,
)


class SettingsPage(QWidget):
    """
    Page volontairement minimale.

    Seul le dossier des projets est exposé dans
    l'interface.

    Les autres paramètres techniques restent
    disponibles en interne pour préserver la
    compatibilité du workflow existant.
    """

    save_requested = Signal(object, str)

    # Signaux conservés pour compatibilité
    # avec MainWindow.
    test_requested = Signal(object, str)
    add_collection_requested = Signal(str)

    def __init__(
        self,
    ) -> None:
        super().__init__()

        self._settings = AppSettings()

        # ------------------------------------------
        # En-tête
        # ------------------------------------------

        title = QLabel(
            "Paramètres"
        )

        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Choisissez l’emplacement de stockage "
            "de vos projets."
        )

        subtitle.setObjectName(
            "muted"
        )

        # ------------------------------------------
        # Carte stockage
        # ------------------------------------------

        card = QFrame()

        card.setObjectName(
            "settingsCard"
        )

        card_layout = QVBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            22,
            20,
            22,
            22,
        )

        card_layout.setSpacing(
            14
        )

        section_title = QLabel(
            "Stockage local"
        )

        section_title.setObjectName(
            "sectionTitle"
        )

        section_text = QLabel(
            "Emplacement utilisé par Visual AI Studio "
            "pour conserver les projets et leurs fichiers."
        )

        section_text.setObjectName(
            "muted"
        )

        section_text.setWordWrap(
            True
        )

        folder_label = QLabel(
            "Dossier des projets"
        )

        folder_label.setObjectName(
            "fieldLabel"
        )

        self.projects_dir = QLineEdit()

        self.projects_dir.setPlaceholderText(
            "Choisissez un dossier…"
        )

        choose = QPushButton(
            "Choisir…"
        )

        choose.setMinimumWidth(
            100
        )

        choose.clicked.connect(
            self._choose_projects_dir
        )

        folder_row = QHBoxLayout()

        folder_row.setSpacing(
            8
        )

        folder_row.addWidget(
            self.projects_dir,
            1,
        )

        folder_row.addWidget(
            choose
        )

        privacy = QLabel(
            "Les données de travail restent stockées "
            "localement sur votre ordinateur."
        )

        privacy.setObjectName(
            "settingsHint"
        )

        privacy.setWordWrap(
            True
        )

        card_layout.addWidget(
            section_title
        )

        card_layout.addWidget(
            section_text
        )

        card_layout.addSpacing(
            6
        )

        card_layout.addWidget(
            folder_label
        )

        card_layout.addLayout(
            folder_row
        )

        card_layout.addWidget(
            privacy
        )

        # ------------------------------------------
        # Action
        # ------------------------------------------

        save = QPushButton(
            "Enregistrer"
        )

        save.setObjectName(
            "primaryButton"
        )

        save.setMinimumWidth(
            120
        )

        save.clicked.connect(
            self._emit_save
        )

        actions = QHBoxLayout()

        actions.addStretch()

        actions.addWidget(
            save
        )

        self.feedback = QLabel(
            ""
        )

        self.feedback.setObjectName(
            "settingsFeedback"
        )

        self.feedback.setWordWrap(
            True
        )

        # ------------------------------------------
        # Layout principal
        # ------------------------------------------

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            28,
            26,
            28,
            24,
        )

        layout.setSpacing(
            14
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            4
        )

        layout.addWidget(
            card
        )

        layout.addStretch()

        layout.addWidget(
            self.feedback
        )

        layout.addLayout(
            actions
        )

        # ------------------------------------------
        # Compatibilité interne
        # ------------------------------------------
        #
        # Ces champs ne sont PAS affichés.
        # Ils permettent de conserver l'API actuelle
        # sans modifier MainWindow ou AppSettings.
        # ------------------------------------------

        self.webhook = QLineEdit(
            self
        )

        self.secret = QLineEdit(
            self
        )

        self.header = QLineEdit(
            self
        )

        self.timeout = QDoubleSpinBox(
            self
        )

        self.agent_url = QLineEdit(
            self
        )

        self.max_file = QSpinBox(
            self
        )

        self.new_collection = QLineEdit(
            self
        )

        self._compat_widgets = [
            self.webhook,
            self.secret,
            self.header,
            self.timeout,
            self.agent_url,
            self.max_file,
            self.new_collection,
        ]

        for widget in self._compat_widgets:
            widget.hide()

    def set_settings(
        self,
        settings: AppSettings,
        has_secret: bool,
    ) -> None:
        self._settings = settings.model_copy(
            deep=True
        )

        self.projects_dir.setText(
            str(
                settings.projects_dir
            )
        )

        # Maintien silencieux des paramètres
        # techniques existants.

        self.webhook.setText(
            str(
                settings.webhook_url
                or ""
            )
        )

        self.header.setText(
            settings.auth_header_name
        )

        self.timeout.setValue(
            settings.timeout_seconds
        )

        self.agent_url.setText(
            str(
                settings.agent_url
                or ""
            )
        )

        self.max_file.setValue(
            settings.max_file_size_mb
        )

        if has_secret:
            self.secret.setPlaceholderText(
                "Secret configuré"
            )

        if not has_secret:
            self.secret.setPlaceholderText(
                ""
            )

    def values(
        self,
    ) -> AppSettings:
        path = (
            self.projects_dir.text()
            .strip()
        )

        if not path:
            path = str(
                self._settings.projects_dir
            )

        return self._settings.model_copy(
            update={
                "projects_dir": Path(path),
            },
            deep=True,
        )

    def _emit_save(
        self,
    ) -> None:
        self.save_requested.emit(
            self.values(),
            "",
        )

    def _choose_projects_dir(
        self,
    ) -> None:
        current = (
            self.projects_dir.text()
            .strip()
        )

        path = (
            QFileDialog.getExistingDirectory(
                self,
                "Choisir le dossier des projets",
                current,
            )
        )

        if path:
            self.projects_dir.setText(
                path
            )