from __future__ import annotations

import argparse
import json
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


# ---------------------------------------------------------------------------
# Exit codes — dipisah agar CI bisa membedakan jenis kegagalan.
# ---------------------------------------------------------------------------
class ExitCode(IntEnum):
    OK = 0
    SOURCE_ERROR = 1        # lexer / parse / semantic / runtime error
    IO_ERROR = 2            # file tidak bisa dibaca
    USAGE_ERROR = 64        # argumen / ekstensi salah (konvensi sysexits.h)
    TIMEOUT = 124           # eksekusi melebihi batas waktu
    INTERRUPTED = 130       # Ctrl+C (128 + SIGINT)


class _ExecutionTimeout(Exception):
    """Timeout eksekusi, dibedakan dari TimeoutError umum."""


class _CliError(Exception):
    """Error CLI yang membawa exit code spesifik."""

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
        # TODO: sinkronkan dengan pyproject.toml saat rilis.
        return "0.1.0"


def _write_error(message: str, output: TextIO) -> None:
    print(f"zen: {message}", file=output)


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
            f"{path}: source exceeds {MAX_SOURCE_CHARS} characters "
            f"(read at least {len(source)})",
            ExitCode.SOURCE_ERROR,
        )
    return source


def _validate_program(source: str):
    program = parse(source)
    validation = validate_ast(program)

    if not validation.is_valid:
        messages = "; ".join(
            diagnostic.message for diagnostic in validation.diagnostics
        )
        raise ValueError(f"Invalid AST: {messages}")

    SemanticAnalyzer().analyze_strict(program)
    return program


