# FIX_LINTER_STEPS.md

## Purpose

This document records a real WordPress failure case that passed the current RegexPad Grammar Check but required manual repair afterward.

Use the supplied broken/fixed pair as paired regression data:

- Broken / current-linter-pass sample:
  - `～事務職で活かせるおすすめ資格5選～.wp_html`
- Fully repaired sample:
  - `～事務職で活かせるおすすめ資格5選～修正版.wp_html`

The goal is **not** to make the linter reproduce every textual or formatting difference between the two files.

The goal is to identify the structural HTML / WordPress mistakes that were present in the broken file, add focused lint rules for those mistakes, and prove that the repaired file does not trigger the new rules.

---

## Important policy

Treat the two files as a pair:

- `broken` file = positive regression sample
- `fixed` file = negative regression sample

For every newly added rule:

1. Confirm the broken form currently escapes Grammar Check.
2. Add a minimal focused failing test first.
3. Implement the smallest general rule that catches the malformed structure.
4. Confirm the repaired equivalent is accepted.
5. Run the full existing linter test suite.
6. Do not rewrite source text automatically.
7. Do not turn editorial/style differences into lint errors.

The linter should learn from the **structural delta**, not from every diff line.

---

# 1. Primary missed error: HTML attributes written outside the opening tag

## Broken pattern

The broken file repeatedly contains this shape inside `wp:html`:

```html
<!-- wp:html -->
<div>
    style="display:inline-block; border:2px solid #985000; padding:16px;"
>
・内容
</div>
<!-- /wp:html -->
```

The critical problem is:

```html
<div>
```

has already completed the opening tag.

Therefore the following:

```text
style="..."
```

is **not an attribute of the `<div>`**.

It is ordinary text inside the element.

The later standalone:

```text
>
```

is also ordinary text.

This is malformed markup relative to the author's intended HTML and should be reported.

---

## Confirmed occurrences in the broken sample

The broken sample contains this family of error at approximately these original lines:

```text
21
81
108
126
150
210
287
360
429
495
522
```

There are 11 occurrences.

Representative cases follow.

### Case A

```html
<!-- wp:html -->
<div>
    style="display:inline-block; border:2px solid #F2E407; padding:16px; margin:2em 0 2em; border-radius:8px; font-weight: bold ;background-color: #DCFFF2;">
>
・書類作成<br><br>
・数字の管理<br><br>
・情報の整理<br><br>
</div>
<!-- /wp:html -->
```

### Case B

```html
<!-- wp:html -->
<div>
    style="display:inline-block; border:2px solid #985000; padding:16px; margin:2em 0 1.5em; border-radius:8px; font-weight: bold;background-color: #FFF1CF;"
>
・Excelを使ったデータ入力や集計<br><br>
・Wordによる報告書や案内文の作成<br><br>
・PowerPointによる説明資料の作成<br><br>
</div>
<!-- /wp:html -->
```

### Case C

```html
<!-- wp:html -->
<div>
  style="--separator-line-style: solid; --separator-thickness: 4px; --separator-color: #79b7d8; --separator-gradient: linear-gradient(90deg, #79b7d8 0%, #f0b84a 100%); margin: 2em 0; height: var(--separator-thickness); border: 0; border-radius: 999px; background: var(--separator-gradient);"<br><br>
  aria-hidden="true"<br><br>
></div>
<!-- /wp:html -->
```

This case contains two additional symptoms:

- live `<br>` tags appear in what was intended to be an opening-tag attribute list
- `aria-hidden="true"` is also outside the already-closed `<div>` opening tag

---

# 2. Correct repaired form

The repaired file converts the malformed structure to a real opening tag:

```html
<!-- wp:html -->
<div style="display:inline-block;border:2px solid #985000;padding:16px;margin:2em 0 1.5em;border-radius:8px;font-weight:bold;background-color:#FFF1CF">
・内容
</div>
<!-- /wp:html -->
```

The decorative separator is likewise repaired to:

