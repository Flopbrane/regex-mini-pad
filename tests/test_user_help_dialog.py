from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from dialogs.user_help_dialog import UserHelpDialog
from localization.translator import Translator
from main import MainWindow


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_user_help_dialog_uses_application_language(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "ja")
    dialog = UserHelpDialog(translator)

    assert dialog.windowTitle() == "使い方"
    assert dialog.topic_list.item(0).text() == "ファイル"
    dialog.topic_list.setCurrentRow(3)
    assert "タグ挿入" in dialog.help_browser.toPlainText()
    assert "WordPress HTML モード" in dialog.help_browser.toPlainText()
    assert "候補から隠します" in dialog.help_browser.toPlainText()
    assert dialog.topic_list.item(4).text() == "HTML属性図鑑"
    assert dialog.topic_list.item(5).text() == "WPパラメータ記述の注意事項"

    translator.set_language("en")
    dialog.apply_language()

    assert dialog.windowTitle() == "Help"
    assert dialog.topic_list.item(3).text() == "Tag Insertion"
    assert dialog.topic_list.item(4).text() == "HTML Attribute Guide"
    assert dialog.topic_list.item(5).text() == "WordPress Parameter Notes"
    assert "Tag Insertion" in dialog.help_browser.toPlainText()
    assert "WordPress HTML Modes" in dialog.help_browser.toPlainText()
    assert "hide risky snippets" in dialog.help_browser.toPlainText()


def test_user_help_dialog_can_navigate_topics(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "ja")
    dialog = UserHelpDialog(translator)

    dialog.topic_list.setCurrentRow(2)

    assert "検索 / 置換" in dialog.help_browser.toPlainText()

    dialog.topic_list.setCurrentRow(4)

    help_text = dialog.help_browser.toPlainText()

    assert "HTML属性図鑑" in help_text
    assert 'href="https://www.example.com"' in help_text
    assert "CSSが無い場合" in help_text
    assert "class=\"lead-text\"" in help_text
    assert "style=\"color: #333;" in help_text

    dialog.topic_list.setCurrentRow(5)

    help_text = dialog.help_browser.toPlainText()

    assert "WPパラメータ記述の注意事項" in help_text
    assert '{"level":3}' in help_text
    assert "ブロックコメント側とHTML側" in help_text
    assert "Gutenbergで作成して保存した後のHTML" in help_text

    dialog.topic_list.setCurrentRow(6)

    assert "ステータスバー" in dialog.help_browser.toPlainText()


def test_user_help_dialog_has_english_attribute_guide(app: QApplication) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = UserHelpDialog(translator)

    dialog.topic_list.setCurrentRow(4)

    help_text = dialog.help_browser.toPlainText()

    assert "HTML Attribute Guide" in help_text
    assert 'href="https://www.example.com"' in help_text
    assert "Without that CSS" in help_text
    assert "class=\"lead-text\"" in help_text
    assert "style=\"color: #333;" in help_text


def test_user_help_dialog_has_english_wordpress_parameter_notes(
    app: QApplication,
) -> None:
    _ = app
    translator = Translator(Path("resources"), "en")
    dialog = UserHelpDialog(translator)

    dialog.topic_list.setCurrentRow(5)

    help_text = dialog.help_browser.toPlainText()

    assert "WordPress Parameter Notes" in help_text
    assert '{"level":3}' in help_text
    assert "block comment and HTML" in help_text
    assert "Copying HTML from Gutenberg after saving" in help_text


def test_main_window_has_user_help_action(app: QApplication) -> None:
    _ = app
    window = MainWindow()

    assert window.user_help_action.shortcut().toString() == "F1"
    assert window.user_help_action.text() == "使い方(&H)..."

    window.show_user_help_dialog()

    assert window.user_help_dialog is not None
    assert window.user_help_dialog.isVisible()
