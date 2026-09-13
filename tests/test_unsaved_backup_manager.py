from __future__ import annotations

from pathlib import Path

from fileio.unsaved_backup_manager import UnsavedBackup, UnsavedBackupManager


def test_unsaved_backup_manager_saves_and_loads_backup(tmp_path: Path) -> None:
    manager = UnsavedBackupManager(tmp_path / "autosave" / "unsaved_backup.json")

    manager.save(
        UnsavedBackup(
            text="draft text",
            encoding="utf-8",
            save_file_path=tmp_path / "draft.txt",
        )
    )
    backup = manager.load()

    assert backup is not None
    assert backup.text == "draft text"
    assert backup.encoding == "utf-8"
    assert backup.save_file_path == tmp_path / "draft.txt"


def test_unsaved_backup_manager_returns_none_for_broken_json(tmp_path: Path) -> None:
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    backup_path.parent.mkdir(parents=True)
    backup_path.write_text("{", encoding="utf-8")

    backup = UnsavedBackupManager(backup_path).load()

    assert backup is None


def test_unsaved_backup_manager_clears_backup(tmp_path: Path) -> None:
    backup_path = tmp_path / "autosave" / "unsaved_backup.json"
    manager = UnsavedBackupManager(backup_path)
    manager.save(UnsavedBackup(text="draft text", encoding="utf-8"))

    manager.clear()

    assert not backup_path.exists()
