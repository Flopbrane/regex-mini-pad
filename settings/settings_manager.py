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
    wordpress_mode_label_key: str = "tag.wordpress_mode.normal"
    hover_hints_enabled: bool = True
    backup_folder: str = ""
    font_family: str = "Consolas"
    font_size: int = 11


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
            wordpress_mode_label_key=str(
                load_data.get("wordpress_mode_label_key", "tag.wordpress_mode.normal")
            ),
            hover_hints_enabled=bool(load_data.get("hover_hints_enabled", True)),
            backup_folder=str(load_data.get("backup_folder", "")),
            font_family=str(load_data.get("font_family", "Consolas")),
            font_size=int(load_data.get("font_size", 11)),
        )

    def save(
        self,
        *,
        word_wrap_enabled: bool,
        line_numbers_enabled: bool,
        language_code: str,
        window_width: int,
        window_height: int,
        wordpress_mode_label_key: str = "tag.wordpress_mode.normal",
        hover_hints_enabled: bool = True,
        backup_folder: str = "",
        font_family: str = "Consolas",
        font_size: int = 11,
    ) -> None:
        save_data = {
            "word_wrap_enabled": word_wrap_enabled,
            "line_numbers_enabled": line_numbers_enabled,
            "language_code": language_code,
            "window_width": window_width,
            "window_height": window_height,
            "wordpress_mode_label_key": wordpress_mode_label_key,
            "hover_hints_enabled": hover_hints_enabled,
            "backup_folder": backup_folder,
            "font_family": font_family,
            "font_size": font_size,
        }
        self.settings_path.write_text(
            json.dumps(save_data, indent=2),
            encoding="utf-8",
        )
