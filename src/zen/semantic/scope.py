"""Scope and symbol table for Zen semantic analysis.

Block scope is the approved v0.1 design decision.
Redeclaration rules (OQ-01) and name-resolution algorithm (OQ-04)
are not finalized; the current implementation uses a conservative
local-shadowing model and records unresolved policy points.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterator


class SymbolKind(Enum):
    VARIABLE = auto()
    CONSTANT = auto()
    FUNCTION = auto()
    PARAMETER = auto()


@dataclass(slots=True)
class Symbol:
    name: str
    kind: SymbolKind
    # Declaration span for diagnostics (optional).
    span: object | None = None
    # Whether a variable has an initializer (relevant for OQ-02).
    initialized: bool = False
    # Arity for functions (None if not a function).
    arity: int | None = None


@dataclass
class Scope:
    """A single lexical scope. Parent chain forms the scope stack."""

    parent: Scope | None = None
    symbols: dict[str, Symbol] = field(default_factory=dict)
    # True when this scope is a function body (affects return validation).
    is_function: bool = False

    def define(self, symbol: Symbol) -> bool:
        """Define a symbol in this scope.

        Returns True if the name was newly defined, False if it already
        existed in *this* scope (redeclaration).

        Note: OQ-01 (exact redeclaration rules) is unresolved. This method
        reports conflict within the same scope; the analyzer decides policy.
        """
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def resolve(self, name: str) -> Symbol | None:
        """Resolve a name by walking the parent chain (OQ-04 provisional)."""
        scope: Scope | None = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def resolve_local(self, name: str) -> Symbol | None:
        return self.symbols.get(name)

    def ancestors(self) -> Iterator[Scope]:
        scope: Scope | None = self
        while scope is not None:
            yield scope
            scope = scope.parent

    def in_function(self) -> bool:
        for s in self.ancestors():
            if s.is_function:
                return True
        return False
