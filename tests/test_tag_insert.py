from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent, QTextCursor
from PySide6.QtWidgets import QApplication, QMenu

from dialogs.tag_insert_dialog import TagInsertDialog
from editor.tag_insert import (
    TagSnippet,
    ordered_tag_snippet_groups,
    tag_snippet_category_key,
    tag_snippet_groups,
    wordpress_mode_keys,
)
from main import MainWindow

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
    assert window.insert_tag_menu.toolTipsVisible()
    assert all(menu.toolTipsVisible() for menu in group_menus)
    html_category_menus = child_menus(group_menus[0])
    assert [menu.title() for menu in html_category_menus] == [
        "基本",
        "テキスト",
        "リンク / 画像",
        "レイアウト",
        "リスト",
        "コード",
        "ユーティリティ",
    ]
    first_html_action = html_category_menus[0].actions()[0]
    assert first_html_action.text() == "段落 <p>"
    assert "必須パラメータ" in first_html_action.statusTip()
    image_action = html_category_menus[2].actions()[2]
    assert image_action.text() == "画像 <img>"
    assert "src" in image_action.statusTip()
    assert "alt" in image_action.toolTip()
    assert "&lt;img&gt;" in image_action.toolTip()

    markdown_category_menus = child_menus(group_menus[1])
    assert [menu.title() for menu in markdown_category_menus] == [
        "テキスト",
        "リンク / 画像",
        "コード",
        "リスト",
        "レイアウト",
        "ユーティリティ",
    ]
    assert [action.text() for action in markdown_category_menus[0].actions()] == [
        "見出し1",
        "見出し2",
        "見出し3",
        "見出し4",
        "太字",
        "斜体",
        "取り消し線",
    ]

    wordpress_mode_menus = child_menus(group_menus[2])
    assert [menu.title() for menu in wordpress_mode_menus] == [
        "Normal",
        "企業・事業所",
        "Hi-security",
    ]


def test_insert_tag_menu_hides_tooltips_when_hover_hints_are_disabled(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()

    window.hover_hints_enabled = False
    window._rebuild_insert_tag_menu()

    group_menus = child_menus(window.insert_tag_menu)
    html_category_menus = child_menus(group_menus[0])
    first_html_action = html_category_menus[0].actions()[0]

    assert not window.insert_tag_menu.toolTipsVisible()
    assert not group_menus[0].toolTipsVisible()
    assert "必須パラメータ" not in first_html_action.toolTip()
    assert first_html_action.statusTip() == ""


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


def test_editor_context_menu_has_tag_insert_actions(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    context_menu = window._create_editor_context_menu()

    action_texts = [action.text() for action in context_menu.actions()]
    insert_tag_menu: QMenu | None = None
    for action in context_menu.actions():
        child_menu = action.menu()
        if isinstance(child_menu, QMenu) and child_menu.title() == "タグ挿入(&T)":
            insert_tag_menu = child_menu
            break

    assert "タグ挿入..." in action_texts
    assert isinstance(insert_tag_menu, QMenu)
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


def test_tag_insert_dialog_updates_hint_on_hover(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    dialog = TagInsertDialog(window.translator)
    dialog.set_snippet_groups(ordered_tag_snippet_groups(Path("sample.html")))

    item = dialog.snippet_list.item(0)
    assert item is not None
    assert dialog.hint_label.textFormat() == Qt.TextFormat.PlainText
    assert "&lt;p&gt;" in item.toolTip()

    dialog.hint_label.clear()
    dialog._handle_hovered_item(item)

    assert "<p>" in dialog.hint_label.text()
    assert "必須パラメータ" in dialog.hint_label.text()


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
    assert len(html_group.snippets) == 20
    assert html_group.snippets[0].label_key == "tag.html.paragraph"
    assert html_group.snippets[-1].label_key == "tag.html.horizontal_rule"


def test_tag_dictionary_rejects_empty_required_values(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{selection}{cursor}</p>",
            }
        ],
    )

    with pytest.raises(ValueError, match=r"non-empty.*html_dict\.json item #1"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_rejects_missing_required_key(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.paragraph",
                "template": "<p>{selection}{cursor}</p>",
            }
        ],
    )

    with pytest.raises(ValueError, match=r"missing required key.*hint_key"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_rejects_duplicated_label_key(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.paragraph",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{selection}{cursor}</p>",
            },
            {
                "label_key": "tag.html.paragraph",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{selection}</p>",
            },
        ],
    )

    with pytest.raises(
        ValueError,
        match=r"duplicated label_key.*tag\.html\.paragraph.*item #2.*item #1",
    ):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_rejects_duplicated_cursor_placeholder(
    tmp_path: Path,
) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.paragraph",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{cursor}{selection}{cursor}</p>",
            }
        ],
    )

    with pytest.raises(ValueError, match=r"duplicated cursor.*html_dict\.json item #1"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_rejects_unknown_placeholder(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.paragraph",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{selected_text}</p>",
            }
        ],
    )

    with pytest.raises(ValueError, match=r"unknown placeholder.*html_dict\.json item #1"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_rejects_broken_placeholder(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.paragraph",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{selection</p>",
            }
        ],
    )

    with pytest.raises(ValueError, match=r"broken placeholder.*selection"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_accepts_structured_parameters(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.link",
                "hint_key": "tag.hint.html.link",
                "template": '<a href="{cursor}">{selection}</a>',
                "parameters": [
                    {
                        "name": "href",
                        "required": True,
                        "kind": "url",
                        "description_key": "tag.parameter.href",
                    }
                ],
            }
        ],
    )

    resources_path = tmp_path / "resources"
    resources_path.mkdir()
    write_app_text_files(
        resources_path,
        {
            "tag.html.link": "Link",
            "tag.hint.html.link": "Link hint",
            "tag.parameter.href": "Destination URL",
        },
    )

    snippet = tag_snippet_groups(tmp_path, resources_path)[0].snippets[0]

    assert snippet.parameters[0].name == "href"
    assert snippet.parameters[0].required is True
    assert snippet.parameters[0].kind == "url"
    assert snippet.parameters[0].description_key == "tag.parameter.href"


