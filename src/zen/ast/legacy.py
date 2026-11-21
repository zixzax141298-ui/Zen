"""Explicit, non-mutating adapter from legacy ASTs to canonical ASTs."""

from dataclasses import replace

from .nodes import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    ExpressionStmt,
    FunctionDecl,
    GroupingExpr,
    IdentifierExpr,
    IfStmt,
    LiteralExpr,
    Node,
    Program,
    ReturnStmt,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)

from .source_identity import SourceIdentifier
from .traversal import iter_child_nodes
from .validation import ASTValidationLimits, _validate_ast


def _with_identity(
    node: Node,
    source_id: SourceIdentifier,
    clones: dict[int, Node],
) -> Node:

    changes = {"source_id": source_id}

    if isinstance(node, (Program, BlockStmt)):
        changes["statements"] = tuple(
            clones[id(child)]
            for child in node.statements
        )

    elif isinstance(node, FunctionDecl):
        changes["body"] = clones[id(node.body)]

    elif isinstance(node, VarDecl):
        if node.initializer is not None:
            changes["initializer"] = clones[
                id(node.initializer)
            ]

    elif isinstance(node, IfStmt):
        changes["condition"] = clones[id(node.condition)]
        changes["then_branch"] = clones[id(node.then_branch)]

        if node.else_branch is not None:
            changes["else_branch"] = clones[
                id(node.else_branch)
            ]

    elif isinstance(node, WhileStmt):
        changes["condition"] = clones[id(node.condition)]
        changes["body"] = clones[id(node.body)]

    elif isinstance(node, ReturnStmt):
        if node.value is not None:
            changes["value"] = clones[id(node.value)]

    elif isinstance(node, ExpressionStmt):
        changes["expression"] = clones[id(node.expression)]

    elif isinstance(node, UnaryExpr):
        changes["operand"] = clones[id(node.operand)]

    elif isinstance(node, BinaryExpr):
        changes["left"] = clones[id(node.left)]
        changes["right"] = clones[id(node.right)]

    elif isinstance(node, GroupingExpr):
        changes["expression"] = clones[id(node.expression)]

    elif isinstance(node, AssignExpr):
        changes["target"] = clones[id(node.target)]
        changes["value"] = clones[id(node.value)]

    elif isinstance(node, CallExpr):
        changes["callee"] = clones[id(node.callee)]
        changes["arguments"] = tuple(
            clones[id(child)]
            for child in node.arguments
        )

    elif not isinstance(node, (LiteralExpr, IdentifierExpr)):
        raise TypeError("unsupported legacy AST node type")

    return replace(node, **changes)


def adapt_legacy_ast(
    root: Program,
    source_id: SourceIdentifier,
    *,
    limits: ASTValidationLimits | None = None,
) -> Program:
    """Clone a legacy Program and assign one explicitly supplied source ID.

    The input must be a well-formed tree whose nodes have no source identity.
    The input is never mutated. Cycles, reused nodes, malformed children, or
    pre-existing identities are rejected rather than silently overwritten.
    """

    if not isinstance(root, Program):
        raise TypeError("legacy adapter requires a Program root")

    if not isinstance(source_id, SourceIdentifier):
        raise TypeError("source_id must be a SourceIdentifier")

    if limits is None:
        limits = ASTValidationLimits()

    if not isinstance(limits, ASTValidationLimits):
        raise TypeError(
            "limits must be ASTValidationLimits or None"
        )

    result = _validate_ast(
        root,
        limits,
        require_source_identity=False,
    )

    if not result.is_valid or not result.complete:
        first = (
            result.diagnostics[0].message
            if result.diagnostics
            else "incomplete validation"
        )

        raise ValueError(
            f"legacy AST cannot be adapted: {first}"
        )

    # Explicitly reject any existing identity. The adapter must not overwrite it.
    stack = [root]
    seen = set()

    while stack:
        node = stack.pop()
        node_id = id(node)

        if node_id in seen:
            raise ValueError(
                "legacy AST contains a cycle or reused node"
            )

        seen.add(node_id)

        if node.source_id is not None:
            raise ValueError(
                "legacy adapter refuses to overwrite an existing source identity"
            )

        stack.extend(
            reversed(tuple(iter_child_nodes(node)))
        )

    # Iterative post-order cloning; no recursive Python calls.
    clones: dict[int, Node] = {}
    postorder = [(root, False)]

    while postorder:
        node, leaving = postorder.pop()

        if not leaving:
            postorder.append((node, True))

            for child in reversed(tuple(iter_child_nodes(node))):
                postorder.append((child, False))

        else:
            clones[id(node)] = _with_identity(
                node,
                source_id,
                clones,
            )

    adapted = clones[id(root)]
    return adapted  # type: ignore[return-value]
