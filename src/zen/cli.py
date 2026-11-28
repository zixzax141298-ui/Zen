from __future__ import annotations

import argparse
import json
import platform
import signal
import sys
import time
from collections.abc import Callable, Sequence
from contextlib import contextmanager
from dataclasses import is_dataclass, replace
from enum import IntEnum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, TextIO

from zen.cli_core import CLIContext, Command, CommandRegistry, ExitCode, dispatch
from zen.cli_core.completion import render_completion
from zen.cli_core.completion_install import (
    CompletionInstallError,
    install_completion as install_shell_completion,
    uninstall_completion as uninstall_shell_completion,
)
from zen.cli_core.diagnostics import (
    diagnostic_from_exception,
    diagnostics_payload,
    format_diagnostic,
)

from zen import (
    Interpreter,
    Lexer,
    LexerError,
    ParseError,
    RuntimeError as ZenRuntimeError,
    SemanticAnalyzer,
    SemanticError,
    TokenType,
    parse,
    validate_ast,
)
from zen.lexer import MAX_SOURCE_CHARS
from zen.ziif import generate_fingerprint  # <-- TAMBAHAN BARU

# ---------------------------------------------------------------------------
# Terminal Colors (ANSI)
# ---------------------------------------------------------------------------
class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    @classmethod
    def disable(cls):
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.CYAN = cls.RESET = cls.BOLD = ""

# ---------------------------------------------------------------------------
# Exit Codes
# ---------------------------------------------------------------------------
class _ExecutionTimeout(Exception):
    pass

class _CliError(Exception):
    def __init__(self, message: str, code: ExitCode) -> None:
        super().__init__(message)
        self.code = code

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _version_string() -> str:
    try:
        return version("zen-language")
    except PackageNotFoundError:
        return "0.1.0"

def _write_error(message: str, output: TextIO) -> None:
    print(f"{Color.RED}zen: {message}{Color.RESET}", file=output)

def _read_source(path: Path, error: TextIO) -> str:
    if path.suffix.lower() != ".zen":
        raise _CliError(
            "source files must use the .zen extension",
            ExitCode.USAGE_ERROR,
        )
    try:
        with path.open(encoding="utf-8") as source_file:
            source = source_file.read(MAX_SOURCE_CHARS + 1)
    except (OSError, UnicodeError) as exc:
        raise _CliError(f"cannot read {path}: {exc}", ExitCode.IO_ERROR) from exc
        
    if len(source) > MAX_SOURCE_CHARS:
        raise _CliError(
            f"Source exceeds {MAX_SOURCE_CHARS} characters",
            ExitCode.SOURCE_ERROR,
        )
    return source

class _CLIDiagnosticError(Exception):
    """Internal CLI-only container for normalized frontend diagnostics."""

    def __init__(self, diagnostics, message=None):
        self.diagnostics = tuple(diagnostics)
        if message is None:
            message = (
                self.diagnostics[0].message
                if self.diagnostics
                else "validation failed"
            )
        super().__init__(message)


def _write_cli_diagnostics(
    path: str,
    exc: BaseException,
    error: TextIO,
) -> None:
    """Write normalized frontend diagnostics to the CLI error stream."""
    if isinstance(exc, _CLIDiagnosticError):
        diagnostics = exc.diagnostics
    else:
        diagnostics = (diagnostic_from_exception(exc),)

    if not diagnostics:
        _write_error(str(exc), error)
        return

    for diagnostic in diagnostics:
        print(format_diagnostic(path, diagnostic), file=error)


def _write_repl_exception(exc: BaseException, output: TextIO) -> None:
    if isinstance(exc, _CLIDiagnosticError):
        for diagnostic in exc.diagnostics:
            print(format_diagnostic("<repl>", diagnostic), file=output)
        if not exc.diagnostics:
            _write_error(str(exc), output)
        return

    if isinstance(exc, (LexerError, ParseError, SemanticError, ValueError)):
        _write_cli_diagnostics("<repl>", exc, output)
        return

    _write_error(str(exc), output)


