from __future__ import annotations

from pathlib import Path


def test_pyinstaller_spec_collects_project_json_files() -> None:
    spec_text = Path("regex-pad.spec").read_text(encoding="utf-8")

    assert "def _project_json_datas():" in spec_text
    assert 'PROJECT_ROOT.rglob("*.json")' in spec_text
    assert "*_project_json_datas()," in spec_text
    assert '"build"' in spec_text
    assert '"dist"' in spec_text
    assert '"_internal"' in spec_text


def test_pyinstaller_spec_json_datas_include_current_project_json() -> None:
    spec_path = Path("regex-pad.spec")
    spec_prefix = spec_path.read_text(encoding="utf-8").split("a = Analysis", maxsplit=1)[0]
    namespace: dict[str, object] = {"SPECPATH": str(spec_path.resolve().parent)}
    exec(spec_prefix, namespace)  # noqa: S102 - The project-owned spec prefix is evaluated for packaging coverage.

    app_datas = namespace["app_datas"]
    assert isinstance(app_datas, list)
    assert ("resources/app_text_ja.json", "resources") in app_datas
    assert ("dictionaries/standards/standard_css.json", "dictionaries/standards") in app_datas
    assert ("config.json", ".") in app_datas
    assert all(not source.startswith("_internal/") for source, _target in app_datas)


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
