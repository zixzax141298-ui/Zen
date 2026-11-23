"""Semantic diagnostics and errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from zen.ast.source_identity import SourceIdentifier
from zen.ast.source_location import SourceLocation
from zen.ast.source_span import SourceSpan
from zen.ast.validation import Diagnostic, DiagnosticSeverity


class SemanticSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class SemanticDiagnostic:
    code: str
    message: str
    severity: SemanticSeverity = SemanticSeverity.ERROR
    span: SourceSpan | None = None
    source_id: SourceIdentifier | None = field(default=None, kw_only=True)

    def as_diagnostic(self) -> Diagnostic:
        location = None
        if self.source_id is not None and self.span is not None:
            location = SourceLocation(self.source_id, self.span)
        return Diagnostic(
            code=self.code,
            message=self.message,
            severity=(
                DiagnosticSeverity.ERROR
                if self.severity is SemanticSeverity.ERROR
                else DiagnosticSeverity.WARNING
            ),
            component="SemanticAnalysis",
            source_location=location,
            line=self.span.start_line if self.span else 1,
            column=self.span.start_column if self.span else 1,
        )


@dataclass(frozen=True, slots=True)
class SemanticError(Exception):
    """Raised when semantic analysis fails closed on the first error.

    Matches the project strict-error policy: first semantic error stops
    the current program analysis.
    """

    message: str
    diagnostic: SemanticDiagnostic

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)

    def __str__(self) -> str:
        d = self.diagnostic
        if d.span is not None:
            return (
                f"{self.message} at line {d.span.start_line}, "
                f"column {d.span.start_column}"
            )
        return self.message
