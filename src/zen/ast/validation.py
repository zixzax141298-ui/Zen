"""Deterministic, iterative structural validation for canonical Zen ASTs."""

from dataclasses import dataclass
from enum import Enum
from itertools import chain, islice
import math

from zen.limits import (
    MAX_AST_DEPTH,
    MAX_AST_NODES,
    MAX_DIRECT_CHILDREN,
    MAX_EXPRESSION_NODES,
    MAX_STATEMENT_NODES,
)

from .nodes import (
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
    Node,
    Program,
    ReturnStmt,
    Statement,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)

from .source_identity import SourceIdentifier
from .source_location import SourceLocation
from .source_span import SourceSpan
from .traversal import iter_child_nodes


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR
    component: str = "ZASI"
    source_location: SourceLocation | None = None
    line: int | None = None
    column: int | None = None
    related_locations: tuple[SourceLocation, ...] = ()

    def __post_init__(self) -> None:
        if type(self.code) is not str or not self.code:
            raise ValueError("diagnostic code must be non-empty")

        if type(self.message) is not str or not self.message:
            raise ValueError("diagnostic message must be non-empty")

        if not isinstance(self.severity, DiagnosticSeverity):
            raise TypeError(
                "diagnostic severity must be DiagnosticSeverity"
            )

        if type(self.component) is not str or not self.component:
            raise ValueError("diagnostic component must be non-empty")

        if (
            self.source_location is not None
            and not isinstance(self.source_location, SourceLocation)
        ):
            raise TypeError(
                "source_location must be a SourceLocation or None"
            )

        if self.line is not None and (
            type(self.line) is not int or self.line < 1
        ):
            raise ValueError(
                "diagnostic line must be a positive integer or None"
            )

        if self.column is not None and (
            type(self.column) is not int or self.column < 1
        ):
            raise ValueError(
                "diagnostic column must be a positive integer or None"
            )

        if type(self.related_locations) is not tuple or any(
            not isinstance(item, SourceLocation)
            for item in self.related_locations
        ):
            raise TypeError(
                "related_locations must be a tuple of SourceLocation values"
            )


@dataclass(frozen=True, slots=True)
class ASTValidationLimits:
    """Per-validation limits that may tighten, but never loosen, hard limits."""

    max_nodes: int = MAX_AST_NODES
    max_depth: int = MAX_AST_DEPTH
    max_expression_nodes: int = MAX_EXPRESSION_NODES
    max_statement_nodes: int = MAX_STATEMENT_NODES
    max_parameters: int = MAX_DIRECT_CHILDREN
    max_direct_children: int = MAX_DIRECT_CHILDREN

    def __post_init__(self) -> None:
        ceilings = {
            "max_nodes": MAX_AST_NODES,
            "max_depth": MAX_AST_DEPTH,
            "max_expression_nodes": MAX_EXPRESSION_NODES,
            "max_statement_nodes": MAX_STATEMENT_NODES,
            "max_parameters": MAX_DIRECT_CHILDREN,
            "max_direct_children": MAX_DIRECT_CHILDREN,
        }

        for name, ceiling in ceilings.items():
            value = getattr(self, name)

            if type(value) is not int or value < 1:
                raise ValueError(
                    f"{name} must be a positive integer"
                )

            if value > ceiling:
                raise ValueError(
                    f"{name} cannot exceed the configured hard ceiling {ceiling}"
                )


@dataclass(frozen=True, slots=True)
class ASTValidationResult:
    is_valid: bool
    diagnostics: tuple[Diagnostic, ...]
    nodes_visited: int
    max_depth: int
    expression_nodes: int
    statement_nodes: int
    parameter_count: int
    complete: bool

    @property
    def valid(self) -> bool:
        """Compatibility-friendly shorthand for ``is_valid``."""
        return self.is_valid


_KNOWN_NODE_TYPES = (
    Program,
    VarDecl,
    FunctionDecl,
    BlockStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    ExpressionStmt,
    LiteralExpr,
    IdentifierExpr,
    UnaryExpr,
    BinaryExpr,
    GroupingExpr,
    AssignExpr,
    CallExpr,
)


def _node_location(node: Node) -> SourceLocation | None:
    source_id = getattr(node, "source_id", None)
    span = getattr(node, "span", None)

    if (
        isinstance(source_id, SourceIdentifier)
        and isinstance(span, SourceSpan)
    ):
        try:
            span.__post_init__()
            return SourceLocation(source_id, span)
        except (TypeError, ValueError):
            return None

    return None


