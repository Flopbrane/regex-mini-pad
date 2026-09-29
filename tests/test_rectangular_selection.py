from editor.rectangular_selection import (
    RectangularSelection,
    rectangular_selection_from_text_positions,
    rectangular_text,
)


def test_rectangular_selection_from_text_positions() -> None:
    source_text = "abcd\nwxyz\n1234"

    selection = rectangular_selection_from_text_positions(source_text, 1, 8)

    assert selection == RectangularSelection(
        start_line=0,
        start_column=1,
        end_line=1,
        end_column=3,
    )


def test_rectangular_text_copies_same_columns_from_each_line() -> None:
    source_text = "abcd\nwxyz\n1234"
    selection = RectangularSelection(
        start_line=0,
        start_column=1,
        end_line=2,
        end_column=3,
    )

    assert rectangular_text(source_text, selection) == "bc\nxy\n23"


def test_rectangular_text_keeps_short_lines_as_empty_cells() -> None:
    source_text = "abcd\nx\n1234"
    selection = RectangularSelection(
        start_line=0,
        start_column=2,
        end_line=2,
        end_column=4,
    )

    assert rectangular_text(source_text, selection) == "cd\n\n34"
