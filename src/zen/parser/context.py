"""Immutable parser accounting context for AST depth and node limits."""

from dataclasses import dataclass

from zen.limits import MAX_AST_DEPTH, MAX_AST_NODES
from zen.ast.source_span import SourceSpan
from .diagnostics import ParseError


def _location(span: SourceSpan | None) -> tuple[int, int]:
    if span is None:
        return 1, 1
    return span.start_line, span.start_column


@dataclass(frozen=True, slots=True)
class ParseContext:
    depth: int
    node_count: int

    @classmethod
    def initial(cls) -> "ParseContext":
        return cls(depth=0, node_count=0)

    def enter(self, span: SourceSpan | None = None) -> "ParseContext":
        depth = self.depth + 1
        if depth > MAX_AST_DEPTH:
            line, column = _location(span)
            raise ParseError("AST nesting depth limit exceeded", line, column, span)
        return ParseContext(depth=depth, node_count=self.node_count)

    def track_node(self, span: SourceSpan | None = None) -> "ParseContext":
        node_count = self.node_count + 1
        if node_count > MAX_AST_NODES:
            line, column = _location(span)
            raise ParseError("AST node count limit exceeded", line, column, span)
        return ParseContext(depth=self.depth, node_count=node_count)
