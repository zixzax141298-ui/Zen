"""Grammar conformance tests for Zen v0.1 (ZSS-03 matrix coverage).

Covers positive and negative cases for official grammar productions.
"""

from __future__ import annotations

import pytest

from zen.ast.nodes import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    ExpressionStmt,
    FunctionDecl,
    GroupingExpr,
    IdentifierExpr,
    IfStmt,
    LiteralExpr,
    Program,
    ReturnStmt,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)
from zen.ast.validation import validate_ast
from zen.parser import ParseError, parse


def _ok(src: str) -> Program:
    prog = parse(src)
    assert isinstance(prog, Program)
    result = validate_ast(prog)
    assert result.is_valid, f"AST validation failed: {result.diagnostics}"
    return prog


def _fail(src: str) -> None:
    with pytest.raises(ParseError):
        parse(src)


def test_P_PROG_01_empty_program():
    prog = _ok("")
    assert prog.statements == ()


def test_P_PROG_01b_empty_with_separators():
    prog = _ok("\n\n;\n")
    assert prog.statements == ()


def test_P_BLOCK_01_empty_block():
    prog = _ok("fn f() { }")
    body = prog.statements[0].body
    assert isinstance(body, BlockStmt)
    assert body.statements == ()


def test_P_VAR_01_let_no_init():
    prog = _ok("let x")
    stmt = prog.statements[0]
    assert isinstance(stmt, VarDecl)
    assert stmt.is_const is False
    assert stmt.initializer is None


def test_P_VAR_02_let_with_init():
    prog = _ok("let x = 42")
    assert prog.statements[0].initializer is not None


def test_P_VAR_03_const_with_init():
    prog = _ok("const y = true")
    assert prog.statements[0].is_const is True


def test_N_VAR_01_const_without_init():
    _fail("const x")


def test_P_FN_01_zero_params():
    prog = _ok("fn f() {}")
    assert prog.statements[0].parameters == ()


def test_P_FN_03_multi_params():
    prog = _ok("fn f(a, b, c) {}")
    assert prog.statements[0].parameters == ("a", "b", "c")


def test_N_PARAMS_01_trailing_comma():
    _fail("fn f(a,) {}")


def test_P_IF_01_no_else():
    prog = _ok("if (true) {}")
    assert prog.statements[0].else_branch is None


def test_P_IF_02_with_else():
    prog = _ok("if (true) {} else {}")
    assert prog.statements[0].else_branch is not None


def test_P_IF_03_else_if():
    prog = _ok("if (a) {} else if (b) {}")
    assert isinstance(prog.statements[0].else_branch, IfStmt)


def test_P_WHILE_01():
    prog = _ok("while (false) {}")
    assert isinstance(prog.statements[0], WhileStmt)


def test_N_IF_01_missing_parens():
    _fail("if true {}")


def test_N_WHILE_01_missing_parens():
    _fail("while true {}")


def test_P_RET_01_bare_return():
    prog = _ok("fn f() { return }")
    ret = prog.statements[0].body.statements[0]
    assert isinstance(ret, ReturnStmt)
    assert ret.value is None


def test_P_ASSIGN_01_right_assoc():
    prog = _ok("a = b = 3")
    expr = prog.statements[0].expression
    assert isinstance(expr, AssignExpr)
    assert isinstance(expr.value, AssignExpr)


def test_P_TERM_01_left_assoc():
    prog = _ok("a + b - c")
    expr = prog.statements[0].expression
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "-"
    assert isinstance(expr.left, BinaryExpr)


def test_P_FACTOR_01_left_assoc():
    prog = _ok("a * b / c % d")
    expr = prog.statements[0].expression
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "%"


def test_P_CALL_01_chained():
    prog = _ok("f()()")
    expr = prog.statements[0].expression
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, CallExpr)


def test_N_ASSIGN_01_paren_target():
    _fail("(a) = 1")


def test_N_ARGS_01_trailing_comma():
    _fail("f(1,)")


def test_N_SEP_01_two_stmts_same_line():
    _fail("let a = 1 let b = 2")


def test_P_SEP_02_semicolon():
    prog = _ok("let a = 1; let b = 2")
    assert len(prog.statements) == 2


def test_P_MIX_01_precedence():
    prog = _ok("a + b * c")
    expr = prog.statements[0].expression
    assert isinstance(expr, BinaryExpr)
    assert expr.operator == "+"
    assert isinstance(expr.right, BinaryExpr)


def test_sequential_blocks_do_not_accumulate_depth():
    parts = [f"fn f{i}() {{}}" for i in range(40)]
    src = "\n".join(parts)
    prog = _ok(src)
    assert len(prog.statements) == 40
