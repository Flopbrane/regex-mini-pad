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

12. Saved-file generation backups
    - Save / Save As keeps the current on-disk file as a per-file backup before overwriting it.
    - Default backup retention count is 20 generations.
    - Unsaved backup remains a temporary crash-recovery file, separate from saved-file generations.

13. Snippet dictionary expansion
    - Added extra HTML, Markdown, and WordPress HTML snippets.
    - Kept dictionary entries backed by Japanese and English labels and hints.

## Next Recommended Steps

Progress on 2026-09-27:

- Regex rewrite / `normalise.py` workflow validation completed.
  - Full pytest passed: `207 passed`.
  - Ruff passed: `All checks passed!`.
  - Pyright passed: `0 errors, 0 warnings, 0 informations`.
  - JSON validation passed for app text resources and `wordpress_html_dict.json`.
  - Added a cancel-path test for the regex rewrite operation picker.
- Regex preview / replacement safety progressed.
  - Replace All from the Find / Replace dialog now fills the preview table and asks for confirmation before changing text.
  - Direct internal `replace_all()` calls remain usable for focused tests and non-dialog code paths.
- Save-time HTML / WordPress grammar safety progressed.
  - When HTML/WP typo lint is enabled, Save / Save As now runs the grammar check before writing.
  - If paragraph-split-related tag or WordPress block issues are found, the first issue line is selected and the user can cancel saving.
- Settings, dictionary, and file backup safety progressed.
  - Settings loading now falls back safely when individual values have invalid types.
  - Settings saving now uses a temporary file before replacing `settings.json`.
  - Saved-file generation backup now runs before overwriting an existing file.
  - Backup retention count / days now prune saved-file backup generations.
  - Unsaved backup stays scoped as temporary crash-recovery data for tabs/windows.
  - Snippet dictionaries were expanded with small practical HTML, Markdown, and WordPress entries.

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
   - Copy rectangular selection. Initial normal-selection-to-rectangle copy is implemented in `Step13-section1`.

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
  - `wp:html` custom code box uses a styled multi-line `<pre>` wrapper and keeps text immediately after `<code>`.
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
   - Completed in `dictionaries/README.md`.
   - The note documents required snippet keys, supported placeholders, validation rules, and the typo lint reference JSON.

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
   - Completed:
     - Backup retention count is editable and is used for saved-file generation backups.
     - Backup retention days is editable and is used for saved-file generation backups.
     - Unsaved backup remains temporary crash-recovery storage, not long-term history.
   - Remaining:
     - Backup interval.
     - Multi-tab temporary backup restore behavior.

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

4. Backup generation history
   - The retention count / days values are stored in Options.
   - Saved-file backups now rotate and prune by retention count / days.
   - The unsaved-backup implementation intentionally remains a temporary single crash-recovery file.
   - Add a restore UI for saved-file backup generations if users need in-app recovery.

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
  - These values are now used to prune saved-file generation backups.
  - Unsaved backup remains a separate temporary recovery file and does not use generation pruning.
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

1. Backup restore UI
   - Saved-file generation backups are now created and pruned.
   - Add an in-app restore / compare UI if users should recover from backups without opening the backup folder manually.

2. User dictionary folder integration
   - Load user-provided dictionaries separately from bundled dictionaries.
   - Keep bundled dictionaries read-only in normal use.

## Step11-section10 HTML Transform Helpers

Changes:

- Added context-menu HTML transform commands:
  - HTML Escape
  - HTML Unescape
  - WordPress Code Block
- The commands only transform the selected text.
  - If there is no selection, they leave the document unchanged and show a status-bar message.
- HTML Escape uses Python's standard HTML escaping with quote characters preserved.
  - `<` becomes `&lt;`
  - `>` becomes `&gt;`
  - `&` becomes `&amp;`
  - quotes stay readable.
- HTML Unescape converts escaped HTML entities back to literal HTML.
- WordPress Code Block wraps the selected text in:
  - `<!-- wp:html -->`
  - Multi-line `<pre ...>` attributes for easier editing.
  - `><code>...</code></pre>`
  - `<!-- /wp:html -->`
- The WordPress code-block helper does not add extra newlines immediately after `<code>` or before `</code>`.
- The WordPress HTML custom code-box snippet uses the same multi-line `<pre>` style.
- Added a WordPress HTML link block snippet:
  - The selected text becomes the link text.
  - The cursor is placed inside `href=""`.
  - The snippet is available in Normal, Business / Office, and Hi-security modes.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Latest result:

```text
pytest: 125 passed
ruff: All checks passed
pyright: 0 errors, 0 warnings, 0 informations
JSON validation: app_text_en.json OK, app_text_ja.json OK, wordpress_html_dict.json OK
```

## Step11-section11 Dictionary Safety Validation

Changes:

- Strengthened dictionary JSON validation at load time.
- Error messages now include the dictionary file and item number where possible.
- Added detection for:
  - Missing required keys: `label_key`, `hint_key`, `template`.
  - Empty required values.
  - Duplicate `label_key` values inside one dictionary file.
  - Duplicate `{cursor}` placeholders.
  - Broken `{selection}` / `{cursor}` placeholders.
  - Unknown placeholders such as `{selected_text}`.
  - Missing dictionary label / hint translation keys in both Japanese and English resources.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_tag_insert.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check editor\tag_insert.py tests\test_tag_insert.py
```

Latest result:

```text
pytest tests\test_tag_insert.py: 33 passed
ruff targeted: All checks passed
```

## Step11-section12 Future Multi-language Dictionary Plugins

Lightweight placeholder only. Do not start the heavy implementation until the current editor display work, color work, and WordPress HTML refinements are stable.

Goal:

- Allow RegexPad to behave as a lightweight multi-language editing helper by loading additional user dictionary files.
- Example future user dictionaries:
  - `javascript.json`
  - `textscript.json`
  - `css.json`
  - `php.json`
  - Other language or workflow-specific snippet packs.

Proposed future shape:

- Keep bundled dictionaries read-only and stable.
- Treat user dictionaries as plugin-like optional snippet packs.
- A user dictionary should be able to declare:
  - Display group name or translation key.
  - Target extensions such as `.js`, `.css`, or custom text formats.
  - Snippets with `label`, `hint`, `template`, and optional `category`.
  - Optional language id for later linting or coloring.
- The current dictionary safety validation should remain the first gate before a user dictionary is accepted.

Future lint files:

- Added a lightweight `json_lint.py` for validating JSON structure and readable error output.
- Added placeholder `multi_lang_lint.py` as the future coordinator for language-specific standards.
- Added standard reference files only as data, not executable code.
  - Example names:
    - `standard_javascript.json`
    - `standard_textscript.json`
    - `standard_css.json`
- These standard files can define allowed snippet fields, placeholder rules, recommended categories, and later language-specific constraints.

Deferred on purpose:

- Syntax coloring for each language.
- Heavy multi-language parsing.
- Full plugin manager UI.
- Automatic linting while typing.
- Complex standard-file enforcement beyond dictionary validation.

First small implementation entry, when ready:

1. Expand standard JSON files only when the user dictionary plugin format is finalized.
2. Decide whether direct `label` / `hint` text is allowed in addition to translation keys.
3. Only after that, wire the lint result into Options `Dict validation`.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_multi_lang_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check json_lint.py multi_lang_lint.py tests\test_multi_lang_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\standards\standard_javascript.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\standards\standard_textscript.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\standards\standard_css.json
```

Latest result:

```text
pytest tests\test_multi_lang_lint.py: 5 passed
ruff targeted: All checks passed
standard JSON validation: OK
```

## Step11-section15 HTML / WordPress Typo Lint Reference Cache

Changes:

- Added `dictionaries/lint_reference.json` as the HTML / WordPress typo lint reference file.
- Added `search/html_typo_lint.py`.
- The lint reference is loaded once at module startup into `LintReferenceCache`.
- Repeated lint calls use cached sets and tuples instead of reading JSON files again.
- Typo lint can now report:
  - Unknown HTML tags against `html_tags`.
  - Unknown HTML attributes against `html_attributes`.
  - Unknown WordPress core block names against `wordpress_core_blocks`.
- `aria-*` and `data-*` are accepted through `allowed_attribute_prefixes`.
- Added tests for tag typo, attribute typo, WordPress block typo, allowed prefixes, and no JSON reread during lint calls.
- Added a manual grammar-check action:
  - The Search menu now includes `Grammar Check` / `文法チェック`.
  - Shortcut: `F7`.
  - The action runs the current document through the HTML / WordPress typo lint.
  - Results are shown with line numbers in a dialog.
  - When issues are found, the cursor moves to the first reported line.
  - When no issues are found, a no-issues message is shown.
- Added WordPress paragraph block structure checks:
  - Detect missing `<p>` inside `<!-- wp:paragraph --> ... <!-- /wp:paragraph -->`.
  - Detect missing `</p>` inside `<!-- wp:paragraph --> ... <!-- /wp:paragraph -->`.
  - Detect `<!-- /wp:paragraph -->` without a matching opening block.
  - Detect mismatched or unclosed WordPress block comments.
  - Show a dedicated warning when `<!-- wp:html -->` is missing `<!-- /wp:html -->`, because later text may be treated as part of the HTML block.

Warning 2026-09-24:

- The first Grammar Check implementation only checked tag names, attribute names, and WordPress block names.
- It did not validate the internal structure of `wp:paragraph`, so WordPress paragraph errors could be missed even when WordPress reported them after paste/save.
- Current behavior is a practical pre-save guard for the reported cases, not a complete Gutenberg validator.
- `wp:html` closing-block omissions are high-risk because WordPress may treat following paragraph text and block comments as part of the HTML block after draft save.
- If WordPress reports another paragraph/block restriction, add the exact rejected snippet and WordPress error text as a regression case before broadening the checker.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_main_window_search.py tests\test_html_typo_lint.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\lint_reference.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
```

Latest result:

```text
pytest targeted: 38 passed
pytest: 160 passed
ruff: All checks passed
pyright: 0 errors, 0 warnings, 0 informations
JSON validation: lint_reference.json OK, app_text_ja.json OK, app_text_en.json OK
```

## Step11-section17 Regex Replacement Dollar Groups

Changes:

- Added support for `$1`, `$2`, and other dollar-style regex replacement groups in Regex-Pad replacement text.
- Added support for named dollar groups such as `${name}`.
- Existing Python-style replacement groups such as `\1`, `\2`, and `\g<name>` remain supported.
- In regex mode, `$$` now inserts a literal `$`, so `$$1` produces literal `$1`.
- Replacement preview, Replace, Replace All, and Replace Marked all share the same search engine conversion.
- Regex replacement lint now validates dollar-style replacement groups too.
- Clarification:
  - The presence or absence of `\n` in the search pattern does not decide whether replacement is regex-based.
  - Regex-Pad uses regex behavior when the Regular expression checkbox is ON.
  - The issue was that Python `re.sub()` does not treat `$1` as a capture-group reference unless Regex-Pad converts it first.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_search_engine.py tests\test_regex_lint.py tests\test_main_window_search.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check search\search_engine.py search\regex_lint.py tests\test_search_engine.py tests\test_regex_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright search\search_engine.py search\regex_lint.py tests\test_search_engine.py tests\test_regex_lint.py
```

Latest result:

```text
targeted pytest: 49 passed
targeted ruff: All checks passed
targeted pyright: 0 errors, 0 warnings, 0 informations
```

## Step11-section18 Regex Token Highlighting

Changes:

- Added regex-token highlighting to the Find / Replace dialog.
- When the Regular expression checkbox is ON, regex tokens in the Find and Replace inputs are shown in brown.
- Escaped literal HTML/WP text such as `\{` and `\}` remains unhighlighted where possible.
- The initial practical token coverage includes:
  - capture groups such as `(.*?)`
  - character classes by escape such as `\s*`, `\d+`, and `\w+`
  - anchors and alternation such as `^`, `$`, and `|`
  - replacement references such as `\1`, `$1`, and `${name}`
- When the checkbox is OFF, regex highlighting is disabled.
- The color is a UI hint only; regex execution is still controlled by the checkbox state.
- If inline highlighting is not readable enough in the actual GUI, add a one-line parsed-token preview between the Find and Replace inputs.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_find_replace_dialog.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check dialogs\find_replace_dialog.py dialogs\regex_input_edit.py tests\test_find_replace_dialog.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright dialogs\find_replace_dialog.py dialogs\regex_input_edit.py tests\test_find_replace_dialog.py
```

Latest result:

```text
targeted pytest: 9 passed
targeted ruff: All checks passed
targeted pyright: 0 errors, 0 warnings, 0 informations
```

## Step11-section16 Visible Whitespace Marker Colors

Changes:

- Added separate color settings for visible whitespace markers:
  - `visible_space_marker_color`
  - `visible_tab_marker_color`
  - `visible_newline_marker_color`
- Added View-tab Options controls for space, TAB, and newline marker colors.
- Existing tabs and new tabs now receive the configured marker colors.
- Visible whitespace painting now selects marker color by character type instead of using one shared color.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_text_editor_visible_whitespace.py tests\test_settings_manager.py tests\test_options_dialog.py -q
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check editor\text_editor.py settings\settings_manager.py dialogs\options_dialog.py main.py tests\test_text_editor_visible_whitespace.py tests\test_settings_manager.py tests\test_options_dialog.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright editor\text_editor.py settings\settings_manager.py dialogs\options_dialog.py main.py tests\test_text_editor_visible_whitespace.py tests\test_settings_manager.py tests\test_options_dialog.py
```

Latest result:

```text
targeted pytest: 10 passed
targeted ruff: All checks passed
targeted pyright: 0 errors, 0 warnings, 0 informations
```

## Step11-section13 WordPress Text Column Snippets

Changes:

- Added practical WordPress multi-column text snippets:
  - `2-column text block`
  - `3-column text block`
- Both snippets use WordPress standard `wp:columns` and `wp:column` wrappers.
- The selected text is inserted into the first column.
- The cursor is placed at the end of the first column's paragraph text.
- Remaining columns contain editable placeholder text.
- The snippets are categorized as Layout.
- The snippets are available in Normal, Business / Office, and Hi-security modes.
- Added Japanese and English labels and hover hints.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_tag_insert.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check editor\tag_insert.py tests\test_tag_insert.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\wordpress_html_dict.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
```

Latest result:

```text
pytest targeted: 39 passed
ruff targeted: All checks passed
JSON validation: wordpress_html_dict.json OK, app_text_ja.json OK, app_text_en.json OK
```

## Step11-section14 WordPress Custom Frame Snippet

Changes:

- Added a practical WordPress frame snippet:
  - `Custom frame block` / `自由枠ブロック`
- Added frame presets with temporary practical values:
  - `Notice frame block` / `注意枠ブロック`
    - `border: 2px solid #f2c94c`
    - `background-color: #fff8e1`
    - `color: #3a2a00`
  - `Info frame block` / `補足枠ブロック`
    - `border: 2px solid #2f80ed`
    - `background-color: #eef6ff`
    - `color: #102a43`
  - `Important frame block` / `重要枠ブロック`
    - `border: 3px solid #d64545`
    - `background-color: #fff1f1`
    - `color: #4a1111`
- The snippet uses a WordPress group wrapper and an editable inline `style`.
- The editable visual parameters are:
  - Border width: `border: 2px ...`
  - Border color: `#2f80ed`
  - Background color: `background-color: #f5f9ff`
  - Text color: `color: #111111`
  - Padding and border radius are included as practical defaults.
- The selected text is inserted into the frame paragraph.
- The cursor is placed at the end of the inserted paragraph text.
- The snippet is categorized as Layout.
- The snippet is available in Normal, Business / Office, and Hi-security modes.
- Added Japanese and English labels and hover hints.
- Future design note:
  - Add an Options `Theme` tab later.
  - Theme parameters should eventually manage editor colors and reusable content-frame values.
  - Candidate frame parameters:
    - Border width.
    - Border color.
    - Background color.
    - Text color.
    - Padding.
    - Border radius.
  - Keep current dictionary values as temporary defaults until theme editing exists.

Warning 2026-09-23:

- The business WordPress environment blocked or warned on the previous frame output.
- Temporary safety policy:
  - Treat decorated frame snippets as Custom HTML blocks.
  - Do not emit `wp:group` for decorated frame snippets.
  - Keep the opening and closing decorated `<div>` inside one `<!-- wp:html -->` block.
  - Do not split the opening `<div>` and closing `</div>` into separate `wp:html` blocks.
- Current temporary dictionary behavior:
  - `Custom frame block`, `Notice frame block`, `Info frame block`, and `Important frame block` now emit one `wp:html` block containing one styled `<div>`.
  - The selected text is inserted directly inside the styled `<div>` instead of being wrapped in an inner `wp:paragraph`.
  - This is intentionally conservative for on-site testing and may need another revision after the next saved test pattern is checked in the actual business WordPress environment.
