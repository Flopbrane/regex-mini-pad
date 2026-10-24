# Mini Editor

Mini Editor is a lightweight portable text editor for Windows 11.

The project focuses on practical regular expression search and replacement without requiring an installer, administrator privileges, registry changes, or online services.

## Search exclusions

The Find / Replace dialog has an **Exclude** field. Search results that overlap
an exclusion match are skipped by Find, Previous, highlights, previews, Replace,
Replace All, and Replace Marked. Leave it empty to disable exclusions.
The inputs appear in this order: Find text, Exclude, Replace with.

With regular expressions enabled, search for `\n` and set Exclude to
`<br><br>\n|>\n` to skip newlines immediately after those tags. Use `|` for
alternatives; a leading `-` has no special meaning. For CRLF text, use `\r?\n`
in both patterns. Without regex mode, Exclude is one literal string. Regex and
case sensitivity follow the search checkboxes; whole-word matching applies only
to the search pattern. Exclusions protect matching characters, rather than entire
lines; zero-width exclusion matches protect no characters. For selected/visible
searches, exclusion patterns are evaluated inside that search scope. Inputs stay
in the dialog for the current session and are not saved across restarts.

## WordPress Preview (normal)

- Choose **View > WordPress Preview (normal)** or press **Ctrl+Alt+P**. The current
  unsaved editor contents are rendered by real WordPress and its standard theme,
  then opened in the default browser. Run the action again after editing to update
  the preview. Source files and editor text are not rewritten.
- First use prepares an optional environment under `runtime/wordpress-preview/`.
  It downloads official WordPress core and WordPress Playground PHP.wasm packages
  (Playground 3.1.60 / PHP 8.3). A preinstalled WordPress, PHP server or MySQL is
  unnecessary. Compatible Node.js (24.18+) is reused; on Windows, when Node/npm is
  unavailable, a portable Node LTS distribution is downloaded and verified against
  the official SHA-256 list. No global install or administrator rights are used.
- Initial preparation needs internet access. Cached standard rendering works
  locally afterwards; externally hosted article images still need access to their
  URLs. This machine's optional environment occupies about 126 MB with existing
  Node.js; a portable Node download and extraction add about 138 MB in the tested
  Windows configuration. These optional runtime files are excluded from normal
  Git tracking and PyInstaller JSON collection.
- The local server binds only to `127.0.0.1` and rejects HTTP writes. Article
  updates reach it through the editor's private process input. The preview post
  and SQLite database exist only in the process's virtual filesystem; nothing is
  published to a real site. The preview uses standard WordPress demo data, not a
  production site's theme, plugins or database.
  External API/oEmbed processing on the PHP side is outside this first offline
  baseline; browser-loaded remote images need connectivity.
- WordPress front-end execution feedback appears separately in Grammar Check.
  A successful render is not HTML validation: the qualification-article regression
  renders with HTTP 200 and no PHP warnings on both sides, while the existing
  structural linter still correctly identifies 11 problems on the broken side.
  This does not run Gutenberg editor `save()` validation.
- **View > Stop WordPress Preview** stops the local environment. Closing the editor
  also stops its own preview process. A browser tab left open after stopping will
  no longer refresh. Startup/preparation runs in the background.
- Optional real-engine verification (may prepare the runtime):
  `D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe -m preview.verify_wordpress_preview`.
  This checks dynamic block rendering, real-article feedback, loopback restrictions
  and shutdown; ordinary pytest does not download WordPress.

Official references: [WordPress Playground](https://developer.wordpress.org/playground/developers/local-development/),
[WordPress rendering](https://developer.wordpress.org/reference/functions/do_blocks/).

### Building with the WordPress environment

Run `./build.ps1` in PowerShell. The default build prepares the preview environment
and a portable Node even if the build machine already has Node, then includes them
under `dist/regex-pad/_internal/runtime/wordpress-preview/`. The EXE uses this
bundled environment directly, so recipients do not need WordPress, PHP, MySQL,
Node, or first-use downloads for standard local rendering. Distribute the entire
`dist/regex-pad/` folder, including `_internal`, rather than the EXE alone.

The bundle contains WordPress with its standard theme, PHP.wasm dependencies,
SQLite integration, Node, and their license files. Download caches, setup logs,
Node ZIP archives and Node's npm tooling are excluded. First build preparation
needs internet access; subsequent builds reuse the prepared files. Build failure
is reported if required runtime data is missing or the bundled Node cannot run.

For a smaller distribution retaining first-use setup, run
`./build.ps1 -SkipWordPressRuntime`. A direct `.spec` build requires a prepared
runtime; use `python -m preview.package_runtime` with the specified interpreter
first. For direct `.spec` lightweight builds only, set
`REGEXPAD_SKIP_WORDPRESS_RUNTIME=1`. Build-time preparation uses the normal source
`runtime/wordpress-preview/` folder and does not change global Node/npm settings.

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
- Detects known attributes accidentally written as body text after a completed
  opening tag, such as `<div>` followed by `style="..."` and another `>`.
  Attribute-like multiline continuations and a standalone `>` immediately after
  an opener are checked using parser context. Live `<br>` tokens inside an
  attribute continuation produce one repair-oriented warning instead of a cascade.
  Valid multiline opening tags, ordinary body breaks, comments, display-code
  regions and ordinary prose are preserved; Grammar Check never rewrites the source.
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
