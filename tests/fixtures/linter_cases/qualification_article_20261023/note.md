# Qualification article: attributes outside completed opening tags

Date: 2026-10-23

## Symptom and provenance

The user supplied an article that passed RegexPad Grammar Check but required
manual WordPress HTML repair, together with the official repaired article and
`D:\PC\Python\regex_pad_project\FIX_LINTER_STEPS.md` as implementation guidance.

- `broken.wp_html` is a byte-for-byte copy of
  `test_sample/～事務職で活かせるおすすめ資格5選～.wp_html`.
- `fixed.wp_html` is a byte-for-byte copy of
  `test_sample/～事務職で活かせるおすすめ資格5選～修正版.wp_html`.
- Original files remain untouched. These fixtures are self-contained test inputs,
  independent of the user's ignored `test_sample` directory.

## Current RegexPad result before this repair

Direct `lint_html_typos` runs returned zero findings for both original files.
The focused test-first reproduction produced 58 failures and 176 passing tests.

## Root cause

Eleven `<div>` opening tags were already closed before `style="..."` appeared
as body text. An additional raw `>` and, in three cases, live `<br>` tokens
completed an apparent attempted attribute continuation. Valid paired tag counts
did not detect this authoring mistake.

Broken opening-tag lines: 21, 81, 108, 126, 150, 210, 287, 360, 429, 495, 522.
New root-cause warning lines (first orphan attribute):
22, 82, 109, 127, 151, 211, 288, 361, 430, 496, 523.

## Expected new lint

- `html_attribute_outside_opening_tag`: eight article occurrences.
- `malformed_html_attribute_continuation`: three article occurrences, on lines
  109, 127 and 523; consolidated instead of warning separately on every attribute,
  `<br>`, and delimiter.
- `unexpected_html_tag_close_delimiter`: covered by an independent focused case
  of a standalone `>` immediately after a completed opening tag. The article's
  delimiters are covered by the attribute root cause and produce no extra warning.
- The fixed article must have zero findings for this family. Tests assert the
  family rather than a global warning total that unrelated rules may change.

## Fixed confirmation and limits

The fixed file is the user's official repaired source. Its WordPress save/reload
or public-page rendering was not independently exercised in this task.
The rules do not regenerate Gutenberg HTML, infer editorial/style changes, or
rewrite source. Valid multiline start tags, quoted `>` values, normal body `<br>`
tags, code/display regions, comments, and ordinary prose are negative controls.
