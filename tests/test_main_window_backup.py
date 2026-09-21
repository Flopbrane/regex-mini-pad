from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from fileio.unsaved_backup_manager import UnsavedBackup, UnsavedBackupManager
from main import MainWindow
from settings.settings_manager import SettingsManager


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_main_window_restores_unsaved_backup_when_accepted(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    UnsavedBackupManager(backup_path).save(
        UnsavedBackup(text="draft text", encoding="utf-8")
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )

    assert window.editor.toPlainText() == "draft text"
    assert window.editor.document().isModified()


def test_main_window_clears_unsaved_backup_when_declined(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    UnsavedBackupManager(backup_path).save(
        UnsavedBackup(text="draft text", encoding="utf-8")
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )

    assert window.editor.toPlainText() == ""
    assert not backup_path.exists()


def test_main_window_skips_unsaved_backup_restore_when_option_is_disabled(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    settings_path = tmp_path / "settings.json"
    UnsavedBackupManager(backup_path).save(
        UnsavedBackup(text="draft text", encoding="utf-8")
    )
    SettingsManager(settings_path).save(
        word_wrap_enabled=False,
        line_numbers_enabled=True,
        ruler_enabled=False,
        visible_spaces_enabled=False,
        visible_tabs_enabled=False,
        visible_newlines_enabled=False,
        fixed_column_wrap_enabled=False,
        fixed_column_wrap_column=80,
        startup_restore_enabled=False,
        language_code="ja",
        default_encoding="utf-8",
        newline_code="lf",
        window_width=900,
        window_height=650,
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: pytest.fail("restore dialog should not open"),
    )

    window = MainWindow(
        settings_path=settings_path,
        unsaved_backup_path=backup_path,
    )

    assert window.editor.toPlainText() == ""
    assert backup_path.exists()


def test_main_window_saves_and_clears_unsaved_backup(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )
    window.editor.setPlainText("draft text")
    window.editor.document().setModified(True)

    window._save_unsaved_backup()

    assert backup_path.exists()

    window._save_to_path(tmp_path / "saved.txt")

    assert not backup_path.exists()
