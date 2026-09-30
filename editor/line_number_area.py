from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QMouseEvent, QPaintEvent
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from editor.text_editor import TextEditor


class LineNumberArea(QWidget):
    def __init__(self, editor: TextEditor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return self.editor.line_number_area_size_hint()

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.paint_line_number_area(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        self.editor.select_line_at_view_y(round(event.position().y()))
        event.accept()