def _children_for_node(
    node: Node,
    emit,
    max_direct_children: int,
    *,
    require_function_metadata: bool,
):
    """Return validated direct children, parameter count, and completeness."""

    children: list[Node] = []
    parameter_count = 0
    complete = True

    def one(
        value,
        expected,
        field_name: str,
        *,
        optional: bool = False,
    ) -> None:
        nonlocal complete

        if optional and value is None:
            return

        if not isinstance(value, expected):
            emit(
                "AST_CHILD_TYPE_INVALID",
                f"{field_name} has an invalid child type",
                node,
            )
            complete = False
            return

        children.append(value)

    def many(values, expected, field_name: str) -> None:
        nonlocal complete

        if type(values) is not tuple:
            emit(
                "AST_CHILD_COLLECTION_INVALID",
                f"{field_name} must be a tuple",
                node,
            )
            complete = False
            return

        if len(values) > max_direct_children:
            emit(
                "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
                f"{field_name} exceeds the direct-child limit",
                node,
            )
            complete = False

        for index, value in enumerate(
            islice(values, max_direct_children)
        ):
            if not isinstance(value, expected):
                emit(
                    "AST_CHILD_TYPE_INVALID",
                    f"{field_name}[{index}] has an invalid child type",
                    node,
                )
                complete = False
            else:
                children.append(value)

    node_type = type(node)

    if node_type in (Program, BlockStmt):
        many(
            getattr(node, "statements", None),
            Statement,
            "statements",
        )

    elif node_type is FunctionDecl:
        if type(getattr(node, "name", None)) is not str:
            emit(
                "AST_FIELD_INVALID",
                "function name must be a string",
                node,
            )
            complete = False

        parameters = getattr(node, "parameters", None)

        if type(parameters) is not tuple:
            emit(
                "AST_FIELD_INVALID",
                "function parameters must be a tuple",
                node,
            )
            complete = False
        else:
            parameter_count = len(parameters)

            if parameter_count > max_direct_children:
                emit(
                    "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
                    "function parameters exceed the direct-child limit",
                    node,
                )
                complete = False

            if any(
                type(item) is not str
                for item in islice(
                    parameters,
                    max_direct_children,
                )
            ):
                emit(
                    "AST_FIELD_INVALID",
                    "function parameters must contain strings",
                    node,
                )
                complete = False

        name_span = getattr(node, "name_span", None)
        parameter_spans = getattr(node, "parameter_spans", None)
        body = getattr(node, "body", None)

        if name_span is None and parameter_spans is None:
            if require_function_metadata:
                emit(
                    "AST_FUNCTION_METADATA_MISSING",
                    "canonical FunctionDecl requires name_span and parameter_spans",
                    node,
                )
                complete = False
        elif name_span is None or parameter_spans is None:
            emit(
                "AST_FUNCTION_METADATA_MISSING",
                "FunctionDecl metadata must provide both name_span and parameter_spans",
                node,
            )
            complete = False
        else:
            metadata_valid = True

            if not isinstance(name_span, SourceSpan):
                emit(
                    "AST_FUNCTION_NAME_SPAN_INVALID",
                    "function name_span must be a SourceSpan",
                    node,
                )
                metadata_valid = False
            else:
                try:
                    name_span.__post_init__()
                except (TypeError, ValueError):
                    emit(
                        "AST_FUNCTION_NAME_SPAN_INVALID",
                        "function name_span is malformed",
                        node,
                    )
                    metadata_valid = False

            if type(parameter_spans) is not tuple:
                emit(
                    "AST_FUNCTION_PARAMETER_SPANS_INVALID",
                    "function parameter_spans must be a tuple",
                    node,
                )
                metadata_valid = False
            else:
                if (
                    type(parameters) is tuple
                    and len(parameter_spans) != len(parameters)
                ):
                    emit(
                        "AST_FUNCTION_PARAMETER_SPAN_COUNT_MISMATCH",
                        "parameter_spans count must match parameters count",
                        node,
                    )
                    metadata_valid = False

                if len(parameter_spans) > max_direct_children:
                    emit(
                        "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
                        "function parameter spans exceed the direct-child limit",
                        node,
                    )
                    metadata_valid = False
                else:
                    for index, item in enumerate(parameter_spans):
                        if not isinstance(item, SourceSpan):
                            emit(
                                "AST_FUNCTION_PARAMETER_SPAN_INVALID",
                                f"parameter_spans[{index}] must be a SourceSpan",
                                node,
                            )
                            metadata_valid = False
                            continue

                        try:
                            item.__post_init__()
                        except (TypeError, ValueError):
                            emit(
                                "AST_FUNCTION_PARAMETER_SPAN_INVALID",
                                f"parameter_spans[{index}] is malformed",
                                node,
                            )
                            metadata_valid = False

            declaration_span = getattr(node, "span", None)

            if not isinstance(declaration_span, SourceSpan):
                metadata_valid = False
            else:
                try:
                    declaration_span.__post_init__()
                except (TypeError, ValueError):
                    metadata_valid = False

            if metadata_valid and isinstance(body, BlockStmt):
                previous_end = None

                for item in chain(
                    (name_span,),
                    parameter_spans,
                    (body.span,),
                ):
                    if not isinstance(item, SourceSpan):
                        metadata_valid = False
                        break

                    if not declaration_span.contains(item):
                        emit(
                            "AST_FUNCTION_METADATA_OUT_OF_RANGE",
                            "function metadata and body spans must be contained in the declaration span",
                            node,
                        )
                        metadata_valid = False
                        break

                    if (
                        previous_end is not None
                        and item.start < previous_end
                    ):
                        emit(
                            "AST_FUNCTION_METADATA_ORDER_INVALID",
                            "function name, parameter, and body spans must be ordered and non-overlapping",
                            node,
                        )
                        metadata_valid = False
                        break

                    previous_end = item.end

            if not metadata_valid:
                complete = False

        one(
            body,
            BlockStmt,
            "body",
        )

    elif node_type is VarDecl:
        if type(getattr(node, "name", None)) is not str:
            emit(
                "AST_FIELD_INVALID",
                "variable name must be a string",
                node,
            )

        if type(getattr(node, "is_const", None)) is not bool:
            emit(
                "AST_FIELD_INVALID",
                "is_const must be a boolean",
                node,
            )

        one(
            getattr(node, "initializer", None),
            Expression,
            "initializer",
            optional=True,
        )

    elif node_type is IfStmt:
        one(
            getattr(node, "condition", None),
            Expression,
            "condition",
        )
        one(
            getattr(node, "then_branch", None),
            BlockStmt,
            "then_branch",
        )
        one(
            getattr(node, "else_branch", None),
            (BlockStmt, IfStmt),
            "else_branch",
            optional=True,
        )

    elif node_type is WhileStmt:
        one(
            getattr(node, "condition", None),
            Expression,
            "condition",
        )
        one(
            getattr(node, "body", None),
            BlockStmt,
            "body",
        )

    elif node_type is ReturnStmt:
        one(
            getattr(node, "value", None),
            Expression,
            "value",
            optional=True,
        )

    elif node_type is ExpressionStmt:
        one(
            getattr(node, "expression", None),
            Expression,
            "expression",
        )

    elif node_type is LiteralExpr:
        value = getattr(node, "value", object())

        if type(value) not in (
            type(None),
            bool,
            int,
            float,
            str,
        ):
            emit(
                "AST_FIELD_INVALID",
                "literal value is not an immutable Zen primitive",
                node,
            )
            complete = False

        elif type(value) is float and not math.isfinite(value):
            emit(
                "AST_FIELD_INVALID",
                "literal float must be finite",
                node,
            )

    elif node_type is IdentifierExpr:
        if type(getattr(node, "name", None)) is not str:
            emit(
                "AST_FIELD_INVALID",
                "identifier name must be a string",
                node,
            )
            complete = False

    elif node_type is UnaryExpr:
        if type(getattr(node, "operator", None)) is not str:
            emit(
                "AST_FIELD_INVALID",
                "unary operator must be a string",
                node,
            )

        one(
            getattr(node, "operand", None),
            Expression,
            "operand",
        )

    elif node_type is BinaryExpr:
        if type(getattr(node, "operator", None)) is not str:
            emit(
                "AST_FIELD_INVALID",
                "binary operator must be a string",
                node,
            )

        one(
            getattr(node, "left", None),
            Expression,
            "left",
        )
        one(
            getattr(node, "right", None),
            Expression,
            "right",
        )

    elif node_type is GroupingExpr:
        one(
            getattr(node, "expression", None),
            Expression,
            "expression",
        )

    elif node_type is AssignExpr:
        one(
            getattr(node, "target", None),
            IdentifierExpr,
            "target",
        )
        one(
            getattr(node, "value", None),
            Expression,
            "value",
        )

    elif node_type is CallExpr:
        one(
            getattr(node, "callee", None),
            Expression,
            "callee",
        )
        many(
            getattr(node, "arguments", None),
            Expression,
            "arguments",
        )

    else:
        emit(
            "AST_NODE_TYPE_INVALID",
            "AST contains an unsupported Node subclass",
            node,
        )
        complete = False

    if len(children) > max_direct_children:
        emit(
            "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
            "node exceeds the direct-child limit",
            node,
        )
        children = children[:max_direct_children]
        complete = False

    return children, parameter_count, complete


