from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from editor.tag_insert import (
    TagSnippet,
    TagSnippetGroup,
    tag_snippet_category_key,
)
from localization.translator import Translator


@dataclass(frozen=True)
class TagSnippetChoice:
    label: str
    search_text: str
    hint: str
    snippet: TagSnippet


class TagInsertDialog(QDialog):
    snippet_selected = Signal(TagSnippet)

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.translator = translator
        self.choices: list[TagSnippetChoice] = []
        self.selected_snippet: TagSnippet | None = None

        self.search_label = QLabel(self)
        self.search_edit = QLineEdit(self)
        self.snippet_list = QListWidget(self)
        self.hint_label = QLabel(self)
        self.hint_label.setWordWrap(True)
        self.insert_button = QPushButton(self)
        self.close_button = QPushButton(self)

        self._create_layout()
        self._connect_signals()
        self.apply_language()

    def apply_language(self) -> None:
        self.setWindowTitle(self.translator.text("tag_picker.title"))
        self.search_label.setText(self.translator.text("tag_picker.filter"))
        self.search_edit.setPlaceholderText(
            self.translator.text("tag_picker.filter_placeholder")
        )
        self.insert_button.setText(self.translator.text("tag_picker.insert"))
        self.close_button.setText(self.translator.text("tag_picker.close"))

    def set_snippet_groups(self, groups: tuple[TagSnippetGroup, ...]) -> None:
        self.choices = []
        for group in groups:
            group_label = self.translator.text(group.label_key)
            for snippet in group.snippets:
                category_key = tag_snippet_category_key(group.label_key, snippet)
                category_label = self.translator.text(category_key)
                snippet_label = self.translator.text(snippet.label_key)
                hint = self.translator.text(snippet.hint_key)
                label = f"{group_label} / {category_label} / {snippet_label}"
                self.choices.append(
                    TagSnippetChoice(
                        label=label,
                        search_text=f"{label} {hint} {snippet.template}".lower(),
                        hint=hint,
                        snippet=snippet,
                    )
                )
        self._refresh_list()

    def selected_choice(self) -> TagSnippet | None:
        return self.selected_snippet

    def _create_layout(self) -> None:
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.close_button)

        root_layout = QVBoxLayout()
        root_layout.addLayout(search_layout)
        root_layout.addWidget(self.snippet_list)
        root_layout.addWidget(self.hint_label)
        root_layout.addLayout(button_layout)
        self.setLayout(root_layout)
        self.resize(560, 420)

    def _connect_signals(self) -> None:
        self.search_edit.textChanged.connect(self._refresh_list)
        self.search_edit.installEventFilter(self)
        self.snippet_list.installEventFilter(self)
        self.snippet_list.currentItemChanged.connect(self._handle_current_item_changed)
        self.snippet_list.itemDoubleClicked.connect(lambda _item: self._accept_current())
        self.insert_button.clicked.connect(self._accept_current)
        self.close_button.clicked.connect(self.reject)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)
        if not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)

        key = event.key()
        if watched == self.search_edit:
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Tab):
                self._move_selection(1)
                self.snippet_list.setFocus()
                return True
            if key == Qt.Key.Key_Up:
                self._move_selection(-1)
                self.snippet_list.setFocus()
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._accept_current()
                return True
        if watched == self.snippet_list and key in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            self._accept_current()
            return True
        return super().eventFilter(watched, event)

    def _refresh_list(self) -> None:
        filter_text = self.search_edit.text().strip().lower()
        self.snippet_list.clear()
        for choice in self.choices:
            if filter_text and filter_text not in choice.search_text:
                continue
            item = QListWidgetItem(choice.label)
            item.setToolTip(choice.hint)
            item.setData(Qt.ItemDataRole.UserRole, choice)
            self.snippet_list.addItem(item)

        if self.snippet_list.count() > 0:
            self.snippet_list.setCurrentRow(0)
        else:
            self.hint_label.setText(self.translator.text("tag_picker.no_matches"))

    def _handle_current_item_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            self.hint_label.clear()
            return
        choice = current.data(Qt.ItemDataRole.UserRole)
        if isinstance(choice, TagSnippetChoice):
            self.hint_label.setText(choice.hint)

    def _move_selection(self, delta: int) -> None:
        if self.snippet_list.count() == 0:
            return
        current_row = self.snippet_list.currentRow()
        current_row = max(current_row, 0)
        next_row = min(max(current_row + delta, 0), self.snippet_list.count() - 1)
        self.snippet_list.setCurrentRow(next_row)

    def _accept_current(self) -> None:
        current = self.snippet_list.currentItem()
        if current is None:
            return
        choice = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(choice, TagSnippetChoice):
            return
        self.selected_snippet = choice.snippet
        self.snippet_selected.emit(choice.snippet)
        self.accept()
