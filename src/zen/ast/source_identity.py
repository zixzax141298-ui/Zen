"""Stable identity token for one logical Zen compilation unit."""

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SourceIdentifier:
    """Immutable, opaque identifier for one logical compilation unit.

    Call ``new()`` explicitly for a new source input. To continue an existing
    logical compilation unit, pass its previously retained identifier. The
    token's syntax does not prove registry membership or authenticity.
    """

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("SourceIdentifier value must be a string")

        if not self.value or len(self.value) > 128:
            raise ValueError(
                "SourceIdentifier must contain 1 to 128 characters"
            )

        if self.value.strip() != self.value:
            raise ValueError(
                "SourceIdentifier cannot have surrounding whitespace"
            )

        if any(
            not char.isprintable() or char.isspace()
            for char in self.value
        ):
            raise ValueError(
                "SourceIdentifier cannot contain control or whitespace characters"
            )

    @classmethod
    def new(cls) -> "SourceIdentifier":
        """Allocate a fresh UUID4-backed token; allocation is never implicit."""
        return cls(str(uuid4()))

    @classmethod
    def parse(cls, value: str) -> "SourceIdentifier":
        """Restore an opaque serialized token.

        Parsing validates the token representation only. It does not prove
        registry membership, authenticity, or historical continuity.
        """
        return cls(value)

    def __str__(self) -> str:
        return self.value
