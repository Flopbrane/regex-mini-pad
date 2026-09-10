from __future__ import annotations

import sys
from pathlib import Path
from re import error as RegexError

from PySide6.QtGui import QAction, QCloseEvent, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)

from dialogs.find_replace_dialog import FindReplaceDialog
from dialogs.regex_help_dialog import RegexHelpDialog
from editor.text_editor import TextEditor
from fileio.file_manager import FileManager
from search.search_engine import SearchEngine, SearchMatch, SearchOptions
from settings.settings_manager import SettingsManager


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_manager = SettingsManager(Path(__file__).with_name("settings.json"))
        self.file_manager = FileManager()
        self.search_engine = SearchEngine()
        self.current_save_file_path: Path | None = None
        self.find_replace_dialog: FindReplaceDialog | None = None
        self.regex_help_dialog: RegexHelpDialog | None = None
        self.search_scope: tuple[int, int] | None = None

        self.editor = TextEditor()
        self.setCentralWidget(self.editor)

        self.setWindowTitle("Mini Editor")
        self.resize(900, 650)
        self._create_actions()
        self._create_menus()
        self._create_status_bar()
        self._restore_settings()

        self.editor.textChanged.connect(self._update_status_bar)
        self.editor.cursorPositionChanged.connect(self._update_status_bar)
        self.editor.document().modificationChanged.connect(self._update_window_title)
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

        self.find_action = QAction("&Find / Replace...", self)
        self.find_action.setShortcut("Ctrl+F")
        self.find_action.triggered.connect(self.show_find_replace_dialog)

        self.word_wrap_action = QAction("&Word Wrap", self)
        self.word_wrap_action.setCheckable(True)
        self.word_wrap_action.toggled.connect(self.editor.set_word_wrap_enabled)

        self.line_numbers_action = QAction("&Line Numbers", self)
        self.line_numbers_action.setCheckable(True)
        self.line_numbers_action.toggled.connect(self.editor.set_line_numbers_enabled)

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

        search_menu = menu_bar.addMenu("&Search")
        search_menu.addAction(self.find_action)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.line_numbers_action)
        view_menu.addAction(self.word_wrap_action)

    def _create_status_bar(self) -> None:
        self.setStatusBar(QStatusBar(self))

    def _restore_settings(self) -> None:
        settings = self.settings_manager.load()
        self.line_numbers_action.setChecked(settings.line_numbers_enabled)
        self.editor.set_line_numbers_enabled(settings.line_numbers_enabled)
        self.word_wrap_action.setChecked(settings.word_wrap_enabled)
        self.editor.set_word_wrap_enabled(settings.word_wrap_enabled)
        if settings.window_width > 0 and settings.window_height > 0:
            self.resize(settings.window_width, settings.window_height)

    def _save_settings(self) -> None:
        self.settings_manager.save(
            word_wrap_enabled=self.word_wrap_action.isChecked(),
            line_numbers_enabled=self.line_numbers_action.isChecked(),
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

    def show_find_replace_dialog(self) -> None:
        if self.find_replace_dialog is None:
            self.find_replace_dialog = FindReplaceDialog(self)
            self.find_replace_dialog.find_requested.connect(self.find_next)
            self.find_replace_dialog.replace_requested.connect(self.replace_current)
            self.find_replace_dialog.replace_all_requested.connect(self.replace_all)
            self.find_replace_dialog.regex_help_requested.connect(self.show_regex_help_dialog)

        selected_text = self.editor.textCursor().selectedText()
        if selected_text:
            cursor = self.editor.textCursor()
            self.search_scope = (cursor.selectionStart(), cursor.selectionEnd())
            self.find_replace_dialog.set_find_text(selected_text.replace("\u2029", "\n"))
        else:
            self.search_scope = None
        self.find_replace_dialog.clear_error()
        self.find_replace_dialog.show()
        self.find_replace_dialog.raise_()
        self.find_replace_dialog.activateWindow()

    def find_next(self, search_text: str, options: SearchOptions) -> None:
        if not search_text:
            self._set_search_error("Enter text to find.")
            return

        cursor = self.editor.textCursor()
        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error("Select text before searching only selected text.")
            return

        source_text = scope_text if scope_text is not None else self.editor.toPlainText()
        start_position = cursor.selectionEnd() if cursor.hasSelection() else cursor.position()
        start_position = min(max(start_position - scope_offset, 0), len(source_text))

        try:
            match = self.search_engine.find_next(
                source_text,
                search_text,
                start_position,
                options,
            )
        except RegexError as error:
            self._set_search_error(f"Invalid regular expression: {error}")
            return

        if match is None:
            self._set_search_error("No matches found.")
            return

        self._select_match(
            SearchMatch(
                match.start + scope_offset,
                match.end + scope_offset,
                match.text,
            )
        )
        self._set_search_status("Match found.")

    def replace_current(
        self,
        search_text: str,
        replace_text: str,
        options: SearchOptions,
    ) -> None:
        if not search_text:
            self._set_search_error("Enter text to find.")
            return

        cursor = self.editor.textCursor()
        source_text = self.editor.toPlainText()
        selected_match = SearchMatch(
            cursor.selectionStart(),
            cursor.selectionEnd(),
            cursor.selectedText().replace("\u2029", "\n"),
        )

        try:
            current_selection_matches = self.search_engine.find_all(
                selected_match.text,
                search_text,
                options,
            )
            if (
                not cursor.hasSelection()
                or len(current_selection_matches) != 1
                or current_selection_matches[0].start != 0
                or current_selection_matches[0].end != len(selected_match.text)
            ):
                self.find_next(search_text, options)
                return

            result = self.search_engine.replace_match(
                source_text,
                selected_match,
                replace_text,
                search_text,
                options,
            )
        except RegexError as error:
            self._set_search_error(f"Invalid regular expression: {error}")
            return

        if result.count == 0:
            self._set_search_error("No current match to replace.")
            return

        self._replace_document_text(result.text)
        replaced_end = selected_match.start + len(result.text) - (
            len(source_text) - selected_match.end
        )
        self._set_cursor_position(replaced_end)
        self._set_search_status("Replaced 1 match.")

    def replace_all(
        self,
        search_text: str,
        replace_text: str,
        options: SearchOptions,
    ) -> None:
        if not search_text:
            self._set_search_error("Enter text to find.")
            return

        scope_text, _scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error("Select text before replacing only selected text.")
            return

        source_text = self.editor.toPlainText()
        target_text = scope_text if scope_text is not None else source_text

        try:
            result = self.search_engine.replace_all(
                target_text,
                search_text,
                replace_text,
                options,
            )
        except RegexError as error:
            self._set_search_error(f"Invalid regular expression: {error}")
            return

        if result.count == 0:
            self._set_search_error("No matches replaced.")
            return

        if scope_text is not None and self.search_scope is not None:
            scope_start, scope_end = self.search_scope
            result_text = source_text[:scope_start] + result.text + source_text[scope_end:]
            self.search_scope = (scope_start, scope_start + len(result.text))
        else:
            result_text = result.text

        self._replace_document_text(result_text)
        self._set_search_status(f"Replaced {result.count} match(es).")

    def show_regex_help_dialog(self) -> None:
        if self.regex_help_dialog is None:
            resources_path = Path(__file__).parent / "resources"
            regex_help_paths = {
                "EN_Ver.": resources_path / "regex_help_en.json",
                "JP_Ver.": resources_path / "regex_help_ja.json",
            }
            self.regex_help_dialog = RegexHelpDialog(regex_help_paths, self)
            self.regex_help_dialog.pattern_insert_requested.connect(
                self._insert_regex_pattern
            )

        self.regex_help_dialog.show()
        self.regex_help_dialog.raise_()
        self.regex_help_dialog.activateWindow()

    def _insert_regex_pattern(self, pattern: str) -> None:
        if self.find_replace_dialog is None:
            self.show_find_replace_dialog()
        if self.find_replace_dialog is not None:
            self.find_replace_dialog.insert_find_text(pattern)

    def _search_scope_text(self, options: SearchOptions) -> tuple[str | None, int]:
        if not options.selected_only:
            return None, 0

        if self.search_scope is None:
            cursor = self.editor.textCursor()
            if not cursor.hasSelection():
                return None, 0
            self.search_scope = (cursor.selectionStart(), cursor.selectionEnd())

        scope_start, scope_end = self.search_scope
        source_text = self.editor.toPlainText()
        if scope_start >= scope_end or scope_end > len(source_text):
            return None, 0
        return source_text[scope_start:scope_end], scope_start

    def _replace_document_text(self, text: str) -> None:
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(text)
        cursor.endEditBlock()

    def _select_match(self, match: SearchMatch) -> None:
        cursor = self.editor.textCursor()
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _set_cursor_position(self, position: int) -> None:
        cursor = self.editor.textCursor()
        cursor.setPosition(min(max(position, 0), len(self.editor.toPlainText())))
        self.editor.setTextCursor(cursor)

    def _set_search_error(self, message: str) -> None:
        if self.find_replace_dialog is not None:
            self.find_replace_dialog.set_error(message)
        self.statusBar().showMessage(message)

    def _set_search_status(self, message: str) -> None:
        if self.find_replace_dialog is not None:
            self.find_replace_dialog.clear_error()
        self.statusBar().showMessage(message)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
