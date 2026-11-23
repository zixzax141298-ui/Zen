import re
import unittest

from zen.ast import (
    ASTFingerprintError,
    BlockStmt,
    ExpressionStmt,
    FunctionDecl,
    LiteralExpr,
    Program,
    SourceIdentifier,
    SourceSpan,
    fingerprint_ast,
)


def make_program(
    value,
    *,
    source_id=None,
    span=None,
):
    if source_id is None:
        source_id = SourceIdentifier("fingerprint-test-source")

    if span is None:
        span = SourceSpan(1, 1, 1, 20)

    literal = LiteralExpr(
        span,
        value,
        source_id=source_id,
    )
    statement = ExpressionStmt(
        span,
        literal,
        source_id=source_id,
    )
    return Program(
        span,
        (statement,),
        source_id=source_id,
    )


class ASTIdentityFingerprintTests(unittest.TestCase):
    def test_fingerprint_has_versioned_sha256_format(self):
        result = fingerprint_ast(make_program(42))

        self.assertRegex(
            result,
            re.compile(r"^zen-ast-sha256-v1:[0-9a-f]{64}$"),
        )

    def test_fingerprint_is_deterministic(self):
        first = make_program(42)
        second = make_program(42)

        self.assertEqual(
            fingerprint_ast(first),
            fingerprint_ast(second),
        )

    def test_source_identity_is_excluded_from_structure(self):
        first = make_program(
            42,
            source_id=SourceIdentifier("source-one"),
        )
        second = make_program(
            42,
            source_id=SourceIdentifier("source-two"),
        )

        self.assertEqual(
            fingerprint_ast(first),
            fingerprint_ast(second),
        )

    def test_source_spans_are_excluded_from_structure(self):
        first = make_program(
            42,
            span=SourceSpan(1, 1, 1, 20),
        )
        second = make_program(
            42,
            span=SourceSpan(5, 2, 8, 30),
        )

        self.assertEqual(
            fingerprint_ast(first),
            fingerprint_ast(second),
        )

    def test_different_literal_values_change_fingerprint(self):
        self.assertNotEqual(
            fingerprint_ast(make_program(42)),
            fingerprint_ast(make_program(43)),
        )

    def test_boolean_and_integer_have_distinct_encodings(self):
        self.assertNotEqual(
            fingerprint_ast(make_program(True)),
            fingerprint_ast(make_program(1)),
        )

    def test_positive_and_negative_zero_have_distinct_encodings(self):
        self.assertNotEqual(
            fingerprint_ast(make_program(0.0)),
            fingerprint_ast(make_program(-0.0)),
        )

    def test_large_integer_does_not_require_decimal_conversion(self):
        value = 1 << 10000

        result = fingerprint_ast(make_program(value))

        self.assertRegex(
            result,
            re.compile(r"^zen-ast-sha256-v1:[0-9a-f]{64}$"),
        )

    def test_missing_source_identity_is_rejected(self):
        span = SourceSpan(1, 1, 1, 20)
        literal = LiteralExpr(span, 42)
        statement = ExpressionStmt(span, literal)
        program = Program(span, (statement,))

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_SOURCE_ID_MISSING",
            context.exception.diagnostic_codes,
        )

    def test_mismatched_source_identity_is_rejected(self):
        span = SourceSpan(1, 1, 1, 20)
        root_id = SourceIdentifier("root-source")
        child_id = SourceIdentifier("different-source")

        literal = LiteralExpr(
            span,
            42,
            source_id=child_id,
        )
        statement = ExpressionStmt(
            span,
            literal,
            source_id=child_id,
        )
        program = Program(
            span,
            (statement,),
            source_id=root_id,
        )

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_SOURCE_ID_MISMATCH",
            context.exception.diagnostic_codes,
        )

    def test_nested_expression_encoding_is_iterative(self):
        source_id = SourceIdentifier("deep-expression")
        span = SourceSpan(1, 1, 1, 20)

        expression = LiteralExpr(
            span,
            7,
            source_id=source_id,
        )

        # Keep below the existing AST validation depth ceiling.
        from zen.ast import UnaryExpr

        for _ in range(80):
            expression = UnaryExpr(
                span,
                "!",
                expression,
                source_id=source_id,
            )

        statement = ExpressionStmt(
            span,
            expression,
            source_id=source_id,
        )
        program = Program(
            span,
            (statement,),
            source_id=source_id,
        )

        result = fingerprint_ast(program)

        self.assertRegex(
            result,
            re.compile(r"^zen-ast-sha256-v1:[0-9a-f]{64}$"),
        )



    def test_function_source_metadata_is_excluded_from_v1_fingerprint(self):
        source_id = SourceIdentifier("function-metadata-fingerprint")
        declaration_span = SourceSpan(1, 1, 1, 20)
        body_span = SourceSpan(1, 10, 1, 15)

        def make_function(name_span, parameter_span):
            body = BlockStmt(
                body_span,
                (),
                source_id=source_id,
            )
            function = FunctionDecl(
                declaration_span,
                "f",
                ("x",),
                body,
                source_id=source_id,
                name_span=name_span,
                parameter_spans=(parameter_span,),
            )
            return Program(
                declaration_span,
                (function,),
                source_id=source_id,
            )

        first = make_function(
            SourceSpan(1, 1, 1, 2),
            SourceSpan(1, 3, 1, 4),
        )
        second = make_function(
            SourceSpan(1, 2, 1, 3),
            SourceSpan(1, 5, 1, 6),
        )

        self.assertEqual(
            fingerprint_ast(first),
            fingerprint_ast(second),
        )

if __name__ == "__main__":
    unittest.main()
