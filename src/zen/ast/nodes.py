"""Immutable, typed abstract syntax tree nodes for Zen."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .source_span import SourceSpan


def _tuple_of(values: tuple, field_name: str) -> tuple:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{field_name} must be a collection, not text")
    try:
        return tuple(values)
    except TypeError as exc:
        raise TypeError(f"{field_name} must be iterable") from exc


@dataclass(frozen=True, slots=True)
class Node:
    span: SourceSpan

    def __post_init__(self) -> None:
        if not isinstance(self.span, SourceSpan):
            raise TypeError("AST node span must be a SourceSpan")


class Statement(Node):
    """Base class for statement nodes."""


class Expression(Node):
    """Base class for expression nodes."""


@dataclass(frozen=True, slots=True)
class Program(Node):
    statements: tuple[Statement, ...]

    def __post_init__(self) -> None:
        super(Program, self).__post_init__()
        object.__setattr__(
            self, "statements", _tuple_of(self.statements, "statements")
        )
        if any(not isinstance(item, Statement) for item in self.statements):
            raise TypeError("Program statements must contain Statement nodes")


@dataclass(frozen=True, slots=True)
class VarDecl(Statement):
    name: str
    initializer: Expression | None
    is_const: bool

    def __post_init__(self) -> None:
        super(VarDecl, self).__post_init__()
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Variable name must be a non-empty string")
        if self.initializer is not None and not isinstance(
            self.initializer, Expression
        ):
            raise TypeError("Variable initializer must be an Expression")
        if type(self.is_const) is not bool:
            raise TypeError("is_const must be a boolean")


@dataclass(frozen=True, slots=True)
class FunctionDecl(Statement):
    name: str
    parameters: tuple[str, ...]
    body: BlockStmt

    def __post_init__(self) -> None:
        super(FunctionDecl, self).__post_init__()
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Function name must be a non-empty string")
        object.__setattr__(
            self, "parameters", _tuple_of(self.parameters, "parameters")
        )
        if any(not isinstance(item, str) or not item for item in self.parameters):
            raise ValueError("Function parameters must be non-empty strings")
        if not isinstance(self.body, BlockStmt):
            raise TypeError("Function body must be a BlockStmt")


@dataclass(frozen=True, slots=True)
class BlockStmt(Statement):
    statements: tuple[Statement, ...]

    def __post_init__(self) -> None:
        super(BlockStmt, self).__post_init__()
        object.__setattr__(
            self, "statements", _tuple_of(self.statements, "statements")
        )
        if any(not isinstance(item, Statement) for item in self.statements):
            raise TypeError("Block statements must contain Statement nodes")


@dataclass(frozen=True, slots=True)
class IfStmt(Statement):
    condition: Expression
    then_branch: BlockStmt
    else_branch: BlockStmt | IfStmt | None

    def __post_init__(self) -> None:
        super(IfStmt, self).__post_init__()
        if not isinstance(self.condition, Expression):
            raise TypeError("If condition must be an Expression")
        if not isinstance(self.then_branch, BlockStmt):
            raise TypeError("If then_branch must be a BlockStmt")
        if self.else_branch is not None and not isinstance(
            self.else_branch, (BlockStmt, IfStmt)
        ):
            raise TypeError("If else_branch must be a BlockStmt, IfStmt, or None")


@dataclass(frozen=True, slots=True)
class WhileStmt(Statement):
    condition: Expression
    body: BlockStmt

    def __post_init__(self) -> None:
        super(WhileStmt, self).__post_init__()
        if not isinstance(self.condition, Expression):
            raise TypeError("While condition must be an Expression")
        if not isinstance(self.body, BlockStmt):
            raise TypeError("While body must be a BlockStmt")


@dataclass(frozen=True, slots=True)
class ReturnStmt(Statement):
    value: Expression | None

    def __post_init__(self) -> None:
        super(ReturnStmt, self).__post_init__()
        if self.value is not None and not isinstance(self.value, Expression):
            raise TypeError("Return value must be an Expression or None")


@dataclass(frozen=True, slots=True)
class ExpressionStmt(Statement):
    expression: Expression

    def __post_init__(self) -> None:
        super(ExpressionStmt, self).__post_init__()
        if not isinstance(self.expression, Expression):
            raise TypeError("ExpressionStmt requires an Expression")


@dataclass(frozen=True, slots=True)
class LiteralExpr(Expression):
    value: object

    def __post_init__(self) -> None:
        super(LiteralExpr, self).__post_init__()

        allowed_types = (type(None), bool, int, float, str)
        if type(self.value) not in allowed_types:
            raise TypeError(
                "Literal value must be an immutable Zen primitive"
            )

        if type(self.value) is float and not math.isfinite(self.value):
            raise ValueError("Literal float must be finite")


@dataclass(frozen=True, slots=True)
class IdentifierExpr(Expression):
    name: str

    def __post_init__(self) -> None:
        super(IdentifierExpr, self).__post_init__()
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Identifier name must be a non-empty string")


@dataclass(frozen=True, slots=True)
class UnaryExpr(Expression):
    operator: str
    operand: Expression

    def __post_init__(self) -> None:
        super(UnaryExpr, self).__post_init__()
        if not isinstance(self.operator, str) or not self.operator:
            raise ValueError("Unary operator must be a non-empty string")
        if not isinstance(self.operand, Expression):
            raise TypeError("Unary operand must be an Expression")


@dataclass(frozen=True, slots=True)
class BinaryExpr(Expression):
    left: Expression
    operator: str
    right: Expression

    def __post_init__(self) -> None:
        super(BinaryExpr, self).__post_init__()
        if not isinstance(self.left, Expression):
            raise TypeError("Binary left operand must be an Expression")
        if not isinstance(self.operator, str) or not self.operator:
            raise ValueError("Binary operator must be a non-empty string")
        if not isinstance(self.right, Expression):
            raise TypeError("Binary right operand must be an Expression")


@dataclass(frozen=True, slots=True)
class GroupingExpr(Expression):
    expression: Expression

    def __post_init__(self) -> None:
        super(GroupingExpr, self).__post_init__()
        if not isinstance(self.expression, Expression):
            raise TypeError("Grouping expression must be an Expression")


@dataclass(frozen=True, slots=True)
class AssignExpr(Expression):
    target: IdentifierExpr
    value: Expression

    def __post_init__(self) -> None:
        super(AssignExpr, self).__post_init__()
        if not isinstance(self.target, IdentifierExpr):
            raise TypeError("Assignment target must be an IdentifierExpr")
        if not isinstance(self.value, Expression):
            raise TypeError("Assignment value must be an Expression")


@dataclass(frozen=True, slots=True)
class CallExpr(Expression):
    callee: Expression
    arguments: tuple[Expression, ...]

    def __post_init__(self) -> None:
        super(CallExpr, self).__post_init__()
        if not isinstance(self.callee, Expression):
            raise TypeError("Call callee must be an Expression")
        object.__setattr__(
            self, "arguments", _tuple_of(self.arguments, "arguments")
        )
        if any(not isinstance(item, Expression) for item in self.arguments):
            raise TypeError("Call arguments must contain Expression nodes")
