from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import get_close_matches
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

LINT_REFERENCE_PATH = Path(__file__).resolve().parent.parent / "dictionaries" / "lint_reference.json"
BLOCK_COMMENT_PATTERN = re.compile(
    r"<!--\s*(/)?\s*wp:([a-zA-Z0-9_/-]+)(?:\s+([^\r\n]*?))?\s*-->",
)
HTML_TAG_TOKEN_PATTERN = re.compile(
    r"<\s*(/)?\s*([A-Za-z][A-Za-z0-9:-]*)(?:\s[^<>]*)?(/)?\s*>",
    re.IGNORECASE,
)

DEFAULT_WORDPRESS_CORE_BLOCKS = {
    "accordion",
    "accordion-heading",
    "accordion-item",
    "accordion-panel",
    "audio",
    "button",
    "buttons",
    "code",
    "column",
    "columns",
    "cover",
    "details",
    "embed",
    "file",
    "gallery",
    "group",
    "heading",
    "html",
    "image",
    "list",
    "list-item",
    "media-text",
    "more",
    "nextpage",
    "paragraph",
    "preformatted",
    "quote",
    "separator",
    "shortcode",
    "spacer",
    "table",
    "verse",
    "video",
}
DEFAULT_HTML_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "ul",
}
DEFAULT_HTML_ATTRIBUTES = {
    "alt",
    "aria-hidden",
    "aria-label",
    "class",
    "controls",
    "datetime",
    "decoding",
    "fetchpriority",
    "height",
    "href",
    "id",
    "loop",
    "muted",
    "open",
    "placeholder",
    "playsinline",
    "poster",
    "preload",
    "rel",
    "role",
    "sizes",
    "src",
    "srcset",
    "style",
    "target",
    "title",
    "type",
    "width",
}
DEFAULT_ALLOWED_ATTRIBUTE_PREFIXES = ("aria-", "data-")
DEFAULT_GLOBAL_HTML_ATTRIBUTES = {
    "aria-hidden",
    "aria-label",
    "class",
    "data",
    "id",
    "lang",
    "role",
    "style",
    "tabindex",
    "title",
}
DEFAULT_HTML_ATTRIBUTES_BY_TAG = {
    "a": {"download", "href", "hreflang", "referrerpolicy", "rel", "target", "type"},
    "audio": {
        "autoplay",
        "controls",
        "loop",
        "muted",
        "preload",
        "src",
    },
    "blockquote": {"cite"},
    "button": {"disabled", "name", "type", "value"},
    "col": {"span"},
    "colgroup": {"span"},
    "code": set(),
    "div": set(),
    "em": set(),
    "figcaption": set(),
    "figure": set(),
    "h1": set(),
    "h2": set(),
    "h3": set(),
    "h4": set(),
    "h5": set(),
    "h6": set(),
    "iframe": {
        "allow",
        "allowfullscreen",
        "height",
        "loading",
        "name",
        "referrerpolicy",
        "src",
        "srcdoc",
        "width",
    },
    "img": {
        "alt",
        "crossorigin",
        "decoding",
        "fetchpriority",
        "height",
        "loading",
        "referrerpolicy",
        "sizes",
        "src",
        "srcset",
        "usemap",
        "width",
    },
    "li": {"value"},
    "ol": {"reversed", "start", "type"},
    "p": set(),
    "q": {"cite"},
    "span": set(),
    "source": {"height", "media", "sizes", "src", "srcset", "type", "width"},
    "strong": set(),
    "td": {"colspan", "headers", "rowspan"},
    "th": {"abbr", "colspan", "headers", "rowspan", "scope"},
    "time": {"datetime"},
    "track": {"default", "kind", "label", "src", "srclang"},
    "video": {
        "autoplay",
        "controls",
        "height",
        "loop",
        "muted",
        "playsinline",
        "poster",
        "preload",
        "src",
        "width",
    },
}
COMMON_HTML_ATTRIBUTE_TYPOS = {
    "calss": "class",
    "clas": "class",
    "decodng": "decoding",
    "fetchprority": "fetchpriority",
    "herf": "href",
    "hrfe": "href",
    "scr": "src",
    "scrset": "srcset",
    "sies": "sizes",
    "sryle": "style",
    "stlye": "style",
    "styel": "style",
    "taget": "target",
    "taret": "target",
    "titel": "title",
}
RESTRICTED_HTML_TAG_REASONS = {
    "script": "arbitrary JavaScript",
    "style": "embedded CSS",
    "iframe": "external embed",
    "object": "external object/embed",
    "embed": "external object/embed",
    "form": "form submission",
    "input": "form control",
    "textarea": "form control",
    "select": "form control",
    "button": "form or script control",
    "canvas": "JavaScript drawing surface",
}
RESTRICTED_HTML_ATTRIBUTE_PREFIXES = ("on",)
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
INLINE_TAGS = {
    "a",
    "b",
    "code",
    "em",
    "i",
    "mark",
    "small",
    "span",
    "strong",
}
INLINE_PARENT_BOUNDARY_TAGS = {
    "blockquote",
    "dd",
    "div",
    "dt",
    "figcaption",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "p",
    "pre",
    "td",
    "th",
}
ESCAPED_FRAGMENT_IGNORED_WORDPRESS_BLOCKS = {"code", "html"}
NON_NESTABLE_WORDPRESS_BLOCKS = {
    "code",
    "heading",
    "html",
    "list-item",
    "paragraph",
    "separator",
    "spacer",
}
STRUCTURAL_HTML_TAGS = {
    "blockquote",
    "article",
    "aside",
    "code",
    "div",
    "footer",
    "figcaption",
    "figure",
    "header",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}
