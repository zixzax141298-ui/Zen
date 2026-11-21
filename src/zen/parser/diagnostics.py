"""Source-located parser errors with a common diagnostic representation."""

from dataclasses import dataclass, field

from zen.ast.source_identity import SourceIdentifier
from zen.ast.source_location import SourceLocation
from zen.ast.source_span import SourceSpan
from zen.ast.validation import Diagnostic, DiagnosticSeverity


@dataclass(frozen=True, slots=True)
class ParseError(Exception):
    message: str
    line: int
    column: int
    span: SourceSpan | None = None
    source_id: SourceIdentifier | None = field(
        default=None,
        kw_only=True,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.message, str) or not self.message:
            raise ValueError("ParseError message must be non-empty")

        if type(self.line) is not int or self.line < 1:
            raise ValueError(
                "ParseError line must be a positive integer"
            )

        if type(self.column) is not int or self.column < 1:
            raise ValueError(
                "ParseError column must be a positive integer"
            )

        if self.span is not None and not isinstance(
            self.span,
            SourceSpan,
        ):
            raise TypeError(
                "ParseError span must be a SourceSpan or None"
            )

        if self.span is not None:
            self.span.__post_init__()

        if (
            self.source_id is not None
            and not isinstance(self.source_id, SourceIdentifier)
        ):
            raise TypeError(
                "ParseError source_id must be a SourceIdentifier or None"
            )

        Exception.__init__(self, self.message)

    def __str__(self) -> str:
        return (
            f"{self.message} at line {self.line}, "
            f"column {self.column}"
        )

    def as_diagnostic(self) -> Diagnostic:
        location = None

        if self.source_id is not None and self.span is not None:
            location = SourceLocation(
                self.source_id,
                self.span,
            )

        return Diagnostic(
            code="PARSER_ERROR",
            message=self.message,
            severity=DiagnosticSeverity.ERROR,
            component="Parser",
            source_location=location,
            line=self.line,
            column=self.column,
        )
