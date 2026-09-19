"""Prepare the portable runtime folder for regex-pad."""
from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
import venv
from datetime import datetime
from pathlib import Path
from typing import Any

APP_NAME = "regex-pad"
SCHEMA_VERSION = "1.0"
REQUIREMENT_CANDIDATES = (
    "requirements_locked.txt",
    "requirements.txt",
    "requirements_dev.txt",
)


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def project_root() -> Path:
    return Path(__file__).resolve().parent


def default_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return project_root() / "dist" / APP_NAME


def app_paths(app_root: Path) -> dict[str, Path]:
    return {
        "app_root": app_root,
        "runtime": app_root / "runtime",
        "venv": app_root / "runtime" / "venv",
        "modules": app_root / "modules",
        "wheels": app_root / "modules" / "wheels",
        "cache_pip": app_root / "cache" / "pip",
        "cache_app": app_root / "cache" / "app_cache",
        "data_input": app_root / "data" / "input",
        "data_output": app_root / "data" / "output",
        "data_temp": app_root / "data" / "temp",
        "logs": app_root / "logs",
        "install_records": app_root / "install_records",
    }


def ensure_portable_folders(app_root: Path) -> None:
    for folder_path in app_paths(app_root).values():
        folder_path.mkdir(parents=True, exist_ok=True)


def venv_python_path(venv_path: Path) -> Path:
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def resolve_requirements(requirements_path: str | None) -> Path | None:
    if requirements_path:
        path = Path(requirements_path).resolve()
        return path if path.exists() else None

    root = project_root()
    for candidate in REQUIREMENT_CANDIDATES:
        path = root / candidate
        if path.exists():
            return path

    return None


def list_pip_packages(python_path: Path) -> list[str]:
    if not python_path.exists():
        return []

    completed_process = subprocess.run(
        [str(python_path), "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed_process.returncode != 0:
        return []

    return [line.strip() for line in completed_process.stdout.splitlines() if line.strip()]


def classify_path(file_path: Path, app_root: Path) -> tuple[str, str]:
    lower_path = str(file_path).lower()
    if "site-packages" in lower_path:
        return "module", "pip"
    if str(file_path).startswith(str(app_root / "data")):
        return "data", "app"
    if str(file_path).startswith(str(app_root / "cache")):
        return "cache", "app"
    if str(file_path).startswith(str(app_root / "logs")):
        return "log", "app"
    return "unknown", "unknown"


def snapshot_files(app_root: Path) -> list[dict[str, Any]]:
    if not app_root.exists():
        return []

    records: list[dict[str, Any]] = []
    for file_path in app_root.rglob("*"):
        if not file_path.is_file():
            continue
        kind, source = classify_path(file_path, app_root)
        stat_result = file_path.stat()
        records.append(
            {
                "path": str(file_path.resolve()),
                "size_bytes": stat_result.st_size,
                "mtime": datetime.fromtimestamp(stat_result.st_mtime).astimezone().isoformat(timespec="seconds"),
                "kind": kind,
                "source": source,
                "owned_by_this_app": True,
                "delete_candidate": False,
            }
        )

    return records


def build_snapshot(app_root: Path) -> dict[str, Any]:
    paths = app_paths(app_root)
    python_path = venv_python_path(paths["venv"])
    return {
        "schema_version": SCHEMA_VERSION,
        "app_name": APP_NAME,
        "created_at": now_text(),
        "computer_name": socket.gethostname(),
        "user_name": os.environ.get("USERNAME") or os.environ.get("USER") or "",
        "python_versions": [{"path": str(python_path), "version": platform.python_version(), "exists": python_path.exists()}],
        "venvs": [{"path": str(paths["venv"]), "exists": paths["venv"].exists()}],
        "pip_packages": list_pip_packages(python_path),
        "model_dirs": [],
        "cache_dirs": [str(paths["cache_pip"]), str(paths["cache_app"])],
        "files": snapshot_files(app_root),
    }


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_diff(before: dict[str, Any], after: dict[str, Any], app_root: Path) -> dict[str, Any]:
    before_files = {item["path"] for item in before.get("files", [])}
    app_root_text = str(app_root.resolve())
    added_files = []
    for item in after.get("files", []):
        item_path = item.get("path", "")
        if item_path in before_files or not item_path.startswith(app_root_text):
            continue
        added = dict(item)
        added["owned_by_this_app"] = True
        added["delete_candidate"] = True
        added_files.append(added)

    before_packages = set(before.get("pip_packages", []))
    after_packages = set(after.get("pip_packages", []))
    return {
        "schema_version": SCHEMA_VERSION,
        "app_name": APP_NAME,
        "created_at": now_text(),
        "added_pip_packages": sorted(after_packages - before_packages),
        "added_files": added_files,
    }


def create_venv_if_needed(venv_path: Path) -> None:
    python_path = venv_python_path(venv_path)
    if python_path.exists():
        return
    venv.EnvBuilder(with_pip=True, clear=False).create(venv_path)


def install_requirements(app_root: Path, requirements_path: Path) -> None:
    paths = app_paths(app_root)
    create_venv_if_needed(paths["venv"])
    python_path = venv_python_path(paths["venv"])
    env = os.environ.copy()
    env["PIP_CACHE_DIR"] = str(paths["cache_pip"])
    completed_process = subprocess.run(
        [str(python_path), "-m", "pip", "install", "-r", str(requirements_path)],
        env=env,
        check=False,
    )
    if completed_process.returncode != 0:
        raise RuntimeError(f"pip install failed: {requirements_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare portable runtime folders.")
    parser.add_argument("--app-root", default=str(default_app_root()))
    parser.add_argument("--requirements", default=None)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--snapshot-before", action="store_true")
    parser.add_argument("--snapshot-after", action="store_true")
    parser.add_argument("--diff", action="store_true")
    args = parser.parse_args()

    app_root = Path(args.app_root).resolve()
    ensure_portable_folders(app_root)
    records = app_paths(app_root)["install_records"]

    if args.snapshot_before or args.install:
        save_json(records / "pre_install_module.json", build_snapshot(app_root))
    if args.install:
        requirements_path = resolve_requirements(args.requirements)
        if requirements_path is None:
            raise FileNotFoundError("requirements file was not found.")
        install_requirements(app_root, requirements_path)
    if args.snapshot_after or args.install:
        save_json(records / "after_install_module.json", build_snapshot(app_root))
    if args.diff or args.install:
        before_path = records / "pre_install_module.json"
        after_path = records / "after_install_module.json"
        if before_path.exists() and after_path.exists():
            save_json(records / "install_diff.json", build_diff(load_json(before_path), load_json(after_path), app_root))

    print(f"Prepared portable folders: {app_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
