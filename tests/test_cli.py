from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from zen.runtime import RuntimeError

from zen.cli import main, run_file, run_repl


def test_run_file_prints_final_expression(tmp_path: Path, capsys):
    source = tmp_path / "hello.zen"
    source.write_text("40 + 2\n", encoding="utf-8")

    assert run_file(source) == 0

    captured = capsys.readouterr()
    assert captured.out == "42\n"
    assert captured.err == ""


def test_run_file_reports_language_errors(tmp_path: Path, capsys):
    source = tmp_path / "broken.zen"
    source.write_text("let = 1\n", encoding="utf-8")

    assert run_file(source) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "zen:" in captured.err
    assert "line" in captured.err


def test_run_file_rejects_non_zen_extension(tmp_path: Path, capsys):
    source = tmp_path / "program.txt"
    source.write_text("42", encoding="utf-8")

    assert run_file(source) == 2
    assert ".zen" in capsys.readouterr().err


def test_run_file_reports_missing_file(tmp_path: Path, capsys):
    assert run_file(tmp_path / "missing.zen") == 1
    assert "cannot read" in capsys.readouterr().err


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("zen ")


def test_repl_keeps_variables_between_submissions():
    commands = iter(["let answer = 40", "answer + 2", ":quit"])
    output = StringIO()

    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0

    rendered = output.getvalue()
    assert "42" in rendered
    assert "Goodbye." in rendered


def test_repl_supports_multiline_functions():
    commands = iter(
        [
            "fn add(a, b) {",
            "  return a + b",
            "}",
            "add(20, 22)",
            ":quit",
        ]
    )
    output = StringIO()

    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0
    assert "42" in output.getvalue()


def test_repl_recovers_after_invalid_submission():
    commands = iter(["let = 1", "40 + 2", ":quit"])
    output = StringIO()

    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0

    rendered = output.getvalue()
    assert "zen:" in rendered
    assert "42" in rendered

def test_repl_does_not_reexecute_previous_statements(monkeypatch):
    from zen.runtime.interpreter import Interpreter as RealInterpreter

    instances = []
    interpreted_statement_counts = []

    class RecordingInterpreter(RealInterpreter):
        def __init__(self):
            super().__init__()
            instances.append(self)

        def interpret(self, program):
            interpreted_statement_counts.append(len(program.statements))
            return super().interpret(program)

    monkeypatch.setattr("zen.cli.Interpreter", RecordingInterpreter)

    commands = iter(
        [
            "let counter = 0",
            "counter = counter + 1",
            "counter = counter + 1",
            "counter",
            ":quit",
        ]
    )
    output = StringIO()

    assert run_repl(
        input_fn=lambda _prompt: next(commands),
        output=output,
    ) == 0

    assert len(instances) == 1
    assert interpreted_statement_counts == [1, 1, 1, 1]
    assert output.getvalue().splitlines().count("2") == 2


def test_repl_rolls_back_global_state_after_runtime_error():
    commands = iter(
        [
            "let counter = 1",
            "counter = 2",
            "1 / 0",
            "counter",
            ":quit",
        ]
    )
    output = StringIO()

    assert run_repl(
        input_fn=lambda _prompt: next(commands),
        output=output,
    ) == 0

    rendered = output.getvalue()
    assert "Division by zero" in rendered
    assert rendered.splitlines().count("2") == 2


def test_repl_reset_clears_previous_variables():
    commands = iter(
        [
            "let counter = 10",
            ":reset",
            "counter",
            ":quit",
        ]
    )
    output = StringIO()

    assert run_repl(
        input_fn=lambda _prompt: next(commands),
        output=output,
    ) == 0

    rendered = output.getvalue()
    assert "Session reset." in rendered
    assert "Undefined identifier 'counter'" in rendered
# CORE-01 regression coverage: failed REPL submissions are transactional.

def test_repl_rolls_back_partial_assignment_and_preserves_session_metadata():
    from zen.cli import _ReplSession

    session = _ReplSession()
    session.execute_submission("let counter = 2")

    previous_source = session.source
    previous_statement_count = session.statement_count

    with pytest.raises(RuntimeError, match="Division by zero"):
        session.execute_submission("counter = 3\n1 / 0")

    assert session.interpreter.globals.get("counter") == 2
    assert session.source == previous_source
    assert session.statement_count == previous_statement_count

    assert session.execute_submission("counter = counter + 1") == 3
    assert session.execute_submission("counter") == 3


@pytest.mark.parametrize(
    ("submission", "name", "is_constant"),
    [
        ("let transient = 9\n1 / 0", "transient", False),
        ("const transient_const = 9\n1 / 0", "transient_const", True),
        (
            "fn transient_fn() { return 1 }\n1 / 0",
            "transient_fn",
            False,
        ),
    ],
)
def test_repl_rolls_back_new_global_declarations(
    submission,
    name,
    is_constant,
):
    from zen.cli import _ReplSession

    session = _ReplSession()

    with pytest.raises(RuntimeError, match="Division by zero"):
        session.execute_submission(submission)

    assert name not in session.interpreter.globals.values

    if is_constant:
        assert name not in session.interpreter.globals.constants


def test_repl_rolls_back_global_mutation_through_function():
    from zen.cli import _ReplSession

    session = _ReplSession()
    session.execute_submission(
        "let counter = 2\n"
        "fn bump() {\n"
        "  counter = counter + 1\n"
        "}"
    )

    with pytest.raises(RuntimeError, match="Division by zero"):
        session.execute_submission("bump()\n1 / 0")

    assert session.interpreter.globals.get("counter") == 2