def test_tag_dictionary_rejects_invalid_parameters(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.paragraph",
                "hint_key": "tag.hint.html.paragraph",
                "template": "<p>{selection}{cursor}</p>",
                "parameters": [{"required": True}],
            }
        ],
    )

    with pytest.raises(ValueError, match=r"parameter requires non-empty name"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_rejects_duplicated_parameter_names(tmp_path: Path) -> None:
    write_tag_dictionary_files(
        tmp_path,
        html_items=[
            {
                "label_key": "tag.html.image",
                "hint_key": "tag.hint.html.image",
                "template": '<img src="{cursor}" alt="{selection}">',
                "parameters": [
                    {"name": "src", "required": True},
                    {"name": "src", "required": False},
                ],
            }
        ],
    )

    with pytest.raises(ValueError, match=r"duplicated name 'src'"):
        tag_snippet_groups(tmp_path)


def test_tag_dictionary_translation_keys_exist() -> None:
    snippets = [
        snippet
        for group in tag_snippet_groups()
        for snippet in group.snippets
    ]
    resource_paths = [
        PROJECT_ROOT / "resources" / "app_text_en.json",
        PROJECT_ROOT / "resources" / "app_text_ja.json",
    ]

    for resource_path in resource_paths:
        translations = json.loads(resource_path.read_text(encoding="utf-8"))
        missing_keys = [
            key
            for snippet in snippets
            for key in (snippet.label_key, snippet.hint_key)
            if key not in translations
        ]

        assert missing_keys == []


def test_tag_dictionary_rejects_missing_translation_key(tmp_path: Path) -> None:
    dictionaries_path = tmp_path / "dictionaries"
    resources_path = tmp_path / "resources"
    dictionaries_path.mkdir()
    resources_path.mkdir()
    write_tag_dictionary_files(
        dictionaries_path,
        html_items=[
            {
                "label_key": "tag.html.custom_missing",
                "hint_key": "tag.hint.html.custom_missing",
                "template": "<p>{selection}{cursor}</p>",
            }
        ],
    )
    write_app_text_files(
        resources_path,
        extra_keys={
            "tag.html.custom_missing": "Custom",
        },
    )

    with pytest.raises(
        ValueError,
        match=r"app_text_ja\.json.*tag\.hint\.html\.custom_missing",
    ):
        tag_snippet_groups(dictionaries_path, resources_path)


def write_tag_dictionary_files(
    dictionaries_path: Path,
    html_items: list[dict[str, object]],
) -> None:
    valid_item = {
        "label_key": "tag.html.paragraph",
        "hint_key": "tag.hint.html.paragraph",
        "template": "<p>{selection}{cursor}</p>",
    }
    (dictionaries_path / "html_dict.json").write_text(
        json.dumps(html_items),
        encoding="utf-8",
    )
    (dictionaries_path / "markdown_dict.json").write_text(
        json.dumps([valid_item]),
        encoding="utf-8",
    )
    (dictionaries_path / "wordpress_html_dict.json").write_text(
        json.dumps([valid_item]),
        encoding="utf-8",
    )


def write_app_text_files(
    resources_path: Path,
    extra_keys: dict[str, str] | None = None,
) -> None:
    texts = {
        "tag.group.html": "HTML",
        "tag.group.markdown": "Markdown",
        "tag.group.wordpress_html": "WordPress HTML",
        "tag.html.paragraph": "Paragraph",
        "tag.hint.html.paragraph": "Paragraph hint",
    }
    if extra_keys:
        texts.update(extra_keys)
    for language_code in ("ja", "en"):
        (resources_path / f"app_text_{language_code}.json").write_text(
            json.dumps(texts),
            encoding="utf-8",
        )


def test_insert_html_div_places_cursor_in_class_parameter(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("content")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    div_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[0].snippets
        if snippet.label_key == "tag.html.div"
    )

    window.insert_tag_snippet(div_snippet)

    assert window.editor.toPlainText() == '<div class="">content</div>'
    assert window.editor.textCursor().position() == len('<div class="')


def test_markdown_snippets_are_loaded_from_json() -> None:
    markdown_group = tag_snippet_groups()[1]

    assert markdown_group.label_key == "tag.group.markdown"
    assert len(markdown_group.snippets) == 26
    assert markdown_group.snippets[0].label_key == "tag.markdown.heading1"
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
    code_block_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[1].snippets
        if snippet.label_key == "tag.markdown.code_block"
    )

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
    python_code_block_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[1].snippets
        if snippet.label_key == "tag.markdown.code_block_python"
    )

    window.insert_tag_snippet(python_code_block_snippet)

    assert window.editor.toPlainText() == "```python\nprint('hello')\n```"
    assert window.editor.textCursor().position() == len("```python\nprint('hello')")


