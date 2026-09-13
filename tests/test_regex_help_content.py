from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_KEYS = {
    "category",
    "label",
    "pattern",
    "description",
    "example_text",
    "usage_example",
    "matches",
    "replace_with",
    "replacement_result",
}


def load_help_items(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_english_and_japanese_help_have_matching_structure() -> None:
    english_items = load_help_items(Path("resources/regex_help_en.json"))
    japanese_items = load_help_items(Path("resources/regex_help_ja.json"))

    assert len(english_items) == len(japanese_items)
    for english_item, japanese_item in zip(english_items, japanese_items, strict=True):
        assert set(english_item) == REQUIRED_KEYS
        assert set(japanese_item) == REQUIRED_KEYS


def test_english_and_japanese_help_keep_same_regex_patterns() -> None:
    english_items = load_help_items(Path("resources/regex_help_en.json"))
    japanese_items = load_help_items(Path("resources/regex_help_ja.json"))

    english_patterns = [item["pattern"] for item in english_items]
    japanese_patterns = [item["pattern"] for item in japanese_items]

    assert japanese_patterns == english_patterns


def test_japanese_help_contains_readable_japanese_text() -> None:
    japanese_items = load_help_items(Path("resources/regex_help_ja.json"))

    assert japanese_items[0]["category"] == "位置"
    assert japanese_items[0]["label"] == "行の先頭"
    assert "位置" in japanese_items[0]["description"]