- If additional restrictions appear, record the rejected snippet output and the WordPress warning/error text before changing the dictionary again.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_tag_insert.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check editor\tag_insert.py tests\test_tag_insert.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\wordpress_html_dict.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
```

Latest result:

```text
pytest tests/test_tag_insert.py: 44 passed
pytest full: 150 passed
ruff full: All checks passed
pyright full: 0 errors, 0 warnings, 0 informations
JSON validation: wordpress_html_dict.json OK
```

## Priority Implementation Queue From 2026-09-21

Track these items before adding larger editor features.

Current status:

Resolved items from the previous next-work order:

1. WordPress HTML mode policy documentation
   - Completed in User Help and this project note.
   - Normal, Business / Office, and Hi-security behavior is documented.
   - Current policy: stricter modes hide risky snippets rather than merely de-prioritize them.

2. Display feature review checklist
   - Completed as a manual/visual checklist below.
   - The checklist covers marker color, search highlights, wrapped lines, proportional fonts, large files, and narrow windows.
   - The actual GUI review should be run before changing colors or rendering behavior.

3. User dictionary plugin format decision
   - Completed for the current format.
   - Current decision: keep `label_key` / `hint_key` required for current user dictionaries.
   - Direct `label` / `hint` text is deferred until the plugin-like dictionary format is designed.

Recommended next-work order:

1. Structured parameter metadata
   - Completed for the minimum schema and validation.
   - Snippet JSON now accepts optional `parameters` arrays with `name`, `required`, `kind`, and `description_key`.
   - Validation rejects invalid parameter shapes, empty names, duplicate names, invalid `required`, invalid `kind`, invalid `description_key`, and missing translations for parameter description keys.

2. Separate lint helpers in Options
   - Foundation completed for the HTML/WP typo lint toggle.
   - The Search tab now owns ON/OFF settings for both Regex lint and HTML/WP typo lint.
   - The Search menu now has a manual Grammar Check action that runs the HTML/WP typo lint against the current document.

1. Dictionary safety validation - mostly completed
   - Completed:
     - Dictionary JSON is parsed at load time.
     - Required `label_key`, `hint_key`, and `template` values are checked.
     - Empty required values are rejected.
     - Duplicate `label_key` values inside one dictionary file are rejected.
     - Duplicate `{cursor}` placeholders are rejected.
     - Broken `{selection}` / `{cursor}` placeholders are rejected.
     - Unknown placeholders other than `{selection}` and `{cursor}` are rejected.
     - Optional structured `parameters` arrays are validated.
     - Parameter `description_key` values are checked against Japanese and English resources when present.
     - Dictionary label and hint keys are checked against Japanese and English resources at load time.
     - Error messages identify the dictionary file and item number where possible.
     - User dictionary folders can be validated from Options before applying the setting.
     - `dictionaries/README.md` documents bundled snippet dictionary format and validation rules.
     - Current user dictionaries continue to require `label_key` / `hint_key`; direct `label` / `hint` text is deferred to the future plugin-like dictionary format.
     - HTML/WP typo lint can be run manually from Search > Grammar Check.

2. Hover hint enrichment - mostly completed
   - Completed:
     - HTML, Markdown, and WordPress HTML hints were expanded.
     - Practical attribute guidance such as `href`, `src`, `alt`, `class`, `id`, `rel`, and `target` was added where relevant.
     - Hover hints remain optional through the Options window.
     - Tag menus now enable Qt menu tooltips when hover hints are enabled.
     - The Insert Tag dialog now updates its hint text when the mouse hovers over a snippet row.
     - Help now includes an HTML attribute guide for `href`, `src`, `alt`, `class`, `id`, `style`, link safety attributes, CSS requirements, and common inline style properties.
     - Structured parameter metadata usage in future linting or guided editing is recorded as future workflow work, not a current blocker.

3. WordPress HTML mode refinement - partially completed
   - Completed:
     - WordPress modes exist: `Normal`, `Business / Office`, and `Hi-security`.
     - Snippets are filtered by mode.
     - Media snippets such as image, gallery, video, audio, and layout/media blocks were categorized and reviewed in tests.
     - User Help documents the exact policy for each mode.
     - Stricter modes hide risky snippets rather than only de-prioritizing them.
     - No immediate work remains. Review the policy again only if users need a temporary "show all snippets" override.

4. User dictionary folder - completed for Options wiring
   - Completed:
     - User-provided dictionaries can be configured separately from bundled dictionaries.
     - The Insert Tag menu and Insert Tag dialog use the configured user dictionary folder.
     - Options has a `Dict validation` toggle.
     - Bundled dictionaries remain separate from user-provided dictionaries.
     - Current user dictionaries continue to require translation keys through `label_key` / `hint_key`.
     - Future plugin-like dictionary needs are recorded as future design work: group metadata, extension metadata, and direct labels.
     - `json_lint.py`, `multi_lang_lint.py`, and `standard_*.json` should stay lightweight until the plugin format is finalized.

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
     - Options wiring for line numbers, word wrap, ruler, wrap-at-column, wrap column, visible whitespace, and separate whitespace marker colors.
     - Display review checklist was added below for manual/visual checks.
     - No code change is queued for display features. Run the display review checklist on the actual GUI before changing marker colors or rendering behavior.

Display review checklist:

1. Large file visibility
   - Open or paste a long document with hundreds or thousands of lines.
   - Enable visible spaces, TABs, and newlines.
   - Scroll quickly and confirm the editor remains responsive enough for normal use.

2. Search highlight interaction
   - Search for a term that appears many times.
   - Confirm search markers, current match color, and whitespace marks remain readable together.
   - Check both light and dense text areas.

3. Wrapped line behavior
   - Enable word wrap and fixed-column wrap.
   - Use long Japanese and English lines.
   - Confirm visible spaces, TAB marks, newline marks, and the green wrap-column guide do not visually collide in a confusing way.

4. Proportional font behavior
   - Change the editor font to a proportional font from Options.
   - Confirm the ruler and wrap-column guide remain understandable.
   - If proportional fonts make the ruler misleading, document monospace as the recommended setting for ruler-based editing.

5. Narrow window behavior
   - Shrink the window width.
   - Confirm line numbers, ruler, search highlights, and visible whitespace marks do not obscure normal editing.

6. Color adjustment decision
   - Change colors only if the above checks show a concrete readability problem.
   - Prefer existing preset colors before adding a free color picker.

## Step12-section1 WordPress Image, Paragraph Split, And Simple Structure Check

Changes:

- Updated image insertion snippets:
  - `dictionaries/html_dict.json`
    - HTML `<img>` now inserts `style="width: 80%; display: block; margin: 2em auto 1.5em auto;"` immediately after `src`.
  - `dictionaries/wordpress_html_dict.json`
    - WordPress image block now inserts the same default image style.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Image hover/help text now mentions default width, alignment, and outer margin.
  - `tests/test_tag_insert.py`
    - Added insertion tests that confirm `src=""` cursor placement and the default image style.

- Added paragraph split context-menu support:
  - `editor/paragraph_splitter.py`
    - Added focused WordPress paragraph splitting helpers.
    - Detects a simple `<!-- wp:paragraph --> ... <!-- /wp:paragraph -->` block containing `<p>...</p>`.
    - Rebuilds output as `paragraph before`, inserted block, and `paragraph after`.
    - Trims only edge `<br>` / `<br><br>` markers while preserving meaningful internal line breaks.
    - Supports spacer insertion, empty HTML code block insertion, and selected-text decorated frame wrapping.
  - `main.py`
    - Added the editor context-menu submenu `段落分割`.
    - Added menu items:
      - `スペーサー挿入`
      - `HTML挿入`
      - `枠組み指定`
    - Shows a warning when the cursor or selection cannot be safely handled as a single paragraph block.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added labels and error title strings for the paragraph split menu.
  - `tests/test_paragraph_splitter.py`
    - Added string-level regression tests for paragraph detection, spacer insertion, HTML insertion, code wrapping, decorated frame wrapping, and invalid positions.
  - `tests/test_tag_insert.py`
    - Added context-menu regression coverage for the `段落分割` submenu and its three entries.

- Confirmed decorated frame output does not use `wp:preformatted`:
  - Paragraph split `枠組み指定` uses one `wp:html` block containing a styled `div`.
  - Existing WordPress decorated frame snippets continue to use one `wp:html` block and do not emit nested `wp:paragraph` or `wp:preformatted`.
  - Added regression checks for this policy.

- Added WP block simple structure checks to Grammar Check:
  - `search/html_typo_lint.py`
    - Added lightweight count checks for:
      - `<!-- wp:paragraph -->` / `<!-- /wp:paragraph -->`
      - `<!-- wp:html -->` / `<!-- /wp:html -->`
      - `<p>` / `</p>`
      - `<pre>` / `</pre>`
      - `<code>` / `</code>`
    - Added detection for malformed `<\p>`.
    - Added detection for known `margin:2en` typo.
    - Added detection for `wp:html` nested inside `wp:paragraph`.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added localized warning messages.
    - Updated the no-issue message to:
      - `簡易チェック完了：大きな構造エラーは見つかりませんでした。`
  - `tests/test_html_typo_lint.py`
    - Added regression tests for all newly added simple structure checks.
  - `tests/test_main_window_search.py`
    - Updated the no-issue dialog expectation.

Important policy notes:

- Do not use `wp:preformatted` for decorated frame output.
- If `wp:preformatted` is used by a separate snippet, do not place `wp:html` inside that `wp:preformatted` block.
- Keep decorated frame snippets as a single `wp:html` block with ordinary HTML inside.
- The new simple structure check is intentionally lightweight. It is not a full HTML validator; it targets common WordPress paste-breaking mistakes first.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\html_dict.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\wordpress_html_dict.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_paragraph_splitter.py tests\test_tag_insert.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_main_window_search.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
```

Validation result:

- JSON validation passed for the changed dictionaries and resources.
- `pytest tests\test_paragraph_splitter.py tests\test_tag_insert.py`: 60 passed.
- `pytest tests\test_html_typo_lint.py tests\test_main_window_search.py tests\test_app_translation.py`: 48 passed.
- Full `pytest`: 204 passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Targeted Ruff passed for the changed Python test/lint files.
- Full `ruff check .` still stops on the pre-existing import-order issue in `dialogs/find_replace_dialog.py`; this was not introduced by Step12-section1.

## Step12-section2 Settings Resilience, Dictionary Expansion, And Saved-File Backups

Purpose:

- Split backup responsibilities clearly:
  - Unsaved backup is temporary crash-recovery data for tabs/windows.
  - Saved-file backup is per-file generation history made before overwriting an existing file.
- Address the frustration that Undo can be cut off at the pre-restore state by keeping external file generations as a separate recovery path.
- Keep `main.py` structurally stable for now; avoid large file splitting until more of the feature surface is settled.

Changes:

- Hardened settings loading and saving:
  - `settings/settings_manager.py`
    - Invalid individual setting value types now fall back to defaults instead of crashing startup.
    - Non-object `settings.json` content falls back to defaults.
    - String boolean values such as `"true"` / `"false"` are handled safely.
    - Numeric settings reject boolean values and fall back on invalid strings such as `"wide"`.
    - Settings are now saved through a temporary file before replacing `settings.json`.
    - Default `backup_retention_count` changed from 10 to 20.
  - `tests/test_settings_manager.py`
    - Added regression coverage for invalid setting value types.
    - Added coverage for saving when the parent settings folder does not exist.

