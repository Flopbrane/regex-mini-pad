"""Portable runtime path setup for regex-pad."""
from __future__ import annotations

import os
import site
import sys
from pathlib import Path


def app_base_dir() -> Path:
    """Return the folder that should contain runtime/cache/model data."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _add_site_dir(site_dir: Path) -> None:
    if site_dir.exists():
        site.addsitedir(str(site_dir))


def configure_portable_runtime() -> Path:
    """Keep app-owned modules and caches under the app folder."""
    base_dir = app_base_dir()
    runtime_dir = base_dir / "runtime"
    venv_dir = runtime_dir / "venv"
    modules_dir = base_dir / "modules"
    cache_dir = base_dir / "cache"
    data_dir = base_dir / "data"

    for folder_path in (
        venv_dir,
        modules_dir / "site-packages",
        modules_dir / "wheels",
        cache_dir / "pip",
        cache_dir / "app_cache",
        data_dir / "input",
        data_dir / "output",
        data_dir / "temp",
        base_dir / "logs",
        base_dir / "install_records",
    ):
        folder_path.mkdir(parents=True, exist_ok=True)

    _add_site_dir(modules_dir / "site-packages")
    _add_site_dir(venv_dir / "Lib" / "site-packages")
    _add_site_dir(venv_dir / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages")

    os.environ.setdefault("PIP_CACHE_DIR", str(cache_dir / "pip"))
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir / "matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_dir / "xdg"))
    os.environ.setdefault("MYAPP_BASE_DIR", str(base_dir))
    os.environ.setdefault("MYAPP_MODULES_DIR", str(modules_dir / "site-packages"))

    return base_dir
