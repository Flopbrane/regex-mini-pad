# SCRIPT_STEP.md

## Python environment

D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe

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

## Step11-section7 Options Window Entry

Completed:

- Added the `Options` / `設定` menu.
- Added the `Options...` / `オプション...` action.
- Added the `Ctrl+,` shortcut for opening the options window.
- Built the options window as a tabbed dialog.
- Grouped future and current settings by topic:
  - General
  - View
  - Tag Insert
  - Backup
  - Font
  - Search
- Connected the currently usable options:
  - Default WordPress HTML mode.
  - Hover hint visibility.
  - Backup folder.
  - Editor font family.
  - Editor font size.
- Kept not-yet-implemented options visible as disabled placeholders so the planned categories are clear.
- The backup folder option uses local files only.
- The application must not change environment variables from options.
- Settings that might otherwise require Registry usage should be stored in a local settings file instead.

Follow-up candidates:

1. Complete visible whitespace rendering
   - Draw half-width spaces.
   - Draw tabs.
   - Draw newline marks.
   - Use the saved `visible_spaces_enabled`, `visible_tabs_enabled`, and `visible_newlines_enabled` flags.

2. Backup detail options
   - Backup interval.
   - Backup retention count.
   - Backup retention days.
   - Multi-tab backup restore behavior.

3. Search option expansion
   - Regex lint display behavior.
   - Consider free color selection later if presets are not enough.

## Step11-section8 View And Search Options

Completed:

- Moved existing View toggles into the Options window:
  - Line numbers.
  - Word wrap.
- Added `Ruler` / `文字数ルーラー` as both:
  - A View menu toggle.
  - An Options > View setting.
- Implemented the lightweight character ruler:
  - `editor/ruler.py` now draws character-position ticks.
  - It follows the current editor font.
  - It follows horizontal scroll position.
  - It aligns with the line-number margin.
- Added Search color options:
  - Search marker color.
  - Current match marker color.
  - Preset colors are used first to keep the setting simple and stable.
- Stored the new settings in local `settings.json` through `EditorSettings`:
  - `ruler_enabled`
  - `search_marker_color`
  - `current_match_marker_color`
- Applied View and Search settings to all open tabs.
- Implemented visible whitespace rendering:
  - Options > View now has separate checkboxes for spaces, TABs, and newlines.
  - `EditorSettings` persists:
    - `visible_spaces_enabled`
    - `visible_tabs_enabled`
    - `visible_newlines_enabled`
  - `TextEditor.set_visible_whitespace_options()` stores those flags and requests a viewport update.
  - `TextEditor.paintEvent()` overlays visible marks without changing document text.
  - Half-width spaces use `␣`.
  - Full-width spaces use `□`.
  - TABs use `→`.
  - Newlines use `↵`.
  - Only visible blocks are painted.
- Fixed the main-window action initialization so Undo / Redo / Select All call the current editor lazily instead of reading `self.editor` before the first tab exists.
- Updated Japanese and English Options text for the new visible whitespace checkboxes.
- Updated tests for the new Options values, saved settings, visible whitespace mark detection, and the offscreen paint path.
- Moved the character ruler into each editor tab:
  - The ruler now appears below the tab bar and above the editor area.
  - Each tab owns its own `EditorTab` container with a `Ruler` and `TextEditor`.
  - Existing tab operations still address the underlying `TextEditor`.
- Added fixed-column wrap support:
  - Options > View now has `Wrap at ruler column` / `設定文字数で折り返す`.
  - Clicking the ruler stores the selected wrap column.
  - When fixed-column wrap is enabled, the editor wraps at the selected ruler column.
  - A thin green guide line marks the selected wrap column.
  - The source text is not modified; wrapping is display-only.
  - `EditorSettings` persists:
    - `fixed_column_wrap_enabled`
    - `fixed_column_wrap_column`