- Added saved-file generation backups:
  - `fileio/file_backup_manager.py`
    - Added `FileBackupManager`.
    - Backs up an existing file before it is overwritten.
    - Skips backup creation when the target file does not exist yet.
    - Stores backups per original file path using a safe file-name prefix and path hash.
    - Prunes backups by retention count and retention days.
  - `main.py`
    - Save / Save As now calls the file backup manager before writing the new file content.
    - Default saved-file backup location is `autosave/file_backups`.
    - If a backup folder is configured, saved-file backups go under `<backup_folder>/file_backups`.
    - Changing the backup folder from Options refreshes both the temporary unsaved backup manager and the saved-file backup manager.
  - `tests/test_file_backup_manager.py`
    - Added coverage for backup creation, missing-file skip behavior, and 20-generation pruning.
  - `tests/test_main_window_backup.py`
    - Added coverage that overwriting an existing file preserves the old content in saved-file backup history.

- Expanded snippet dictionaries:
  - `dictionaries/html_dict.json`
    - Added `<small>`, `<mark>`, `<details>`, and a basic `<table>` snippet.
  - `dictionaries/markdown_dict.json`
    - Added a 3-column table snippet.
  - `dictionaries/wordpress_html_dict.json`
    - Added a WordPress `wp:table` snippet.
    - Added a single-`wp:html` details/disclosure snippet.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added matching labels and hover hints for all new snippets.
  - `editor/tag_insert.py`
    - Updated category mapping and WordPress mode behavior for the new snippets.
  - `tests/test_tag_insert.py`
    - Updated snippet counts and mode/category expectations.
    - Added insertion tests for the WordPress table and single-`wp:html` details snippet.

- Added WordPress block parameter consistency checks:
  - `search/html_typo_lint.py`
    - Warns when WordPress block comment `{}` parameters are invalid JSON.
    - Warns when `wp:heading` `level` and the inner `<h*>` tag disagree.
    - Warns when `wp:spacer` `height` and inner HTML `style` height disagree.
    - Warns when `wp:image` `sizeSlug` and inner HTML `size-*` class disagree.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added localized Grammar Check messages for invalid block parameters and comment/HTML mismatches.
  - `tests/test_html_typo_lint.py`
    - Added mismatch and matching-case regression tests.

- Added WordPress parameter writing help:
  - `dialogs/user_help_dialog.py`
    - Added `WPパラメータ記述の注意事項` / `WordPress Parameter Notes`.
    - Documents that `{}` block attributes and inner HTML values must stay aligned.
    - Includes safe and risky examples for heading, spacer, and image blocks.
  - `tests/test_user_help_dialog.py`
    - Added navigation/content checks for the new help topic.

Policy notes:

- Unsaved backup should remain temporary and scoped to crash recovery. Do not treat it as long-term version history.
- Saved-file generation backup should run only when an existing file is about to be overwritten.
- The restore UI is available from File > Restore from Backup. It loads a selected backup into the editor as an unsaved change, so the original file is not overwritten until the user saves.
- The WordPress details snippet is provisional until real Gutenberg paste/save behavior is checked.
- The new parameter consistency lint is intentionally targeted. It checks common high-risk core blocks first, not every possible WordPress block attribute.
- Do not try to cover every core block attribute at once. When dictionaries add or change actual WordPress snippets, extend the lint with focused regression tests for those concrete attributes.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_settings_manager.py tests\test_tag_insert.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_file_backup_manager.py tests\test_main_window_backup.py tests\test_settings_manager.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_user_help_dialog.py tests\test_main_window_search.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- Targeted settings / tag / translation tests: 62 passed.
- Targeted backup tests: 12 passed.
- Targeted lint / user help / save-warning / translation tests: 60 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Full `pytest`: 221 passed.

## Step12-section3 Saved-File Backup Restore UI

Purpose:

- Finish the saved-file generation backup loop by adding an in-app recovery path.
- Keep restore behavior conservative: selected backups are loaded into the current editor as unsaved changes, not written directly over the original file.

Changes:

- Added File menu recovery action:
  - `main.py`
    - Added `Restore from Backup...` / `バックアップから復元...`.
    - Shows a dated backup picker for the current saved file.
    - Warns when no saved file is active or no backup exists for that file.
    - Respects the existing unsaved-change confirmation before replacing editor text.
    - Reads the backup using the current file encoding.
    - Marks restored content as modified so the user can review before saving.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added localized action text, picker text, empty-state messages, and restore result text.
  - `fileio/file_backup_manager.py`
    - Backup listing and pruning now sort by generated backup file name instead of file mtime.
    - This avoids unstable retention order when rapid consecutive backups inherit the same source-file mtime through `copy2`.

- Added regression tests:
  - `tests/test_main_window_backup.py`
    - Restoring a saved-file backup loads the backup text into the editor.
    - Restoring does not immediately overwrite the current disk file.
    - Declining the unsaved-change confirmation leaves the current editor text intact.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_main_window_backup.py tests\test_file_backup_manager.py
```

Validation result:

- Targeted backup tests: 10 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Full `pytest`: 227 passed.

## Step13-section1 Rectangular Copy Foundation

Purpose:

- Start the rectangular-selection section with a safe, testable foundation.
- Provide a usable first action before implementing a full mouse/keyboard rectangular selection mode.

Changes:

- Added rectangular text extraction helpers:
  - `editor/rectangular_selection.py`
    - Converts normal text selection positions into line/column rectangle coordinates.
    - Extracts the same column range from each selected line.
    - Preserves short lines as empty cells instead of padding or changing source text.

- Added an Edit menu action:
  - `main.py`
    - Added `Copy as Rectangle` / `矩形としてコピー`.
    - Shortcut: `Ctrl+Alt+C`.
    - Copies the rectangular text to the clipboard.
    - Leaves editor text and undo history unchanged.
    - Shows status messages for no selection, empty rectangular copy, and successful copy.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added action and status text.

- Added regression tests:
  - `tests/test_rectangular_selection.py`
    - Covers position-to-rectangle conversion and rectangular text extraction.
  - `tests/test_main_window_rectangular_selection.py`
    - Covers MainWindow action wiring through the clipboard.

Remaining for this section:

- Full rectangular selection mode is still pending.
- Mouse-based rectangular selection and keyboard expansion are still pending.
- Visual rectangular selection highlighting is still pending.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_rectangular_selection.py tests\test_main_window_rectangular_selection.py tests\test_app_translation.py
```

Validation result:

- Targeted rectangular-copy tests: 7 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Full `pytest`: 227 passed.

## Step13-section2 HTML Dictionary Help Topic

Purpose:

- Add a beginner-friendly HTML dictionary separate from the existing HTML attribute guide.
- Make RegexPad usable as a reference when writing ordinary HTML pages, not only WordPress snippets.

Changes:

- Added a new Help topic:
  - `dialogs/user_help_dialog.py`
    - Added `HTML Dictionary` / `HTML辞典`.
    - Covers the overview of HTML, CSS, and JavaScript responsibilities.
    - Includes a basic full-page HTML structure with `doctype`, `html`, `head`, `body`, `meta`, CSS, and script placement.
    - Lists common text, layout, media, form, table, and `head` tags, including tags not currently provided as snippets.
    - Explains what data can be placed inside tags: text, child HTML, attributes, metadata, CSS, JavaScript, and JSON data for scripts.
    - Adds META and JavaScript writing examples.
    - Adds a practical list of tags/features likely to be removed or restricted outside Normal mode, such as `script`, event attributes, `style`, `iframe`, embed tags, forms, SVG with script, `canvas`, and body-level `meta`/`link`.
    - Keeps code examples copyable from the Help viewer.

- Updated regression tests:
  - `tests/test_user_help_dialog.py`
    - Updated topic ordering after inserting `HTML辞典`.
    - Added Japanese and English content checks for the new dictionary.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_user_help_dialog.py
```

Validation result:

- Targeted user help tests: 6 passed.

## Step13-section3 HTML Tag Expansion, Risk Lint, And Color Picker

Purpose:

- Connect the new HTML dictionary to practical tag insertion.
- Add lightweight pre-save visibility for HTML tags and attributes that are often removed or restricted in stricter WordPress/security contexts.
- Improve existing color settings with visible swatches and a `#RRGGBB` color picker.
- Confirm that regex token coloring in Find / Replace already exists before changing that area.

Changes:

- Expanded HTML tag snippets:
  - `dictionaries/html_dict.json`
    - Added semantic/page-structure snippets: `header`, `nav`, `main`, `section`, `article`, `aside`, `footer`.
    - Added form/media snippets: `form`, `button`, `video`, `audio`.
  - `editor/tag_insert.py`
    - Categorized the new snippets into existing HTML menu groups.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added labels and hover hints for the new snippets.

- Added restricted HTML warnings:
  - `search/html_typo_lint.py`
    - Warns for tags that are likely to be removed or restricted by stricter WordPress/site settings, such as `script`, `style`, `iframe`, `object`, `embed`, form controls, `button`, and `canvas`.
    - Warns for event-handler attributes such as `onclick`.
    - Keeps these as warnings because they may be valid in normal standalone HTML.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added localized warning messages.

- Improved color selection UI:
  - `dialogs/options_dialog.py`
    - Existing color settings now show small color swatches in their combo boxes.
    - Added `色選択...` / `Choose Color...` buttons next to the existing color combo boxes.
    - The dialog accepts arbitrary colors through Qt's color picker and stores them as `#rrggbb`.
    - Applied to search marker colors, visible whitespace marker colors, and WordPress frame background/text colors.

