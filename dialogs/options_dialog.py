from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from editor.tag_insert import wordpress_mode_label_keys
from localization.translator import Translator
from settings.settings_manager import EditorSettings


@dataclass(frozen=True)
class OptionsDialogValues:
    wordpress_mode_label_key: str
    hover_hints_enabled: bool
    backup_folder: str
    font_family: str
    font_size: int


class OptionsDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        settings: EditorSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.translator = translator
        self.wordpress_mode_keys = wordpress_mode_label_keys()

        self.tabs = QTabWidget(self)
        self.wordpress_mode_combo = QComboBox(self)
        self.hover_hints_checkbox = QCheckBox(self)
        self.backup_folder_edit = QLineEdit(self)
        self.backup_folder_button = QPushButton(self)
        self.font_family_combo = QComboBox(self)
        self.font_size_spin = QSpinBox(self)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )

        self._create_tabs()
        self._connect_signals()
        self.apply_language()
        self.set_values(settings)

    def apply_language(self) -> None:
        self.setWindowTitle(self.translator.text("options.title"))
        for index, key in enumerate(
            (
                "options.tab.general",
                "options.tab.view",
                "options.tab.tag_insert",
                "options.tab.backup",
                "options.tab.font",
                "options.tab.search",
            )
        ):
            self.tabs.setTabText(index, self.translator.text(key))

        self.hover_hints_checkbox.setText(
            self.translator.text("options.hover_hints_enabled")
        )
        self.backup_folder_button.setText(self.translator.text("options.browse"))

    def set_values(self, settings: EditorSettings) -> None:
        self.wordpress_mode_combo.clear()
        for mode_label_key in self.wordpress_mode_keys:
            self.wordpress_mode_combo.addItem(
                self.translator.text(mode_label_key),
                mode_label_key,
            )
        mode_index = self.wordpress_mode_combo.findData(settings.wordpress_mode_label_key)
        self.wordpress_mode_combo.setCurrentIndex(max(mode_index, 0))
        self.hover_hints_checkbox.setChecked(settings.hover_hints_enabled)
        self.backup_folder_edit.setText(settings.backup_folder)
        self._set_font_families(settings.font_family)
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(settings.font_size)

    def values(self) -> OptionsDialogValues:
        return OptionsDialogValues(
            wordpress_mode_label_key=str(self.wordpress_mode_combo.currentData()),
            hover_hints_enabled=self.hover_hints_checkbox.isChecked(),
            backup_folder=self.backup_folder_edit.text().strip(),
            font_family=self.font_family_combo.currentText(),
            font_size=self.font_size_spin.value(),
        )

    def _create_tabs(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.addWidget(self.tabs)
        root_layout.addWidget(self.button_box)
        self.setLayout(root_layout)

        self.tabs.addTab(self._general_tab(), "")
        self.tabs.addTab(self._view_tab(), "")
        self.tabs.addTab(self._tag_insert_tab(), "")
        self.tabs.addTab(self._backup_tab(), "")
        self.tabs.addTab(self._font_tab(), "")
        self.tabs.addTab(self._search_tab(), "")
        self.resize(620, 420)

    def _general_tab(self) -> QWidget:
        return self._placeholder_tab(
            (
                "options.item.language",
                "options.item.startup_restore",
                "options.item.default_encoding",
                "options.item.newline",
            )
        )

    def _view_tab(self) -> QWidget:
        return self._placeholder_tab(
            (
                "options.item.line_numbers",
                "options.item.word_wrap",
                "options.item.ruler",
                "options.item.visible_spaces",
                "options.item.theme",
            )
        )

    def _tag_insert_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        layout.addRow(
            self.translator.text("options.wordpress_mode"),
            self.wordpress_mode_combo,
        )
        layout.addRow(self.hover_hints_checkbox)
        layout.addRow(self._disabled_checkbox("options.item.user_dictionary"))
        layout.addRow(self._disabled_checkbox("options.item.dictionary_check"))
        tab.setLayout(layout)
        return tab

    def _backup_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.backup_folder_edit)
        folder_layout.addWidget(self.backup_folder_button)
        layout.addRow(self.translator.text("options.backup_folder"), folder_layout)
        layout.addRow(self._disabled_checkbox("options.item.local_settings_file"))
        layout.addRow(self._disabled_checkbox("options.item.no_environment_changes"))
        layout.addRow(self._disabled_checkbox("options.item.backup_retention"))
        layout.addRow(self._disabled_checkbox("options.item.backup_restore_mode"))
        tab.setLayout(layout)
        return tab

    def _font_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        layout.addRow(self.translator.text("options.font_family"), self.font_family_combo)
        layout.addRow(self.translator.text("options.font_size"), self.font_size_spin)
        layout.addRow(self._disabled_checkbox("options.item.tab_width"))
        tab.setLayout(layout)
        return tab

    def _search_tab(self) -> QWidget:
        return self._placeholder_tab(
            (
                "options.item.search_marker_color",
                "options.item.current_match_color",
                "options.item.regex_lint",
            )
        )

    def _placeholder_tab(self, translation_keys: tuple[str, ...]) -> QWidget:
        tab = QWidget(self)
        layout = QVBoxLayout()
        for translation_key in translation_keys:
            layout.addWidget(self._disabled_checkbox(translation_key))
        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _disabled_checkbox(self, translation_key: str) -> QCheckBox:
        checkbox = QCheckBox(self.translator.text(translation_key), self)
        checkbox.setEnabled(False)
        return checkbox

    def _connect_signals(self) -> None:
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.backup_folder_button.clicked.connect(self._choose_backup_folder)

    def _choose_backup_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.text("options.backup_folder"),
            self.backup_folder_edit.text(),
        )
        if selected_folder:
            self.backup_folder_edit.setText(selected_folder)

    def _set_font_families(self, current_font_family: str) -> None:
        font_families = sorted(QFontDatabase.families())
        self.font_family_combo.clear()
        self.font_family_combo.addItems(font_families)
        font_index = self.font_family_combo.findText(current_font_family)
        if font_index == -1:
            self.font_family_combo.insertItem(0, current_font_family)
            font_index = 0
        self.font_family_combo.setCurrentIndex(font_index)
