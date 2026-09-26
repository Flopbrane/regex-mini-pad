# pylint: disable=C0114,C0115,C0116
from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

PARAGRAPH_BLOCK_PATTERN = re.compile(
    r"<!--\s+wp:paragraph\s+-->(.*?)<!--\s+/wp:paragraph\s+-->",
    re.DOTALL | re.IGNORECASE,
)
PARAGRAPH_TAG_PATTERN = re.compile(
    r"<p\b[^>]*>(.*?)</p>",
    re.DOTALL | re.IGNORECASE,
)
LEADING_BREAK_PATTERN = re.compile(r"^(?:\s*<br\s*/?>\s*)+", re.IGNORECASE)
TRAILING_BREAK_PATTERN = re.compile(r"(?:\s*<br\s*/?>\s*)+$", re.IGNORECASE)


class ParagraphSplitError(ValueError):
    """Raised when paragraph splitting cannot be safely applied."""


@dataclass(frozen=True)
class ParagraphBlock:
    block_start: int
    block_end: int
    content_start: int
    content_end: int


@dataclass(frozen=True)
class ParagraphReplacement:
    text: str
    cursor_position: int


@dataclass(frozen=True)
class _BuiltBlock:
    text: str
    cursor_offset: int


def find_current_paragraph_block(text: str, cursor_pos: int) -> ParagraphBlock | None:
    """Return the wp:paragraph block containing cursor_pos, if it is simple."""
    for match in PARAGRAPH_BLOCK_PATTERN.finditer(text):
        block_start = match.start()
        block_end = match.end()
        if not block_start <= cursor_pos <= block_end:
            continue

        paragraph_match = PARAGRAPH_TAG_PATTERN.search(match.group(0))
        if paragraph_match is None:
            return None

        return ParagraphBlock(
            block_start=block_start,
            block_end=block_end,
            content_start=block_start + paragraph_match.start(1),
            content_end=block_start + paragraph_match.end(1),
        )
    return None


def build_paragraph_block(content: str) -> str:
    """Build a WordPress paragraph block, or an empty string for empty content."""
    clean_content = _clean_paragraph_edge_breaks(content)
    if not clean_content:
        return ""
    return (
        "<!-- wp:paragraph -->\n"
        f"<p>{clean_content}</p>\n"
        "<!-- /wp:paragraph -->"
    )


def build_spacer_block(height: int = 32) -> str:
    return (
        f'<!-- wp:spacer {{"height":"{height}px"}} -->\n'
        f'<div style="height:{height}px" aria-hidden="true" '
        'class="wp-block-spacer"></div>\n'
        "<!-- /wp:spacer -->"
    )


def build_html_code_block(content: str = "") -> str:
    escaped_content = escape(_code_text_from_paragraph_content(content), quote=False)
    code_text = escaped_content if escaped_content else "\n"
    block_text = (
        "<!-- wp:html -->\n"
        "<pre\n"
        '    class="wp-block-code"\n'
        '    style="display:inline-block; border:1px solid #999; padding:16px; '
        'border-radius:8px; background-color:#f9f9f9;"\n'
        f"><code>{code_text}</code></pre>\n"
        "<!-- /wp:html -->"
    )
    return block_text


def build_decorated_block(content: str = "") -> str:
    body = _decorated_text_from_paragraph_content(content)
    if not body:
        body = "ここに本文を入れます。"
    return (
        "<!-- wp:html -->\n"
        "<div\n"
        '    style="display:inline-block; border:1px solid #999; padding:16px; '
        'margin:2em 0 1.5em; border-radius:8px; background-color:#f9f9f9;"\n'
        ">\n"
        f"{body}\n"
        "</div>\n"
        "<!-- /wp:html -->"
    )


def split_paragraph_insert_spacer(text: str, cursor_pos: int) -> ParagraphReplacement:
    return _replace_current_paragraph_selection(
        text,
        cursor_pos,
        cursor_pos,
        _BuiltBlock(build_spacer_block(), len(build_spacer_block())),
    )


def split_paragraph_insert_html(text: str, cursor_pos: int) -> ParagraphReplacement:
    html_block = build_html_code_block()
    cursor_offset = html_block.index("<code>\n") + len("<code>\n")
    return _replace_current_paragraph_selection(
        text,
        cursor_pos,
        cursor_pos,
        _BuiltBlock(html_block, cursor_offset),
    )


