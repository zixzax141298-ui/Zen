"""Versioned canonical structural fingerprints for validated Zen ASTs.

The fingerprint deliberately excludes source identity and source coordinates.
Those values are validated before encoding, but are not part of structural
identity.
"""

from __future__ import annotations

import hashlib
import struct

from .nodes import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    ExpressionStmt,
    FunctionDecl,
    GroupingExpr,
    IdentifierExpr,
    IfStmt,
    LiteralExpr,
    Node,
    Program,
    ReturnStmt,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)
from .validation import validate_ast


FINGERPRINT_VERSION = 1
FINGERPRINT_PREFIX = "zen-ast-sha256-v1:"
_DOMAIN_SEPARATOR = b"ZEN-AST-STRUCTURAL-FINGERPRINT\x00"
_LENGTH_SIZE = 8


class ASTFingerprintError(ValueError):
    """Raised when an AST cannot be safely fingerprinted."""

    def __init__(
        self,
        message: str,
        *,
        diagnostic_codes: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.diagnostic_codes = diagnostic_codes


# This is a closed schema. Field order and tags are part of version 1.
# Do not replace this mapping with generic dataclass introspection.
_NODE_SCHEMAS = {
    Program: (
        "Program",
        ("statements",),
    ),
    VarDecl: (
        "VarDecl",
        ("name", "initializer", "is_const"),
    ),
    FunctionDecl: (
        "FunctionDecl",
        ("name", "parameters", "body"),
    ),
    BlockStmt: (
        "BlockStmt",
        ("statements",),
    ),
    IfStmt: (
        "IfStmt",
        ("condition", "then_branch", "else_branch"),
    ),
    WhileStmt: (
        "WhileStmt",
        ("condition", "body"),
    ),
    ReturnStmt: (
        "ReturnStmt",
        ("value",),
    ),
    ExpressionStmt: (
        "ExpressionStmt",
        ("expression",),
    ),
    LiteralExpr: (
        "LiteralExpr",
        ("value",),
    ),
    IdentifierExpr: (
        "IdentifierExpr",
        ("name",),
    ),
    UnaryExpr: (
        "UnaryExpr",
        ("operator", "operand"),
    ),
    BinaryExpr: (
        "BinaryExpr",
        ("left", "operator", "right"),
    ),
    GroupingExpr: (
        "GroupingExpr",
        ("expression",),
    ),
    AssignExpr: (
        "AssignExpr",
        ("target", "value"),
    ),
    CallExpr: (
        "CallExpr",
        ("callee", "arguments"),
    ),
}


def _write_length(digest, length: int) -> None:
    if length < 0 or length >= 1 << (_LENGTH_SIZE * 8):
        raise ASTFingerprintError("encoded value length is out of range")

    digest.update(length.to_bytes(_LENGTH_SIZE, "big"))


def _write_blob(digest, value: bytes) -> None:
    _write_length(digest, len(value))
    digest.update(value)


def _encode_integer(digest, value: int) -> None:
    """Encode arbitrary-size integers without decimal string conversion."""
    magnitude = abs(value)
    byte_length = max(1, (magnitude.bit_length() + 7) // 8)
    encoded = magnitude.to_bytes(byte_length, "big")

    digest.update(b"I")
    digest.update(b"\x01" if value < 0 else b"\x00")
    _write_blob(digest, encoded)


def _encode_string(digest, value: str) -> None:
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ASTFingerprintError(
            "AST string contains data that cannot be encoded as UTF-8"
        ) from exc

    digest.update(b"S")
    _write_blob(digest, encoded)


def _encode_value(digest, value, stack: list[tuple[str, object]]) -> None:
    """Encode one value or schedule its contents without recursion."""

    value_type = type(value)

    if value is None:
        digest.update(b"N")
        return

    # bool must be handled before int because bool subclasses int.
    if value_type is bool:
        digest.update(b"B1" if value else b"B0")
        return

    if value_type is int:
        _encode_integer(digest, value)
        return

    if value_type is float:
        digest.update(b"F")
        digest.update(struct.pack(">d", value))
        return

    if value_type is str:
        _encode_string(digest, value)
        return

    if value_type is tuple:
        digest.update(b"T")
        _write_length(digest, len(value))

        for item in reversed(value):
            stack.append(("value", item))

        return

    if isinstance(value, Node):
        schema = _NODE_SCHEMAS.get(value_type)

        if schema is None:
            raise ASTFingerprintError(
                "AST contains a node type outside the fingerprint schema"
            )

        node_tag, field_names = schema

        digest.update(b"D")
        _write_blob(digest, node_tag.encode("ascii"))
        digest.update(len(field_names).to_bytes(4, "big"))

        # Reverse-push so the stack emits fields in declared schema order.
        for field_name in reversed(field_names):
            stack.append(("value", getattr(value, field_name)))
            stack.append(("field", field_name))

        return

    raise ASTFingerprintError(
        "AST contains a value type outside the fingerprint schema"
    )


def fingerprint_ast(program: Program) -> str:
    """Return the version 1 SHA-256 structural fingerprint of a valid AST.

    Validation is mandatory and occurs before any structural encoding.
    SourceIdentifier and SourceSpan participate in validation but are
    intentionally excluded from the structural fingerprint.

    The encoder is iterative and does not use recursive AST traversal.
    """

    validation = validate_ast(program)

    if not validation.is_valid or not validation.complete:
        diagnostic_codes = tuple(
            diagnostic.code
            for diagnostic in validation.diagnostics
        )

        codes_text = (
            ", ".join(diagnostic_codes)
            if diagnostic_codes
            else "no diagnostic code available"
        )

        raise ASTFingerprintError(
            "AST validation failed; fingerprint generation refused: "
            + codes_text,
            diagnostic_codes=diagnostic_codes,
        )

    digest = hashlib.sha256()
    digest.update(_DOMAIN_SEPARATOR)
    digest.update(bytes((FINGERPRINT_VERSION,)))

    # Explicit operation stack: no recursive calls for nested AST nodes.
    stack: list[tuple[str, object]] = [("value", program)]

    while stack:
        operation, value = stack.pop()

        if operation == "field":
            digest.update(b"K")
            _write_blob(digest, str(value).encode("ascii"))
            continue

        _encode_value(digest, value, stack)

    return FINGERPRINT_PREFIX + digest.hexdigest()
