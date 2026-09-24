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
    messages.extend(_lint_wordpress_block_typos(load_data))
    messages.extend(_lint_wordpress_block_structure(load_data))
    parser = HtmlTypoLintParser()
    parser.feed(load_data)
    parser.close()
    messages.extend(parser.messages)
    return sorted(messages, key=lambda message: message.line_number)


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
    block_stack: list[tuple[str, int, int]] = []

    for block_match in BLOCK_COMMENT_PATTERN.finditer(load_data):
        is_closing = bool(block_match.group(1))
        block_name = _normalize_block_name(block_match.group(2))
        line_number = _line_number_at(block_match.start(), line_starts)

        if not is_closing:
            if block_stack and block_stack[-1][0] == "html":
                messages.append(
                    HtmlTypoLintMessage(
                        "warning",
                        "html_typo_lint.wordpress_html_contains_block_comment",
                        line_number,
                    )
                )
            block_stack.append((block_name, block_match.end(), line_number))
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

        open_block_name, open_end, open_line_number = block_stack.pop()
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

        if block_name == "paragraph":
            messages.extend(
                _lint_wordpress_paragraph_body(
                    load_data[open_end : block_match.start()],
                    open_line_number,
                )
            )

    for block_name, _open_end, open_line_number in block_stack:
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
