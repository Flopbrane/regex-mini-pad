from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox

from fileio.unsaved_backup_manager import (
    UnsavedBackup,
    UnsavedBackupManager,
    UnsavedBackupSession,
)
from main import MainWindow
from portable_runtime import app_base_dir
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


def test_main_window_restores_unsaved_backup_session_when_accepted(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    UnsavedBackupManager(backup_path).save_session(
        UnsavedBackupSession(
            tabs=[
                UnsavedBackup(
                    text="first draft",
                    encoding="utf-8",
                    save_file_path=tmp_path / "first.txt",
                ),
                UnsavedBackup(
                    text="second draft",
                    encoding="cp932",
                    save_file_path=None,
                ),
            ],
            current_index=1,
        )
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
    first_editor = window._editor_at(0)
    second_editor = window._editor_at(1)

    assert first_editor is not None
    assert second_editor is not None
    assert window.tab_widget.count() == 2
    assert first_editor.toPlainText() == "first draft"
    assert second_editor.toPlainText() == "second draft"
    assert first_editor.document().isModified()
    assert second_editor.document().isModified()
    assert window.tab_widget.currentIndex() == 1
    assert window.current_encoding == "cp932"


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


def test_main_window_saves_session_for_all_modified_tabs(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )
    first_save_file_path = tmp_path / "first.txt"
    window._set_current_file_state(first_save_file_path, "utf-8")
    window.editor.setPlainText("first draft")
    window.editor.document().setModified(True)
    second_editor = window.create_editor_tab(
        text="second draft",
        encoding="cp932",
        modified=True,
    )
    second_editor.document().setModified(True)

    window._save_unsaved_backup()
    session = UnsavedBackupManager(backup_path).load_session()

    assert session is not None
    assert session.current_index == 1
    assert [tab.text for tab in session.tabs] == ["first draft", "second draft"]
    assert session.tabs[0].save_file_path == first_save_file_path
    assert session.tabs[1].save_file_path is None
    assert [tab.encoding for tab in session.tabs] == ["utf-8", "cp932"]


def test_main_window_saving_one_tab_preserves_other_modified_tab_backup(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )
    first_editor = window.editor
    first_editor.setPlainText("first draft")
    first_editor.document().setModified(True)
    second_editor = window.create_editor_tab(text="second draft", modified=True)
    second_editor.document().setModified(True)
    window.tab_widget.setCurrentIndex(0)

    assert window._save_to_path(tmp_path / "first.txt")
    session = UnsavedBackupManager(backup_path).load_session()

    assert session is not None
    assert [tab.text for tab in session.tabs] == ["second draft"]


def test_main_window_duplicate_tab_is_added_to_unsaved_session(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )
    window.editor.setPlainText("source draft")
    window.editor.document().setModified(True)

    window.duplicate_tab(0)
    session = UnsavedBackupManager(backup_path).load_session()

    assert session is not None
    assert [tab.text for tab in session.tabs] == ["source draft", "source draft"]


def test_main_window_closing_discarded_tab_updates_unsaved_session(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=backup_path,
    )
    first_editor = window.editor
    first_editor.setPlainText("discarded draft")
    first_editor.document().setModified(True)
    window.create_editor_tab(text="kept draft", modified=True)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    assert window.close_tab(0)
    session = UnsavedBackupManager(backup_path).load_session()

    assert session is not None
    assert [tab.text for tab in session.tabs] == ["kept draft"]


def test_main_window_saves_existing_file_backup_before_overwrite(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    save_file_path = tmp_path / "saved.txt"
    save_file_path.write_text("old text", encoding="utf-8")
    backup_folder = tmp_path / "backup"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=tmp_path / "autosave" / "unsaved_backup.json",
        restore_unsaved_backup=False,
    )
    window.backup_folder = str(backup_folder)
    window.file_backup_manager = window.file_backup_manager.__class__(
        window._file_backup_folder_for_folder(window.backup_folder)
    )
    window._set_current_file_state(save_file_path, "utf-8")
    window.editor.setPlainText("new text")
    window.editor.document().setModified(True)

    assert window._save_to_path(save_file_path)

    backups = window.file_backup_manager.backups_for_file(save_file_path)
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "old text"
    assert save_file_path.read_text(encoding="utf-8") == "new text"


def test_main_window_default_backup_paths_are_under_internal_folder(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        restore_unsaved_backup=False,
    )

    assert window.unsaved_backup_manager.backup_path == (
        app_base_dir() / "_internal" / "autosave" / "unsaved_backup.json"
    )
    assert window.file_backup_manager.backup_root == app_base_dir() / "_internal" / "backup"


def test_main_window_custom_backup_folder_is_used_as_file_backup_root(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    backup_folder = tmp_path / "custom-backup"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        restore_unsaved_backup=False,
    )

    assert window._file_backup_folder_for_folder(str(backup_folder)) == backup_folder
    assert window._unsaved_backup_path() == (
        app_base_dir() / "_internal" / "autosave" / "unsaved_backup.json"
    )


def test_main_window_restores_file_backup_into_editor(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    save_file_path = tmp_path / "saved.txt"
    save_file_path.write_text("backup text", encoding="utf-8")
    backup_folder = tmp_path / "backup"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=tmp_path / "autosave" / "unsaved_backup.json",
        restore_unsaved_backup=False,
    )
    window.backup_folder = str(backup_folder)
    window.file_backup_manager = window.file_backup_manager.__class__(
        window._file_backup_folder_for_folder(window.backup_folder)
    )
    window.file_backup_manager.backup_existing_file(save_file_path)
    save_file_path.write_text("current disk text", encoding="utf-8")
    window._set_current_file_state(save_file_path, "utf-8")
    window.editor.setPlainText("current editor text")
    window.editor.document().setModified(False)

    def select_first_backup(*args, **kwargs) -> tuple[str, bool]:
        labels = args[3]
        return labels[0], True

    monkeypatch.setattr(QInputDialog, "getItem", select_first_backup)

    window.restore_file_backup()

    assert window.editor.toPlainText() == "backup text"
    assert window.editor.document().isModified()
    assert save_file_path.read_text(encoding="utf-8") == "current disk text"


def test_main_window_keeps_modified_text_when_file_backup_restore_is_declined(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    save_file_path = tmp_path / "saved.txt"
    save_file_path.write_text("backup text", encoding="utf-8")
    backup_folder = tmp_path / "backup"
    window = MainWindow(
        settings_path=tmp_path / "settings.json",
        unsaved_backup_path=tmp_path / "autosave" / "unsaved_backup.json",
        restore_unsaved_backup=False,
    )
    window.backup_folder = str(backup_folder)
    window.file_backup_manager = window.file_backup_manager.__class__(
        window._file_backup_folder_for_folder(window.backup_folder)
    )
    window.file_backup_manager.backup_existing_file(save_file_path)
    window._set_current_file_state(save_file_path, "utf-8")
    window.editor.setPlainText("do not replace")
    window.editor.document().setModified(True)

    def select_first_backup(*args, **kwargs) -> tuple[str, bool]:
        labels = args[3]
        return labels[0], True

    monkeypatch.setattr(QInputDialog, "getItem", select_first_backup)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    window.restore_file_backup()

    assert window.editor.toPlainText() == "do not replace"
    assert window.editor.document().isModified()
