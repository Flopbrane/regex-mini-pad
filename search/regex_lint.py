from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern


@dataclass(frozen=True)
class RegexLintMessage:
    severity: str
    message: str


class RegexLint:
    def lint(
        self,
        pattern_text: str,
        replacement_text: str = "",
        *,
        check_replacement: bool = False,
    ) -> list[RegexLintMessage]:
        messages: list[RegexLintMessage] = []
        if not pattern_text:
            return [RegexLintMessage("warning", "Search pattern is empty.")]

        pattern = self._compile_pattern(pattern_text, messages)
        if pattern is None:
            return messages

        self._warn_about_empty_matches(pattern, messages)
        self._warn_about_broad_patterns(pattern_text, messages)

        if check_replacement:
            self._check_replacement(pattern, replacement_text, messages)

        return messages

    def _compile_pattern(
        self,
        pattern_text: str,
        messages: list[RegexLintMessage],
    ) -> Pattern[str] | None:
        try:
            return re.compile(pattern_text)
        except re.error as error:
            messages.append(
                RegexLintMessage("error", f"Invalid regular expression: {error}")
            )
            return None

    def _warn_about_empty_matches(
        self,
        pattern: Pattern[str],
        messages: list[RegexLintMessage],
    ) -> None:
        if pattern.match("") is not None:
            messages.append(
                RegexLintMessage(
                    "warning",
                    "This pattern can match empty text. Empty matches are skipped.",
                )
            )

    def _warn_about_broad_patterns(
        self,
        pattern_text: str,
        messages: list[RegexLintMessage],
    ) -> None:
        if pattern_text in {".*", ".*?", "^.*$", "^.*?$"}:
            messages.append(
                RegexLintMessage(
                    "warning",
                    "This pattern can match very broad ranges of text.",
                )
            )
        if pattern_text.startswith(".*") and len(pattern_text) > 2:
            messages.append(
                RegexLintMessage(
                    "warning",
                    "A leading .* can make searches slower and less precise.",
                )
            )

    def _check_replacement(
        self,
        pattern: Pattern[str],
        replacement_text: str,
        messages: list[RegexLintMessage],
    ) -> None:
        try:
            pattern.sub(replacement_text, "", count=1)
        except re.error as error:
            messages.append(
                RegexLintMessage("error", f"Invalid replacement text: {error}")
            )
