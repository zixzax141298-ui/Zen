"""Immutable, typed abstract syntax tree nodes for Zen."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from zen.limits import MAX_DIRECT_CHILDREN
from .source_identity import SourceIdentifier
from .source_location import SourceLocation
from .source_span import SourceSpan


def _tuple_of(values, field_name: str, *, child_collection: bool = True) -> tuple:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{field_name} must be a collection, not text")
    try:
        result = tuple(values)
    except TypeError as exc:
        raise TypeError(f"{field_name} must be iterable") from exc
    if child_collection and len(result) > MAX_DIRECT_CHILDREN:
        raise ValueError(f"{field_name} exceeds MAX_DIRECT_CHILDREN")
    return result


def _validate_children(parent: "Node", children: tuple, field_name: str) -> None:
    # Local import avoids a module cycle: validation and traversal depend on Node.
    from .validation import require_ordered_children

    require_ordered_children(parent, children, field_name)


@dataclass(frozen=True, slots=True)
class Node:
    span: SourceSpan
    # Optional only during staged legacy migration.
    # validate_ast rejects nodes without a SourceIdentifier.
    source_id: SourceIdentifier | None = field(
        default=None,
        kw_only=True,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.span, SourceSpan):
            raise TypeError("AST node span must be a SourceSpan")

        if (
            self.source_id is not None
            and not isinstance(self.source_id, SourceIdentifier)
        ):
            raise TypeError(
                "AST node source_id must be a SourceIdentifier or None"
            )

    @property
    def location(self) -> SourceLocation | None:
        if self.source_id is None:
            return None
        return SourceLocation(self.source_id, self.span)


class Statement(Node):
    """Base class for statement nodes."""


class Expression(Node):
    """Base class for expression nodes."""


@dataclass(frozen=True, slots=True)
class Program(Node):
    statements: tuple[Statement, ...]

    def __post_init__(self) -> None:
        super(Program, self).__post_init__()
        statements = _tuple_of(self.statements, "statements")
        object.__setattr__(self, "statements", statements)
        if any(not isinstance(item, Statement) for item in statements):
            raise TypeError("Program statements must contain Statement nodes")
        _validate_children(self, statements, "statements")


@dataclass(frozen=True, slots=True)
class VarDecl(Statement):
    name: str
    initializer: Expression | None
    is_const: bool

    def __post_init__(self) -> None:
        super(VarDecl, self).__post_init__()
        if not isinstance(self.name, str):
            raise TypeError("Variable name must be a string")
        if self.initializer is not None and not isinstance(self.initializer, Expression):
            raise TypeError("Variable initializer must be an Expression")
        if type(self.is_const) is not bool:
            raise TypeError("is_const must be a boolean")
        _validate_children(self, tuple(x for x in (self.initializer,) if x is not None), "initializer")


@dataclass(frozen=True, slots=True)
class FunctionDecl(Statement):
    name: str
    parameters: tuple[str, ...]
    body: "BlockStmt"

    def __post_init__(self) -> None:
        super(FunctionDecl, self).__post_init__()
        if not isinstance(self.name, str):
            raise TypeError("Function name must be a string")
        parameters = _tuple_of(self.parameters, "parameters", child_collection=False)
        object.__setattr__(self, "parameters", parameters)
        if any(not isinstance(item, str) for item in parameters):
            raise TypeError("Function parameters must be strings")
        if not isinstance(self.body, BlockStmt):
            raise TypeError("Function body must be a BlockStmt")
        _validate_children(self, (self.body,), "body")


@dataclass(frozen=True, slots=True)
class BlockStmt(Statement):
    statements: tuple[Statement, ...]

    def __post_init__(self) -> None:
        super(BlockStmt, self).__post_init__()
        statements = _tuple_of(self.statements, "statements")
        object.__setattr__(self, "statements", statements)
        if any(not isinstance(item, Statement) for item in statements):
            raise TypeError("Block statements must contain Statement nodes")
        _validate_children(self, statements, "statements")


@dataclass(frozen=True, slots=True)
class IfStmt(Statement):
    condition: Expression
    then_branch: BlockStmt
    else_branch: BlockStmt | "IfStmt" | None

    def __post_init__(self) -> None:
        super(IfStmt, self).__post_init__()
        if not isinstance(self.condition, Expression):
            raise TypeError("If condition must be an Expression")
        if not isinstance(self.then_branch, BlockStmt):
            raise TypeError("If then_branch must be a BlockStmt")
        if self.else_branch is not None and not isinstance(self.else_branch, (BlockStmt, IfStmt)):
            raise TypeError("If else_branch must be a BlockStmt, IfStmt, or None")
        _validate_children(self, tuple(x for x in (self.condition, self.then_branch, self.else_branch) if x is not None), "branches")


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
        _validate_children(self, (self.condition, self.body), "condition/body")


@dataclass(frozen=True, slots=True)
class ReturnStmt(Statement):
    value: Expression | None

    def __post_init__(self) -> None:
        super(ReturnStmt, self).__post_init__()
        if self.value is not None and not isinstance(self.value, Expression):
            raise TypeError("Return value must be an Expression or None")
        _validate_children(self, tuple(x for x in (self.value,) if x is not None), "value")


@dataclass(frozen=True, slots=True)
class ExpressionStmt(Statement):
    expression: Expression

    def __post_init__(self) -> None:
        super(ExpressionStmt, self).__post_init__()
        if not isinstance(self.expression, Expression):
            raise TypeError("ExpressionStmt requires an Expression")
        _validate_children(self, (self.expression,), "expression")


@dataclass(frozen=True, slots=True)
class LiteralExpr(Expression):
    value: object

    def __post_init__(self) -> None:
        super(LiteralExpr, self).__post_init__()
        allowed_types = (type(None), bool, int, float, str)
        if type(self.value) not in allowed_types:
            raise TypeError("Literal value must be an immutable Zen primitive")
        if type(self.value) is float and not math.isfinite(self.value):
            raise ValueError("Literal float must be finite")


@dataclass(frozen=True, slots=True)
class IdentifierExpr(Expression):
    name: str

    def __post_init__(self) -> None:
        super(IdentifierExpr, self).__post_init__()
        if not isinstance(self.name, str):
            raise TypeError("Identifier name must be a string")


@dataclass(frozen=True, slots=True)
class UnaryExpr(Expression):
    operator: str
    operand: Expression

    def __post_init__(self) -> None:
        super(UnaryExpr, self).__post_init__()
        if not isinstance(self.operator, str):
            raise TypeError("Unary operator must be a string")
        if not isinstance(self.operand, Expression):
            raise TypeError("Unary operand must be an Expression")
        _validate_children(self, (self.operand,), "operand")


@dataclass(frozen=True, slots=True)
class BinaryExpr(Expression):
    left: Expression
    operator: str
    right: Expression

    def __post_init__(self) -> None:
        super(BinaryExpr, self).__post_init__()
        if not isinstance(self.left, Expression) or not isinstance(self.right, Expression):
            raise TypeError("Binary operands must be Expressions")
        if not isinstance(self.operator, str):
            raise TypeError("Binary operator must be a string")
        _validate_children(self, (self.left, self.right), "operands")


@dataclass(frozen=True, slots=True)
class GroupingExpr(Expression):
    expression: Expression

    def __post_init__(self) -> None:
        super(GroupingExpr, self).__post_init__()
        if not isinstance(self.expression, Expression):
            raise TypeError("Grouping expression must be an Expression")
        _validate_children(self, (self.expression,), "expression")


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
        _validate_children(self, (self.target, self.value), "target/value")


@dataclass(frozen=True, slots=True)
class CallExpr(Expression):
    callee: Expression
    arguments: tuple[Expression, ...]

    def __post_init__(self) -> None:
        super(CallExpr, self).__post_init__()
        if not isinstance(self.callee, Expression):
            raise TypeError("Call callee must be an Expression")
        arguments = _tuple_of(self.arguments, "arguments", child_collection=False)
        if len(arguments) + 1 > MAX_DIRECT_CHILDREN:
            raise ValueError("callee/arguments exceeds MAX_DIRECT_CHILDREN")
        object.__setattr__(self, "arguments", arguments)
        if any(not isinstance(item, Expression) for item in arguments):
            raise TypeError("Call arguments must contain Expression nodes")
        _validate_children(self, (self.callee, *arguments), "callee/arguments")
