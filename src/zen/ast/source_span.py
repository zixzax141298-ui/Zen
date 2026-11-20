"""Source location spans for Zen syntax tree nodes."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A source range with an exclusive end position.

    Lines and columns are 1-based. Columns count Python Unicode code points.
    The end position is exclusive.
    """

    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def __post_init__(self) -> None:
        values = (
            self.start_line,
            self.start_column,
            self.end_line,
            self.end_column,
        )
        if any(type(value) is not int for value in values):
            raise TypeError("SourceSpan positions must be integers")

        if self.start_line < 1 or self.start_column < 1:
            raise ValueError("SourceSpan start positions must be positive")

        if self.end_line < 1 or self.end_column < 1:
            raise ValueError("SourceSpan end positions must be positive")

        if (self.end_line, self.end_column) < (
            self.start_line,
            self.start_column,
        ):
            raise ValueError("SourceSpan end cannot precede its start")
