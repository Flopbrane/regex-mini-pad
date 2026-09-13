from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from main import MainWindow


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    assert isinstance(application, QApplication)
    return application


def test_new_file_adds_tab_without_clearing_current_text(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("first document")

    window.new_file()

    assert window.tab_widget.count() == 2
    first_editor = window._editor_at(0)
    assert first_editor is not None
    assert first_editor.toPlainText() == "first document"
    assert window.editor.toPlainText() == ""


def test_unsaved_tab_title_uses_first_line(app: QApplication, tmp_path: Path) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")

    window.editor.setPlainText("draft title\nbody")
    window.editor.document().setModified(True)
    window._update_tab_titles()

    assert window.tab_widget.tabText(0) == "*draft title"


def test_duplicate_tab_copies_text_as_unsaved_tab(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("backup draft\nbody")

    duplicate_editor = window.duplicate_tab(0)

    assert duplicate_editor is not None
    assert window.tab_widget.count() == 2
    assert duplicate_editor.toPlainText() == "backup draft\nbody"
    assert duplicate_editor.document().isModified()
    assert window.tab_widget.tabText(1) == "*backup draft"


def test_close_tab_can_discard_unsaved_changes(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("discard me")
    window.editor.document().setModified(True)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    closed = window.close_tab(0)

    assert closed
    assert window.tab_widget.count() == 1
    assert window.editor.toPlainText() == ""


def test_close_tab_can_be_cancelled(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("keep me")
    window.editor.document().setModified(True)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )

    closed = window.close_tab(0)

    assert not closed
    assert window.tab_widget.count() == 1
    assert window.editor.toPlainText() == "keep me"


def test_move_tab_to_new_window_moves_text_and_removes_source_tab(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("compare this\nbody")

    new_window = window.move_tab_to_new_window(0)

    assert new_window is not None
    assert new_window.editor.toPlainText() == "compare this\nbody"
    assert window.editor.toPlainText() == ""
    assert len(window.tab_windows) == 1


def test_each_window_has_uuid_and_child_window_is_registered(
    app: QApplication,
    tmp_path: Path,
) -> None:
    _ = app
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("child window source")

    new_window = window.move_tab_to_new_window(0)

    assert new_window is not None
    assert uuid.UUID(window.window_id)
    assert uuid.UUID(new_window.window_id)
    assert new_window.window_id != window.window_id
    assert window.child_windows[new_window.window_id] is new_window
