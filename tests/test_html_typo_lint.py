from __future__ import annotations

from pathlib import Path
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
        and message.line_number == 2
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
        and message.line_number == 2
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
        and message.line_number == 2
        for message in messages
    )


def test_lint_reports_simple_count_mismatches() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p><pre><code>本文</code></pre>\n"
        "<!-- wp:html -->\n"
        "<div>HTML</div>\n"
    )

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.count_mismatch_wordpress_paragraph" in message_keys
    assert "html_typo_lint.count_mismatch_wordpress_html" in message_keys
    assert "html_typo_lint.count_mismatch_p" in message_keys


def test_lint_reports_pre_and_code_count_mismatches() -> None:
    messages = lint_html_typos("<pre><code>本文</pre>")

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.count_mismatch_code" in message_keys
    assert "html_typo_lint.count_mismatch_pre" not in message_keys


def test_lint_reports_html_tag_closing_order_for_tracked_tags() -> None:
    messages = lint_html_typos("<pre><code>sample</pre></code>")

    assert any(
        message.message_key == "html_typo_lint.mismatched_html_tag"
        and message.line_number == 1
        and message.values == {"open_tag": "code", "close_tag": "pre"}
        for message in messages
    )


def test_lint_reports_unexpected_html_closing_tag_for_tracked_tags() -> None:
    messages = lint_html_typos("<p>text</p>\n</pre>")

    assert any(
        message.message_key == "html_typo_lint.unexpected_html_closing_tag"
        and message.line_number == 2
        and message.values == {"tag": "pre"}
        for message in messages
    )


def test_lint_reports_missing_html_closing_tag_for_tracked_tags() -> None:
    messages = lint_html_typos("<pre><code>sample</code>")

    assert any(
        message.message_key == "html_typo_lint.missing_html_closing_tag"
        and message.line_number == 1
        and message.values == {"tag": "pre"}
        for message in messages
    )


def test_lint_reports_nested_code_and_strong_count_mismatch() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p><code>one <code>two</code></p>\n"
        "<p><strong>strong text</p>\n"
        "<!-- /wp:paragraph -->"
    )

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.nested_html_tag" in message_keys
    assert "html_typo_lint.count_mismatch_code" in message_keys
    assert "html_typo_lint.inline_tag_unclosed_before_parent" in message_keys


def test_lint_reports_inline_tag_unclosed_before_paragraph_close() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>本文です。<br><br>\n"
        "<strong>重要です。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key == "html_typo_lint.inline_tag_unclosed_before_parent"
        and message.line_number == 3
        and message.values == {"tag": "strong", "parent": "p"}
        for message in messages
    )


def test_lint_reports_inline_tag_closing_order() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        '<p><strong><span style="color: red;">重要です。</strong></span></p>\n'
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key == "html_typo_lint.inline_tag_closing_order"
        and message.line_number == 2
        and message.values == {"tag": "span", "closing_tag": "strong"}
        for message in messages
    )


def test_lint_reports_inline_tag_unclosed_at_document_end() -> None:
    messages = lint_html_typos("<p><strong>重要です。")

    assert any(
        message.message_key == "html_typo_lint.inline_tag_unclosed_at_document_end"
        and message.line_number == 1
        and message.values == {"tag": "strong"}
        for message in messages
    )


def test_lint_accepts_escaped_html_inside_wordpress_code_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:code -->\n"
        "<pre class=\"wp-block-code\"><code>&lt;!-- wp:paragraph --&gt;\n"
        "&lt;p&gt;段落は &lt;code&gt;&amp;lt;p&amp;gt;&lt;/code&gt; タグで作ります。&lt;/p&gt;\n"
        "&lt;!-- /wp:paragraph --&gt;</code></pre>\n"
        "<!-- /wp:code -->"
    )

    assert not any(
        message.message_key == "html_typo_lint.escaped_code_close_fragment"
        for message in messages
    )


def test_lint_reports_orphan_empty_paragraph_and_break() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<p></p>\n"
        "<br>\n"
    )

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.empty_paragraph_outside_wordpress_block" in message_keys
    assert "html_typo_lint.break_outside_wordpress_block" in message_keys


def test_lint_reports_separator_code_contamination_and_escaped_code_fragment() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p><code>&lt;!-- wp:paragraph --&gt;/code&gt;</code></p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- wp:separator -->\n"
        '<hr class="wp-block-separator has-alpha-channel-opacity"><code><code>\n'
        "<!-- /wp:separator -->"
    )

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.wordpress_separator_contains_code" in message_keys
    assert "html_typo_lint.escaped_code_close_fragment" in message_keys