def _validate_program(source: str):
    try:
        program = parse(source)
    except (LexerError, ParseError) as exc:
        raise _CLIDiagnosticError(
            (diagnostic_from_exception(exc),),
            message=str(exc),
        ) from exc

    validation = validate_ast(program)
    if not validation.is_valid:
        messages = "; ".join(
            diagnostic.message for diagnostic in validation.diagnostics
        )
        raise _CLIDiagnosticError(
            validation.diagnostics,
            message=f"Invalid AST: {messages}",
        )

    try:
        SemanticAnalyzer().analyze_strict(program)
    except SemanticError as exc:
        raise _CLIDiagnosticError(
            (diagnostic_from_exception(exc),),
            message=str(exc),
        ) from exc

    return program

@contextmanager
def _timeout(seconds: float | None):
    if seconds is None or seconds <= 0 or sys.platform == "win32":
        yield
        return

    def _handler(signum, frame):
        raise _ExecutionTimeout(f"Execution exceeded {seconds}s")

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)

def _serialize_ast(node: Any) -> Any:
    if node is None or isinstance(node, (str, int, float, bool)):
        return node
    if isinstance(node, (list, tuple)):
        return [_serialize_ast(item) for item in node]
    if isinstance(node, dict):
        return {str(k): _serialize_ast(v) for k, v in node.items()}
    if is_dataclass(node) and not isinstance(node, type):
        out: dict[str, Any] = {"__type__": type(node).__name__}
        for field_name in node.__dataclass_fields__:
            out[field_name] = _serialize_ast(getattr(node, field_name))
        return out
    if hasattr(node, "__dict__"):
        out = {"__type__": type(node).__name__}
        for k, v in vars(node).items():
            if not k.startswith("_"):
                out[k] = _serialize_ast(v)
        return out
    return repr(node)

def _format_result(result: Any) -> str:
    return result if isinstance(result, str) else repr(result)

# ---------------------------------------------------------------------------
# Core Commands
# ---------------------------------------------------------------------------
def run_file(
    path: Path,
    *,
    output: TextIO | None = None,
    error: TextIO | None = None,
    check_only: bool = False,
    json_output: bool = False,
    show_stats: bool = False,
    timeout: float | None = None,
) -> int:
    if output is None:
        output = sys.stdout
    if error is None:
        error = sys.stderr

    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    t0 = time.perf_counter()
    try:
        program = _validate_program(source)
    except _CLIDiagnosticError as exc:
        if json_output:
            payload = {
                "schema_version": 1,
                "file": str(path),
                "status": "error",
                "phase": "validate",
                "message": str(exc),
                "diagnostics": diagnostics_payload(exc.diagnostics),
            }
            print(json.dumps(payload), file=output)
        else:
            for diagnostic in exc.diagnostics:
                print(format_diagnostic(str(path), diagnostic), file=error)
            if not exc.diagnostics:
                _write_error(str(exc), error)
        return int(ExitCode.SOURCE_ERROR)
    except (LexerError, ParseError, SemanticError, ValueError) as exc:
        diagnostic = diagnostic_from_exception(exc)
        if json_output:
            payload = {
                "schema_version": 1,
                "file": str(path),
                "status": "error",
                "phase": "validate",
                "message": str(exc),
                "diagnostics": diagnostics_payload((diagnostic,)),
            }
            print(json.dumps(payload), file=output)
        else:
            print(format_diagnostic(str(path), diagnostic), file=error)
        return int(ExitCode.SOURCE_ERROR)
    t1 = time.perf_counter()

    if check_only:
        if json_output:
            print(json.dumps({"schema_version": 1, "file": str(path), "status": "ok", "phase": "validate", "diagnostics": []}), file=output)
        else:
            print(f"{Color.GREEN}✓ {path}: valid{Color.RESET}", file=output)
        if show_stats and not json_output:
            print(f"[stats] parse+analyze={1000 * (t1 - t0):.2f}ms", file=error)
        return int(ExitCode.OK)

    t2 = time.perf_counter()
    try:
        with _timeout(timeout):
            result = Interpreter().interpret(program)
    except _ExecutionTimeout as exc:
        _write_error(str(exc), error)
        return int(ExitCode.TIMEOUT)
    except ZenRuntimeError as exc:
        if json_output:
            diagnostic = diagnostic_from_exception(exc)
            payload = {
                "schema_version": 1,
                "file": str(path),
                "status": "error",
                "phase": "runtime",
                "message": str(exc),
                "diagnostics": diagnostics_payload((diagnostic,)),
            }
            print(json.dumps(payload), file=output)
        else:
            _write_error(str(exc), error)
        return int(ExitCode.SOURCE_ERROR)
    t3 = time.perf_counter()

    if json_output:
        payload: dict[str, Any] = {
            "schema_version": 1,
            "file": str(path),
            "status": "ok",
            "result": result if isinstance(result, (str, int, float, bool)) or result is None else repr(result),
            "diagnostics": [],
        }
        if show_stats:
            payload["stats"] = {
                "parse_analyze_ms": round((t1 - t0) * 1000, 3),
                "execute_ms": round((t3 - t2) * 1000, 3),
                "total_ms": round((t3 - t0) * 1000, 3),
            }
        print(json.dumps(payload), file=output)
    else:
        if result is not None:
            print(_format_result(result), file=output)
        if show_stats:
            print(f"[stats] parse+analyze={1000 * (t1 - t0):.2f}ms exec={1000 * (t3 - t2):.2f}ms total={1000 * (t3 - t0):.2f}ms", file=error)

    return int(ExitCode.OK)