- Added `editor/editor_tab.py` for the per-tab ruler/editor layout.
- Updated tests for fixed-column wrap settings and editor behavior.
- Continued Options wiring:
  - General > Startup restore is now an editable checkbox.
  - Font > TAB width is now an editable spin box.
  - View > Wrap column is now an editable spin box.
  - TAB width is applied to existing and newly created tabs.
  - Startup restore controls whether the unsaved-backup restore prompt appears on launch.
  - The wrap-column spin box and ruler-click behavior share the same saved column value.
  - `EditorSettings` persists:
    - `startup_restore_enabled`
    - `tab_width`
- Updated tests for startup-restore opt-out, TAB width application, saved settings, and Options values.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
```

Latest result:

```text
pytest: 113 passed
ruff: All checks passed
pyright: 0 errors, 0 warnings, 0 informations
JSON validation: app_text_en.json OK, app_text_ja.json OK
```

Follow-up candidates:

1. Visible whitespace polish
   - Tune marker color if it feels too strong or too faint.
   - Review behavior with very large files.
   - Review behavior with wrapped lines and proportional fonts.

2. Ruler polish
   - Review visual feel of the green wrap-column guide.
   - Review behavior with narrow windows and very large wrap columns.

3. Search / display interaction checks
   - Confirm visible whitespace markers remain readable when search highlights are active.
   - Consider user-facing presets if more display colors are added later.

4. Backup rotation
   - The retention count / days values are now stored in Options.
   - The current unsaved-backup implementation still uses a single backup file.
   - Add pruning behavior when rotating backup files are introduced.

## Step11-section9 General, Search, Backup, And Dictionary Options

Implementation order:

1. General > Display language
2. General > Default encoding
3. General > Newline code
4. Search > Regex lint
5. Backup > Retention count / retention days
6. Tag Insert > User dictionary folder / Dict validation

Changes:

- Made General > Display language editable from the Options window.
  - The selected language is applied immediately through the existing localization flow.
  - The value is persisted in the local settings file.
- Added General > Default encoding.
  - New tabs and fallback file state now use the configured default encoding.
  - Open-file encoding selection falls back to this setting.
  - Save still uses the current tab encoding after a file is opened.
- Added General > Newline code.
  - Save output can now be normalized to LF, CRLF, or CR.
  - The editor text itself is not rewritten when the option is changed.
- Added Search > Regex lint.
  - Regex lint warnings can be enabled or disabled from Options.
  - The setting is applied to the Find / Replace dialog when it is open or newly created.
- Added Backup > Retention count and Retention days.
  - The settings are persisted for the backup feature.
  - The current backup manager still stores one unsaved-backup file, so these values are not pruning multiple backup files yet.
- Added Tag Insert > User dictionary folder.
  - User dictionaries can be loaded in addition to bundled dictionaries.
  - The Insert Tag menu and dialog use the configured user dictionary folder.
- Added Tag Insert > Dict validation.
  - When enabled, the selected user dictionary folder is validated before Options are applied.
  - Validation errors are shown with a localized message and the setting change is stopped.
- Updated Japanese and English option text for the new controls.
- Updated tests for settings persistence, option values, file newline output, regex lint disabling, and main-window option wiring.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
```

Latest result:

```text
pytest: 113 passed
ruff: All checks passed
pyright: 0 errors, 0 warnings, 0 informations
JSON validation: app_text_en.json OK, app_text_ja.json OK
```

Follow-up candidates:

1. Backup rotation behavior
   - Introduce rotating backup files if retention count / days should actively prune old backups.

2. User dictionary validation details
   - Expand messages so each broken dictionary entry is easier to identify.

## Priority Implementation Queue From 2026-09-21

Track these items before adding larger editor features.

Current status:

