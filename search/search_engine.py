from __future__ import annotations

import re
from dataclasses import dataclass
from re import Match, Pattern


@dataclass(frozen=True)
class SearchOptions:
    case_sensitive: bool = False
    regular_expression: bool = False
    whole_word: bool = False
    selected_only: bool = False


@dataclass(frozen=True)
class SearchMatch:
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class ReplaceResult:
    text: str
    count: int


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
            if match.start() != match.end()
        ]

    def find_next(
        self,
        source_text: str,
        search_text: str,
        start_position: int,
        options: SearchOptions | None = None,
    ) -> SearchMatch | None:
        if not search_text:
            return None

        pattern = self._compile_pattern(search_text, options or SearchOptions())
        bounded_start_position = min(max(start_position, 0), len(source_text))
        match = self._first_non_empty_match(
            pattern,
            source_text,
            bounded_start_position,
        )
        if match is None and bounded_start_position > 0:
            match = self._first_non_empty_match(pattern, source_text, 0)

        if match is None:
            return None
        return SearchMatch(match.start(), match.end(), match.group(0))

    def replace_all(
        self,
        source_text: str,
        search_text: str,
        replace_text: str,
        options: SearchOptions | None = None,
    ) -> ReplaceResult:
        if not search_text:
            return ReplaceResult(source_text, 0)

        pattern = self._compile_pattern(search_text, options or SearchOptions())
        replaced_text, count = pattern.subn(replace_text, source_text)
        return ReplaceResult(replaced_text, count)

    def replace_match(
        self,
        source_text: str,
        match: SearchMatch,
        replace_text: str,
        search_text: str,
        options: SearchOptions | None = None,
    ) -> ReplaceResult:
        pattern = self._compile_pattern(search_text, options or SearchOptions())
        target_text = source_text[match.start : match.end]
        replaced_text, count = pattern.subn(replace_text, target_text, count=1)
        if count == 0:
            return ReplaceResult(source_text, 0)

        return ReplaceResult(
            source_text[: match.start] + replaced_text + source_text[match.end :],
            count,
        )

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

    def _first_non_empty_match(
        self,
        pattern: Pattern[str],
        source_text: str,
        start_position: int,
    ) -> Match[str] | None:
        for match in pattern.finditer(source_text, start_position):
            if match.start() != match.end():
                return match
        return None
