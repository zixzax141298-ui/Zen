"""Source positions and half-open source spans for Zen syntax trees."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class SourcePosition:
    """A 1-based source position ordered lexicographically by line/column."""

    line: int
    column: int

    def __post_init__(self) -> None:
        if type(self.line) is not int or type(self.column) is not int:
            raise TypeError("SourcePosition coordinates must be integers")
        if self.line < 1 or self.column < 1:
            raise ValueError("SourcePosition coordinates must be positive")


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """A half-open source range: start inclusive, end exclusive.

    Lines and columns are 1-based. Columns count Python Unicode code points.
    """

    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def __post_init__(self) -> None:
        values = (self.start_line, self.start_column, self.end_line, self.end_column)
        if any(type(value) is not int for value in values):
            raise TypeError("SourceSpan positions must be integers")
        if self.start_line < 1 or self.start_column < 1:
            raise ValueError("SourceSpan start positions must be positive")
        if self.end_line < 1 or self.end_column < 1:
            raise ValueError("SourceSpan end positions must be positive")
        if self.end < self.start:
            raise ValueError("SourceSpan end cannot precede its start")

    @property
    def start(self) -> SourcePosition:
        return SourcePosition(self.start_line, self.start_column)

    @property
    def end(self) -> SourcePosition:
        return SourcePosition(self.end_line, self.end_column)

    def contains(self, other: "SourceSpan") -> bool:
        """Return whether ``other`` is fully contained in this half-open span."""
        if not isinstance(other, SourceSpan):
            raise TypeError("contains() requires a SourceSpan")
        return self.start <= other.start and other.end <= self.end
