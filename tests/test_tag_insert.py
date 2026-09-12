from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QMenu

from editor.tag_insert import TagSnippet, tag_snippet_groups
from main import MainWindow


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_tag_snippet_renders_selection_and_cursor_position() -> None:
    snippet = TagSnippet(
        "label",
        "hint",
        '<a href="{cursor}">{selection}</a>',
    )

    rendered_text, cursor_position = snippet.render("OpenAI")

    assert rendered_text == '<a href="">OpenAI</a>'
    assert cursor_position == len('<a href="')


def test_insert_tag_menu_has_groups_and_parameter_hints(app: QApplication) -> None:
    _ = app
    window = MainWindow()

    assert window.insert_tag_menu.title() == "タグ挿入(&T)"
    group_menus: list[QMenu] = []
    for action in window.insert_tag_menu.actions():
        child_menu = action.menu()
        if isinstance(child_menu, QMenu):
            group_menus.append(child_menu)

    assert [menu.title() for menu in group_menus] == [
        "HTML",
        "Markdown",
        "WordPress HTML",
    ]
    first_html_action = group_menus[0].actions()[0]
    assert first_html_action.text() == "段落 <p>"
    assert "必須パラメータ" in first_html_action.statusTip()


def test_insert_tag_snippet_wraps_selected_text(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("hello")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    paragraph_snippet = tag_snippet_groups()[0].snippets[0]

    window.insert_tag_snippet(paragraph_snippet)

    assert window.editor.toPlainText() == "<p>hello</p>"
    assert window.editor.textCursor().position() == len("<p>hello")


def test_insert_link_snippet_places_cursor_in_href(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("OpenAI")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    link_snippet = tag_snippet_groups()[0].snippets[1]

    window.insert_tag_snippet(link_snippet)

    assert window.editor.toPlainText() == '<a href="">OpenAI</a>'
    assert window.editor.textCursor().position() == len('<a href="')
