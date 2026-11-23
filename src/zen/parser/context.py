"""Immutable parser accounting context, separate from AST validation."""

from dataclasses import dataclass, field

from zen.limits import MAX_AST_NODES, MAX_PARSER_DEPTH
from zen.ast.source_identity import SourceIdentifier
from zen.ast.source_span import SourceSpan

from .diagnostics import ParseError


def _location(
    span: SourceSpan | None,
) -> tuple[int, int]:

    if span is None:
        return 1, 1

    return span.start_line, span.start_column


@dataclass(frozen=True, slots=True)
class ParseContext:
    # `depth` remains the public compatibility name;
    # it means parser nesting depth.
    depth: int
    node_count: int

    source_id: SourceIdentifier | None = field(
        default=None,
        kw_only=True,
    )

    def __post_init__(self) -> None:
        if type(self.depth) is not int or self.depth < 0:
            raise ValueError(
                "parser depth must be a non-negative integer"
            )

        if type(self.node_count) is not int or self.node_count < 0:
            raise ValueError(
                "node_count must be a non-negative integer"
            )

        if self.depth > MAX_PARSER_DEPTH:
            raise ValueError(
                "parser depth exceeds MAX_PARSER_DEPTH"
            )

        if self.node_count > MAX_AST_NODES:
            raise ValueError(
                "node_count exceeds MAX_AST_NODES"
            )

        if (
            self.source_id is not None
            and not isinstance(self.source_id, SourceIdentifier)
        ):
            raise TypeError(
                "source_id must be a SourceIdentifier or None"
            )

    @property
    def parser_depth(self) -> int:
        return self.depth

    @classmethod
    def initial(
        cls,
        source_id: SourceIdentifier | None = None,
    ) -> "ParseContext":

        return cls(
            depth=0,
            node_count=0,
            source_id=source_id,
        )

    def enter(
        self,
        span: SourceSpan | None = None,
    ) -> "ParseContext":

        depth = self.depth + 1

        if depth > MAX_PARSER_DEPTH:
            line, column = _location(span)

            raise ParseError(
                "Parser nesting depth limit exceeded",
                line,
                column,
                span,
                source_id=self.source_id,
            )

        return ParseContext(
            depth=depth,
            node_count=self.node_count,
            source_id=self.source_id,
        )

    def track_node(
        self,
        span: SourceSpan | None = None,
    ) -> "ParseContext":

        node_count = self.node_count + 1

        if node_count > MAX_AST_NODES:
            line, column = _location(span)

            raise ParseError(
                "Parser AST node-count limit exceeded",
                line,
                column,
                span,
                source_id=self.source_id,
            )

        return ParseContext(
            depth=self.depth,
            node_count=node_count,
            source_id=self.source_id,
        )
