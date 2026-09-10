from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

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
