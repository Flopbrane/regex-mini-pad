from __future__ import annotations

from pathlib import Path


def test_pyinstaller_spec_includes_dictionaries_folder() -> None:
    spec_text = Path("regex-pad.spec").read_text(encoding="utf-8")

    assert "('dictionaries', 'dictionaries')" in spec_text


def test_pyinstaller_spec_builds_gui_app_without_upx() -> None:
    spec_text = Path("regex-pad.spec").read_text(encoding="utf-8")

    assert "console=False" in spec_text
    assert "upx=False" in spec_text


def test_build_script_uses_clean_build_without_codex_runtime_path() -> None:
    build_script = Path("build.ps1").read_text(encoding="utf-8")

    assert "--clean" in build_script
    assert "codex-runtimes" in build_script
    assert '$PyInstallerCachePath = Join-Path $env:LOCALAPPDATA "pyinstaller"' in build_script
    assert "Remove-Item -LiteralPath $ResolvedCachePath -Recurse -Force" in build_script
