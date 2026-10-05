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
- Tag insertion assistance for HTML, Markdown, and WordPress HTML.
- WordPress-oriented paragraph splitting and snippet insertion helpers.
- Grammar Check for lightweight HTML and WordPress block safety checks.
- Grammar Check result list copy button.
- Optional pre-save HTML / WordPress typo check.

## HTML / WordPress Grammar Check

Grammar Check is a lightweight paste-safety linter. It is not a full browser or
WordPress parser, but it is designed to catch common document-breaking mistakes
before pasting or saving article HTML.

- Detects unknown HTML tags and suspicious HTML attribute typos.
- Warns when a known HTML attribute appears on an unusual tag, such as
  `href` on `<p>` or `src` on `<a>`.
- Detects unknown WordPress core block names.
- Detects invalid JSON inside WordPress block comment `{}` parameters.
- Warns about unsupported or unexpected `{}` parameters using the bundled
  WordPress core block attribute dictionary.
- Checks WordPress block start / end mismatches, missing closing comments, and
  repeated non-nestable blocks such as `wp:list-item`.
- Checks whether HTML tags are complete inside each WordPress block.
- Checks pure HTML files as a whole when no WordPress block comments are used.
- Detects common structural problems such as missing `</div>`, reversed closing
  order, and unclosed inline tags before `</p>`.
- Suppresses likely cascade noise after known representative errors such as
  separator blocks contaminated with stray `<code>` tags.
- Keeps escaped code examples inside `<code>...</code>` acceptable when they are
  display text rather than executable HTML.

## Tag Snippets

- Tag candidates are managed separately in `dictionaries/html_dict.json`,
  `dictionaries/markdown_dict.json`, and
  `dictionaries/wordpress_html_dict.json`.
- Insert tags or snippets at the current cursor position from the editor context menu.
- Snippet insertion supports HTML, Markdown, and WordPress HTML article helpers.
- WordPress helpers are intentionally conservative and preserve article block
  boundaries.

## Planned Direction

- Add an optional Japanese typo / style-variation check after a dictionary and
  settings switch are prepared.
- Keep the bundled WordPress core block / attribute dictionary aligned with
  official references and real examples.

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
