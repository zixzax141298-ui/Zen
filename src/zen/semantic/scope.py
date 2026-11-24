"""Lexical scope and symbol table for semantic analysis."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum, auto

from zen.ast.source_span import SourceSpan


class SymbolKind(Enum):
    VARIABLE = auto()
    CONSTANT = auto()
    FUNCTION = auto()
    PARAMETER = auto()


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    span: SourceSpan | None = None
    initialized: bool = False
    arity: int | None = None


@dataclass
class Scope:
    parent: Scope | None = None
    is_function: bool = False
    symbols: dict[str, Symbol] = field(default_factory=dict)

    def define(self, symbol: Symbol) -> bool:
        """Define a symbol in this scope. Returns False if already defined."""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def resolve_local(self, name: str) -> Symbol | None:
        return self.symbols.get(name)

    def resolve(self, name: str) -> Symbol | None:
        scope: Scope | None = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None

    def in_function(self) -> bool:
        scope: Scope | None = self
        while scope is not None:
            if scope.is_function:
                return True
            scope = scope.parent
        return False

    def __iter__(self) -> Iterator[Symbol]:
        return iter(self.symbols.values())