COMMON_WORDPRESS_BLOCK_ATTRIBUTES = {
    "align",
    "anchor",
    "backgroundColor",
    "className",
    "fontSize",
    "gradient",
    "lock",
    "metadata",
    "style",
    "textColor",
}
WORDPRESS_BLOCK_ATTRIBUTE_ALLOWLISTS = {
    "button": COMMON_WORDPRESS_BLOCK_ATTRIBUTES
    | {
        "linkTarget",
        "placeholder",
        "rel",
        "tagName",
        "text",
        "textAlign",
        "title",
        "url",
        "width",
    },
    "heading": COMMON_WORDPRESS_BLOCK_ATTRIBUTES | {"content", "level", "placeholder"},
    "image": COMMON_WORDPRESS_BLOCK_ATTRIBUTES
    | {
        "alt",
        "aspectRatio",
        "caption",
        "height",
        "href",
        "id",
        "linkClass",
        "linkDestination",
        "linkTarget",
        "rel",
        "scale",
        "sizeSlug",
        "title",
        "url",
        "width",
    },
    "list": COMMON_WORDPRESS_BLOCK_ATTRIBUTES | {"ordered", "reversed", "start", "type"},
    "paragraph": COMMON_WORDPRESS_BLOCK_ATTRIBUTES
    | {"content", "direction", "dropCap", "placeholder"},
    "separator": COMMON_WORDPRESS_BLOCK_ATTRIBUTES | {"opacity"},
    "spacer": COMMON_WORDPRESS_BLOCK_ATTRIBUTES | {"height", "width"},
}
WORDPRESS_BLOCK_ATTRIBUTE_TYPE_RULES = {
    ("heading", "level"): "integer",
    ("paragraph", "dropCap"): "boolean",
}
WORDPRESS_BLOCK_ATTRIBUTE_VALUE_RULES = {
    ("paragraph", "align"): {"left", "center", "right"},
}


@dataclass(frozen=True)
class HtmlTypoLintMessage:
    severity: str
    message_key: str
    line_number: int
    values: dict[str, str] | None = None

    @property
    def message(self) -> str:
        if not self.values:
            return self.message_key
        values = ", ".join(self.values.values())
        return f"{self.message_key}: {values}"


@dataclass(frozen=True)
class LintReferenceCache:
    wordpress_core_blocks: set[str]
    wordpress_block_attributes: dict[str, set[str]]
    html_tags: set[str]
    html_attributes: set[str]
    html_attributes_by_tag: dict[str, set[str]]
    global_html_attributes: set[str]
    allowed_attribute_prefixes: tuple[str, ...]


@dataclass(frozen=True)
class _LintToken:
    position: int
    line_number: int
    name: str
    token_type: str


_WordPressBlockStackItem = tuple[str, int, int, dict[str, Any], bool]


def lint_html_typos(load_data: str) -> list[HtmlTypoLintMessage]:
    suppressed_ranges = _contaminated_wordpress_separator_body_ranges(load_data)
    html_lint_data = _mask_ranges(
        load_data,
        suppressed_ranges,
    )
    messages: list[HtmlTypoLintMessage] = []
    messages.extend(_lint_wordpress_simple_structure(html_lint_data))
    messages.extend(_lint_wordpress_block_typos(load_data))
    messages.extend(_lint_wordpress_block_structure(load_data))
    messages.extend(_lint_known_fragile_typos(load_data))
    parser = HtmlTypoLintParser(load_data, suppressed_ranges)
    parser.feed(load_data)
    parser.close()
    messages.extend(parser.messages)
    return sorted(messages, key=lambda message: message.line_number)


def _lint_wordpress_simple_structure(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    wordpress_tokens = _wordpress_block_tokens(load_data)
    html_tokens = _html_tag_tokens(load_data)
    messages.extend(
        _lint_wordpress_block_comment_count(
            wordpress_tokens,
            "paragraph",
            "html_typo_lint.count_mismatch_wordpress_paragraph",
        )
    )
    messages.extend(
        _lint_wordpress_block_comment_count(
            wordpress_tokens,
            "html",
            "html_typo_lint.count_mismatch_wordpress_html",
        )
    )
    messages.extend(
        _lint_html_tag_count(
            html_tokens,
            "p",
            "html_typo_lint.count_mismatch_p",
        )
    )
    messages.extend(
        _lint_html_tag_count(
            html_tokens,
            "pre",
            "html_typo_lint.count_mismatch_pre",
        )
    )
    messages.extend(
        _lint_html_tag_count(
            html_tokens,
            "code",
            "html_typo_lint.count_mismatch_code",
        )
    )
    messages.extend(_lint_non_nestable_html_tag(html_tokens, "code"))
    if not wordpress_tokens:
        messages.extend(_lint_html_tag_structure(html_tokens, STRUCTURAL_HTML_TAGS))
    messages.extend(_lint_orphan_html_lines_outside_wordpress_blocks(load_data))
    return messages


def _lint_wordpress_block_comment_count(
    tokens: list[_LintToken],
    name: str,
    message_key: str,
) -> list[HtmlTypoLintMessage]:
    return _lint_token_count(
        name,
        [token for token in tokens if token.name == name],
        message_key,
    )


def _lint_html_tag_count(
    tokens: list[_LintToken],
    name: str,
    message_key: str,
) -> list[HtmlTypoLintMessage]:
    return _lint_token_count(
        name,
        [token for token in tokens if token.name == name],
        message_key,
    )


def _lint_token_count(
    name: str,
    tokens: list[_LintToken],
    message_key: str,
) -> list[HtmlTypoLintMessage]:
    open_count = sum(1 for token in tokens if token.token_type == "open")
    close_count = sum(1 for token in tokens if token.token_type == "close")
    if open_count == close_count:
        return []

    first_problem_token = _first_count_problem_token(tokens, open_count, close_count)
    return [
        HtmlTypoLintMessage(
            "warning",
            message_key,
            first_problem_token.line_number if first_problem_token else 1,
            {
                "name": name,
                "open_count": str(open_count),
                "close_count": str(close_count),
            },
        )
    ]


def _first_count_problem_token(
    tokens: list[_LintToken],
    open_count: int,
    close_count: int,
) -> _LintToken | None:
    balance = 0
    last_open_token: _LintToken | None = None
    last_close_token: _LintToken | None = None
    for token in sorted(tokens, key=lambda item: item.position):
        if token.token_type == "open":
            if open_count > close_count and balance > 0:
                return token
            balance += 1
            last_open_token = token
        else:
            balance -= 1
            last_close_token = token
        if balance < 0:
            return token
    if open_count > close_count:
        return last_open_token
    return last_close_token


def _lint_non_nestable_html_tag(
    tokens: list[_LintToken],
    name: str,
) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    open_tokens: list[_LintToken] = []
    for token in sorted(tokens, key=lambda item: item.position):
        if token.name != name:
            continue
        if token.token_type == "close":
            if open_tokens:
                open_tokens.pop()
            continue
        if token.token_type != "open":
            continue
        if open_tokens:
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.nested_html_tag",
                    token.line_number,
                    {"tag": name},
                )
            )
            continue
        open_tokens.append(token)
    return messages


