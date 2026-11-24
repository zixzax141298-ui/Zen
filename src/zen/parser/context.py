"""Immutable parse context for resource accounting."""

from dataclasses import dataclass, field

from zen.ast.source_identity import SourceIdentifier
from zen.ast.source_span import SourceSpan
from zen.limits import MAX_AST_NODES, MAX_PARSER_DEPTH

from .diagnostics import ParseError


@dataclass(frozen=True, slots=True)
class ParseContext:
    """Tracks parser recursion depth and AST node count."""

    depth: int = 0
    node_count: int = 0
    source_id: SourceIdentifier | None = None

    @classmethod
    def initial(cls, *, source_id: SourceIdentifier | None = None) -> ParseContext:
        return cls(depth=0, node_count=0, source_id=source_id)

    def enter(self, span: SourceSpan | None = None) -> ParseContext:
        new_depth = self.depth + 1
        if new_depth > MAX_PARSER_DEPTH:
            raise ParseError(
                f"Parser recursion depth exceeded (max {MAX_PARSER_DEPTH})",
                span.start_line if span else 1,
                span.start_column if span else 1,
                span,
                source_id=self.source_id,
            )
        return ParseContext(
            depth=new_depth,
            node_count=self.node_count,
            source_id=self.source_id,
        )

    def track_node(self, span: SourceSpan | None = None) -> ParseContext:
        new_count = self.node_count + 1
        if new_count > MAX_AST_NODES:
            raise ParseError(
                f"AST node limit exceeded (max {MAX_AST_NODES})",
                span.start_line if span else 1,
                span.start_column if span else 1,
                span,
                source_id=self.source_id,
            )
        return ParseContext(
            depth=self.depth,
            node_count=new_count,
            source_id=self.source_id,
        )
