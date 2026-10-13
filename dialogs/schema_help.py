from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HelpTopic = tuple[str, str]

_TEXT = {
    "en": {
        "html_title": "HTML Tag / Attribute Table",
        "html_intro": (
            "This table is generated from `html_tag_schema.json`. "
            "Global attributes and `aria-` / `data-` attributes may be used in "
            "addition to the tag-specific attributes shown below."
        ),
        "tag_attributes": "Tag-Specific Attributes",
        "global_attributes": "Global Attributes",
        "tag": "Tag",
        "attribute": "Attribute",
        "rule": "Type / Allowed Values",
        "required": "Required",
        "yes": "Yes",
        "no": "No",
        "none": "None",
        "void_tags": "Void tags",
        "prefixes": "Additional allowed prefixes",
        "css_title": "CSS Property Table",
        "css_intro": (
            "This table is generated from `standard_css.json` and is also used "
            "by CSS syntax checks for HTML style attributes and .css files."
        ),
        "properties": "Properties",
        "property": "Property",
        "known_typos": "Known Typo Corrections",
        "incorrect": "Incorrect",
        "correction": "Correction",
        "units": "Units",
        "category": "Category",
        "values": "Values",
        "wp_title": "WordPress Block JSON Table",
        "wp_intro": (
            "This initial table is generated from `wordpress_block_schema.json`. "
            "It lists known block attributes and their value constraints. Some "
            "content attributes are read from saved HTML rather than written in "
            "the block-comment JSON, so also check the saved markup."
        ),
        "block_attributes": "Block Attributes",
        "shared_attributes": "Shared Attribute Candidates",
        "block": "Block",
        "coverage": "Coverage",
        "load_error": "The schema table could not be loaded",
    },
    "ja": {
        "html_title": "HTMLタグ・属性表",
        "html_intro": (
            "この表は `html_tag_schema.json` から自動生成しています。"
            "タグ固有属性に加えて、グローバル属性と `aria-` / `data-` 属性を使用できます。"
        ),
        "tag_attributes": "タグ固有属性",
        "global_attributes": "グローバル属性",
        "tag": "タグ",
        "attribute": "属性",
        "rule": "型・使用可能な値",
        "required": "必須",
        "yes": "はい",
        "no": "いいえ",
        "none": "なし",
        "void_tags": "終了タグを持たないタグ",
        "prefixes": "追加で使用可能な接頭辞",
        "css_title": "CSSプロパティ表",
        "css_intro": (
            "この表は `standard_css.json` から自動生成しています。"
            "HTMLのstyle属性と.cssファイルのCSS文法チェックでも同じ辞書を使用します。"
        ),
        "properties": "プロパティ",
        "property": "プロパティ",
        "known_typos": "既知のTypo修正候補",
        "incorrect": "誤りの候補",
        "correction": "修正候補",
        "units": "単位",
        "category": "分類",
        "values": "値",
        "wp_title": "WordPressブロックJSON表",
        "wp_intro": (
            "この初期表は `wordpress_block_schema.json` から自動生成しています。"
            "既知のブロック属性と値の制約を確認できます。contentなど、ブロックコメントの"
            "JSONではなく保存HTMLから読み取られる属性もあるため、保存HTMLとの整合性も確認してください。"
        ),
        "block_attributes": "ブロック固有属性",
        "shared_attributes": "共有属性候補",
        "block": "ブロック",
        "coverage": "収録範囲",
        "load_error": "スキーマ表を読み込めませんでした",
    },
}


def load_schema_help_topics(
    standards_path: Path,
    language_code: str,
) -> tuple[HelpTopic, HelpTopic, HelpTopic]:
    """Build separate HTML, CSS, and WordPress topics from bundled schemas."""
    language = "en" if language_code == "en" else "ja"
    html_topic = _load_topic(
        standards_path / "html_tag_schema.json",
        language,
        "html",
    )
    css_topic = _load_topic(
        standards_path / "standard_css.json",
        language,
        "css",
    )
    wordpress_topic = _load_topic(
        standards_path / "wordpress_block_schema.json",
        language,
        "wordpress",
    )
    return html_topic, css_topic, wordpress_topic


def _load_topic(
    load_file_path: Path,
    language: str,
    schema_kind: str,
) -> HelpTopic:
    text = _TEXT[language]
    title_keys = {
        "html": "html_title",
        "css": "css_title",
        "wordpress": "wp_title",
    }
    title = text[title_keys[schema_kind]]
    try:
        load_data: Any = json.loads(load_file_path.read_text(encoding="utf-8"))
        if not isinstance(load_data, dict):
            raise TypeError("schema root must be an object")
        if schema_kind == "html":
            return title, _build_html_topic(load_data, language)
        if schema_kind == "css":
            return title, _build_css_topic(load_data, language)
        return title, _build_wordpress_topic(load_data, language)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        return title, f"# {title}\n\n{text['load_error']}: `{error}`"