def dump_ast(path: Path, *, output: TextIO | None = None, error: TextIO | None = None) -> int:
    if output is None:
        output = sys.stdout
    if error is None:
        error = sys.stderr
    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    try:
        program = _validate_program(source)
    except (_CLIDiagnosticError, LexerError, ParseError, SemanticError, ValueError) as exc:
        _write_cli_diagnostics(str(path), exc, error)
        return int(ExitCode.SOURCE_ERROR)

    print(json.dumps(_serialize_ast(program), indent=2), file=output)
    return int(ExitCode.OK)

def dump_tokens(path: Path, *, output: TextIO | None = None, error: TextIO | None = None) -> int:
    if output is None:
        output = sys.stdout
    if error is None:
        error = sys.stderr
    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    try:
        tokens = Lexer(source).tokenize()
    except LexerError as exc:
        _write_cli_diagnostics(str(path), exc, error)
        return int(ExitCode.SOURCE_ERROR)

    for index, token in enumerate(tokens):
        name = token.type.name if hasattr(token.type, "name") else str(token.type)
        extra = ""
        for attr in ("lexeme", "value", "literal"):
            if hasattr(token, attr):
                val = getattr(token, attr)
                if val is not None:
                    extra = f"  {val!r}"
                    break
        print(f"[{index:04d}] {Color.CYAN}{name:<20}{Color.RESET}{extra}", file=output)
    return int(ExitCode.OK)

def fingerprint_file(path: Path, *, output: TextIO | None = None, error: TextIO | None = None) -> int:
    if output is None:
        output = sys.stdout
    if error is None:
        error = sys.stderr
    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    try:
        program = _validate_program(source)
    except (_CLIDiagnosticError, LexerError, ParseError, SemanticError, ValueError) as exc:
        _write_cli_diagnostics(str(path), exc, error)
        return int(ExitCode.SOURCE_ERROR)

    fp = generate_fingerprint(program)
    print(f"{Color.CYAN}{fp}{Color.RESET}", file=output)
    return int(ExitCode.OK)

def format_source(path: Path, *, output: TextIO | None = None, error: TextIO | None = None) -> int:
    if output is None:
        output = sys.stdout
    if error is None:
        error = sys.stderr
    try:
        source = _read_source(path, error)
        _validate_program(source)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)
    except (_CLIDiagnosticError, LexerError, ParseError, SemanticError, ValueError) as exc:
        _write_cli_diagnostics(str(path), exc, error)
        return int(ExitCode.SOURCE_ERROR)

    print(source.strip(), file=output)
    return int(ExitCode.OK)

def print_docs(output: TextIO | None = None) -> int:
    if output is None:
        output = sys.stdout
    print(f"{Color.BOLD}Zen Language Quick Reference{Color.RESET}", file=output)
    print("============================\n", file=output)
    print("Variables:", file=output)
    print("  let x = 10", file=output)
    print("  let y = 20\n", file=output)
    print("Functions:", file=output)
    print("  fn add(a, b) {", file=output)
    print("    return a + b", file=output)
    print("  }\n", file=output)
    print("Control Flow:", file=output)
    print("  if (condition) { ... } else { ... }", file=output)
    print("  while (condition) { ... }\n", file=output)
    print("Run 'zen repl' to start exploring interactively.", file=output)
    return int(ExitCode.OK)

# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------
def _needs_more_input(source: str) -> bool:
    try:
        tokens = Lexer(source).tokenize()
    except LexerError as exc:
        return exc.message == "Unterminated block comment"

    pairs = {
        TokenType.LEFT_PAREN: TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE: TokenType.RIGHT_BRACE,
        TokenType.LEFT_BRACKET: TokenType.RIGHT_BRACKET,
    }
    closers = {closing: opening for opening, closing in pairs.items()}

    stack: list[TokenType] = []
    for token in tokens:
        if token.type in pairs:
            stack.append(token.type)
        elif token.type in closers:
            if not stack or stack[-1] != closers[token.type]:
                return False
            stack.pop()

    return bool(stack)

class _ReplSession:
    def __init__(self) -> None:
        self.interpreter = Interpreter()
        self.source = ""
        self.statement_count = 0

    def reset(self) -> None:
        self.interpreter = Interpreter()
        self.source = ""
        self.statement_count = 0

    def execute_submission(self, submission: str):
        candidate_source = f"{self.source}\n{submission}" if self.source else submission
        program = _validate_program(candidate_source)
        new_statements = program.statements[self.statement_count:]

        if not new_statements:
            self.source = candidate_source
            return None

        incremental_program = replace(program, statements=new_statements)

        global_values = self.interpreter.globals.values.copy()
        global_constants = self.interpreter.globals.constants.copy()

        try:
            result = self.interpreter.interpret(incremental_program)
        except Exception:
            self.interpreter.globals.values.clear()
            self.interpreter.globals.values.update(global_values)
            self.interpreter.globals.constants.clear()
            self.interpreter.globals.constants.update(global_constants)
            raise

        self.source = candidate_source
        self.statement_count = len(program.statements)
        return result

def _print_repl_help(output: TextIO) -> None:
    print(f"{Color.BOLD}Zen Interactive Shell{Color.RESET}", file=output)
    print("Enter a ZSS statement or expression. Multi-line blocks are supported.\n", file=output)
    print(f"{Color.CYAN}:help{Color.RESET}          Show this help", file=output)
    print(f"{Color.CYAN}:reset{Color.RESET}         Clear the current session", file=output)
    print(f"{Color.CYAN}:vars{Color.RESET}          List all defined global variables", file=output)
    print(f"{Color.CYAN}:ast{Color.RESET}           Summarize the current session AST", file=output)
    print(f"{Color.CYAN}:load <file>{Color.RESET}   Load and execute a .zen file into the session", file=output)
    print(f"{Color.CYAN}:save <file>{Color.RESET}   Save the current session source to a file", file=output)
    print(f"{Color.CYAN}:quit{Color.RESET}          Exit the shell", file=output)

