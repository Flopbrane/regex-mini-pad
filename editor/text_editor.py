from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPaintEvent,
    QResizeEvent,
    QTextCharFormat,
    QTextCursor,
    QTextOption,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit

from editor.line_number_area import LineNumberArea
from editor.search_marker_area import SearchMarkerArea
from search.search_engine import SearchMatch


class TextEditor(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.search_marker_area = SearchMarkerArea(self)
        self.line_numbers_enabled = True
        self.search_matches: list[SearchMatch] = []

        self.setFont(QFont("Consolas", 11))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_editor_margins()

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

    def set_line_numbers_enabled(self, enabled: bool) -> None:
        self.line_numbers_enabled = enabled
        self.line_number_area.setVisible(enabled)
        self.update_line_number_area_width()

    def line_number_area_size_hint(self) -> QSize:
        return QSize(self.line_number_area_width(), 0)

    def line_number_area_width(self) -> int:
        if not self.line_numbers_enabled:
            return 0

        digits = len(str(max(1, self.blockCount())))
        space_width = self.fontMetrics().horizontalAdvance("9") * digits
        return 12 + space_width

    def search_marker_area_width(self) -> int:
        return 10

    def update_line_number_area_width(self) -> None:
        self.update_editor_margins()

    def update_editor_margins(self) -> None:
        self.setViewportMargins(
            self.line_number_area_width(),
            0,
            self.search_marker_area_width(),
            0,
        )

    def update_line_number_area(self, rect: QRect, vertical_delta: int) -> None:
        if vertical_delta:
            self.line_number_area.scroll(0, vertical_delta)
        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height(),
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()
        self.search_marker_area.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        content_rect = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                content_rect.left(),
                content_rect.top(),
                self.line_number_area_width(),
                content_rect.height(),
            )
        )
        marker_width = self.search_marker_area_width()
        self.search_marker_area.setGeometry(
            QRect(
                content_rect.right() - marker_width + 1,
                content_rect.top(),
                marker_width,
                content_rect.height(),
            )
        )

    def set_search_matches(self, matches: list[SearchMatch]) -> None:
        self.search_matches = matches
        self._apply_search_highlights()
        self.search_marker_area.update()

    def clear_search_matches(self) -> None:
        self.set_search_matches([])

    def _apply_search_highlights(self) -> None:
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#fff2a8"))

        selections: list[QTextEdit.ExtraSelection] = []
        for match in self.search_matches[:1000]:
            if match.start == match.end:
                continue
            selection = QTextEdit.ExtraSelection()
            selection.format = highlight_format
            cursor = QTextCursor(self.document())
            cursor.setPosition(match.start)
            cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
            selection.cursor = cursor
            selections.append(selection)
        self.setExtraSelections(selections)

    def paint_line_number_area(self, event: QPaintEvent) -> None:
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#f3f3f3"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#606060"))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def paint_search_marker_area(self, event: QPaintEvent) -> None:
        painter = QPainter(self.search_marker_area)
        painter.fillRect(event.rect(), QColor("#f7f7f7"))
        if not self.search_matches:
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#d49a00"))
        area_width = self.search_marker_area.width()
        area_height = max(1, self.search_marker_area.height())
        block_count = max(1, self.blockCount())
        marked_lines = {
            self.document().findBlock(match.start).blockNumber()
            for match in self.search_matches
            if match.start != match.end
        }
        for line_number in marked_lines:
            marker_y = round((line_number / block_count) * area_height)
            painter.drawRect(2, marker_y, area_width - 4, 3)
