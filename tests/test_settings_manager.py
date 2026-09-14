from __future__ import annotations

from settings.settings_manager import SettingsManager


def test_load_returns_defaults_when_settings_file_does_not_exist(tmp_path) -> None:
    settings_manager = SettingsManager(tmp_path / "settings.json")

    settings = settings_manager.load()

    assert settings.word_wrap_enabled is False
    assert settings.line_numbers_enabled is True
    assert settings.language_code == "ja"
    assert settings.window_width == 900
    assert settings.window_height == 650
    assert settings.wordpress_mode_label_key == "tag.wordpress_mode.normal"
    assert settings.hover_hints_enabled is True
    assert settings.backup_folder == ""
    assert settings.font_family == "Consolas"
    assert settings.font_size == 11


def test_save_and_load_settings(tmp_path) -> None:
    settings_manager = SettingsManager(tmp_path / "settings.json")

    settings_manager.save(
        word_wrap_enabled=True,
        line_numbers_enabled=False,
        language_code="en",
        window_width=1200,
        window_height=800,
        wordpress_mode_label_key="tag.wordpress_mode.high_security",
        hover_hints_enabled=False,
        backup_folder="D:/backup",
        font_family="Meiryo",
        font_size=14,
    )
    settings = settings_manager.load()

    assert settings.word_wrap_enabled is True
    assert settings.line_numbers_enabled is False
    assert settings.language_code == "en"
    assert settings.window_width == 1200
    assert settings.window_height == 800
    assert settings.wordpress_mode_label_key == "tag.wordpress_mode.high_security"
    assert settings.hover_hints_enabled is False
    assert settings.backup_folder == "D:/backup"
    assert settings.font_family == "Meiryo"
    assert settings.font_size == 14
