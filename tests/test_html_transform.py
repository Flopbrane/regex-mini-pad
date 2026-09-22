from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QMenu

from main import MainWindow
from search.search_engine import SearchOptions


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def select_text(window: MainWindow, start: int, end: int) -> None:
    cursor = window.editor.textCursor()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)


def test_html_escape_selected_text_preserves_quotes_and_japanese(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    source_text = '前 <h1 class="title">タイトル & 本文</h1> 後'
    window.editor.setPlainText(source_text)
    select_text(window, 2, len(source_text) - 2)

    window.escape_selected_html()

    assert window.editor.toPlainText() == (
        '前 &lt;h1 class="title"&gt;タイトル &amp; 本文&lt;/h1&gt; 後'
    )


def test_html_unescape_selected_text(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    source_text = "前 &lt;h1&gt;タイトル&lt;/h1&gt; 後"
    window.editor.setPlainText(source_text)
    select_text(window, 2, len(source_text) - 2)

    window.unescape_selected_html()

    assert window.editor.toPlainText() == "前 <h1>タイトル</h1> 後"


def test_html_escape_changes_only_selection_and_can_be_undone(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    source_text = "keep <p>本文</p> keep"
    window.editor.setPlainText(source_text)
    select_text(window, len("keep "), len("keep <p>本文</p>"))

    window.escape_selected_html()

    assert window.editor.toPlainText() == "keep &lt;p&gt;本文&lt;/p&gt; keep"

    window.undo_action.trigger()

    assert window.editor.toPlainText() == source_text


def test_wordpress_code_block_escapes_multiline_indented_html(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    source_text = "before\n  <h2>タイトル</h2>\n  <p>本文です。</p>\nafter"
    selected_text = "  <h2>タイトル</h2>\n  <p>本文です。</p>"
    window.editor.setPlainText(source_text)
    start = len("before\n")
    select_text(window, start, start + len(selected_text))

    window.wrap_selected_as_wordpress_code_block()

    assert window.editor.toPlainText() == (
        "before\n"
        "<!-- wp:html -->\n"
        "<pre\n"
        '    class="wp-block-code"\n'
        '    style="display: inline-block; border: 1px solid #999; '
        "padding: 16px; border-radius: 8px; background-color: #f9f9f9;\"\n"
        "><code>"
        "  &lt;h2&gt;タイトル&lt;/h2&gt;\n"
        "  &lt;p&gt;本文です。&lt;/p&gt;"
        "</code></pre>\n"
        "<!-- /wp:html -->"
        "\nafter"
    )


def test_html_transform_does_nothing_without_selection(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    source_text = "<h1>タイトル</h1>"
    window.editor.setPlainText(source_text)
    window.editor.moveCursor(QTextCursor.MoveOperation.Start)

    window.escape_selected_html()

    assert window.editor.toPlainText() == source_text
    assert "選択" in window.statusBar().currentMessage()


def test_html_transform_context_menu_is_available(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    context_menu = window._create_editor_context_menu()

    html_transform_menu: QMenu | None = None
    for action in context_menu.actions():
        child_menu = action.menu()
        if isinstance(child_menu, QMenu) and child_menu.title() == "HTML変換":
            html_transform_menu = child_menu
            break

    assert html_transform_menu is not None
    assert [action.text() for action in html_transform_menu.actions()] == [
        "HTMLエスケープ",
        "HTMLエスケープ解除",
        "",
        "WordPressコードブロック化",
    ]


def test_html_transform_does_not_break_regex_search(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("<h1>タイトル</h1>")
    select_text(window, 0, len("<h1>タイトル</h1>"))
    window.escape_selected_html()

    window.find_next("タイトル", SearchOptions())

    assert window.editor.textCursor().selectedText() == "タイトル"
