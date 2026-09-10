from __future__ import annotations

from search.regex_lint import RegexLint


def test_lint_reports_invalid_regex() -> None:
    messages = RegexLint().lint("[")

    assert messages
    assert messages[0].severity == "error"
    assert messages[0].message_key == "regex_lint.invalid_regex"


def test_lint_warns_about_empty_matches() -> None:
    messages = RegexLint().lint(r"\d*")

    assert any(message.message_key == "regex_lint.empty_match" for message in messages)


def test_lint_reports_invalid_replacement_reference() -> None:
    messages = RegexLint().lint(
        r"item-(\d+)",
        r"\2",
        check_replacement=True,
    )

    assert any(message.severity == "error" for message in messages)


def test_lint_warns_about_unescaped_dot() -> None:
    messages = RegexLint().lint("example.com")

    assert any(message.message_key == "regex_lint.unescaped_dot" for message in messages)


def test_lint_warns_about_backslash_n() -> None:
    messages = RegexLint().lint(r"\n{3,}")

    assert any(message.message_key == "regex_lint.backslash_n" for message in messages)
