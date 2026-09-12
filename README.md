# Mini Editor

Mini Editor is a lightweight portable text editor for Windows 11.

The project focuses on practical regular expression search and replacement without requiring an installer, administrator privileges, registry changes, or online services.

## Goals

- Portable folder-based execution.
- Local settings only.
- Python 3.12.
- PySide6 GUI.
- Strong regex search and replacement support.
- English and Japanese UI text.
- English and Japanese regex help.

## Current Features

- New, Open, Save, Save As, and Exit.
- Open with Encoding.
- Reload and Reload with Encoding.
- Save As encoding selector.
- Undo, Redo, and Select All.
- Line numbers.
- Word wrap toggle.
- Find / Replace dialog.
- Regex search and replacement.
- Case-sensitive search.
- Whole-word search.
- Search only selected text.
- Regex insertion popup.
- Regex lint warnings.
- Regex help with examples and replacement recipes.

## Planned Direction

- Tag insertion assistance for HTML, Markdown, and WordPress HTML.
- Manage candidates separately in `html_dict.py`, `md_dict.py`, and `wphtml_dict.py`.
- Insert tags or snippets at the current cursor position from the editor context menu.
- Consider both mouse selection and keyboard selection with arrow keys plus Enter.
- Consider automatic snippet switching by extension, such as `.html`, `.md`, and `.wp.html`.

## Supported Encodings

- UTF-8
- UTF-8 with BOM
- CP932 / Shift_JIS
- Shift_JIS
- EUC-JP
- UTF-16
- UTF-16 LE
- UTF-16 BE

When a file is opened or reloaded with a selected encoding, Save uses that encoding until another encoding is selected.

## Run

Use the project virtual environment:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" main.py
```

## Validate

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

## Project Structure

```text
mini_editor_project/
├─ main.py
├─ dialogs/
├─ editor/
├─ fileio/
├─ localization/
├─ resources/
├─ search/
├─ settings/
└─ tests/
```

## Notes

The regex engine uses Python's standard `re` module.

Search never modifies the document. Text is modified only when Replace or Replace All is executed.

Invalid regular expressions are reported without changing the document.