def wrap_selection_as_code_block(
    text: str,
    selection_start: int,
    selection_end: int,
) -> ParagraphReplacement:
    selected_text = _selected_text(text, selection_start, selection_end)
    html_block = build_html_code_block(selected_text)
    cursor_offset = html_block.index("</code>")
    return _replace_current_paragraph_selection(
        text,
        selection_start,
        selection_end,
        _BuiltBlock(html_block, cursor_offset),
    )


def wrap_selection_as_decorated_block(
    text: str,
    selection_start: int,
    selection_end: int,
) -> ParagraphReplacement:
    selected_text = _selected_text(text, selection_start, selection_end)
    decorated_block = build_decorated_block(selected_text)
    cursor_offset = decorated_block.index("</div>")
    return _replace_current_paragraph_selection(
        text,
        selection_start,
        selection_end,
        _BuiltBlock(decorated_block, cursor_offset),
    )


def _replace_current_paragraph_selection(
    text: str,
    selection_start: int,
    selection_end: int,
    inserted_block: _BuiltBlock,
) -> ParagraphReplacement:
    start = min(selection_start, selection_end)
    end = max(selection_start, selection_end)
    block = _paragraph_block_for_range(text, start, end)
    before_content = text[block.content_start:start]
    after_content = text[end:block.content_end]
    before_block = build_paragraph_block(before_content)
    after_block = build_paragraph_block(after_content)
    replacement_text, cursor_offset = _join_split_blocks(
        before_block,
        inserted_block,
        after_block,
    )
    new_text = text[: block.block_start] + replacement_text + text[block.block_end :]
    return ParagraphReplacement(
        text=new_text,
        cursor_position=block.block_start + cursor_offset,
    )


def _paragraph_block_for_range(text: str, start: int, end: int) -> ParagraphBlock:
    block = find_current_paragraph_block(text, start)
    if block is None:
        raise ParagraphSplitError("現在の位置では段落分割できません。")

    check_pos = max(start, end - 1)
    end_block = find_current_paragraph_block(text, check_pos)
    if end_block != block:
        raise ParagraphSplitError(
            "選択範囲が複数ブロックにまたがっているため、処理を中止しました。"
        )

    if start < block.content_start or end > block.content_end:
        raise ParagraphSplitError("現在の位置では段落分割できません。")
    return block


def _join_split_blocks(
    before_block: str,
    inserted_block: _BuiltBlock,
    after_block: str,
) -> tuple[str, int]:
    pieces: list[tuple[str, int | None]] = []
    if before_block:
        pieces.append((before_block, None))
    pieces.append((inserted_block.text, inserted_block.cursor_offset))
    if after_block:
        pieces.append((after_block, None))

    replacement_text = ""
    cursor_offset = 0
    for index, (piece, piece_cursor_offset) in enumerate(pieces):
        if index > 0:
            replacement_text += "\n\n"
        if piece_cursor_offset is not None:
            cursor_offset = len(replacement_text) + piece_cursor_offset
        replacement_text += piece
    return replacement_text, cursor_offset


def _selected_text(text: str, selection_start: int, selection_end: int) -> str:
    start = min(selection_start, selection_end)
    end = max(selection_start, selection_end)
    return text[start:end]


def _clean_paragraph_edge_breaks(content: str) -> str:
    clean_content = content.strip()
    previous = None
    while clean_content != previous:
        previous = clean_content
        clean_content = LEADING_BREAK_PATTERN.sub("", clean_content).strip()
        clean_content = TRAILING_BREAK_PATTERN.sub("", clean_content).strip()
    return clean_content


def _code_text_from_paragraph_content(content: str) -> str:
    clean_content = _clean_paragraph_edge_breaks(content)
    return re.sub(r"\s*<br\s*/?>\s*", "\n", clean_content, flags=re.IGNORECASE).strip()


def _decorated_text_from_paragraph_content(content: str) -> str:
    code_text = _code_text_from_paragraph_content(content)
    if not code_text:
        return ""
    lines = [line.strip() for line in code_text.splitlines()]
    return "<br>\n".join(line for line in lines if line)
