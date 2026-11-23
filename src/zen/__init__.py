"""Public API for the Zen programming language."""

from __future__ import annotations

from typing import Any

from .lexer import Lexer, LexerError, Token, TokenType
from .parser import ParseError, parse
from .semantic import SemanticAnalyzer, SemanticError, analyze
from .semantic.diagnostics import SemanticDiagnostic
from .runtime import Interpreter, RuntimeError, ZenRuntimeError, interpret
from .ast.validation import validate_ast


def execute(source: str) -> Any:
    """Safe high-level pipeline: Parse → AST validate → Semantic → Runtime.

    Raises:
        TypeError: source is not a string
        LexerError / ParseError: lexical or syntax failure
        ValueError: AST structural validation failure
        SemanticError: semantic validation failure
        RuntimeError / ZenRuntimeError: runtime failure
    """
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    program = parse(source)
    result = validate_ast(program)
    if not result.is_valid:
        msgs = "; ".join(d.message for d in result.diagnostics)
        raise ValueError(f"Invalid AST: {msgs}")
    SemanticAnalyzer().analyze_strict(program)
    return interpret(program)


__all__ = [
    "Lexer",
    "LexerError",
    "Token",
    "TokenType",
    "parse",
    "ParseError",
    "analyze",
    "SemanticAnalyzer",
    "SemanticError",
    "SemanticDiagnostic",
    "interpret",
    "Interpreter",
    "RuntimeError",
    "ZenRuntimeError",
    "execute",
    "validate_ast",
]
