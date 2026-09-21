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
        newline_code: str = "lf",
    ) -> None:
        save_file_path.parent.mkdir(parents=True, exist_ok=True)
        normalized_save_data = self._normalize_newlines(save_data, newline_code)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding=encoding,
            newline="",
            dir=save_file_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(normalized_save_data)
            temporary_file.flush()
            temporary_file_path = Path(temporary_file.name)

        temporary_file_path.replace(save_file_path)

    def _normalize_newlines(self, save_data: str, newline_code: str) -> str:
        normalized_data = save_data.replace("\r\n", "\n").replace("\r", "\n")
        if newline_code == "crlf":
            return normalized_data.replace("\n", "\r\n")
        if newline_code == "cr":
            return normalized_data.replace("\n", "\r")
        return normalized_data
