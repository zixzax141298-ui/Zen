"""Source-located parser diagnostics; no grammar implementation is provided."""

from dataclasses import dataclass

from zen.ast.source_span import SourceSpan


@dataclass(frozen=True, slots=True)
class ParseError(Exception):
    message: str
    line: int
    column: int
    span: SourceSpan | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.message, str) or not self.message:
            raise ValueError("ParseError message must be non-empty")
        if type(self.line) is not int or self.line < 1:
            raise ValueError("ParseError line must be a positive integer")
        if type(self.column) is not int or self.column < 1:
            raise ValueError("ParseError column must be a positive integer")
        if self.span is not None and not isinstance(self.span, SourceSpan):
            raise TypeError("ParseError span must be a SourceSpan or None")
        Exception.__init__(self, self.message)

    def __str__(self) -> str:
        return f"{self.message} at line {self.line}, column {self.column}"
