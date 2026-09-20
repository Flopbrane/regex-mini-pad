from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from editor.text_editor import TextEditor


class Ruler(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor: TextEditor | None = None
        self.setFixedHeight(24)

    def set_editor(self, editor: TextEditor | None) -> None:
        if self.editor is not None:
            try:
                self.editor.horizontalScrollBar().valueChanged.disconnect(self.update)
                self.editor.cursorPositionChanged.disconnect(self.update)
            except (RuntimeError, TypeError):
                pass

        self.editor = editor
        if self.editor is not None:
            self.setFont(self.editor.font())
            self.editor.horizontalScrollBar().valueChanged.connect(self.update)
            self.editor.cursorPositionChanged.connect(self.update)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#f7f7f7"))
        painter.setPen(QColor("#d0d0d0"))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        if self.editor is None:
            return

        metrics = QFontMetrics(self.editor.font())
        character_width = max(1, metrics.horizontalAdvance("0"))
        horizontal_offset = self.editor.horizontalScrollBar().value()
        left_margin = self.editor.line_number_area_width()
        first_column = max(0, horizontal_offset // character_width)
        visible_columns = max(1, (self.width() - left_margin) // character_width + 2)

        painter.setPen(QColor("#606060"))
        for column in range(first_column, first_column + visible_columns + 1):
            x_position = left_margin + (column * character_width) - horizontal_offset
            if x_position < left_margin:
                continue
            tick_height = 10 if column % 10 == 0 else 5
            painter.drawLine(
                x_position,
                self.height() - tick_height - 1,
                x_position,
                self.height() - 1,
            )
            if column > 0 and column % 10 == 0:
                painter.drawText(
                    x_position + 2,
                    1,
                    50,
                    self.height() - 4,
                    Qt.AlignmentFlag.AlignLeft,
                    str(column),
                )