def _validate_ast(
    root: object,
    limits: ASTValidationLimits,
    *,
    require_source_identity: bool,
    require_function_metadata: bool,
) -> ASTValidationResult:

    diagnostics: list[Diagnostic] = []

    nodes_visited = 0
    expression_nodes = 0
    statement_nodes = 0
    parameter_count = 0
    maximum_depth = 0
    complete = True

    root_source_id = getattr(root, "source_id", None)

    def emit(
        code: str,
        message: str,
        node: object | None = None,
    ) -> None:
        location = (
            _node_location(node)
            if isinstance(node, Node)
            else None
        )

        diagnostics.append(
            Diagnostic(
                code=code,
                message=message,
                component="ZASI",
                source_location=location,
            )
        )

    if not isinstance(root, Program):
        emit(
            "AST_ROOT_TYPE_INVALID",
            "validate_ast requires a Program root",
        )

        return ASTValidationResult(
            False,
            tuple(diagnostics),
            0,
            0,
            0,
            0,
            0,
            False,
        )

    # Explicit enter/exit frames avoid Python recursion.
    stack = [(root, 1, False)]

    active: set[int] = set()
    seen: set[int] = set()

    while stack:
        node, depth, leaving = stack.pop()
        node_id = id(node)

        if leaving:
            active.discard(node_id)
            continue

        if node_id in active:
            emit(
                "AST_NODE_CYCLE",
                "AST cycle detected",
                node,
            )
            continue

        if node_id in seen:
            emit(
                "AST_NODE_REUSED",
                "AST node is reused at multiple tree locations",
                node,
            )
            continue

        if nodes_visited >= limits.max_nodes:
            emit(
                "AST_NODE_LIMIT_EXCEEDED",
                "AST node-count limit exceeded",
                node,
            )
            complete = False
            break

        if depth > limits.max_depth:
            emit(
                "AST_DEPTH_LIMIT_EXCEEDED",
                "AST structural-depth limit exceeded",
                node,
            )
            complete = False
            continue

        seen.add(node_id)
        active.add(node_id)

        nodes_visited += 1
        maximum_depth = max(maximum_depth, depth)

        if type(node) not in _KNOWN_NODE_TYPES:
            emit(
                "AST_NODE_TYPE_INVALID",
                "AST contains an unsupported Node subclass",
                node,
            )
            complete = False
            stack.append((node, depth, True))
            continue

        if require_source_identity:
            source_id = getattr(node, "source_id", None)

            if source_id is None:
                emit(
                    "AST_SOURCE_ID_MISSING",
                    "canonical AST node requires a SourceIdentifier",
                    node,
                )

            elif not isinstance(source_id, SourceIdentifier):
                emit(
                    "AST_SOURCE_ID_INVALID",
                    "source_id must be a SourceIdentifier",
                    node,
                )

            elif (
                isinstance(root_source_id, SourceIdentifier)
                and source_id != root_source_id
            ):
                emit(
                    "AST_SOURCE_ID_MISMATCH",
                    "all nodes in one compilation unit must share its SourceIdentifier",
                    node,
                )

        else:
            source_id = getattr(node, "source_id", None)

            if (
                source_id is not None
                and not isinstance(source_id, SourceIdentifier)
            ):
                emit(
                    "AST_SOURCE_ID_INVALID",
                    "source_id must be a SourceIdentifier or None",
                    node,
                )

        span = getattr(node, "span", None)
        span_valid = isinstance(span, SourceSpan)

        if span_valid:
            try:
                span.__post_init__()
            except (TypeError, ValueError):
                span_valid = False

        if not span_valid:
            emit(
                "AST_SPAN_INVALID",
                "AST node has an invalid SourceSpan",
                node,
            )

        if isinstance(node, Expression):
            expression_nodes += 1

            if expression_nodes > limits.max_expression_nodes:
                emit(
                    "AST_EXPRESSION_LIMIT_EXCEEDED",
                    "AST expression-node limit exceeded",
                    node,
                )
                complete = False
                break

        if isinstance(node, Statement):
            statement_nodes += 1

            if statement_nodes > limits.max_statement_nodes:
                emit(
                    "AST_STATEMENT_LIMIT_EXCEEDED",
                    "AST statement-node limit exceeded",
                    node,
                )
                complete = False
                break

        children, node_parameters, children_complete = (
            _children_for_node(
                node,
                emit,
                limits.max_direct_children,
                require_function_metadata=require_function_metadata,
            )
        )

        complete = complete and children_complete

        parameter_count += node_parameters

        if parameter_count > limits.max_parameters:
            emit(
                "AST_PARAMETER_LIMIT_EXCEEDED",
                "AST parameter-count limit exceeded",
                node,
            )
            complete = False
            break

        if span_valid and children_complete:
            try:
                require_ordered_children(
                    node,
                    tuple(children),
                    "children",
                )
            except (TypeError, ValueError):
                emit(
                    "AST_SOURCE_ORDER_INVALID",
                    "child spans must be contained, ordered, and non-overlapping",
                    node,
                )

        stack.append((node, depth, True))

        for child in reversed(children):
            stack.append((child, depth + 1, False))

    is_valid = not any(
        item.severity is DiagnosticSeverity.ERROR
        for item in diagnostics
    )

    return ASTValidationResult(
        is_valid,
        tuple(diagnostics),
        nodes_visited,
        maximum_depth,
        expression_nodes,
        statement_nodes,
        parameter_count,
        complete,
    )


