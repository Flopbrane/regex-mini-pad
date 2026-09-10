from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class RegexHelpItem:
    category: str
    label: str
    pattern: str
    description: str
    example_text: str
    matches: str
    replace_with: str
    replacement_result: str


class RegexHelpDialog(QDialog):
    pattern_insert_requested = Signal(str)

    def __init__(
        self,
        regex_help_path: Path | dict[str, Path],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Regular Expression Help")
        self.resize(980, 520)
        self.regex_help_paths = self._normalize_help_paths(regex_help_path)

        self.language_combo_box = QComboBox(self)
        for language_name in self.regex_help_paths:
            self.language_combo_box.addItem(language_name)

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self._set_headers()
        for column in (0, 1, 2):
            self.table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        for column in (3, 4, 5, 6):
            self.table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch,
            )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setWordWrap(True)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            self,
        )
        self.insert_button = button_box.addButton(
            "Insert Pattern",
            QDialogButtonBox.ButtonRole.ActionRole,
        )

        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Help language", self))
        language_layout.addWidget(self.language_combo_box)
        language_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(language_layout)
        layout.addWidget(self.table)
        layout.addWidget(button_box)
        self.setLayout(layout)

        self._load_current_language()
        self.insert_button.clicked.connect(self._emit_selected_pattern)
        button_box.rejected.connect(self.close)
        self.table.itemDoubleClicked.connect(self._emit_item_pattern)
        self.language_combo_box.currentTextChanged.connect(self._load_current_language)

    def _normalize_help_paths(
        self,
        regex_help_path: Path | dict[str, Path],
    ) -> dict[str, Path]:
        if isinstance(regex_help_path, Path):
            return {"EN_Ver.": regex_help_path}
        return regex_help_path

    def _set_headers(self) -> None:
        if self.language_combo_box.currentText() == "JP_Ver.":
            headers = [
                "種類",
                "用途",
                "パターン",
                "平文での意味",
                "例文",
                "対象になる部分",
                "置換文字 / 結果",
            ]
        else:
            headers = [
                "Category",
                "Use",
                "Pattern",
                "Plain meaning",
                "Example text",
                "Matches",
                "Replace with / Result",
            ]
        self.table.setHorizontalHeaderLabels(headers)

    def _load_current_language(self) -> None:
        self._set_headers()
        self._load_items(self.regex_help_paths[self.language_combo_box.currentText()])

    def _load_items(self, regex_help_path: Path) -> None:
        load_data = json.loads(regex_help_path.read_text(encoding="utf-8"))
        items = [
            RegexHelpItem(
                category=str(item.get("category", "")),
                label=str(item["label"]),
                pattern=str(item["pattern"]),
                description=str(item["description"]),
                example_text=str(item.get("example_text", "")),
                matches=str(item.get("matches", "")),
                replace_with=str(item.get("replace_with", "")),
                replacement_result=str(item.get("replacement_result", "")),
            )
            for item in load_data
        ]
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            replace_summary = self._replace_summary(item)
            self.table.setItem(row, 0, QTableWidgetItem(item.category))
            self.table.setItem(row, 1, QTableWidgetItem(item.label))
            self.table.setItem(row, 2, QTableWidgetItem(item.pattern))
            self.table.setItem(row, 3, QTableWidgetItem(item.description))
            self.table.setItem(row, 4, QTableWidgetItem(item.example_text))
            self.table.setItem(row, 5, QTableWidgetItem(item.matches))
            self.table.setItem(row, 6, QTableWidgetItem(replace_summary))
        self.table.resizeRowsToContents()

    def _replace_summary(self, item: RegexHelpItem) -> str:
        if not item.replace_with and not item.replacement_result:
            return ""
        if item.replace_with and item.replacement_result:
            return f"{item.replace_with} -> {item.replacement_result}"
        return item.replace_with or item.replacement_result

    def _emit_selected_pattern(self) -> None:
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        pattern_item = self.table.item(selected_items[0].row(), 1)
        if pattern_item is not None:
            self.pattern_insert_requested.emit(pattern_item.text())

    def _emit_item_pattern(self, item: QTableWidgetItem) -> None:
        pattern_item = self.table.item(item.row(), 1)
        if pattern_item is not None:
            self.pattern_insert_requested.emit(pattern_item.text())
