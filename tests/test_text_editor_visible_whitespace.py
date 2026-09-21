from __future__ import annotations

import os
import sys

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

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
        (1, "·"),
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
        (1, "·"),
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
