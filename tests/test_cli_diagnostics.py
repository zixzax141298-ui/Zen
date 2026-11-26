from types import SimpleNamespace

import pytest

from zen.ast.source_span import SourceSpan
from zen.ast.source_identity import SourceIdentifier
from zen.ast.source_location import SourceLocation
from zen.ast.validation import Diagnostic, DiagnosticSeverity
from zen.cli import (
    dump_ast,
    dump_tokens,
    fingerprint_file,
    format_source,
    run_file,
    run_repl,
)
from zen.cli_core.diagnostics import (
    diagnostic_from_exception,
    diagnostic_to_dict,
    diagnostics_payload,
    format_diagnostic,
)
from zen.parser.diagnostics import ParseError
from zen.semantic.diagnostics import (
    SemanticDiagnostic,
    SemanticError,
    ZSS_S001_UNDEFINED,
)


def test_lexer_error_normalization_does_not_invent_span():
    error = SimpleNamespace(
        message="unexpected character",
        line=3,
        column=7,
    )

    from zen.cli_core.diagnostics import diagnostic_from_lexer_error
    diagnostic = diagnostic_from_lexer_error(error)

    assert diagnostic.code == "LEXER_ERROR"
    assert diagnostic.component == "Lexer"
    assert diagnostic.line == 3
    assert diagnostic.column == 7
    assert diagnostic.source_location is None


def test_parser_error_uses_existing_common_adapter():
    error = ParseError("expected expression", 2, 4)

    diagnostic = diagnostic_from_exception(error)

    assert diagnostic.code == "PARSER_ERROR"
    assert diagnostic.component == "Parser"
    assert diagnostic.line == 2
    assert diagnostic.column == 4


def test_semantic_error_preserves_stable_code_and_location():
    span = SourceSpan(4, 2, 4, 5)
    semantic = SemanticDiagnostic(
        code=ZSS_S001_UNDEFINED,
        message="undefined variable",
        span=span,
    )
    error = SemanticError("undefined variable", semantic)

    diagnostic = diagnostic_from_exception(error)

    assert diagnostic.code == ZSS_S001_UNDEFINED
    assert diagnostic.component == "SemanticAnalysis"
    assert diagnostic.line == 4
    assert diagnostic.column == 2


def test_diagnostic_serialization_is_json_compatible():
    diagnostic = Diagnostic(
        code="TEST001",
        message="example",
        severity=DiagnosticSeverity.ERROR,
        component="Tests",
        line=5,
        column=9,
    )

    payload = diagnostic_to_dict(diagnostic)

    assert payload["code"] == "TEST001"
    assert payload["severity"] == "error"
    assert payload["line"] == 5
    assert payload["column"] == 9
    assert payload["location"] is None
    assert payload["related_locations"] == []
    assert diagnostics_payload((diagnostic,)) == [payload]


def test_source_location_serialization_uses_half_open_coordinates():
    source_id = SourceIdentifier("diagnostic-test")
    span = SourceSpan(1, 2, 1, 6)
    diagnostic = Diagnostic(
        code="TEST002",
        message="located",
        component="Tests",
        source_location=SourceLocation(source_id, span),
    )

    payload = diagnostic_to_dict(diagnostic)

    assert payload["location"] == {
        "start": {"line": 1, "column": 2},
        "end": {"line": 1, "column": 6},
    }


def test_human_diagnostic_format_includes_path_code_and_location():
    diagnostic = Diagnostic(
        code="PARSER_ERROR",
        message="expected expression",
        component="Parser",
        line=8,
        column=3,
    )

    assert format_diagnostic(
        "sample.zen", diagnostic
    ) == (
        "zen: sample.zen: line 8, column 3: "
        "error[PARSER_ERROR]: expected expression"
    )


def test_unsupported_exception_is_rejected():
    with pytest.raises(TypeError):
        diagnostic_from_exception(RuntimeError("unrelated"))


@pytest.mark.parametrize(
    ("command", "source_text", "expected_code"),
    [
        (dump_ast, "let = 1\n", "PARSER_ERROR"),
        (fingerprint_file, "let = 1\n", "PARSER_ERROR"),
        (format_source, "let = 1\n", "PARSER_ERROR"),
        (dump_tokens, "@\n", "LEXER_ERROR"),
    ],
)
def test_frontend_commands_emit_normalized_diagnostics(
    tmp_path,
    command,
    source_text,
    expected_code,
):
    from io import StringIO

    source = tmp_path / "invalid.zen"
    source.write_text(source_text, encoding="utf-8")
    output = StringIO()
    error = StringIO()

    result = command(source, output=output, error=error)

    assert result != 0
    assert expected_code in error.getvalue()
    assert "line" in error.getvalue()


@pytest.mark.parametrize(
    ("source_text", "expected_code"),
    [
        ("let = 1\n", "PARSER_ERROR"),
        ("unknown_name\n", ZSS_S001_UNDEFINED),
    ],
)
def test_run_file_json_validation_errors_include_legacy_and_diagnostic_fields(
    tmp_path,
    source_text,
    expected_code,
):
    import json
    from io import StringIO

    source = tmp_path / "invalid.zen"
    source.write_text(source_text, encoding="utf-8")
    output = StringIO()
    error = StringIO()

    result = run_file(
        source,
        output=output,
        error=error,
        json_output=True,
    )

    payload = json.loads(output.getvalue())

    assert result != 0
    assert payload["schema_version"] == 1
    assert payload["file"] == str(source)
    assert payload["status"] == "error"
    assert payload["phase"] == "validate"
    assert isinstance(payload["message"], str)
    assert payload["diagnostics"]
    assert payload["diagnostics"][0]["code"] == expected_code
    assert payload["diagnostics"][0]["severity"] == "error"


def test_run_file_json_runtime_errors_include_diagnostic(tmp_path):
    import json
    from io import StringIO

    source = tmp_path / "runtime_error.zen"
    source.write_text("1 / 0\n", encoding="utf-8")
    output = StringIO()

    result = run_file(source, json_output=True, output=output)
    payload = json.loads(output.getvalue())

    assert result != 0
    assert payload["schema_version"] == 1
    assert payload["file"] == str(source)
    assert payload["status"] == "error"
    assert payload["phase"] == "runtime"
    assert "Division by zero" in payload["message"]

    diagnostic = payload["diagnostics"][0]
    assert diagnostic["code"] == "RUNTIME_ERROR"
    assert diagnostic["component"] == "Runtime"
    assert diagnostic["severity"] == "error"
    assert diagnostic["column"] is None


def test_repl_frontend_errors_render_normalized_diagnostics():
    from io import StringIO

    commands = iter(["let = 1", ":quit"])
    output = StringIO()

    result = run_repl(
        input_fn=lambda _prompt: next(commands),
        output=output,
    )

    rendered = output.getvalue()
    assert result == 0
    assert "PARSER_ERROR" in rendered
    assert "<repl>" in rendered
    assert "line 1" in rendered
