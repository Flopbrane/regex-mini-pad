from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EditorSettings:
    word_wrap_enabled: bool = False
    line_numbers_enabled: bool = True
    ruler_enabled: bool = False
    visible_spaces_enabled: bool = False
    visible_tabs_enabled: bool = False
    visible_newlines_enabled: bool = False
    fixed_column_wrap_enabled: bool = False
    fixed_column_wrap_column: int = 80
    startup_restore_enabled: bool = True
    language_code: str = "ja"
    default_encoding: str = "utf-8"
    newline_code: str = "lf"
    window_width: int = 900
    window_height: int = 650
    wordpress_mode_label_key: str = "tag.wordpress_mode.normal"
    hover_hints_enabled: bool = True
    user_dictionary_folder: str = ""
    dictionary_check_enabled: bool = True
    backup_folder: str = ""
    backup_retention_count: int = 10
    backup_retention_days: int = 30
    font_family: str = "Consolas"
    font_size: int = 11
    tab_width: int = 4
    search_marker_color: str = "#ffff00"
    current_match_marker_color: str = "#ff9900"
    visible_space_marker_color: str = "#9a9a9a"
    visible_tab_marker_color: str = "#9ed8ff"
    visible_newline_marker_color: str = "#ff9900"
    regex_lint_enabled: bool = True
    html_typo_lint_enabled: bool = True


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
            ruler_enabled=bool(load_data.get("ruler_enabled", False)),
            visible_spaces_enabled=bool(
                load_data.get("visible_spaces_enabled", False)
            ),
            visible_tabs_enabled=bool(load_data.get("visible_tabs_enabled", False)),
            visible_newlines_enabled=bool(
                load_data.get("visible_newlines_enabled", False)
            ),
            fixed_column_wrap_enabled=bool(
                load_data.get("fixed_column_wrap_enabled", False)
            ),
            fixed_column_wrap_column=max(
                1,
                int(load_data.get("fixed_column_wrap_column", 80)),
            ),
            startup_restore_enabled=bool(
                load_data.get("startup_restore_enabled", True)
            ),
            language_code=str(load_data.get("language_code", "ja")),
            default_encoding=str(load_data.get("default_encoding", "utf-8")),
            newline_code=str(load_data.get("newline_code", "lf")),
            window_width=int(load_data.get("window_width", 900)),
            window_height=int(load_data.get("window_height", 650)),
            wordpress_mode_label_key=str(
                load_data.get("wordpress_mode_label_key", "tag.wordpress_mode.normal")
            ),
            hover_hints_enabled=bool(load_data.get("hover_hints_enabled", True)),
            user_dictionary_folder=str(load_data.get("user_dictionary_folder", "")),
            dictionary_check_enabled=bool(
                load_data.get("dictionary_check_enabled", True)
            ),
            backup_folder=str(load_data.get("backup_folder", "")),
            backup_retention_count=max(
                1,
                int(load_data.get("backup_retention_count", 10)),
            ),
            backup_retention_days=max(
                1,
                int(load_data.get("backup_retention_days", 30)),
            ),
            font_family=str(load_data.get("font_family", "Consolas")),
            font_size=int(load_data.get("font_size", 11)),
            tab_width=max(1, int(load_data.get("tab_width", 4))),
            search_marker_color=str(load_data.get("search_marker_color", "#ffff00")),
            current_match_marker_color=str(
                load_data.get("current_match_marker_color", "#ff9900")
            ),
            visible_space_marker_color=str(
                load_data.get("visible_space_marker_color", "#9a9a9a")
            ),
            visible_tab_marker_color=str(
                load_data.get("visible_tab_marker_color", "#9ed8ff")
            ),
            visible_newline_marker_color=str(
                load_data.get("visible_newline_marker_color", "#ff9900")
            ),
            regex_lint_enabled=bool(load_data.get("regex_lint_enabled", True)),
            html_typo_lint_enabled=bool(
                load_data.get("html_typo_lint_enabled", True)
            ),
        )

    def save(
        self,
        *,
        word_wrap_enabled: bool,
        line_numbers_enabled: bool,
        ruler_enabled: bool,
        visible_spaces_enabled: bool,
        visible_tabs_enabled: bool,
        visible_newlines_enabled: bool,
        fixed_column_wrap_enabled: bool,
        fixed_column_wrap_column: int,
        startup_restore_enabled: bool,
        language_code: str,
        default_encoding: str,
        newline_code: str,
        window_width: int,
        window_height: int,
        wordpress_mode_label_key: str = "tag.wordpress_mode.normal",
        hover_hints_enabled: bool = True,
        user_dictionary_folder: str = "",
        dictionary_check_enabled: bool = True,
        backup_folder: str = "",
        backup_retention_count: int = 10,
        backup_retention_days: int = 30,
        font_family: str = "Consolas",
        font_size: int = 11,
        tab_width: int = 4,
        search_marker_color: str = "#ffff00",
        current_match_marker_color: str = "#ff9900",
        visible_space_marker_color: str = "#9a9a9a",
        visible_tab_marker_color: str = "#9ed8ff",
        visible_newline_marker_color: str = "#ff9900",
        regex_lint_enabled: bool = True,
        html_typo_lint_enabled: bool = True,
    ) -> None:
        save_data = {
            "word_wrap_enabled": word_wrap_enabled,
            "line_numbers_enabled": line_numbers_enabled,
            "ruler_enabled": ruler_enabled,
            "visible_spaces_enabled": visible_spaces_enabled,
            "visible_tabs_enabled": visible_tabs_enabled,
            "visible_newlines_enabled": visible_newlines_enabled,
            "fixed_column_wrap_enabled": fixed_column_wrap_enabled,
            "fixed_column_wrap_column": max(1, fixed_column_wrap_column),
            "startup_restore_enabled": startup_restore_enabled,
            "language_code": language_code,
            "default_encoding": default_encoding,
            "newline_code": newline_code,
            "window_width": window_width,
            "window_height": window_height,
            "wordpress_mode_label_key": wordpress_mode_label_key,
            "hover_hints_enabled": hover_hints_enabled,
            "user_dictionary_folder": user_dictionary_folder,
            "dictionary_check_enabled": dictionary_check_enabled,
            "backup_folder": backup_folder,
            "backup_retention_count": max(1, backup_retention_count),
            "backup_retention_days": max(1, backup_retention_days),
            "font_family": font_family,
            "font_size": font_size,
            "tab_width": max(1, tab_width),
            "search_marker_color": search_marker_color,
            "current_match_marker_color": current_match_marker_color,
            "visible_space_marker_color": visible_space_marker_color,
            "visible_tab_marker_color": visible_tab_marker_color,
            "visible_newline_marker_color": visible_newline_marker_color,
            "regex_lint_enabled": regex_lint_enabled,
            "html_typo_lint_enabled": html_typo_lint_enabled,
        }
        self.settings_path.write_text(
            json.dumps(save_data, indent=2),
            encoding="utf-8",
        )