- Confirmed existing regex coloring:
  - `dialogs/regex_input_edit.py`
    - `RegexInputHighlighter` already colors regex tokens when regex mode is enabled in the Find / Replace dialog.
    - No behavior change was made there in this section.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool dictionaries\html_dict.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_tag_insert.py tests\test_html_typo_lint.py tests\test_options_dialog.py tests\test_find_replace_dialog.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
```

Validation result:

- JSON validation passed for the HTML dictionary and both app translation files.
- Targeted tag/lint/options/find-replace tests: 90 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.

## Step13-section4 Editor Theme And HTML Syntax Highlighting

Purpose:

- Add full editor-side HTML tag coloring to make HTML and WordPress snippets easier to inspect in the main text editor.
- Add editor-wide theme switching with saved background, text, and HTML tag colors.
- Keep the implementation local and portable through the existing settings JSON.

Changes:

- Added editor-side HTML highlighting:
  - `editor/text_editor.py`
    - Added a `QSyntaxHighlighter` for HTML tags and WordPress block comments.
    - Tags such as `<div>`, `</p>`, and `<br>` are highlighted in the configured HTML tag color.
    - WordPress block comments such as `<!-- wp:paragraph -->` are highlighted in a softer comment color.
    - The highlighter is visual only and does not modify the source text.

- Added editor theme settings:
  - `settings/settings_manager.py`
    - Added persistent keys for `editor_theme`, `editor_background_color`, `editor_text_color`, and `html_tag_color`.
  - `dialogs/options_dialog.py`
    - Added theme presets: light, soft paper, dark, high contrast, and custom.
    - Added color picker rows for editor background, editor text, and HTML tag color.
  - `main.py`
    - Applies the saved editor colors to all open tabs.
    - Applies the selected colors immediately after accepting the Options dialog.
    - Applies the saved colors to newly created tabs.

- Updated localization and tests:
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added labels for editor theme controls and color rows.
  - `tests/test_settings_manager.py`
    - Covered saving/loading the new theme fields.
  - `tests/test_options_dialog.py`
    - Covered the new theme controls and returned values.
  - `tests/test_text_editor_visible_whitespace.py`
    - Covered editor color application to the text editor stylesheet.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_options_dialog.py tests\test_settings_manager.py tests\test_text_editor_visible_whitespace.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- JSON validation passed for both app translation files.
- Targeted options/settings/text-editor tests: 13 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Full `pytest`: 230 passed.

## Step13-section5 Modeless Grammar Check And Core Block Color

Purpose:

- Allow editing the main document while grammar check results remain visible.
- Reduce fragile tag-count false positives by counting actual HTML tag tokens instead of broad text matches.
- Make WordPress core block comment color configurable separately from ordinary HTML tag color.

Changes:

- Added a modeless grammar check results window:
  - `dialogs/grammar_check_dialog.py`
    - Added a reusable non-modal grammar check dialog.
    - Shows the current result summary and a clickable list of issue rows.
    - Clicking an issue moves the editor cursor to that line.
    - Added a `Recheck` / `再チェック` button so the user can keep the results window open while editing.
  - `main.py`
    - Manual Grammar Check now opens/updates the modeless result window instead of blocking with `QMessageBox.warning()` or `QMessageBox.information()`.
    - Save-time grammar confirmation remains modal because it protects the save operation.

- Tightened lint token counting:
  - `search/html_typo_lint.py`
    - Counts `<p>`, `<pre>`, and `<code>` pairs from extracted `<...>` HTML tag tokens.
    - Does not treat plain text such as `code` as a tag.
    - Accepts compact WordPress block comments such as `<!--wp:paragraph-->` and `<!--/wp:paragraph-->` for simple count checks.

- Added configurable core block color:
  - `editor/text_editor.py`
    - WordPress block comments can now use a separate configured color.
  - `settings/settings_manager.py`, `dialogs/options_dialog.py`, and `main.py`
    - Added `wordpress_core_block_color` to load/save, options, theme presets, and all-tab application.
  - `resources/app_text_ja.json` and `resources/app_text_en.json`
    - Added labels for core block color and grammar recheck.

- Updated tests:
  - `tests/test_main_window_search.py`
    - Verifies grammar check uses a modeless result window and that issue rows can jump to the source line.
  - `tests/test_html_typo_lint.py`
    - Verifies `<code>code</code>` and compact WordPress comments do not trigger false count mismatches.
  - `tests/test_options_dialog.py`, `tests/test_settings_manager.py`, and `tests/test_text_editor_visible_whitespace.py`
    - Covered the new core block color setting.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_main_window_search.py tests\test_options_dialog.py tests\test_settings_manager.py tests\test_text_editor_visible_whitespace.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- JSON validation passed for both app translation files.
- Targeted lint/main-window/options/settings/text-editor tests: 67 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Full `pytest`: 231 passed.

## Step13-section6 Sample-Based Grammar Lint Expansion

Purpose:

- Reduce the gap between RegexPad's grammar check and the real `sample/test.wp_html` problems found during external review.
- Stop collapsing several different HTML/WP breakages into only one `<code>` count mismatch.
- Preserve the lightweight lint approach while adding regression coverage for the current sample.

Findings:

- `sample/test.wp_html` no longer had the old global backslash escaping issue.
- RegexPad reported only one `<code>` count mismatch because the existing lint mostly checked total open/close counts.
- The sample actually had several different issue categories:
  - Empty `<p></p>` outside a WordPress block.
  - Duplicated paragraph openings after the embed section.
  - Broken `/code&gt;` fragments.
  - Nested/unclosed `<code>` tags.
  - `<code>` contamination inside a separator block.
  - Missing `</strong>`.
  - Lone `<br>` outside a WordPress block.

Changes:

- Expanded `search/html_typo_lint.py`:
  - Added `<strong>` count mismatch checks.
  - Added non-nestable `<code>` nesting checks so broken code snippets are reported near their source.
  - Added orphan line checks for standalone `<p></p>` and `<br>` outside WordPress blocks.
  - Added a separator-body check that warns when `<code>` tags are mixed into a separator block.
  - Added a broken escaped close-fragment check for `/code&gt;`.
  - Added a lightweight duplicate WordPress paragraph opening check based on normalized visible paragraph text.
  - Adjusted the first mismatch position logic so an unclosed/nested `<code>` reports near the first nested problem instead of only near the final imbalance.

- Updated localization:
  - `resources/app_text_ja.json`
  - `resources/app_text_en.json`
  - Added user-facing messages for the new lint categories.

- Updated regression tests:
  - `tests/test_html_typo_lint.py`
    - Added focused tests for nested `<code>`, missing `</strong>`, orphan `<p></p>` / `<br>`, separator code contamination, `/code&gt;`, duplicate paragraph openings, and the real `sample/test.wp_html` problem categories.
    - The sample now produces multiple issue categories instead of only one `<code>` count mismatch.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_main_window_search.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- JSON validation passed for both app translation files.
- Targeted lint/main-window tests: 59 passed.
- Full `ruff check .`: All checks passed.
- `pyright`: 0 errors, 0 warnings, 0 informations.
- Full `pytest`: 236 passed.
- Current `sample/test.wp_html` lint output: 16 issue rows across the expected categories.

## Step13-section7 Escaped Code Display And Inline Tag Lint Order

Purpose:

- Re-check the grammar lint algorithm after `sample/test.wp_html` was mostly repaired.
- Avoid false positives from escaped HTML shown inside code display blocks.
- Report real inline HTML tag breakage at the source line instead of at a later unrelated matching tag.

Findings:

- Current `sample/test.wp_html` no longer has the previous broad set of sample breakages.
- The remaining grammar-check output had three rows:
  - 299 and 319 were `/code&gt;` fragments inside `wp:code` display content, not broken live HTML.
  - The `<strong>` issue was still real in the file, but the old count-based check pointed at a later normal `<strong>` line.
- Total tag counts are useful as a coarse fallback, but they are fragile for inline tags because a later valid close tag can mask where the actual omission started.

Lint order policy:

1. Read WordPress block comments first and identify block bodies.
2. Treat escaped display content inside `wp:code` and `wp:html` as code text for fragile escaped-fragment checks.
3. Run simple WordPress block structure checks.
4. Run real HTML token checks with `HTMLParser`.
5. For inline tags such as `strong`, `em`, `span`, `code`, and `a`, detect:
   - Unclosed inline tags before a parent close such as `</p>`.
   - Invalid closing order such as closing `</strong>` before `</span>`.
6. Keep dictionary/tag/attribute and WordPress attribute-vs-HTML consistency checks as targeted warnings.

Changes:

- Updated `search/html_typo_lint.py`:
  - Added inline-tag stack checks for unclosed inline tags before parent close tags.
  - Added a separate document-end message for inline tags that remain open at EOF.
  - Added closing-order checks for nested inline tags.
  - Stopped using global `<strong>` count mismatch as the primary diagnostic.
  - Ignored `/code&gt;` escaped-fragment warnings inside `wp:code` and `wp:html` bodies.

- Updated localization:
  - `resources/app_text_ja.json`
  - `resources/app_text_en.json`
  - Added repair-oriented messages for inline tag closing and closing-order issues.

- Updated regression tests:
  - `tests/test_html_typo_lint.py`
    - Added tests for `<strong>` missing before `</p>`.
    - Added tests for invalid inline nesting order.
    - Added tests for inline tags left open at document end.
    - Added tests confirming escaped HTML inside a WordPress code block is accepted.
    - Adjusted the real sample check so repaired samples do not depend on old issue counts.

Current sample result:

- `sample/test.wp_html` now reports one remaining issue:
  - 501行目: `<strong>` is not closed before `</p>`.
- The former 299/319 `/code&gt;` rows are no longer reported.

## Step13-section8 Planned Lint Ledger Refactor

Purpose:

- Prepare the next lint foundation pass before adding more individual rules.
- Reduce false positives and missed errors by separating typo detection, WordPress block structure, and HTML tag structure.
- Use the standard lint dictionary as the shared reference source instead of letting each check infer its own truth.

Direction:

- Treat `dictionaries/lint_reference.json` as the standard reference dictionary for known WordPress core blocks, HTML tags, HTML attributes, and allowed attribute prefixes.
- Gradually change the grammar check into three comparison stages:
  1. `Typo_lint`
     - Detect simple textual damage and dictionary mismatches.
     - Examples: unknown WordPress block names, unknown HTML tags, unknown attributes, `<\p>`, `margin:2en`, and fragile literal fragments.
     - Do not decide complex open/close structure here.
  2. `WP_lint`
     - Parse only WordPress block comments such as `<!-- wp:paragraph -->` and `<!-- /wp:paragraph -->`.
     - Build a WordPress block ledger with line numbers, open/close kind, block name, parent relationship, body range, and display-code/custom-HTML ranges.
     - Do not deeply validate HTML tags in this stage.
  3. `HTML_lint`
     - Parse real HTML tags using the WP ledger as context.
     - Ignore escaped display content inside `wp:code` and other ledger-marked display areas.
     - Check tag open/close order, missing close tags, unexpected close tags, and inline-tag parent boundaries.

Ledger policy:

- Prefer in-memory ledgers for normal lint execution.
- Use `lint_wp_blocks.json` and `lint_html_tags.json` only as optional debug output or inspection artifacts, not as always-on source-of-truth files.
- Avoid depending on stale generated JSON during ordinary grammar checks.
- If debug JSON output is added later, write it under a cache/debug location and make it explicitly regenerated per lint run.

Planned internal records:

- `WPBlockRecord`
  - `line_number`
  - `block_name`
  - `kind` (`open` / `close`)
  - `pair_id`
  - `parent_pair_id`
  - `body_start`
  - `body_end`
  - `is_display_code_area`
- `HtmlTagRecord`
  - `line_number`
  - `tag_name`
  - `kind` (`open` / `close` / `self_closing`)
  - `pair_id`
  - `wp_block_pair_id`
  - `ignored_reason`

Implementation notes for next pass:

- Keep existing user-facing grammar-check output stable while replacing the internal structure.
- First build ledger helpers inside `search/html_typo_lint.py` to avoid premature large-file/module splitting.
- After behavior is stable, consider extracting to dedicated modules such as `linting_wp_block.py` and `linting_html_tag.py`.
- Add regression tests for each migration step before removing old count-based checks.
- Keep `wp:code` and inline `<code>&lt;...&gt;</code>` display content out of live HTML structural checks.

## Step13-section9 Grammar Issue Background Highlight

Purpose:

- Make grammar-check findings visible directly in the main editor while the check result is active.
- Restore the editor to the normal theme/background when the warning context is gone or the text changes.

Changes:

- Updated `editor/text_editor.py`:
  - Added a separate grammar issue line highlight state.
  - Combined grammar issue selections with existing search selections instead of replacing search highlights.
  - Uses a faint red full-line background for grammar issue lines.

- Updated `main.py`:
  - Manual Grammar Check now highlights all issue lines in the current editor.
  - A no-issue result clears existing grammar issue highlights.
  - Editing the text clears stale grammar issue highlights.
  - Save-time grammar confirmation highlights issue lines only while the confirmation is active, then clears them.
  - Closing/hiding the modeless grammar-check dialog clears the highlights.

- Updated `dialogs/grammar_check_dialog.py`:
  - Added a `dismissed` signal emitted when the dialog is hidden.

- Updated `tests/test_main_window_search.py`:
  - Added regression tests for issue-line highlighting.
  - Added tests for clearing highlights after no-issue checks, edits, and dialog hide.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_main_window_search.py tests\test_text_editor_visible_whitespace.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check editor\text_editor.py dialogs\grammar_check_dialog.py main.py tests\test_main_window_search.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
```

