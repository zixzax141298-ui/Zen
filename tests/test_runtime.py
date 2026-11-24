"""Runtime tests — OQ-07 evaluation contract."""

from __future__ import annotations

import pytest

from zen.parser import parse
from zen.runtime import RuntimeError, interpret
from zen.semantic import SemanticAnalyzer, SemanticError


def _run(src: str):
    """Fail-closed-ish helper: analyze strict then interpret."""
    prog = parse(src)
    SemanticAnalyzer().analyze_strict(prog)
    return interpret(prog)


def test_literal_and_arithmetic():
    assert _run("1 + 2 * 3") == 7
    assert _run("(1 + 2) * 3") == 9


def test_variables():
    assert _run("let x = 10\nx") == 10


def test_assignment():
    assert _run("let x = 1\nx = 5\nx") == 5


def test_function_call():
    src = "fn add(a, b) {\n  return a + b\n}\nadd(2, 3)"
    assert _run(src) == 5


def test_if_else():
    src = "let x = 0\nif (true) {\n  x = 1\n} else {\n  x = 2\n}\nx"
    assert _run(src) == 1


def test_while():
    src = (
        "let i = 0\nlet sum = 0\n"
        "while (i < 5) {\n  sum = sum + i\n  i = i + 1\n}\nsum"
    )
    assert _run(src) == 10


def test_div_by_zero():
    with pytest.raises(RuntimeError, match="Division by zero"):
        _run("1 / 0")


def test_short_circuit_and():
    src = (
        "let called = false\n"
        "fn f() { called = true\n return true }\n"
        "false && f()\n"
        "called"
    )
    assert _run(src) is False


def test_short_circuit_or():
    src = (
        "let called = false\n"
        "fn f() { called = true\n return false }\n"
        "true || f()\n"
        "called"
    )
    assert _run(src) is False


def test_non_boolean_if_condition():
    with pytest.raises(RuntimeError, match="Boolean"):
        _run("if (1) { 0 }")


def test_bool_not_numeric():
    with pytest.raises(RuntimeError, match="number"):
        _run("true + 1")


def test_cross_type_equality():
    assert _run("1 == true") is False
    assert _run("1 != true") is True
    assert _run("1 == 1") is True


def test_const_assign_caught_by_semantic():
    """Const reassignment is a semantic error on the fail-closed path."""
    with pytest.raises(SemanticError, match="constant"):
        _run("const x = 1\nx = 2")


def test_const_assign_runtime_defense():
    """If semantic is bypassed, runtime still rejects const assign."""
    with pytest.raises(RuntimeError, match="constant"):
        interpret(parse("const x = 1\nx = 2"))


def test_string_addition_rejected():
    with pytest.raises(RuntimeError, match="numbers"):
        _run('"a" + "b"')


def test_return_signal_not_leaked():
    with pytest.raises(RuntimeError, match="return"):
        interpret(parse("return 1"))


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


def test_runtime_step_limit_exact_boundary(monkeypatch):
    from zen.runtime import interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MAX_RUNTIME_STEPS", 2)
    assert interpret(parse("1")) == 1


def test_runtime_step_limit_exceeded(monkeypatch):
    from zen.runtime import interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MAX_RUNTIME_STEPS", 1)
    with pytest.raises(RuntimeError, match="Runtime step limit exceeded"):
        interpret(parse("1"))


def test_infinite_loop_stops_at_runtime_limit(monkeypatch):
    from zen.runtime import interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MAX_RUNTIME_STEPS", 40)
    source = "let i = 0\nwhile (true) { i = i + 1 }"
    with pytest.raises(RuntimeError, match="Runtime step limit exceeded"):
        interpret(parse(source))


def test_function_call_depth_limit(monkeypatch):
    from zen.runtime import interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MAX_CALL_DEPTH", 3)
    source = "fn recurse() { recurse() }\nrecurse()"
    with pytest.raises(RuntimeError, match="Maximum function call depth exceeded"):
        interpret(parse(source))
