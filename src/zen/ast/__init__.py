"""Public AST types and validation contracts for the Zen language."""

# ZIIF-01: Canonical AST Identity Fingerprint
from .fingerprint import (
    FINGERPRINT_PREFIX,
    FINGERPRINT_VERSION,
    ASTFingerprintError,
    fingerprint_ast,
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
from .source_span import SourcePosition, SourceSpan
from .validation import (
    ASTValidationLimits,
    ASTValidationResult,
    Diagnostic,
    DiagnosticSeverity,
    validate_ast,
)

__all__ = [
    "FINGERPRINT_PREFIX",
    "FINGERPRINT_VERSION",
    # ZIIF-01 exports
    "ASTFingerprintError",
    "ASTValidationLimits",
    "ASTValidationResult",
    "AssignExpr",
    "BinaryExpr",
    "BlockStmt",
    "CallExpr",
    "Diagnostic",
    "DiagnosticSeverity",
    "Expression",
    "ExpressionStmt",
    "FunctionDecl",
    "GroupingExpr",
    "IdentifierExpr",
    "IfStmt",
    "LiteralExpr",
    "Node",
    "Program",
    "ReturnStmt",
    "SourceIdentifier",
    "SourceLocation",
    "SourcePosition",
    "SourceSpan",
    "Statement",
    "UnaryExpr",
    "VarDecl",
    "WhileStmt",
    "fingerprint_ast",
    "validate_ast",
]
