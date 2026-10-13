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


@dataclass(frozen=True)
class JsonFragmentIssue:
    message: str
    line_number: int
    column_number: int


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


def lint_json_fragment(
    load_data: str,
    *,
    start_line_number: int = 1,
    start_column_number: int = 1,
    require_container: bool = True,
) -> tuple[JsonFragmentIssue, ...]:
    """Lint an extracted JSON fragment while preserving source coordinates."""
    try:
        parsed_data: Any = json.loads(load_data)
    except JSONDecodeError as error:
        line_number, column_number = _source_position_for_json_error(
            error,
            start_line_number,
            start_column_number,
        )
        return (
            JsonFragmentIssue(
                f"Invalid JSON at line {line_number}, column {column_number}: "
                f"{error.msg}",
                line_number,
                column_number,
            ),
        )

    if require_container and not isinstance(parsed_data, dict | list):
        return (
            JsonFragmentIssue(
                "JSON root must be an object or an array.",
                start_line_number,
                start_column_number,
            ),
        )
    return ()


def _source_position_for_json_error(
    error: JSONDecodeError,
    start_line_number: int,
    start_column_number: int,
) -> tuple[int, int]:
    line_number = start_line_number + error.lineno - 1
    if error.lineno == 1:
        return line_number, start_column_number + error.colno - 1
    return line_number, error.colno


def validate_json_file(load_file_path: Path) -> None:
    issues = lint_json_file(load_file_path)
    if issues:
        raise ValueError(format_json_lint_issues(issues))


def format_json_lint_issues(issues: tuple[JsonLintIssue, ...]) -> str:
    return "\n".join(issue.format() for issue in issues)