def test_wordpress_html_snippets_are_loaded_from_json() -> None:
    wordpress_group = tag_snippet_groups()[2]

    assert wordpress_group.label_key == "tag.group.wordpress_html"
    assert len(wordpress_group.snippets) == 28
    assert wordpress_group.snippets[0].label_key == "tag.wordpress.paragraph_block"
    assert wordpress_group.snippets[7].label_key == "tag.wordpress.html_code_box"
    assert wordpress_group.snippets[11].label_key == "tag.wordpress.link_block"
    assert wordpress_group.snippets[12].label_key == (
        "tag.wordpress.custom_frame_block"
    )
    assert wordpress_group.snippets[15].label_key == (
        "tag.wordpress.important_frame_block"
    )
    assert wordpress_group.snippets[21].label_key == (
        "tag.wordpress.columns_2_text_block"
    )
    assert wordpress_group.snippets[22].label_key == (
        "tag.wordpress.columns_3_text_block"
    )
    assert wordpress_group.snippets[-2].label_key == "tag.wordpress.video_block"
    assert wordpress_group.snippets[-1].label_key == "tag.wordpress.audio_block"


def test_wordpress_media_snippets_use_media_category() -> None:
    wordpress_group = tag_snippet_groups()[2]

    media_categories = {
        tag_snippet_category_key(wordpress_group.label_key, snippet)
        for snippet in wordpress_group.snippets
        if snippet.label_key
        in {
            "tag.wordpress.image_block",
            "tag.wordpress.media_text_left_block",
            "tag.wordpress.video_block",
            "tag.wordpress.audio_block",
        }
    }

    assert media_categories == {"tag.category.media"}


def test_wordpress_link_snippet_uses_link_image_category() -> None:
    wordpress_group = tag_snippet_groups()[2]
    link_snippet = next(
        snippet
        for snippet in wordpress_group.snippets
        if snippet.label_key == "tag.wordpress.link_block"
    )

    assert tag_snippet_category_key(wordpress_group.label_key, link_snippet) == (
        "tag.category.link_image"
    )


def test_wordpress_text_columns_use_layout_category() -> None:
    wordpress_group = tag_snippet_groups()[2]
    column_snippets = [
        snippet
        for snippet in wordpress_group.snippets
        if snippet.label_key
        in {
            "tag.wordpress.columns_2_text_block",
            "tag.wordpress.columns_3_text_block",
        }
    ]

    assert [
        tag_snippet_category_key(wordpress_group.label_key, snippet)
        for snippet in column_snippets
    ] == ["tag.category.layout", "tag.category.layout"]


def test_wordpress_custom_frame_uses_layout_category() -> None:
    wordpress_group = tag_snippet_groups()[2]
    frame_snippets = [
        snippet
        for snippet in wordpress_group.snippets
        if snippet.label_key
        in {
            "tag.wordpress.custom_frame_block",
            "tag.wordpress.notice_frame_block",
            "tag.wordpress.info_frame_block",
            "tag.wordpress.important_frame_block",
        }
    ]

    assert [
        tag_snippet_category_key(wordpress_group.label_key, snippet)
        for snippet in frame_snippets
    ] == [
        "tag.category.layout",
        "tag.category.layout",
        "tag.category.layout",
        "tag.category.layout",
    ]


