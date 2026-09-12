# SCRIPT_STEP.md

## Development Steps

This file records the planned build order for `mini_editor_project`.

## Completed

1. Main window
   - PySide6 `QMainWindow` entry point.
   - File, Edit, Search, View, and Language menus.

2. Basic text editor
   - `QPlainTextEdit` based editor.
   - Monospace font and basic tab width.

3. File open/save
   - New, Open, Save, Save As, and Exit.
   - Safe save through a temporary file.
   - Local settings file only.

4. Undo/Redo
   - Standard editor undo and redo actions.

5. Line numbers
   - Left-side line number area.
   - View menu toggle.

6. Find and Replace
   - Modeless Find / Replace dialog.
   - Find, Replace, Replace All, and Close.

7. Regular expression support
   - Python `re` based search and replace.
   - Regex replacement groups such as `\1` and `\2`.
   - Invalid regex handling without modifying source text.

8. Search options
   - Case-sensitive search.
   - Whole-word search.
   - Search only selected text.
   - Search only visible text.

9. Regex assistance
   - Regex insertion popup.
   - Regex lint warnings.
   - English and Japanese regex help.
   - Practical examples and replacement recipes.

10. App localization
    - English and Japanese application UI text.
    - Language menu.
    - Local language setting.

11. Encoding support
    - Open with Encoding.
    - Reload.
    - Reload with Encoding.
    - Save As encoding selector.
    - Preserve selected encoding when saving.

## Next Recommended Steps

1. Regex preview
   - Show match count before replacement.
   - Show target text snippets.
   - Make it clear what will be changed before Replace All.

2. Match highlighting
   - Highlight all current matches in the editor.
   - Keep current selected match visually distinct.
   - Show match markers beside the vertical scroll area.

3. Find Previous
   - Add previous-match navigation.
   - Keep wrap-around behavior predictable.

4. Replacement preview
   - Show before/after rows for regex replacement.
   - Allow users to confirm large replacements.

5. Newline handling
   - Detect CRLF / LF / CR.
   - Preserve newline style on save.
   - Add newline conversion if needed.

6. Character information
   - Total character count.
   - Space count.
   - Tab count.
   - Newline count.

7. Whitespace display
   - Visible spaces.
   - Visible tabs.
   - Visible newlines.

8. Ruler
   - Column ruler above the editor.
   - Toggle from View menu.

9. Rectangular selection
   - Rectangular selection mode.
   - Copy rectangular selection.

10. Distribution
    - Review PyInstaller spec.
    - Verify resources load next to the executable.
    - Confirm portable folder behavior.

11. Tag insertion assistance
    - Add `html_dict.py`, `md_dict.py`, and `wphtml_dict.py`.
    - Show file-format-specific tag snippets from the editor context menu.
    - Insert the selected tag or snippet at the current cursor position.
    - Support mouse selection and keyboard selection with arrow keys plus Enter.
    - Consider automatic snippet set switching by extension, such as `.html`, `.md`, and `.wp.html`.

## Validation Commands

Use the project virtual environment:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

## Project Principles

- Keep the app portable.
- Do not use the Windows Registry.
- Do not require administrator privileges.
- Store settings locally.
- Keep regex usable for non-programmers.
- Do not modify text during search.
- Modify text only when the user explicitly runs Replace or Replace All.
- Keep English and Japanese help aligned in meaning.
