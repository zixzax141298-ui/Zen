"""CLI adapters and stable JSON serialization for Zen diagnostics."""

from __future__ import annotations

from typing import Any

from zen.ast.validation import Diagnostic, DiagnosticSeverity


def _location_payload(location: Any) -> dict[str, Any]:
    span = location.span
    return {
        "start": {
            "line": span.start_line,
            "column": span.start_column,
        },
        "end": {
            "line": span.end_line,
            "column": span.end_column,
        },
    }


def diagnostic_from_lexer_error(error: BaseException) -> Diagnostic:
    """Normalize a lexer error without inventing unavailable source spans."""
    return Diagnostic(
        code="LEXER_ERROR",
        message=str(error.message),
        severity=DiagnosticSeverity.ERROR,
        component="Lexer",
        line=error.line,
        column=error.column,
    )


def diagnostic_from_exception(error: BaseException) -> Diagnostic:
    """Convert supported frontend exceptions to the common model."""
    from zen import LexerError, ParseError, SemanticError
    from zen import RuntimeError as ZenRuntimeError

    if isinstance(error, LexerError):
        return diagnostic_from_lexer_error(error)

    if isinstance(error, ParseError):
        return error.as_diagnostic()

    if isinstance(error, SemanticError):
        return error.diagnostic.as_diagnostic()

    if isinstance(error, ZenRuntimeError):
        return Diagnostic(
            code="RUNTIME_ERROR",
            message=str(error),
            severity=DiagnosticSeverity.ERROR,
            component="Runtime",
            line=getattr(error, "line", None),
        )

    if isinstance(error, ValueError):
        return Diagnostic(
            code="CLI_VALIDATION_ERROR",
            message=str(error),
            severity=DiagnosticSeverity.ERROR,
            component="Validation",
        )

    raise TypeError(
        f"unsupported diagnostic exception: {type(error).__name__}"
    )


def diagnostic_to_dict(diagnostic: Diagnostic) -> dict[str, Any]:
    """Serialize the common diagnostic model without exposing source IDs."""
    location = diagnostic.source_location

    result: dict[str, Any] = {
        "code": diagnostic.code,
        "message": diagnostic.message,
        "severity": diagnostic.severity.value,
        "component": diagnostic.component,
        "line": diagnostic.line,
        "column": diagnostic.column,
        "location": (
            _location_payload(location) if location is not None else None
        ),
        "related_locations": [
            _location_payload(item)
            for item in diagnostic.related_locations
        ],
    }
    return result


def diagnostics_payload(
    diagnostics: tuple[Diagnostic, ...] | list[Diagnostic],
) -> list[dict[str, Any]]:
    return [diagnostic_to_dict(item) for item in diagnostics]


def format_diagnostic(path: str, diagnostic: Diagnostic) -> str:
    """Render one stable, human-readable CLI diagnostic."""
    if diagnostic.line is not None and diagnostic.column is not None:
        location = (
            f"{path}: line {diagnostic.line}, "
            f"column {diagnostic.column}"
        )
    elif diagnostic.line is not None:
        location = f"{path}: line {diagnostic.line}"
    else:
        location = path

    return (
        f"zen: {location}: "
        f"{diagnostic.severity.value}[{diagnostic.code}]: "
        f"{diagnostic.message}"
    )
