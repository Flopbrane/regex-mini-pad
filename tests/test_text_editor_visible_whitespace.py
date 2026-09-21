from __future__ import annotations

import os
import sys

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QPlainTextEdit

from editor.text_editor import TextEditor

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_visible_whitespace_marks_are_empty_by_default(app: QApplication) -> None:
    _ = app
    editor = TextEditor()
    editor.setPlainText("a b\tc\n")

    assert editor.visible_whitespace_marks() == []


def test_visible_whitespace_marks_follow_individual_options(
    app: QApplication,
) -> None:
    _ = app
    editor = TextEditor()
    editor.setPlainText("a b\tc\nwide　space")

    editor.set_visible_whitespace_options(
        spaces_enabled=True,
        tabs_enabled=False,
        newlines_enabled=True,
    )

    assert [
        (mark.text_position, mark.marker) for mark in editor.visible_whitespace_marks()
    ] == [
        (1, "␣"),
        (5, "↵"),
        (10, "□"),
    ]


def test_visible_whitespace_options_do_not_modify_text(app: QApplication) -> None:
    _ = app
    editor = TextEditor()
    source_text = "a b\tc\n"
    editor.setPlainText(source_text)

    editor.set_visible_whitespace_options(
        spaces_enabled=True,
        tabs_enabled=True,
        newlines_enabled=True,
    )

    assert editor.toPlainText() == source_text
    assert [
        (mark.text_position, mark.marker) for mark in editor.visible_whitespace_marks()
    ] == [
        (1, "␣"),
        (3, "→"),
        (5, "↵"),
    ]


def test_visible_whitespace_paint_path_renders(app: QApplication) -> None:
    editor = TextEditor()
    source_text = "a b\tc\n"
    editor.setPlainText(source_text)
    editor.resize(320, 160)
    editor.set_visible_whitespace_options(
        spaces_enabled=True,
        tabs_enabled=True,
        newlines_enabled=True,
    )
    editor.show()
    app.processEvents()

    image = QImage(
        editor.viewport().size(),
        QImage.Format.Format_ARGB32,
    )
    editor.viewport().render(image)

    assert editor.toPlainText() == source_text


def test_fixed_column_wrap_overrides_wrap_mode_without_modifying_text(
    app: QApplication,
) -> None:
    _ = app
    editor = TextEditor()
    source_text = "abcdefghijklmnopqrstuvwxyz"
    editor.setPlainText(source_text)

    editor.set_word_wrap_enabled(False)
    editor.set_fixed_column_wrap_options(enabled=True, column=12)

    assert editor.toPlainText() == source_text
    assert editor.fixed_column_wrap_enabled is True
    assert editor.fixed_column_wrap_column == 12
    assert editor.lineWrapMode() == QPlainTextEdit.LineWrapMode.WidgetWidth
    assert editor.fixed_column_wrap_pixel_width() > 0

    editor.set_fixed_column_wrap_options(enabled=False, column=12)

    assert editor.lineWrapMode() == QPlainTextEdit.LineWrapMode.NoWrap