def run_repl(*, input_fn: Callable[[str], str] | None = None, output: TextIO | None = None) -> int:
    if input_fn is None:
        input_fn = input
    if output is None:
        output = sys.stdout

    repl = _ReplSession()
    pending = ""

    print(f"{Color.GREEN}Zen v{_version_string()} interactive shell.{Color.RESET} Type :help for help.", file=output)

    while True:
        prompt = f"{Color.YELLOW}... {Color.RESET}" if pending else f"{Color.BLUE}>>> {Color.RESET}"

        try:
            line = input_fn(prompt)
        except EOFError:
            if pending:
                print("\nIncomplete input discarded.", file=output)
            print("Goodbye.", file=output)
            return int(ExitCode.OK)
        except KeyboardInterrupt:
            pending = ""
            print("\nInput cancelled.", file=output)
            continue

        command = line.strip()

        if command in (":quit", ":exit"):
            if pending:
                print("Incomplete input discarded.", file=output)
            print("Goodbye.", file=output)
            return int(ExitCode.OK)

        if command == ":help":
            _print_repl_help(output)
            continue

        if command in (":reset", ":clear"):
            repl.reset()
            pending = ""
            print("Session reset.", file=output)
            continue
            
        if command == ":vars":
            vals = repl.interpreter.globals.values
            if not vals:
                print("No global variables defined.", file=output)
            else:
                for k, v in vals.items():
                    is_const = k in repl.interpreter.globals.constants
                    prefix = "const" if is_const else "let"
                    print(f"  {prefix} {Color.CYAN}{k}{Color.RESET} = {_format_result(v)}", file=output)
            continue

        if command == ":ast":
            if not repl.source:
                print("Session is empty.", file=output)
                continue
            try:
                program = _validate_program(repl.source)
            except (_CLIDiagnosticError, LexerError, ParseError, SemanticError, ValueError) as exc:
                _write_repl_exception(exc, output)
                continue
            print(f"AST: {len(program.statements)} statement(s)", file=output)
            continue

        if command.startswith(":load "):
            path_str = command[len(":load "):].strip()
            try:
                file_source = _read_source(Path(path_str), output)
            except _CliError as exc:
                print(f"zen: {exc}", file=output)
                continue
            try:
                result = repl.execute_submission(file_source)
            except (_CLIDiagnosticError, LexerError, ParseError, SemanticError, ZenRuntimeError, ValueError) as exc:
                _write_repl_exception(exc, output)
                continue
            if result is not None:
                print(_format_result(result), file=output)
            else:
                print(f"Loaded {path_str}.", file=output)
            continue

        if command.startswith(":save "):
            path_str = command[len(":save "):].strip()
            try:
                Path(path_str).write_text(repl.source, encoding="utf-8")
            except OSError as exc:
                print(f"zen: cannot save {path_str}: {exc}", file=output)
                continue
            print(f"Saved {len(repl.source)} chars to {path_str}.", file=output)
            continue

        pending = f"{pending}\n{line}" if pending else line

        candidate_source = f"{repl.source}\n{pending}" if repl.source else pending

        if _needs_more_input(candidate_source):
            continue

        try:
            result = repl.execute_submission(pending)
        except (_CLIDiagnosticError, LexerError, ParseError, SemanticError, ZenRuntimeError, ValueError) as exc:
            _write_repl_exception(exc, output)
            pending = ""
            continue

        pending = ""

        if result is not None:
            print(_format_result(result), file=output)

# ---------------------------------------------------------------------------
# Argparse Setup
# ---------------------------------------------------------------------------
def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zen",
        description=f"{Color.BOLD}Zen Language Toolchain{Color.RESET} — run, check, and inspect ZSS code.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_version_string()}",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in output",
    )

    commands = parser.add_subparsers(dest="command", metavar="<command>")

    run_p = commands.add_parser("run", help="execute a .zen source file")
    run_p.add_argument("file", type=Path, help="path to a .zen source file")
    run_p.add_argument("--check", action="store_true", help="validate without executing")
    run_p.add_argument("--json", action="store_true", help="emit machine-readable JSON to stdout")
    run_p.add_argument("--stats", action="store_true", help="print timing statistics to stderr")
    run_p.add_argument("--timeout", type=float, default=None, metavar="SECONDS", help="abort execution after N seconds")

    check_p = commands.add_parser("check", help="validate a .zen source file")
    check_p.add_argument("file", type=Path, help="path to a .zen source file")
    check_p.add_argument("--json", action="store_true", help="emit machine-readable JSON to stdout")

    ast_p = commands.add_parser("ast", help="dump the AST as JSON")
    ast_p.add_argument("file", type=Path, help="path to a .zen source file")

    fp_p = commands.add_parser("fp", help="print the ZIIF fingerprint of a .zen file")
    fp_p.add_argument("file", type=Path, help="path to a .zen source file")

    tokens_p = commands.add_parser("tokens", help="dump the token stream")
    tokens_p.add_argument("file", type=Path, help="path to a .zen source file")

    fmt_p = commands.add_parser("format", aliases=["fmt"], help="format a .zen source file")
    fmt_p.add_argument("file", type=Path, help="path to a .zen source file")

    commands.add_parser("docs", help="print a quick reference guide for ZSS")
    commands.add_parser("env", help="print environment and system information")
    commands.add_parser("version", help="print the Zen version")
    commands.add_parser("repl", help="start the interactive shell")
    commands.add_parser("doctor", help="inspect basic ZEN CLI and Python environment details")
    commands.add_parser("info", help="print ZEN and host environment information")
    completion_p = commands.add_parser("completion", help="generate or manage shell completion")
    completion_p.add_argument("shell", choices=("bash", "zsh"), help="target shell")
    completion_action = completion_p.add_mutually_exclusive_group()
    completion_action.add_argument(
        "--install",
        action="store_true",
        help="install shell completion for the current user",
    )
    completion_action.add_argument(
        "--uninstall",
        action="store_true",
        help="remove ZEN-managed shell completion",
    )

    return parser

