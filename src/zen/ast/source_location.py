"""A source identity paired with a coordinate span."""

from dataclasses import dataclass

from .source_identity import SourceIdentifier
from .source_span import SourceSpan


@dataclass(frozen=True, slots=True)
class SourceLocation:
    source_id: SourceIdentifier
    span: SourceSpan

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, SourceIdentifier):
            raise TypeError(
                "SourceLocation source_id must be a SourceIdentifier"
            )

        if not isinstance(self.span, SourceSpan):
            raise TypeError(
                "SourceLocation span must be a SourceSpan"
            )

        self.span.__post_init__()

    @property
    def start_line(self) -> int:
        return self.span.start_line

    @property
    def start_column(self) -> int:
        return self.span.start_column

    @property
    def end_line(self) -> int:
        return self.span.end_line

    @property
    def end_column(self) -> int:
        return self.span.end_column
