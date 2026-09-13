from __future__ import annotations

import re

import pytest

from search.search_engine import SearchEngine, SearchOptions


def test_find_all_returns_literal_matches() -> None:
    engine = SearchEngine()

    matches = engine.find_all("Alpha alpha beta", "alpha")

    assert [(match.start, match.end, match.text) for match in matches] == [
        (0, 5, "Alpha"),
        (6, 11, "alpha"),
    ]


def test_find_all_supports_regular_expressions() -> None:
    engine = SearchEngine()

    matches = engine.find_all(
        "item-01 item-20",
        r"item-\d+",
        SearchOptions(regular_expression=True),
    )

    assert [match.text for match in matches] == ["item-01", "item-20"]


def test_find_all_can_be_case_sensitive() -> None:
    engine = SearchEngine()

    matches = engine.find_all(
        "Alpha alpha",
        "alpha",
        SearchOptions(case_sensitive=True),
    )

    assert [match.text for match in matches] == ["alpha"]


def test_find_all_can_match_whole_words() -> None:
    engine = SearchEngine()

    matches = engine.find_all(
        "cat catalog cat",
        "cat",
        SearchOptions(whole_word=True),
    )

    assert [(match.start, match.end) for match in matches] == [(0, 3), (12, 15)]


def test_find_next_wraps_to_the_beginning() -> None:
    engine = SearchEngine()

    match = engine.find_next("abc abc", "abc", 5)

    assert match is not None
    assert (match.start, match.end, match.text) == (0, 3, "abc")


def test_find_previous_wraps_to_the_end() -> None:
    engine = SearchEngine()

    match = engine.find_previous("abc abc", "abc", 0)

    assert match is not None
    assert (match.start, match.end, match.text) == (4, 7, "abc")


def test_replace_all_supports_regex_groups() -> None:
    engine = SearchEngine()

    result = engine.replace_all(
        "item-01 item-20",
        r"(\w+)-(\d+)",
        r"\2:\1",
        SearchOptions(regular_expression=True),
    )

    assert result.text == "01:item 20:item"
    assert result.count == 2


def test_replace_all_supports_literal_search_text() -> None:
    engine = SearchEngine()

    result = engine.replace_all(
        "a.b a-b",
        "a.b",
        "dot",
    )

    assert result.text == "dot a-b"
    assert result.count == 1


def test_regex_line_end_matches_each_line() -> None:
    engine = SearchEngine()

    result = engine.replace_all(
        "first  \nsecond\t\nthird",
        r"[ \t]+$",
        "",
        SearchOptions(regular_expression=True),
    )

    assert result.text == "first\nsecond\nthird"
    assert result.count == 2


def test_preview_replacement_returns_single_match_result() -> None:
    engine = SearchEngine()

    result = engine.preview_replacement(
        "2026-09-11",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"\1/\2/\3",
        SearchOptions(regular_expression=True),
    )

    assert result.text == "2026/09/11"
    assert result.count == 1


def test_invalid_replacement_reference_is_reported() -> None:
    engine = SearchEngine()

    with pytest.raises(re.error):
        engine.replace_all(
            "item-01",
            r"item-(\d+)",
            r"\2",
            SearchOptions(regular_expression=True),
        )


def test_invalid_regular_expression_is_reported() -> None:
    engine = SearchEngine()

    with pytest.raises(re.error):
        engine.find_all(
            "source text",
            r"[",
            SearchOptions(regular_expression=True),
        )