1. Dictionary safety validation - partially completed
   - Completed:
     - Dictionary JSON is parsed at load time.
     - Required `label_key`, `hint_key`, and `template` values are checked.
     - Empty required values are rejected.
     - Duplicate `{cursor}` placeholders are rejected.
     - Unknown placeholders other than `{selection}` and `{cursor}` are rejected.
     - Bundled dictionary label and hint keys are checked against Japanese and English resources by tests.
     - User dictionary folders can be validated from Options before applying the setting.
   - Remaining:
     - Detect duplicate `label_key` values inside one dictionary file.
     - Improve error messages so they identify the dictionary file and snippet more clearly.
     - Consider running the Japanese/English translation-key check for user dictionaries too, not only bundled dictionaries.

2. Hover hint enrichment - mostly completed
   - Completed:
     - HTML, Markdown, and WordPress HTML hints were expanded.
     - Practical attribute guidance such as `href`, `src`, `alt`, `class`, `id`, `rel`, and `target` was added where relevant.
     - Hover hints remain optional through the Options window.
     - Tag menus now enable Qt menu tooltips when hover hints are enabled.
     - The Insert Tag dialog now updates its hint text when the mouse hovers over a snippet row.
     - Help now includes an HTML attribute guide for `href`, `src`, `alt`, `class`, `id`, `style`, link safety attributes, CSS requirements, and common inline style properties.
   - Remaining:
     - Add structured parameter metadata only if future linting or guided editing needs it.

3. WordPress HTML mode refinement - partially completed
   - Completed:
     - WordPress modes exist: `Normal`, `Business / Office`, and `Hi-security`.
     - Snippets are filtered by mode.
     - Media snippets such as image, gallery, video, audio, and layout/media blocks were categorized and reviewed in tests.
   - Remaining:
     - Document the exact policy for each mode in the project notes or user help.
     - Review whether stricter modes should hide risky snippets completely or only de-prioritize them.

4. User dictionary folder - completed for Options wiring
   - Completed:
     - User-provided dictionaries can be configured separately from bundled dictionaries.
     - The Insert Tag menu and Insert Tag dialog use the configured user dictionary folder.
     - Options has a `Dict validation` toggle.
     - Bundled dictionaries remain separate from user-provided dictionaries.
   - Remaining:
     - Improve per-entry validation diagnostics as part of the dictionary safety work above.

5. PyInstaller dictionary packaging - completed
   - Completed:
     - `regex-pad.spec` includes the whole `dictionaries` folder.
     - Dictionary JSON files are not listed one by one.
     - A test checks that the spec includes `('dictionaries', 'dictionaries')`.
     - `regex-pad.spec` includes `resources/app_text_*.json` and `resources/regex_help_*.json`.
     - Clean PyInstaller build completed successfully.
     - Built executable startup smoke test completed without the previous `resources/app_text_en.json` `FileNotFoundError`.
   - Validation:
     - `.\build.ps1`
     - `Test-Path .\dist\regex-pad\_internal\resources\app_text_en.json`
     - `Test-Path .\dist\regex-pad\_internal\dictionaries\html_dict.json`
     - `dist\regex-pad\regex-pad.exe` stayed running for 3 seconds and was then stopped for the smoke test.

6. Display features - mostly completed
   - Completed:
     - Character ruler.
     - Ruler below the tab bar.
     - Click-to-set wrap column.
     - Green wrap-column guide line.
     - Visible half-width spaces, full-width spaces, tabs, and newlines.
     - Options wiring for line numbers, word wrap, ruler, wrap-at-column, wrap column, and visible whitespace.
   - Remaining:
     - Review marker color and visibility with large files, search highlights, wrapped lines, and proportional fonts.

## Validation Commands

Use the project virtual environment:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

## Project Principles

- Keep the app usable as a high-function one-folder application.
- Do not modify environment variables.
- Do not use the Windows Registry for settings.
- If a setting would normally require Registry usage, store it in a local `.ini` or `.json` file instead.
- Do not require administrator privileges.
- Store settings locally.
- Keep regex usable for non-programmers.
- Do not modify text during search.
- Modify text only when the user explicitly runs Replace or Replace All.
- Keep English and Japanese help aligned in meaning.
