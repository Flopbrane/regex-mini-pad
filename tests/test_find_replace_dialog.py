from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMenu

from dialogs.find_replace_dialog import FindReplaceDialog
from localization.translator import Translator


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_recipe_sets_find_replace_and_regex_mode(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "ja")
    dialog = FindReplaceDialog(translator)

    dialog.set_search_recipe(r"[ \t]+$", "")

    assert dialog.find_text_edit.text() == r"[ \t]+$"
    assert dialog.replace_text_edit.text() == ""
    assert dialog.regular_expression_check_box.isChecked()


def test_preview_table_displays_rows(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = FindReplaceDialog(translator)

    dialog.set_preview_rows(
        [(2, "second  ", "second")],
        "Previewing 1 match(es).",
    )

    assert dialog.preview_summary_label.text() == "Previewing 1 match(es)."
    assert dialog.preview_table.rowCount() == 1
    line_item = dialog.preview_table.item(0, 0)
    before_item = dialog.preview_table.item(0, 1)
    after_item = dialog.preview_table.item(0, 2)
    assert line_item is not None
    assert before_item is not None
    assert after_item is not None
    assert line_item.text() == "2"
    assert before_item.text() == "second  "
    assert after_item.text() == "second"


def test_dialog_returns_visible_only_search_option(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = FindReplaceDialog(translator)

    dialog.visible_only_check_box.setChecked(True)

    assert dialog.current_search_options().visible_only


def test_dialog_has_explicit_previous_next_buttons(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "ja")
    dialog = FindReplaceDialog(translator)

    assert dialog.find_previous_button.text() == "↑"
    assert dialog.find_next_button.text() == "↓"
    assert dialog.find_previous_button.toolTip() == "前へ"
    assert dialog.find_next_button.toolTip() == "次へ"
    assert dialog.replace_marked_button.text() == "マーカー部分を全て置換"


def test_regex_snippet_insert_enables_regex_mode_and_places_cursor(
    app: QApplication,
) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = FindReplaceDialog(translator)
    dialog.find_text_edit.setText("prefix suffix")
    dialog.find_text_edit.setSelection(7, 6)

    dialog.insert_find_text("()", cursor_offset=1)

    assert dialog.regular_expression_check_box.isChecked()
    assert dialog.find_text_edit.text() == "prefix ()"
    assert dialog.find_text_edit.cursorPosition() == 8


def test_regex_insert_menu_is_grouped(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = FindReplaceDialog(translator)

    regex_menu = dialog.insert_regex_button.menu()
    assert regex_menu is not None
    group_menus: list[QMenu] = []
    for action in regex_menu.actions():
        child_menu = action.menu()
        if isinstance(child_menu, QMenu):
            group_menus.append(child_menu)

    assert [menu.title() for menu in group_menus] == [
        "Characters",
        "Positions",
        "Repetition",
        "Groups",
    ]
