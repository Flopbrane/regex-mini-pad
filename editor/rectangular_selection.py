from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RectangularSelection:
    start_line: int
    start_column: int
    end_line: int
    end_column: int
