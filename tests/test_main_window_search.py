from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from main import MainWindow
from search.search_engine import SearchOptions


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_find_next_selects_regex_match(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("abc item-123 xyz")

    window.find_next(
        r"item-\d+",
        SearchOptions(regular_expression=True),
    )

    assert window.editor.textCursor().selectedText() == "item-123"


def test_replace_all_uses_regex_groups(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("item-01 item-20")

    window.replace_all(
        r"(\w+)-(\d+)",
        r"\2:\1",
        SearchOptions(regular_expression=True),
    )

    assert window.editor.toPlainText() == "01:item 20:item"


def test_invalid_regex_does_not_modify_document(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("keep this text")

    window.replace_all(
        r"[",
        "changed",
        SearchOptions(regular_expression=True),
    )

    assert window.editor.toPlainText() == "keep this text"


def test_replace_all_can_target_selected_text_only(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("first 123\nsecond 456\nthird 789")
    cursor = window.editor.textCursor()
    cursor.setPosition(10)
    cursor.setPosition(20, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    window.search_scope = (cursor.selectionStart(), cursor.selectionEnd())

    window.replace_all(
        r"\d+",
        "NUM",
        SearchOptions(regular_expression=True, selected_only=True),
    )

    assert window.editor.toPlainText() == "first 123\nsecond NUM\nthird 789"


def test_find_next_can_target_selected_text_only(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("target\ninside target\noutside")
    cursor = window.editor.textCursor()
    cursor.setPosition(7)
    cursor.setPosition(20, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    window.search_scope = (cursor.selectionStart(), cursor.selectionEnd())

    window.find_next(
        "target",
        SearchOptions(selected_only=True),
    )

    assert window.editor.textCursor().selectedText() == "target"
    assert window.editor.textCursor().selectionStart() == 14
