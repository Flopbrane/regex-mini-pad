from __future__ import annotations

import json
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class JsonLintIssue:
    load_file_path: Path
    message: str

    def format(self) -> str:
        return f"{self.load_file_path}: {self.message}"


def lint_json_file(load_file_path: Path) -> tuple[JsonLintIssue, ...]:
    try:
        load_data: Any = json.loads(load_file_path.read_text(encoding="utf-8"))
    except JSONDecodeError as error:
        return (
            JsonLintIssue(
                load_file_path,
                f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}",
            ),
        )

    if not isinstance(load_data, dict | list):
        return (
            JsonLintIssue(
                load_file_path,
                "JSON root must be an object or an array.",
            ),
        )
    return ()


def validate_json_file(load_file_path: Path) -> None:
    issues = lint_json_file(load_file_path)
    if issues:
        raise ValueError(format_json_lint_issues(issues))


def format_json_lint_issues(issues: tuple[JsonLintIssue, ...]) -> str:
    return "\n".join(issue.format() for issue in issues)