def _lint_html_tag_structure(
    tokens: list[_LintToken],
    tag_names: set[str],
) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    open_tokens: list[_LintToken] = []
    for token in sorted(tokens, key=lambda item: item.position):
        if token.name not in tag_names or token.token_type == "self_close":
            continue
        if token.token_type == "open":
            open_tokens.append(token)
            continue

        matching_index = _last_open_html_tag_index(open_tokens, token.name)
        if matching_index is None:
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.unexpected_html_closing_tag",
                    token.line_number,
                    {"tag": token.name},
                )
            )
            continue
        if matching_index != len(open_tokens) - 1:
            expected_token = open_tokens[-1]
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.mismatched_html_tag",
                    token.line_number,
                    {
                        "open_tag": expected_token.name,
                        "close_tag": token.name,
                    },
                )
            )
        del open_tokens[matching_index]

    for token in open_tokens:
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.missing_html_closing_tag",
                token.line_number,
                {"tag": token.name},
            )
        )
    return messages


def _last_open_html_tag_index(
    open_tokens: list[_LintToken],
    tag_name: str,
) -> int | None:
    for index in range(len(open_tokens) - 1, -1, -1):
        if open_tokens[index].name == tag_name:
            return index
    return None


def _lint_orphan_html_lines_outside_wordpress_blocks(
    load_data: str,
) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    block_depth = 0
    for line_number, line in enumerate(load_data.splitlines(), start=1):
        stripped_line = line.strip()
        if block_depth == 0:
            if re.fullmatch(r"<p\s*>\s*</p\s*>", stripped_line, re.IGNORECASE):
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.empty_paragraph_outside_wordpress_block",
                        line_number,
                    )
                )
            if re.fullmatch(r"<br\s*/?\s*>", stripped_line, re.IGNORECASE):
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.break_outside_wordpress_block",
                        line_number,
                    )
                )
        for block_match in BLOCK_COMMENT_PATTERN.finditer(line):
            if block_match.group(1):
                block_depth = max(0, block_depth - 1)
            else:
                block_depth += 1
    return messages


def _lint_known_fragile_typos(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    line_starts = _line_start_positions(load_data)
    ignored_ranges = _wordpress_block_body_ranges(
        load_data,
        ESCAPED_FRAGMENT_IGNORED_WORDPRESS_BLOCKS,
    )
    ordinary_checks = (
        (r"<\\p\s*>", "html_typo_lint.invalid_p_closing_tag"),
        (r"margin\s*:\s*2en\b", "html_typo_lint.known_typo_margin_2en"),
    )
    for pattern, message_key in ordinary_checks:
        for match in re.finditer(pattern, load_data, re.IGNORECASE):
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    message_key,
                    _line_number_at(match.start(), line_starts),
                )
            )
    for match in re.finditer(r"/code&gt;", load_data, re.IGNORECASE):
        if _position_in_ranges(match.start(), ignored_ranges):
            continue
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.escaped_code_close_fragment",
                _line_number_at(match.start(), line_starts),
            )
        )
    return messages


