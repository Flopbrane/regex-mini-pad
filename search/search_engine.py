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
    visible_only: bool = False


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
        *,
        max_matches: int | None = None,
    ) -> list[SearchMatch]:
        if not search_text:
            return []

        pattern = self._compile_pattern(search_text, options or SearchOptions())
        matches: list[SearchMatch] = []
        for match in pattern.finditer(source_text):
            if match.start() == match.end():
                continue
            matches.append(SearchMatch(match.start(), match.end(), match.group(0)))
            if max_matches is not None and len(matches) >= max_matches:
                break
        return matches

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

    def find_previous(
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
        match = self._last_non_empty_match(
            pattern,
            source_text,
            0,
            bounded_start_position,
        )
        if match is None and bounded_start_position < len(source_text):
            match = self._last_non_empty_match(
                pattern,
                source_text,
                bounded_start_position,
                len(source_text),
            )

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

        search_options = options or SearchOptions()
        pattern = self._compile_pattern(search_text, search_options)
        replacement_text = self._replacement_text_for_options(replace_text, search_options)
        replaced_text, count = pattern.subn(replacement_text, source_text)
        return ReplaceResult(replaced_text, count)

    def replace_match(
        self,
        source_text: str,
        match: SearchMatch,
        replace_text: str,
        search_text: str,
        options: SearchOptions | None = None,
    ) -> ReplaceResult:
        search_options = options or SearchOptions()
        pattern = self._compile_pattern(search_text, search_options)
        replacement_text = self._replacement_text_for_options(replace_text, search_options)
        target_text = source_text[match.start : match.end]
        replaced_text, count = pattern.subn(replacement_text, target_text, count=1)
        if count == 0:
            return ReplaceResult(source_text, 0)

        return ReplaceResult(
            source_text[: match.start] + replaced_text + source_text[match.end :],
            count,
        )

    def preview_replacement(
        self,
        match_text: str,
        search_text: str,
        replace_text: str,
        options: SearchOptions | None = None,
    ) -> ReplaceResult:
        if not search_text:
            return ReplaceResult(match_text, 0)

        search_options = options or SearchOptions()
        pattern = self._compile_pattern(search_text, search_options)
        replacement_text = self._replacement_text_for_options(replace_text, search_options)
        replaced_text, count = pattern.subn(replacement_text, match_text, count=1)
        return ReplaceResult(replaced_text, count)

    def _compile_pattern(
        self,
        search_text: str,
        options: SearchOptions,
    ) -> Pattern[str]:
        pattern_text = search_text if options.regular_expression else re.escape(search_text)
        if options.whole_word:
            pattern_text = rf"\b(?:{pattern_text})\b"

        flags = re.MULTILINE if options.regular_expression else 0
        if not options.case_sensitive:
            flags |= re.IGNORECASE
        return re.compile(pattern_text, flags)

    def _replacement_text_for_options(
        self,
        replace_text: str,
        options: SearchOptions,
    ) -> str:
        if not options.regular_expression:
            return replace_text
        return convert_dollar_replacement_references(replace_text)

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

    def _last_non_empty_match(
        self,
        pattern: Pattern[str],
        source_text: str,
        start_position: int,
        end_position: int,
    ) -> Match[str] | None:
        last_match: Match[str] | None = None
        for match in pattern.finditer(source_text, start_position, end_position):
            if match.start() != match.end():
                last_match = match
        return last_match


def convert_dollar_replacement_references(replace_text: str) -> str:
    converted: list[str] = []
    index = 0
    while index < len(replace_text):
        character = replace_text[index]
        if character != "$":
            converted.append(character)
            index += 1
            continue

        next_index = index + 1
        if next_index >= len(replace_text):
            converted.append(character)
            index += 1
            continue

        next_character = replace_text[next_index]
        if next_character == "$":
            converted.append("$")
            index += 2
            continue

        if next_character.isdigit():
            group_end = next_index + 1
            while group_end < len(replace_text) and replace_text[group_end].isdigit():
                group_end += 1
            converted.append(rf"\g<{replace_text[next_index:group_end]}>")
            index = group_end
            continue

        if next_character == "{":
            closing_index = replace_text.find("}", next_index + 1)
            if closing_index != -1:
                group_name = replace_text[next_index + 1 : closing_index]
                if group_name.isidentifier() or group_name.isdigit():
                    converted.append(rf"\g<{group_name}>")
                    index = closing_index + 1
                    continue

        converted.append(character)
        index += 1
    return "".join(converted)