def validate_ast(
    program: Program,
    limits: ASTValidationLimits | None = None,
) -> ASTValidationResult:
    """Validate canonical AST structure without mutating or repairing it."""

    if limits is None:
        limits = ASTValidationLimits()

    if not isinstance(limits, ASTValidationLimits):
        raise TypeError(
            "limits must be ASTValidationLimits or None"
        )

    return _validate_ast(
        program,
        limits,
        require_source_identity=True,
        require_function_metadata=True,
    )


def require_child_span(
    parent: Node,
    child: Node,
    field_name: str,
) -> None:

    if not isinstance(parent, Node) or not isinstance(child, Node):
        raise TypeError("parent and child must be AST Nodes")

    if not parent.span.contains(child.span):
        raise ValueError(
            f"{field_name} span must be contained in parent span"
        )


def require_ordered_children(
    parent: Node,
    children: tuple[Node, ...],
    field_name: str,
) -> None:

    if not isinstance(parent, Node):
        raise TypeError("parent must be an AST Node")

    previous = None

    for child in children:
        if not isinstance(child, Node):
            raise TypeError(
                f"{field_name} must contain only AST Nodes"
            )

        require_child_span(parent, child, field_name)

        if (
            previous is not None
            and child.span.start < previous.span.end
        ):
            raise ValueError(
                f"{field_name} spans must be ordered and non-overlapping"
            )

        previous = child


