from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QPaintEvent
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from editor.text_editor import TextEditor


class SearchMarkerArea(QWidget):
    def __init__(self, editor: TextEditor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.search_marker_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.paint_search_marker_area(event)