@contextmanager
def _timeout(seconds: float | None):
    """Batasi waktu eksekusi via SIGALRM. No-op di Windows / saat seconds=None."""
    if seconds is None or seconds <= 0 or sys.platform == "win32":
        yield
        return

    def _handler(signum, frame):
        raise _ExecutionTimeout(f"execution exceeded {seconds}s")

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _serialize_ast(node: Any) -> Any:
    """Serialisasi AST generik: dataclass, list, dict, scalar."""
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
# Perintah: run / check
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
    output = output or sys.stdout
    error = error or sys.stderr

    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    t0 = time.perf_counter()
    try:
        program = _validate_program(source)
    except (LexerError, ParseError, SemanticError, ValueError) as exc:
        if json_output:
            print(
                json.dumps(
                    {
                        "file": str(path),
                        "status": "error",
                        "phase": "validate",
                        "message": str(exc),
                    }
                ),
                file=output,
            )
        else:
            _write_error(str(exc), error)
        return int(ExitCode.SOURCE_ERROR)
    t1 = time.perf_counter()

    if check_only:
        if json_output:
            print(
                json.dumps({"file": str(path), "status": "ok", "phase": "validate"}),
                file=output,
            )
        else:
            print(f"{path}: valid", file=output)
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
            print(
                json.dumps(
                    {
                        "file": str(path),
                        "status": "error",
                        "phase": "runtime",
                        "message": str(exc),
                    }
                ),
                file=output,
            )
        else:
            _write_error(str(exc), error)
        return int(ExitCode.SOURCE_ERROR)
    t3 = time.perf_counter()

    if json_output:
        payload: dict[str, Any] = {
            "file": str(path),
            "status": "ok",
            "result": result
            if isinstance(result, (str, int, float, bool)) or result is None
            else repr(result),
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
            print(
                f"[stats] parse+analyze={1000 * (t1 - t0):.2f}ms "
                f"exec={1000 * (t3 - t2):.2f}ms "
                f"total={1000 * (t3 - t0):.2f}ms",
                file=error,
            )

    return int(ExitCode.OK)


# ---------------------------------------------------------------------------
# Perintah: ast
# ---------------------------------------------------------------------------
def dump_ast(
    path: Path,
    *,
    output: TextIO | None = None,
    error: TextIO | None = None,
) -> int:
    output = output or sys.stdout
    error = error or sys.stderr

    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    try:
        program = _validate_program(source)
    except (LexerError, ParseError, SemanticError, ValueError) as exc:
        _write_error(str(exc), error)
        return int(ExitCode.SOURCE_ERROR)

    print(json.dumps(_serialize_ast(program), indent=2), file=output)
    return int(ExitCode.OK)


# ---------------------------------------------------------------------------
# Perintah: tokens
# ---------------------------------------------------------------------------
def dump_tokens(
    path: Path,
    *,
    output: TextIO | None = None,
    error: TextIO | None = None,
) -> int:
    output = output or sys.stdout
    error = error or sys.stderr

    try:
        source = _read_source(path, error)
    except _CliError as exc:
        _write_error(str(exc), error)
        return int(exc.code)

    try:
        tokens = Lexer(source).tokenize()
    except LexerError as exc:
        _write_error(str(exc), error)
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
        print(f"[{index:04d}] {name:<20}{extra}", file=output)
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
        # TODO: parsing inkremental — saat ini O(n^2) terhadap panjang sesi.
        candidate_source = (
            f"{self.source}\n{submission}" if self.source else submission
        )
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
    print("Zen interactive shell", file=output)
    print(
        "Enter a ZSS statement or expression. Multi-line blocks are supported.",
        file=output,
    )
    print(":help          Show this help", file=output)
    print(":reset         Clear the current session", file=output)
    print(":ast           Summarize the current session AST", file=output)
    print(":load <file>   Load and execute a .zen file into the session", file=output)
    print(":save <file>   Save the current session source to a file", file=output)
    print(":quit          Exit the shell", file=output)


def run_repl(
    *,
    input_fn: Callable[[str], str] | None = None,
    output: TextIO | None = None,
) -> int:
    if input_fn is None:
        input_fn = input
    if output is None:
        output = sys.stdout

    repl = _ReplSession()
    pending = ""

    print(
        f"Zen v{_version_string()} interactive shell. Type :help for help.",
        file=output,
    )

    while True:
        prompt = "... " if pending else ">>> "

        try:
            line = input_fn(prompt)
        except EOFError:
            if pending:
                print("Incomplete input discarded.", file=output)
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

        if command == ":ast":
            if not repl.source:
                print("Session is empty.", file=output)
                continue
            try:
                program = _validate_program(repl.source)
            except (LexerError, ParseError, SemanticError, ValueError) as exc:
                print(f"zen: {exc}", file=output)
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
            except (
                LexerError,
                ParseError,
                SemanticError,
                ZenRuntimeError,
                ValueError,
            ) as exc:
                print(f"zen: {exc}", file=output)
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

        candidate_source = (
            f"{repl.source}\n{pending}" if repl.source else pending
        )

        if _needs_more_input(candidate_source):
            continue

        try:
            result = repl.execute_submission(pending)
        except (
            LexerError,
            ParseError,
            SemanticError,
            ZenRuntimeError,
            ValueError,
        ) as exc:
            _write_error(str(exc), output)
            pending = ""
            continue

        pending = ""

        if result is not None:
            print(_format_result(result), file=output)


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------
def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zen",
        description="Zen toolchain: run, check, inspect.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_version_string()}",
    )

    commands = parser.add_subparsers(dest="command", metavar="<command>")

    run_p = commands.add_parser("run", help="execute a .zen source file")
    run_p.add_argument("file", type=Path, help="path to a .zen source file")
    run_p.add_argument(
        "--check",
        action="store_true",
        help="validate without executing",
    )
    run_p.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON to stdout",
    )
    run_p.add_argument(
        "--stats",
        action="store_true",
        help="print timing statistics to stderr",
    )
    run_p.add_argument(
        "--timeout",
        type=float,
        default=None,
        metavar="SECONDS",
        help="abort execution after N seconds (POSIX only)",
    )

    check_p = commands.add_parser("check", help="validate a .zen source file")
    check_p.add_argument("file", type=Path, help="path to a .zen source file")
    check_p.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON to stdout",
    )

    ast_p = commands.add_parser("ast", help="dump the AST as JSON")
    ast_p.add_argument("file", type=Path, help="path to a .zen source file")

    tokens_p = commands.add_parser("tokens", help="dump the token stream")
    tokens_p.add_argument("file", type=Path, help="path to a .zen source file")

    commands.add_parser("version", help="print the Zen version")
    commands.add_parser("repl", help="start the interactive shell")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _argument_parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else int(ExitCode.OK)

    try:
        if args.command == "run":
            return run_file(
                args.file,
                check_only=args.check,
                json_output=args.json,
                show_stats=args.stats,
                timeout=args.timeout,
            )
        if args.command == "check":
            return run_file(
                args.file,
                check_only=True,
                json_output=args.json,
            )
        if args.command == "ast":
            return dump_ast(args.file)
        if args.command == "tokens":
            return dump_tokens(args.file)
        if args.command == "version":
            print(_version_string())
            return int(ExitCode.OK)
        # `repl` atau tanpa subcommand → REPL
        return run_repl()
    except KeyboardInterrupt:
        _write_error("interrupted", sys.stderr)
        return int(ExitCode.INTERRUPTED)


if __name__ == "__main__":
    sys.exit(main())
