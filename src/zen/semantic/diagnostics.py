"""Semantic diagnostics and structured error catalog (OQ-09)."""

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


# Stable diagnostic codes (OQ-09)
ZSS_S001_UNDEFINED = "ZSS-S001"
ZSS_S002_DUPLICATE = "ZSS-S002"
ZSS_S003_UNINITIALIZED = "ZSS-S003"
ZSS_S004_CONST_ASSIGN = "ZSS-S004"
ZSS_S005_NOT_CALLABLE = "ZSS-S005"
ZSS_S006_ARITY = "ZSS-S006"
ZSS_S007_DUP_PARAM = "ZSS-S007"
ZSS_S008_RETURN_OUTSIDE = "ZSS-S008"


@dataclass(frozen=True, slots=True)
class SemanticDiagnostic:
    code: str
    message: str
    severity: SemanticSeverity = SemanticSeverity.ERROR
    span: SourceSpan | None = None
    symbol: str | None = None
    related_span: SourceSpan | None = None
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
    """Raised when semantic analysis fails closed on hard errors."""

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
