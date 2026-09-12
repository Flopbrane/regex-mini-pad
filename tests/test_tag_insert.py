from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent, QTextCursor
from PySide6.QtWidgets import QApplication, QMenu

from dialogs.tag_insert_dialog import TagInsertDialog
from editor.tag_insert import TagSnippet, ordered_tag_snippet_groups, tag_snippet_groups
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
    html_category_menus = child_menus(group_menus[0])
    assert [menu.title() for menu in html_category_menus] == [
        "基本",
        "リンク / 画像",
        "レイアウト",
        "リスト",
        "コード",
    ]
    first_html_action = html_category_menus[0].actions()[0]
    assert first_html_action.text() == "段落 <p>"
    assert "必須パラメータ" in first_html_action.statusTip()
    image_action = html_category_menus[1].actions()[2]
    assert image_action.text() == "画像 <img>"
    assert "src" in image_action.statusTip()
    assert "alt" in image_action.toolTip()

    markdown_category_menus = child_menus(group_menus[1])
    assert [menu.title() for menu in markdown_category_menus] == [
        "テキスト",
        "リンク / 画像",
        "コード",
        "リスト",
        "ユーティリティ",
    ]
    assert [action.text() for action in markdown_category_menus[0].actions()] == [
        "見出し2",
        "見出し3",
        "太字",
        "斜体",
    ]


def test_insert_tag_picker_shortcut_is_available(app: QApplication) -> None:
    _ = app
    window = MainWindow()

    assert window.insert_tag_picker_action.shortcut().toString() == "Ctrl+Shift+T"
    assert window.insert_tag_picker_action.text() == "タグ挿入..."


def test_undo_redo_shortcuts_are_available(app: QApplication) -> None:
    _ = app
    window = MainWindow()

    assert window.undo_action.shortcut().toString() == "Ctrl+Z"
    assert [shortcut.toString() for shortcut in window.redo_action.shortcuts()] == [
        "Ctrl+Y",
        "Ctrl+Shift+Z",
    ]


def child_menus(menu: QMenu) -> list[QMenu]:
    menus: list[QMenu] = []
    for action in menu.actions():
        child_menu = action.menu()
        if isinstance(child_menu, QMenu):
            menus.append(child_menu)
    return menus


