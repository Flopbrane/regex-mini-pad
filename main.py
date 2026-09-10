from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QAction, QCloseEvent, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)

from editor.text_editor import TextEditor
from fileio.file_manager import FileManager
from settings.settings_manager import SettingsManager


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_manager = SettingsManager(Path(__file__).with_name("settings.json"))
        self.file_manager = FileManager()
        self.current_save_file_path: Path | None = None

        self.editor = TextEditor()
        self.setCentralWidget(self.editor)

        self.setWindowTitle("Mini Editor")
        self.resize(900, 650)
        self._create_actions()
        self._create_menus()
        self._create_status_bar()
        self._restore_settings()

        self.editor.textChanged.connect(self._update_status_bar)
        self.editor.modificationChanged.connect(self._update_window_title)
        self._update_status_bar()
        self._update_window_title()

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._confirm_discard_changes():
            event.ignore()
            return
        self._save_settings()
        event.accept()

    def _create_actions(self) -> None:
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_file_as)

        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Alt+F4")
        self.exit_action.triggered.connect(self.close)

        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self.editor.redo)

        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self.editor.selectAll)

        self.word_wrap_action = QAction("&Word Wrap", self)
        self.word_wrap_action.setCheckable(True)
        self.word_wrap_action.toggled.connect(self.editor.set_word_wrap_enabled)

    def _create_menus(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.word_wrap_action)

    def _create_status_bar(self) -> None:
        self.setStatusBar(QStatusBar(self))

    def _restore_settings(self) -> None:
        settings = self.settings_manager.load()
        self.word_wrap_action.setChecked(settings.word_wrap_enabled)
        self.editor.set_word_wrap_enabled(settings.word_wrap_enabled)
        if settings.window_width > 0 and settings.window_height > 0:
            self.resize(settings.window_width, settings.window_height)

    def _save_settings(self) -> None:
        self.settings_manager.save(
            word_wrap_enabled=self.word_wrap_action.isChecked(),
            window_width=self.width(),
            window_height=self.height(),
        )

    def _update_status_bar(self) -> None:
        cursor = self.editor.textCursor()
        line_number = cursor.blockNumber() + 1
        column_number = cursor.positionInBlock() + 1
        character_count = len(self.editor.toPlainText())
        self.statusBar().showMessage(
            f"Line {line_number}, Column {column_number} | Characters {character_count}"
        )

    def _update_window_title(self) -> None:
        load_file_path = self.current_save_file_path
        document_name = load_file_path.name if load_file_path else "Untitled"
        changed_mark = "*" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"{changed_mark}{document_name} - Mini Editor")

    def _confirm_discard_changes(self) -> bool:
        if not self.editor.document().isModified():
            return True

        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            "The document has unsaved changes. Continue without saving?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes

    def new_file(self) -> None:
        if not self._confirm_discard_changes():
            return
        self.editor.clear()
        self.editor.document().setModified(False)
        self.current_save_file_path = None
        self._update_window_title()

    def open_file(self) -> None:
        if not self._confirm_discard_changes():
            return

        selected_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if not selected_path:
            return

        load_file_path = Path(selected_path)
        try:
            load_data = self.file_manager.load_text(load_file_path)
        except OSError as error:
            QMessageBox.critical(self, "Open Failed", str(error))
            return

        self.editor.setPlainText(load_data)
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.editor.document().setModified(False)
        self.current_save_file_path = load_file_path
        self._update_window_title()

    def save_file(self) -> None:
        if self.current_save_file_path is None:
            self.save_file_as()
            return
        self._save_to_path(self.current_save_file_path)

    def save_file_as(self) -> None:
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if not selected_path:
            return
        self._save_to_path(Path(selected_path))

    def _save_to_path(self, save_file_path: Path) -> None:
        save_data = self.editor.toPlainText()
        try:
            self.file_manager.save_text(save_file_path, save_data)
        except OSError as error:
            QMessageBox.critical(self, "Save Failed", str(error))
            return

        self.current_save_file_path = save_file_path
        self.editor.document().setModified(False)
        self._update_window_title()


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
