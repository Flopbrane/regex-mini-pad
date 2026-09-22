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

COLOR_PRESETS: tuple[tuple[str, str], ...] = (
    ("Yellow", "#ffff00"),
    ("Orange", "#ff9900"),
    ("Green", "#b6f2a5"),
    ("Blue", "#9ed8ff"),
    ("Pink", "#ffb3d9"),
    ("Gray", "#d9d9d9"),
)
ENCODING_PRESETS: tuple[tuple[str, str], ...] = (
    ("UTF-8", "utf-8"),
    ("UTF-8 with BOM", "utf-8-sig"),
    ("CP932 / Shift_JIS", "cp932"),
    ("Shift_JIS", "shift_jis"),
    ("EUC-JP", "euc_jp"),
    ("UTF-16", "utf-16"),
    ("UTF-16 LE", "utf-16-le"),
    ("UTF-16 BE", "utf-16-be"),
)
NEWLINE_PRESETS: tuple[tuple[str, str], ...] = (
    ("LF", "lf"),
    ("CRLF", "crlf"),
    ("CR", "cr"),
)


@dataclass(frozen=True)
class OptionsDialogValues:
    word_wrap_enabled: bool
    line_numbers_enabled: bool
    ruler_enabled: bool
    visible_spaces_enabled: bool
    visible_tabs_enabled: bool
    visible_newlines_enabled: bool
    fixed_column_wrap_enabled: bool
    fixed_column_wrap_column: int
    startup_restore_enabled: bool
    language_code: str
    default_encoding: str
    newline_code: str
    wordpress_mode_label_key: str
    hover_hints_enabled: bool
    user_dictionary_folder: str
    dictionary_check_enabled: bool
    backup_folder: str
    backup_retention_count: int
    backup_retention_days: int
    font_family: str
    font_size: int
    tab_width: int
    search_marker_color: str
    current_match_marker_color: str
    visible_space_marker_color: str
    visible_tab_marker_color: str
    visible_newline_marker_color: str
    regex_lint_enabled: bool
    html_typo_lint_enabled: bool


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
        self.line_numbers_checkbox = QCheckBox(self)
        self.word_wrap_checkbox = QCheckBox(self)
        self.ruler_checkbox = QCheckBox(self)
        self.fixed_column_wrap_checkbox = QCheckBox(self)
        self.fixed_column_wrap_column_spin = QSpinBox(self)
        self.visible_spaces_checkbox = QCheckBox(self)
        self.visible_tabs_checkbox = QCheckBox(self)
        self.visible_newlines_checkbox = QCheckBox(self)
        self.startup_restore_checkbox = QCheckBox(self)
        self.language_combo = QComboBox(self)
        self.default_encoding_combo = QComboBox(self)
        self.newline_combo = QComboBox(self)
        self.wordpress_mode_combo = QComboBox(self)
        self.hover_hints_checkbox = QCheckBox(self)
        self.user_dictionary_folder_edit = QLineEdit(self)
        self.user_dictionary_folder_button = QPushButton(self)
        self.dictionary_check_checkbox = QCheckBox(self)
        self.backup_folder_edit = QLineEdit(self)
        self.backup_folder_button = QPushButton(self)
        self.backup_retention_count_spin = QSpinBox(self)
        self.backup_retention_days_spin = QSpinBox(self)
        self.font_family_combo = QComboBox(self)
        self.font_size_spin = QSpinBox(self)
        self.tab_width_spin = QSpinBox(self)
        self.search_marker_color_combo = QComboBox(self)
        self.current_match_marker_color_combo = QComboBox(self)
        self.visible_space_marker_color_combo = QComboBox(self)
        self.visible_tab_marker_color_combo = QComboBox(self)
        self.visible_newline_marker_color_combo = QComboBox(self)
        self.regex_lint_checkbox = QCheckBox(self)
        self.html_typo_lint_checkbox = QCheckBox(self)
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

        self.line_numbers_checkbox.setText(
            self.translator.text("options.item.line_numbers")
        )
        self.word_wrap_checkbox.setText(self.translator.text("options.item.word_wrap"))
        self.ruler_checkbox.setText(self.translator.text("options.item.ruler"))
        self.fixed_column_wrap_checkbox.setText(
            self.translator.text("options.item.fixed_column_wrap")
        )
        self.visible_spaces_checkbox.setText(
            self.translator.text("options.item.visible_spaces")
        )
        self.visible_tabs_checkbox.setText(
            self.translator.text("options.item.visible_tabs")
        )
        self.visible_newlines_checkbox.setText(
            self.translator.text("options.item.visible_newlines")
        )
        self.startup_restore_checkbox.setText(
            self.translator.text("options.item.startup_restore")
        )
        self.hover_hints_checkbox.setText(
            self.translator.text("options.hover_hints_enabled")
        )
        self.user_dictionary_folder_button.setText(
            self.translator.text("options.browse")
        )
        self.dictionary_check_checkbox.setText(
            self.translator.text("options.item.dictionary_check")
        )
        self.backup_folder_button.setText(self.translator.text("options.browse"))
        self.regex_lint_checkbox.setText(
            self.translator.text("options.item.regex_lint")
        )
        self.html_typo_lint_checkbox.setText(
            self.translator.text("options.item.html_typo_lint")
        )

    def set_values(self, settings: EditorSettings) -> None:
        self.line_numbers_checkbox.setChecked(settings.line_numbers_enabled)
        self.word_wrap_checkbox.setChecked(settings.word_wrap_enabled)
        self.ruler_checkbox.setChecked(settings.ruler_enabled)
        self.fixed_column_wrap_checkbox.setChecked(settings.fixed_column_wrap_enabled)
        self.fixed_column_wrap_column_spin.setRange(1, 500)
        self.fixed_column_wrap_column_spin.setValue(settings.fixed_column_wrap_column)
        self.visible_spaces_checkbox.setChecked(settings.visible_spaces_enabled)
        self.visible_tabs_checkbox.setChecked(settings.visible_tabs_enabled)
        self.visible_newlines_checkbox.setChecked(settings.visible_newlines_enabled)
        self.startup_restore_checkbox.setChecked(settings.startup_restore_enabled)
        self._set_language_combo(settings.language_code)
        self._set_preset_combo(
            self.default_encoding_combo,
            ENCODING_PRESETS,
            settings.default_encoding,
        )
        self._set_preset_combo(
            self.newline_combo,
            NEWLINE_PRESETS,
            settings.newline_code,
        )
        self.wordpress_mode_combo.clear()
        for mode_label_key in self.wordpress_mode_keys:
            self.wordpress_mode_combo.addItem(
                self.translator.text(mode_label_key),
                mode_label_key,
            )
        mode_index = self.wordpress_mode_combo.findData(settings.wordpress_mode_label_key)
        self.wordpress_mode_combo.setCurrentIndex(max(mode_index, 0))
        self.hover_hints_checkbox.setChecked(settings.hover_hints_enabled)
        self.user_dictionary_folder_edit.setText(settings.user_dictionary_folder)
        self.dictionary_check_checkbox.setChecked(settings.dictionary_check_enabled)
        self.backup_folder_edit.setText(settings.backup_folder)
        self.backup_retention_count_spin.setRange(1, 999)
        self.backup_retention_count_spin.setValue(settings.backup_retention_count)
        self.backup_retention_days_spin.setRange(1, 9999)
        self.backup_retention_days_spin.setValue(settings.backup_retention_days)
        self._set_font_families(settings.font_family)
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(settings.font_size)
        self.tab_width_spin.setRange(1, 16)
        self.tab_width_spin.setValue(settings.tab_width)
        self._set_color_combo(
            self.search_marker_color_combo,
            settings.search_marker_color,
        )
        self._set_color_combo(
            self.current_match_marker_color_combo,
            settings.current_match_marker_color,
        )
        self._set_color_combo(
            self.visible_space_marker_color_combo,
            settings.visible_space_marker_color,
        )
        self._set_color_combo(
            self.visible_tab_marker_color_combo,
            settings.visible_tab_marker_color,
        )
        self._set_color_combo(
            self.visible_newline_marker_color_combo,
            settings.visible_newline_marker_color,
        )
        self.regex_lint_checkbox.setChecked(settings.regex_lint_enabled)
        self.html_typo_lint_checkbox.setChecked(settings.html_typo_lint_enabled)

    def values(self) -> OptionsDialogValues:
        return OptionsDialogValues(
            word_wrap_enabled=self.word_wrap_checkbox.isChecked(),
            line_numbers_enabled=self.line_numbers_checkbox.isChecked(),
            ruler_enabled=self.ruler_checkbox.isChecked(),
            visible_spaces_enabled=self.visible_spaces_checkbox.isChecked(),
            visible_tabs_enabled=self.visible_tabs_checkbox.isChecked(),
            visible_newlines_enabled=self.visible_newlines_checkbox.isChecked(),
            fixed_column_wrap_enabled=self.fixed_column_wrap_checkbox.isChecked(),
            fixed_column_wrap_column=self.fixed_column_wrap_column_spin.value(),
            startup_restore_enabled=self.startup_restore_checkbox.isChecked(),
            language_code=str(self.language_combo.currentData()),
            default_encoding=str(self.default_encoding_combo.currentData()),
            newline_code=str(self.newline_combo.currentData()),
            wordpress_mode_label_key=str(self.wordpress_mode_combo.currentData()),
            hover_hints_enabled=self.hover_hints_checkbox.isChecked(),
            user_dictionary_folder=self.user_dictionary_folder_edit.text().strip(),
            dictionary_check_enabled=self.dictionary_check_checkbox.isChecked(),
            backup_folder=self.backup_folder_edit.text().strip(),
            backup_retention_count=self.backup_retention_count_spin.value(),
            backup_retention_days=self.backup_retention_days_spin.value(),
            font_family=self.font_family_combo.currentText(),
            font_size=self.font_size_spin.value(),
            tab_width=self.tab_width_spin.value(),
            search_marker_color=str(self.search_marker_color_combo.currentData()),
            current_match_marker_color=str(
                self.current_match_marker_color_combo.currentData()
            ),
            visible_space_marker_color=str(
                self.visible_space_marker_color_combo.currentData()
            ),
            visible_tab_marker_color=str(
                self.visible_tab_marker_color_combo.currentData()
            ),
            visible_newline_marker_color=str(
                self.visible_newline_marker_color_combo.currentData()
            ),
            regex_lint_enabled=self.regex_lint_checkbox.isChecked(),
            html_typo_lint_enabled=self.html_typo_lint_checkbox.isChecked(),
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
        tab = QWidget(self)
        layout = QFormLayout()
        layout.addRow(
            self.translator.text("options.item.language"),
            self.language_combo,
        )
        layout.addRow(
            self.translator.text("options.item.default_encoding"),
            self.default_encoding_combo,
        )
        layout.addRow(
            self.translator.text("options.item.newline"),
            self.newline_combo,
        )
        layout.addRow(self.startup_restore_checkbox)
        tab.setLayout(layout)
        return tab

    def _view_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        layout.addRow(self.line_numbers_checkbox)
        layout.addRow(self.word_wrap_checkbox)
        layout.addRow(self.fixed_column_wrap_checkbox)
        layout.addRow(
            self.translator.text("options.fixed_column_wrap_column"),
            self.fixed_column_wrap_column_spin,
        )
        layout.addRow(self.ruler_checkbox)
        layout.addRow(self.visible_spaces_checkbox)
        self._populate_color_combo(self.visible_space_marker_color_combo)
        layout.addRow(
            self.translator.text("options.item.visible_space_marker_color"),
            self.visible_space_marker_color_combo,
        )
        layout.addRow(self.visible_tabs_checkbox)
        self._populate_color_combo(self.visible_tab_marker_color_combo)
        layout.addRow(
            self.translator.text("options.item.visible_tab_marker_color"),
            self.visible_tab_marker_color_combo,
        )
        layout.addRow(self.visible_newlines_checkbox)
        self._populate_color_combo(self.visible_newline_marker_color_combo)
        layout.addRow(
            self.translator.text("options.item.visible_newline_marker_color"),
            self.visible_newline_marker_color_combo,
        )
        layout.addRow(self._disabled_checkbox("options.item.theme"))
        tab.setLayout(layout)
        return tab

    def _tag_insert_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        layout.addRow(
            self.translator.text("options.wordpress_mode"),
            self.wordpress_mode_combo,
        )
        layout.addRow(self.hover_hints_checkbox)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.user_dictionary_folder_edit)
        folder_layout.addWidget(self.user_dictionary_folder_button)
        layout.addRow(self.translator.text("options.item.user_dictionary"), folder_layout)
        layout.addRow(self.dictionary_check_checkbox)
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
        layout.addRow(
            self.translator.text("options.backup_retention_count"),
            self.backup_retention_count_spin,
        )
        layout.addRow(
            self.translator.text("options.backup_retention_days"),
            self.backup_retention_days_spin,
        )
        layout.addRow(self._disabled_checkbox("options.item.backup_restore_mode"))
        tab.setLayout(layout)
        return tab

    def _font_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        layout.addRow(self.translator.text("options.font_family"), self.font_family_combo)
        layout.addRow(self.translator.text("options.font_size"), self.font_size_spin)
        layout.addRow(self.translator.text("options.item.tab_width"), self.tab_width_spin)
        tab.setLayout(layout)
        return tab

    def _search_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QFormLayout()
        self._populate_color_combo(self.search_marker_color_combo)
        self._populate_color_combo(self.current_match_marker_color_combo)
        layout.addRow(
            self.translator.text("options.item.search_marker_color"),
            self.search_marker_color_combo,
        )
        layout.addRow(
            self.translator.text("options.item.current_match_color"),
            self.current_match_marker_color_combo,
        )
        layout.addRow(self.regex_lint_checkbox)
        layout.addRow(self.html_typo_lint_checkbox)
        tab.setLayout(layout)
        return tab

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
        self.user_dictionary_folder_button.clicked.connect(
            self._choose_user_dictionary_folder
        )

    def _choose_backup_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.text("options.backup_folder"),
            self.backup_folder_edit.text(),
        )
        if selected_folder:
            self.backup_folder_edit.setText(selected_folder)

    def _choose_user_dictionary_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.text("options.item.user_dictionary"),
            self.user_dictionary_folder_edit.text(),
        )
        if selected_folder:
            self.user_dictionary_folder_edit.setText(selected_folder)

    def _set_language_combo(self, current_language_code: str) -> None:
        self.language_combo.clear()
        self.language_combo.addItem(self.translator.text("language.japanese"), "ja")
        self.language_combo.addItem(self.translator.text("language.english"), "en")
        language_index = self.language_combo.findData(current_language_code)
        self.language_combo.setCurrentIndex(max(language_index, 0))

    def _set_preset_combo(
        self,
        combo_box: QComboBox,
        presets: tuple[tuple[str, str], ...],
        current_value: str,
    ) -> None:
        combo_box.clear()
        for label, value in presets:
            combo_box.addItem(label, value)
        current_index = combo_box.findData(current_value)
        if current_index == -1:
            combo_box.insertItem(0, current_value, current_value)
            current_index = 0
        combo_box.setCurrentIndex(current_index)

    def _set_font_families(self, current_font_family: str) -> None:
        font_families = sorted(QFontDatabase.families())
        self.font_family_combo.clear()
        self.font_family_combo.addItems(font_families)
        font_index = self.font_family_combo.findText(current_font_family)
        if font_index == -1:
            self.font_family_combo.insertItem(0, current_font_family)
            font_index = 0
        self.font_family_combo.setCurrentIndex(font_index)

    def _populate_color_combo(self, combo_box: QComboBox) -> None:
        combo_box.clear()
        for label, color_code in COLOR_PRESETS:
            combo_box.addItem(f"{label} ({color_code})", color_code)

    def _set_color_combo(self, combo_box: QComboBox, color_code: str) -> None:
        color_index = combo_box.findData(color_code)
        if color_index == -1:
            combo_box.insertItem(0, color_code, color_code)
            color_index = 0
        combo_box.setCurrentIndex(color_index)
