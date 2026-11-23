"""Tests for Zen semantic analysis (implemented subset)."""

from __future__ import annotations

import pytest

from zen.parser import parse
from zen.semantic import SemanticAnalyzer, SemanticError, analyze


def test_return_outside_function_rejected():
    prog = parse("return 1")
    diags = analyze(prog)
    assert any(d.code == "SEM_RETURN_OUTSIDE" for d in diags)


def test_return_inside_function_ok():
    prog = parse("fn f() { return 1 }")
    diags = analyze(prog)
    assert not any(d.code == "SEM_RETURN_OUTSIDE" for d in diags)


def test_nested_return_inside_function_ok():
    src = """
fn f() {
  if (true) {
    return 1
  }
}
"""
    prog = parse(src)
    diags = analyze(prog)
    assert not any(d.code == "SEM_RETURN_OUTSIDE" for d in diags)


def test_analyze_strict_raises():
    prog = parse("return")
    with pytest.raises(SemanticError) as exc_info:
        SemanticAnalyzer().analyze_strict(prog)
    assert "return" in str(exc_info.value).lower()


def test_const_reassignment_reported():
    prog = parse("const x = 1\nx = 2")
    diags = analyze(prog)
    assert any(d.code == "SEM_CONST_ASSIGN" for d in diags)


def test_same_scope_redecl_reported():
    prog = parse("let a = 1\nlet a = 2")
    diags = analyze(prog)
    assert any(d.code == "SEM_REDECL" for d in diags)


def test_function_params_and_body():
    src = """
fn add(a, b) {
  return a + b
}
"""
    prog = parse(src)
    diags = analyze(prog)
    assert not any(d.code == "SEM_RETURN_OUTSIDE" for d in diags)


def test_duplicate_param_reported():
    prog = parse("fn f(a, a) {}")
    diags = analyze(prog)
    assert any(d.code == "SEM_PARAM_DUP" for d in diags)


def test_empty_program():
    prog = parse("")
    diags = analyze(prog)
    assert diags == []