```html
<!-- wp:html -->
<div style="--separator-line-style:solid;--separator-thickness:4px;--separator-color:#79b7d8;--separator-gradient:linear-gradient(90deg,#79b7d8 0%,#f0b84a 100%);margin:2em 0;height:var(--separator-thickness);border:0;border-radius:999px;background:var(--separator-gradient)" aria-hidden="true"></div>
<!-- /wp:html -->
```

Spacing and semicolon normalization are **not** the important part.

The important structural difference is:

```text
BROKEN:
<div>
style="..."
>

FIXED:
<div style="...">
```

---

# 3. Required new lint behavior

## P0-A: orphan HTML attribute syntax after a completed opening tag

Add detection for a known HTML attribute assignment that appears as live text immediately after an element opening tag has already closed.

Example:

```html
<div>
style="..."
```

Expected finding concept:

```text
`style="..."` appears outside the `<div>` opening tag.
Move the attribute before the opening tag's `>`.
```

Suggested internal key:

```text
html_attribute_outside_opening_tag
```

Severity:

```text
warning
```

or `error` if the current lint severity policy considers malformed intended markup an error.

### Attribute candidates

Do not hard-code only `style`.

Reuse existing HTML attribute dictionaries where practical.

At minimum consider:

```text
style
class
id
title
role
href
src
alt
width
height
aria-*
data-*
```

However, avoid warning on normal prose merely containing strings like:

```text
style="color:red"
```

The rule must use surrounding HTML-token context.

---

## P0-B: standalone `>` with no open start-tag context

Broken samples contain:

```html
<div>
style="..."
>
```

The standalone `>` should be suspicious **only if there is no currently unfinished opening tag**.

Suggested internal key:

```text
unexpected_html_tag_close_delimiter
```

Important:

Do **not** reject valid multiline start tags such as:

```html
<div
    style="color:red"
    aria-hidden="true"
>
content
</div>
```

That form is valid and exists as a useful positive control.

Therefore this must be parser-state-aware rather than a broad regular expression such as:

```regex
^\s*>\s*$
```

by itself.

---

## P0-C: HTML tags embedded in an orphan attribute continuation

Example from the broken file:

```html
<div>
  style="..."<br><br>
  aria-hidden="true"<br><br>
></div>
```

Once `<div>` has already ended, these `<br>` tags are parsed as live body tags, even though the text around them clearly resembles an attempted attribute continuation.

Add a focused diagnostic for this malformed continuation pattern.

Suggested key:

```text
malformed_html_attribute_continuation
```

The message should explain the practical repair:

```text
The opening tag appears to have ended before its attributes.
Move style/aria attributes into `<div ...>` and remove the `<br>` tags from the opening-tag declaration.
```

This should not be implemented as a generic ban on `<br>` inside `wp:html`.

`<br>` is valid in normal HTML body content.

---

# 4. WordPress `wp:html` context check

The supplied failures occur inside Custom HTML blocks:

```html
<!-- wp:html -->
...
<!-- /wp:html -->
```

Add a conservative Custom HTML body sanity pass.

A strong suspicious sequence is:

```text
completed opening element
↓
raw text beginning with a known HTML attribute assignment
↓
optional `<br>` tokens
↓
standalone `>`
```

For example:

```html
<div>
style="..."
>
```

or:

```html
<div>
style="..."<br><br>
aria-hidden="true"<br><br>
></div>
```

This should be detected without requiring browser DOM recovery.

Do not attempt to regenerate Gutenberg save output.

---

# 5. Required positive controls

The implementation must preserve these valid forms.

## Valid one-line element

```html
<div style="color:red">text</div>
```

No new lint finding.

## Valid multiline opening tag

```html
<div
    style="color:red"
    aria-hidden="true"
>
text
</div>
```

No new lint finding.

## Normal body `<br>`

```html
<div style="color:red">
line 1<br><br>
line 2
</div>
```

No new lint finding.

## Literal attribute example inside escaped code

