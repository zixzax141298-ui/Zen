"""Deterministic, read-only traversal helpers for Zen AST nodes."""

from collections.abc import Iterator

from .nodes import (
    AssignExpr, BinaryExpr, BlockStmt, CallExpr, ExpressionStmt, FunctionDecl,
    GroupingExpr, IfStmt, Node, Program, ReturnStmt, UnaryExpr, VarDecl,
    WhileStmt,
)


def iter_child_nodes(node: Node) -> Iterator[Node]:
    """Yield direct AST children in source/field order; ignore non-node fields."""
    if not isinstance(node, Node):
        raise TypeError("iter_child_nodes() requires an AST Node")
    if isinstance(node, (Program, BlockStmt)):
        children = node.statements
    elif isinstance(node, FunctionDecl):
        children = (node.body,)
    elif isinstance(node, VarDecl):
        children = (node.initializer,)
    elif isinstance(node, IfStmt):
        children = (node.condition, node.then_branch, node.else_branch)
    elif isinstance(node, WhileStmt):
        children = (node.condition, node.body)
    elif isinstance(node, ReturnStmt):
        children = (node.value,)
    elif isinstance(node, ExpressionStmt):
        children = (node.expression,)
    elif isinstance(node, UnaryExpr):
        children = (node.operand,)
    elif isinstance(node, BinaryExpr):
        children = (node.left, node.right)
    elif isinstance(node, GroupingExpr):
        children = (node.expression,)
    elif isinstance(node, AssignExpr):
        children = (node.target, node.value)
    elif isinstance(node, CallExpr):
        children = (node.callee, *node.arguments)
    else:
        children = ()
    for child in children:
        if isinstance(child, Node):
            yield child
