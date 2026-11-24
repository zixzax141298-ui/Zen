from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from dataclasses import replace
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import sys
from typing import TextIO

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


def _version_string() -> str:
    try:
        return version("zen-language")
    except PackageNotFoundError:
        return "0.1.0"


def _write_error(message: str, output: TextIO) -> None:
    print(f"zen: {message}", file=output)


def _validate_program(source: str):
    program = parse(source)
    validation = validate_ast(program)

    if not validation.is_valid:
        messages = "; ".join(
            diagnostic.message
            for diagnostic in validation.diagnostics
        )
        raise ValueError(f"Invalid AST: {messages}")

    SemanticAnalyzer().analyze_strict(program)
    return program


def run_file(
    path: Path,
    *,
    output: TextIO | None = None,
) -> int:
    if output is None:
        output = sys.stdout

    if path.suffix.lower() != ".zen":
        _write_error(
            "source files must use the .zen extension",
            sys.stderr,
        )
        return 2

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _write_error(f"cannot read {path}: {exc}", sys.stderr)
        return 1

    try:
        program = _validate_program(source)
        result = Interpreter().interpret(program)
    except (
        LexerError,
        ParseError,
        SemanticError,
        ZenRuntimeError,
        ValueError,
    ) as exc:
        _write_error(str(exc), sys.stderr)
        return 1

    if result is not None:
        print(
            result if isinstance(result, str) else repr(result),
            file=output,
        )

    return 0


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
    closers = {
        closing: opening
        for opening, closing in pairs.items()
    }

    stack: list[TokenType] = []

    for token in tokens:
        if token.type in pairs:
            stack.append(token.type)
        elif token.type in closers:
            if not stack or stack[-1] is not closers[token.type]:
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
        candidate_source = (
            f"{self.source}\n{submission}"
            if self.source
            else submission
        )

        program = _validate_program(candidate_source)
        new_statements = program.statements[self.statement_count:]

        if not new_statements:
            self.source = candidate_source
            return None

        incremental_program = replace(
            program,
            statements=new_statements,
        )

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
        "Enter a ZSS statement or expression. "
        "Multi-line blocks are supported.",
        file=output,
    )
    print(":help   Show this help", file=output)
    print(":reset  Clear the current session", file=output)
    print(":quit   Exit the shell", file=output)


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
        f"Zen v{_version_string()} interactive shell. "
        "Type :help for help.",
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
            return 0
        except KeyboardInterrupt:
            pending = ""
            print("\nInput cancelled.", file=output)
            continue

        command = line.strip()

        if command in (":quit", ":exit"):
            if pending:
                print("Incomplete input discarded.", file=output)
            print("Goodbye.", file=output)
            return 0

        if command == ":help":
            _print_repl_help(output)
            continue

        if command in (":reset", ":clear"):
            repl.reset()
            pending = ""
            print("Session reset.", file=output)
            continue

        pending = f"{pending}\n{line}" if pending else line

        candidate_source = (
            f"{repl.source}\n{pending}"
            if repl.source
            else pending
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
            print(
                result if isinstance(result, str) else repr(result),
                file=output,
            )


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zen",
        description="Run ZSS source files or start the interactive shell.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_version_string()}",
    )

    commands = parser.add_subparsers(dest="command")
    run_parser = commands.add_parser(
        "run",
        help="execute a .zen source file",
    )
    run_parser.add_argument(
        "file",
        type=Path,
        help="path to a .zen source file",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)

    if args.command == "run":
        return run_file(args.file)

    return run_repl()