def _wordpress_block_body_ranges(
    load_data: str,
    block_names: set[str],
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    block_stack: list[tuple[str, int]] = []
    for block_match in BLOCK_COMMENT_PATTERN.finditer(load_data):
        is_closing = bool(block_match.group(1))
        block_name = _normalize_block_name(block_match.group(2))
        if not is_closing:
            block_stack.append((block_name, block_match.end()))
            continue
        if not block_stack:
            continue
        open_block_name, open_end = block_stack.pop()
        if open_block_name != block_name:
            continue
        if block_name in block_names:
            ranges.append((open_end, block_match.start()))
    return ranges


def _contaminated_wordpress_separator_body_ranges(load_data: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for start, end in _wordpress_block_body_ranges(load_data, {"separator"}):
        block_body = load_data[start:end]
        if re.search(r"</?code(?:\s|>)", block_body, re.IGNORECASE):
            ranges.append((start, end))
    return ranges


def _mask_ranges(load_data: str, ranges: list[tuple[int, int]]) -> str:
    if not ranges:
        return load_data

    characters = list(load_data)
    for start, end in ranges:
        for index in range(start, end):
            if characters[index] != "\n":
                characters[index] = " "
    return "".join(characters)


def _position_in_ranges(position: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in ranges)


def _wordpress_block_tokens(load_data: str) -> list[_LintToken]:
    line_starts = _line_start_positions(load_data)
    tokens: list[_LintToken] = []
    for block_match in BLOCK_COMMENT_PATTERN.finditer(load_data):
        block_name = _normalize_block_name(block_match.group(2))
        tokens.append(
            _LintToken(
                position=block_match.start(),
                line_number=_line_number_at(block_match.start(), line_starts),
                name=block_name,
                token_type="close" if block_match.group(1) else "open",
            )
        )
    return tokens


def _html_tag_tokens(
    load_data: str,
    line_number_offset: int = 0,
) -> list[_LintToken]:
    collector = _HtmlTagTokenCollector(
        _line_start_positions(load_data),
        line_number_offset,
    )
    collector.feed(load_data)
    collector.close()
    return collector.tokens


def _position_from_parser_pos(
    line_starts: list[int],
    line_number: int,
    column_number: int,
) -> int:
    if line_number <= 0 or line_number > len(line_starts):
        return 0
    return line_starts[line_number - 1] + column_number


def _load_lint_reference() -> dict[str, Any]:
    try:
        data = json.loads(LINT_REFERENCE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _reference_list(
    reference_data: dict[str, Any],
    key: str,
    fallback: list[str],
) -> list[str]:
    values = reference_data.get(key)
    if not isinstance(values, list):
        return fallback

    result = [value.strip().lower() for value in values if isinstance(value, str) and value.strip()]
    if not result:
        return fallback
    return result


def _reference_set(
    reference_data: dict[str, Any],
    key: str,
    fallback: set[str],
) -> set[str]:
    return set(_reference_list(reference_data, key, sorted(fallback)))


def _reference_attribute_map(
    reference_data: dict[str, Any],
    key: str,
    fallback: dict[str, set[str]],
) -> dict[str, set[str]]:
    values = reference_data.get(key)
    if not isinstance(values, dict):
        return fallback

    result: dict[str, set[str]] = {}
    for block_name, attributes in values.items():
        if not isinstance(block_name, str) or not isinstance(attributes, list):
            continue
        clean_block_name = block_name.strip().lower()
        clean_attributes = {
            attribute.strip()
            for attribute in attributes
            if isinstance(attribute, str) and attribute.strip()
        }
        if clean_block_name and clean_attributes:
            result[clean_block_name] = clean_attributes
    return result or fallback


def _reference_string_map(
    reference_data: dict[str, Any],
    key: str,
    fallback: dict[str, set[str]],
) -> dict[str, set[str]]:
    values = reference_data.get(key)
    if not isinstance(values, dict):
        return fallback

    result: dict[str, set[str]] = {}
    for item_name, item_values in values.items():
        if not isinstance(item_name, str) or not isinstance(item_values, list):
            continue
        clean_name = item_name.strip().lower()
        clean_values = {
            value.strip().lower()
            for value in item_values
            if isinstance(value, str) and value.strip()
        }
        if clean_name:
            result[clean_name] = clean_values
    return result or fallback


def _build_lint_reference_cache() -> LintReferenceCache:
    reference_data = _load_lint_reference()
    return LintReferenceCache(
        wordpress_core_blocks=_reference_set(
            reference_data,
            "wordpress_core_blocks",
            DEFAULT_WORDPRESS_CORE_BLOCKS,
        ),
        wordpress_block_attributes=_reference_attribute_map(
            reference_data,
            "wordpress_block_attributes",
            WORDPRESS_BLOCK_ATTRIBUTE_ALLOWLISTS,
        ),
        html_tags=_reference_set(reference_data, "html_tags", DEFAULT_HTML_TAGS),
        html_attributes=_reference_set(
            reference_data,
            "html_attributes",
            DEFAULT_HTML_ATTRIBUTES,
        ),
        html_attributes_by_tag=_reference_string_map(
            reference_data,
            "html_attributes_by_tag",
            DEFAULT_HTML_ATTRIBUTES_BY_TAG,
        ),
        global_html_attributes=_reference_set(
            reference_data,
            "global_html_attributes",
            DEFAULT_GLOBAL_HTML_ATTRIBUTES,
        ),
        allowed_attribute_prefixes=tuple(
            _reference_list(
                reference_data,
                "allowed_attribute_prefixes",
                list(DEFAULT_ALLOWED_ATTRIBUTE_PREFIXES),
            )
        ),
    )


LINT_REFERENCE_CACHE = _build_lint_reference_cache()
KNOWN_WORDPRESS_CORE_BLOCKS = LINT_REFERENCE_CACHE.wordpress_core_blocks
KNOWN_WORDPRESS_BLOCK_ATTRIBUTES = LINT_REFERENCE_CACHE.wordpress_block_attributes
KNOWN_HTML_TAGS = LINT_REFERENCE_CACHE.html_tags
KNOWN_HTML_ATTRIBUTES = LINT_REFERENCE_CACHE.html_attributes
KNOWN_HTML_ATTRIBUTES_BY_TAG = LINT_REFERENCE_CACHE.html_attributes_by_tag
KNOWN_GLOBAL_HTML_ATTRIBUTES = LINT_REFERENCE_CACHE.global_html_attributes
ALLOWED_HTML_ATTRIBUTE_PREFIXES = LINT_REFERENCE_CACHE.allowed_attribute_prefixes


def _lint_wordpress_block_typos(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    for line_number, line in enumerate(load_data.splitlines(), start=1):
        for block_match in BLOCK_COMMENT_PATTERN.finditer(line):
            block_name = _normalize_block_name(block_match.group(2))
            if "/" in block_name or block_name in KNOWN_WORDPRESS_CORE_BLOCKS:
                continue

            suggestion = _find_closest_word(block_name, KNOWN_WORDPRESS_CORE_BLOCKS)
            values = {"block": block_name}
            if suggestion:
                values["suggestion"] = suggestion
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.unknown_wordpress_block",
                    line_number,
                    values,
                )
            )
    return messages


def _lint_wordpress_block_structure(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    line_starts = _line_start_positions(load_data)
    block_stack: list[_WordPressBlockStackItem] = []
    paragraph_prefix_lines: dict[str, int] = {}

    for block_match in BLOCK_COMMENT_PATTERN.finditer(load_data):
        is_closing = bool(block_match.group(1))
        block_name = _normalize_block_name(block_match.group(2))
        line_number = _line_number_at(block_match.start(), line_starts)

        if not is_closing:
            if (
                block_stack
                and block_stack[-1][0] == block_name
                and block_name in NON_NESTABLE_WORDPRESS_BLOCKS
            ):
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.missing_wordpress_closing_block",
                        line_number,
                        {"block": block_name},
                    )
                )
                block_stack.pop()
            block_attributes_valid = True
            block_attributes = _parse_wordpress_block_attributes(block_match.group(3))
            if block_attributes is None:
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.invalid_wordpress_block_attributes",
                        line_number,
                        {"block": block_name},
                    )
                )
                block_attributes_valid = False
                block_attributes = {}
            messages.extend(
                _lint_unknown_wordpress_block_attributes(
                    block_name,
                    block_attributes,
                    line_number,
                )
            )
            messages.extend(
                _lint_wordpress_block_attribute_semantics(
                    block_name,
                    block_attributes,
                    line_number,
                )
            )
            if block_stack and block_stack[-1][0] == "html":
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.wordpress_html_contains_block_comment",
                        line_number,
                    )
                )
            if block_stack and block_stack[-1][0] == "paragraph" and block_name == "html":
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.wordpress_paragraph_contains_html_block",
                        line_number,
                    )
                )
            block_stack.append(
                (
                    block_name,
                    block_match.end(),
                    line_number,
                    block_attributes,
                    block_attributes_valid,
                )
            )
            continue

        if not block_stack:
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.unexpected_wordpress_closing_block",
                    line_number,
                    {"block": block_name},
                )
            )
            continue

        (
            open_block_name,
            open_end,
            open_line_number,
            block_attributes,
            block_attributes_valid,
        ) = block_stack[-1]
        if open_block_name != block_name:
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.mismatched_wordpress_block",
                    line_number,
                    {"open_block": open_block_name, "close_block": block_name},
                )
            )
            matching_index = _last_open_wordpress_block_index(block_stack, block_name)
            if matching_index is None:
                continue
            for unclosed_block in reversed(block_stack[matching_index + 1 :]):
                messages.append(_missing_wordpress_block_message(unclosed_block))
            del block_stack[matching_index:]
            continue

        block_stack.pop()
        block_body = load_data[open_end : block_match.start()]
        body_line_number = _line_number_at(open_end, line_starts)
        if block_name == "paragraph":
            messages.extend(
                _lint_wordpress_paragraph_body(
                    block_body,
                    open_end,
                    line_starts,
                    open_line_number,
                )
            )
            paragraph_key = _paragraph_duplicate_key(block_body)
            if paragraph_key:
                previous_line = paragraph_prefix_lines.get(paragraph_key)
                if previous_line is not None:
                    messages.append(
                        HtmlTypoLintMessage(
                            "warning",
                            "html_typo_lint.duplicate_wordpress_paragraph",
                            open_line_number,
                            {"previous_line": str(previous_line)},
                        )
                    )
                else:
                    paragraph_prefix_lines[paragraph_key] = open_line_number
        if block_name == "separator":
            messages.extend(
                _lint_wordpress_separator_body(
                    block_body,
                    open_end,
                    line_starts,
                    open_line_number,
                )
            )
        if block_name != "separator":
            messages.extend(
                _lint_html_tag_structure(
                    _html_tag_tokens(
                        block_body,
                        line_number_offset=body_line_number - 1,
                    ),
                    STRUCTURAL_HTML_TAGS,
                )
            )
        if block_attributes_valid:
            messages.extend(
                _lint_wordpress_block_attribute_html_consistency(
                    block_name,
                    block_attributes,
                    block_body,
                    open_line_number,
                )
            )

    for block in block_stack:
        messages.append(_missing_wordpress_block_message(block))
    return messages


