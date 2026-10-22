# Mini Editor

Mini Editor is a lightweight portable text editor for Windows 11.

The project focuses on practical regular expression search and replacement without requiring an installer, administrator privileges, registry changes, or online services.

## Search exclusions

The Find / Replace dialog has an **Exclude** field. Search results that overlap
an exclusion match are skipped by Find, Previous, highlights, previews, Replace,
Replace All, and Replace Marked. Leave it empty to disable exclusions.

With regular expressions enabled, search for `\n` and set Exclude to
`<br><br>\n|>\n` to skip newlines immediately after those tags. Use `|` for
alternatives; a leading `-` has no special meaning. For CRLF text, use `\r?\n`
in both patterns. Without regex mode, Exclude is one literal string. Regex and
case sensitivity follow the search checkboxes; whole-word matching applies only
to the search pattern. Exclusions protect matching characters, rather than entire
lines; zero-width exclusion matches protect no characters. For selected/visible
searches, exclusion patterns are evaluated inside that search scope. Inputs stay
in the dialog for the current session and are not saved across restarts.

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
- The editor context menu can insert `background-color: ;` and offer nine
  recommended WordPress background colors with swatches; press `Esc` to close
  the list and type a custom CSS color value.
- `color: ;` offers the same seven colors as the inline text-color shortcuts.
  The editor context menu also has a Text Color submenu, while `Ctrl+Alt+1`
  through `Ctrl+Alt+7` remain direct color shortcuts for selected text.
- Inline HTML wrap shortcuts for selected text, including `<strong>`, `<u>`,
  and seven colored `<span>` text variants.
- WordPress-oriented paragraph splitting and snippet insertion helpers.
- Selected Markdown tables and lists can be converted by the embedded
  `wp_conv_core` module and replaced with WordPress block HTML.
- Grammar Check for lightweight CSS, HTML, and WordPress block safety checks.
- Grammar Check result list copy button.
- Per-tab Grammar Check result display for multi-file editing.
- Optional pre-save CSS, HTML, and WordPress typo check.
- A modeless HTML / CSS / WordPress reference window that can remain beside the
  editable main window, with separate tables generated from the bundled lint schemas.

## CSS / HTML / WordPress Grammar Check

Grammar Check is a lightweight paste-safety linter. It is not a full browser or
WordPress parser, but it is designed to catch common document-breaking mistakes
before pasting or saving article HTML.

- Detects unknown HTML tags and suspicious HTML attribute typos.
- Uses the same CSS dictionary to check HTML `style` attributes, `<style>`
  elements, and standalone `.css` documents.
- Detects missing or extra braces, unclosed comments, quotes and parentheses,
  full-width punctuation, missing colons, and likely missing semicolons.
- Detects unknown or misspelled CSS properties and units, invalid registered
  keywords, malformed hexadecimal colors, missing units, duplicate properties,
  and selected numeric range/type mistakes.
- Warns when a known HTML attribute appears on an unusual tag, such as
  `href` on `<p>` or `src` on `<a>`.
- Detects unknown WordPress core block names.
- Detects invalid JSON inside WordPress block comment `{}` parameters.
- Warns about unsupported or unexpected `{}` parameters using the bundled
  WordPress core block attribute dictionary.
- Warns about selected WordPress block attribute type / value mistakes, such as
  string `level` values, string booleans, and misspelled paragraph alignment.
- Checks WordPress block start / end mismatches, missing closing comments, and
  repeated non-nestable blocks such as `wp:list-item`.
- Checks whether HTML tags are complete inside each WordPress block.
- Checks pure HTML files as a whole when no WordPress block comments are used.
- Also checks HTML outside WordPress blocks in mixed documents.
- Reports extra inline closing tags, mismatched `h1` through `h6` pairs,
  nested paragraphs/links, block elements inside paragraphs, and list items
  without a direct `ul`, `ol`, or `menu` parent.
- Accepts self-closing WordPress comments such as `<!-- wp:latest-posts /-->`.
  They do not open a block or affect subsequent pair counts.
- Checks direct `list-item` / `list` and `column` / `columns` relationships,
  allowed children of lists/columns, and child blocks inside paragraphs.
- Requires one root `p` in a paragraph block and one root heading in a heading
  block; comments and escaped tag examples do not count as elements.
- Compares selected paragraph typography/color styles and declared color/size
  preset classes with block-comment attributes. Inline child formatting is
  checked separately. Theme CSS, arbitrary custom classes, spacing/borders,
  and the complete Gutenberg save output are outside this consistency check.
- Reuses the HTML tag inventory for whole-document and block-boundary checks,
  and displays identical findings on the same line once.
- Detects common structural problems such as missing `</div>`, reversed closing
  order, and unclosed inline tags before `</p>`.
- Suppresses likely cascade noise after known representative errors such as
  separator blocks contaminated with stray `<code>` tags.
- Keeps escaped code examples inside `<code>...</code>` acceptable when they are
  display text rather than executable HTML.
- Keeps Grammar Check results associated with each editor tab. When switching
  tabs, the result dialog shows the selected tab's latest valid result, and the
  dialog title includes the target document name.
- Removes the temporary Grammar Check result folder when the last RegexPad
  window closes.

## Tag Snippets

- Tag candidates are managed separately in `dictionaries/html_dict.json`,
  `dictionaries/markdown_dict.json`, and
  `dictionaries/wordpress_html_dict.json`.
- Insert tags or snippets at the current cursor position from the editor context menu.
- Snippet insertion supports HTML, Markdown, and WordPress HTML article helpers.
- Common inline HTML wrappers are also available from shortcuts: `Ctrl+B` for
  `<strong>`, `Ctrl+U` for `<u>`, `Ctrl+Alt+1` through `Ctrl+Alt+7` for
  colored `<span>` text, and `Ctrl+Alt+R` as a red-text alias.
- Text and background swatch names and CSS values are loaded from the editable
  `color_presets.json` beside the application. Text-color shortcut assignments
  are stored there too. Restart RegexPad after editing this file.
- WordPress helpers are intentionally conservative and preserve article block
  boundaries.
- The editor context menu's Paragraph Split submenu can convert selected
  Markdown tables and lists through
  the embedded `wp_conv_core` module, so no external converter path or
  environment variable is required.
- `List to Framed Block` converts a selected Markdown list or existing
  WordPress list block to one Custom HTML (`wp:html`) frame. It emits visible
  `・` or numbered text instead of `ul` / `ol` markers, so the result remains
  readable when a WordPress theme hides list markers.

## Editable Color Presets

- Development runs use the project-root `color_presets.json`.
- A packaged EXE creates `color_presets.json` beside `regex-pad.exe` from the
  bundled default when the editable file is missing.
- Edit `text_colors` for `color: ;`, the Text Color submenu, and inline color
  shortcuts. Edit `background_colors` for `background-color: ;`.
- Each entry has a stable `id`, Japanese and English `name` values, and a CSS
  `value`. Text-color entries may also define a `shortcuts` array.
- Invalid editable JSON is left untouched; RegexPad falls back to the bundled
  default for that launch.

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