def test_lint_suppresses_separator_code_cascade_errors() -> None:
    messages = lint_html_typos(
        "<!-- wp:separator -->\n"
        '<hr class="wp-block-separator has-alpha-channel-opacity"><code><code>\n'
        "<!-- /wp:separator -->\n"
        '<!-- wp:heading {"level":3} -->\n'
        '<h3 class="wp-block-heading">Sub block</h3>\n'
        "<!-- /wp:heading -->"
    )

    message_keys = [message.message_key for message in messages]
    assert message_keys == ["html_typo_lint.wordpress_separator_contains_code"]


def test_lint_reports_duplicate_wordpress_paragraph_opening() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>ただし、制限が強いWordPressでは、埋め込みがうまく残らない場合があります。</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- wp:paragraph -->\n"
        "<p>ただし、制限が強いWordPressでは、埋め込みがうまく残らない時があります。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key == "html_typo_lint.duplicate_wordpress_paragraph"
        and message.values
        and message.values["previous_line"] == "1"
        for message in messages
    )


def test_lint_counts_only_html_tag_tokens_for_code() -> None:
    messages = lint_html_typos(
        "<!--wp:paragraph-->\n"
        "<p>コード表示は <code>code</code> と書きます。</p>\n"
        "<!--/wp:paragraph-->"
    )

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.count_mismatch_code" not in message_keys
    assert "html_typo_lint.count_mismatch_wordpress_paragraph" not in message_keys


def test_lint_counts_ignore_escaped_html_code_examples() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>表示例は <code>&lt;code&gt;本文&lt;/code&gt;</code> です。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    assert not any(
        message.message_key == "html_typo_lint.count_mismatch_code"
        for message in messages
    )


def test_lint_wordpress_mismatch_does_not_consume_valid_open_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:html -->\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key == "html_typo_lint.mismatched_wordpress_block"
        and message.line_number == 3
        and message.values == {"open_block": "paragraph", "close_block": "html"}
        for message in messages
    )
    assert not any(
        message.message_key == "html_typo_lint.missing_wordpress_closing_block"
        and message.values
        and message.values.get("block") == "paragraph"
        for message in messages
    )


def test_lint_reports_real_sample_problem_categories() -> None:
    sample_path = Path("sample/test.wp_html")
    if not sample_path.exists():
        return
    sample_text = sample_path.read_text(encoding="utf-8")

    messages = lint_html_typos(sample_text)

    assert not any(
        message.message_key == "html_typo_lint.escaped_code_close_fragment"
        and message.line_number in {299, 319}
        for message in messages
    )
    if "<strong>ブロックの設定情報です。</p>" in sample_text:
        assert any(
            message.message_key == "html_typo_lint.inline_tag_unclosed_before_parent"
            and message.line_number == 501
            and message.values == {"tag": "strong", "parent": "p"}
            for message in messages
        )


def test_lint_reports_test_sample_without_separator_cascade() -> None:
    sample_path = Path("sample/test_sample.wp_html")
    if not sample_path.exists():
        return
    sample_text = sample_path.read_text(encoding="utf-8")

    messages = lint_html_typos(sample_text)

    assert [
        (message.line_number, message.message_key, message.values)
        for message in messages
    ] == [
        (
            31,
            "html_typo_lint.inline_tag_unclosed_before_parent",
            {"tag": "strong", "parent": "p"},
        ),
        (
            35,
            "html_typo_lint.inline_tag_closing_order",
            {"tag": "span", "closing_tag": "strong"},
        ),
        (
            49,
            "html_typo_lint.inline_tag_unclosed_before_parent",
            {"tag": "a", "parent": "p"},
        ),
        (
            81,
            "html_typo_lint.missing_wordpress_closing_block",
            {"block": "list-item"},
        ),
        (98, "html_typo_lint.escaped_code_close_fragment", None),
        (120, "html_typo_lint.missing_html_closing_tag", {"tag": "div"}),
        (131, "html_typo_lint.wordpress_separator_contains_code", None),
        (
            148,
            "html_typo_lint.inline_tag_unclosed_before_parent",
            {"tag": "span", "parent": "p"},
        ),
    ]


def test_lint_reports_known_fragile_typos() -> None:
    messages = lint_html_typos('<p style="margin:2en 0 1.5em;">本文<\\p>')

    message_keys = {message.message_key for message in messages}
    assert "html_typo_lint.invalid_p_closing_tag" in message_keys
    assert "html_typo_lint.known_typo_margin_2en" in message_keys


def test_lint_reports_html_block_inside_wordpress_paragraph_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:paragraph -->\n"
        "<p>前半\n"
        "<!-- wp:html -->\n"
        "<div>入れ子HTML</div>\n"
        "<!-- /wp:html -->\n"
        "</p>\n"
        "<!-- /wp:paragraph -->"
    )

    assert any(
        message.message_key
        == "html_typo_lint.wordpress_paragraph_contains_html_block"
        and message.line_number == 3
        for message in messages
    )


