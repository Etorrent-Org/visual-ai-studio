from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.domain.models import (
    HumanConfirmations,
    ValidationReport,
)
from visual_ai_studio.domain.statuses import (
    ArtifactType,
)


class DropZone(QFrame):
    paths_dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()

        self.setAcceptDrops(True)
        self.setObjectName("dropZone")

        label = QLabel("Déposez ici les fichiers générés")

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)

        layout.addWidget(label)

    def dragEnterEvent(
        self,
        event: QDragEnterEvent,
    ) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(
        self,
        event: QDropEvent,
    ) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls()]

        expanded: list[Path] = []

        for path in paths:
            if path.is_dir():
                expanded.extend(path.iterdir())

            if path.is_file():
                expanded.append(path)

        self.paths_dropped.emit(expanded)

        event.acceptProposedAction()


class ImportPage(QWidget):
    import_requested = Signal(list)
    confirmations_changed = Signal(object)

    def __init__(
        self,
    ) -> None:
        super().__init__()

        # ------------------------------------------
        # En-tête
        # ------------------------------------------

        title = QLabel("Validation du résultat")

        title.setObjectName("pageTitle")

        subtitle = QLabel("Contrôlez le résultat avant de valider le projet.")

        subtitle.setObjectName("muted")

        # ------------------------------------------
        # Import
        # ------------------------------------------

        self.drop_zone = DropZone()

        self.drop_zone.paths_dropped.connect(self.import_requested)

        choose_files = QPushButton("Choisir des fichiers…")

        choose_files.clicked.connect(self._choose_files)

        choose_folder = QPushButton("Choisir un dossier…")

        choose_folder.clicked.connect(self._choose_folder)

        chooser = QHBoxLayout()

        chooser.addWidget(choose_files)

        chooser.addWidget(choose_folder)

        chooser.addStretch()

        # ------------------------------------------
        # Résultats validation
        # ------------------------------------------

        self.result_list = QListWidget()

        self.result_list.setMaximumHeight(190)

        # ------------------------------------------
        # Galerie images
        # ------------------------------------------

        gallery_title = QLabel("Aperçu des images")

        gallery_title.setObjectName("sectionTitle")

        self.gallery_scroll = QScrollArea()

        self.gallery_scroll.setWidgetResizable(True)

        self.gallery_scroll.setMinimumHeight(370)

        self.gallery_host = QWidget()

        self.gallery_layout = QGridLayout(self.gallery_host)

        self.gallery_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.gallery_layout.setHorizontalSpacing(12)

        self.gallery_layout.setVerticalSpacing(12)

        self.gallery_layout.setColumnStretch(
            0,
            1,
        )

        self.gallery_layout.setColumnStretch(
            1,
            1,
        )

        self.gallery_scroll.setWidget(self.gallery_host)

        self.preview_labels: list[QLabel] = []

        # ------------------------------------------
        # Validation humaine
        # ------------------------------------------

        self.approved = QCheckBox("Je valide ce résultat")

        self.approved.toggled.connect(self._emit_confirmations)

        # ------------------------------------------
        # Layout
        # ------------------------------------------

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            28,
            26,
            28,
            24,
        )

        layout.setSpacing(12)

        layout.addWidget(title)

        layout.addWidget(subtitle)

        layout.addWidget(self.drop_zone)

        layout.addLayout(chooser)

        layout.addWidget(self.result_list)

        layout.addWidget(gallery_title)

        layout.addWidget(
            self.gallery_scroll,
            1,
        )

        layout.addWidget(self.approved)

    def confirmations(
        self,
    ) -> HumanConfirmations:
        return HumanConfirmations(approved=(self.approved.isChecked()))

    def set_report(
        self,
        report: ValidationReport,
    ) -> None:
        self.result_list.clear()

        self._clear_gallery()

        if report.automatic_checks_passed:
            self.result_list.addItem("✓ Contrôles automatiques conformes.")

        for issue in report.issues:
            prefix = "✗"

            if not issue.blocking:
                prefix = "⚠"

            self.result_list.addItem(f"{prefix} {issue.message}")

        image_artifacts = []

        for artifact in report.artifacts:
            self.result_list.addItem(artifact.filename)

            if artifact.artifact_type is ArtifactType.IMAGE:
                image_artifacts.append(artifact)

        for index, artifact in enumerate(image_artifacts):
            self._add_preview(
                index,
                artifact.filename,
                Path(artifact.local_path),
            )

        if not image_artifacts:
            empty = QLabel("Aucune image disponible pour l'aperçu.")

            empty.setObjectName("muted")

            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.gallery_layout.addWidget(
                empty,
                0,
                0,
                1,
                2,
            )

    def _clear_gallery(
        self,
    ) -> None:
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.preview_labels.clear()

    def _add_preview(
        self,
        index: int,
        filename: str,
        path: Path,
    ) -> None:
        card = QFrame()

        card.setObjectName("previewCard")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        card_layout.setSpacing(8)

        preview = QLabel()

        preview.setObjectName("preview")

        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preview.setMinimumSize(
            240,
            300,
        )

        pixmap = QPixmap(str(path))

        if not pixmap.isNull():
            scaled = pixmap.scaled(
                380,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            preview.setPixmap(scaled)

        if pixmap.isNull():
            preview.setText("Aperçu indisponible")

        caption = QLabel(filename)

        caption.setObjectName("previewCaption")

        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

        caption.setWordWrap(True)

        card_layout.addWidget(
            preview,
            1,
        )

        card_layout.addWidget(caption)

        row = index // 2
        column = index % 2

        self.gallery_layout.addWidget(
            card,
            row,
            column,
        )

        self.preview_labels.append(preview)

    def _choose_files(
        self,
    ) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Choisir les fichiers générés",
            "",
            ("Fichiers pris en charge (*.png *.jpg *.jpeg *.webp *.md *.txt *.json)"),
        )

        if paths:
            self.import_requested.emit([Path(path) for path in paths])

    def _choose_folder(
        self,
    ) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choisir le dossier des fichiers générés",
        )

        if folder:
            path = Path(folder)

            self.import_requested.emit(list(path.iterdir()))

    def _emit_confirmations(
        self,
    ) -> None:
        self.confirmations_changed.emit(self.confirmations())
