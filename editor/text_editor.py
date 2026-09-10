from __future__ import annotations

from PySide6.QtGui import QFont, QTextOption
from PySide6.QtWidgets import QPlainTextEdit


class TextEditor(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setFont(QFont("Consolas", 11))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)

    def set_word_wrap_enabled(self, enabled: bool) -> None:
        wrap_mode = (
            QPlainTextEdit.LineWrapMode.WidgetWidth
            if enabled
            else QPlainTextEdit.LineWrapMode.NoWrap
        )
        self.setLineWrapMode(wrap_mode)
        self.setWordWrapMode(
            QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
            if enabled
            else QTextOption.WrapMode.NoWrap
        )
