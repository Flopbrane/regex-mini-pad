"""Bridge selected Markdown text to the embedded WordPress conversion core."""

from __future__ import annotations

from collections.abc import Callable

from wp_conv_core.wp_converters.wp_markdown_converter import (
    WPComplexMarkdownConversionError,
    wp_convert_complex_markdown_blocks_to_wordpress,
    wp_convert_markdown_lists_to_wordpress,
    wp_convert_markdown_tables_to_wordpress,
)


class WordPressMarkdownConversionError(RuntimeError):
    """Raised when the embedded WordPress converter cannot produce output."""


def convert_complex_markdown_blocks_to_wordpress_html(markdown_text: str) -> str:
    """Convert selected Markdown table/list text to WordPress block HTML."""
    return _convert_with_embedded_core(
        wp_convert_complex_markdown_blocks_to_wordpress,
        markdown_text,
    )


def convert_markdown_tables_to_wordpress_html(markdown_text: str) -> str:
    """Convert selected Markdown table text to WordPress table blocks."""
    return _convert_with_embedded_core(
        wp_convert_markdown_tables_to_wordpress,
        markdown_text,
    )


def convert_markdown_lists_to_wordpress_html(markdown_text: str) -> str:
    """Convert selected Markdown list text to WordPress list blocks."""
    return _convert_with_embedded_core(
        wp_convert_markdown_lists_to_wordpress,
        markdown_text,
    )


def _convert_with_embedded_core(
    converter: Callable[[str], str],
    markdown_text: str,
) -> str:
    try:
        return converter(markdown_text)
    except WPComplexMarkdownConversionError as error:
        raise WordPressMarkdownConversionError(str(error)) from error
