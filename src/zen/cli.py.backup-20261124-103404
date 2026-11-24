from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import sys
from typing import TextIO

from zen import (
    Lexer,
    LexerError,
    ParseError,
    RuntimeError as ZenRuntimeError,
    SemanticError,
    execute,
)
from zen.lexer import TokenType


def _version_string() -> str:
    try:
        return version("zen-language")
    except PackageNotFoundError:
        return "0.1.0"


def _write_error(message: str, output: TextIO) -> None:
    print(f"zen: {message}", file=output)


def run_file(path: Path, *, output: TextIO | None = None) -> int:
    """Execute one UTF-8 encoded .zen source file."""
    if output is None:
        output = sys.stdout

    if path.suffix.lower() != ".zen":
        _write_error("source files must use the .zen extension", sys.stderr)
        return 2

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _write_error(f"cannot read {path}: {exc}", sys.stderr)
        return 1

    try:
        result = execute(source)
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
        print(result if isinstance(result, str) else repr(result), file=output)
    return 0


def _needs_more_input(source: str) -> bool:
    """Return whether an opening delimiter still needs a matching closer."""
    try:
        tokens = Lexer(source).tokenize()
    except LexerError as exc:
        return "Unterminated block comment" in exc.message

    pairs = {
        TokenType.LEFT_PAREN: TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE: TokenType.RIGHT_BRACE,
        TokenType.LEFT_BRACKET: TokenType.RIGHT_BRACKET,
    }
    closers = {value: key for key, value in pairs.items()}
    stack: list[TokenType] = []

    for token in tokens:
        if token.type in pairs:
            stack.append(token.type)
        elif token.type in closers:
            if not stack or stack[-1] is not closers[token.type]:
                return False
            stack.pop()

    return bool(stack)


def _print_repl_help(output: TextIO) -> None:
    print("Zen interactive shell", file=output)
    print("Enter a ZSS statement or expression. Multi-line blocks are supported.", file=output)
    print(":help   Show this help", file=output)
    print(":reset  Clear the current session", file=output)
    print(":quit   Exit the shell", file=output)


def run_repl(
    *,
    input_fn: Callable[[str], str] | None = None,
    output: TextIO | None = None,
) -> int:
    """Start a persistent REPL through the public fail-closed pipeline.

    Session source is replayed on each submission. This retains language
    state while ensuring every submission uses the same public pipeline
    as execute(), without introducing a second semantic-analysis path.
    """
    if input_fn is None:
        input_fn = input
    if output is None:
        output = sys.stdout

    session = ""
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
            session = ""
            pending = ""
            print("Session reset.", file=output)
            continue

        pending = f"{pending}\n{line}" if pending else line
        candidate = f"{session}\n{pending}" if session else pending

        if _needs_more_input(candidate):
            continue

        try:
            result = execute(candidate)
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

        session = candidate
        pending = ""
        if result is not None:
            print(result if isinstance(result, str) else repr(result), file=output)


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
    run_parser = commands.add_parser("run", help="execute a .zen source file")
    run_parser.add_argument("file", type=Path, help="path to a .zen source file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. No subcommand starts the interactive shell."""
    args = _argument_parser().parse_args(argv)
    if args.command == "run":
        return run_file(args.file)
    return run_repl()
