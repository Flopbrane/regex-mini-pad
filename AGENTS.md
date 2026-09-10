# AGENTS.md

## Project overview

This project is `mini_editor_project`.

The goal is to create a lightweight portable text editor for Windows 11.

The editor should be similar to a small subset of Mery.

Main requirements:

- No installer required
- Do not use the Windows Registry
- No administrator privileges required
- Portable execution
- Settings should be stored in local files
- Offline operation
- Python 3.12
- GUI framework: PySide6


## Python environment

Use the following Python interpreter:

D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe

Do not use another Python interpreter unless explicitly instructed.

When running commands, prefer:

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" <command>

Examples:

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" main.py

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pylint <target_file>

## Project structure

Expected structure:

mini_editor_project/
├─ main.py
├─ editor/
│  ├─ text_editor.py
│  ├─ line_number_area.py
│  ├─ ruler.py
│  └─ rectangular_selection.py
├─ dialogs/
│  ├─ find_replace_dialog.py
│  └─ regex_help_dialog.py
├─ search/
│  └─ search_engine.py
├─ fileio/
│  └─ file_manager.py
├─ settings/
│  └─ settings_manager.py
├─ resources/
│  ├─ regex_help_en.json
│  └─ regex_help_ja.json
└─ tests/

Do not place all functionality in `main.py`.

Keep each responsibility separated into appropriate modules.


## Coding rules

- Target Python version: Python 3.12
- Use PySide6
- Use type hints where practical
- Prefer pathlib.Path for file paths
- Use descriptive variable and function names
- Keep functions and methods reasonably small
- Avoid unnecessary global variables
- Avoid unnecessary third-party dependencies
- Use Python standard library when sufficient
- Use `re` for regular expressions
- Do not add dependencies without explaining why


## File path naming

Use the following terminology in code:

- `load_file_path` for input file paths
- `save_file_path` for output file paths
- `load_data` for loaded file data
- `save_data` for data to be saved

Avoid generic names such as `file_path` when the direction is known.


## GUI requirements

The application should eventually support:

### File

- New
- Open
- Save
- Save As
- Exit

### Edit

- Undo
- Redo
- Select
- Rectangular selection
- Copy rectangular selection

### Search

- Find
- Replace

The Find/Replace dialog should support:

- Find text
- Replace text
- Find
- Replace
- Replace All
- Close
- Case-sensitive search
- Regular expression search
- Whole-word search
- Search only selected text
- Regular expression help
- Regular expression insertion popup

### View

- Ruler
- Line numbers
- Total character count
- Spaces
- Newlines
- Tabs
- Word wrap


## Regular expression behavior

Use Python's standard `re` module.

Regular expression input must not modify the source text unless the user explicitly performs a replace operation.

Invalid regular expressions must be caught and reported to the user without crashing the application.

Do not silently alter regular expression patterns entered by the user.


## Portable application requirements

Do not use:

- Windows Registry
- Administrator-only locations
- System-wide configuration
- External online services

Application settings should be saved locally, for example:

settings.ini

or:

settings.json


## Safety rules for file saving

Avoid unnecessary risk of file corruption.

When possible:

1. Write new data to a temporary file.
2. Confirm the write succeeded.
3. Replace the original file safely.

Do not silently delete user files.

Do not overwrite files unless the requested operation requires it.


## Development policy

Implement the project incrementally.

Preferred order:

1. Main window
2. Basic text editor
3. File open/save
4. Undo/Redo
5. Line numbers
6. Find
7. Replace
8. Regular expression support
9. Search options
10. Regex insertion popup
11. Regex help
12. Character count
13. Word wrap
14. Space/TAB/newline display
15. Ruler
16. Rectangular selection

Do not implement multiple large features at once unless explicitly requested.


## Before editing code

Before making changes:

1. Inspect the relevant files.
2. Understand the existing implementation.
3. Explain briefly what files will be changed.
4. Make the smallest reasonable change.

Do not rewrite unrelated working code.


## Validation

After changes, run appropriate checks.

Preferred commands:

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright

Run pytest when tests exist:

"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest

If a check fails, report the reason instead of hiding the failure.


## Communication

When reporting work:

- Explain what changed
- List changed files
- Mention validation results
- Mention remaining issues
- Do not claim success if tests or checks were not run