```html
<code>&lt;div style="color:red"&gt;</code>
```

No new lint finding.

Also preserve the current rules that exclude escaped display-code regions from live HTML structural checks.

---

# 6. Whole-file paired regression tests

Add a real-sample regression using both supplied files.

Suggested organization:

```text
sample/linter_cases/
└─ qualification_article_20261023/
   ├─ broken.wp_html
   └─ fixed.wp_html
```

If project policy prefers keeping original Japanese names, that is acceptable.

## Broken-file expectation

The broken file must produce one or more findings from the new malformed-opening-tag family.

Prefer asserting:

- the expected diagnostic keys exist
- representative source lines are correct
- all repeated malformed instances are discoverable when practical

Do not make the test depend on the total number of all lint findings in the document unless necessary.

Other linter rules may evolve.

## Fixed-file expectation

The repaired file must produce **zero findings for the new keys**:

```text
html_attribute_outside_opening_tag
unexpected_html_tag_close_delimiter
malformed_html_attribute_continuation
```

Do not require the entire file to have globally zero warnings unless that is already guaranteed by current project policy.

The pair is specifically the oracle for these new structural rules.

---

# 7. Minimal focused regression cases

Add small unit tests in addition to the whole-file pair.

## Test 1: style outside div opener

Input:

```html
<!-- wp:html -->
<div>
style="color:red"
>
text
</div>
<!-- /wp:html -->
```

Expected:

```text
html_attribute_outside_opening_tag
```

and/or the chosen consolidated malformed-opening diagnostic.

---

## Test 2: valid style inside div opener

Input:

```html
<!-- wp:html -->
<div style="color:red">
text
</div>
<!-- /wp:html -->
```

Expected:

```text
no new malformed-opening finding
```

---

## Test 3: valid multiline opening tag

Input:

```html
<!-- wp:html -->
<div
  style="color:red"
  aria-hidden="true"
>
text
</div>
<!-- /wp:html -->
```

Expected:

```text
no new malformed-opening finding
```

This test is especially important because a naive line-based check for `style=` followed by `>` would incorrectly reject valid HTML.

---

## Test 4: broken continuation containing br

Input:

```html
<!-- wp:html -->
<div>
style="color:red"<br><br>
aria-hidden="true"<br><br>
></div>
<!-- /wp:html -->
```

Expected:

```text
malformed_html_attribute_continuation
```

Do not emit a noisy cascade of many secondary warnings if one root-cause diagnostic is sufficient.

---

## Test 5: normal br body content

Input:

```html
<!-- wp:html -->
<div style="color:red">
A<br><br>
B
</div>
<!-- /wp:html -->
```

Expected:

```text
no malformed-opening finding
```

---

# 8. Cascade suppression policy

Prefer one useful root-cause message over many derived messages.

For:

```html
<div>
style="..."<br><br>
aria-hidden="true"<br><br>
></div>
```

A useful result is one or a few repair-oriented findings such as:

```text
Opening `<div>` ended before `style` / `aria-hidden`.
Move those attributes inside `<div ...>`.
```

Avoid flooding the result list with redundant warnings for:

- raw `style` text
- raw `aria-hidden` text
- each `<br>`
- the standalone `>`

unless they represent independent repair actions.

This follows the existing RegexPad policy used for separator cascade suppression.

---

# 9. Do NOT learn these unrelated differences as errors

The repaired document contains many editorial and stylistic changes that are not evidence of malformed source.

Do not create lint errors merely because these differ between the two files.

## WordPress heading attribute normalization

Broken/original examples include:

```html
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">...</h2>
<!-- /wp:heading -->
```

The repaired file may use:

```html
<!-- wp:heading -->
<h2 class="wp-block-heading">...</h2>
<!-- /wp:heading -->
```

Both can be valid.

Do not flag the explicit `level:2` merely because the repaired file removed it.

Likewise, a matching:

```html
<!-- wp:heading {"level":4} -->
<h4 class="wp-block-heading">...</h4>
<!-- /wp:heading -->
```

