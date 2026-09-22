# Dictionary Format

RegexPad keeps bundled snippet dictionaries in this folder. Bundled dictionaries are read-only during normal use; user dictionaries are loaded from the folder selected in Options.

## Tag Snippet Dictionaries

The following bundled files use the same snippet format:

- `html_dict.json`
- `markdown_dict.json`
- `wordpress_html_dict.json`

Each item is an object with these required fields:

```json
{
  "label_key": "tag.html.paragraph",
  "hint_key": "tag.hint.html.paragraph",
  "template": "<p>{selection}{cursor}</p>"
}
```

- `label_key`: translation key for the visible snippet name.
- `hint_key`: translation key for the hover hint and picker hint.
- `template`: inserted text.
- `parameters`: optional structured metadata for editable values in the snippet.

Supported placeholders:

- `{selection}`: selected text, or empty text when there is no selection.
- `{cursor}`: final cursor position after insertion. Use at most one.

Validation rejects missing required keys, empty required values, duplicate `label_key` values within one dictionary, duplicate `{cursor}` placeholders, broken placeholders, unknown placeholders, and missing Japanese or English translation keys.

Optional `parameters` entries use this minimum format:

```json
{
  "name": "href",
  "required": true,
  "kind": "url",
  "description_key": "tag.parameter.href"
}
```

- `name`: required non-empty identifier for the editable value.
- `required`: optional boolean. Defaults to `false`.
- `kind`: optional non-empty string such as `text`, `url`, `number`, or `choice`. Defaults to `text`.
- `description_key`: optional translation key for future guided editing and lint hints.

Validation rejects non-list `parameters`, non-object parameter entries, empty parameter names, duplicate parameter names within one snippet, non-boolean `required` values, empty `kind` values, non-string `description_key` values, and missing translations for non-empty `description_key` values.

Current policy for user dictionaries:

- User dictionaries use the same `label_key` / `hint_key` format as bundled dictionaries.
- Direct `label` / `hint` text is not accepted yet.
- Direct labels may be reconsidered later for plugin-like dictionaries, but that needs a separate format decision so localization behavior stays predictable.

## Typo Lint Reference

`lint_reference.json` is not a snippet dictionary. It is loaded once at startup into a cache and is used by HTML / WordPress typo linting.

It contains:

- `wordpress_core_blocks`: valid WordPress core block names such as `paragraph`, `group`, and `list-item`.
- `html_tags`: valid HTML tag names.
- `html_attributes`: valid HTML attribute names.
- `allowed_attribute_prefixes`: prefixes such as `aria-` and `data-`.

Add entries here when RegexPad should treat a tag, block, or attribute spelling as valid.
