from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Translator:
    def __init__(self, resources_path: Path, language_code: str = "ja") -> None:
        self.resources_path = resources_path
        self.language_code = language_code
        self._texts = self._load_texts(language_code)

    def set_language(self, language_code: str) -> None:
        self.language_code = language_code
        self._texts = self._load_texts(language_code)

    def text(self, key: str, **values: object) -> str:
        text = str(self._texts.get(key, key))
        if values:
            return text.format(**values)
        return text

    def _load_texts(self, language_code: str) -> dict[str, Any]:
        language_path = self.resources_path / f"app_text_{language_code}.json"
        if not language_path.exists():
            language_path = self.resources_path / "app_text_en.json"
        return json.loads(language_path.read_text(encoding="utf-8"))
