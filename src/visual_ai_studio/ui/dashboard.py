from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.domain.models import (
    Project,
)
from visual_ai_studio.domain.statuses import (
    ProjectStatus,
)


class MetricCard(QFrame):
    def __init__(
        self,
        label: str,
        hint: str,
    ) -> None:
        super().__init__()

        self.setObjectName(
            "metricCard"
        )

        self.value = QLabel(
            "0"
        )
        self.value.setObjectName(
            "metricValue"
        )

        self.label = QLabel(
            label
        )
        self.label.setObjectName(
            "metricLabel"
        )

        self.hint = QLabel(
            hint
        )
        self.hint.setObjectName(
            "metricHint"
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        layout.setSpacing(
            1
        )

        layout.addWidget(
            self.value
        )

        layout.addWidget(
            self.label
        )

        layout.addWidget(
            self.hint
        )

    def set_value(
        self,
        value: int,
    ) -> None:
        self.value.setText(
            str(value)
        )


class DashboardPage(QWidget):
    create_requested = Signal()
    open_requested = Signal(str)
    duplicate_requested = Signal(str)
    archive_requested = Signal(str)

    def __init__(
        self,
    ) -> None:
        super().__init__()

        self._projects: list[
            Project
        ] = []

        # ------------------------------------------
        # Header
        # ------------------------------------------

        title = QLabel(
            "Projets"
        )
        title.setObjectName(
            "pageTitle"
        )

        subtitle = QLabel(
            "Brief → Studio Visuel → validation → export"
        )
        subtitle.setObjectName(
            "muted"
        )

        title_block = QVBoxLayout()
        title_block.setSpacing(3)

        title_block.addWidget(
            title
        )

        title_block.addWidget(
            subtitle
        )

        self.status_filter = QComboBox()
        self.status_filter.setObjectName(
            "statusFilter"
        )

        self.status_filter.setMinimumWidth(
            170
        )

        self.status_filter.setMaximumWidth(
            190
        )

        self.status_filter.setFixedHeight(
            36
        )

        self.status_filter.setMaxVisibleItems(
            6
        )

        self.status_filter.addItem(
            "Tous les statuts",
            "",
        )

        for status in ProjectStatus:
            self.status_filter.addItem(
                status.value,
                status.value,
            )

        self.status_filter.view().setMaximumHeight(
            150
        )

        self.status_filter.currentIndexChanged.connect(
            self._apply_filters
        )

        self.new_button = QPushButton(
            "Nouveau projet"
        )

        self.new_button.setObjectName(
            "primaryButton"
        )

        self.new_button.setMinimumWidth(
            138
        )

        self.new_button.clicked.connect(
            self.create_requested
        )

        header = QHBoxLayout()

        header.addLayout(
            title_block
        )

        header.addStretch()

        header.addWidget(
            self.status_filter
        )

        header.addWidget(
            self.new_button
        )

        # ------------------------------------------
        # Metrics
        # ------------------------------------------

        self.total_metric = MetricCard(
            "Projets",
            "Total",
        )

        self.brief_metric = MetricCard(
            "Brief",
            "À préparer",
        )

        self.validated_metric = MetricCard(
            "Validé",
            "Prêts ou exportés",
        )

        self.archived_metric = MetricCard(
            "Archivé",
            "Historique",
        )

        metrics = QHBoxLayout()
        metrics.setSpacing(12)

        metrics.addWidget(
            self.total_metric,
            1,
        )

        metrics.addWidget(
            self.brief_metric,
            1,
        )

        metrics.addWidget(
            self.validated_metric,
            1,
        )

        metrics.addWidget(
            self.archived_metric,
            1,
        )

        # ------------------------------------------
        # Projects panel
        # ------------------------------------------

        panel = QFrame()
        panel.setObjectName(
            "panel"
        )

        panel_layout = QVBoxLayout(
            panel
        )

        panel_layout.setContentsMargins(
            16,
            15,
            16,
            14,
        )

        panel_layout.setSpacing(
            12
        )

        list_title = QLabel(
            "Liste des projets"
        )

        list_title.setObjectName(
            "sectionTitle"
        )

        self.search = QLineEdit()

        self.search.setObjectName(
            "searchField"
        )

        self.search.setPlaceholderText(
            "Rechercher par nom, collection ou style…"
        )

        self.search.setClearButtonEnabled(
            True
        )

        self.search.textChanged.connect(
            self._apply_filters
        )

        list_header = QHBoxLayout()

        list_header.addWidget(
            list_title
        )

        list_header.addStretch()

        list_header.addWidget(
            self.search,
            1,
        )

        self.table = QTableWidget(
            0,
            5,
        )

        self.table.setObjectName(
            "projectTable"
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Projet",
                "Collection",
                "Style",
                "Statut",
                "Dernière modification",
            ]
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setShowGrid(
            False
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.verticalHeader().setDefaultSectionSize(
            46
        )

        header_view = (
            self.table.horizontalHeader()
        )

        header_view.setMinimumHeight(
            40
        )

        header_view.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        header_view.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header_view.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header_view.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header_view.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.table.doubleClicked.connect(
            lambda _index: self._emit_open()
        )

        self.table.itemSelectionChanged.connect(
            self._update_actions
        )

        # ------------------------------------------
        # Actions
        # ------------------------------------------

        self.open_button = QPushButton(
            "Ouvrir"
        )

        self.open_button.setObjectName(
            "primaryButton"
        )

        self.open_button.clicked.connect(
            self._emit_open
        )

        self.duplicate_button = QPushButton(
            "Dupliquer"
        )

        self.duplicate_button.clicked.connect(
            self._emit_duplicate
        )

        self.archive_button = QPushButton(
            "Archiver"
        )

        self.archive_button.setObjectName(
            "dangerButton"
        )

        self.archive_button.clicked.connect(
            self._emit_archive
        )

        actions = QHBoxLayout()

        actions.addWidget(
            self.open_button
        )

        actions.addWidget(
            self.duplicate_button
        )

        actions.addWidget(
            self.archive_button
        )

        actions.addStretch()

        panel_layout.addLayout(
            list_header
        )

        panel_layout.addWidget(
            self.table,
            1,
        )

        panel_layout.addLayout(
            actions
        )

        # ------------------------------------------
        # Main layout
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
            18
        )

        layout.addLayout(
            header
        )

        layout.addLayout(
            metrics
        )

        layout.addWidget(
            panel,
            1,
        )

        self._update_actions()

    def set_projects(
        self,
        projects: list[Project],
    ) -> None:
        self._projects = projects

        self._update_metrics()
        self._apply_filters()

    def _update_metrics(
        self,
    ) -> None:
        total = len(
            self._projects
        )

        brief_count = sum(
            1
            for project in self._projects
            if project.status
            is ProjectStatus.BRIEF
        )

        validated_count = sum(
            1
            for project in self._projects
            if project.status
            is ProjectStatus.VALIDATED
        )

        archived_count = sum(
            1
            for project in self._projects
            if project.status
            is ProjectStatus.ARCHIVED
        )

        self.total_metric.set_value(
            total
        )

        self.brief_metric.set_value(
            brief_count
        )

        self.validated_metric.set_value(
            validated_count
        )

        self.archived_metric.set_value(
            archived_count
        )

    def _apply_filters(
        self,
    ) -> None:
        needle = (
            self.search.text()
            .casefold()
            .strip()
        )

        status = str(
            self.status_filter.currentData()
            or ""
        )

        visible: list[
            Project
        ] = []

        for project in self._projects:
            status_matches = (
                not status
                or project.status.value
                == status
            )

            searchable = " ".join(
                [
                    project.title,
                    project.brief.collection,
                    project.brief.style,
                ]
            ).casefold()

            text_matches = (
                not needle
                or needle in searchable
            )

            if (
                status_matches
                and text_matches
            ):
                visible.append(
                    project
                )

        self.table.setRowCount(
            len(visible)
        )

        status_colors = {
            ProjectStatus.BRIEF.value: (
                "#60A5FA"
            ),
            ProjectStatus.VALIDATED.value: (
                "#4ADE80"
            ),
            ProjectStatus.ARCHIVED.value: (
                "#94A3B8"
            ),
        }

        for row, project in enumerate(
            visible
        ):
            values = [
                project.title,
                project.brief.collection,
                project.brief.style,
                project.status.value,
                project.updated_at.astimezone().strftime(
                    "%d/%m/%Y %H:%M"
                ),
            ]

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    value
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    str(project.id),
                )

                if column == 3:
                    color = status_colors.get(
                        project.status.value,
                        "#CBD5E1",
                    )

                    item.setForeground(
                        QColor(color)
                    )

                    font = item.font()
                    font.setBold(True)

                    item.setFont(
                        font
                    )

                self.table.setItem(
                    row,
                    column,
                    item,
                )

        self._update_actions()

    def _selected_id(
        self,
    ) -> str:
        row = (
            self.table.currentRow()
        )

        if row < 0:
            return ""

        item = self.table.item(
            row,
            0,
        )

        if item is None:
            return ""

        return str(
            item.data(
                Qt.ItemDataRole.UserRole
            )
        )

    def _update_actions(
        self,
    ) -> None:
        selected = bool(
            self._selected_id()
        )

        self.open_button.setEnabled(
            selected
        )

        self.duplicate_button.setEnabled(
            selected
        )

        self.archive_button.setEnabled(
            selected
        )

    def _emit_open(
        self,
    ) -> None:
        project_id = (
            self._selected_id()
        )

        if project_id:
            self.open_requested.emit(
                project_id
            )

    def _emit_duplicate(
        self,
    ) -> None:
        project_id = (
            self._selected_id()
        )

        if project_id:
            self.duplicate_requested.emit(
                project_id
            )

    def _emit_archive(
        self,
    ) -> None:
        project_id = (
            self._selected_id()
        )

        if project_id:
            self.archive_requested.emit(
                project_id
            )