def detect_cycles(root: Node) -> None:
    """Raise ValueError if a depth-first traversal finds a graph cycle."""

    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")

    visiting: set[int] = set()
    visited: set[int] = set()

    stack = [(root, iter_child_nodes(root))]
    visiting.add(id(root))

    while stack:
        node, children = stack[-1]

        try:
            child = next(children)

        except StopIteration:
            stack.pop()
            visiting.remove(id(node))
            visited.add(id(node))
            continue

        child_id = id(child)

        if child_id in visiting:
            raise ValueError("AST cycle detected")

        if child_id not in visited:
            visiting.add(child_id)
            stack.append(
                (child, iter_child_nodes(child))
            )


def detect_reused_nodes(root: Node) -> None:
    """Raise ValueError if a Node object occurs at multiple tree locations."""

    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")

    seen = {id(root)}
    stack = [root]

    while stack:
        node = stack.pop()

        for child in iter_child_nodes(node):
            child_id = id(child)

            if child_id in seen:
                raise ValueError("AST node reuse detected")

            seen.add(child_id)
            stack.append(child)


def _unique_preorder(root: Node):
    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")

    seen = set()
    stack = [root]

    while stack:
        node = stack.pop()
        node_id = id(node)

        if node_id in seen:
            raise ValueError("AST graph is not a finite tree")

        seen.add(node_id)
        yield node

        stack.extend(
            reversed(tuple(iter_child_nodes(node)))
        )


def count_nodes(root: Node) -> int:
    """Count all nodes in a finite tree, including its root."""
    return sum(1 for _ in _unique_preorder(root))


def measure_depth(root: Node) -> int:
    """Return maximum structural depth; the root has depth one."""

    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")

    maximum = 0
    seen = set()
    stack = [(root, 1)]

    while stack:
        node, depth = stack.pop()

        if id(node) in seen:
            raise ValueError("AST graph is not a finite tree")

        seen.add(id(node))
        maximum = max(maximum, depth)

        stack.extend(
            (child, depth + 1)
            for child in iter_child_nodes(node)
        )

    return maximum
