from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


class FileBackupManager:
    def __init__(self, backup_root: Path) -> None:
        self.backup_root = backup_root

    def backup_existing_file(
        self,
        load_file_path: Path,
        *,
        retention_count: int = 20,
        retention_days: int = 30,
    ) -> Path | None:
        _ = retention_count, retention_days
        if not load_file_path.exists() or not load_file_path.is_file():
            return None

        backup_folder = self._backup_folder_for_file(load_file_path)
        backup_folder.mkdir(parents=True, exist_ok=True)
        backup_path = self._latest_backup_path(backup_folder, load_file_path)
        shutil.copy2(load_file_path, backup_path)
        backup_path.touch()
        return backup_path

    def backups_for_file(self, load_file_path: Path) -> list[Path]:
        backup_folder = self._backup_folder_for_file(load_file_path)
        if not backup_folder.exists():
            return []
        return sorted(
            (item for item in backup_folder.iterdir() if item.is_file()),
            key=lambda item: item.name,
            reverse=True,
        )

    def _backup_folder_for_file(self, load_file_path: Path) -> Path:
        resolved_path = load_file_path.resolve()
        path_hash = hashlib.sha1(str(resolved_path).encode("utf-8")).hexdigest()[:12]
        safe_name = _safe_path_part(resolved_path.stem) or "file"
        return self.backup_root / f"{safe_name}-{path_hash}"

    def _latest_backup_path(self, backup_folder: Path, load_file_path: Path) -> Path:
        safe_name = _safe_path_part(load_file_path.name) or "file.txt"
        return backup_folder / f"{safe_name}.latest.bak"


def _safe_path_part(value: str) -> str:
    safe_characters: list[str] = []
    for character in value:
        if character.isalnum() or character in {"-", "_", "."}:
            safe_characters.append(character)
        else:
            safe_characters.append("_")
    return "".join(safe_characters).strip("._")
