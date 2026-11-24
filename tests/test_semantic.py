"""Semantic analysis tests — OQ-01 through OQ-09."""

from __future__ import annotations

import pytest

from zen.parser import parse
from zen.semantic import SemanticAnalyzer, SemanticError, analyze
from zen.semantic.diagnostics import (
    ZSS_S001_UNDEFINED,
    ZSS_S002_DUPLICATE,
    ZSS_S003_UNINITIALIZED,
    ZSS_S004_CONST_ASSIGN,
    ZSS_S005_NOT_CALLABLE,
    ZSS_S006_ARITY,
    ZSS_S007_DUP_PARAM,
    ZSS_S008_RETURN_OUTSIDE,
)


def codes(src: str) -> set[str]:
    return {d.code for d in analyze(parse(src))}


def test_return_outside_function():
    assert ZSS_S008_RETURN_OUTSIDE in codes("return 1")


def test_return_inside_function_ok():
    assert ZSS_S008_RETURN_OUTSIDE not in codes("fn f() { return 1 }")


def test_undefined_identifier():
    assert ZSS_S001_UNDEFINED in codes("x")


def test_duplicate_declaration():
    assert ZSS_S002_DUPLICATE in codes("let a = 1\nlet a = 2")


def test_shadowing_allowed():
    src = "let a = 1\nfn f() { let a = 2\n return a }"
    assert ZSS_S002_DUPLICATE not in codes(src)


def test_uninitialized_read():
    assert ZSS_S003_UNINITIALIZED in codes("let x\nx")


def test_initialized_read_ok():
    assert ZSS_S003_UNINITIALIZED not in codes("let x = 1\nx")


def test_const_reassignment():
    assert ZSS_S004_CONST_ASSIGN in codes("const x = 1\nx = 2")


def test_duplicate_param():
    assert ZSS_S007_DUP_PARAM in codes("fn f(a, a) {}")


def test_arity_mismatch():
    src = "fn f(a) { return a }\nf(1, 2)"
    assert ZSS_S006_ARITY in codes(src)


def test_non_callable():
    src = "let x = 1\nx()"
    assert ZSS_S005_NOT_CALLABLE in codes(src)


def test_direct_recursion_ok():
    src = "fn fact(n) {\n  if (false) {\n    return fact(n)\n  }\n  return n\n}"
    diags = analyze(parse(src))
    assert not any(d.code == ZSS_S001_UNDEFINED for d in diags)


def test_if_without_else_uninitialized():
    src = "let x\nif (true) { x = 1 }\nx"
    assert ZSS_S003_UNINITIALIZED in codes(src)


def test_if_else_both_init():
    src = "let x\nif (true) { x = 1 } else { x = 2 }\nx"
    assert ZSS_S003_UNINITIALIZED not in codes(src)


def test_analyze_strict_raises():
    with pytest.raises(SemanticError):
        SemanticAnalyzer().analyze_strict(parse("return"))


def test_empty_program():
    assert analyze(parse("")) == []


def test_shadow_inner_uninit_not_confused_with_outer():
    src = """
let x = 1
fn f() {
  let x
  return x
}
"""
    assert ZSS_S003_UNINITIALIZED in codes(src)


def test_shadow_if_block_inner_uninit():
    src = """
let x = 1
if (true) {
  let x
  x
}
"""
    assert ZSS_S003_UNINITIALIZED in codes(src)


def test_duplicate_related_span():
    diags = analyze(parse("let a = 1\nlet a = 2"))
    dups = [d for d in diags if d.code == ZSS_S002_DUPLICATE]
    assert dups
    assert dups[0].symbol == "a"
