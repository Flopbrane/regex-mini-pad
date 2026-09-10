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
    QVBoxLayout,
    QWidget,
)

from search.regex_lint import RegexLint
from search.search_engine import SearchOptions


class FindReplaceDialog(QDialog):
    find_requested = Signal(str, SearchOptions)
    replace_requested = Signal(str, str, SearchOptions)
    replace_all_requested = Signal(str, str, SearchOptions)
    regex_help_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Find / Replace")
        self.setModal(False)
        self.regex_lint = RegexLint()

        self.find_text_edit = QLineEdit(self)
        self.replace_text_edit = QLineEdit(self)

        self.case_sensitive_check_box = QCheckBox("Case-sensitive", self)
        self.regular_expression_check_box = QCheckBox("Regular expression", self)
        self.whole_word_check_box = QCheckBox("Whole word", self)
        self.selected_only_check_box = QCheckBox("Search only selected text", self)

        self.find_button = QPushButton("Find", self)
        self.replace_button = QPushButton("Replace", self)
        self.replace_all_button = QPushButton("Replace All", self)
        self.insert_regex_button = QPushButton("Insert Regex", self)
        self.regex_help_button = QPushButton("Regex Help", self)
        self.close_button = QPushButton("Close", self)
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: #b00020;")
        self.error_label.setWordWrap(True)
        self.warning_label = QLabel(self)
        self.warning_label.setStyleSheet("color: #8a5a00;")
        self.warning_label.setWordWrap(True)

        self._create_layout()
        self._create_regex_insert_menu()
        self._connect_signals()

    def set_find_text(self, text: str) -> None:
        self.find_text_edit.setText(text)
        self.find_text_edit.selectAll()

    def set_error(self, message: str) -> None:
        self.error_label.setText(message)

    def clear_error(self) -> None:
        self.error_label.clear()

    def insert_find_text(self, text: str) -> None:
        self.find_text_edit.insert(text)
        self.find_text_edit.setFocus()

    def _create_layout(self) -> None:
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Find text", self), 0, 0)
        form_layout.addWidget(self.find_text_edit, 0, 1)
        form_layout.addWidget(QLabel("Replace text", self), 1, 0)
        form_layout.addWidget(self.replace_text_edit, 1, 1)
        form_layout.addWidget(self.case_sensitive_check_box, 2, 1)
        form_layout.addWidget(self.regular_expression_check_box, 3, 1)
        form_layout.addWidget(self.whole_word_check_box, 4, 1)
        form_layout.addWidget(self.selected_only_check_box, 5, 1)

        button_layout = QGridLayout()
        button_layout.addWidget(self.find_button, 0, 0)
        button_layout.addWidget(self.replace_button, 0, 1)
        button_layout.addWidget(self.replace_all_button, 1, 0)
        button_layout.addWidget(self.insert_regex_button, 1, 1)
        button_layout.addWidget(self.regex_help_button, 2, 0)
        button_layout.addWidget(self.close_button, 2, 1)

        root_layout = QVBoxLayout()
        root_layout.addLayout(form_layout)
        root_layout.addLayout(button_layout)
        root_layout.addWidget(self.warning_label)
        root_layout.addWidget(self.error_label)
        self.setLayout(root_layout)

    def _create_regex_insert_menu(self) -> None:
        regex_menu = QMenu(self)
        snippets = {
            "Digit": r"\d",
            "Word character": r"\w",
            "Whitespace": r"\s",
            "Any character": ".",
            "Start of line": "^",
            "End of line": "$",
            "One or more": "+",
            "Zero or more": "*",
            "Optional": "?",
            "Capture group": r"()",
            "Character class": r"[]",
        }
        for label, pattern in snippets.items():
            action = QAction(f"{label}    {pattern}", self)
            action.triggered.connect(lambda checked=False, value=pattern: self.insert_find_text(value))
            regex_menu.addAction(action)
        self.insert_regex_button.setMenu(regex_menu)

    def _connect_signals(self) -> None:
        self.find_button.clicked.connect(self._emit_find_requested)
        self.find_text_edit.returnPressed.connect(self._emit_find_requested)
        self.replace_button.clicked.connect(self._emit_replace_requested)
        self.replace_all_button.clicked.connect(self._emit_replace_all_requested)
        self.regex_help_button.clicked.connect(self.regex_help_requested.emit)
        self.close_button.clicked.connect(self.close)
        self.find_text_edit.textChanged.connect(self._update_regex_lint)
        self.replace_text_edit.textChanged.connect(self._update_regex_lint)
        self.regular_expression_check_box.toggled.connect(self._update_regex_lint)

    def _search_options(self) -> SearchOptions:
        return SearchOptions(
            case_sensitive=self.case_sensitive_check_box.isChecked(),
            regular_expression=self.regular_expression_check_box.isChecked(),
            whole_word=self.whole_word_check_box.isChecked(),
            selected_only=self.selected_only_check_box.isChecked(),
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
        errors = [message.message for message in messages if message.severity == "error"]
        warnings = [
            message.message for message in messages if message.severity == "warning"
        ]
        if errors:
            self.warning_label.setText(errors[0])
        elif warnings:
            self.warning_label.setText(warnings[0])
        else:
            self.warning_label.clear()

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
