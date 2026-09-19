"""Dry-run-first cleaner for the regex-pad portable folder."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

APP_NAME = "regex-pad"


def default_app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent / "dist" / APP_NAME


def records_dir(app_root: Path) -> Path:
    return app_root / "install_records"


def append_log(app_root: Path, message: str) -> None:
    path = app_root / "logs" / "cleaner.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    old_text = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(old_text + message + "\n", encoding="utf-8")


def load_install_diff(app_root: Path) -> dict[str, Any]:
    path = records_dir(app_root) / "install_diff.json"
    if not path.exists():
        return {"added_files": [], "added_pip_packages": []}
    return json.loads(path.read_text(encoding="utf-8"))


def is_inside(child_path: Path, parent_path: Path) -> bool:
    try:
        child_path.resolve().relative_to(parent_path.resolve())
    except ValueError:
        return False
    return True


def delete_candidates(app_root: Path) -> list[Path]:
    candidates: list[Path] = []
    for item in load_install_diff(app_root).get("added_files", []):
        if not item.get("owned_by_this_app", False) or not item.get("delete_candidate", False):
            continue
        candidate_path = Path(item.get("path", ""))
        if candidate_path.exists() and is_inside(candidate_path, app_root):
            candidates.append(candidate_path)
    return candidates


def write_report(app_root: Path, mode: str, candidates: list[Path]) -> None:
    report = {
        "app_name": APP_NAME,
        "mode": mode,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "app_root": str(app_root),
        "candidates": [str(path) for path in candidates],
    }
    report_path = records_dir(app_root) / "cleaner_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def scan(app_root: Path) -> int:
    candidates = delete_candidates(app_root)
    write_report(app_root, "scan", candidates)
    print(f"App folder: {app_root}")
    print(f"Delete candidates: {len(candidates)}")
    for candidate in candidates:
        print(candidate)
    return 0


def dry_run(app_root: Path) -> int:
    candidates = delete_candidates(app_root)
    write_report(app_root, "dry-run", candidates)
    print("Dry-run only. No files were deleted.")
    for candidate in candidates:
        print(candidate)
    return 0


def clean(app_root: Path, yes: bool) -> int:
    candidates = delete_candidates(app_root)
    write_report(app_root, "clean", candidates)
    if not candidates:
        print("No delete candidates were found.")
        return 0
    for candidate in candidates:
        print(candidate)
    if not yes and input("Type DELETE to continue: ") != "DELETE":
        print("Cancelled.")
        return 1
    for candidate in candidates:
        if candidate.is_dir():
            shutil.rmtree(candidate)
        elif candidate.exists():
            candidate.unlink()
        append_log(app_root, f"deleted: {candidate}")
    print("Clean completed. You may delete the app folder manually after closing this cleaner.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean only files recorded as added by this app.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--clean", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--app-root", default=str(default_app_root()))
    args = parser.parse_args()

    app_root = Path(args.app_root).resolve()
    if args.scan:
        return scan(app_root)
    if args.dry_run:
        return dry_run(app_root)
    return clean(app_root, args.yes)


if __name__ == "__main__":
    raise SystemExit(main())