Validation result:

- Targeted grammar/search/editor tests: 43 passed.
- Targeted Ruff: All checks passed.
- Pyright: 0 errors, 0 warnings, 0 informations.

## Step13-section10 Line Selection From Gutter

Purpose:

- Make line selection easier while reviewing lint results or editing line-based text.
- Allow clicking the line-number area to select exactly that line.
- When line numbers are hidden, allow the far-left line head area to perform the same line selection.

Changes:

- Updated `editor/line_number_area.py`:
  - Left-clicking the line number gutter selects the clicked line.

- Updated `editor/text_editor.py`:
  - Added shared line-selection helpers based on visible block position.
  - Added a small left-edge hit area for line selection when line numbers are hidden.
  - Kept ordinary clicks unchanged outside that narrow left-edge area.

- Updated `tests/test_text_editor_visible_whitespace.py`:
  - Added tests for selecting a line by clicking the line-number area.
  - Added tests for selecting a line by clicking the line head when line numbers are hidden.

Related validation fix:

- Updated `fileio/file_backup_manager.py` after full-suite validation exposed an existing backup-retention instability.
  - Fast repeated backups could collide or sort inconsistently when relying on timestamps alone.
  - Backup filenames now include a manager-local monotonic sequence.
  - Backup file mtime is refreshed after copy so retention-days checks use the backup creation time rather than the source file timestamp.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_file_backup_manager.py tests\test_text_editor_visible_whitespace.py tests\test_main_window_search.py
```

Validation result:

- Targeted file-backup/editor/search tests: 48 passed.

## Step13-section11 Backup Scope Policy

Purpose:

- Clarify the backup feature policy after the line-selection and lint-highlight pass.
- Keep backup behavior simple and local instead of turning it into a full long-term generation history system.

Policy:

- Saved-file backups are treated as a per-file recovery ring, similar to an external Undo/Redo safety net.
- Keep about 20 recent backups per original file by default.
- Do not expand this into a separate heavy generation-backup feature unless requirements change.
- The temporary unsaved backup remains separate:
  - It is for tab/window crash recovery.
  - It is not long-term file history.
- The default backup location should remain inside the RegexPad project folder:
  - Unsaved temporary backup: `autosave/unsaved_backup.json`
  - Saved-file recovery backups: `autosave/file_backups`
- The current Options-based backup folder override is sufficient:
  - Empty setting uses the RegexPad-local default.
  - A configured folder stores the same backup data under that user-selected location.

Implementation note:

- The current saved-file backup manager already keeps backups per original file path and defaults to 20 entries.
- Keep the restore UI conservative: selected backup content is loaded into the editor as an unsaved change, not written directly over the original file.

## Step13-section12 Paragraph Split Insertion Baseline

Purpose:

- Make the paragraph split insertion start point match the user's actual editing gesture.
- Reduce accidental paragraph splitting when inserting spacer, HTML code, or decorated frame blocks.

Changes:

- Updated `editor/paragraph_splitter.py`:
  - Spacer insertion now only works from an empty line inside a simple `wp:paragraph`.
  - Non-empty-line spacer insertion is rejected with a clear message asking the user to right-click an empty line created by Enter.
  - HTML code block wrapping and decorated frame wrapping now expand a partial selection to whole content lines before splitting the paragraph.
  - The selected line range becomes the inserted `wp:html` block content, while before/after lines remain normal paragraph blocks.

- Updated `main.py`:
  - Right-clicking the editor moves the cursor to the clicked position only when there is no active selection.
  - HTML insertion now uses the same selection-wrapping path as the code-block wrapper, so selected text is contained instead of inserting an empty block at the cursor.

- Updated `tests/test_paragraph_splitter.py`:
  - Added spacer-empty-line behavior coverage.
  - Added nonblank-line spacer rejection coverage.
  - Added partial-selection-to-line-range coverage for HTML code and decorated frame wrapping.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_paragraph_splitter.py
```

Validation result:

- Paragraph splitter tests: 10 passed.

## Step13-section13 Linter Token Inventory Hardening

Purpose:

- Continue hardening the Grammar Check / HTML-WP linter foundation.
- Move fragile count checks toward separate token inventories for WordPress block comments and live HTML tags.
- Keep displayed escaped code examples out of live HTML tag counting.

Changes:

- Updated `search/html_typo_lint.py`:
  - Added an internal `_LintToken` model for detected WordPress block comments and HTML tags.
  - WordPress block count checks now use a WordPress-comment token list instead of ad hoc per-rule counting.
  - HTML `<p>`, `<pre>`, and `<code>` count checks now use `HTMLParser`-collected live tag tokens.
  - Nested `<code>` detection now uses the same live tag token stream.
  - WordPress block mismatch handling no longer consumes the currently open block when the closing comment name is wrong and no matching block exists on the stack.

- Updated `tests/test_html_typo_lint.py`:
  - Added coverage that escaped display examples such as `&lt;code&gt;...&lt;/code&gt;` do not trip live `<code>` counts.
  - Added coverage that a wrong closing WordPress block comment does not hide a later valid closing comment for the still-open block.

Sample check:

