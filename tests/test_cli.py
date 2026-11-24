from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from zen.runtime import RuntimeError
from zen.cli import main, run_file, run_repl, Color

# MATIKAN WARNA ANSI SAAT TESTING AGAR TIDAK MERUSAK PENTCOCOKAN STRING
Color.disable()

# ===========================================================================
# BAGIAN 1: TEST LAMA (REGRESI)
# ===========================================================================

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

def test_run_file_accepts_source_at_character_limit(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr("zen.cli.MAX_SOURCE_CHARS", 8)
    monkeypatch.setattr("zen.lexer.MAX_SOURCE_CHARS", 8)
    source = tmp_path / "boundary.zen"
    source.write_text("42      ", encoding="utf-8")
    assert run_file(source) == 0
    captured = capsys.readouterr()
    assert captured.out == "42\n"
    assert captured.err == ""

def test_run_file_counts_unicode_source_by_characters(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr("zen.cli.MAX_SOURCE_CHARS", 8)
    monkeypatch.setattr("zen.lexer.MAX_SOURCE_CHARS", 8)
    source = tmp_path / "unicode.zen"
    source.write_text("//ééé\n42", encoding="utf-8")
    assert len(source.read_text(encoding="utf-8")) == 8
    assert run_file(source) == 0
    assert capsys.readouterr().out == "42\n"

def test_run_file_reads_at_most_limit_plus_one_characters(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr("zen.cli.MAX_SOURCE_CHARS", 8)
    monkeypatch.setattr("zen.lexer.MAX_SOURCE_CHARS", 8)
    source = tmp_path / "oversized.zen"
    source.write_text("42" + (" " * 100), encoding="utf-8")

    real_open = Path.open
    requested_sizes = []

    class ReadTracker:
        def __init__(self, stream): self.stream = stream
        def __enter__(self):
            self.stream.__enter__()
            return self
        def __exit__(self, exc_type, exc_value, traceback):
            return self.stream.__exit__(exc_type, exc_value, traceback)
        def read(self, size=-1):
            requested_sizes.append(size)
            return self.stream.read(size)

    def tracked_open(path, *args, **kwargs):
        stream = real_open(path, *args, **kwargs)
        if path == source: return ReadTracker(stream)
        return stream

    monkeypatch.setattr(Path, "open", tracked_open)
    assert run_file(source) == 1
    assert requested_sizes == [9]
    assert "Source exceeds 8 characters" in capsys.readouterr().err

def test_run_file_reports_invalid_utf8(tmp_path: Path, capsys):
    source = tmp_path / "invalid-utf8.zen"
    source.write_bytes(b"\xff")
    assert run_file(source) == 1
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
    commands = iter(["fn add(a, b) {", "  return a + b", "}", "add(20, 22)", ":quit"])
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
    commands = iter(["let counter = 0", "counter = counter + 1", "counter = counter + 1", "counter", ":quit"])
    output = StringIO()
    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0
    assert len(instances) == 1
    assert interpreted_statement_counts == [1, 1, 1, 1]
    assert output.getvalue().splitlines().count("2") == 2

def test_repl_rolls_back_global_state_after_runtime_error():
    commands = iter(["let counter = 1", "counter = 2", "1 / 0", "counter", ":quit"])
    output = StringIO()
    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0
    rendered = output.getvalue()
    assert "Division by zero" in rendered
    assert rendered.splitlines().count("2") == 2

def test_repl_reset_clears_previous_variables():
    commands = iter(["let counter = 10", ":reset", "counter", ":quit"])
    output = StringIO()
    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0
    rendered = output.getvalue()
    assert "Session reset." in rendered
    assert "Undefined identifier 'counter'" in rendered


# ===========================================================================
# BAGIAN 2: TEST FITUR BARU CLI
# ===========================================================================

def test_cli_check_command(tmp_path: Path, capsys):
    source = tmp_path / "valid.zen"
    source.write_text("40 + 2\n", encoding="utf-8")
    assert main(["check", str(source)]) == 0
    captured = capsys.readouterr()
    assert "valid" in captured.out
    assert captured.err == ""

def test_cli_check_command_json(tmp_path: Path, capsys):
    source = tmp_path / "valid.zen"
    source.write_text("40 + 2\n", encoding="utf-8")
    assert main(["check", str(source), "--json"]) == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "ok"
    assert data["file"] == str(source)

def test_cli_run_command_json_and_stats(tmp_path: Path, capsys):
    source = tmp_path / "hello.zen"
    source.write_text("40 + 2\n", encoding="utf-8")
    assert main(["run", str(source), "--json", "--stats"]) == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "ok"
    assert data["result"] == 42
    assert "stats" in data

def test_cli_ast_command(tmp_path: Path, capsys):
    source = tmp_path / "hello.zen"
    source.write_text("40 + 2\n", encoding="utf-8")
    assert main(["ast", str(source)]) == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, dict)
    assert "__type__" in data

def test_cli_tokens_command(tmp_path: Path, capsys):
    source = tmp_path / "hello.zen"
    source.write_text("40 + 2\n", encoding="utf-8")
    assert main(["tokens", str(source)]) == 0
    captured = capsys.readouterr()
    # SUDAH DIPERBAIKI MENJADI INTEGER
    assert "INTEGER" in captured.out
    assert "PLUS" in captured.out

def test_cli_format_command(tmp_path: Path, capsys):
    source = tmp_path / "unformatted.zen"
    source.write_text("  40 + 2  \n\n", encoding="utf-8")
    assert main(["fmt", str(source)]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "40 + 2"

def test_cli_docs_command(capsys):
    assert main(["docs"]) == 0
    captured = capsys.readouterr()
    assert "Variables:" in captured.out
    assert "Control Flow:" in captured.out

def test_cli_env_command(capsys):
    assert main(["env"]) == 0
    captured = capsys.readouterr()
    assert "Zen Version:" in captured.out
    assert "Python:" in captured.out
    assert "OS:" in captured.out

def test_cli_version_explicit_command(capsys):
    assert main(["version"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() != ""

@pytest.mark.skipif(sys.platform == "win32", reason="SIGALRM tidak didukung di Windows")
def test_cli_run_timeout(tmp_path: Path, capsys):
    source = tmp_path / "infinite.zen"
    source.write_text("while (true) { }\n", encoding="utf-8")
    assert main(["run", str(source), "--timeout", "0.1"]) == 124
    captured = capsys.readouterr()
    assert "Execution exceeded" in captured.err


# ===========================================================================
# BAGIAN 3: TEST FITUR REPL BARU
# ===========================================================================

def test_repl_vars_command():
    # Karena ANSI Color sudah dimatikan di atas, test ini pasti lolos 100%
    commands = iter(["let x = 10", "let y = 20", ":vars", ":quit"])
    output = StringIO()
    assert run_repl(input_fn=lambda _prompt: next(commands), output=output) == 0
    rendered = output.getvalue()
    assert "let x = 10" in rendered
    assert "let y = 20" in rendered

def test_repl_save_and_load(tmp_path: Path):
    file_path = tmp_path / "session.zen"
    commands_save = iter(["let x = 99", f":save {file_path}", ":quit"])
    output_save = StringIO()
    run_repl(input_fn=lambda _prompt: next(commands_save), output=output_save)
    assert "Saved" in output_save.getvalue()
    assert file_path.exists()
    assert "let x = 99" in file_path.read_text()

    commands_load = iter([f":load {file_path}", "x", ":quit"])
    output_load = StringIO()
    run_repl(input_fn=lambda _prompt: next(commands_load), output=output_load)
    rendered = output_load.getvalue()
    assert "Loaded" in rendered
    assert "99" in rendered
