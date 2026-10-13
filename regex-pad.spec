# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


PROJECT_ROOT = Path(SPECPATH)
JSON_EXCLUDE_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "_internal",
    "build",
    "dist",
}


def _project_json_datas():
    json_datas = []
    for json_path in sorted(PROJECT_ROOT.rglob("*.json")):
        relative_path = json_path.relative_to(PROJECT_ROOT)
        if any(part in JSON_EXCLUDE_PARTS for part in relative_path.parts):
            continue
        source_path = relative_path.as_posix()
        target_dir = relative_path.parent.as_posix()
        if target_dir == ".":
            target_dir = "."
        json_datas.append((source_path, target_dir))
    return json_datas


app_datas = [
    *_project_json_datas(),
    ('readme.txt', '.'),
    ('readme_jp.txt', '.'),
    ('LICENSE.txt', '.'),
    ('module_installer.py', '.'),
    ('portable_runtime.py', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=app_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='regex-pad',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

cleaner_a = Analysis(
    ['module_cleaner.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
cleaner_pyz = PYZ(cleaner_a.pure)

cleaner_exe = EXE(
    cleaner_pyz,
    cleaner_a.scripts,
    [],
    exclude_binaries=True,
    name='module_cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    cleaner_exe,
    a.binaries,
    cleaner_a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='regex-pad',
)
