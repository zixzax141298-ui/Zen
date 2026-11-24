"""Zen semantic analysis package.

Performs meaning-related checks on a structurally validated AST.
Does not re-parse source or mutate the canonical AST.
"""

from .analyzer import SemanticAnalyzer, analyze
from .diagnostics import SemanticDiagnostic, SemanticError
from .scope import Scope, Symbol, SymbolKind

__all__ = [
    "Scope",
    "SemanticAnalyzer",
    "SemanticDiagnostic",
    "SemanticError",
    "Symbol",
    "SymbolKind",
    "analyze",
]
