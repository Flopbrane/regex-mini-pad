from __future__ import annotations

import sys
from pathlib import Path
from re import error as RegexError

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QKeySequence, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
)

from dialogs.find_replace_dialog import FindReplaceDialog
from dialogs.regex_help_dialog import RegexHelpDialog
from dialogs.tag_insert_dialog import TagInsertDialog
from dialogs.user_help_dialog import UserHelpDialog
from editor.tag_insert import (
    TagSnippet,
    ordered_tag_snippet_groups,
    tag_snippet_category_key,
)
from editor.text_editor import TextEditor
from fileio.file_manager import FileManager
from localization.translator import Translator
from search.search_engine import SearchEngine, SearchMatch, SearchOptions
from settings.settings_manager import SettingsManager

ENCODING_OPTIONS = {
    "UTF-8": "utf-8",
    "UTF-8 with BOM": "utf-8-sig",
    "CP932 / Shift_JIS": "cp932",
    "Shift_JIS": "shift_jis",
    "EUC-JP": "euc_jp",
    "UTF-16": "utf-16",
    "UTF-16 LE": "utf-16-le",
    "UTF-16 BE": "utf-16-be",
}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.resources_path = Path(__file__).parent / "resources"
        self.settings_manager = SettingsManager(Path(__file__).with_name("settings.json"))
        settings = self.settings_manager.load()
        self.translator = Translator(self.resources_path, settings.language_code)
        self.file_manager = FileManager()
        self.search_engine = SearchEngine()
        self.current_save_file_path: Path | None = None
        self.current_encoding = "utf-8"
        self.find_replace_dialog: FindReplaceDialog | None = None
        self.regex_help_dialog: RegexHelpDialog | None = None
        self.tag_insert_dialog: TagInsertDialog | None = None
        self.user_help_dialog: UserHelpDialog | None = None
        self.search_scope: tuple[int, int] | None = None

        self.editor = TextEditor()
        self.setCentralWidget(self.editor)

        self.resize(900, 650)
        self._create_actions()
        self._create_menus()
        self._create_status_bar()
        self._restore_settings(settings)
        self._apply_language()

        self.editor.textChanged.connect(self._update_status_bar)
        self.editor.textChanged.connect(self._refresh_search_highlights_from_dialog)
        self.editor.cursorPositionChanged.connect(self._update_status_bar)
        self.editor.document().modificationChanged.connect(self._update_window_title)
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self._show_editor_context_menu)
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

        self.open_with_encoding_menu = QMenu(self)
        self.open_encoding_actions: dict[str, QAction] = {}
        for label, encoding in ENCODING_OPTIONS.items():
            action = QAction(label, self)
            action.triggered.connect(
                lambda checked=False, value=encoding: self.open_file(value)
            )
            self.open_encoding_actions[encoding] = action
            self.open_with_encoding_menu.addAction(action)

        self.reload_action = QAction(self)
        self.reload_action.setShortcut("Ctrl+R")
        self.reload_action.triggered.connect(self.reload_file)

        self.reload_with_encoding_menu = QMenu(self)
        self.reload_encoding_actions: dict[str, QAction] = {}
        for label, encoding in ENCODING_OPTIONS.items():
            action = QAction(label, self)
            action.triggered.connect(
                lambda checked=False, value=encoding: self.reload_file(value)
            )
            self.reload_encoding_actions[encoding] = action
            self.reload_with_encoding_menu.addAction(action)

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
        self.redo_action.setShortcuts(
            [QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")]
        )
        self.redo_action.triggered.connect(self.editor.redo)

        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self.editor.selectAll)

        self.insert_tag_menu = QMenu(self)
        self.insert_tag_picker_action = QAction(self)
        self.insert_tag_picker_action.setShortcut("Ctrl+Shift+T")
        self.insert_tag_picker_action.triggered.connect(self.show_tag_insert_dialog)

        self.find_action = QAction(self)
        self.find_action.setShortcut("Ctrl+F")
        self.find_action.triggered.connect(self.show_find_replace_dialog)

        self.word_wrap_action = QAction(self)
        self.word_wrap_action.setCheckable(True)
        self.word_wrap_action.toggled.connect(self.editor.set_word_wrap_enabled)

        self.line_numbers_action = QAction(self)
        self.line_numbers_action.setCheckable(True)
        self.line_numbers_action.toggled.connect(self.editor.set_line_numbers_enabled)

        self.user_help_action = QAction(self)
        self.user_help_action.setShortcut("F1")
        self.user_help_action.triggered.connect(self.show_user_help_dialog)

        self.english_action = QAction(self)
        self.english_action.setCheckable(True)
        self.english_action.triggered.connect(lambda: self.set_language("en"))

        self.japanese_action = QAction(self)
        self.japanese_action.setCheckable(True)
        self.japanese_action.triggered.connect(lambda: self.set_language("ja"))

        self.language_action_group = QActionGroup(self)
        self.language_action_group.setExclusive(True)
        self.language_action_group.addAction(self.english_action)
        self.language_action_group.addAction(self.japanese_action)

    def _create_menus(self) -> None:
        menu_bar = self.menuBar()

        self.file_menu = QMenu(self)
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addMenu(self.open_with_encoding_menu)
        self.file_menu.addAction(self.reload_action)
        self.file_menu.addMenu(self.reload_with_encoding_menu)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        menu_bar.addMenu(self.file_menu)

        self.edit_menu = QMenu(self)
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.select_all_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.insert_tag_picker_action)
        self.edit_menu.addMenu(self.insert_tag_menu)
        menu_bar.addMenu(self.edit_menu)

        self.search_menu = QMenu(self)
        self.search_menu.addAction(self.find_action)
        menu_bar.addMenu(self.search_menu)

        self.view_menu = QMenu(self)
        self.view_menu.addAction(self.line_numbers_action)
        self.view_menu.addAction(self.word_wrap_action)
        menu_bar.addMenu(self.view_menu)

        self.language_menu = QMenu(self)
        self.language_menu.addAction(self.english_action)
        self.language_menu.addAction(self.japanese_action)
        menu_bar.addMenu(self.language_menu)

        self.help_menu = QMenu(self)
        self.help_menu.addAction(self.user_help_action)
        menu_bar.addMenu(self.help_menu)

    def _create_status_bar(self) -> None:
        self.setStatusBar(QStatusBar(self))

    def _restore_settings(self, settings) -> None:
        self.line_numbers_action.setChecked(settings.line_numbers_enabled)
        self.editor.set_line_numbers_enabled(settings.line_numbers_enabled)
        self.word_wrap_action.setChecked(settings.word_wrap_enabled)
        self.editor.set_word_wrap_enabled(settings.word_wrap_enabled)
        self.english_action.setChecked(settings.language_code == "en")
        self.japanese_action.setChecked(settings.language_code != "en")
        if settings.window_width > 0 and settings.window_height > 0:
            self.resize(settings.window_width, settings.window_height)

    def _save_settings(self) -> None:
        self.settings_manager.save(
            word_wrap_enabled=self.word_wrap_action.isChecked(),
            line_numbers_enabled=self.line_numbers_action.isChecked(),
            language_code=self.translator.language_code,
            window_width=self.width(),
            window_height=self.height(),
        )

    def set_language(self, language_code: str) -> None:
        self.translator.set_language(language_code)
        self.english_action.setChecked(language_code == "en")
        self.japanese_action.setChecked(language_code == "ja")
        self._apply_language()
        self._save_settings()

    def _apply_language(self) -> None:
        self.file_menu.setTitle(self.translator.text("menu.file"))
        self.edit_menu.setTitle(self.translator.text("menu.edit"))
        self.search_menu.setTitle(self.translator.text("menu.search"))
        self.view_menu.setTitle(self.translator.text("menu.view"))
        self.language_menu.setTitle(self.translator.text("menu.language"))
        self.help_menu.setTitle(self.translator.text("menu.help"))

        self.new_action.setText(self.translator.text("action.new"))
        self.open_action.setText(self.translator.text("action.open"))
        self.open_with_encoding_menu.setTitle(
            self.translator.text("action.open_with_encoding")
        )
        self.reload_action.setText(self.translator.text("action.reload"))
        self.reload_with_encoding_menu.setTitle(
            self.translator.text("action.reload_with_encoding")
        )
        self.save_action.setText(self.translator.text("action.save"))
        self.save_as_action.setText(self.translator.text("action.save_as"))
        self.exit_action.setText(self.translator.text("action.exit"))
        self.undo_action.setText(self.translator.text("action.undo"))
        self.redo_action.setText(self.translator.text("action.redo"))
        self.select_all_action.setText(self.translator.text("action.select_all"))
        self.insert_tag_picker_action.setText(
            self.translator.text("action.insert_tag_picker")
        )
        self._rebuild_insert_tag_menu()
        self.find_action.setText(self.translator.text("action.find_replace"))
        self.word_wrap_action.setText(self.translator.text("action.word_wrap"))
        self.line_numbers_action.setText(self.translator.text("action.line_numbers"))
        self.user_help_action.setText(self.translator.text("action.user_help"))
        self.english_action.setText(self.translator.text("language.english"))
        self.japanese_action.setText(self.translator.text("language.japanese"))

        if self.find_replace_dialog is not None:
            self.find_replace_dialog.apply_language()
        if self.regex_help_dialog is not None:
            self.regex_help_dialog.apply_language()
        if self.tag_insert_dialog is not None:
            self.tag_insert_dialog.apply_language()
        if self.user_help_dialog is not None:
            self.user_help_dialog.apply_language()
        self._update_status_bar()
        self._update_window_title()

    def _rebuild_insert_tag_menu(self) -> None:
        self.insert_tag_menu.clear()
        self.insert_tag_menu.setTitle(self.translator.text("action.insert_tag"))
        self._populate_insert_tag_menu(self.insert_tag_menu)

    def _populate_insert_tag_menu(self, root_menu: QMenu) -> None:
        for group in ordered_tag_snippet_groups(self.current_save_file_path):
            group_menu = root_menu.addMenu(self.translator.text(group.label_key))
            assert group_menu is not None
            category_menus: dict[str, QMenu] = {}
            for snippet in group.snippets:
                category_key = tag_snippet_category_key(group.label_key, snippet)
                category_menu = category_menus.get(category_key)
                if category_menu is None:
                    category_menu = group_menu.addMenu(self.translator.text(category_key))
                    assert category_menu is not None
                    category_menus[category_key] = category_menu
                category_menu.addAction(self._create_tag_snippet_action(snippet))

    def _create_tag_snippet_action(self, snippet: TagSnippet) -> QAction:
        label = self.translator.text(snippet.label_key)
        hint = self.translator.text(snippet.hint_key)
        action = QAction(label, self)
        action.setStatusTip(hint)
        action.setToolTip(hint)
        action.hovered.connect(
            lambda hint_text=hint: self.statusBar().showMessage(hint_text)
        )
        action.triggered.connect(
            lambda checked=False, value=snippet: self.insert_tag_snippet(value)
        )
        return action

    def _show_editor_context_menu(self, position: QPoint) -> None:
        context_menu = self.editor.createStandardContextMenu()
        context_menu.addSeparator()
        context_menu.addAction(self.insert_tag_picker_action)
        insert_tag_menu = QMenu(self.translator.text("action.insert_tag"), context_menu)
        self._populate_insert_tag_menu(insert_tag_menu)
        context_menu.addMenu(insert_tag_menu)
        context_menu.exec(self.editor.mapToGlobal(position))

    def show_tag_insert_dialog(self) -> None:
        if self.tag_insert_dialog is None:
            self.tag_insert_dialog = TagInsertDialog(self.translator, self)

        self.tag_insert_dialog.set_snippet_groups(
            ordered_tag_snippet_groups(self.current_save_file_path)
        )
        self.tag_insert_dialog.search_edit.clear()
        self.tag_insert_dialog.selected_snippet = None
        if self.tag_insert_dialog.exec() != TagInsertDialog.DialogCode.Accepted:
            return
        selected_snippet = self.tag_insert_dialog.selected_choice()
        if selected_snippet is not None:
            self.insert_tag_snippet(selected_snippet)

    def insert_tag_snippet(self, snippet: TagSnippet) -> None:
        cursor = self.editor.textCursor()
        insert_start = cursor.selectionStart()
        selected_text = cursor.selectedText().replace("\u2029", "\n")
        insert_text, cursor_offset = snippet.render(selected_text)

        cursor.beginEditBlock()
        cursor.insertText(insert_text)
        cursor.endEditBlock()
        cursor.setPosition(insert_start + cursor_offset)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _update_status_bar(self) -> None:
        cursor = self.editor.textCursor()
        line_number = cursor.blockNumber() + 1
        column_number = cursor.positionInBlock() + 1
        character_count = len(self.editor.toPlainText())
        self.statusBar().showMessage(
            self.translator.text(
                "status.position",
                line=line_number,
                column=column_number,
                characters=character_count,
            )
        )

    def _update_window_title(self) -> None:
        load_file_path = self.current_save_file_path
        document_name = (
            load_file_path.name
            if load_file_path
            else self.translator.text("document.untitled")
        )
        changed_mark = "*" if self.editor.document().isModified() else ""
        self.setWindowTitle(
            f"{changed_mark}{document_name} - {self.translator.text('app.title')}"
        )

    def _confirm_discard_changes(self) -> bool:
        if not self.editor.document().isModified():
            return True

        result = QMessageBox.question(
            self,
            self.translator.text("dialog.unsaved.title"),
            self.translator.text("dialog.unsaved.message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return result == QMessageBox.StandardButton.Yes

    def new_file(self) -> None:
        if not self._confirm_discard_changes():
            return
        self.editor.clear()
        self.editor.clear_search_matches()
        self.editor.document().setModified(False)
        self.current_save_file_path = None
        self._update_window_title()

    def open_file(self, encoding: str | None = None) -> None:
        if not self._confirm_discard_changes():
            return

        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.text("dialog.open.title"),
        )
        if not selected_path:
            return

        load_file_path = Path(selected_path)
        selected_encoding = encoding or "utf-8"
        try:
            load_data = self.file_manager.load_text(load_file_path, selected_encoding)
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(
                self,
                self.translator.text("dialog.open_failed.title"),
                str(error),
            )
            return

        self.editor.setPlainText(load_data)
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.editor.document().setModified(False)
        self.current_save_file_path = load_file_path
        self.current_encoding = selected_encoding
        self._update_window_title()
        self._set_encoding_status()

    def reload_file(self, encoding: str | None = None) -> None:
        if self.current_save_file_path is None:
            self._set_search_error(self.translator.text("dialog.reload_no_file"))
            return
        if not self._confirm_discard_changes():
            return

        selected_encoding = encoding or self.current_encoding
        try:
            load_data = self.file_manager.load_text(
                self.current_save_file_path,
                selected_encoding,
            )
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(
                self,
                self.translator.text("dialog.reload_failed.title"),
                self.translator.text(
                    "dialog.encoding_failed",
                    encoding=selected_encoding,
                    error=error,
                ),
            )
            return

        self.current_encoding = selected_encoding
        self.editor.setPlainText(load_data)
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.editor.document().setModified(False)
        self._update_window_title()
        self._set_encoding_status()

    def save_file(self) -> None:
        if self.current_save_file_path is None:
            self.save_file_as()
            return
        self._save_to_path(self.current_save_file_path)

    def save_file_as(self) -> None:
        selected_save_file_path, selected_encoding = self._get_save_file_path()
        if selected_save_file_path is None:
            return
        self.current_encoding = selected_encoding
        self._save_to_path(selected_save_file_path)

    def _get_save_file_path(self) -> tuple[Path | None, str]:
        dialog = QFileDialog(self, self.translator.text("dialog.save_as.title"))
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.selectFile(
            self.current_save_file_path.name if self.current_save_file_path else ""
        )

        encoding_combo_box = QComboBox(dialog)
        for label, encoding in ENCODING_OPTIONS.items():
            encoding_combo_box.addItem(label, encoding)
        current_encoding_index = encoding_combo_box.findData(self.current_encoding)
        if current_encoding_index >= 0:
            encoding_combo_box.setCurrentIndex(current_encoding_index)

        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel(self.translator.text("dialog.save_encoding")))
        encoding_layout.addWidget(encoding_combo_box)

        dialog_layout = dialog.layout()
        if isinstance(dialog_layout, QVBoxLayout):
            dialog_layout.addLayout(encoding_layout)
        elif dialog_layout is not None:
            dialog_layout.addWidget(QLabel(self.translator.text("dialog.save_encoding")))
            dialog_layout.addWidget(encoding_combo_box)

        if dialog.exec() != QFileDialog.DialogCode.Accepted:
            return None, self.current_encoding

        selected_files = dialog.selectedFiles()
        if not selected_files:
            return None, self.current_encoding

        return Path(selected_files[0]), str(encoding_combo_box.currentData())

    def _save_to_path(self, save_file_path: Path) -> None:
        save_data = self.editor.toPlainText()
        try:
            self.file_manager.save_text(save_file_path, save_data, self.current_encoding)
        except OSError as error:
            QMessageBox.critical(
                self,
                self.translator.text("dialog.save_failed.title"),
                str(error),
            )
            return

        self.current_save_file_path = save_file_path
        self.editor.document().setModified(False)
        self._update_window_title()

    def show_find_replace_dialog(self) -> None:
        if self.find_replace_dialog is None:
            self.find_replace_dialog = FindReplaceDialog(self.translator, self)
            self.find_replace_dialog.find_requested.connect(self.find_next)
            self.find_replace_dialog.find_previous_requested.connect(self.find_previous)
            self.find_replace_dialog.replace_requested.connect(self.replace_current)
            self.find_replace_dialog.replace_all_requested.connect(self.replace_all)
            self.find_replace_dialog.replace_marked_requested.connect(
                self.replace_marked_matches
            )
            self.find_replace_dialog.preview_requested.connect(self.preview_matches)
            self.find_replace_dialog.search_parameters_changed.connect(
                self.update_search_highlights
            )
            self.find_replace_dialog.regex_help_requested.connect(self.show_regex_help_dialog)

        selected_text = self.editor.textCursor().selectedText()
        if selected_text:
            cursor = self.editor.textCursor()
            self.search_scope = (
                self.editor.cursor_position_to_text_position(cursor.selectionStart()),
                self.editor.cursor_position_to_text_position(cursor.selectionEnd()),
            )
            self.find_replace_dialog.set_find_text(selected_text.replace("\u2029", "\n"))
        else:
            self.search_scope = None
        self.find_replace_dialog.clear_error()
        self.update_search_highlights(
            self.find_replace_dialog.find_text_edit.text(),
            self.find_replace_dialog.current_search_options(),
        )
        self.find_replace_dialog.show()
        self.find_replace_dialog.raise_()
        self.find_replace_dialog.activateWindow()

    def find_next(self, search_text: str, options: SearchOptions) -> None:
        if not search_text:
            self._set_search_error(self.translator.text("search.empty"))
            return

        cursor = self.editor.textCursor()
        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error(self.translator.text("search.select_before_find"))
            return

        source_text = scope_text if scope_text is not None else self.editor.toPlainText()
        cursor_position = cursor.selectionEnd() if cursor.hasSelection() else cursor.position()
        start_position = self.editor.cursor_position_to_text_position(cursor_position)
        start_position = min(max(start_position - scope_offset, 0), len(source_text))

        try:
            match = self.search_engine.find_next(
                source_text,
                search_text,
                start_position,
                options,
            )
        except RegexError as error:
            self._set_search_error(self.translator.text("search.invalid_regex", error=error))
            return

        if match is None:
            self._set_search_error(self.translator.text("search.no_matches"))
            return

        self._select_match(
            SearchMatch(
                match.start + scope_offset,
                match.end + scope_offset,
                match.text,
            )
        )
        self._set_search_status(self.translator.text("search.match_found"))

    def find_previous(self, search_text: str, options: SearchOptions) -> None:
        if not search_text:
            self._set_search_error(self.translator.text("search.empty"))
            return

        cursor = self.editor.textCursor()
        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error(self.translator.text("search.select_before_find"))
            return

        source_text = scope_text if scope_text is not None else self.editor.toPlainText()
        cursor_position = (
            cursor.selectionStart() if cursor.hasSelection() else cursor.position()
        )
        start_position = self.editor.cursor_position_to_text_position(cursor_position)
        start_position = min(max(start_position - scope_offset, 0), len(source_text))

        try:
            match = self.search_engine.find_previous(
                source_text,
                search_text,
                start_position,
                options,
            )
        except RegexError as error:
            self._set_search_error(
                self.translator.text("search.invalid_regex", error=error)
            )
            return

        if match is None:
            self._set_search_error(self.translator.text("search.no_matches"))
            return

        self._select_match(
            SearchMatch(
                match.start + scope_offset,
                match.end + scope_offset,
                match.text,
            )
        )
        self._set_search_status(self.translator.text("search.match_found"))

    def replace_current(
        self,
        search_text: str,
        replace_text: str,
        options: SearchOptions,
    ) -> None:
        if not search_text:
            self._set_search_error(self.translator.text("search.empty"))
            return

        cursor = self.editor.textCursor()
        source_text = self.editor.toPlainText()
        selected_match = SearchMatch(
            self.editor.cursor_position_to_text_position(cursor.selectionStart()),
            self.editor.cursor_position_to_text_position(cursor.selectionEnd()),
            cursor.selectedText().replace("\u2029", "\n"),
        )
        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error(self.translator.text("search.select_before_replace"))
            return
        if scope_text is not None and not self._match_is_inside_scope(
            selected_match,
            scope_offset,
            len(scope_text),
        ):
            self.find_next(search_text, options)
            return

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
            self._set_search_error(self.translator.text("search.invalid_regex", error=error))
            return

        if result.count == 0:
            self._set_search_error(self.translator.text("search.no_current_match"))
            return

        self._replace_document_text(result.text)
        self.update_search_highlights(search_text, options)
        replaced_end = selected_match.start + len(result.text) - (
            len(source_text) - selected_match.end
        )
        self._set_cursor_position(replaced_end)
        self._set_search_status(self.translator.text("search.replaced_one"))

    def replace_all(
        self,
        search_text: str,
        replace_text: str,
        options: SearchOptions,
    ) -> None:
        if not search_text:
            self._set_search_error(self.translator.text("search.empty"))
            return

        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error(self.translator.text("search.select_before_replace"))
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
            self._set_search_error(self.translator.text("search.invalid_regex", error=error))
            return

        if result.count == 0:
            self._set_search_error(self.translator.text("search.no_replacements"))
            return

        if scope_text is not None:
            scope_start = scope_offset
            scope_end = scope_offset + len(scope_text)
            result_text = source_text[:scope_start] + result.text + source_text[scope_end:]
            if options.selected_only:
                self.search_scope = (scope_start, scope_start + len(result.text))
        else:
            result_text = result.text

        self._replace_document_text(result_text)
        self.update_search_highlights(search_text, options)
        self._set_search_status(
            self.translator.text("search.replaced_many", count=result.count)
        )

    def replace_marked_matches(
        self,
        search_text: str,
        replace_text: str,
        options: SearchOptions,
    ) -> None:
        if not search_text:
            self._set_search_error(self.translator.text("search.empty"))
            return
        if not self.editor.search_matches:
            self._set_search_error(self.translator.text("search.no_replacements"))
            return

        result_text = self.editor.toPlainText()
        replacement_count = 0
        try:
            for match in sorted(
                self.editor.search_matches,
                key=lambda search_match: search_match.start,
                reverse=True,
            ):
                if match.start < 0 or match.end > len(result_text):
                    continue
                target_text = result_text[match.start : match.end]
                preview_result = self.search_engine.preview_replacement(
                    target_text,
                    search_text,
                    replace_text,
                    options,
                )
                if preview_result.count == 0:
                    continue
                result_text = (
                    result_text[: match.start]
                    + preview_result.text
                    + result_text[match.end :]
                )
                replacement_count += 1
        except RegexError as error:
            self._set_search_error(
                self.translator.text("search.invalid_regex", error=error)
            )
            return

        if replacement_count == 0:
            self._set_search_error(self.translator.text("search.no_replacements"))
            return

        self._replace_document_text(result_text)
        self.update_search_highlights(search_text, options)
        self._set_search_status(
            self.translator.text("search.replaced_many", count=replacement_count)
        )

    def update_search_highlights(
        self,
        search_text: str,
        options: SearchOptions,
    ) -> None:
        if not search_text:
            self.editor.clear_search_matches()
            return

        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self.editor.clear_search_matches()
            return

        source_text = scope_text if scope_text is not None else self.editor.toPlainText()
        try:
            matches = self.search_engine.find_all(source_text, search_text, options)
        except RegexError:
            self.editor.clear_search_matches()
            return

        self.editor.set_search_matches(
            [
                SearchMatch(
                    match.start + scope_offset,
                    match.end + scope_offset,
                    match.text,
                )
                for match in matches
            ]
        )

    def _refresh_search_highlights_from_dialog(self) -> None:
        if self.find_replace_dialog is None or not self.find_replace_dialog.isVisible():
            return
        self.update_search_highlights(
            self.find_replace_dialog.find_text_edit.text(),
            self.find_replace_dialog.current_search_options(),
        )

    def preview_matches(
        self,
        search_text: str,
        replace_text: str,
        options: SearchOptions,
    ) -> None:
        if self.find_replace_dialog is None:
            return
        if not search_text:
            self._set_search_error(self.translator.text("search.empty"))
            return

        scope_text, scope_offset = self._search_scope_text(options)
        if options.selected_only and scope_text is None:
            self._set_search_error(self.translator.text("search.select_before_find"))
            return

        source_text = scope_text if scope_text is not None else self.editor.toPlainText()
        try:
            matches = self.search_engine.find_all(source_text, search_text, options)
            rows = self._preview_rows(
                source_text,
                matches,
                search_text,
                replace_text,
                options,
                scope_offset,
            )
        except RegexError as error:
            self._set_search_error(self.translator.text("search.invalid_regex", error=error))
            return

        shown_count = len(rows)
        if not matches:
            summary = self.translator.text("search.preview.no_matches")
        elif shown_count < len(matches):
            summary = self.translator.text(
                "search.preview.limited",
                shown=shown_count,
                total=len(matches),
            )
        else:
            summary = self.translator.text("search.preview.matches", count=len(matches))

        self.find_replace_dialog.set_preview_rows(rows, summary)
        self._set_search_status(summary)

    def show_regex_help_dialog(self) -> None:
        if self.regex_help_dialog is None:
            regex_help_paths = {
                "EN_Ver.": self.resources_path / "regex_help_en.json",
                "JP_Ver.": self.resources_path / "regex_help_ja.json",
            }
            self.regex_help_dialog = RegexHelpDialog(
                regex_help_paths,
                self.translator,
                self,
            )
            self.regex_help_dialog.pattern_insert_requested.connect(
                self._insert_regex_pattern
            )

        self.regex_help_dialog.show()
        self.regex_help_dialog.raise_()
        self.regex_help_dialog.activateWindow()

    def show_user_help_dialog(self) -> None:
        if self.user_help_dialog is None:
            self.user_help_dialog = UserHelpDialog(self.translator, self)

        self.user_help_dialog.show()
        self.user_help_dialog.raise_()
        self.user_help_dialog.activateWindow()

    def _insert_regex_pattern(self, pattern: str) -> None:
        if self.find_replace_dialog is None:
            self.show_find_replace_dialog()
        if self.find_replace_dialog is not None:
            self.find_replace_dialog.insert_find_text(pattern)

    def _search_scope_text(self, options: SearchOptions) -> tuple[str | None, int]:
        if not options.selected_only and not options.visible_only:
            return None, 0

        source_text = self.editor.toPlainText()
        scope_bounds: tuple[int, int] | None = None

        if options.selected_only:
            selected_bounds = self._selected_search_bounds(len(source_text))
            if selected_bounds is None:
                return None, 0
            scope_bounds = selected_bounds

        if options.visible_only:
            visible_bounds = self._visible_search_bounds(len(source_text))
            if visible_bounds is None:
                return "", 0
            scope_bounds = (
                visible_bounds
                if scope_bounds is None
                else (
                    max(scope_bounds[0], visible_bounds[0]),
                    min(scope_bounds[1], visible_bounds[1]),
                )
            )

        if scope_bounds is None:
            return None, 0

        scope_start, scope_end = scope_bounds
        if scope_start >= scope_end:
            return "", scope_start
        return source_text[scope_start:scope_end], scope_start

    def _selected_search_bounds(self, source_length: int) -> tuple[int, int] | None:
        if self.search_scope is None:
            cursor = self.editor.textCursor()
            if not cursor.hasSelection():
                return None
            self.search_scope = (
                self.editor.cursor_position_to_text_position(cursor.selectionStart()),
                self.editor.cursor_position_to_text_position(cursor.selectionEnd()),
            )

        scope_start, scope_end = self.search_scope
        if scope_start >= scope_end or scope_end > source_length:
            return None
        return scope_start, scope_end

    def _visible_search_bounds(self, source_length: int) -> tuple[int, int] | None:
        first_block = self.editor.firstVisibleBlock()
        if not first_block.isValid():
            return None

        viewport_rect = self.editor.viewport().rect()
        block = first_block
        top = round(
            self.editor.blockBoundingGeometry(block)
            .translated(self.editor.contentOffset())
            .top()
        )
        bottom = top + round(self.editor.blockBoundingRect(block).height())
        visible_start: int | None = None
        visible_end: int | None = None

        while block.isValid() and top <= viewport_rect.bottom():
            if block.isVisible() and bottom >= viewport_rect.top():
                if visible_start is None:
                    visible_start = self.editor.cursor_position_to_text_position(
                        block.position()
                    )
                visible_end = min(
                    self.editor.cursor_position_to_text_position(
                        block.position() + block.length()
                    ),
                    source_length,
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.editor.blockBoundingRect(block).height())

        if visible_start is None or visible_end is None:
            return None
        return visible_start, visible_end

    def _match_is_inside_scope(
        self,
        match: SearchMatch,
        scope_offset: int,
        scope_length: int,
    ) -> bool:
        return scope_offset <= match.start and match.end <= scope_offset + scope_length

    def _preview_rows(
        self,
        source_text: str,
        matches: list[SearchMatch],
        search_text: str,
        replace_text: str,
        options: SearchOptions,
        scope_offset: int,
    ) -> list[tuple[int, str, str]]:
        rows: list[tuple[int, str, str]] = []
        for match in matches[:200]:
            absolute_start = scope_offset + match.start
            line_number = self.editor.toPlainText().count("\n", 0, absolute_start) + 1
            before_text = self._line_context(source_text, match)
            preview_result = self.search_engine.preview_replacement(
                match.text,
                search_text,
                replace_text,
                options,
            )
            after_text = self._replacement_context(
                source_text,
                match,
                preview_result.text if preview_result.count else match.text,
            )
            rows.append(
                (
                    line_number,
                    before_text,
                    after_text,
                )
            )
        return rows

    def _line_context(self, source_text: str, match: SearchMatch) -> str:
        line_start = source_text.rfind("\n", 0, match.start) + 1
        line_end = source_text.find("\n", match.end)
        if line_end == -1:
            line_end = len(source_text)
        prefix = source_text[line_start : match.start]
        suffix = source_text[match.end : line_end]
        context_text = f"{prefix}{match.text}{suffix}"
        return self._visible_preview_text(context_text)

    def _replacement_context(
        self,
        source_text: str,
        match: SearchMatch,
        replacement_text: str,
    ) -> str:
        line_start = source_text.rfind("\n", 0, match.start) + 1
        line_end = source_text.find("\n", match.end)
        if line_end == -1:
            line_end = len(source_text)
        prefix = source_text[line_start : match.start]
        suffix = source_text[match.end : line_end]
        return self._visible_preview_text(f"{prefix}{replacement_text}{suffix}")

    def _visible_preview_text(self, text: str) -> str:
        visible_text = text.replace("\t", "\\t").replace("\n", "\\n")
        if len(visible_text) > 140:
            return f"{visible_text[:137]}..."
        return visible_text

    def _replace_document_text(self, text: str) -> None:
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(text)
        cursor.endEditBlock()

    def _select_match(self, match: SearchMatch) -> None:
        cursor = self.editor.textCursor()
        cursor.setPosition(self.editor.text_position_to_cursor_position(match.start))
        cursor.setPosition(
            self.editor.text_position_to_cursor_position(match.end),
            QTextCursor.MoveMode.KeepAnchor,
        )
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _set_cursor_position(self, position: int) -> None:
        cursor = self.editor.textCursor()
        cursor.setPosition(self.editor.text_position_to_cursor_position(position))
        self.editor.setTextCursor(cursor)

    def _set_search_error(self, message: str) -> None:
        if self.find_replace_dialog is not None:
            self.find_replace_dialog.set_error(message)
        self.statusBar().showMessage(message)

    def _set_search_status(self, message: str) -> None:
        if self.find_replace_dialog is not None:
            self.find_replace_dialog.clear_error()
        self.statusBar().showMessage(message)

    def _set_encoding_status(self) -> None:
        self.statusBar().showMessage(
            self.translator.text("status.encoding", encoding=self.current_encoding)
        )


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