def _last_open_wordpress_block_index(
    block_stack: list[_WordPressBlockStackItem],
    block_name: str,
) -> int | None:
    for index in range(len(block_stack) - 1, -1, -1):
        if block_stack[index][0] == block_name:
            return index
    return None


def _missing_wordpress_block_message(
    block: _WordPressBlockStackItem,
) -> HtmlTypoLintMessage:
    block_name, _open_end, open_line_number, _block_attributes, _attributes_valid = block
    message_key = "html_typo_lint.missing_wordpress_closing_block"
    if block_name == "html":
        message_key = "html_typo_lint.missing_wordpress_html_closing_block"
    return HtmlTypoLintMessage(
        "warning",
        message_key,
        open_line_number,
        {"block": block_name},
    )


def _parse_wordpress_block_attributes(attributes_text: str | None) -> dict[str, Any] | None:
    if attributes_text is None:
        return {}
    attributes_text = attributes_text.strip()
    if not attributes_text:
        return {}
    try:
        block_attributes = json.loads(attributes_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(block_attributes, dict):
        return None
    return block_attributes


def _lint_unknown_wordpress_block_attributes(
    block_name: str,
    block_attributes: dict[str, Any],
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    allowed_attributes = KNOWN_WORDPRESS_BLOCK_ATTRIBUTES.get(block_name)
    if allowed_attributes is None:
        return []

    messages: list[HtmlTypoLintMessage] = []
    for attribute in block_attributes:
        if attribute in allowed_attributes:
            continue
        values = {"block": block_name, "attribute": attribute}
        suggestion = _find_closest_word(attribute, allowed_attributes)
        if suggestion:
            values["suggestion"] = suggestion
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.unknown_wordpress_block_attribute",
                line_number,
                values,
            )
        )
    return messages


