from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class VisibleWhitespaceMark:
    text_position: int
    marker: str


class TextEditor(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.search_marker_area = SearchMarkerArea(self)
        self.line_numbers_enabled = True
        self.search_matches: list[SearchMatch] = []
        self.search_marker_color = "#ffff00"
        self.current_match_marker_color = "#ff9900"
        self.visible_spaces_enabled = False
        self.visible_tabs_enabled = False
        self.visible_newlines_enabled = False
        self.visible_space_marker_color = "#9a9a9a"
        self.visible_tab_marker_color = "#9ed8ff"
        self.visible_newline_marker_color = "#ff9900"
        self.word_wrap_enabled = False
        self.fixed_column_wrap_enabled = False
        self.fixed_column_wrap_column = 80

        self.setFont(QFont("Consolas", 11))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self._apply_search_highlights)
        self.update_editor_margins()

    def set_word_wrap_enabled(self, enabled: bool) -> None:
        self.word_wrap_enabled = enabled
        self._apply_line_wrap_mode()

    def set_fixed_column_wrap_options(self, *, enabled: bool, column: int) -> None:
        self.fixed_column_wrap_enabled = enabled
        self.fixed_column_wrap_column = max(1, column)
        self._apply_line_wrap_mode()
        self.update_editor_margins()
        self.viewport().update()

    def _apply_line_wrap_mode(self) -> None:
        enabled = self.word_wrap_enabled or self.fixed_column_wrap_enabled
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
        left_margin = self.line_number_area_width()
        right_margin = self.search_marker_area_width() + self._fixed_wrap_extra_margin()
        self.setViewportMargins(
            left_margin,
            0,
            right_margin,
            0,
        )

    def _fixed_wrap_extra_margin(self) -> int:
        if not self.fixed_column_wrap_enabled:
            return 0

        content_width = self.contentsRect().width()
        available_text_width = max(
            0,
            content_width - self.line_number_area_width() - self.search_marker_area_width(),
        )
        target_text_width = self.fixed_column_wrap_pixel_width()
        return max(0, available_text_width - target_text_width)

    def fixed_column_wrap_pixel_width(self) -> int:
        return max(
            1,
            self.fontMetrics().horizontalAdvance("0") * self.fixed_column_wrap_column,
        )

    def fixed_column_wrap_line_x(self) -> int | None:
        if not self.fixed_column_wrap_enabled:
            return None

        horizontal_offset = self.horizontalScrollBar().value()
        x_position = self.fixed_column_wrap_pixel_width() - horizontal_offset
        if x_position < 0 or x_position > self.viewport().width():
            return None
        return min(x_position, max(0, self.viewport().width() - 1))

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

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        self._paint_fixed_column_wrap_guide(event)
        self._paint_visible_whitespace(event)

    def _paint_fixed_column_wrap_guide(self, event: QPaintEvent) -> None:
        line_x = self.fixed_column_wrap_line_x()
        if line_x is None:
            return

        painter = QPainter(self.viewport())
        painter.setPen(QColor("#1f9d55"))
        painter.drawLine(line_x, event.rect().top(), line_x, event.rect().bottom())

    def set_search_matches(self, matches: list[SearchMatch]) -> None:
        self.search_matches = matches
        self._apply_search_highlights()
        self.search_marker_area.update()

    def clear_search_matches(self) -> None:
        self.set_search_matches([])

    def set_search_marker_colors(
        self,
        search_marker_color: str,
        current_match_marker_color: str,
    ) -> None:
        self.search_marker_color = search_marker_color
        self.current_match_marker_color = current_match_marker_color
        self._apply_search_highlights()
        self.search_marker_area.update()

    def set_visible_whitespace_options(
        self,
        *,
        spaces_enabled: bool,
        tabs_enabled: bool,
        newlines_enabled: bool,
    ) -> None:
        self.visible_spaces_enabled = spaces_enabled
        self.visible_tabs_enabled = tabs_enabled
        self.visible_newlines_enabled = newlines_enabled
        self.viewport().update()

    def set_visible_whitespace_marker_colors(
        self,
        *,
        space_color: str,
        tab_color: str,
        newline_color: str,
    ) -> None:
        self.visible_space_marker_color = space_color
        self.visible_tab_marker_color = tab_color
        self.visible_newline_marker_color = newline_color
        self.viewport().update()

    def visible_whitespace_marks(self) -> list[VisibleWhitespaceMark]:
        source_text = self.toPlainText()
        marks: list[VisibleWhitespaceMark] = []
        for text_position, character in enumerate(source_text):
            marker = self._visible_whitespace_marker(character)
            if marker is not None:
                marks.append(VisibleWhitespaceMark(text_position, marker))
        return marks

    def _visible_whitespace_marker(self, character: str) -> str | None:
        if self.visible_spaces_enabled:
            if character == " ":
                return "␣"
            if character == "\u3000":
                return "□"
        if self.visible_tabs_enabled and character == "\t":
            return "→"
        if self.visible_newlines_enabled and character == "\n":
            return "↵"
        return None

    def _paint_visible_whitespace(self, event: QPaintEvent) -> None:
        if not (
            self.visible_spaces_enabled
            or self.visible_tabs_enabled
            or self.visible_newlines_enabled
        ):
            return

        source_text = self.toPlainText()
        painter = QPainter(self.viewport())

        block = self.firstVisibleBlock()
        top = round(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                self._paint_block_visible_whitespace(
                    painter,
                    event.rect(),
                    source_text,
                    block.position(),
                    block.text(),
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())

    def _paint_block_visible_whitespace(
        self,
        painter: QPainter,
        event_rect: QRect,
        source_text: str,
        block_position: int,
        block_text: str,
    ) -> None:
        for character_index, character in enumerate(block_text):
            marker = self._visible_whitespace_marker(character)
            if marker is not None:
                self._paint_visible_whitespace_marker(
                    painter,
                    event_rect,
                    block_position + character_index,
                    marker,
                    character,
                )

        newline_position = block_position + len(block_text)
        if (
            newline_position < len(source_text)
            and source_text[newline_position] == "\n"
        ):
            marker = self._visible_whitespace_marker("\n")
            if marker is not None:
                self._paint_visible_whitespace_marker(
                    painter,
                    event_rect,
                    newline_position,
                    marker,
                    "\n",
                )

    def _paint_visible_whitespace_marker(
        self,
        painter: QPainter,
        event_rect: QRect,
        text_position: int,
        marker: str,
        character: str,
    ) -> None:
        cursor = QTextCursor(self.document())
        cursor.setPosition(self.text_position_to_cursor_position(text_position))
        marker_rect = self.cursorRect(cursor)
        if not marker_rect.intersects(event_rect.adjusted(-20, -20, 20, 20)):
            return

        painter.setPen(QColor(self._visible_whitespace_marker_color(character)))

        if character == "\t":
            marker_rect.setWidth(
                max(marker_rect.width(), round(self.tabStopDistance()))
            )
            alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        elif character == "\n":
            marker_rect.translate(2, 0)
            marker_rect.setWidth(max(marker_rect.width(), self.fontMetrics().height()))
            alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        else:
            alignment = Qt.AlignmentFlag.AlignCenter
        painter.drawText(marker_rect, alignment, marker)

    def _visible_whitespace_marker_color(self, character: str) -> str:
        if character == "\t":
            return self.visible_tab_marker_color
        if character == "\n":
            return self.visible_newline_marker_color
        return self.visible_space_marker_color

    def _apply_search_highlights(self) -> None:
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(self.search_marker_color))
        current_highlight_format = QTextCharFormat()
        current_highlight_format.setBackground(QColor(self.current_match_marker_color))

        selections: list[QTextEdit.ExtraSelection] = []
        cursor = self.textCursor()
        selection_start = self.cursor_position_to_text_position(cursor.selectionStart())
        selection_end = self.cursor_position_to_text_position(cursor.selectionEnd())
        for match in self.search_matches[:1000]:
            if match.start == match.end:
                continue
            selection = QTextEdit.ExtraSelection()
            selection.format = (
                current_highlight_format
                if match.start == selection_start and match.end == selection_end
                else highlight_format
            )
            match_cursor = QTextCursor(self.document())
            match_cursor.setPosition(self.text_position_to_cursor_position(match.start))
            match_cursor.setPosition(
                self.text_position_to_cursor_position(match.end),
                QTextCursor.MoveMode.KeepAnchor,
            )
            selection.cursor = match_cursor
            selections.append(selection)
        self.setExtraSelections(selections)

    def text_position_to_cursor_position(self, text_position: int) -> int:
        source_text = self.toPlainText()
        bounded_position = min(max(text_position, 0), len(source_text))
        return len(source_text[:bounded_position].encode("utf-16-le")) // 2

    def cursor_position_to_text_position(self, cursor_position: int) -> int:
        source_text = self.toPlainText()
        bounded_position = max(cursor_position, 0)
        utf16_position = 0
        for text_position, character in enumerate(source_text):
            character_width = 2 if ord(character) > 0xFFFF else 1
            if utf16_position + character_width > bounded_position:
                return text_position
            utf16_position += character_width
        return len(source_text)

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
        painter.setBrush(QColor(self.search_marker_color))
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
