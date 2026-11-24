"""Tree-walk interpreter for Zen v0.1 — OQ-07 evaluation contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zen.ast.nodes import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    Expression,
    ExpressionStmt,
    FunctionDecl,
    GroupingExpr,
    IdentifierExpr,
    IfStmt,
    LiteralExpr,
    Program,
    ReturnStmt,
    Statement,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)


class ZenRuntimeError(Exception):
    """Language-level runtime error (not a raw Python exception leak)."""

    def __init__(self, message: str, line: int | None = None) -> None:
        self.line = line
        super().__init__(
            message if line is None else f"{message} (line {line})"
        )


RuntimeError = ZenRuntimeError


class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


@dataclass
class Environment:
    parent: Environment | None = None
    values: dict[str, Any] = field(default_factory=dict)
    constants: set[str] = field(default_factory=set)

    def define(self, name: str, value: Any, *, is_const: bool = False) -> None:
        self.values[name] = value
        if is_const:
            self.constants.add(name)

    def assign(self, name: str, value: Any) -> None:
        env: Environment | None = self
        while env is not None:
            if name in env.values:
                if name in env.constants:
                    raise ZenRuntimeError(f"Cannot assign to constant '{name}'")
                env.values[name] = value
                return
            env = env.parent
        raise ZenRuntimeError(f"Undefined variable '{name}'")

    def get(self, name: str) -> Any:
        env: Environment | None = self
        while env is not None:
            if name in env.values:
                return env.values[name]
            env = env.parent
        raise ZenRuntimeError(f"Undefined variable '{name}'")


@dataclass
class ZenFunction:
    declaration: FunctionDecl
    closure: Environment

    def arity(self) -> int:
        return len(self.declaration.parameters)


def _is_number(value: Any) -> bool:
    return type(value) in (int, float)


def _is_bool(value: Any) -> bool:
    return type(value) is bool


def _is_primitive(value: Any) -> bool:
    return type(value) in (int, float, bool, str) or value is None


def _primitive_equal(left: Any, right: Any) -> bool:
    """OQ-07: same-type primitive equality only; no function/object equality."""
    if not _is_primitive(left) or not _is_primitive(right):
        raise ZenRuntimeError(
            "Equality is only defined for primitive values"
        )
    if type(left) is not type(right):
        return False
    return left == right


class Interpreter:
    def __init__(self) -> None:
        self.globals = Environment()
        self.env = self.globals

    def interpret(self, program: Program) -> Any:
        result: Any = None
        for stmt in program.statements:
            result = self._execute(stmt)
        return result

    def _execute(self, stmt: Statement) -> Any:
        if isinstance(stmt, VarDecl):
            value = None
            if stmt.initializer is not None:
                value = self._evaluate(stmt.initializer)
            self.env.define(stmt.name, value, is_const=stmt.is_const)
            return None
        if isinstance(stmt, FunctionDecl):
            fn = ZenFunction(stmt, self.env)
            self.env.define(stmt.name, fn)
            return None
        if isinstance(stmt, ExpressionStmt):
            return self._evaluate(stmt.expression)
        if isinstance(stmt, BlockStmt):
            return self._execute_block(stmt, Environment(parent=self.env))
        if isinstance(stmt, IfStmt):
            cond = self._evaluate(stmt.condition)
            if not _is_bool(cond):
                line = stmt.condition.span.start_line if stmt.condition.span else None
                raise ZenRuntimeError("if condition must be a Boolean", line)
            if cond is True:
                return self._execute(stmt.then_branch)
            if stmt.else_branch is not None:
                return self._execute(stmt.else_branch)
            return None
        if isinstance(stmt, WhileStmt):
            result = None
            while True:
                cond = self._evaluate(stmt.condition)
                if not _is_bool(cond):
                    line = (
                        stmt.condition.span.start_line
                        if stmt.condition.span
                        else None
                    )
                    raise ZenRuntimeError(
                        "while condition must be a Boolean", line
                    )
                if cond is not True:
                    break
                result = self._execute(stmt.body)
            return result
        if isinstance(stmt, ReturnStmt):
            value = None
            if stmt.value is not None:
                value = self._evaluate(stmt.value)
            raise ReturnSignal(value)
        return None

    def _execute_block(self, block: BlockStmt, env: Environment) -> Any:
        previous = self.env
        self.env = env
        result: Any = None
        try:
            for s in block.statements:
                result = self._execute(s)
        finally:
            self.env = previous
        return result

    def _evaluate(self, expr: Expression) -> Any:
        if isinstance(expr, LiteralExpr):
            return expr.value
        if isinstance(expr, IdentifierExpr):
            return self.env.get(expr.name)
        if isinstance(expr, AssignExpr):
            value = self._evaluate(expr.value)
            if isinstance(expr.target, IdentifierExpr):
                self.env.assign(expr.target.name, value)
            return value
        if isinstance(expr, GroupingExpr):
            return self._evaluate(expr.expression)
        if isinstance(expr, UnaryExpr):
            operand = self._evaluate(expr.operand)
            if expr.operator == "!":
                if not _is_bool(operand):
                    raise ZenRuntimeError(
                        "Operand of '!' must be a Boolean",
                        expr.span.start_line if expr.span else None,
                    )
                return not operand
            if expr.operator == "-":
                if not _is_number(operand):
                    raise ZenRuntimeError(
                        "Operand of unary '-' must be a number",
                        expr.span.start_line if expr.span else None,
                    )
                return -operand
            raise ZenRuntimeError(f"Unknown unary operator '{expr.operator}'")
        if isinstance(expr, BinaryExpr):
            op = expr.operator
            if op == "&&":
                left = self._evaluate(expr.left)
                if not _is_bool(left):
                    raise ZenRuntimeError(
                        "Operands of '&&' must be Boolean",
                        expr.span.start_line if expr.span else None,
                    )
                if left is False:
                    return False
                right = self._evaluate(expr.right)
                if not _is_bool(right):
                    raise ZenRuntimeError(
                        "Operands of '&&' must be Boolean",
                        expr.span.start_line if expr.span else None,
                    )
                return right
            if op == "||":
                left = self._evaluate(expr.left)
                if not _is_bool(left):
                    raise ZenRuntimeError(
                        "Operands of '||' must be Boolean",
                        expr.span.start_line if expr.span else None,
                    )
                if left is True:
                    return True
                right = self._evaluate(expr.right)
                if not _is_bool(right):
                    raise ZenRuntimeError(
                        "Operands of '||' must be Boolean",
                        expr.span.start_line if expr.span else None,
                    )
                return right
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            if op == "+":
                if _is_number(left) and _is_number(right):
                    return left + right
                raise ZenRuntimeError(
                    "Operands of '+' must be numbers"
                )
            if op in ("-", "*", "/", "%"):
                if not _is_number(left) or not _is_number(right):
                    raise ZenRuntimeError(
                        f"Operands of '{op}' must be numbers"
                    )
                if op == "-":
                    return left - right
                if op == "*":
                    return left * right
                if op == "/":
                    if right == 0:
                        raise ZenRuntimeError("Division by zero")
                    return left / right
                if right == 0:
                    raise ZenRuntimeError("Modulo by zero")
                return left % right
            if op in ("<", "<=", ">", ">="):
                if not _is_number(left) or not _is_number(right):
                    raise ZenRuntimeError(
                        f"Operands of '{op}' must be numbers"
                    )
                if op == "<":
                    return left < right
                if op == "<=":
                    return left <= right
                if op == ">":
                    return left > right
                return left >= right
            if op == "==":
                return _primitive_equal(left, right)
            if op == "!=":
                return not _primitive_equal(left, right)
            raise ZenRuntimeError(f"Unknown binary operator '{op}'")
        if isinstance(expr, CallExpr):
            callee = self._evaluate(expr.callee)
            args = [self._evaluate(a) for a in expr.arguments]
            if not isinstance(callee, ZenFunction):
                raise ZenRuntimeError("Can only call functions")
            if len(args) != callee.arity():
                raise ZenRuntimeError(
                    f"Expected {callee.arity()} arguments but got {len(args)}"
                )
            return self._call(callee, args)
        raise ZenRuntimeError(
            f"Unsupported expression type: {type(expr).__name__}"
        )

    def _call(self, fn: ZenFunction, args: list[Any]) -> Any:
        env = Environment(parent=fn.closure)
        for name, value in zip(fn.declaration.parameters, args):
            env.define(name, value)
        try:
            self._execute_block(fn.declaration.body, env)
        except ReturnSignal as ret:
            return ret.value
        return None


def interpret(program: Program) -> Any:
    try:
        return Interpreter().interpret(program)
    except ReturnSignal:
        raise ZenRuntimeError("'return' used outside of a function") from None
