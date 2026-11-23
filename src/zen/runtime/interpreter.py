"""Tree-walk interpreter for Zen v0.1 (minimal defined subset).

Only evaluation behavior that is sufficiently constrained is implemented.
Open questions (especially OQ-07) are not silently resolved.
"""

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


class RuntimeError(Exception):
    def __init__(self, message: str, line: int | None = None) -> None:
        self.line = line
        super().__init__(message if line is None else f"{message} (line {line})")


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
                    raise RuntimeError(f"Cannot assign to constant '{name}'")
                env.values[name] = value
                return
            env = env.parent
        raise RuntimeError(f"Undefined variable '{name}'")

    def get(self, name: str) -> Any:
        env: Environment | None = self
        while env is not None:
            if name in env.values:
                return env.values[name]
            env = env.parent
        raise RuntimeError(f"Undefined variable '{name}'")


@dataclass
class ZenFunction:
    declaration: FunctionDecl
    closure: Environment

    def arity(self) -> int:
        return len(self.declaration.parameters)


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
            if self._is_truthy(cond):
                return self._execute(stmt.then_branch)
            if stmt.else_branch is not None:
                return self._execute(stmt.else_branch)
            return None
        if isinstance(stmt, WhileStmt):
            result = None
            while self._is_truthy(self._evaluate(stmt.condition)):
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
                return not self._is_truthy(operand)
            if expr.operator == "-":
                self._check_number(operand, expr)
                return -operand
            raise RuntimeError(f"Unknown unary operator '{expr.operator}'")
        if isinstance(expr, BinaryExpr):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            op = expr.operator
            if op == "+":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise RuntimeError("Operands of '+' must be two numbers or two strings")
            if op in ("-", "*", "/", "%"):
                self._check_number(left, expr)
                self._check_number(right, expr)
                if op == "-":
                    return left - right
                if op == "*":
                    return left * right
                if op == "/":
                    if right == 0:
                        raise RuntimeError("Division by zero")
                    return left / right
                if op == "%":
                    if right == 0:
                        raise RuntimeError("Modulo by zero")
                    return left % right
            if op in ("<", "<=", ">", ">="):
                self._check_number(left, expr)
                self._check_number(right, expr)
                if op == "<":
                    return left < right
                if op == "<=":
                    return left <= right
                if op == ">":
                    return left > right
                return left >= right
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == "&&":
                return self._is_truthy(left) and self._is_truthy(right)
            if op == "||":
                return self._is_truthy(left) or self._is_truthy(right)
            raise RuntimeError(f"Unknown binary operator '{op}'")
        if isinstance(expr, CallExpr):
            callee = self._evaluate(expr.callee)
            args = [self._evaluate(a) for a in expr.arguments]
            if not isinstance(callee, ZenFunction):
                raise RuntimeError("Can only call functions")
            if len(args) != callee.arity():
                raise RuntimeError(
                    f"Expected {callee.arity()} arguments but got {len(args)}"
                )
            return self._call(callee, args)
        raise RuntimeError(f"Unsupported expression type: {type(expr).__name__}")

    def _call(self, fn: ZenFunction, args: list[Any]) -> Any:
        env = Environment(parent=fn.closure)
        for name, value in zip(fn.declaration.parameters, args):
            env.define(name, value)
        try:
            self._execute_block(fn.declaration.body, env)
        except ReturnSignal as ret:
            return ret.value
        return None

    def _is_truthy(self, value: Any) -> bool:
        if value is None or value is False:
            return False
        return True

    def _check_number(self, value: Any, expr: Expression) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            line = expr.span.start_line if expr.span else None
            raise RuntimeError("Operand must be a number", line)


def interpret(program: Program) -> Any:
    return Interpreter().interpret(program)
