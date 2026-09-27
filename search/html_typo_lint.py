from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import get_close_matches
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

LINT_REFERENCE_PATH = Path(__file__).resolve().parent.parent / "dictionaries" / "lint_reference.json"
BLOCK_COMMENT_PATTERN = re.compile(
    r"<!--\s*(/)?wp:([a-zA-Z0-9_/-]+)(?:\s+(\{.*?\}))?\s*-->",
)

DEFAULT_WORDPRESS_CORE_BLOCKS = {
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
    "height",
    "href",
    "id",
    "rel",
    "src",
    "style",
    "target",
    "title",
    "type",
    "width",
}
DEFAULT_ALLOWED_ATTRIBUTE_PREFIXES = ("aria-", "data-")
COMMON_HTML_ATTRIBUTE_TYPOS = {
    "calss": "class",
    "clas": "class",
    "herf": "href",
    "hrfe": "href",
    "scr": "src",
    "sryle": "style",
    "stlye": "style",
    "styel": "style",
    "taget": "target",
    "taret": "target",
    "titel": "title",
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
    html_tags: set[str]
    html_attributes: set[str]
    allowed_attribute_prefixes: tuple[str, ...]


def lint_html_typos(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    messages.extend(_lint_wordpress_simple_structure(load_data))
    messages.extend(_lint_wordpress_block_typos(load_data))
    messages.extend(_lint_wordpress_block_structure(load_data))
    parser = HtmlTypoLintParser()
    parser.feed(load_data)
    parser.close()
    messages.extend(parser.messages)
    return sorted(messages, key=lambda message: message.line_number)


def _lint_wordpress_simple_structure(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    messages.extend(
        _lint_matching_count(
            load_data,
            "paragraph",
            r"<!--\s+wp:paragraph\s+-->",
            r"<!--\s+/wp:paragraph\s+-->",
            "html_typo_lint.count_mismatch_wordpress_paragraph",
        )
    )
    messages.extend(
        _lint_matching_count(
            load_data,
            "html",
            r"<!--\s+wp:html\s+-->",
            r"<!--\s+/wp:html\s+-->",
            "html_typo_lint.count_mismatch_wordpress_html",
        )
    )
    messages.extend(
        _lint_matching_count(
            load_data,
            "p",
            r"<p(?:\s|>)",
            r"</p\s*>",
            "html_typo_lint.count_mismatch_p",
        )
    )
    messages.extend(
        _lint_matching_count(
            load_data,
            "pre",
            r"<pre(?:\s|>)",
            r"</pre\s*>",
            "html_typo_lint.count_mismatch_pre",
        )
    )
    messages.extend(
        _lint_matching_count(
            load_data,
            "code",
            r"<code(?:\s|>)",
            r"</code\s*>",
            "html_typo_lint.count_mismatch_code",
        )
    )
    messages.extend(_lint_known_fragile_typos(load_data))
    return messages


def _lint_matching_count(
    load_data: str,
    name: str,
    open_pattern: str,
    close_pattern: str,
    message_key: str,
) -> list[HtmlTypoLintMessage]:
    open_matches = list(re.finditer(open_pattern, load_data, re.IGNORECASE))
    close_matches = list(re.finditer(close_pattern, load_data, re.IGNORECASE))
    if len(open_matches) == len(close_matches):
        return []

    first_problem_position = _first_count_problem_position(open_matches, close_matches)
    return [
        HtmlTypoLintMessage(
            "warning",
            message_key,
            _line_number_at(first_problem_position, _line_start_positions(load_data)),
            {
                "name": name,
                "open_count": str(len(open_matches)),
                "close_count": str(len(close_matches)),
            },
        )
    ]


def _first_count_problem_position(
    open_matches: list[re.Match[str]],
    close_matches: list[re.Match[str]],
) -> int:
    all_matches = sorted(
        [(match.start(), "open") for match in open_matches]
        + [(match.start(), "close") for match in close_matches]
    )
    balance = 0
    for position, match_type in all_matches:
        if match_type == "open":
            balance += 1
        else:
            balance -= 1
        if balance < 0:
            return position
    if len(open_matches) > len(close_matches) and open_matches:
        return open_matches[-1].start()
    if close_matches:
        return close_matches[-1].start()
    return 0


def _lint_known_fragile_typos(load_data: str) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    line_starts = _line_start_positions(load_data)
    typo_checks = (
        (r"<\\p\s*>", "html_typo_lint.invalid_p_closing_tag"),
        (r"margin\s*:\s*2en\b", "html_typo_lint.known_typo_margin_2en"),
    )
    for pattern, message_key in typo_checks:
        for match in re.finditer(pattern, load_data, re.IGNORECASE):
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    message_key,
                    _line_number_at(match.start(), line_starts),
                )
            )
    return messages


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


def _build_lint_reference_cache() -> LintReferenceCache:
    reference_data = _load_lint_reference()
    return LintReferenceCache(
        wordpress_core_blocks=_reference_set(
            reference_data,
            "wordpress_core_blocks",
            DEFAULT_WORDPRESS_CORE_BLOCKS,
        ),
        html_tags=_reference_set(reference_data, "html_tags", DEFAULT_HTML_TAGS),
        html_attributes=_reference_set(
            reference_data,
            "html_attributes",
            DEFAULT_HTML_ATTRIBUTES,
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
KNOWN_HTML_TAGS = LINT_REFERENCE_CACHE.html_tags
KNOWN_HTML_ATTRIBUTES = LINT_REFERENCE_CACHE.html_attributes
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
    block_stack: list[tuple[str, int, int, dict[str, Any]]] = []

    for block_match in BLOCK_COMMENT_PATTERN.finditer(load_data):
        is_closing = bool(block_match.group(1))
        block_name = _normalize_block_name(block_match.group(2))
        line_number = _line_number_at(block_match.start(), line_starts)

        if not is_closing:
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
                block_attributes = {}
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
                (block_name, block_match.end(), line_number, block_attributes)
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

        open_block_name, open_end, open_line_number, block_attributes = block_stack.pop()
        if open_block_name != block_name:
            messages.append(
                HtmlTypoLintMessage(
                    "warning",
                    "html_typo_lint.mismatched_wordpress_block",
                    line_number,
                    {"open_block": open_block_name, "close_block": block_name},
                )
            )
            continue

        block_body = load_data[open_end : block_match.start()]
        if block_name == "paragraph":
            messages.extend(
                _lint_wordpress_paragraph_body(
                    block_body,
                    open_line_number,
                )
            )
        messages.extend(
            _lint_wordpress_block_attribute_html_consistency(
                block_name,
                block_attributes,
                block_body,
                open_line_number,
            )
        )

    for block_name, _open_end, open_line_number, _block_attributes in block_stack:
        message_key = "html_typo_lint.missing_wordpress_closing_block"
        if block_name == "html":
            message_key = "html_typo_lint.missing_wordpress_html_closing_block"
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                message_key,
                open_line_number,
                {"block": block_name},
            )
        )
    return messages


def _parse_wordpress_block_attributes(attributes_text: str | None) -> dict[str, Any] | None:
    if attributes_text is None:
        return {}
    try:
        block_attributes = json.loads(attributes_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(block_attributes, dict):
        return None
    return block_attributes


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
    line_number: int,
) -> list[HtmlTypoLintMessage]:
    messages: list[HtmlTypoLintMessage] = []
    if not re.search(r"<p(?:\s|>)", block_body, re.IGNORECASE):
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.wordpress_paragraph_missing_p_open",
                line_number,
            )
        )
    if not re.search(r"</p\s*>", block_body, re.IGNORECASE):
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.wordpress_paragraph_missing_p_close",
                line_number,
            )
        )
    if re.search(r"<div(?:\s|>)", block_body, re.IGNORECASE):
        messages.append(
            HtmlTypoLintMessage(
                "warning",
                "html_typo_lint.wordpress_paragraph_contains_div",
                line_number,
            )
        )
    return messages


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


class HtmlTypoLintParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.messages: list[HtmlTypoLintMessage] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._lint_tag_and_attrs(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._lint_tag_and_attrs(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        clean_tag = tag.lower()
        line_number = self.getpos()[0]
        self._lint_unknown_html_tag(clean_tag, line_number)

    def _lint_tag_and_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = tag.lower()
        line_number = self.getpos()[0]
        self._lint_unknown_html_tag(clean_tag, line_number)
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        self._lint_unknown_html_attrs(clean_tag, attrs_dict, line_number)

    def _lint_unknown_html_tag(self, tag: str, line_number: int) -> None:
        if tag in KNOWN_HTML_TAGS or "-" in tag or ":" in tag:
            return

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