def _build_html_topic(schema: dict[str, Any], language: str) -> str:
    text = _TEXT[language]
    lines = [
        f"# {text['html_title']}",
        "",
        text["html_intro"],
        "",
        f"## {text['tag_attributes']}",
        "",
        _table_header(
            text["tag"],
            text["attribute"],
            text["rule"],
            text["required"],
        ),
    ]
    tags = _require_dict(schema, "tags")
    for tag_name in sorted(tags):
        tag_data = _as_dict(tags[tag_name])
        attributes = _as_dict(tag_data.get("attributes", {}))
        required_attributes = set(_as_list(tag_data.get("required_attributes", [])))
        if not attributes:
            lines.append(
                _table_row(
                    _code(f"<{tag_name}>"),
                    text["none"],
                    "-",
                    text["no"],
                )
            )
            continue
        for attribute_name in sorted(attributes):
            attribute_data = _as_dict(attributes[attribute_name])
            lines.append(
                _table_row(
                    _code(f"<{tag_name}>"),
                    _code(attribute_name),
                    _format_rule(attribute_data),
                    text["yes"] if attribute_name in required_attributes else text["no"],
                )
            )

    lines.extend(
        [
            "",
            f"## {text['global_attributes']}",
            "",
            _table_header(text["attribute"], text["rule"]),
        ]
    )
    global_attributes = _require_dict(schema, "global_attributes")
    for attribute_name in sorted(global_attributes):
        lines.append(
            _table_row(
                _code(attribute_name),
                _format_rule(_as_dict(global_attributes[attribute_name])),
            )
        )

    void_tags = ", ".join(_code(tag) for tag in _as_list(schema.get("void_tags", [])))
    prefixes = ", ".join(
        _code(prefix) for prefix in _as_list(schema.get("allowed_attribute_prefixes", []))
    )
    lines.extend(
        [
            "",
            f"- {text['void_tags']}: {void_tags or '-'}",
            f"- {text['prefixes']}: {prefixes or '-'}",
        ]
    )
    return "\n".join(lines)


def _build_css_topic(schema: dict[str, Any], language: str) -> str:
    text = _TEXT[language]
    lines = [
        f"# {text['css_title']}",
        "",
        text["css_intro"],
        "",
        f"## {text['properties']}",
        "",
        _table_header(text["property"], text["rule"]),
    ]
    properties = _require_dict(schema, "properties")
    for property_name in sorted(properties):
        lines.append(
            _table_row(
                _code(property_name),
                _format_rule(_as_dict(properties[property_name])),
            )
        )

    known_typos = _require_dict(schema, "known_typos")
    lines.extend(
        [
            "",
            f"## {text['known_typos']}",
            "",
            _table_header(text["category"], text["incorrect"], text["correction"]),
        ]
    )
    for typo_category in ("property_names", "units"):
        typo_items = _as_dict(known_typos.get(typo_category, {}))
        for incorrect, correction in sorted(typo_items.items()):
            lines.append(
                _table_row(
                    _code(typo_category),
                    _code(str(incorrect)),
                    _code(str(correction)),
                )
            )

    lines.extend(
        [
            "",
            f"## {text['units']}",
            "",
            _table_header(text["category"], text["values"]),
        ]
    )
    units = _require_dict(schema, "units")
    for unit_category in sorted(units):
        unit_values = ", ".join(_code(str(value)) for value in _as_list(units[unit_category]))
        lines.append(_table_row(_code(unit_category), unit_values))
    return "\n".join(lines)


def _build_wordpress_topic(schema: dict[str, Any], language: str) -> str:
    text = _TEXT[language]
    coverage = str(schema.get("coverage", "-"))
    lines = [
        f"# {text['wp_title']}",
        "",
        text["wp_intro"],
        "",
        f"- {text['coverage']}: `{_escape_cell(coverage)}`",
        "",
        f"## {text['block_attributes']}",
        "",
        _table_header(text["block"], text["attribute"], text["rule"]),
    ]
    blocks = _require_dict(schema, "blocks")
    for block_name in sorted(blocks):
        block_data = _as_dict(blocks[block_name])
        attributes = _as_dict(block_data.get("attributes", {}))
        if not attributes:
            lines.append(_table_row(_code(f"core/{block_name}"), text["none"], "-"))
            continue
        for attribute_name in sorted(attributes):
            lines.append(
                _table_row(
                    _code(f"core/{block_name}"),
                    _code(attribute_name),
                    _format_rule(_as_dict(attributes[attribute_name])),
                )
            )

    lines.extend(
        [
            "",
            f"## {text['shared_attributes']}",
            "",
            _table_header(text["attribute"], text["rule"]),
        ]
    )
    shared_attributes = _require_dict(schema, "shared_attributes")
    for attribute_name in sorted(shared_attributes):
        lines.append(
            _table_row(
                _code(attribute_name),
                _format_rule(_as_dict(shared_attributes[attribute_name])),
            )
        )
    return "\n".join(lines)


def _format_rule(rule: dict[str, Any]) -> str:
    raw_types = rule.get("type", "unknown")
    type_names = raw_types if isinstance(raw_types, list) else [raw_types]
    parts = [" / ".join(_code(str(type_name)) for type_name in type_names)]

    enum_values = rule.get("enum", rule.get("values", rule.get("keywords")))
    if isinstance(enum_values, list) and enum_values:
        parts.append(" / ".join(_code(str(value)) for value in enum_values))
    if "minimum" in rule:
        parts.append(f">= {_code(str(rule['minimum']))}")
    if "maximum" in rule:
        parts.append(f"<= {_code(str(rule['maximum']))}")
    if "item_type" in rule:
        parts.append(f"items: {_code(str(rule['item_type']))}")
    if "value_type" in rule:
        parts.append(f"value: {_code(str(rule['value_type']))}")
    if "default" in rule:
        parts.append(f"default: {_code(str(rule['default']))}")
    if rule.get("allow_empty") is True:
        parts.append("empty: OK")
    return "; ".join(parts)


def _table_header(*labels: str) -> str:
    return "\n".join(
        (
            _table_row(*labels),
            _table_row(*("---" for _label in labels)),
        )
    )


def _table_row(*values: str) -> str:
    return "| " + " | ".join(_escape_cell(value) for value in values) + " |"


def _code(value: str) -> str:
    return f"`{value.replace('`', '\\`')}`"


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def _require_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data[key]
    if not isinstance(value, dict):
        raise TypeError(f"{key} must be an object")
    return value


def _as_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("schema entry must be an object")
    return value


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError("schema entry must be an array")
    return value
