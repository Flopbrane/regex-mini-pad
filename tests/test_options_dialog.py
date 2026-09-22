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
    assert dialog.startup_restore_checkbox.text() == "起動時の復元"
    assert dialog.dictionary_check_checkbox.text() == "Dict 検証"
    assert dialog.regex_lint_checkbox.text() == "正規表現チェック"
    assert dialog.html_typo_lint_checkbox.text() == "HTML/WP表記チェック"
    assert dialog.line_numbers_checkbox.text() == "行番号"
    assert dialog.word_wrap_checkbox.text() == "折り返し"
    assert dialog.fixed_column_wrap_checkbox.text() == "設定文字数で折り返す"
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
            fixed_column_wrap_enabled=True,
            fixed_column_wrap_column=72,
            startup_restore_enabled=False,
            language_code="en",
            default_encoding="cp932",
            newline_code="crlf",
            wordpress_mode_label_key="tag.wordpress_mode.high_security",
            hover_hints_enabled=False,
            user_dictionary_folder="D:/dicts",
            dictionary_check_enabled=False,
            backup_folder="D:/backup",
            backup_retention_count=12,
            backup_retention_days=45,
            font_family="Consolas",
            font_size=14,
            tab_width=8,
            search_marker_color="#9ed8ff",
            current_match_marker_color="#ffb3d9",
            regex_lint_enabled=False,
            html_typo_lint_enabled=False,
        ),
    )

    values = dialog.values()

    assert values.word_wrap_enabled is True
    assert values.line_numbers_enabled is False
    assert values.ruler_enabled is True
    assert values.visible_spaces_enabled is True
    assert values.visible_tabs_enabled is False
    assert values.visible_newlines_enabled is True
    assert values.fixed_column_wrap_enabled is True
    assert values.fixed_column_wrap_column == 72
    assert values.startup_restore_enabled is False
    assert values.language_code == "en"
    assert values.default_encoding == "cp932"
    assert values.newline_code == "crlf"
    assert values.wordpress_mode_label_key == "tag.wordpress_mode.high_security"
    assert values.hover_hints_enabled is False
    assert values.user_dictionary_folder == "D:/dicts"
    assert values.dictionary_check_enabled is False
    assert values.backup_folder == "D:/backup"
    assert values.backup_retention_count == 12
    assert values.backup_retention_days == 45
    assert values.font_size == 14
    assert values.tab_width == 8
    assert values.search_marker_color == "#9ed8ff"
    assert values.current_match_marker_color == "#ffb3d9"
    assert values.regex_lint_enabled is False
    assert values.html_typo_lint_enabled is False
