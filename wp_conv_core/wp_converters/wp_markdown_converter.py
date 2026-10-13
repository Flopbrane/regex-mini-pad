"""Convert selected complex Markdown blocks to WordPress Gutenberg HTML."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from wp_conv_core.wp_blocks.wp_list_block import (
    wp_create_list_block,
    wp_normalize_adjacent_list_blocks,
)
from wp_conv_core.wp_blocks.wp_table import wp_create_table_block_from_rows
from wp_conv_core.wp_dictionaries.wp_markdown_dict import (
    WP_MARKDOWN_ORDERED_LIST_PATTERN,
    WP_MARKDOWN_TABLE_ROW_PATTERN,
    WP_MARKDOWN_TABLE_SEPARATOR_PATTERN,
    WP_MARKDOWN_UNORDERED_LIST_PATTERN,
)

WPComplexMarkdownBlockType = Literal["table", "list"]


@dataclass(frozen=True)
class WPComplexMarkdownBlock:
    """Parsed complex Markdown block."""

    block_type: WPComplexMarkdownBlockType
    lines: list[str]
    ordered: bool = False


class WPComplexMarkdownConversionError(ValueError):
    """Raised when the selection has no supported complex Markdown blocks."""


def wp_convert_complex_markdown_blocks_to_wordpress(markdown_text: str) -> str:
    """Convert Markdown table/list selections to WordPress block HTML."""
    source_text = _wp_normalize_escaped_pipe_table(markdown_text)
    blocks = wp_parse_complex_markdown_blocks(source_text)
    if not blocks:
        raise WPComplexMarkdownConversionError(
            "Markdown table or list block was not found in the selection."
        )

    save_data = "\n\n".join(_wp_render_complex_block(block) for block in blocks)
    return wp_normalize_adjacent_list_blocks(save_data)


def wp_convert_markdown_tables_to_wordpress(markdown_text: str) -> str:
    """Convert only Markdown table blocks in the selection to WordPress HTML."""
    blocks = _wp_supported_blocks_of_type(markdown_text, "table", "Markdown table")
    return "\n\n".join(_wp_render_complex_block(block) for block in blocks)


def wp_convert_markdown_lists_to_wordpress(markdown_text: str) -> str:
    """Convert only Markdown list blocks in the selection to WordPress HTML."""
    blocks = _wp_supported_blocks_of_type(markdown_text, "list", "Markdown list")
    save_data = "\n\n".join(_wp_render_complex_block(block) for block in blocks)
    return wp_normalize_adjacent_list_blocks(save_data)


def wp_parse_complex_markdown_blocks(markdown_text: str) -> list[WPComplexMarkdownBlock]:
    """Parse supported complex Markdown blocks from the selection."""
    blocks: list[WPComplexMarkdownBlock] = []
    table_lines: list[str] = []
    list_items: list[str] = []
    list_ordered = False

    for line in markdown_text.splitlines():
        stripped_line = line.strip()

        if _wp_is_table_row(stripped_line):
            _wp_flush_list_blocks(blocks, list_items, list_ordered)
            list_ordered = False
            table_lines.append(_wp_normalize_escaped_table_delimiters(stripped_line))
            continue

        list_match = _wp_match_list_item(line)
        if list_match is not None:
            _wp_flush_table_blocks(blocks, table_lines)
            item_text, current_ordered = list_match
            if list_items and list_ordered != current_ordered:
                _wp_flush_list_blocks(blocks, list_items, list_ordered)
            list_ordered = current_ordered
            list_items.append(item_text)
            continue

        _wp_flush_table_blocks(blocks, table_lines)
        _wp_flush_list_blocks(blocks, list_items, list_ordered)
        list_ordered = False

    _wp_flush_table_blocks(blocks, table_lines)
    _wp_flush_list_blocks(blocks, list_items, list_ordered)
    return blocks


def _wp_supported_blocks_of_type(
    markdown_text: str,
    block_type: WPComplexMarkdownBlockType,
    description: str,
) -> list[WPComplexMarkdownBlock]:
    source_text = _wp_normalize_escaped_pipe_table(markdown_text)
    blocks = [
        block
        for block in wp_parse_complex_markdown_blocks(source_text)
        if block.block_type == block_type
    ]
    if not blocks:
        raise WPComplexMarkdownConversionError(
            f"{description} block was not found in the selection."
        )
    return blocks


def _wp_render_complex_block(block: WPComplexMarkdownBlock) -> str:
    if block.block_type == "table":
        headers = _wp_split_table_row(block.lines[0])
        rows = [_wp_split_table_row(row) for row in block.lines[2:]]
        headers, rows = _wp_normalize_table_width(headers, rows)
        return wp_create_table_block_from_rows(
            headers,
            rows,
            convert_inline_code=True,
        )
    if block.block_type == "list":
        return wp_create_list_block(
            block.lines,
            ordered=block.ordered,
            convert_inline_code=True,
        )
    raise AssertionError(f"Unsupported block type: {block.block_type}")


def _wp_flush_table_blocks(
    blocks: list[WPComplexMarkdownBlock],
    table_lines: list[str],
) -> None:
    if not table_lines:
        return
    if len(table_lines) >= 2 and WP_MARKDOWN_TABLE_SEPARATOR_PATTERN.match(table_lines[1]):
        blocks.append(WPComplexMarkdownBlock("table", table_lines[:]))
    table_lines.clear()


def _wp_flush_list_blocks(
    blocks: list[WPComplexMarkdownBlock],
    list_items: list[str],
    ordered: bool,
) -> None:
    if list_items:
        blocks.append(WPComplexMarkdownBlock("list", list_items[:], ordered=ordered))
        list_items.clear()


def _wp_is_table_row(stripped_line: str) -> bool:
    return bool(
        WP_MARKDOWN_TABLE_ROW_PATTERN.match(
            _wp_normalize_escaped_table_delimiters(stripped_line)
        )
    )


def _wp_match_list_item(line: str) -> tuple[str, bool] | None:
    ordered_match = WP_MARKDOWN_ORDERED_LIST_PATTERN.match(line)
    if ordered_match is not None:
        return ordered_match.group(1), True
    unordered_match = WP_MARKDOWN_UNORDERED_LIST_PATTERN.match(line)
    if unordered_match is not None:
        return unordered_match.group(1), False
    return None


def _wp_split_table_row(row: str) -> list[str]:
    normalized_row = _wp_normalize_escaped_table_delimiters(row)
    stripped_row = normalized_row.strip()
    stripped_row = stripped_row.removeprefix("|")
    if stripped_row.endswith("|") and not stripped_row.endswith(r"\|"):
        stripped_row = stripped_row[:-1]

    cells: list[str] = []
    current_cell: list[str] = []
    escaped = False
    for character in stripped_row:
        if escaped:
            current_cell.append(character)
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == "|":
            cells.append("".join(current_cell).strip())
            current_cell = []
            continue
        current_cell.append(character)
    if escaped:
        current_cell.append("\\")
    cells.append("".join(current_cell).strip())
    return cells


def _wp_normalize_table_width(
    headers: list[str],
    rows: list[list[str]],
) -> tuple[list[str], list[list[str]]]:
    """Pad simple Markdown tables so all WordPress rows have the same width."""
    column_count = max(
        [len(headers), *(len(row) for row in rows)],
        default=0,
    )
    if column_count == 0:
        return headers, rows
    normalized_headers = [*headers, *([""] * (column_count - len(headers)))]
    normalized_rows = [
        [*row, *([""] * (column_count - len(row)))]
        for row in rows
    ]
    return normalized_headers, normalized_rows


def _wp_normalize_escaped_table_delimiters(markdown_line: str) -> str:
    """Accept web-copied tables where structural pipes are escaped."""
    stripped_line = markdown_line.strip()
    if stripped_line.startswith(r"\|") and stripped_line.endswith(r"\|"):
        return stripped_line.replace(r"\|", "|")
    return markdown_line


def _wp_normalize_escaped_pipe_table(markdown_text: str) -> str:
    return markdown_text.strip()
