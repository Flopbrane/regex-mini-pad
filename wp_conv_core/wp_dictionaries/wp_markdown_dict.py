"""Markdown rule patterns for the embedded WordPress conversion core."""

from __future__ import annotations

import re

WP_MARKDOWN_TABLE_ROW_PATTERN: re.Pattern[str] = re.compile(r"^\s*\|(.+)\|\s*$")
WP_MARKDOWN_TABLE_SEPARATOR_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\|?[\s:-]+\|[\s|:-]+\|?\s*$"
)
WP_MARKDOWN_UNORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\s*[-*]\s+(.+)$")
WP_MARKDOWN_ORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\s*\d+[.)]\s+(.+)$")

