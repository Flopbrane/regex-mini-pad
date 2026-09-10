from __future__ import annotations

from search.regex_lint import RegexLint


def test_lint_reports_invalid_regex() -> None:
    messages = RegexLint().lint("[")

    assert messages
    assert messages[0].severity == "error"
    assert "Invalid regular expression" in messages[0].message


def test_lint_warns_about_empty_matches() -> None:
    messages = RegexLint().lint(r"\d*")

    assert any("empty text" in message.message for message in messages)


def test_lint_reports_invalid_replacement_reference() -> None:
    messages = RegexLint().lint(
        r"item-(\d+)",
        r"\2",
        check_replacement=True,
    )

    assert any(message.severity == "error" for message in messages)
