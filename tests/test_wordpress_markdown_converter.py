from __future__ import annotations

import pytest

from editor.wordpress_markdown_converter import (
    WordPressMarkdownConversionError,
    convert_complex_markdown_blocks_to_wordpress_html,
    convert_markdown_lists_to_wordpress_html,
    convert_markdown_tables_to_wordpress_html,
)


def test_convert_complex_markdown_blocks_converts_table() -> None:
    result = convert_complex_markdown_blocks_to_wordpress_html(
        "| Purpose | AI |\n"
        "|---|---|\n"
        "| B-roll | **Runway / Veo / Luma** |"
    )

    assert result.startswith("<!-- wp:table -->")
    assert "<th>Purpose</th><th>AI</th>" in result
    assert "<td>B-roll</td><td><strong>Runway / Veo / Luma</strong></td>" in result
    assert result.endswith("<!-- /wp:table -->")


def test_convert_complex_markdown_blocks_accepts_escaped_pipe_text() -> None:
    result = convert_complex_markdown_blocks_to_wordpress_html(
        r"\| Purpose \| AI \|"
        "\n"
        r"\|---\|---\|"
        "\n"
        r"\| B-roll \| Runway \|"
    )

    assert "<!-- wp:table -->" in result
    assert "<th>Purpose</th><th>AI</th>" in result


def test_convert_markdown_table_keeps_literal_escaped_pipe_in_cell() -> None:
    result = convert_markdown_tables_to_wordpress_html(
        "| Tool | Note |\n"
        "|---|---|\n"
        r"| Runway | speed \| quality |"
    )

    assert "<td>Runway</td><td>speed | quality</td>" in result


def test_convert_markdown_table_pads_short_rows_for_stable_columns() -> None:
    result = convert_markdown_tables_to_wordpress_html(
        "| Purpose | AI | Cost |\n"
        "|---|---|---|\n"
        "| B-roll | Runway |"
    )

    assert "<th>Purpose</th><th>AI</th><th>Cost</th>" in result
    assert "<td>B-roll</td><td>Runway</td><td></td>" in result


def test_convert_markdown_tables_converts_only_table_blocks() -> None:
    result = convert_markdown_tables_to_wordpress_html(
        "| Purpose | AI |\n"
        "|---|---|\n"
        "| B-roll | Runway |\n"
        "\n"
        "- Not converted here"
    )

    assert "<!-- wp:table -->" in result
    assert "<!-- wp:list -->" not in result


def test_convert_complex_markdown_blocks_converts_unordered_list() -> None:
    result = convert_complex_markdown_blocks_to_wordpress_html(
        "- **Runway** for realistic B-roll\n"
        "- `Kling` for short motion clips"
    )

    assert "<!-- wp:list -->" in result
    assert '<ul class="wp-block-list">' in result
    assert "<!-- wp:list-item -->" in result
    assert "<li><strong>Runway</strong> for realistic B-roll</li>" in result
    assert "<li><code>Kling</code> for short motion clips</li>" in result
    assert "<!-- /wp:list -->" in result


def test_convert_markdown_lists_converts_only_list_blocks() -> None:
    result = convert_markdown_lists_to_wordpress_html(
        "| Purpose | AI |\n"
        "|---|---|\n"
        "| B-roll | Runway |\n"
        "\n"
        "- Converted here"
    )

    assert "<!-- wp:table -->" not in result
    assert "<!-- wp:list -->" in result
    assert "<li>Converted here</li>" in result


def test_convert_complex_markdown_blocks_converts_ordered_list() -> None:
    result = convert_complex_markdown_blocks_to_wordpress_html(
        "1. Prepare source\n2. Convert block"
    )

    assert '<!-- wp:list {"ordered":true} -->' in result
    assert '<ol class="wp-block-list">' in result
    assert "<li>Prepare source</li>" in result
    assert "<li>Convert block</li>" in result


def test_convert_complex_markdown_blocks_keeps_table_and_list_blocks() -> None:
    result = convert_complex_markdown_blocks_to_wordpress_html(
        "| Purpose | AI |\n"
        "|---|---|\n"
        "| B-roll | Runway |\n"
        "\n"
        "- First point\n"
        "- Second point"
    )

    assert "<!-- wp:table -->" in result
    assert "<!-- wp:list -->" in result
    assert result.index("<!-- wp:table -->") < result.index("<!-- wp:list -->")


def test_convert_complex_markdown_blocks_rejects_plain_text() -> None:
    with pytest.raises(WordPressMarkdownConversionError, match="Markdown table or list"):
        convert_complex_markdown_blocks_to_wordpress_html("plain text")


def test_convert_markdown_tables_rejects_list_only_selection() -> None:
    with pytest.raises(WordPressMarkdownConversionError, match="Markdown table"):
        convert_markdown_tables_to_wordpress_html("- list only")


def test_convert_markdown_lists_rejects_table_only_selection() -> None:
    with pytest.raises(WordPressMarkdownConversionError, match="Markdown list"):
        convert_markdown_lists_to_wordpress_html("| A | B |\n|---|---|\n| 1 | 2 |")
