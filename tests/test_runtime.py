"""Runtime / OQ-07 evaluation tests."""
from __future__ import annotations

import pytest

from zen.parser import parse
from zen.runtime import RuntimeError, interpret
from zen.semantic import SemanticAnalyzer


def _run(src: str):
    program = parse(src)
    SemanticAnalyzer().analyze_strict(program)
    return interpret(program)


def test_arithmetic():
    assert _run("1 + 2 * 3") == 7


def test_short_circuit_and():
    src = """
fn boom() { return 1 / 0 }
false && boom()
"""
    assert _run(src) is False


def test_short_circuit_or():
    src = """
fn boom() { return 1 / 0 }
true || boom()
"""
    assert _run(src) is True


def test_if_requires_bool():
    with pytest.raises(RuntimeError, match="Boolean"):
        _run("if (1) { 2 }")


def test_string_addition_rejected():
    with pytest.raises(RuntimeError, match="numbers"):
        _run('"a" + "b"')


def test_return_signal_not_leaked():
    with pytest.raises(RuntimeError, match="return"):
        interpret(parse("return 1"))


def test_cross_type_equality():
    assert _run("1 == true") is False
    assert _run("1 != true") is True
    assert _run("1 == 1") is True


def test_const_assign_runtime():
    with pytest.raises(RuntimeError):
        _run("const x = 1\nx = 2")


def test_function_equality_rejected():
    src = "fn f() { return 1 }\nfn g() { return 2 }\nf == g"
    with pytest.raises(RuntimeError, match="primitive"):
        _run(src)


def test_primitive_equality_matrix():
    assert _run("1 == 1") is True
    assert _run("1 == 2") is False
    assert _run("true == false") is False
    assert _run('"a" == "a"') is True
    assert _run("1 != 2") is True
