from __future__ import annotations

import tempfile
from pathlib import Path


class FileManager:
    def load_text(self, load_file_path: Path) -> str:
        return load_file_path.read_text(encoding="utf-8")

    def save_text(self, save_file_path: Path, save_data: str) -> None:
        save_file_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=save_file_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(save_data)
            temporary_file.flush()
            temporary_file_path = Path(temporary_file.name)

        temporary_file_path.replace(save_file_path)