def _build_command_registry() -> CommandRegistry:
    """Build the command table using explicitly injected CLI operations."""
    from zen.cli_commands import CLIOperations, register_commands

    operations = CLIOperations(
        run_file=run_file,
        dump_ast=dump_ast,
        dump_tokens=dump_tokens,
        fingerprint_file=fingerprint_file,
        format_source=format_source,
        print_docs=print_docs,
        run_repl=run_repl,
        print_environment=_print_environment,
        print_version=_print_version,
        print_doctor=_print_doctor,
        generate_completion=_generate_completion,
        install_completion=_install_completion,
        uninstall_completion=_uninstall_completion,
    )
    return register_commands(CommandRegistry(), operations)

def _generate_completion(shell: str, *, output: TextIO, error: TextIO) -> int:
    # Generate from the same argparse parser used by the CLI.
    try:
        script = render_completion(shell, _argument_parser())
        output.write(script)
        output.flush()
    except OSError as exc:
        _write_error(f"cannot write completion output: {exc}", error)
        return int(ExitCode.IO_ERROR)
    return int(ExitCode.OK)


def _install_completion(shell: str, *, output: TextIO, error: TextIO) -> int:
    try:
        script = render_completion(shell, _argument_parser())
        install_shell_completion(shell, script)
        print(f"ZEN {shell} completion installed.", file=output)
        output.flush()
    except (CompletionInstallError, OSError) as exc:
        _write_error(f"cannot install {shell} completion: {exc}", error)
        return int(ExitCode.IO_ERROR)
    return int(ExitCode.OK)


def _uninstall_completion(shell: str, *, output: TextIO, error: TextIO) -> int:
    try:
        uninstall_shell_completion(shell)
        print(f"ZEN {shell} completion uninstalled.", file=output)
        output.flush()
    except (CompletionInstallError, OSError) as exc:
        _write_error(f"cannot uninstall {shell} completion: {exc}", error)
        return int(ExitCode.IO_ERROR)
    return int(ExitCode.OK)


def _print_environment(output: TextIO) -> int:
    print(f"Zen Version: {_version_string()}", file=output)
    print(f"Python:      {platform.python_version()} ({platform.python_implementation()})", file=output)
    print(f"OS:          {platform.system()} {platform.release()}", file=output)
    return int(ExitCode.OK)


def _print_version(output: TextIO) -> int:
    print(_version_string(), file=output)
    return int(ExitCode.OK)


def _print_doctor(output: TextIO) -> int:
    """Report basic host/package facts; this is not a sandbox security audit."""
    print("ZEN CLI diagnostics", file=output)
    print(f"Version:      {_version_string()}", file=output)
    print(f"Python:       {platform.python_version()} ({platform.python_implementation()})", file=output)
    print(f"Platform:     {platform.system()} {platform.release()}", file=output)
    print(f"Source limit: {MAX_SOURCE_CHARS} characters", file=output)
    print("Status:       basic environment inspection completed", file=output)
    return int(ExitCode.OK)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main(argv: Sequence[str] | None = None) -> int:
    parser = _argument_parser()
    
    # Biarkan SystemExit dari argparse berjalan natural
    args = parser.parse_args(argv)

    color_names = ("RED", "GREEN", "YELLOW", "BLUE", "CYAN", "RESET", "BOLD")
    previous_colors = {name: getattr(Color, name) for name in color_names}

    try:
        if getattr(args, "no_color", False):
            Color.disable()

        context = CLIContext(stdout=sys.stdout, stderr=sys.stderr)
        return dispatch(
            _build_command_registry(),
            context,
            args.command,
            args,
            default=lambda ctx, _args: run_repl(output=ctx.stdout),
            unknown_exit_code=int(ExitCode.USAGE_ERROR),
        )

    except KeyboardInterrupt:
        _write_error("interrupted", sys.stderr)
        return int(ExitCode.INTERRUPTED)

    finally:
        for name, value in previous_colors.items():
            setattr(Color, name, value)

if __name__ == "__main__":
    sys.exit(main())
