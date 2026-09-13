from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SELECTION_PLACEHOLDER = "{selection}"
CURSOR_PLACEHOLDER = "{cursor}"
VALID_PLACEHOLDERS = {"selection", "cursor"}
PLACEHOLDER_PATTERN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


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


def tag_snippet_groups(dictionaries_path: Path | None = None) -> tuple[TagSnippetGroup, ...]:
    dictionaries_path = (
        dictionaries_path or Path(__file__).resolve().parent.parent / "dictionaries"
    )
    return (
        TagSnippetGroup(
            "tag.group.html",
            _load_snippets_from_json(dictionaries_path / "html_dict.json"),
        ),
        TagSnippetGroup(
            "tag.group.markdown",
            _load_snippets_from_json(dictionaries_path / "markdown_dict.json"),
        ),
        TagSnippetGroup(
            "tag.group.wordpress_html",
            _load_snippets_from_json(dictionaries_path / "wordpress_html_dict.json"),
        ),
    )


def ordered_tag_snippet_groups(
    save_file_path: Path | None,
    dictionaries_path: Path | None = None,
) -> tuple[TagSnippetGroup, ...]:
    groups = tag_snippet_groups(dictionaries_path)
    preferred_label_key = _preferred_group_label_key(save_file_path)
    if preferred_label_key is None:
        return groups
    return tuple(
        sorted(
            groups,
            key=lambda group: 0 if group.label_key == preferred_label_key else 1,
        )
    )


def tag_snippet_category_key(group_label_key: str, snippet: TagSnippet) -> str:
    label_key = snippet.label_key
    if group_label_key == "tag.group.html":
        return _html_category_key(label_key)
    if group_label_key == "tag.group.markdown":
        return _markdown_category_key(label_key)
    if group_label_key == "tag.group.wordpress_html":
        return _wordpress_category_key(label_key)
    return "tag.category.utility"


def _preferred_group_label_key(save_file_path: Path | None) -> str | None:
    if save_file_path is None:
        return None

    suffixes = [suffix.lower() for suffix in save_file_path.suffixes]
    file_name = save_file_path.name.lower()
    if file_name.endswith(".wp.html"):
        return "tag.group.wordpress_html"
    if ".md" in suffixes or ".markdown" in suffixes:
        return "tag.group.markdown"
    if ".html" in suffixes or ".htm" in suffixes:
        return "tag.group.html"
    return None


def _html_category_key(label_key: str) -> str:
    if label_key in {
        "tag.html.paragraph",
        "tag.html.heading2",
        "tag.html.heading3",
    }:
        return "tag.category.basic"
    if label_key in {
        "tag.html.link",
        "tag.html.link_blank",
        "tag.html.image",
        "tag.html.figure",
    }:
        return "tag.category.link_image"
    if label_key in {
        "tag.html.unordered_list",
        "tag.html.ordered_list",
    }:
        return "tag.category.lists"
    if label_key in {
        "tag.html.code",
        "tag.html.pre_code",
    }:
        return "tag.category.code"
    if label_key in {
        "tag.html.div",
        "tag.html.span",
    }:
        return "tag.category.layout"
    return "tag.category.utility"


def _markdown_category_key(label_key: str) -> str:
    if label_key in {
        "tag.markdown.heading2",
        "tag.markdown.heading3",
        "tag.markdown.bold",
        "tag.markdown.italic",
    }:
        return "tag.category.text"
    if label_key in {
        "tag.markdown.link",
        "tag.markdown.image",
    }:
        return "tag.category.link_image"
    if label_key in {
        "tag.markdown.inline_code",
        "tag.markdown.code_block",
        "tag.markdown.code_block_python",
        "tag.markdown.code_block_html",
        "tag.markdown.code_block_css",
        "tag.markdown.code_block_javascript",
        "tag.markdown.code_block_json",
        "tag.markdown.code_block_powershell",
        "tag.markdown.code_block_bash",
        "tag.markdown.code_block_sql",
    }:
        return "tag.category.code"
    if label_key in {
        "tag.markdown.quote",
        "tag.markdown.bullet",
        "tag.markdown.numbered",
    }:
        return "tag.category.lists"
    return "tag.category.utility"


def _wordpress_category_key(label_key: str) -> str:
    if label_key in {
        "tag.wordpress.paragraph_block",
        "tag.wordpress.heading2_block",
        "tag.wordpress.heading3_block",
        "tag.wordpress.list_block",
        "tag.wordpress.quote_block",
    }:
        return "tag.category.text"
    if label_key in {
        "tag.wordpress.code_block",
        "tag.wordpress.preformatted_block",
        "tag.wordpress.html_code_box",
    }:
        return "tag.category.code"
    if label_key in {
        "tag.wordpress.separator_block",
        "tag.wordpress.spacer_block",
        "tag.wordpress.buttons_block",
    }:
        return "tag.category.layout"
    return "tag.category.utility"


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
    if not label_key.strip() or not hint_key.strip() or not template:
        raise ValueError(
            "Dictionary item requires non-empty label_key, hint_key, and template: "
            f"{load_file_path}"
        )
    cursor_count = template.count(CURSOR_PLACEHOLDER)
    if cursor_count > 1:
        raise ValueError(
            f"Dictionary item has duplicated cursor placeholder: {load_file_path}"
        )
    unknown_placeholders = sorted(
        {
            placeholder
            for placeholder in PLACEHOLDER_PATTERN.findall(template)
            if placeholder not in VALID_PLACEHOLDERS
        }
    )
    if unknown_placeholders:
        raise ValueError(
            "Dictionary item has unknown placeholder(s) "
            f"{', '.join(unknown_placeholders)}: {load_file_path}"
        )
    return TagSnippet(label_key, hint_key, template)