def test_lint_reports_invalid_wordpress_block_attributes() -> None:
    messages = lint_html_typos(
        '<!-- wp:spacer {"height":"32px",} -->\n'
        '<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>\n'
        "<!-- /wp:spacer -->"
    )

    assert any(
        message.message_key == "html_typo_lint.invalid_wordpress_block_attributes"
        for message in messages
    )


def test_lint_reports_unknown_wordpress_block_attribute() -> None:
    messages = lint_html_typos(
        '<!-- wp:heading {"level":3,"badParam":true} -->\n'
        '<h3 class="wp-block-heading">見出し</h3>\n'
        "<!-- /wp:heading -->"
    )

    assert any(
        message.message_key == "html_typo_lint.unknown_wordpress_block_attribute"
        and message.line_number == 1
        and message.values == {"block": "heading", "attribute": "badParam"}
        for message in messages
    )


def test_lint_accepts_known_wordpress_block_attributes() -> None:
    messages = lint_html_typos(
        '<!-- wp:spacer {"height":"32px","className":"wide"} -->\n'
        '<div style="height:32px" aria-hidden="true" class="wp-block-spacer wide"></div>\n'
        "<!-- /wp:spacer -->"
    )

    assert not any(
        message.message_key == "html_typo_lint.unknown_wordpress_block_attribute"
        for message in messages
    )


def test_lint_reports_unclosed_div_inside_wordpress_html_block() -> None:
    messages = lint_html_typos(
        "<!-- wp:html -->\n"
        '<div class="notice">\n'
        "本文<br>\n"
        "<!-- /wp:html -->"
    )

    assert any(
        message.message_key == "html_typo_lint.missing_html_closing_tag"
        and message.line_number == 2
        and message.values == {"tag": "div"}
        for message in messages
    )


def test_lint_checks_entire_plain_html_file_structure() -> None:
    messages = lint_html_typos(
        '<main><div class="notice">\n'
        "<p>本文</p>\n"
        "</main>"
    )

    assert any(
        message.message_key == "html_typo_lint.mismatched_html_tag"
        and message.line_number == 3
        and message.values == {"open_tag": "div", "close_tag": "main"}
        for message in messages
    )


def test_lint_reports_wordpress_heading_level_html_mismatch() -> None:
    messages = lint_html_typos(
        '<!-- wp:heading {"level":3} -->\n'
        '<h2 class="wp-block-heading">見出し</h2>\n'
        "<!-- /wp:heading -->"
    )

    mismatch = next(
        message
        for message in messages
        if message.message_key
        == "html_typo_lint.wordpress_block_attribute_html_mismatch"
    )
    assert mismatch.values == {
        "block": "heading",
        "attribute": "level",
        "attribute_value": "3",
        "html_value": "h2",
    }


def test_lint_reports_wordpress_spacer_height_html_mismatch() -> None:
    messages = lint_html_typos(
        '<!-- wp:spacer {"height":"64px"} -->\n'
        '<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>\n'
        "<!-- /wp:spacer -->"
    )

    assert any(
        message.message_key
        == "html_typo_lint.wordpress_block_attribute_html_mismatch"
        and message.values
        and message.values["block"] == "spacer"
        for message in messages
    )


def test_lint_reports_wordpress_image_size_html_mismatch() -> None:
    messages = lint_html_typos(
        '<!-- wp:image {"sizeSlug":"large","linkDestination":"none"} -->\n'
        '<figure class="wp-block-image size-full"><img src="sample.jpg" alt="説明"/></figure>\n'
        "<!-- /wp:image -->"
    )

    assert any(
        message.message_key
        == "html_typo_lint.wordpress_block_attribute_html_mismatch"
        and message.values
        and message.values["block"] == "image"
        for message in messages
    )


def test_lint_accepts_matching_wordpress_comment_attributes_and_html() -> None:
    messages = lint_html_typos(
        '<!-- wp:heading {"level":3} -->\n'
        '<h3 class="wp-block-heading">見出し</h3>\n'
        "<!-- /wp:heading -->\n"
        '<!-- wp:spacer {"height":"32px"} -->\n'
        '<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>\n'
        "<!-- /wp:spacer -->\n"
        '<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->\n'
        '<figure class="wp-block-image size-full"><img src="sample.jpg" alt="説明"/></figure>\n'
        "<!-- /wp:image -->"
    )

    assert not any(
        message.message_key
        == "html_typo_lint.wordpress_block_attribute_html_mismatch"
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


def test_lint_warns_about_restricted_html_tags_and_event_attributes() -> None:
    messages = lint_html_typos(
        '<script>alert("x")</script>\n'
        '<iframe src="https://example.com"></iframe>\n'
        '<button type="button" onclick="alert(1)">押す</button>'
    )
    message_keys = [message.message_key for message in messages]

    assert message_keys.count("html_typo_lint.restricted_html_tag") >= 3
    assert "html_typo_lint.restricted_html_attribute" in message_keys
