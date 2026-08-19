from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from visual_ai_studio.domain.models import (
    Brief,
    Project,
    ReferenceValue,
)
from visual_ai_studio.domain.output_modes import (
    OutputMode,
    preset_for,
)


class BriefPage(QWidget):
    save_requested = Signal(object)
    generate_requested = Signal(object)
    new_collection_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        self._project: Project | None = None

        self._collection_values: dict[
            str,
            ReferenceValue,
        ] = {}

        title = QLabel("Brief créatif")
        title.setObjectName("pageTitle")

        self.info = QLabel()
        self.info.setObjectName("infoBanner")
        self.info.setWordWrap(True)

        # ------------------------------------------
        # Sortie
        # ------------------------------------------

        self.mode_combo = QComboBox()

        self.mode_combo.addItem(
            "Pinterest",
            OutputMode.PINTEREST.value,
        )

        self.mode_combo.addItem(
            "Instagram",
            OutputMode.INSTAGRAM.value,
        )

        self.mode_combo.addItem(
            "Autre / personnalisé",
            OutputMode.CUSTOM.value,
        )

        self.mode_combo.currentIndexChanged.connect(self._mode_changed)

        # ------------------------------------------
        # Brief principal
        # ------------------------------------------

        self.title_edit = QLineEdit()

        self.collection = QComboBox()
        self.collection.setEditable(True)

        self.style_combo = QComboBox()
        self.style_combo.setEditable(True)

        self.raw_idea = QTextEdit()

        self.raw_idea.setPlaceholderText(
            "Décrivez le visuel à créer, son objectif et le résultat attendu…"
        )

        self.audience = QLineEdit()

        self.text_overlay = QLineEdit()

        self.text_overlay.setPlaceholderText("Laisser vide pour aucun texte dans l'image")

        self.notes = QTextEdit()

        # ------------------------------------------
        # Format
        # ------------------------------------------

        self.width = QSpinBox()
        self.width.setRange(
            0,
            10000,
        )
        self.width.setSpecialValueText("Auto")
        self.width.setSuffix(" px")

        self.height = QSpinBox()
        self.height.setRange(
            0,
            10000,
        )
        self.height.setSpecialValueText("Auto")
        self.height.setSuffix(" px")

        self.aspect_ratio = QLineEdit()

        format_group = QGroupBox("Format")

        format_layout = QFormLayout(format_group)

        format_layout.addRow(
            "Largeur",
            self.width,
        )

        format_layout.addRow(
            "Hauteur",
            self.height,
        )

        format_layout.addRow(
            "Ratio",
            self.aspect_ratio,
        )

        # ------------------------------------------
        # Direction créative
        # ------------------------------------------

        self.advanced_group = QGroupBox("Direction créative avancée")

        advanced_layout = QFormLayout(self.advanced_group)

        self.advanced: dict[
            str,
            QLineEdit,
        ] = {}

        labels = {
            "intent": "Objectif",
            "subject": "Sujet principal",
            "setting": "Décor",
            "ambience": "Ambiance",
            "palette": "Palette",
            "lighting": "Lumière",
            "materials": "Matières",
            "composition": "Composition",
            "detail_level": "Niveau de détail",
            "required_elements": "Éléments obligatoires",
            "forbidden_elements": "Éléments interdits",
            "reference_note": "Note de référence",
        }

        for key, label in labels.items():
            widget = QLineEdit()

            self.advanced[key] = widget

            advanced_layout.addRow(
                label,
                widget,
            )

        reference_row = QHBoxLayout()

        self.reference_image = QLineEdit()
        self.reference_image.setReadOnly(True)

        reference_button = QPushButton("Choisir…")

        reference_button.clicked.connect(self._choose_reference)

        reference_row.addWidget(
            self.reference_image,
            1,
        )

        reference_row.addWidget(reference_button)

        advanced_layout.addRow(
            "Image de référence",
            reference_row,
        )

        # ------------------------------------------
        # Formulaire principal
        # ------------------------------------------

        form = QFormLayout()

        form.addRow(
            "Sortie *",
            self.mode_combo,
        )

        form.addRow(
            "Nom du projet *",
            self.title_edit,
        )

        form.addRow(
            "Collection / campagne",
            self.collection,
        )

        form.addRow(
            "Style",
            self.style_combo,
        )

        form.addRow(
            "Idée / demande *",
            self.raw_idea,
        )

        form.addRow(
            "Audience",
            self.audience,
        )

        form.addRow(
            "Texte dans l'image",
            self.text_overlay,
        )

        form.addRow(
            "Notes",
            self.notes,
        )

        # ------------------------------------------
        # Actions
        # ------------------------------------------

        save = QPushButton("Enregistrer le brouillon")

        save.clicked.connect(self._emit_save)

        generate = QPushButton("Préparer pour Studio Visuel")

        generate.setObjectName("primaryButton")

        generate.clicked.connect(self._emit_generate)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(save)
        buttons.addWidget(generate)

        content = QWidget()

        content_layout = QVBoxLayout(content)

        content_layout.addWidget(title)

        content_layout.addWidget(self.info)

        content_layout.addLayout(form)

        content_layout.addWidget(format_group)

        content_layout.addWidget(self.advanced_group)

        content_layout.addLayout(buttons)

        content_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        self._mode_changed()

    def set_catalog(
        self,
        collections: list[ReferenceValue],
        styles: list[str],
    ) -> None:
        self._collection_values = {item.value: item for item in collections}

        current_collection = self.collection.currentText()

        current_style = self.style_combo.currentText()

        self.collection.blockSignals(True)

        self.collection.clear()

        for item in collections:
            self.collection.addItem(
                item.value,
                item.value,
            )

        self.collection.setCurrentText(current_collection)

        self.collection.blockSignals(False)

        self.style_combo.clear()
        self.style_combo.addItems(styles)

        self.style_combo.setCurrentText(current_style)

    def set_project(
        self,
        project: Project,
    ) -> None:
        self._project = project

        brief = project.brief

        index = self.mode_combo.findData(brief.mode.value)

        if index >= 0:
            self.mode_combo.setCurrentIndex(index)

        self.title_edit.setText(brief.title)

        self.collection.setCurrentText(brief.collection)

        self.style_combo.setCurrentText(brief.style)

        self.raw_idea.setPlainText(brief.raw_idea)

        self.audience.setText(brief.audience)

        self.text_overlay.setText(brief.text_overlay)

        self.notes.setPlainText(brief.notes)

        self.reference_image.setText(brief.reference_image)

        self.width.setValue(brief.target_width or 0)

        self.height.setValue(brief.target_height or 0)

        self.aspect_ratio.setText(brief.aspect_ratio)

        for key, widget in self.advanced.items():
            widget.setText(
                str(
                    getattr(
                        brief,
                        key,
                        "",
                    )
                )
            )

        self._mode_changed(preserve_values=True)

    def brief(
        self,
    ) -> Brief:
        selected_collection = self.collection.currentText().strip()

        reference = self._collection_values.get(selected_collection)

        mode = OutputMode(str(self.mode_combo.currentData()))

        width: int | None = self.width.value()

        if width == 0:
            width = None

        height: int | None = self.height.value()

        if height == 0:
            height = None

        advanced_values = {key: widget.text() for key, widget in self.advanced.items()}

        return Brief(
            title=self.title_edit.text(),
            mode=mode,
            audience=self.audience.text(),
            target_width=width,
            target_height=height,
            aspect_ratio=self.aspect_ratio.text(),
            text_overlay=self.text_overlay.text(),
            collection=selected_collection,
            collection_is_new=bool(reference and reference.is_new),
            style=self.style_combo.currentText(),
            raw_idea=self.raw_idea.toPlainText(),
            notes=self.notes.toPlainText(),
            reference_image=(self.reference_image.text()),
            **advanced_values,
        )

    def _mode_changed(
        self,
        _index: int = 0,
        preserve_values: bool = False,
    ) -> None:
        mode = OutputMode(str(self.mode_combo.currentData()))

        preset = preset_for(mode)

        custom = mode is OutputMode.CUSTOM

        self.width.setEnabled(custom)

        self.height.setEnabled(custom)

        self.aspect_ratio.setEnabled(custom)

        if not custom:
            self.width.setValue(preset.width or 0)

            self.height.setValue(preset.height or 0)

            self.aspect_ratio.setText(preset.aspect_ratio)

        if custom and not preserve_values:
            self.width.setValue(0)
            self.height.setValue(0)
            self.aspect_ratio.clear()

        format_text = f"{preset.label}"

        if preset.width and preset.height:
            format_text += f" • {preset.width} × {preset.height} • {preset.aspect_ratio}"

        if custom:
            format_text += " • dimensions ou ratio à préciser"

        self.info.setText(format_text)

    def _emit_save(
        self,
    ) -> None:
        self.save_requested.emit(self.brief())

    def _emit_generate(
        self,
    ) -> None:
        self.generate_requested.emit(self.brief())

    def _choose_reference(
        self,
    ) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une image de référence",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)",
        )

        if path:
            self.reference_image.setText(path)
