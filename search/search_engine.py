from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern


@dataclass(frozen=True)
class SearchOptions:
    case_sensitive: bool = False
    regular_expression: bool = False
    whole_word: bool = False


@dataclass(frozen=True)
class SearchMatch:
    start: int
    end: int
    text: str


class SearchEngine:
    def find_all(
        self,
        source_text: str,
        search_text: str,
        options: SearchOptions | None = None,
    ) -> list[SearchMatch]:
        if not search_text:
            return []

        pattern = self._compile_pattern(search_text, options or SearchOptions())
        return [
            SearchMatch(match.start(), match.end(), match.group(0))
            for match in pattern.finditer(source_text)
        ]

    def _compile_pattern(
        self,
        search_text: str,
        options: SearchOptions,
    ) -> Pattern[str]:
        pattern_text = search_text if options.regular_expression else re.escape(search_text)
        if options.whole_word:
            pattern_text = rf"\b(?:{pattern_text})\b"

        flags = 0 if options.case_sensitive else re.IGNORECASE
        return re.compile(pattern_text, flags)
