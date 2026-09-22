from __future__ import annotations

from settings.settings_manager import SettingsManager


def test_load_returns_defaults_when_settings_file_does_not_exist(tmp_path) -> None:
    settings_manager = SettingsManager(tmp_path / "settings.json")

    settings = settings_manager.load()

    assert settings.word_wrap_enabled is False
    assert settings.line_numbers_enabled is True
    assert settings.ruler_enabled is False
    assert settings.visible_spaces_enabled is False
    assert settings.visible_tabs_enabled is False
    assert settings.visible_newlines_enabled is False
    assert settings.fixed_column_wrap_enabled is False
    assert settings.fixed_column_wrap_column == 80
    assert settings.startup_restore_enabled is True
    assert settings.language_code == "ja"
    assert settings.default_encoding == "utf-8"
    assert settings.newline_code == "lf"
    assert settings.window_width == 900
    assert settings.window_height == 650
    assert settings.wordpress_mode_label_key == "tag.wordpress_mode.normal"
    assert settings.hover_hints_enabled is True
    assert settings.user_dictionary_folder == ""
    assert settings.dictionary_check_enabled is True
    assert settings.backup_folder == ""
    assert settings.backup_retention_count == 10
    assert settings.backup_retention_days == 30
    assert settings.font_family == "Consolas"
    assert settings.font_size == 11
    assert settings.tab_width == 4
    assert settings.search_marker_color == "#ffff00"
    assert settings.current_match_marker_color == "#ff9900"
    assert settings.regex_lint_enabled is True
    assert settings.html_typo_lint_enabled is True


def test_save_and_load_settings(tmp_path) -> None:
    settings_manager = SettingsManager(tmp_path / "settings.json")

    settings_manager.save(
        word_wrap_enabled=True,
        line_numbers_enabled=False,
        ruler_enabled=True,
        visible_spaces_enabled=True,
        visible_tabs_enabled=True,
        visible_newlines_enabled=False,
        fixed_column_wrap_enabled=True,
        fixed_column_wrap_column=72,
        startup_restore_enabled=False,
        language_code="en",
        default_encoding="cp932",
        newline_code="crlf",
        window_width=1200,
        window_height=800,
        wordpress_mode_label_key="tag.wordpress_mode.high_security",
        hover_hints_enabled=False,
        user_dictionary_folder="D:/dicts",
        dictionary_check_enabled=False,
        backup_folder="D:/backup",
        backup_retention_count=12,
        backup_retention_days=45,
        font_family="Meiryo",
        font_size=14,
        tab_width=8,
        search_marker_color="#9ed8ff",
        current_match_marker_color="#ffb3d9",
        regex_lint_enabled=False,
        html_typo_lint_enabled=False,
    )
    settings = settings_manager.load()

    assert settings.word_wrap_enabled is True
    assert settings.line_numbers_enabled is False
    assert settings.ruler_enabled is True
    assert settings.visible_spaces_enabled is True
    assert settings.visible_tabs_enabled is True
    assert settings.visible_newlines_enabled is False
    assert settings.fixed_column_wrap_enabled is True
    assert settings.fixed_column_wrap_column == 72
    assert settings.startup_restore_enabled is False
    assert settings.language_code == "en"
    assert settings.default_encoding == "cp932"
    assert settings.newline_code == "crlf"
    assert settings.window_width == 1200
    assert settings.window_height == 800
    assert settings.wordpress_mode_label_key == "tag.wordpress_mode.high_security"
    assert settings.hover_hints_enabled is False
    assert settings.user_dictionary_folder == "D:/dicts"
    assert settings.dictionary_check_enabled is False
    assert settings.backup_folder == "D:/backup"
    assert settings.backup_retention_count == 12
    assert settings.backup_retention_days == 45
    assert settings.font_family == "Meiryo"
    assert settings.font_size == 14
    assert settings.tab_width == 8
    assert settings.search_marker_color == "#9ed8ff"
    assert settings.current_match_marker_color == "#ffb3d9"
    assert settings.regex_lint_enabled is False
    assert settings.html_typo_lint_enabled is False
