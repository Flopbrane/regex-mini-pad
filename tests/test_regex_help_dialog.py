from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from dialogs.regex_help_dialog import RegexHelpDialog
from localization.translator import Translator


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_regex_help_loads_examples(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = RegexHelpDialog(Path("resources/regex_help_en.json"), translator)

    assert dialog.table.rowCount() >= 20
    assert dialog.table.columnCount() == 7
    assert dialog.table.item(0, 0) is not None
    assert dialog.table.item(0, 3) is not None


def test_regex_help_can_switch_between_english_and_japanese(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "ja")
    dialog = RegexHelpDialog(
        {
            "EN_Ver.": Path("resources/regex_help_en.json"),
            "JP_Ver.": Path("resources/regex_help_ja.json"),
        },
        translator,
    )

    assert dialog.language_combo_box.currentText() == "EN_Ver."
    dialog.language_combo_box.setCurrentText("JP_Ver.")

    assert dialog.language_combo_box.currentText() == "JP_Ver."
    header_item = dialog.table.horizontalHeaderItem(0)
    category_item = dialog.table.item(0, 0)
    assert header_item is not None
    assert category_item is not None
    assert header_item.text() == "種類"
    assert category_item.text() == "位置"


def test_help_headers_follow_help_language_not_app_language(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = RegexHelpDialog(
        {
            "EN_Ver.": Path("resources/regex_help_en.json"),
            "JP_Ver.": Path("resources/regex_help_ja.json"),
        },
        translator,
    )

    dialog.language_combo_box.setCurrentText("JP_Ver.")

    header_item = dialog.table.horizontalHeaderItem(0)
    assert header_item is not None
    assert header_item.text() == "種類"


def test_regex_help_emits_selected_pattern(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = RegexHelpDialog(Path("resources/regex_help_en.json"), translator)
    emitted_patterns: list[str] = []
    dialog.pattern_insert_requested.connect(emitted_patterns.append)
    dialog.table.selectRow(0)

    dialog._emit_selected_pattern()

    assert emitted_patterns
