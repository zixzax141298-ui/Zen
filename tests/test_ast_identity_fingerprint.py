
import re
import unittest
from unittest.mock import patch

from zen.ast.fingerprint import _NODE_SCHEMAS
from zen.ast.validation import ASTValidationResult

from zen.ast import (
    ASTFingerprintError,
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
    Program,
    ReturnStmt,
    SourceIdentifier,
    SourceSpan,
    UnaryExpr,
    VarDecl,
    WhileStmt,
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

    def test_primitive_types_have_pairwise_distinct_encodings(self):
        values = (None, False, 0, 0.0, "")

        fingerprints = [
            fingerprint_ast(make_program(value))
            for value in values
        ]

        self.assertEqual(
            len(fingerprints),
            len(set(fingerprints)),
            "Distinct primitive types must have distinct encodings",
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

    def test_domain_separator_and_version_byte_are_included(self):
        class RecordingDigest:
            def __init__(self):
                self.chunks = []

            def update(self, chunk):
                self.chunks.append(chunk)

            def hexdigest(self):
                return "0" * 64

        digest = RecordingDigest()

        with patch(
            "zen.ast.fingerprint.hashlib.sha256",
            return_value=digest,
        ):
            fingerprint_ast(make_program(42))

        self.assertEqual(
            digest.chunks[:2],
            [
                b"ZEN-AST-STRUCTURAL-FINGERPRINT\x00",
                b"\x01",
            ],
        )

    def test_tuple_order_changes_fingerprint(self):
        source_id = SourceIdentifier("tuple-order")
        parent_span = SourceSpan(1, 1, 1, 20)
        callee_span = SourceSpan(1, 2, 1, 3)
        first_arg_span = SourceSpan(1, 4, 1, 5)
        second_arg_span = SourceSpan(1, 6, 1, 7)

        def make_call(first_value, second_value):
            callee = IdentifierExpr(
                callee_span, "f", source_id=source_id
            )
            first = LiteralExpr(
                first_arg_span, first_value, source_id=source_id
            )
            second = LiteralExpr(
                second_arg_span, second_value, source_id=source_id
            )
            call = CallExpr(
                parent_span,
                callee,
                (first, second),
                source_id=source_id,
            )
            statement = ExpressionStmt(
                parent_span, call, source_id=source_id
            )
            return Program(
                parent_span, (statement,), source_id=source_id
            )

        self.assertNotEqual(
            fingerprint_ast(make_call(1, 2)),
            fingerprint_ast(make_call(2, 1)),
        )

    def test_optional_none_field_has_distinct_encoding(self):
        source_id = SourceIdentifier("optional-none")
        span = SourceSpan(1, 1, 1, 20)

        absent = Program(
            span,
            (
                VarDecl(
                    span,
                    "value",
                    None,
                    False,
                    source_id=source_id,
                ),
            ),
            source_id=source_id,
        )

        present = Program(
            span,
            (
                VarDecl(
                    span,
                    "value",
                    LiteralExpr(span, None, source_id=source_id),
                    False,
                    source_id=source_id,
                ),
            ),
            source_id=source_id,
        )

        self.assertNotEqual(
            fingerprint_ast(absent),
            fingerprint_ast(present),
        )

    def test_all_fifteen_node_schemas_and_field_orders_are_declared(self):
        expected = {
            Program: ("Program", ("statements",)),
            VarDecl: ("VarDecl", ("name", "initializer", "is_const")),
            FunctionDecl: (
                "FunctionDecl",
                ("name", "parameters", "body"),
            ),
            BlockStmt: ("BlockStmt", ("statements",)),
            IfStmt: (
                "IfStmt",
                ("condition", "then_branch", "else_branch"),
            ),
            WhileStmt: ("WhileStmt", ("condition", "body")),
            ReturnStmt: ("ReturnStmt", ("value",)),
            ExpressionStmt: ("ExpressionStmt", ("expression",)),
            LiteralExpr: ("LiteralExpr", ("value",)),
            IdentifierExpr: ("IdentifierExpr", ("name",)),
            UnaryExpr: ("UnaryExpr", ("operator", "operand")),
            BinaryExpr: (
                "BinaryExpr",
                ("left", "operator", "right"),
            ),
            GroupingExpr: ("GroupingExpr", ("expression",)),
            AssignExpr: ("AssignExpr", ("target", "value")),
            CallExpr: ("CallExpr", ("callee", "arguments")),
        }

        self.assertEqual(_NODE_SCHEMAS, expected)
        self.assertEqual(len(_NODE_SCHEMAS), 15)

    def test_none_value_uses_explicit_none_marker(self):
        class RecordingDigest:
            def __init__(self):
                self.chunks = []

            def update(self, chunk):
                self.chunks.append(chunk)

            def hexdigest(self):
                return "0" * 64

        source_id = SourceIdentifier("none-marker")
        span = SourceSpan(1, 1, 1, 20)

        program = Program(
            span,
            (
                ReturnStmt(
                    span,
                    None,
                    source_id=source_id,
                ),
            ),
            source_id=source_id,
        )

        digest = RecordingDigest()

        with patch(
            "zen.ast.fingerprint.hashlib.sha256",
            return_value=digest,
        ):
            fingerprint_ast(program)

        self.assertIn(b"N", digest.chunks)

    def test_function_without_required_metadata_is_rejected(self):
        source_id = SourceIdentifier("missing-function-metadata")
        span = SourceSpan(1, 1, 1, 20)

        body = BlockStmt(span, (), source_id=source_id)
        function = FunctionDecl(
            span,
            "f",
            (),
            body,
            source_id=source_id,
        )
        program = Program(
            span,
            (function,),
            source_id=source_id,
        )

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_FUNCTION_METADATA_MISSING",
            context.exception.diagnostic_codes,
        )

    def test_invalid_child_type_is_rejected(self):
        source_id = SourceIdentifier("invalid-child")
        span = SourceSpan(1, 1, 1, 20)

        literal = LiteralExpr(span, 42, source_id=source_id)
        statement = ExpressionStmt(
            span, literal, source_id=source_id
        )
        program = Program(
            span, (statement,), source_id=source_id
        )

        object.__setattr__(statement, "expression", object())

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_CHILD_TYPE_INVALID",
            context.exception.diagnostic_codes,
        )

    def test_runtime_encoding_covers_all_fifteen_canonical_node_types(self):
        source_id = SourceIdentifier("runtime-node-coverage")

        def span(start, end):
            return SourceSpan(1, start, 1, end)

        root_span = span(1, 100)
        node_span = span(2, 99)

        literal = LiteralExpr(
            span(10, 15), 7, source_id=source_id
        )
        identifier = IdentifierExpr(
            span(10, 15), "value", source_id=source_id
        )

        empty_block = BlockStmt(
            span(20, 90), (), source_id=source_id
        )

        function_body = BlockStmt(
            span(30, 90), (), source_id=source_id
        )
        function = FunctionDecl(
            node_span,
            "compute",
            ("x",),
            function_body,
            source_id=source_id,
            name_span=span(5, 12),
            parameter_spans=(span(15, 16),),
        )

        call = CallExpr(
            node_span,
            IdentifierExpr(
                span(5, 10), "compute", source_id=source_id
            ),
            (
                LiteralExpr(
                    span(15, 20), 1, source_id=source_id
                ),
                LiteralExpr(
                    span(25, 30), 2, source_id=source_id
                ),
            ),
            source_id=source_id,
        )

        nodes = {
            "Program": Program(
                root_span, (), source_id=source_id
            ),
            "VarDecl": VarDecl(
                node_span, "value", literal, False,
                source_id=source_id,
            ),
            "FunctionDecl": function,
            "BlockStmt": empty_block,
            "IfStmt": IfStmt(
                node_span,
                IdentifierExpr(
                    span(5, 10), "condition", source_id=source_id
                ),
                BlockStmt(
                    span(20, 40), (), source_id=source_id
                ),
                BlockStmt(
                    span(50, 80), (), source_id=source_id
                ),
                source_id=source_id,
            ),
            "WhileStmt": WhileStmt(
                node_span,
                IdentifierExpr(
                    span(5, 10), "condition", source_id=source_id
                ),
                BlockStmt(
                    span(20, 90), (), source_id=source_id
                ),
                source_id=source_id,
            ),
            "ReturnStmt": ReturnStmt(
                node_span, literal, source_id=source_id
            ),
            "ExpressionStmt": ExpressionStmt(
                node_span, literal, source_id=source_id
            ),
            "LiteralExpr": literal,
            "IdentifierExpr": identifier,
            "UnaryExpr": UnaryExpr(
                node_span, "-", literal, source_id=source_id
            ),
            "BinaryExpr": BinaryExpr(
                node_span,
                literal,
                "+",
                LiteralExpr(
                    span(30, 40), 8, source_id=source_id
                ),
                source_id=source_id,
            ),
            "GroupingExpr": GroupingExpr(
                node_span, literal, source_id=source_id
            ),
            "AssignExpr": AssignExpr(
                node_span,
                IdentifierExpr(
                    span(5, 10), "target", source_id=source_id
                ),
                LiteralExpr(
                    span(20, 25), 9, source_id=source_id
                ),
                source_id=source_id,
            ),
            "CallExpr": call,
        }

        self.assertEqual(len(nodes), 15)

        statement_types = (
            VarDecl,
            FunctionDecl,
            BlockStmt,
            IfStmt,
            WhileStmt,
            ReturnStmt,
            ExpressionStmt,
        )

        for node_name, node in nodes.items():
            with self.subTest(node_type=node_name):
                if isinstance(node, Program):
                    program = node
                else:
                    statement = (
                        node
                        if isinstance(node, statement_types)
                        else ExpressionStmt(
                            node_span,
                            node,
                            source_id=source_id,
                        )
                    )
                    program = Program(
                        root_span,
                        (statement,),
                        source_id=source_id,
                    )

                fingerprint = fingerprint_ast(program)
                self.assertRegex(
                    fingerprint,
                    r"^zen-ast-sha256-v1:[0-9a-f]{64}$",
                )



    def test_invalid_root_type_is_rejected(self):
        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(object())

        self.assertIn(
            "AST_ROOT_TYPE_INVALID",
            context.exception.diagnostic_codes,
        )

    def test_invalid_source_identity_type_is_rejected(self):
        program = make_program(42)
        object.__setattr__(program, "source_id", object())

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_SOURCE_ID_INVALID",
            context.exception.diagnostic_codes,
        )

    def test_malformed_source_span_is_rejected(self):
        program = make_program(42)
        literal = program.statements[0].expression
        object.__setattr__(literal, "span", object())

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_SPAN_INVALID",
            context.exception.diagnostic_codes,
        )

    def test_ast_cycle_is_rejected(self):
        source_id = SourceIdentifier("cycle-test")
        span = SourceSpan(1, 1, 1, 20)

        literal = LiteralExpr(span, 42, source_id=source_id)
        expression = UnaryExpr(
            span, "!", literal, source_id=source_id
        )
        statement = ExpressionStmt(
            span, expression, source_id=source_id
        )
        program = Program(
            span, (statement,), source_id=source_id
        )

        object.__setattr__(expression, "operand", expression)

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_NODE_CYCLE",
            context.exception.diagnostic_codes,
        )

    def test_reused_ast_node_is_rejected(self):
        source_id = SourceIdentifier("reused-node-test")
        span = SourceSpan(1, 1, 1, 20)

        statement = ReturnStmt(
            span, None, source_id=source_id
        )
        program = Program(
            span, (), source_id=source_id
        )

        object.__setattr__(
            program,
            "statements",
            (statement, statement),
        )

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_NODE_REUSED",
            context.exception.diagnostic_codes,
        )

    def test_unsupported_node_subclass_is_rejected(self):
        class UnsupportedLiteral(LiteralExpr):
            pass

        source_id = SourceIdentifier("unsupported-node-test")
        span = SourceSpan(1, 1, 1, 20)

        literal = UnsupportedLiteral(
            span, 42, source_id=source_id
        )
        statement = ExpressionStmt(
            span, literal, source_id=source_id
        )
        program = Program(
            span, (statement,), source_id=source_id
        )

        with self.assertRaises(ASTFingerprintError) as context:
            fingerprint_ast(program)

        self.assertIn(
            "AST_NODE_TYPE_INVALID",
            context.exception.diagnostic_codes,
        )

    def test_incomplete_validation_is_rejected_even_when_valid(self):
        incomplete_result = ASTValidationResult(
            True,
            (),
            0,
            0,
            0,
            0,
            0,
            False,
        )

        with patch(
            "zen.ast.fingerprint.validate_ast",
            return_value=incomplete_result,
        ):
            with self.assertRaises(ASTFingerprintError):
                fingerprint_ast(make_program(42))

if __name__ == "__main__":
    unittest.main()
