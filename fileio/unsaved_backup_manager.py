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


@dataclass(frozen=True)
class UnsavedBackupSession:
    tabs: list[UnsavedBackup]
    current_index: int = 0


class UnsavedBackupManager:
    def __init__(self, backup_path: Path) -> None:
        self.backup_path = backup_path

    def load(self) -> UnsavedBackup | None:
        session = self.load_session()
        if session is None or not session.tabs:
            return None
        return session.tabs[min(max(session.current_index, 0), len(session.tabs) - 1)]

    def load_session(self) -> UnsavedBackupSession | None:
        if not self.backup_path.exists():
            return None

        try:
            load_data: dict[str, Any] = json.loads(
                self.backup_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            return None

        tabs_data = load_data.get("tabs")
        if isinstance(tabs_data, list):
            tabs = [
                backup
                for tab_data in tabs_data
                if isinstance(tab_data, dict)
                for backup in [self._backup_from_data(tab_data)]
                if backup is not None and backup.text
            ]
            if not tabs:
                return None
            current_index = load_data.get("current_index", 0)
            if not isinstance(current_index, int):
                current_index = 0
            return UnsavedBackupSession(
                tabs=tabs,
                current_index=min(max(current_index, 0), len(tabs) - 1),
            )

        backup = self._backup_from_data(load_data)
        if backup is None:
            return None
        return UnsavedBackupSession(tabs=[backup], current_index=0)

    def _backup_from_data(self, load_data: dict[str, Any]) -> UnsavedBackup | None:
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

    def save(self, backup: UnsavedBackup) -> bool:
        return self.save_session(UnsavedBackupSession(tabs=[backup]))

    def save_session(self, session: UnsavedBackupSession) -> bool:
        tabs = [tab for tab in session.tabs if tab.text]
        if not tabs:
            self.clear()
            return True

        temporary_file_path: Path | None = None
        try:
            self.backup_path.parent.mkdir(parents=True, exist_ok=True)
            save_data = {
                "version": 2,
                "current_index": min(max(session.current_index, 0), len(tabs) - 1),
                "tabs": [
                    {
                        "text": tab.text,
                        "encoding": tab.encoding,
                        "save_file_path": (
                            str(tab.save_file_path)
                            if tab.save_file_path is not None
                            else None
                        ),
                    }
                    for tab in tabs
                ],
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
        except OSError:
            if temporary_file_path is not None:
                temporary_file_path.unlink(missing_ok=True)
            return False
        return True

    def clear(self) -> None:
        try:
            self.backup_path.unlink(missing_ok=True)
        except OSError:
            return