is not automatically malformed.

Only mismatched block-level/HTML-level values should remain an error.

---

## CSS whitespace / trailing semicolon normalization

Examples:

```html
style="color: #096B35; background-color: #E4FFEB;"
```

versus:

```html
style="color: #096B35;background-color: #E4FFEB"
```

Both are acceptable CSS forms.

Do not lint stylistic spacing as an error.

---

## Content edits

Do not learn wording changes, added underlines, added image blocks, added separators, changed colors, or list wording as structural rules.

Examples include:

- added image block near the article beginning
- extra decorative separator blocks
- wording changes in the IT passport section
- `<u>` emphasis additions
- color changes
- changing some h4 editorial subheadings to h2
- removal of final `<br><br>` inside framed content

These are content/design decisions unless a separate existing rule already applies.

---

# 10. Recommended implementation direction

Use the existing parser/token inventory where possible.

Do not solve this only with broad regex matching.

Recommended state model:

1. Tokenize live HTML while respecting the existing ignored/display-code ranges.
2. Track whether an opening tag is:
   - currently incomplete, or
   - already closed by `>`.
3. When data immediately following a completed opening tag resembles a known HTML attribute assignment, record a suspicious orphan-attribute candidate.
4. If a standalone `>` later appears while no start tag is open, strengthen the candidate into a malformed-opening finding.
5. If `<br>` tokens appear between orphan attribute-looking lines, report the malformed continuation root cause rather than treating the `<br>` itself as forbidden.
6. Preserve source line positions.
7. Keep checks read-only.

The existing HTML attribute dictionaries should be reused for attribute-name recognition where practical.

---

# 11. Suggested user-facing Japanese messages

Examples only; use the project's existing localization style.

## Attribute outside opening tag

```text
`style="..."` が `<div>` の開始タグの外にあります。
属性は `<div style="...">` のように、開始タグの `>` より前へ移動してください。
```

## Stray tag delimiter

```text
対応する未完了の開始タグがない状態で `>` があります。
直前のタグ属性が開始タグの外へ出ていないか確認してください。
```

## Malformed continuation

```text
`<div>` の開始タグが属性より先に閉じています。
`style` や `aria-*` を `<div ...>` 内へ移動し、属性記述中の `<br>` を削除してください。
```

Keep English resources semantically aligned.

---

# 12. Validation requirements

After implementation run at minimum:

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest tests\test_html_typo_lint.py
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_ja.json
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m json.tool resources\app_text_en.json
```

Also run the linter directly on both supplied article files and record:

```text
broken file:
- new malformed-opening diagnostics detected

fixed file:
- no new malformed-opening diagnostics
```

---

# 13. Acceptance criteria

This task is complete when all of the following are true:

- The broken article no longer passes Grammar Check without a structural warning for the malformed `<div>` attribute layout.
- The repaired article does not trigger the new malformed-opening rules.
- Valid one-line and valid multiline opening tags remain accepted.
- Normal `<br>` usage inside element body content remains accepted.
- Escaped code examples remain excluded from live HTML structure checks.
- Existing Step15-section15 regression behavior remains intact.
- Full pytest passes.
- Ruff passes.
- Pyright reports 0 errors.
- JA/EN resource JSON remains valid.
- No automatic source rewriting is introduced.

---

# 14. Future workflow for real WordPress failures

For future production failures, preserve the same paired-data process:

```text
broken.wp_html
fixed.wp_html
note.md
```

`note.md` should record:

```text
Symptom:
What broke in the WordPress preview/public page.

Current RegexPad result:
Whether Grammar Check missed it or produced the wrong warning.

Root cause:
Exact HTML/WP structural reason.

Expected new lint:
What should be detected.

Fixed confirmation:
Whether the repaired file saved/reloaded correctly in the real WordPress environment.
```

Every real failure should first become a regression pair before adding a new broad rule.

This keeps RegexPad's linter practical and prevents speculative rules from creating false positives.
