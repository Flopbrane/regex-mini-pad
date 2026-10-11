"""Inline Markdown formatting helpers for WordPress block output."""

from __future__ import annotations

import re
from html import escape

WP_MARKDOWN_LINK_PATTERN: re.Pattern[str] = re.compile(
    r"\[([^\]]+)\]\((https?://[^\s)]+)\)"
)
WP_URL_PATTERN: re.Pattern[str] = re.compile(r"(?<![\"'=])\bhttps?://[^\s<]+")
WP_BOLD_PATTERN: re.Pattern[str] = re.compile(r"\*\*(.+?)\*\*")
WP_ITALIC_PATTERN: re.Pattern[str] = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
WP_INLINE_CODE_PATTERN: re.Pattern[str] = re.compile(r"`([^`\n]+)`")


def wp_format_inline_text(
    text: str,
    line_break_html: str = "<br>",
    convert_inline_code: bool = False,
) -> str:
    """Escape text and convert safe inline Markdown patterns to HTML."""
    parts: list[str] = []
    current_position = 0

    for link_match in WP_MARKDOWN_LINK_PATTERN.finditer(text):
        parts.append(
            _wp_escape_and_link_urls(
                text[current_position : link_match.start()],
                convert_inline_code=convert_inline_code,
            )
        )
        parts.append(_wp_create_link_html(link_match.group(1), link_match.group(2)))
        current_position = link_match.end()

    parts.append(
        _wp_escape_and_link_urls(
            text[current_position:],
            convert_inline_code=convert_inline_code,
        )
    )
    safe_text = "".join(parts)
    return line_break_html.join(safe_text.splitlines())


def _wp_escape_and_link_urls(text: str, convert_inline_code: bool = False) -> str:
    safe_text = escape(text)
    safe_text = _wp_format_emphasis(safe_text, convert_inline_code=convert_inline_code)
    return WP_URL_PATTERN.sub(
        lambda match: _wp_create_link_html(match.group(0), match.group(0)),
        safe_text,
    )


def _wp_create_link_html(label: str, url: str) -> str:
    safe_label = escape(label.strip())
    safe_url = escape(url.strip(), quote=True)
    return f'<a href="{safe_url}">{safe_label}</a>'


def _wp_format_emphasis(text: str, convert_inline_code: bool = False) -> str:
    if convert_inline_code:
        text = WP_INLINE_CODE_PATTERN.sub(_wp_replace_backticks_with_code_tag, text)
    text = WP_BOLD_PATTERN.sub(r"<strong>\1</strong>", text)
    return WP_ITALIC_PATTERN.sub(r"<em>\1</em>", text)


def _wp_replace_backticks_with_code_tag(code_match: re.Match[str]) -> str:
    return f"<code>{code_match.group(1)}</code>"

