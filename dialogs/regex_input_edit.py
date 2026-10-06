"""Regex input widget with lightweight regex highlighting."""

from __future__ import annotations

import re

from PySide6 import QtCore, QtGui, QtWidgets

REGEX_TOKEN_COLOR = QtGui.QColor("#7a4a12")


class RegexInputHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for regex input."""
    def __init__(self, document: QtGui.QTextDocument) -> None:
        super().__init__(document)
        self.enabled = False
        self.regex_format = QtGui.QTextCharFormat()
        self.regex_format.setForeground(REGEX_TOKEN_COLOR)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable regex highlighting."""
        self.enabled = enabled
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:
        """Highlight regex tokens in the given text block."""
        if not self.enabled:
            return

        for start, length in self._regex_token_ranges(text):
            self.setFormat(start, length, self.regex_format)

    def _regex_token_ranges(self, text: str) -> list[tuple[int, int]]:
        """Return a list of (start, length) tuples for regex tokens in the given text."""
        ranges: list[tuple[int, int]] = []
        ranges.extend(self._match_ranges(r"\\[AbBdDsSwWZzGnrtfv](?:[*+?]|\{\d+(?:,\d*)?\})?\??", text))
        ranges.extend(self._group_ranges(text))
        ranges.extend(self._match_ranges(r"(?<!\\)\.(?:[*+?]|\{\d+(?:,\d*)?\})?\??", text))
        ranges.extend(self._match_ranges(r"(?<!\\)(?:\^|\$|\|)", text))
        ranges.extend(self._match_ranges(r"(?<!\\)(?:[*+?]|\{\d+(?:,\d*)?\})\??", text))
        ranges.extend(self._match_ranges(r"(?:\\g<[^>]+>|\\[1-9]\d*|\$\d+|\$\{[A-Za-z_]\w*\})", text))
        return self._merge_ranges(ranges)

    def _match_ranges(self, pattern: str, text: str) -> list[tuple[int, int]]:
        """Return a list of (start, length) tuples for matches of the given regex pattern in the text."""
        return [(match.start(), match.end() - match.start()) for match in re.finditer(pattern, text)]

    def _group_ranges(self, text: str) -> list[tuple[int, int]]:
        """Return a list of (start, length) tuples for regex groups in the text."""
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
        """Merge overlapping or adjacent ranges."""
        if not ranges:
            return []
        sorted_ranges: list[tuple[int, int]] = sorted((start, start + length) for start, length in ranges)
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


class RegexInputEdit(QtWidgets.QPlainTextEdit):
    """Plain text edit widget for regex input with lightweight regex highlighting."""
    returnPressed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTabChangesFocus(True)
        self.setMinimumHeight(self._single_line_height())
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.highlighter = RegexInputHighlighter(self.document())

    def sizeHint(self) -> QtCore.QSize:
        """Return the preferred size of the widget, with a single line height."""
        size = super().sizeHint()
        return QtCore.QSize(size.width(), self._single_line_height())

    def minimumSizeHint(self) -> QtCore.QSize:
        """Return the minimum size of the widget, with a single line height."""
        size = super().minimumSizeHint()
        return QtCore.QSize(size.width(), self._single_line_height())

    def _single_line_height(self) -> int:
        """Return the height of a single line of text, plus padding."""
        return self.fontMetrics().height() + 12

    def text(self) -> str:
        """Return the current text in the widget."""
        return self.toPlainText()

    def setText(self, text: str) -> None:
        """Set the text in the widget."""
        self.setPlainText(text)

    def insert(self, text: str) -> None:
        """Insert text at the current cursor position."""
        self.textCursor().insertText(text)

    def selectionStart(self) -> int:
        """Return the start position of the current selection."""
        return self.textCursor().selectionStart()

    def hasSelectedText(self) -> bool:
        """Return whether the widget has selected text."""
        return self.textCursor().hasSelection()

    def cursorPosition(self) -> int:
        """Return the current cursor position."""
        return self.textCursor().position()

    def setCursorPosition(self, position: int) -> None:
        """Set the current cursor position."""
        cursor = self.textCursor()
        cursor.setPosition(position)
        self.setTextCursor(cursor)

    def setSelection(self, start: int, length: int) -> None:
        """Set the selection range in the widget."""
        cursor: QtGui.QTextCursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(start + length, cursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def set_regex_highlighting_enabled(self, enabled: bool) -> None:
        """Enable or disable regex highlighting."""
        self.highlighter.set_enabled(enabled)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Handle key press events, emitting returnPressed signal on Enter key."""
        if event.key() in {QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter} and not (
            event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
        ):
            self.returnPressed.emit()
            event.accept()
            return
        super().keyPressEvent(event)
        #self.viewport().update()

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """Handle focus out events, moving cursor to end if all text is selected."""
        super().focusOutEvent(event)
        cursor = self.textCursor()
        if (
            cursor.hasSelection()
            and cursor.selectionStart() == 0
            and cursor.selectionEnd() == len(self.toPlainText())
        ):
            cursor.setPosition(cursor.selectionEnd())
            self.setTextCursor(cursor)