def test_context_menu_reuses_tag_insert_groups(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    context_menu = QMenu()
    insert_tag_menu = QMenu("タグ挿入", context_menu)

    window._populate_insert_tag_menu(insert_tag_menu)

    assert [menu.title() for menu in child_menus(insert_tag_menu)] == [
        "HTML",
        "Markdown",
        "WordPress HTML",
    ]


def test_tag_insert_dialog_filters_and_accepts_with_keyboard(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    dialog = TagInsertDialog(window.translator)
    dialog.set_snippet_groups(ordered_tag_snippet_groups(Path("sample.md")))

    dialog.search_edit.setText("コード")

    assert dialog.snippet_list.count() > 1
    assert "コード" in dialog.snippet_list.item(0).text()

    down_event = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Down,
        Qt.KeyboardModifier.NoModifier,
    )
    assert dialog.eventFilter(dialog.search_edit, down_event)
    assert dialog.snippet_list.currentRow() == 1

    enter_event = QKeyEvent(
        QEvent.Type.KeyPress,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.NoModifier,
    )
    assert dialog.eventFilter(dialog.snippet_list, enter_event)
    selected_snippet = dialog.selected_choice()
    assert selected_snippet is not None
    assert selected_snippet.label_key.startswith("tag.markdown.code_block")


def test_tag_group_order_prefers_current_file_extension(app: QApplication) -> None:
    _ = app
    window = MainWindow()

    window.current_save_file_path = Path("sample.md")
    assert child_menus_after_rebuild(window)[0].title() == "Markdown"

    window.current_save_file_path = Path("sample.html")
    assert child_menus_after_rebuild(window)[0].title() == "HTML"

    window.current_save_file_path = Path("sample.wp.html")
    assert child_menus_after_rebuild(window)[0].title() == "WordPress HTML"


def child_menus_after_rebuild(window: MainWindow) -> list[QMenu]:
    window._rebuild_insert_tag_menu()
    return child_menus(window.insert_tag_menu)


def test_ordered_tag_snippet_groups_prefers_extensions() -> None:
    assert ordered_tag_snippet_groups(Path("memo.md"))[0].label_key == (
        "tag.group.markdown"
    )
    assert ordered_tag_snippet_groups(Path("index.html"))[0].label_key == (
        "tag.group.html"
    )
    assert ordered_tag_snippet_groups(Path("article.wp.html"))[0].label_key == (
        "tag.group.wordpress_html"
    )


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


def test_insert_tag_snippet_can_be_undone_and_redone(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("hello")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    paragraph_snippet = tag_snippet_groups()[0].snippets[0]

    window.insert_tag_snippet(paragraph_snippet)
    window.undo_action.trigger()

    assert window.editor.toPlainText() == "hello"

    window.redo_action.trigger()

    assert window.editor.toPlainText() == "<p>hello</p>"


def test_insert_link_snippet_places_cursor_in_href(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("OpenAI")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    link_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[0].snippets
        if snippet.label_key == "tag.html.link"
    )

    window.insert_tag_snippet(link_snippet)

    assert window.editor.toPlainText() == '<a href="">OpenAI</a>'
    assert window.editor.textCursor().position() == len('<a href="')


def test_html_snippets_are_loaded_from_json() -> None:
    html_group = tag_snippet_groups()[0]

    assert html_group.label_key == "tag.group.html"
    assert len(html_group.snippets) == 13
    assert html_group.snippets[0].label_key == "tag.html.paragraph"
    assert html_group.snippets[-1].label_key == "tag.html.pre_code"


def test_insert_html_div_places_cursor_in_class_parameter(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("content")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    div_snippet = tag_snippet_groups()[0].snippets[7]

    window.insert_tag_snippet(div_snippet)

    assert window.editor.toPlainText() == '<div class="">content</div>'
    assert window.editor.textCursor().position() == len('<div class="')


def test_markdown_snippets_are_loaded_from_json() -> None:
    markdown_group = tag_snippet_groups()[1]

    assert markdown_group.label_key == "tag.group.markdown"
    assert len(markdown_group.snippets) == 20
    assert markdown_group.snippets[0].label_key == "tag.markdown.heading2"
    assert markdown_group.snippets[-1].label_key == "tag.markdown.horizontal_rule"


def test_insert_markdown_code_block_places_cursor_after_opening_fence(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("print('hello')")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    code_block_snippet = tag_snippet_groups()[1].snippets[7]

    window.insert_tag_snippet(code_block_snippet)

    assert window.editor.toPlainText() == "```\nprint('hello')\n```"
    assert window.editor.textCursor().position() == len("```")


def test_insert_markdown_python_code_block_uses_selected_language(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("print('hello')")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    python_code_block_snippet = tag_snippet_groups()[1].snippets[8]

    window.insert_tag_snippet(python_code_block_snippet)

    assert window.editor.toPlainText() == "```python\nprint('hello')\n```"
    assert window.editor.textCursor().position() == len("```python\nprint('hello')")


def test_wordpress_html_snippets_are_loaded_from_json() -> None:
    wordpress_group = tag_snippet_groups()[2]

    assert wordpress_group.label_key == "tag.group.wordpress_html"
    assert len(wordpress_group.snippets) == 11
    assert wordpress_group.snippets[0].label_key == "tag.wordpress.paragraph_block"
    assert wordpress_group.snippets[7].label_key == "tag.wordpress.html_code_box"


def test_insert_wordpress_code_block_uses_pre_code_markup(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("print('hello')")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    code_snippet = tag_snippet_groups()[2].snippets[5]

    window.insert_tag_snippet(code_snippet)

    assert window.editor.toPlainText() == (
        "<!-- wp:code -->\n"
        '<pre class="wp-block-code"><code>print(\'hello\')</code></pre>\n'
        "<!-- /wp:code -->"
    )
    assert window.editor.textCursor().position() == len(
        "<!-- wp:code -->\n"
        '<pre class="wp-block-code"><code>print(\'hello\')'
    )


def test_insert_wordpress_html_code_box_uses_custom_style(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("sample")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    html_code_box_snippet = tag_snippet_groups()[2].snippets[7]

    window.insert_tag_snippet(html_code_box_snippet)

    assert "<!-- wp:html -->" in window.editor.toPlainText()
    assert 'class="wp-block-code"' in window.editor.toPlainText()
    assert "display:inline-block; border:1px solid #999;" in window.editor.toPlainText()
    assert "<code>sample</code>" in window.editor.toPlainText()
