from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UnsavedBackup:
    text: str
    encoding: str
    save_file_path: Path | None = None


class UnsavedBackupManager:
    def __init__(self, backup_path: Path) -> None:
        self.backup_path = backup_path

    def load(self) -> UnsavedBackup | None:
        if not self.backup_path.exists():
            return None

        try:
            load_data: dict[str, Any] = json.loads(
                self.backup_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return None

        text = load_data.get("text")
        encoding = load_data.get("encoding")
        save_file_path = load_data.get("save_file_path")
        if not isinstance(text, str) or not isinstance(encoding, str):
            return None

        return UnsavedBackup(
            text=text,
            encoding=encoding,
            save_file_path=Path(save_file_path) if isinstance(save_file_path, str) else None,
        )

    def save(self, backup: UnsavedBackup) -> None:
        self.backup_path.parent.mkdir(parents=True, exist_ok=True)
        save_data = {
            "text": backup.text,
            "encoding": backup.encoding,
            "save_file_path": (
                str(backup.save_file_path) if backup.save_file_path is not None else None
            ),
        }
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.backup_path.parent,
            delete=False,
        ) as temporary_file:
            json.dump(save_data, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.flush()
            temporary_file_path = Path(temporary_file.name)

        temporary_file_path.replace(self.backup_path)

    def clear(self) -> None:
        self.backup_path.unlink(missing_ok=True)