- `sample/test.wp_html` currently reports only the expected `<strong>` before `</p>` issue at line 501.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check search\html_typo_lint.py tests\test_html_typo_lint.py
```

Validation result:

- HTML typo linter tests: 33 passed.
- Targeted Ruff: All checks passed.

## Step13-section14 HTML Structural Tag Lint Hardening

Purpose:

- Continue hardening the Grammar Check / HTML-WP linter after the token inventory baseline.
- Detect malformed live HTML tag order that count-only checks can miss.
- Keep the first pass conservative by limiting the structural stack check to `<p>`, `<pre>`, and `<code>`.

Changes:

- Updated `search/html_typo_lint.py`:
  - Added a structural stack pass over the existing live HTML tag token stream.
  - Detects tracked closing tags with no matching opener.
  - Detects crossed closing order such as `<pre><code>...</pre></code>`.
  - Detects tracked tags left open at the end of the document.

- Updated `resources/app_text_ja.json` and `resources/app_text_en.json`:
  - Added localized messages for unexpected, mismatched, and missing HTML closing tags.

- Updated `tests/test_html_typo_lint.py`:
  - Added regression tests for tracked-tag closing order, extra closing tags, and missing closing tags.

Sample check:

- `sample/test.wp_html` still reports only the expected `<strong>` before `</p>` issue at line 501.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check search\html_typo_lint.py tests\test_html_typo_lint.py
```

Validation result:

- HTML typo linter and app translation tests: 39 passed.
- JSON syntax checks: passed.
- Targeted Ruff: All checks passed.

## Step13-section15 Separator Code Cascade Suppression

Purpose:

- Reduce noisy cascade errors in Grammar Check when a separator block contains accidental `<code>` tags.
- Keep the root cause visible as one representative warning.
- Preserve line numbers and normal HTML tag checks outside the contaminated separator block.

Changes:

- Updated `search/html_typo_lint.py`:
  - Added detection for separator block bodies containing `<code>` tags.
  - Masks only those contaminated separator bodies before the general live-HTML tag checks run.
  - Preserves newlines while masking so later warning line numbers stay stable.
  - Keeps the WordPress separator-specific warning on the original source text.

- Updated `resources/app_text_ja.json` and `resources/app_text_en.json`:
  - Expanded the separator `<code>` warning to explain that it can confuse later tag checks and should first be repaired to `<hr ... />` only.

- Updated `tests/test_html_typo_lint.py`:
  - Added a regression test that `<hr ...><code><code>` inside `wp:separator` reports only the representative separator warning instead of cascading into `<code>` count, nesting, and missing-close warnings.

Sample check:

- `sample/test_sample.wp_html` now reports 8 review items instead of 14.
- The 130-line separator issue remains, while the six 131-line `<code>` cascade items are suppressed.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check search\html_typo_lint.py tests\test_html_typo_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- HTML typo linter and app translation tests: 40 passed.
- JSON syntax checks: passed.
- Targeted Ruff: All checks passed.
- Full Ruff: All checks passed.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Full pytest: 255 passed.

## Step13-section16 WordPress Block Message Clarity

Purpose:

- Keep independent Grammar Check findings as separate rows even when line numbers repeat.
- Improve WordPress block findings so each row gives a concrete repair direction.
- Preserve the separator cascade suppression and the 8-item `test_sample.wp_html` result.

Changes:

- Updated `resources/app_text_ja.json` and `resources/app_text_en.json`:
  - `unexpected_wordpress_closing_block` now explains either removing the extra closing comment or adding the intended opening comment.
  - `mismatched_wordpress_block` now shows the expected closing comment before the currently encountered closing comment.
  - `missing_wordpress_closing_block` now shows the exact closing comment to add.

- Updated `tests/test_html_typo_lint.py`:
  - Added `sample/test_sample.wp_html` regression coverage for the current 8 finding rows.
  - Locked in the rule that independent findings remain separate while the separator `<code>` cascade stays suppressed.

Sample check:

- `sample/test_sample.wp_html` reports 8 review items:
  - line 31 `<strong>` before `</p>`
  - line 35 `<span>` before `</strong>`
  - line 49 `<a>` before `</p>`
  - line 78 missing `<!-- /wp:list-item -->`
  - line 85 close `<!-- /wp:list-item -->` before `<!-- /wp:list -->`
  - line 98 broken `/code&gt;`
  - line 130 separator `<code>` contamination representative warning
  - line 148 `<span>` before `</p>`

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- HTML typo linter and app translation tests: 41 passed.
- JSON syntax checks: passed.
- Full Ruff: All checks passed.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Full pytest: 256 passed.

## Step13-section17 Grammar Check Copy List And Wider Dialog

Purpose:

- Make the Grammar Check dialog wide enough for longer Japanese repair hints.
- Let the user copy the current review list as plain text for notes or external review.

Changes:

- Updated `dialogs/grammar_check_dialog.py`:
  - Set the initial dialog size to `930 x 360`.
  - Added a copy-list action button.
  - Store the current result rows as newline-separated plain text.
  - Disable the copy button when there are no findings.

- Updated `resources/app_text_ja.json` and `resources/app_text_en.json`:
  - Added the localized copy-list button label.

- Updated `tests/test_main_window_search.py`:
  - Added regression coverage for the `930` width.
  - Added clipboard-copy coverage for Grammar Check findings.
  - Added no-issue coverage that keeps the copy button disabled.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_main_window_search.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- Main window search and app translation tests: 39 passed.
- JSON syntax checks: passed.
- Full Ruff: All checks passed.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Full pytest: 256 passed.

## Step13-section18 Linter Target Lines And Block Scope Hardening

Purpose:

- Point Grammar Check findings at the line that should be edited, not only the opening WordPress block comment.
- Catch HTML tag structure problems inside each WordPress core block.
- Keep escaped code examples inside `<code>...</code>` acceptable.
- Support whole-file HTML structure checks when the document has no WordPress block comments.
- Add conservative WordPress core block attribute checks for representative blocks.

Changes:

- Updated `search/html_typo_lint.py`:
  - WordPress paragraph checks now report the first body line, `<p>` line, or `<div>` line when available.
  - Separator `<code>` contamination now reports the line containing the stray `<code>`.
  - Repeated non-nestable WordPress blocks such as `wp:list-item` now report the next opening block line as the practical repair point.
  - HTML structure checks now run per WordPress block, while pure HTML files use a whole-file structure check.
  - Block-level HTML tags such as `div`, `main`, `section`, `ul`, `li`, and table tags are now included in structure checks.
  - Added conservative allow-list checks for common WordPress block comment attributes.

- Updated `resources/app_text_ja.json` and `resources/app_text_en.json`:
  - Added `unknown_wordpress_block_attribute` user-facing messages.

- Updated `tests/test_html_typo_lint.py`:
  - Updated expected line numbers from opening block lines to practical repair lines.
  - Added coverage for unknown WordPress block attributes.
  - Added coverage for accepted known block attributes.
  - Added coverage for an unclosed `<div>` inside a `wp:html` block.
  - Added coverage for whole-file pure HTML structure checks.

Notes:

- Japanese typo/style checks are intentionally left as future work because they need a separate Japanese dictionary and settings switch.
- The attribute check is intentionally conservative: blocks without an allow-list are skipped to avoid noisy false positives.

Validation:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py tests\test_app_translation.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check search\html_typo_lint.py tests\test_html_typo_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

Validation result:

- HTML typo linter and app translation tests: 45 passed.
- JSON syntax checks: passed.
- Targeted Ruff: All checks passed.
- Full Ruff: All checks passed.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Full pytest: 260 passed.

## Step13-section19 Scheduled Linter Cascade Review

Date: 2026-10-02

Changes:

- Kept separator structural cascade suppression, but checked original markup for independent unknown tags, attributes, restricted markup, and fragile typos.
- Preserved multiple independent findings on the same line and stable ascending line-number ordering.
- Clarified JA/EN missing WordPress closing-block messages with insertion guidance before the next same-type block or the parent closing markup.
- Added regressions for two independent attributes on a contaminated separator line, a separate CSS typo, a later paragraph error, repeated list-item openings, and a list/list-item closing mismatch.
- Reviewed localized sample/test_sample.wp_html results: 8 findings at lines 31, 35, 49, 81, 98, 120, 131, and 148; no separator code cascade.

Validation:

- Focused linter and translation tests: 49 passed.
- JA/EN translation JSON parsing: passed.
- Full Ruff: passed.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Full pytest: 264 passed.
- Manual GUI and real Gutenberg acceptance were not performed in this scheduled run.

## Step13-section20 WordPress Core Block Reference Dictionary Expansion

Date: 2026-10-03

Changes:

- Expanded `dictionaries/lint_reference.json` with the current official WordPress Core Blocks Reference block names.
- Added `wordpress_block_attributes` to `lint_reference.json` so `{}` parameter checks can be maintained from dictionary data instead of only hard-coded Python allow-lists.
- Kept common WordPress support attributes such as `className`, `style`, `metadata`, `lock`, and common color/font keys accepted conservatively across blocks.
- Added common WordPress-generated HTML attributes such as `srcset`, `sizes`, `decoding`, `fetchpriority`, `datetime`, `poster`, and media boolean attributes.
- Updated `search/html_typo_lint.py` to load block-attribute allow-lists from the startup lint reference cache.
- Updated README files and dictionary format notes for the expanded lint reference.
- Added regressions for official reference block attributes, unknown reference attributes, and WordPress image generated HTML attributes.

Notes:

- The reference is a bundled offline snapshot; RegexPad still does not fetch WordPress documentation at runtime.
- Deprecated / unsupported official core entries are accepted by the linter to avoid false unknown-block warnings, but this does not mean they should be promoted as snippet insertion candidates.
- Real Gutenberg paste/save acceptance was not performed in this step.

## Step13-section21 HTML Attribute Reference and Tag-Specific Lint

Date: 2026-10-05

Changes:

