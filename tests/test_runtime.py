"""Tests for the minimal Zen tree-walk interpreter."""

from __future__ import annotations

import pytest

from zen.parser import parse
from zen.runtime import RuntimeError, interpret
from zen.semantic import SemanticAnalyzer


def _run(src: str):
    prog = parse(src)
    SemanticAnalyzer().analyze(prog)
    return interpret(prog)


def test_literal_and_arithmetic():
    assert _run("1 + 2 * 3") == 7
    assert _run("(1 + 2) * 3") == 9


def test_variables():
    assert _run("let x = 10\nx") == 10
    assert _run("let a = 1\nlet b = 2\na + b") == 3


def test_assignment():
    assert _run("let x = 1\nx = 5\nx") == 5


def test_function_call():
    src = """
fn add(a, b) {
  return a + b
}
add(2, 3)
"""
    assert _run(src) == 5


def test_if_else():
    src = """
let x = 0
if (true) {
  x = 1
} else {
  x = 2
}
x
"""
    assert _run(src) == 1


def test_while():
    src = """
let i = 0
let sum = 0
while (i < 5) {
  sum = sum + i
  i = i + 1
}
sum
"""
    assert _run(src) == 10


def test_const_assign_runtime():
    with pytest.raises(RuntimeError):
        _run("const x = 1\nx = 2")


def test_div_by_zero():
    with pytest.raises(RuntimeError, match="Division by zero"):
        _run("1 / 0")


def test_undefined_variable():
    with pytest.raises(RuntimeError, match="Undefined"):
        _run("x")
