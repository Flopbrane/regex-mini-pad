from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QKeyEvent,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)
from PySide6.QtWidgets import QPlainTextEdit, QWidget

REGEX_TOKEN_COLOR = QColor("#7a4a12")


class RegexInputHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self.enabled = False
        self.regex_format = QTextCharFormat()
        self.regex_format.setForeground(REGEX_TOKEN_COLOR)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:
        if not self.enabled:
            return

        for start, length in self._regex_token_ranges(text):
            self.setFormat(start, length, self.regex_format)

    def _regex_token_ranges(self, text: str) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []
        ranges.extend(self._match_ranges(r"\\[AbBdDsSwWZzG](?:[*+?]|\{\d+(?:,\d*)?\})?\??", text))
        ranges.extend(self._group_ranges(text))
        ranges.extend(self._match_ranges(r"(?<!\\)\.(?:[*+?]|\{\d+(?:,\d*)?\})?\??", text))
        ranges.extend(self._match_ranges(r"(?<!\\)(?:\^|\$|\|)", text))
        ranges.extend(self._match_ranges(r"(?<!\\)(?:[*+?]|\{\d+(?:,\d*)?\})\??", text))
        ranges.extend(self._match_ranges(r"(?:\\g<[^>]+>|\\[1-9]\d*|\$\d+|\$\{[A-Za-z_]\w*\})", text))
        return self._merge_ranges(ranges)

    def _match_ranges(self, pattern: str, text: str) -> list[tuple[int, int]]:
        return [(match.start(), match.end() - match.start()) for match in re.finditer(pattern, text)]

    def _group_ranges(self, text: str) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []
        stack: list[int] = []
        escaped = False
        in_character_class = False
        for index, character in enumerate(text):
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character == "[" and not in_character_class:
                in_character_class = True
                continue
            if character == "]" and in_character_class:
                in_character_class = False
                continue
            if in_character_class:
                continue
            if character == "(":
                stack.append(index)
            elif character == ")" and stack:
                start = stack.pop()
                ranges.append((start, index - start + 1))
        return ranges

    def _merge_ranges(self, ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not ranges:
            return []
        sorted_ranges = sorted((start, start + length) for start, length in ranges)
        merged: list[tuple[int, int]] = []
        current_start, current_end = sorted_ranges[0]
        for start, end in sorted_ranges[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
                continue
            merged.append((current_start, current_end - current_start))
            current_start, current_end = start, end
        merged.append((current_start, current_end - current_start))
        return merged


class RegexInputEdit(QPlainTextEdit):
    returnPressed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTabChangesFocus(True)
        self.setFixedHeight(self.fontMetrics().height() + 12)
        self.highlighter = RegexInputHighlighter(self.document())

    def text(self) -> str:
        return self.toPlainText()

    def setText(self, text: str) -> None:
        self.setPlainText(text)

    def insert(self, text: str) -> None:
        self.textCursor().insertText(text)

    def selectionStart(self) -> int:
        return self.textCursor().selectionStart()

    def hasSelectedText(self) -> bool:
        return self.textCursor().hasSelection()

    def cursorPosition(self) -> int:
        return self.textCursor().position()

    def setCursorPosition(self, position: int) -> None:
        cursor = self.textCursor()
        cursor.setPosition(position)
        self.setTextCursor(cursor)

    def setSelection(self, start: int, length: int) -> None:
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(start + length, cursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def set_regex_highlighting_enabled(self, enabled: bool) -> None:
        self.highlighter.set_enabled(enabled)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and not (
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.returnPressed.emit()
            event.accept()
            return
        super().keyPressEvent(event)