def _lint_wordpress_block_attribute_semantics(
    block_name: str,
    block_attributes: dict[str, Any],
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    allowed_attributes = KNOWN_WORDPRESS_BLOCK_ATTRIBUTES.get(block_name)
    for attribute, value in block_attributes.items():
        if allowed_attributes is not None and attribute not in allowed_attributes:
            continue

        expected_type = WORDPRESS_BLOCK_ATTRIBUTE_TYPE_RULES.get(
            (block_name, attribute)
        )
        if expected_type and not _wordpress_attribute_value_has_type(
            value,
            expected_type,
        ):
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.invalid_wordpress_block_attribute_type",
                    line_number,
                    {
                        "block": block_name,
                        "attribute": attribute,
                        "expected_type": expected_type,
                        "actual_value": _wordpress_attribute_value_text(value),
                    },
                )
            )

        allowed_values = WORDPRESS_BLOCK_ATTRIBUTE_VALUE_RULES.get(
            (block_name, attribute)
        )
        if allowed_values is None:
            continue
        if not isinstance(value, str):
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.invalid_wordpress_block_attribute_type",
                    line_number,
                    {
                        "block": block_name,
                        "attribute": attribute,
                        "expected_type": "string",
                        "actual_value": _wordpress_attribute_value_text(value),
                    },
                )
            )
            continue
        if value in allowed_values:
            continue
        values = {
            "block": block_name,
            "attribute": attribute,
            "allowed_values": ", ".join(sorted(allowed_values)),
            "actual_value": _wordpress_attribute_value_text(value),
        }
        suggestion = _find_closest_word(value, allowed_values)
        if suggestion:
            values["suggestion"] = suggestion
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.invalid_wordpress_block_attribute_value",
                line_number,
                values,
            )
        )
    return messages


def _wordpress_attribute_value_has_type(value: Any, expected_type: str) -> bool:
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "string":
        return isinstance(value, str)
    return True


def _wordpress_attribute_value_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def _lint_wordpress_block_attribute_html_consistency(
    block_name: str,
    block_attributes: dict[str, Any],
    block_body: str,
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    if block_name == "heading":
        return _lint_wordpress_heading_level_consistency(
            block_attributes,
            block_body,
            line_number,
        )
    if block_name == "spacer":
        return _lint_wordpress_spacer_height_consistency(
            block_attributes,
            block_body,
            line_number,
        )
    if block_name == "image":
        return _lint_wordpress_image_size_consistency(
            block_attributes,
            block_body,
            line_number,
        )
    return []


def _lint_wordpress_heading_level_consistency(
    block_attributes: dict[str, Any],
    block_body: str,
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    level = block_attributes.get("level")
    if level is None:
        level = 2
    if not isinstance(level, int) or isinstance(level, bool):
        return []
    heading_match = re.search(r"<h([1-6])(?:\s|>)", block_body, re.IGNORECASE)
    if heading_match is None:
        return []
    html_level = heading_match.group(1)
    if str(level) == html_level:
        return []
    return [
        _wordpress_attribute_html_mismatch_message(
            line_number,
            "heading",
            "level",
            str(level),
            f"h{html_level}",
        )
    ]


def _lint_wordpress_spacer_height_consistency(
    block_attributes: dict[str, Any],
    block_body: str,
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    height = block_attributes.get("height")
    if not isinstance(height, str):
        return []
    height_match = re.search(
        r"\bheight\s*:\s*([^;\"']+)",
        block_body,
        re.IGNORECASE,
    )
    if height_match is None:
        return []
    html_height = _normalize_css_value(height_match.group(1))
    attribute_height = _normalize_css_value(height)
    if attribute_height == html_height:
        return []
    return [
        _wordpress_attribute_html_mismatch_message(
            line_number,
            "spacer",
            "height",
            height,
            height_match.group(1).strip(),
        )
    ]


def _lint_wordpress_image_size_consistency(
    block_attributes: dict[str, Any],
    block_body: str,
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    size_slug = block_attributes.get("sizeSlug")
    if not isinstance(size_slug, str):
        return []
    size_class_match = re.search(
        r'\bclass\s*=\s*["\'][^"\']*\bsize-([a-zA-Z0-9_-]+)\b',
        block_body,
        re.IGNORECASE,
    )
    if size_class_match is None:
        return []
    html_size = size_class_match.group(1)
    if size_slug.lower() == html_size.lower():
        return []
    return [
        _wordpress_attribute_html_mismatch_message(
            line_number,
            "image",
            "sizeSlug",
            size_slug,
            f"size-{html_size}",
        )
    ]


def _wordpress_attribute_html_mismatch_message(
    line_number: int,
    block: str,
    attribute: str,
    attribute_value: str,
    html_value: str,
) -> HtmlTypoLintMessage:
    return HtmlTypoLintMessage(
        "warning",
        "html_typo_lint.wordpress_block_attribute_html_mismatch",
        line_number,
        {
            "block": block,
            "attribute": attribute,
            "attribute_value": attribute_value,
            "html_value": html_value,
        },
    )


def _normalize_css_value(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower())


def _lint_wordpress_paragraph_body(
    block_body: str,
    body_start_position: int,
    line_starts: list[int],
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    p_open_match = re.search(r"<p(?:\s|>)", block_body, re.IGNORECASE)
    p_close_match = re.search(r"</p\s*>", block_body, re.IGNORECASE)
    div_match = re.search(r"<div(?:\s|>)", block_body, re.IGNORECASE)
    if p_open_match is None:
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.wordpress_paragraph_missing_p_open",
                _first_body_content_line_number(
                    block_body,
                    body_start_position,
                    line_starts,
                    line_number,
                ),
            )
        )
    if p_close_match is None:
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.wordpress_paragraph_missing_p_close",
                _match_line_number(
                    p_open_match,
                    body_start_position,
                    line_starts,
                    line_number,
                ),
            )
        )
    if div_match is not None:
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.wordpress_paragraph_contains_div",
                _match_line_number(
                    div_match,
                    body_start_position,
                    line_starts,
                    line_number,
                ),
            )
        )
    return messages


