from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path


class FileBackupManager:
    def __init__(self, backup_root: Path) -> None:
        self.backup_root = backup_root
        self._backup_sequence = 0

    def backup_existing_file(
        self,
        load_file_path: Path,
        *,
        retention_count: int = 20,
        retention_days: int = 30,
    ) -> Path | None:
        if not load_file_path.exists() or not load_file_path.is_file():
            return None

        backup_folder = self._backup_folder_for_file(load_file_path)
        backup_folder.mkdir(parents=True, exist_ok=True)
        backup_path = self._unique_backup_path(backup_folder, load_file_path)
        shutil.copy2(load_file_path, backup_path)
        backup_path.touch()
        self._prune_backups(
            backup_folder,
            retention_count=max(1, retention_count),
            retention_days=max(1, retention_days),
        )
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

    def _backup_file_name(self, load_file_path: Path) -> str:
        self._backup_sequence += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        timestamp = f"{timestamp}-{self._backup_sequence:08d}"
        safe_name = _safe_path_part(load_file_path.name) or "file.txt"
        return f"{timestamp}-{safe_name}"

    def _unique_backup_path(self, backup_folder: Path, load_file_path: Path) -> Path:
        backup_path = backup_folder / self._backup_file_name(load_file_path)
        counter = 1
        while backup_path.exists():
            backup_path = backup_path.with_name(
                f"{backup_path.stem}-{counter}{backup_path.suffix}"
            )
            counter += 1
        return backup_path

    def _prune_backups(
        self,
        backup_folder: Path,
        *,
        retention_count: int,
        retention_days: int,
    ) -> None:
        backups = sorted(
            (item for item in backup_folder.iterdir() if item.is_file()),
            key=lambda item: item.name,
            reverse=True,
        )
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        for index, backup_path in enumerate(backups):
            modified_at = datetime.fromtimestamp(
                backup_path.stat().st_mtime,
                timezone.utc,
            )
            if index >= retention_count or modified_at < cutoff:
                backup_path.unlink(missing_ok=True)


def _safe_path_part(value: str) -> str:
    safe_characters: list[str] = []
    for character in value:
        if character.isalnum() or character in {"-", "_", "."}:
            safe_characters.append(character)
        else:
            safe_characters.append("_")
    return "".join(safe_characters).strip("._")
