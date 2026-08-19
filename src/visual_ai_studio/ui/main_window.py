from __future__ import annotations

import contextlib
from pathlib import Path

from pydantic import ValidationError
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.application import ApplicationContext
from visual_ai_studio.domain.models import Brief, HumanConfirmations, Project, ValidationReport
from visual_ai_studio.domain.normalization import find_close_values, normalize_value
from visual_ai_studio.domain.statuses import ProjectStatus
from visual_ai_studio.infrastructure.automation_runs import AutomationRunRepository
from visual_ai_studio.infrastructure.settings import SettingsStore
from visual_ai_studio.infrastructure.webhook_client import WebhookClient
from visual_ai_studio.services.export_service import export_project_bundle
from visual_ai_studio.services.submission_service import SubmissionService, can_submit
from visual_ai_studio.ui.brief_page import BriefPage
from visual_ai_studio.ui.dashboard import DashboardPage
from visual_ai_studio.ui.import_page import ImportPage
from visual_ai_studio.ui.prompt_page import PromptPage
from visual_ai_studio.ui.settings_page import SettingsPage
from visual_ai_studio.ui.submission_page import SubmissionPage
from visual_ai_studio.ui.theme import polish_widget_tree


class MainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext) -> None:
        super().__init__()
        self.setObjectName("mainWindow")
        self.context = context
        self.current_project: Project | None = None
        self.report: ValidationReport | None = None
        self.confirmations = HumanConfirmations()
        self.setWindowTitle("Visual AI Studio")
        self.resize(1360, 860)
        self.setMinimumSize(1100, 720)

        self.dashboard = DashboardPage()
        self.brief = BriefPage()
        self.prompt = PromptPage()
        self.import_page = ImportPage()
        self.submission = SubmissionPage()
        self.settings_page = SettingsPage()
        self.pages = QStackedWidget()
        for page in (
            self.dashboard,
            self.brief,
            self.prompt,
            self.import_page,
            self.submission,
            self.settings_page,
        ):
            self.pages.addWidget(page)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 18)
        side_layout.setSpacing(4)
        brand = QLabel("VISUAL AI\nSTUDIO")
        brand.setObjectName("brand")
        side_layout.addWidget(brand)
        nav_items = [
            ("Projets", 0),
            ("Créer", 1),
            ("Paramètres", 5),
        ]

        self.nav_page_indices = [index for _label, index in nav_items]

        self.nav_buttons: list[QPushButton] = []
        for label, index in nav_items:
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.clicked.connect(lambda _checked=False, value=index: self.show_page(value))
            side_layout.addWidget(button)
            self.nav_buttons.append(button)
        side_layout.addStretch()
        self.webhook_indicator = QLabel()
        self.webhook_indicator.setWordWrap(True)
        self.webhook_indicator.setVisible(False)
        central = QWidget()
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(sidebar)
        central_layout.addWidget(self.pages, 1)
        self.setCentralWidget(central)

        self.autosave = QTimer(self)
        self.autosave.setSingleShot(True)
        self.autosave.setInterval(800)
        self.autosave.timeout.connect(self._autosave_brief)
        self._connect_signals()
        self._load_settings()
        self._refresh_dashboard()
        polish_widget_tree(self)
        self.show_page(0)

    def _connect_signals(self) -> None:
        self.dashboard.create_requested.connect(self._create_project)
        self.dashboard.open_requested.connect(self._open_project)
        self.dashboard.duplicate_requested.connect(self._duplicate_project)
        self.dashboard.archive_requested.connect(self._archive_project)
        self.brief.save_requested.connect(self._save_brief)
        self.brief.generate_requested.connect(self._generate_prompt)
        self.prompt.back_requested.connect(lambda: self.show_page(1))
        self.prompt.mark_sent_requested.connect(self._mark_sent)
        self.import_page.import_requested.connect(self._import_package)
        self.import_page.confirmations_changed.connect(self._confirmations_changed)
        self.submission.export_requested.connect(self._export_local)
        self.submission.submit_requested.connect(self._submit)
        self.settings_page.save_requested.connect(self._save_settings)
        self.settings_page.test_requested.connect(self._test_connection)
        self.settings_page.add_collection_requested.connect(self._add_collection)
        self.brief.title_edit.textChanged.connect(self._schedule_autosave)
        self.brief.raw_idea.textChanged.connect(self._schedule_autosave)
        self.brief.notes.textChanged.connect(self._schedule_autosave)
        self.brief.collection.currentTextChanged.connect(self._schedule_autosave)
        self.brief.style_combo.currentTextChanged.connect(self._schedule_autosave)
        for widget in self.brief.advanced.values():
            widget.textChanged.connect(self._schedule_autosave)  # type: ignore[attr-defined]

    def show_page(self, index: int) -> None:
        if index in {1, 2, 3, 4} and self.current_project is None:
            QMessageBox.information(
                self,
                "Visual AI Studio",
                "Sélectionnez ou créez d'abord un projet.",
            )
            index = 0

        self.pages.setCurrentIndex(index)

        active_page = index

        if index in {2, 3, 4}:
            active_page = 1

        for button_index, button in enumerate(self.nav_buttons):
            page_index = self.nav_page_indices[button_index]
            button.setProperty(
                "active",
                page_index == active_page,
            )
            button.style().unpolish(button)
            button.style().polish(button)

    def _load_settings(self) -> None:
        try:
            has_secret = bool(self.context.settings_store.get_secret())
        except Exception:
            has_secret = False
        self.settings_page.set_settings(self.context.settings, has_secret)
        self.prompt.set_agent_url(str(self.context.settings.agent_url or ""))
        self._update_webhook_indicator()

    def _update_webhook_indicator(self) -> None:
        configured = bool(self.context.settings.webhook_url)
        self.webhook_indicator.setText(
            "● Webhook configuré" if configured else "○ Webhook non configuré"
        )
        self.webhook_indicator.setProperty("configured", configured)
        self.submission.update_state(
            self.current_project,
            self.report,
            self.confirmations,
            configured,
        )

    def _refresh_dashboard(self) -> None:
        self.dashboard.set_projects(self.context.project_service.list_projects())
        self.brief.set_catalog(
            self.context.project_service.collections(), self.context.project_service.styles()
        )

    def _create_project(self) -> None:
        project = self.context.project_service.create_project()
        self._set_project(project)
        self.show_page(1)

    def _open_project(self, project_id: str) -> None:
        project = self.context.project_service.get(project_id)
        if project:
            self._set_project(project)
            self.show_page(1)

    def _set_project(self, project: Project) -> None:
        self.current_project = project
        self.report = None
        self.confirmations = HumanConfirmations()
        self.brief.set_project(project)
        self.prompt.set_project(project)
        self._update_webhook_indicator()

    def _duplicate_project(self, project_id: str) -> None:
        project = self.context.project_service.get(project_id)
        if project:
            self.context.project_service.duplicate(project)
            self._refresh_dashboard()

    def _archive_project(self, project_id: str) -> None:
        project = self.context.project_service.get(project_id)
        if (
            project
            and QMessageBox.question(self, "Archiver", f"Archiver « {project.title} » ?")
            == QMessageBox.StandardButton.Yes
        ):
            self.context.project_service.archive(project)
            if self.current_project and self.current_project.id == project.id:
                self.current_project = None
            self._refresh_dashboard()

    def _schedule_autosave(self) -> None:
        if self.current_project and self.pages.currentWidget() is self.brief:
            self.autosave.start()

    def _autosave_brief(self) -> None:
        if self.current_project:
            with contextlib.suppress(ValueError):
                self._save_brief(self.brief.brief(), quiet=True)

    def _prepare_collection(self, brief: Brief) -> Brief:
        if not brief.collection:
            return brief
        values = self.context.project_service.collections()
        exact = next(
            (item for item in values if item.normalized_value == normalize_value(brief.collection)),
            None,
        )
        if exact:
            brief.collection = exact.value
            brief.collection_is_new = exact.is_new
            return brief
        similar = find_close_values(brief.collection, [item.value for item in values])
        if similar:
            answer = QMessageBox.question(
                self,
                "Collection proche détectée",
                "Valeur(s) proche(s) : "
                + ", ".join(similar)
                + "\nCréer tout de même la collection ?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                raise ValueError(
                    "Choisissez une collection existante ou confirmez la nouvelle valeur."
                )
        reference, _ = self.context.project_service.add_collection(brief.collection)
        brief.collection = reference.value
        brief.collection_is_new = True
        self._refresh_dashboard()
        return brief

    def _save_brief(self, brief: Brief, quiet: bool = False) -> None:
        if self.current_project is None:
            return
        try:
            brief = self._prepare_collection(brief)
            had_prompt = bool(self.current_project.prompt_text)
            self.current_project = self.context.project_service.save_brief(
                self.current_project, brief
            )
            self.prompt.set_project(self.current_project)
            self._refresh_dashboard()
            if had_prompt and not self.current_project.prompt_text and not quiet:
                QMessageBox.warning(
                    self,
                    "Prompt invalidé",
                    "Le brief a changé : une nouvelle version a été créée "
                    + "et le prompt doit être régénéré.",
                )
        except ValueError as exc:
            if not quiet:
                QMessageBox.warning(self, "Brief incomplet", str(exc))
            raise

    def _generate_prompt(self, brief: Brief) -> None:
        if self.current_project is None:
            return
        try:
            self._save_brief(brief)
            self.current_project = self.context.project_service.generate_prompt(
                self.current_project
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Prompt impossible", str(exc))
            return
        self.prompt.set_project(self.current_project)
        self._refresh_dashboard()
        self.show_page(2)

    def _mark_sent(self) -> None:
        if self.current_project is None:
            return
        try:
            self.current_project = self.context.project_service.mark_sent_to_agent(
                self.current_project
            )
            self._refresh_dashboard()
            self.show_page(3)
        except ValueError as exc:
            QMessageBox.warning(self, "Action impossible", str(exc))

    def _import_package(self, raw_paths: list[object]) -> None:
        if self.current_project is None:
            return
        paths = [Path(str(path)) for path in raw_paths]
        try:
            self.report = self.context.artifact_service.import_package(self.current_project, paths)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Import impossible", str(exc))
            return
        self.import_page.set_report(self.report)
        self._update_webhook_indicator()
        self.show_page(3)

    def _confirmations_changed(
        self,
        confirmations: HumanConfirmations,
    ) -> None:
        self.confirmations = confirmations

        ready = bool(
            self.current_project
            and can_submit(
                self.report,
                confirmations,
            )
        )

        if ready and self.current_project is not None:
            self.current_project.status = ProjectStatus.VALIDATED
            self.context.project_repository.save(self.current_project)
            self._refresh_dashboard()

        self._update_webhook_indicator()

        if ready:
            self.show_page(4)

    def _save_settings(self, settings: object, secret: str) -> None:
        try:
            self.context.settings = type(self.context.settings).model_validate(settings)
            self.context.settings_store.save(self.context.settings)
            if secret:
                self.context.settings_store.set_secret(secret)
            self.context.artifact_service.projects_dir = self.context.settings.projects_dir
            self.context.artifact_service.max_bytes = (
                self.context.settings.max_file_size_mb * 1024 * 1024
            )
        except (OSError, ValidationError, Exception) as exc:
            self.settings_page.feedback.setText(f"Erreur : {exc}")
            return
        self.settings_page.feedback.setText("Paramètres enregistrés.")
        self.prompt.set_agent_url(str(self.context.settings.agent_url or ""))
        self._update_webhook_indicator()

    def _test_connection(self, settings: object, secret: str) -> None:
        try:
            validated = type(self.context.settings).model_validate(settings)
        except ValidationError as exc:
            self.settings_page.feedback.setText(str(exc))
            return
        if not validated.webhook_url:
            self.settings_page.feedback.setText("Renseignez l'URL du webhook.")
            return
        client = WebhookClient(
            str(validated.webhook_url),
            validated.auth_header_name,
            secret or self._secret(),
            validated.timeout_seconds,
        )
        outcome = client.test_connection()
        self.settings_page.feedback.setText(outcome.message)

    def _secret(self) -> str:
        try:
            return SettingsStore.get_secret()
        except Exception:
            return ""

    def _add_collection(self, value: str) -> None:
        try:
            reference, similar = self.context.project_service.add_collection(value)
        except ValueError as exc:
            self.settings_page.feedback.setText(str(exc))
            return
        note = f" Proches détectées : {', '.join(similar)}." if similar else ""
        self.settings_page.feedback.setText(
            f"Collection « {reference.value} » ajoutée localement "
            f"(synchronisation en attente).{note}"
        )
        self.settings_page.new_collection.clear()
        self._refresh_dashboard()

    def _export_local(self) -> None:
        if self.current_project is None:
            return

        if self.report is None:
            return

        if not can_submit(
            self.report,
            self.confirmations,
        ):
            QMessageBox.warning(
                self,
                "Export impossible",
                "Le résultat doit être validé avant l'export.",
            )
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choisir le dossier d'export",
        )

        if not folder:
            return

        try:
            target = export_project_bundle(
                self.current_project,
                self.report.artifacts,
                Path(folder),
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Export impossible",
                str(exc),
            )
            return

        self.submission.set_local_export(str(target))

    def _submit(self) -> None:
        if self.current_project is None or self.report is None:
            return
        settings = self.context.settings
        if not settings.webhook_url:
            QMessageBox.warning(self, "Webhook non configuré", "Renseignez l'URL du webhook.")
            return
        progress = QProgressDialog("Envoi sécurisé du paquet…", "", 0, 0, self)
        progress.setWindowTitle("Visual AI Studio")
        progress.setCancelButton(None)
        progress.show()
        client = WebhookClient(
            str(settings.webhook_url),
            settings.auth_header_name,
            self._secret(),
            settings.timeout_seconds,
        )
        service = SubmissionService(
            client,
            AutomationRunRepository(self.context.database),
            self.context.project_repository,
        )
        outcome = service.submit(
            self.current_project,
            self.report.artifacts,
            self.report,
            self.confirmations,
        )
        progress.close()
        self.submission.set_outcome(outcome)
        self._refresh_dashboard()
