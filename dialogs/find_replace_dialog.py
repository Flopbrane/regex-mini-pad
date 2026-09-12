from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from localization.translator import Translator
from search.regex_lint import RegexLint, RegexLintMessage
from search.search_engine import SearchOptions


class FindReplaceDialog(QDialog):
    find_requested = Signal(str, SearchOptions)
    replace_requested = Signal(str, str, SearchOptions)
    replace_all_requested = Signal(str, str, SearchOptions)
    preview_requested = Signal(str, str, SearchOptions)
    search_parameters_changed = Signal(str, SearchOptions)
    regex_help_requested = Signal()

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.translator = translator
        self.setModal(False)
        self.regex_lint = RegexLint()

        self.find_text_edit = QLineEdit(self)
        self.replace_text_edit = QLineEdit(self)
        self.find_text_label = QLabel(self)
        self.replace_text_label = QLabel(self)

        self.case_sensitive_check_box = QCheckBox("Case-sensitive", self)
        self.regular_expression_check_box = QCheckBox("Regular expression", self)
        self.whole_word_check_box = QCheckBox("Whole word", self)
        self.selected_only_check_box = QCheckBox("Search only selected text", self)
        self.visible_only_check_box = QCheckBox("Search only visible text", self)

        self.find_button = QPushButton("Find", self)
        self.replace_button = QPushButton("Replace", self)
        self.replace_all_button = QPushButton("Replace All", self)
        self.insert_regex_button = QPushButton("Insert Regex", self)
        self.recipe_button = QPushButton("Recipes", self)
        self.preview_button = QPushButton("Preview", self)
        self.regex_help_button = QPushButton("Regex Help", self)
        self.close_button = QPushButton("Close", self)
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: #b00020;")
        self.error_label.setWordWrap(True)
        self.warning_label = QLabel(self)
        self.warning_label.setStyleSheet("color: #8a5a00;")
        self.warning_label.setWordWrap(True)
        self.preview_summary_label = QLabel(self)
        self.preview_table = QTableWidget(0, 3, self)
        self.preview_table.setMinimumHeight(180)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._create_layout()
        self._create_regex_insert_menu()
        self._create_recipe_menu()
        self._connect_signals()
        self.apply_language()

    def set_find_text(self, text: str) -> None:
        self.find_text_edit.setText(text)
        self.find_text_edit.selectAll()

    def set_error(self, message: str) -> None:
        self.error_label.setText(message)

    def clear_error(self) -> None:
        self.error_label.clear()

    def insert_find_text(self, text: str, cursor_offset: int | None = None) -> None:
        insert_position = (
            self.find_text_edit.selectionStart()
            if self.find_text_edit.hasSelectedText()
            else self.find_text_edit.cursorPosition()
        )
        self.regular_expression_check_box.setChecked(True)
        self.find_text_edit.insert(text)
        if cursor_offset is not None:
            self.find_text_edit.setCursorPosition(insert_position + cursor_offset)
        self.find_text_edit.setFocus()

    def current_search_options(self) -> SearchOptions:
        return self._search_options()

    def set_search_recipe(self, search_text: str, replace_text: str) -> None:
        self.find_text_edit.setText(search_text)
        self.replace_text_edit.setText(replace_text)
        self.regular_expression_check_box.setChecked(True)
        self.find_text_edit.setFocus()
        self.find_text_edit.selectAll()

    def set_preview_rows(
        self,
        rows: list[tuple[int, str, str]],
        summary: str,
    ) -> None:
        self.preview_summary_label.setText(summary)
        self.preview_table.setRowCount(len(rows))
        for row_index, (line_number, before_text, after_text) in enumerate(rows):
            values = (str(line_number), before_text, after_text)
            for column_index, value in enumerate(values):
                self.preview_table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(value),
                )
        self.preview_table.resizeColumnsToContents()

    def apply_language(self) -> None:
        self.setWindowTitle(self.translator.text("find.title"))
        self.find_text_label.setText(self.translator.text("find.find_text"))
        self.replace_text_label.setText(self.translator.text("find.replace_text"))
        self.case_sensitive_check_box.setText(self.translator.text("find.case_sensitive"))
        self.regular_expression_check_box.setText(self.translator.text("find.regex"))
        self.whole_word_check_box.setText(self.translator.text("find.whole_word"))
        self.selected_only_check_box.setText(self.translator.text("find.selected_only"))
        self.visible_only_check_box.setText(self.translator.text("find.visible_only"))
        self.find_button.setText(self.translator.text("find.find"))
        self.replace_button.setText(self.translator.text("find.replace"))
        self.replace_all_button.setText(self.translator.text("find.replace_all"))
        self.insert_regex_button.setText(self.translator.text("find.insert_regex"))
        self.recipe_button.setText(self.translator.text("find.regex_recipes"))
        self.preview_button.setText(self.translator.text("find.preview"))
        self.regex_help_button.setText(self.translator.text("find.regex_help"))
        self.close_button.setText(self.translator.text("find.close"))
        self.preview_table.setHorizontalHeaderLabels(
            [
                self.translator.text("find.preview.line"),
                self.translator.text("find.preview.before"),
                self.translator.text("find.preview.after"),
            ]
        )
        self._create_regex_insert_menu()
        self._create_recipe_menu()
        self._update_regex_lint()

    def _create_layout(self) -> None:
        form_layout = QGridLayout()
        form_layout.addWidget(self.find_text_label, 0, 0)
        form_layout.addWidget(self.find_text_edit, 0, 1)
        form_layout.addWidget(self.replace_text_label, 1, 0)
        form_layout.addWidget(self.replace_text_edit, 1, 1)
        form_layout.addWidget(self.case_sensitive_check_box, 2, 1)
        form_layout.addWidget(self.regular_expression_check_box, 3, 1)
        form_layout.addWidget(self.whole_word_check_box, 4, 1)
        form_layout.addWidget(self.selected_only_check_box, 5, 1)
        form_layout.addWidget(self.visible_only_check_box, 6, 1)

        button_layout = QGridLayout()
        button_layout.addWidget(self.find_button, 0, 0)
        button_layout.addWidget(self.replace_button, 0, 1)
        button_layout.addWidget(self.replace_all_button, 0, 2)
        button_layout.addWidget(self.preview_button, 1, 0)
        button_layout.addWidget(self.insert_regex_button, 1, 1)
        button_layout.addWidget(self.recipe_button, 1, 2)
        button_layout.addWidget(self.regex_help_button, 2, 0)
        button_layout.addWidget(self.close_button, 2, 2)

        root_layout = QVBoxLayout()
        root_layout.addLayout(form_layout)
        root_layout.addLayout(button_layout)
        root_layout.addWidget(self.warning_label)
        root_layout.addWidget(self.error_label)
        root_layout.addWidget(self.preview_summary_label)
        root_layout.addWidget(self.preview_table)
        self.setLayout(root_layout)

    def _create_regex_insert_menu(self) -> None:
        regex_menu = QMenu(self)
        snippet_groups = [
            (
                "regex.snippet_group.characters",
                [
                    ("regex.snippet.digit", r"\d", None),
                    ("regex.snippet.not_digit", r"\D", None),
                    ("regex.snippet.word", r"\w", None),
                    ("regex.snippet.not_word", r"\W", None),
                    ("regex.snippet.whitespace", r"\s", None),
                    ("regex.snippet.not_whitespace", r"\S", None),
                    ("regex.snippet.any", ".", None),
                    ("regex.snippet.literal_dot", r"\.", None),
                    ("regex.snippet.line_break", r"\n", None),
                    ("regex.snippet.tab", r"\t", None),
                ],
            ),
            (
                "regex.snippet_group.positions",
                [
                    ("regex.snippet.start", "^", None),
                    ("regex.snippet.end", "$", None),
                    ("regex.snippet.word_boundary", r"\b", None),
                ],
            ),
            (
                "regex.snippet_group.repetition",
                [
                    ("regex.snippet.one_or_more", "+", None),
                    ("regex.snippet.zero_or_more", "*", None),
                    ("regex.snippet.optional", "?", None),
                    ("regex.snippet.exact_count", r"{1}", 1),
                    ("regex.snippet.count_range", r"{1,3}", 1),
                ],
            ),
            (
                "regex.snippet_group.groups",
                [
                    ("regex.snippet.capture", r"()", 1),
                    ("regex.snippet.class", r"[]", 1),
                    ("regex.snippet.non_capture", r"(?:)", 3),
                    ("regex.snippet.alternative", "|", None),
                ],
            ),
        ]
        for group_key, snippets in snippet_groups:
            group_menu = regex_menu.addMenu(self.translator.text(group_key))
            assert group_menu is not None
            for label_key, pattern, cursor_offset in snippets:
                self._add_regex_snippet_action(group_menu, label_key, pattern, cursor_offset)
        self.insert_regex_button.setMenu(regex_menu)

    def _add_regex_snippet_action(
        self,
        menu: QMenu,
        label_key: str,
        pattern: str,
        cursor_offset: int | None,
    ) -> None:
        label = self.translator.text(label_key)
        action = QAction(f"{label}    {pattern}", self)
        action.triggered.connect(
            lambda checked=False,
            value=pattern,
            offset=cursor_offset: self.insert_find_text(value, offset)
        )
        menu.addAction(action)

    def _create_recipe_menu(self) -> None:
        recipe_menu = QMenu(self)
        recipes = [
            ("regex.recipe.collapse_blank_lines", r"\n{3,}", "\n\n"),
            ("regex.recipe.trim_trailing_space", r"[ \t]+$", ""),
            ("regex.recipe.remove_blank_lines", r"^[ \t]*\n", ""),
            ("regex.recipe.tabs_to_spaces", r"\t", "    "),
            ("regex.recipe.date_yyyy_mm_dd_to_slash", r"(\d{4})-(\d{2})-(\d{2})", r"\1/\2/\3"),
            ("regex.recipe.numbered_to_bullets", r"^\d+\.\s+", "- "),
        ]
        for label_key, search_text, replace_text in recipes:
            label = self.translator.text(label_key)
            action = QAction(label, self)
            action.triggered.connect(
                lambda checked=False,
                search_value=search_text,
                replace_value=replace_text: self.set_search_recipe(
                    search_value,
                    replace_value,
                )
            )
            recipe_menu.addAction(action)
        self.recipe_button.setMenu(recipe_menu)

    def _connect_signals(self) -> None:
        self.find_button.clicked.connect(self._emit_find_requested)
        self.find_text_edit.returnPressed.connect(self._emit_find_requested)
        self.replace_button.clicked.connect(self._emit_replace_requested)
        self.replace_all_button.clicked.connect(self._emit_replace_all_requested)
        self.preview_button.clicked.connect(self._emit_preview_requested)
        self.regex_help_button.clicked.connect(self.regex_help_requested.emit)
        self.close_button.clicked.connect(self.close)
        self.find_text_edit.textChanged.connect(self._update_regex_lint)
        self.find_text_edit.textChanged.connect(self._emit_search_parameters_changed)
        self.replace_text_edit.textChanged.connect(self._update_regex_lint)
        self.regular_expression_check_box.toggled.connect(
            self._handle_search_option_changed
        )
        self.case_sensitive_check_box.toggled.connect(
            self._emit_search_parameters_changed
        )
        self.whole_word_check_box.toggled.connect(self._emit_search_parameters_changed)
        self.selected_only_check_box.toggled.connect(self._emit_search_parameters_changed)
        self.visible_only_check_box.toggled.connect(self._emit_search_parameters_changed)

    def _search_options(self) -> SearchOptions:
        return SearchOptions(
            case_sensitive=self.case_sensitive_check_box.isChecked(),
            regular_expression=self.regular_expression_check_box.isChecked(),
            whole_word=self.whole_word_check_box.isChecked(),
            selected_only=self.selected_only_check_box.isChecked(),
            visible_only=self.visible_only_check_box.isChecked(),
        )

    def _update_regex_lint(self) -> None:
        if not self.regular_expression_check_box.isChecked():
            self.warning_label.clear()
            return

        messages = self.regex_lint.lint(
            self.find_text_edit.text(),
            self.replace_text_edit.text(),
            check_replacement=True,
        )
        errors = [message for message in messages if message.severity == "error"]
        warnings = [
            message for message in messages if message.severity == "warning"
        ]
        if errors:
            self.warning_label.setText(self._lint_message_text(errors[0]))
        elif warnings:
            self.warning_label.setText(self._lint_message_text(warnings[0]))
        else:
            self.warning_label.clear()

    def _lint_message_text(self, message: RegexLintMessage) -> str:
        return self.translator.text(message.message_key, **(message.values or {}))

    def _emit_find_requested(self) -> None:
        self.find_requested.emit(self.find_text_edit.text(), self._search_options())

    def _emit_replace_requested(self) -> None:
        self.replace_requested.emit(
            self.find_text_edit.text(),
            self.replace_text_edit.text(),
            self._search_options(),
        )

    def _emit_replace_all_requested(self) -> None:
        self.replace_all_requested.emit(
            self.find_text_edit.text(),
            self.replace_text_edit.text(),
            self._search_options(),
        )

    def _emit_preview_requested(self) -> None:
        self.preview_requested.emit(
            self.find_text_edit.text(),
            self.replace_text_edit.text(),
            self._search_options(),
        )

    def _handle_search_option_changed(self, *_args: object) -> None:
        self._update_regex_lint()
        self._emit_search_parameters_changed()

    def _emit_search_parameters_changed(self, *_args: object) -> None:
        self.search_parameters_changed.emit(
            self.find_text_edit.text(),
            self._search_options(),
        )