def test_wordpress_snippets_have_expected_mode_groups() -> None:
    snippets = {snippet.label_key: snippet for snippet in tag_snippet_groups()[2].snippets}

    assert wordpress_mode_keys(snippets["tag.wordpress.paragraph_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.image_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.link_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.custom_frame_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.notice_frame_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.info_frame_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.important_frame_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.columns_2_text_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.columns_3_text_block"]) == (
        "tag.wordpress_mode.normal",
        "tag.wordpress_mode.business",
        "tag.wordpress_mode.high_security",
    )
    assert wordpress_mode_keys(snippets["tag.wordpress.html_code_box"]) == (
        "tag.wordpress_mode.normal",
    )


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
    assert "display: inline-block; border: 1px solid #999;" in (
        window.editor.toPlainText()
    )
    assert "\n><code>sample</code></pre>" in window.editor.toPlainText()


def test_insert_wordpress_link_block_places_cursor_in_href(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("公式サイト")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    link_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[2].snippets
        if snippet.label_key == "tag.wordpress.link_block"
    )

    window.insert_tag_snippet(link_snippet)

    assert window.editor.toPlainText() == (
        '<!-- wp:paragraph -->\n<p><a href="">公式サイト</a></p>\n'
        "<!-- /wp:paragraph -->"
    )
    assert window.editor.textCursor().position() == len(
        '<!-- wp:paragraph -->\n<p><a href="'
    )


def test_insert_wordpress_custom_frame_block_has_editable_style_parameters(
    app: QApplication,
) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("重要なお知らせ")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    frame_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[2].snippets
        if snippet.label_key == "tag.wordpress.custom_frame_block"
    )

    window.insert_tag_snippet(frame_snippet)

    editor_text = window.editor.toPlainText()
    assert "<!-- wp:group -->" in editor_text
    assert 'class="wp-block-group"' in editor_text
    assert "border: 2px solid #2f80ed;" in editor_text
    assert "background-color: #f5f9ff;" in editor_text
    assert "color: #111111;" in editor_text
    assert "<p>重要なお知らせ</p>" in editor_text
    assert window.editor.textCursor().position() == editor_text.index("</p>")


def test_insert_wordpress_frame_presets_have_distinct_default_colors(
    app: QApplication,
) -> None:
    _ = app
    snippets = {snippet.label_key: snippet for snippet in tag_snippet_groups()[2].snippets}

    expected_styles = {
        "tag.wordpress.notice_frame_block": (
            "border: 2px solid #f2c94c;",
            "background-color: #fff8e1;",
            "color: #3a2a00;",
        ),
        "tag.wordpress.info_frame_block": (
            "border: 2px solid #2f80ed;",
            "background-color: #eef6ff;",
            "color: #102a43;",
        ),
        "tag.wordpress.important_frame_block": (
            "border: 3px solid #d64545;",
            "background-color: #fff1f1;",
            "color: #4a1111;",
        ),
    }
    for label_key, style_parts in expected_styles.items():
        window = MainWindow()
        window.editor.setPlainText("本文")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)

        window.insert_tag_snippet(snippets[label_key])

        editor_text = window.editor.toPlainText()
        assert "<p>本文</p>" in editor_text
        for style_part in style_parts:
            assert style_part in editor_text


def test_insert_wordpress_two_column_text_block(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("1段目")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    two_column_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[2].snippets
        if snippet.label_key == "tag.wordpress.columns_2_text_block"
    )

    window.insert_tag_snippet(two_column_snippet)

    editor_text = window.editor.toPlainText()
    assert editor_text.count("<!-- wp:column -->") == 2
    assert "<p>1段目</p>" in editor_text
    assert "<p>ここに2段目の文章を入力します。</p>" in editor_text
    assert window.editor.textCursor().position() == editor_text.index("</p>")


def test_insert_wordpress_three_column_text_block(app: QApplication) -> None:
    _ = app
    window = MainWindow()
    window.editor.setPlainText("1段目")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    three_column_snippet = next(
        snippet
        for snippet in tag_snippet_groups()[2].snippets
        if snippet.label_key == "tag.wordpress.columns_3_text_block"
    )

    window.insert_tag_snippet(three_column_snippet)

    editor_text = window.editor.toPlainText()
    assert editor_text.count("<!-- wp:column -->") == 3
    assert "<p>1段目</p>" in editor_text
    assert "<p>ここに2段目の文章を入力します。</p>" in editor_text
    assert "<p>ここに3段目の文章を入力します。</p>" in editor_text
