"""Basic positive and negative tests for the Zen v0.1 parser."""

from __future__ import annotations

import pytest

from zen.ast.nodes import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    FunctionDecl,
    IfStmt,
    Program,
    VarDecl,
)
from zen.ast.validation import validate_ast
from zen.parser import ParseError, parse


def test_empty_program():
    prog = parse("")
    assert isinstance(prog, Program)
    assert prog.statements == ()
    assert validate_ast(prog).is_valid


def test_let_and_const():
    prog = parse("let x = 1\nconst y = 2")
    assert len(prog.statements) == 2
    assert isinstance(prog.statements[0], VarDecl)
    assert prog.statements[0].is_const is False
    assert isinstance(prog.statements[1], VarDecl)
    assert prog.statements[1].is_const is True
    assert validate_ast(prog).is_valid


def test_const_requires_initializer():
    with pytest.raises(ParseError):
        parse("const x")


def test_assignment_right_assoc():
    prog = parse("a = b = 3")
    stmt = prog.statements[0]
    expr = stmt.expression
    assert isinstance(expr, AssignExpr)
    assert isinstance(expr.value, AssignExpr)
    assert validate_ast(prog).is_valid


def test_precedence():
    prog = parse("1 + 2 * 3")
    expr = prog.statements[0].expression
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "+"
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator == "*"


def test_if_else_and_function():
    src = """
fn add(a, b) {
  return a + b
}
if (true) {
  let x = add(1, 2)
} else {
  let y = 0
}
"""
    prog = parse(src)
    assert isinstance(prog.statements[0], FunctionDecl)
    assert isinstance(prog.statements[1], IfStmt)
    assert validate_ast(prog).is_valid


def test_trailing_comma_args_rejected():
    with pytest.raises(ParseError):
        parse("f(1,)")


def test_assignment_non_identifier_rejected():
    with pytest.raises(ParseError):
        parse("(a) = 1")


def test_two_statements_need_semicolon():
    with pytest.raises(ParseError):
        parse("let a = 1 let b = 2")


def test_call_chain():
    prog = parse("f()()")
    expr = prog.statements[0].expression
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, CallExpr)