- Added `global_html_attributes` and `html_attributes_by_tag` to `dictionaries/lint_reference.json`.
- Added conservative tag-specific HTML attribute checks so known attributes on unusual tags, such as `href` on `<p>`, can be reported separately from unknown attributes.
- Preserved `aria-*`, `data-*`, and common global attributes as accepted on tag-specific checks.
- Expanded common HTML attribute typo suggestions for WordPress-generated media attributes such as `srcset`, `sizes`, `decoding`, and `fetchpriority`.
- Updated README files and dictionary format notes for the tag-specific HTML attribute dictionary.
- Added regressions for unexpected tag/attribute combinations, global/prefixed attributes, and `scrset` -> `srcset` suggestions.

Notes:

- The tag-specific attribute map is intentionally conservative and article-focused to avoid broad false positives.
- Real Gutenberg paste/save acceptance was not performed in this step.

## Step13-section22 Search Replace Focus Verification

Date: 2026-10-05

Changes:

- Confirmed the SearchEngine replacement path still covers literal replacement, regex groups, `$1` / `${name}` compatibility, preview, selected-only, and visible-only flows through existing tests.
- Restored the find-text focus after single Replace and Replace Marked operations, matching the existing Replace All behavior.
- Added GUI-level regressions for Replace, Replace All, and Replace Marked button flows returning focus to the find text box and selecting the current search text.

Notes:

- The checks were performed with Qt offscreen tests, not manual GUI interaction.

## Step13-section23 Linter Error Sample V2 Robustness

Date: 2026-10-05

Changes:

- Fixed JA/EN `invalid_wordpress_block_attributes` translations by escaping the literal `{}` as `{{}}`, preventing Grammar Check dialog crashes during `.format()`.
- Deduplicated unknown HTML tag warnings for the same tag on the same line, so `<pr>...</pr>` reports one `pr` typo instead of separate open/close messages.
- Suppressed WordPress block attribute-vs-HTML consistency checks when the block comment JSON is invalid, avoiding cascade messages such as default heading `level=2` mismatches after malformed JSON.
- Added typo suggestions for unknown WordPress block attributes such as `lebel` -> `level`.
- Added regressions for literal brace formatting, same-line unknown tag deduplication, invalid block JSON cascade suppression, and block-attribute typo suggestions.
- Checked `sample/wp_linter_error_test.wp_html` and `sample/wp_linter_error_test_v2.wp_html` through MainWindow message formatting with Qt offscreen.

Notes:

- `wp_linter_error_test_v2.wp_html` now formats without crashing and produced 63 findings after deduplication and invalid-JSON cascade suppression.
- Manual GUI dialog display with two real tabs was not performed in this step.

## Step13-section24 Per-Tab Grammar Check Result Files

Date: 2026-10-05

Changes:

- Added a small grammar lint result store that writes the current Grammar Check summary, rows, issue lines, document label, and source hash to a per-tab temporary JSON file.
- Associated each open editor tab with its own result file so multi-tab Grammar Check dialogs can switch to the selected tab's latest valid result.
- Invalidated and deleted stale result files when a tab's text changes, preventing old results from being shown after edits.
- Deleted the associated temporary result file when a tab is closed or removed.
- Deleted the temporary Grammar Check result folder when the last RegexPad window closes, so Temp does not retain an empty application namespace.
- Updated the Grammar Check dialog title to include the current document label, making the displayed result's owner visible.
- Updated README.md and README_jp.md with the per-tab Grammar Check result behavior.
- Added regressions for per-tab result separation, tab-switch dialog refresh, issue-line restoration, result-file deletion on tab close, and Temp folder deletion on window close.

Notes:

- Result files are stored under the OS temporary folder and are intended only for the current editing session; the result folder is removed when the final RegexPad window closes.
- The result is reused only when the stored source hash still matches the current tab text.
- Moving a tab to a new window recreates the tab in the destination window and does not preserve the old temporary result file.

## Step13-section25 WordPress Attribute Semantic Lint

Date: 2026-10-05

Changes:

- Added targeted WordPress block attribute semantic checks for JSON that is syntactically valid and uses known attribute names but has suspicious values.
- Warned when `wp:heading` `level` is a string instead of an integer.
- Warned when `wp:paragraph` `dropCap` is a string instead of a boolean.
- Warned when `wp:paragraph` `align` is outside the accepted `left`, `center`, and `right` values, including a `centre` -> `center` suggestion.
- Broadened WordPress block-comment recovery so malformed attribute text, such as `{"level":3}XYZ`, still participates in block start/end structure checks while reporting the JSON error.
- Added JA/EN messages for attribute type and value warnings.
- Updated README.md and README_jp.md with the attribute type/value lint behavior.
- Added regressions for type mismatches, invalid align values, and block-structure recovery after malformed attribute text.

Notes:

- This is intentionally narrow and dictionary-like: it covers the high-value cases from `sample/wp_linter_error_test_v2.wp_html` without attempting full WordPress schema validation.
- Real Gutenberg paste/save acceptance was not performed in this step.

## Step13-section26 Inline HTML Wrap Shortcuts

Date: 2026-10-05

Changes:

- Added editor actions for wrapping the current selection with common inline HTML.
- Added `Ctrl+B` for `<strong>...</strong>`.
- Added `Ctrl+U` for `<u>...</u>`.
- Added `Ctrl+Alt+R` for `<span style="color: red">...</span>`.
- Supported the no-selection case by inserting the tag pair and placing the cursor between the opening and closing tags.
- Added JA/EN action labels and exposed the actions in the Edit menu.
- Updated README.md and README_jp.md with the inline HTML shortcut behavior.
- Added regressions for shortcut assignment, selected-text wrapping, no-selection insertion, cursor placement, and undo.

Notes:

- These shortcuts are intentionally limited to common inline editing helpers and do not replace the existing tag insertion menu.
- Qt offscreen tests covered the action behavior; manual GUI keypress acceptance was not performed.

## Step13-section27 Find/Replace Regex Input Follow-Up Checks

Date: 2026-10-05

Changes in progress:

- Kept the Find/Replace inputs as `RegexInputEdit` (`QPlainTextEdit`) so regex syntax highlighting can continue to work.
- Delayed Find/Replace focus restoration after Replace/Replace All with a 0 ms `QTimer` so Qt can finish the editor update first.
- Restored full selection of the search text after replacement so the next typed search pattern replaces the previous pattern instead of being inserted before it.
- Cleared a full-input selection when the regex input loses focus, keeping the text visible after moving to the replacement box or buttons.
- Added highlighting support for common escaped regex tokens such as `\n` and `\t`.
- Cleared stale preview rows whenever the search text, replacement text, or search options change.
- Made the Find/Replace search and replacement boxes vertically expandable so multi-line patterns can be inspected by resizing the dialog.
- Added regression coverage for second-pass regex input, visible search text after focus movement, second Replace All success, stale preview clearing, and expandable multi-line input boxes.
- 2026-10-06 follow-up: cleared existing editor search markers immediately when a new delayed search-highlight request is scheduled, preventing old markers from appearing to belong to the current search text.
- 2026-10-06 follow-up: added a regex lint warning for an actual `¥` character used where a regex escape backslash was likely intended. This only warns; it does not rewrite the user's pattern.
- 2026-10-06 follow-up: confirmed by command-line GUI simulation that `<!-- /wp:paragraph -->\n<!-- wp:paragraph -->\n` with real half-width backslashes (`U+005C`) matches and the Find button selects a match.
- 2026-10-06 follow-up: changed preview "after replacement" context so repeated matches on the same line show the line after all replacements in that line, avoiding misleading partial previews such as `<h3 ...></h2>`.

Manual verification checklist for the next session:

- Start the app with `D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe main.py`.
- Open Find/Replace and enable regular expression search.
- Test first replacement with a WordPress paragraph-boundary pattern such as `<!-- /wp:paragraph -->\n\n<!-- wp:paragraph -->` and a replacement such as `<br><br>\n`.
- After Replace All, confirm the search box text remains visible when moving focus to the replacement box.
- Type a second pattern, for example `</p>\n<p>`, and confirm it replaces the previous search text rather than being inserted in front of leftover text.
- Confirm matching markers appear for the second pattern before replacement.
- Confirm changing the search text clears old markers immediately; stale markers should not remain while the 250 ms delayed highlight is pending.
- Run Replace All for the second pattern and confirm it no longer reports "no replacements" when matching text exists.
- Confirm the preview table clears when the search text, replacement text, or regex/search options are changed.
- Confirm a simple same-line replacement such as `2` -> `3` on `<h2 class="wp-block-heading"></h2>` previews as `<h3 class="wp-block-heading"></h3>`.
- Resize the Find/Replace dialog vertically and confirm the search and replacement boxes expand enough to inspect multi-line patterns.
- Confirm `\n`, `\t`, and `\d+` are highlighted in the regex input while regex mode is enabled.
- If a pattern visibly uses `¥n`, confirm whether the character is a displayed backslash (`U+005C`) or an actual yen sign (`U+00A5`). Actual `¥` should show a regex-check warning and should not be treated as an escape.
- If manual GUI behavior differs from tests, capture the exact search text with `find_text_edit.text()` before changing code again.

Validation already run:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
```

Result:

- `pytest`: 294 passed
- `ruff check .`: All checks passed
- `pyright`: 0 errors, 0 warnings, 0 informations

Notes:

- The preview table does not write data back into the search or replacement inputs; it only displays rows and a summary.
- The earlier "visible search text but no match" case was caused by leftover previous search text remaining inside the input after `selectAll()` was removed.
- Real manual GUI acceptance on Windows was not completed after the final expandable-input change.

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
