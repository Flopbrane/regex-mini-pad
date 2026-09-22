from __future__ import annotations

from pathlib import Path

import pytest

from json_lint import lint_json_file, validate_json_file
from multi_lang_lint import (
    lint_dictionary_plugin,
    lint_standard_files,
    standard_file_names,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_json_lint_accepts_object_or_array(tmp_path: Path) -> None:
    object_path = tmp_path / "object.json"
    array_path = tmp_path / "array.json"
    object_path.write_text('{"name": "sample"}', encoding="utf-8")
    array_path.write_text('[{"name": "sample"}]', encoding="utf-8")

    assert lint_json_file(object_path) == ()
    assert lint_json_file(array_path) == ()


def test_json_lint_rejects_invalid_json(tmp_path: Path) -> None:
    load_file_path = tmp_path / "broken.json"
    load_file_path.write_text('{"name": ', encoding="utf-8")

    issues = lint_json_file(load_file_path)

    assert len(issues) == 1
    assert "Invalid JSON" in issues[0].message
    with pytest.raises(ValueError, match="Invalid JSON"):
        validate_json_file(load_file_path)


def test_json_lint_rejects_scalar_root(tmp_path: Path) -> None:
    load_file_path = tmp_path / "scalar.json"
    load_file_path.write_text('"sample"', encoding="utf-8")

    issues = lint_json_file(load_file_path)

    assert len(issues) == 1
    assert "object or an array" in issues[0].message


def test_multi_lang_standard_files_are_present_and_valid() -> None:
    standards_path = PROJECT_ROOT / "dictionaries" / "standards"

    assert standard_file_names() == (
        "standard_javascript.json",
        "standard_textscript.json",
        "standard_css.json",
    )
    assert lint_standard_files(standards_path) == ()


def test_multi_lang_lint_checks_plugin_and_standards(tmp_path: Path) -> None:
    load_file_path = tmp_path / "javascript.json"
    load_file_path.write_text('{"language_id": "javascript"}', encoding="utf-8")

    issues = lint_dictionary_plugin(
        load_file_path,
        PROJECT_ROOT / "dictionaries" / "standards",
    )

    assert issues == ()
