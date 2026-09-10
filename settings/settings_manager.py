from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EditorSettings:
    word_wrap_enabled: bool = False
    line_numbers_enabled: bool = True
    language_code: str = "ja"
    window_width: int = 900
    window_height: int = 650


class SettingsManager:
    def __init__(self, settings_path: Path) -> None:
        self.settings_path = settings_path

    def load(self) -> EditorSettings:
        if not self.settings_path.exists():
            return EditorSettings()

        try:
            load_data: dict[str, Any] = json.loads(
                self.settings_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return EditorSettings()

        return EditorSettings(
            word_wrap_enabled=bool(load_data.get("word_wrap_enabled", False)),
            line_numbers_enabled=bool(load_data.get("line_numbers_enabled", True)),
            language_code=str(load_data.get("language_code", "ja")),
            window_width=int(load_data.get("window_width", 900)),
            window_height=int(load_data.get("window_height", 650)),
        )

    def save(
        self,
        *,
        word_wrap_enabled: bool,
        line_numbers_enabled: bool,
        language_code: str,
        window_width: int,
        window_height: int,
    ) -> None:
        save_data = {
            "word_wrap_enabled": word_wrap_enabled,
            "line_numbers_enabled": line_numbers_enabled,
            "language_code": language_code,
            "window_width": window_width,
            "window_height": window_height,
        }
        self.settings_path.write_text(
            json.dumps(save_data, indent=2),
            encoding="utf-8",
        )
