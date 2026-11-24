"""Semantic analysis tests — OQ-01..OQ-09."""
from __future__ import annotations

from zen.parser import parse
from zen.semantic import analyze
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


def test_undefined_identifier():
    assert ZSS_S001_UNDEFINED in codes("x")


def test_duplicate_same_scope():
    assert ZSS_S002_DUPLICATE in codes("let a = 1\nlet a = 2")


def test_shadowing_allowed():
    src = "let x = 1\nfn f() { let x = 2\n return x }"
    assert ZSS_S002_DUPLICATE not in codes(src)


def test_uninitialized_read():
    assert ZSS_S003_UNINITIALIZED in codes("let x\nx")


def test_initialized_ok():
    assert codes("let x = 1\nx") == set()


def test_const_reassign():
    assert ZSS_S004_CONST_ASSIGN in codes("const x = 1\nx = 2")


def test_not_callable():
    assert ZSS_S005_NOT_CALLABLE in codes("let x = 1\nx()")


def test_arity_mismatch():
    assert ZSS_S006_ARITY in codes("fn f(a) { return a }\nf()")


def test_duplicate_param():
    assert ZSS_S007_DUP_PARAM in codes("fn f(a, a) { return a }")


def test_return_outside():
    assert ZSS_S008_RETURN_OUTSIDE in codes("return 1")


def test_if_both_branches_init():
    src = """
let x
if (true) { x = 1 } else { x = 2 }
x
"""
    assert ZSS_S003_UNINITIALIZED not in codes(src)


def test_if_one_branch_uninit():
    src = """
let x
if (true) { x = 1 }
x
"""
    assert ZSS_S003_UNINITIALIZED in codes(src)


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


def test_diagnostic_source_id_populated():
    from zen.ast.source_identity import SourceIdentifier

    sid = SourceIdentifier.new()
    prog = parse("x", source_id=sid)
    diags = analyze(prog)
    assert diags
    assert diags[0].source_id is not None
    assert diags[0].source_id.value == sid.value


def test_duplicate_related_span_populated():
    diags = analyze(parse("let a = 1\nlet a = 2"))
    dups = [d for d in diags if d.code == ZSS_S002_DUPLICATE]
    assert dups
    assert dups[0].related_span is not None
    assert dups[0].symbol == "a"
    assert dups[0].severity.value == "error" or dups[0].severity.name == "ERROR"
