from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from dialogs.options_dialog import OptionsDialog
from localization.translator import Translator
from settings.settings_manager import EditorSettings


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_options_dialog_groups_items_by_tabs(app: QApplication) -> None:
    _ = app
    dialog = OptionsDialog(Translator(Path("resources"), "ja"), EditorSettings())

    assert [dialog.tabs.tabText(index) for index in range(dialog.tabs.count())] == [
        "一般",
        "表示",
        "タグ挿入",
        "バックアップ",
        "フォント",
        "検索",
    ]
    assert dialog.wordpress_mode_combo.count() == 3
    assert dialog.hover_hints_checkbox.text() == "ホーバーヒントを表示する"
    assert dialog.line_numbers_checkbox.text() == "行番号"
    assert dialog.word_wrap_checkbox.text() == "折り返し"
    assert dialog.ruler_checkbox.text() == "文字数ルーラー"
    assert dialog.visible_spaces_checkbox.text() == "空白を表示"
    assert dialog.visible_tabs_checkbox.text() == "TABを表示"
    assert dialog.visible_newlines_checkbox.text() == "改行を表示"


def test_options_dialog_returns_editable_values(app: QApplication) -> None:
    _ = app
    dialog = OptionsDialog(
        Translator(Path("resources"), "ja"),
        EditorSettings(
            word_wrap_enabled=True,
            line_numbers_enabled=False,
            ruler_enabled=True,
            visible_spaces_enabled=True,
            visible_tabs_enabled=False,
            visible_newlines_enabled=True,
            wordpress_mode_label_key="tag.wordpress_mode.high_security",
            hover_hints_enabled=False,
            backup_folder="D:/backup",
            font_family="Consolas",
            font_size=14,
            search_marker_color="#9ed8ff",
            current_match_marker_color="#ffb3d9",
        ),
    )

    values = dialog.values()

    assert values.word_wrap_enabled is True
    assert values.line_numbers_enabled is False
    assert values.ruler_enabled is True
    assert values.visible_spaces_enabled is True
    assert values.visible_tabs_enabled is False
    assert values.visible_newlines_enabled is True
    assert values.wordpress_mode_label_key == "tag.wordpress_mode.high_security"
    assert values.hover_hints_enabled is False
    assert values.backup_folder == "D:/backup"
    assert values.font_size == 14
    assert values.search_marker_color == "#9ed8ff"
    assert values.current_match_marker_color == "#ffb3d9"
