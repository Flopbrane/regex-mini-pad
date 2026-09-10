from __future__ import annotations

from settings.settings_manager import SettingsManager


def test_load_returns_defaults_when_settings_file_does_not_exist(tmp_path) -> None:
    settings_manager = SettingsManager(tmp_path / "settings.json")

    settings = settings_manager.load()

    assert settings.word_wrap_enabled is False
    assert settings.line_numbers_enabled is True
    assert settings.window_width == 900
    assert settings.window_height == 650


def test_save_and_load_settings(tmp_path) -> None:
    settings_manager = SettingsManager(tmp_path / "settings.json")

    settings_manager.save(
        word_wrap_enabled=True,
        line_numbers_enabled=False,
        window_width=1200,
        window_height=800,
    )
    settings = settings_manager.load()

    assert settings.word_wrap_enabled is True
    assert settings.line_numbers_enabled is False
    assert settings.window_width == 1200
    assert settings.window_height == 800
