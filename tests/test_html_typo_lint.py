from __future__ import annotations

from unittest.mock import patch

from search.html_typo_lint import lint_html_typos


def test_lint_reports_html_tag_and_attribute_typos() -> None:
    messages = lint_html_typos('<p clas="lead"><spna herf="https://example.com">本文</spna></p>')

    assert any(message.message_key == "html_typo_lint.unknown_html_tag" for message in messages)
    assert any(
        message.message_key == "html_typo_lint.unknown_html_attribute"
        and message.values
        and message.values.get("suggestion") == "class"
        for message in messages
    )
    assert any(
        message.message_key == "html_typo_lint.unknown_html_attribute"
        and message.values
        and message.values.get("suggestion") == "href"
        for message in messages
    )


def test_lint_reports_wordpress_block_typo() -> None:
    messages = lint_html_typos("<!-- wp:paragaph -->\n<p>本文</p>\n<!-- /wp:paragaph -->")

    assert any(
        message.message_key == "html_typo_lint.unknown_wordpress_block"
        and message.values
        and message.values.get("suggestion") == "paragraph"
        for message in messages
    )


def test_lint_reports_wordpress_paragraph_missing_p_open() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "段落分割後にp開始タグが抜けています。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key == "html_typo_lint.wordpress_paragraph_missing_p_open"
        and message.line_number == 1
        for message in messages
    )


def test_lint_reports_wordpress_paragraph_missing_p_close() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>最後のp終了タグが抜けています。\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key == "html_typo_lint.wordpress_paragraph_missing_p_close"
        and message.line_number == 1
        for message in messages
    )


def test_lint_reports_unexpected_wordpress_paragraph_closing_block() -> None:
    messages = lint_html_typos(
        "<!-- /wp:paragraph -->\n"
        "<p>終了コメントから始まっています。</p>\n"
    )

    assert any(
        message.message_key
        == "html_typo_lint.unexpected_wordpress_closing_block"
        and message.line_number == 1
        and message.values
        and message.values.get("block") == "paragraph"
        for message in messages
    )


def test_lint_reports_missing_wordpress_html_closing_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:html -->\n"
        "<div class=\"notice\">閉じ忘れたHTMLブロックです。\n"
        "<!-- wp:paragraph -->\n"
        "<p>この段落が巻き込まれる可能性があります。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key
        == "html_typo_lint.missing_wordpress_html_closing_block"
        and message.line_number == 1
        and message.values
        and message.values.get("block") == "html"
        for message in messages
    )


def test_lint_reports_wordpress_block_comment_inside_html_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:html -->\n"
        "<div>本文</div>\n"
        "<!-- wp:paragraph -->\n"
        "<p>混入した段落です。</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- /wp:html -->"
    )

    assert any(
        message.message_key
        == "html_typo_lint.wordpress_html_contains_block_comment"
        and message.line_number == 3
        for message in messages
    )


def test_lint_reports_div_inside_wordpress_paragraph_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<div>段落ブロック内のdivです。</div>\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key
        == "html_typo_lint.wordpress_paragraph_contains_div"
        and message.line_number == 1
        for message in messages
    )


def test_lint_accepts_valid_wordpress_paragraph_blocks() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>1つ目の段落です。</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- wp:paragraph -->\n"
        "<p>2つ目の段落です。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    structural_keys = {
        "html_typo_lint.wordpress_paragraph_missing_p_open",
        "html_typo_lint.wordpress_paragraph_missing_p_close",
        "html_typo_lint.unexpected_wordpress_closing_block",
        "html_typo_lint.mismatched_wordpress_block",
        "html_typo_lint.missing_wordpress_closing_block",
        "html_typo_lint.missing_wordpress_html_closing_block",
        "html_typo_lint.wordpress_html_contains_block_comment",
        "html_typo_lint.wordpress_paragraph_contains_div",
    }
    assert not any(message.message_key in structural_keys for message in messages)


def test_lint_accepts_reference_json_attribute_prefixes() -> None:
    messages = lint_html_typos('<p data-note-id="1" aria-label="説明">本文</p>')

    assert not any(message.message_key == "html_typo_lint.unknown_html_attribute" for message in messages)


def test_lint_uses_startup_reference_cache_without_rereading_json() -> None:
    with patch("pathlib.Path.read_text") as read_text:
        messages = lint_html_typos('<p clas="lead">本文</p>')

    read_text.assert_not_called()
    assert any(
        message.message_key == "html_typo_lint.unknown_html_attribute"
        and message.values
        and message.values.get("suggestion") == "class"
        for message in messages
    )
