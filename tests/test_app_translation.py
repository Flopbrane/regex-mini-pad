from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from localization.translator import Translator


def load_texts(language_code: str) -> dict[str, Any]:
    return json.loads(
        Path(f"resources/app_text_{language_code}.json").read_text(encoding="utf-8")
    )


def test_app_translation_files_have_matching_keys() -> None:
    english_texts = load_texts("en")
    japanese_texts = load_texts("ja")

    assert set(japanese_texts) == set(english_texts)


def test_translator_formats_values() -> None:
    translator = Translator(Path("resources"), "en")

    assert translator.text("status.position", line=2, column=3, characters=10) == (
        "Line 2, Column 3 | Characters 10"
    )


def test_japanese_translation_uses_readable_labels() -> None:
    translator = Translator(Path("resources"), "ja")

    assert translator.text("menu.search") == "検索(&S)"
    assert translator.text("find.regex") == "正規表現として検索する"