def _lint_wordpress_separator_body(
    block_body: str,
    body_start_position: int,
    line_starts: list[int],
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    code_match = re.search(r"</?code(?:\s|>)", block_body, re.IGNORECASE)
    if code_match is None:
        return []
    return [
        HtmlTypoLintMessage(
            "warning",
            "html_typo_lint.wordpress_separator_contains_code",
            _match_line_number(code_match, body_start_position, line_starts, line_number),
        )
    ]


def _first_body_content_line_number(
    block_body: str,
    body_start_position: int,
    line_starts: list[int],
    fallback_line_number: int,
) -> int:
    content_match = re.search(r"\S", block_body)
    return _match_line_number(
        content_match,
        body_start_position,
        line_starts,
        fallback_line_number,
    )


def _match_line_number(
    match: re.Match[str] | None,
    body_start_position: int,
    line_starts: list[int],
    fallback_line_number: int,
) -> int:
    if match is None:
        return fallback_line_number
    return _line_number_at(body_start_position + match.start(), line_starts)


def _paragraph_duplicate_key(block_body: str) -> str:
    without_comments = BLOCK_COMMENT_PATTERN.sub(" ", block_body)
    without_tags = re.sub(r"<[^<>]+>", " ", without_comments)
    text = unescape(without_tags)
    normalized_text = re.sub(r"\s+", "", text)
    if len(normalized_text) < 30:
        return ""
    return normalized_text[:30]


def _line_start_positions(load_data: str) -> list[int]:
    return [0] + [
        match.end()
        for match in re.finditer(r"\n", load_data)
    ]


def _line_number_at(position: int, line_starts: list[int]) -> int:
    line_number = 1
    for index, line_start in enumerate(line_starts, start=1):
        if line_start > position:
            break
        line_number = index
    return line_number


def _normalize_block_name(block_name: str) -> str:
    clean_block_name = block_name.strip().lower()
    if clean_block_name.startswith("core/"):
        return clean_block_name.removeprefix("core/")
    return clean_block_name


def _find_closest_word(word: str, choices: set[str]) -> str | None:
    matches = get_close_matches(word, sorted(choices), n=1, cutoff=0.72)
    if not matches:
        return None
    return matches[0]


def _is_known_html_attribute(attr_name: str) -> bool:
    if attr_name in KNOWN_HTML_ATTRIBUTES:
        return True
    return any(attr_name.startswith(prefix) for prefix in ALLOWED_HTML_ATTRIBUTE_PREFIXES)


def _is_global_html_attribute(attr_name: str) -> bool:
    if attr_name in KNOWN_GLOBAL_HTML_ATTRIBUTES:
        return True
    return any(attr_name.startswith(prefix) for prefix in ALLOWED_HTML_ATTRIBUTE_PREFIXES)


def _is_wordpress_accordion_toggle_button(tag: str, attrs: dict[str, str]) -> bool:
    if tag != "button" or attrs.get("type", "").lower() != "button":
        return False
    class_names = set(attrs.get("class", "").split())
    return "wp-block-accordion-heading__toggle" in class_names


class HtmlTypoLintParser(HTMLParser):
    def __init__(
        self,
        load_data: str = "",
        suppressed_ranges: list[tuple[int, int]] | None = None,
    ) -> None:
        super().__init__(convert_charrefs=False)
        self.messages: list[HtmlTypoLintMessage] = []
        self.inline_stack: list[tuple[str, int]] = []
        self.line_starts = _line_start_positions(load_data)
        self.suppressed_ranges = suppressed_ranges or []
        self.reported_unknown_html_tags: set[tuple[int, str]] = set()

    def _is_suppressed_inline_position(self) -> bool:
        line_number, column_number = self.getpos()
        return bool(self.suppressed_ranges) and _position_in_ranges(
            _position_from_parser_pos(self.line_starts, line_number, column_number),
            self.suppressed_ranges,
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._lint_tag_and_attrs(tag, attrs)
        if self._is_suppressed_inline_position():
            return
        clean_tag = tag.lower()
        if clean_tag in VOID_TAGS:
            return
        if clean_tag in INLINE_TAGS:
            self.inline_stack.append((clean_tag, self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._lint_tag_and_attrs(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        clean_tag = tag.lower()
        line_number = self.getpos()[0]
        self._lint_unknown_html_tag(clean_tag, line_number)
        if not self._is_suppressed_inline_position():
            self._lint_inline_endtag(clean_tag, line_number)

    def close(self) -> None:
        super().close()
        self._lint_unclosed_inline_tags_at_document_end()

    def _lint_tag_and_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = tag.lower()
        line_number = self.getpos()[0]
        self._lint_unknown_html_tag(clean_tag, line_number)
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        self._lint_restricted_html_tag(clean_tag, attrs_dict, line_number)
        self._lint_unknown_html_attrs(clean_tag, attrs_dict, line_number)
        self._lint_unexpected_html_attrs_for_tag(clean_tag, attrs_dict, line_number)
        self._lint_restricted_html_attrs(clean_tag, attrs_dict, line_number)

    def _lint_inline_endtag(self, tag: str, line_number: int) -> None:
        if tag in INLINE_TAGS:
            self._close_inline_tag(tag, line_number)
            return
        if tag in INLINE_PARENT_BOUNDARY_TAGS:
            self._lint_unclosed_inline_tags_before_parent(tag)

    def _close_inline_tag(self, tag: str, line_number: int) -> None:
        if not self.inline_stack:
            return
        if self.inline_stack[-1][0] == tag:
            self.inline_stack.pop()
            return

        matching_index = next(
            (
                index
                for index in range(len(self.inline_stack) - 1, -1, -1)
                if self.inline_stack[index][0] == tag
            ),
            None,
        )
        if matching_index is None:
            return

        expected_tag = self.inline_stack[-1][0]
        self.messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.inline_tag_closing_order",
                line_number,
                {"tag": expected_tag, "closing_tag": tag},
            )
        )
        del self.inline_stack[matching_index]

    def _lint_unclosed_inline_tags_before_parent(self, parent_tag: str) -> None:
        while self.inline_stack:
            tag, line_number = self.inline_stack.pop()
            self.messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.inline_tag_unclosed_before_parent",
                    line_number,
                    {"tag": tag, "parent": parent_tag},
                )
            )

    def _lint_unclosed_inline_tags_at_document_end(self) -> None:
        while self.inline_stack:
            tag, line_number = self.inline_stack.pop()
            self.messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.inline_tag_unclosed_at_document_end",
                    line_number,
                    {"tag": tag},
                )
            )

    def _lint_unknown_html_tag(self, tag: str, line_number: int) -> None:
        if tag in KNOWN_HTML_TAGS or "-" in tag or ":" in tag:
            return
        report_key = (line_number, tag)
        if report_key in self.reported_unknown_html_tags:
            return
        self.reported_unknown_html_tags.add(report_key)

        suggestion = _find_closest_word(tag, KNOWN_HTML_TAGS)
        values = {"tag": tag}
        if suggestion:
            values["suggestion"] = suggestion
        self.messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.unknown_html_tag",
                line_number,
                values,
            )
        )

    def _lint_restricted_html_tag(
        self,
        tag: str,
        attrs: dict[str, str],
        line_number: int,
    ) -> None:
        reason = RESTRICTED_HTML_TAG_REASONS.get(tag)
        if reason is None:
            return
        if _is_wordpress_accordion_toggle_button(tag, attrs):
            return
        self.messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.restricted_html_tag",
                line_number,
                {"tag": tag, "reason": reason},
            )
        )

    def _lint_unknown_html_attrs(
        self,
        tag: str,
        attrs: dict[str, str],
        line_number: int,
    ) -> None:
        for attr_name, attr_value in attrs.items():
            if _is_known_html_attribute(attr_name):
                continue

            suggestion = COMMON_HTML_ATTRIBUTE_TYPOS.get(attr_name)
            if suggestion is None:
                suggestion = _find_closest_word(attr_name, KNOWN_HTML_ATTRIBUTES)
            values = {"tag": tag, "attribute": attr_name, "value": attr_value}
            if suggestion:
                values["suggestion"] = suggestion
            self.messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.unknown_html_attribute",
                    line_number,
                    values,
                )
            )

    def _lint_unexpected_html_attrs_for_tag(
        self,
        tag: str,
        attrs: dict[str, str],
        line_number: int,
    ) -> None:
        allowed_attributes = KNOWN_HTML_ATTRIBUTES_BY_TAG.get(tag)
        if allowed_attributes is None:
            return

        for attr_name in attrs:
            if not _is_known_html_attribute(attr_name):
                continue
            if _is_global_html_attribute(attr_name):
                continue
            if attr_name in allowed_attributes:
                continue
            self.messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.unexpected_html_attribute_for_tag",
                    line_number,
                    {"tag": tag, "attribute": attr_name},
                )
            )

    def _lint_restricted_html_attrs(
        self,
        tag: str,
        attrs: dict[str, str],
        line_number: int,
    ) -> None:
        for attr_name in attrs:
            if not attr_name.startswith(RESTRICTED_HTML_ATTRIBUTE_PREFIXES):
                continue
            self.messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.restricted_html_attribute",
                    line_number,
                    {
                        "tag": tag,
                        "attribute": attr_name,
                        "reason": "inline JavaScript event handler",
                    },
                )
            )


class _HtmlTagTokenCollector(HTMLParser):
    def __init__(self, line_starts: list[int], line_number_offset: int = 0) -> None:
        super().__init__(convert_charrefs=False)
        self.line_starts = line_starts
        self.line_number_offset = line_number_offset
        self.tokens: list[_LintToken] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._append_token(tag, "open")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._append_token(tag, "self_close")

    def handle_endtag(self, tag: str) -> None:
        self._append_token(tag, "close")

    def _append_token(self, tag: str, token_type: str) -> None:
        line_number, column_number = self.getpos()
        self.tokens.append(
            _LintToken(
                position=_position_from_parser_pos(
                    self.line_starts,
                    line_number,
                    column_number,
                ),
                line_number=line_number + self.line_number_offset,
                name=tag.lower(),
                token_type=token_type,
            )
        )
