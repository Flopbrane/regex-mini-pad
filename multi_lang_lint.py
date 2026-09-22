from __future__ import annotations

from pathlib import Path

from json_lint import JsonLintIssue, lint_json_file

STANDARD_FILE_NAMES = (
    "standard_javascript.json",
    "standard_textscript.json",
    "standard_css.json",
)


def standard_file_names() -> tuple[str, ...]:
    return STANDARD_FILE_NAMES


def lint_standard_files(standards_path: Path) -> tuple[JsonLintIssue, ...]:
    issues: list[JsonLintIssue] = []
    for file_name in STANDARD_FILE_NAMES:
        load_file_path = standards_path / file_name
        if not load_file_path.exists():
            issues.append(
                JsonLintIssue(
                    load_file_path,
                    "Standard reference file is missing.",
                )
            )
            continue
        issues.extend(lint_json_file(load_file_path))
    return tuple(issues)


def lint_dictionary_plugin(
    load_file_path: Path,
    standards_path: Path | None = None,
) -> tuple[JsonLintIssue, ...]:
    issues = list(lint_json_file(load_file_path))
    if standards_path is not None:
        issues.extend(lint_standard_files(standards_path))
    return tuple(issues)
