from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SELECTION_PLACEHOLDER = "{selection}"
CURSOR_PLACEHOLDER = "{cursor}"


@dataclass(frozen=True)
class TagSnippet:
    label_key: str
    hint_key: str
    template: str

    def render(self, selected_text: str) -> tuple[str, int]:
        rendered_text = self.template.replace(SELECTION_PLACEHOLDER, selected_text)
        cursor_position = rendered_text.find(CURSOR_PLACEHOLDER)
        if cursor_position == -1:
            return rendered_text, len(rendered_text)
        return rendered_text.replace(CURSOR_PLACEHOLDER, ""), cursor_position


@dataclass(frozen=True)
class TagSnippetGroup:
    label_key: str
    snippets: tuple[TagSnippet, ...]


def tag_snippet_groups(dictionarys_path: Path | None = None) -> tuple[TagSnippetGroup, ...]:
    dictionarys_path = dictionarys_path or Path(__file__).resolve().parent.parent / "dictionarys"
    return (
        TagSnippetGroup(
            "tag.group.html",
            _load_snippets_from_json(dictionarys_path / "html_dict.json"),
        ),
        TagSnippetGroup(
            "tag.group.markdown",
            _load_snippets_from_json(dictionarys_path / "markdown_dict.json"),
        ),
        TagSnippetGroup(
            "tag.group.wordpress_html",
            _load_snippets_from_json(dictionarys_path / "wordpress_html_dict.json"),
        ),
    )


def _load_snippets_from_json(load_file_path: Path) -> tuple[TagSnippet, ...]:
    load_data = json.loads(load_file_path.read_text(encoding="utf-8"))
    if not isinstance(load_data, list):
        raise TypeError(f"Dictionary must contain a list: {load_file_path}")

    snippets: list[TagSnippet] = []
    for item in load_data:
        if not isinstance(item, dict):
            raise TypeError(f"Dictionary item must be an object: {load_file_path}")
        snippets.append(_snippet_from_dict(item, load_file_path))
    return tuple(snippets)


def _snippet_from_dict(item: dict[str, Any], load_file_path: Path) -> TagSnippet:
    label_key = item.get("label_key")
    hint_key = item.get("hint_key")
    template = item.get("template")
    if (
        not isinstance(label_key, str)
        or not isinstance(hint_key, str)
        or not isinstance(template, str)
    ):
        raise TypeError(
            "Dictionary item requires string label_key, hint_key, and template: "
            f"{load_file_path}"
        )
    return TagSnippet(label_key, hint_key, template)
