from __future__ import annotations

import tempfile
from pathlib import Path


class FileManager:
    def load_text(self, load_file_path: Path, encoding: str = "utf-8") -> str:
        return load_file_path.read_text(encoding=encoding)

    def save_text(
        self,
        save_file_path: Path,
        save_data: str,
        encoding: str = "utf-8",
    ) -> None:
        save_file_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding=encoding,
            dir=save_file_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(save_data)
            temporary_file.flush()
            temporary_file_path = Path(temporary_file.name)

        temporary_file_path.replace(save_file_path)
