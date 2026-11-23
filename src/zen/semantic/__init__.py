"""Zen semantic analysis package.

Performs meaning-related checks on a structurally validated AST.
Does not re-parse source or mutate the canonical AST.
"""

from .analyzer import SemanticAnalyzer, analyze
from .diagnostics import SemanticError, SemanticDiagnostic
from .scope import Scope, Symbol, SymbolKind

__all__ = [
    "SemanticAnalyzer",
    "analyze",
    "SemanticError",
    "SemanticDiagnostic",
    "Scope",
    "Symbol",
    "SymbolKind",
]
