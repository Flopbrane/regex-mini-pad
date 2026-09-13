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
    - Continue from `Step11-section1`.
    - Refine tag insertion menus and dictionary-backed snippets.
    - Show file-format-specific tag snippets from the editor context menu.
    - Support mouse selection and keyboard selection with arrow keys plus Enter.
    - Consider automatic snippet set switching by extension, such as `.html`, `.md`, and `.wp.html`.

## Step11-section1 Tag Insertion Entry

Completed:

- Added the `Edit` menu entry `Insert Tag` / `タグ挿入`.
- Added tag insertion groups:
  - HTML
  - Markdown
  - WordPress HTML
- Added insertion templates that support:
  - `{selection}` for wrapping selected text.
  - `{cursor}` for placing the cursor after insertion.
- Added parameter hints through menu action `statusTip` and `toolTip`.
- Moved snippet data to local JSON dictionaries:
  - `dictionaries/html_dict.json`
  - `dictionaries/markdown_dict.json`
  - `dictionaries/wordpress_html_dict.json`
- Added common Markdown snippets:
  - headings, bold, italic, links, images, inline code, fenced code blocks, quote, lists, horizontal rule.
  - language-specific fenced code blocks for Python, HTML, CSS, JavaScript, JSON, PowerShell, Bash, and SQL.
- Added commonly used WordPress HTML snippets:
  - paragraph, headings, list, quote, code, preformatted, custom HTML code box, separator, spacer, and button.
  - `wp:code` uses `<pre class="wp-block-code"><code>...</code></pre>`.
  - `wp:html` custom code box includes the styled `<pre class="wp-block-code"><code>...</code></pre>` wrapper.
- Added common HTML snippets:
  - paragraph, headings, links, image, figure, div, span, lists, inline code, and pre/code block.
  - HTML hints describe common parameters such as `href`, `src`, `alt`, `class`, `id`, `data-*`, `target`, `rel`, `start`, `reversed`, and `type`.
- Added right-click tag insertion:
  - The editor context menu now includes `タグ挿入`.
  - It reuses the same snippet groups and insertion behavior as the menu bar.
- Added menu hierarchy refinement:
  - HTML is split into Basic, Link / Image, Layout, Lists, and Code.
  - Markdown is split into Text, Link / Image, Code, Lists, and Utility.
  - WordPress HTML is split into Text, Code, and Layout.
- Added file extension based ordering:
  - `.md` and `.markdown` prefer Markdown first.
  - `.html` and `.htm` prefer HTML first.
  - `.wp.html` prefers WordPress HTML first.
  - All snippet groups remain available even when one group is prioritized.
- Added keyboard tag insertion picker:
  - `Ctrl+Shift+T` opens the tag insertion picker.
  - The picker supports filtering snippets by text.
  - `Tab` or arrow keys move from the filter field to the candidate list.
  - `Enter` inserts the selected snippet.
- Confirmed Undo/Redo behavior:
  - Existing `Ctrl+Z` and `Ctrl+Y` shortcuts remain available.
  - Inserted snippets can be undone and redone as a single edit operation.

Follow-up candidates:

1. Dictionary JSON validation
   - Validate required keys: `label_key`, `hint_key`, and `template`.
   - Detect missing translation keys.
   - Detect missing or duplicated `{cursor}` when cursor placement is expected.
   - Detect unknown placeholders.
   - Detect empty labels, hints, or templates.

2. Richer parameter hints
   - Consider adding structured `parameters` arrays to JSON.
   - Generate hover text from structured parameter definitions.
   - This can later support linting or inline assistance for tag attributes.

3. Snippet search / keyboard picker
   - Add a small searchable popup for users who prefer typing tag names.
   - Support arrow keys plus Enter.
   - Keep menu insertion and popup insertion backed by the same JSON data.

4. Attribute-aware insertion
   - For common attributes such as `class`, `id`, `href`, `src`, and `alt`, consider optional prompt or placeholder navigation.
   - Keep the current direct insertion as the fast path.

## Step11-section2 Dictionary Validation

Completed:

- Added dictionary validation while loading tag snippet JSON.
- Required fields are checked:
  - `label_key`
  - `hint_key`
  - `template`
- Empty `label_key`, `hint_key`, and `template` values are rejected.
- Duplicated `{cursor}` placeholders are rejected.
- Unknown `{...}` placeholders are rejected.
  - Valid placeholders are `{selection}` and `{cursor}`.
- Added tests that confirm all tag snippet `label_key` and `hint_key` values exist in both:
  - `resources/app_text_en.json`
  - `resources/app_text_ja.json`

Follow-up candidates:

1. Structured parameters
   - Add optional `parameters` arrays to snippet JSON.
   - Store names such as `href`, `src`, `alt`, `class`, `id`, and `rel`.
   - Generate hint text from structured parameter metadata.

2. Duplicate snippet key detection
   - Detect duplicate `label_key` values within one dictionary.
   - Consider detecting duplicates across all dictionaries if cross-group uniqueness becomes important.

3. JSON schema documentation
   - Add a short dictionary format note to README or a dedicated `dictionaries/README.md`.
   - Include examples for simple wrapping, cursor placement, and code-block snippets.

## Step11-section3 User Help Entry

Completed:

- Added an application help dialog.
- Added the `Help` / `ヘルプ` menu.
- Added the `Help...` / `使い方...` menu action.
- Added the `F1` shortcut for opening help.
- Help content covers:
  - File operations.
  - Undo / Redo.
  - Search / Replace.
  - Regex Help.
  - Tag insertion.
  - View options.
  - Language switching.
- Help content follows the current application display language.

Follow-up candidates:

1. Expand help topics as features grow
   - Character count.
   - Whitespace display.
   - Ruler.
   - Rectangular selection.

2. Add dedicated help pages
   - Basic editing.
   - Search and replace.
   - Regular expressions.
   - Tag insertion.

3. Add in-dialog navigation
   - Topic list on the left.
   - Search inside help text.
   - Links from feature dialogs to the relevant help topic.

## Step11-section4 User Help Navigation

Completed:

- Split the help dialog into dedicated topic pages.
- Added a topic list on the left side of the help dialog.
- Added separate help topics for:
  - File.
  - Edit.
  - Search / Replace.
  - Tag Insertion.
  - View.
  - Language.
- Preserved language switching for the currently open help dialog.
- Added View help text for the existing status bar character count.

Follow-up candidates:

1. Search inside help
   - Add a small filter field for help topics.
   - Highlight or jump to matching help text.

2. Direct links from feature dialogs
   - Open Search / Replace help from the Find / Replace dialog.
   - Open Tag Insertion help from the tag picker.

3. Externalize help content
   - Move help content from Python constants to JSON or Markdown files.
   - Keep Japanese and English help structures aligned by tests.

## Step11-section5 Search Navigation And Marked Replace

Completed:

- Added explicit previous / next search buttons beside the search text field.
  - Previous uses the `↑` button.
  - Next uses the `↓` button.
- Added previous-match navigation.
  - Uses the same search options as normal search.
  - Wraps around when there is no previous match before the cursor.
- Added `Replace Marked` / `マーカー部分を全て置換`.
  - Replaces the currently highlighted search marker ranges.
  - Applies replacements from the end of the document to avoid position shifts.
  - Supports regex replacement groups.
- Updated help text for search navigation and marked replacement.

Follow-up candidates:

1. Button icon polish
   - Consider compact icon-only styling for the arrow buttons.
   - Keep tooltips for clarity.

2. Marker replacement preview
   - Reuse the preview table to show only currently marked ranges.
   - Make the difference between all matches and marked matches clearer.

## Step11-section6 Tabbed Documents

Completed:

- Converted the editor surface to a tabbed document interface.
- `New` now creates a new untitled tab without discarding existing text.
- Untitled tab names use the first line of the document as a temporary title.
  - Empty tabs still use `Untitled` / `無題`.
- Added tab right-click commands:
  - `Close` / `閉じる`.
  - `Duplicate This Tab` / `このタブの複製`.
  - `Open in New Window` / `新規ウィンドウで開く`.
- Closing an unsaved tab asks whether to save, discard, or cancel.
- Duplicating a tab copies the current text into a new unsaved tab.
- Moving a tab to a new window transfers the text and file state, then removes it from the source window.
- Each window now has a UUID-based `window_id`.
- Parent windows keep child windows in `child_windows` by `window_id`.
- Updated the user help text with basic tab behavior.

Follow-up candidates:

1. Multi-tab autosave
   - Extend the current single unsaved backup to store multiple tabs.
   - Restore all unsaved tabs on launch.

2. Tab UI polish
   - Add close buttons on tabs after behavior stabilizes.
   - Add keyboard shortcuts for next / previous tab.
   - Consider middle-click close.

## Validation Commands

Use the project virtual environment:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

## Project Principles

- ~~Keep the app portable.~~
- Do not use the Windows Registry.
- Do not require administrator privileges.
- Store settings locally.
- Keep regex usable for non-programmers.
- Do not modify text during search.
- Modify text only when the user explicitly runs Replace or Replace All.
- Keep English and Japanese help aligned in meaning.
