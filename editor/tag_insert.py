from __future__ import annotations

from dataclasses import dataclass

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


def tag_snippet_groups() -> tuple[TagSnippetGroup, ...]:
    return (
        TagSnippetGroup(
            "tag.group.html",
            (
                TagSnippet(
                    "tag.html.paragraph",
                    "tag.hint.html.paragraph",
                    "<p>{selection}{cursor}</p>",
                ),
                TagSnippet(
                    "tag.html.link",
                    "tag.hint.html.link",
                    '<a href="{cursor}">{selection}</a>',
                ),
                TagSnippet(
                    "tag.html.image",
                    "tag.hint.html.image",
                    '<img src="{cursor}" alt="">',
                ),
                TagSnippet(
                    "tag.html.div",
                    "tag.hint.html.div",
                    "<div>{selection}{cursor}</div>",
                ),
            ),
        ),
        TagSnippetGroup(
            "tag.group.markdown",
            (
                TagSnippet(
                    "tag.markdown.bold",
                    "tag.hint.markdown.bold",
                    "**{selection}{cursor}**",
                ),
                TagSnippet(
                    "tag.markdown.link",
                    "tag.hint.markdown.link",
                    "[{selection}]({cursor})",
                ),
                TagSnippet(
                    "tag.markdown.inline_code",
                    "tag.hint.markdown.inline_code",
                    "`{selection}{cursor}`",
                ),
            ),
        ),
        TagSnippetGroup(
            "tag.group.wordpress_html",
            (
                TagSnippet(
                    "tag.wordpress.paragraph_block",
                    "tag.hint.wordpress.paragraph_block",
                    "<!-- wp:paragraph -->\n<p>{selection}{cursor}</p>\n<!-- /wp:paragraph -->",
                ),
                TagSnippet(
                    "tag.wordpress.heading_block",
                    "tag.hint.wordpress.heading_block",
                    "<!-- wp:heading -->\n<h2>{selection}{cursor}</h2>\n<!-- /wp:heading -->",
                ),
            ),
        ),
    )
