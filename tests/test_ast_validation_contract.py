import math
import unittest

from zen.ast import (
    ASTValidationLimits,
    BinaryExpr,
    BlockStmt,
    ExpressionStmt,
    FunctionDecl,
    LiteralExpr,
    Program,
    SourceIdentifier,
    SourceSpan,
    UnaryExpr,
    validate_ast,
)

from zen.parser import ParseContext, ParseError


def sp(start=1, end=10):
    return SourceSpan(1, start, 1, end)


def valid_program():
    source_id = SourceIdentifier.new()

    expression = BinaryExpr(
        sp(),
        LiteralExpr(sp(2, 3), 1, source_id=source_id),
        "+",
        LiteralExpr(sp(4, 5), 2, source_id=source_id),
        source_id=source_id,
    )

    statement = ExpressionStmt(
        sp(),
        expression,
        source_id=source_id,
    )

    return Program(
        sp(),
        (statement,),
        source_id=source_id,
    )


class AstValidationContractTests(unittest.TestCase):

    def codes(self, result):
        return {
            diagnostic.code
            for diagnostic in result.diagnostics
        }

    def test_valid_program_reports_deterministic_accounting(self):
        program = valid_program()

        first = validate_ast(program)

        self.assertTrue(first.is_valid)
        self.assertTrue(first.complete)

        self.assertEqual(first.nodes_visited, 5)
        self.assertEqual(first.expression_nodes, 3)
        self.assertEqual(first.statement_nodes, 1)
        self.assertEqual(first.max_depth, 4)

        self.assertEqual(first, validate_ast(program))

    def test_missing_and_mixed_source_identity_are_rejected(self):
        legacy = Program(
            sp(),
            (
                ExpressionStmt(
                    sp(),
                    LiteralExpr(sp(), 1),
                ),
            ),
        )

        self.assertIn(
            "AST_SOURCE_ID_MISSING",
            self.codes(validate_ast(legacy)),
        )

        program = valid_program()

        object.__setattr__(
            program.statements[0],
            "source_id",
            SourceIdentifier.new(),
        )

        self.assertIn(
            "AST_SOURCE_ID_MISMATCH",
            self.codes(validate_ast(program)),
        )

    def test_invalid_source_identity_type_is_rejected(self):
        program = valid_program()

        object.__setattr__(
            program,
            "source_id",
            "invalid",
        )

        self.assertIn(
            "AST_SOURCE_ID_INVALID",
            self.codes(validate_ast(program)),
        )

    def test_invalid_child_is_reported(self):
        program = valid_program()

        object.__setattr__(
            program,
            "statements",
            (object(),),
        )

        self.assertIn(
            "AST_CHILD_TYPE_INVALID",
            self.codes(validate_ast(program)),
        )

    def test_cycle_and_reused_node_are_reported(self):
        source_id = SourceIdentifier.new()

        cyclic = BlockStmt(
            sp(),
            (),
            source_id=source_id,
        )

        object.__setattr__(
            cyclic,
            "statements",
            (cyclic,),
        )

        root = Program(
            sp(),
            (cyclic,),
            source_id=source_id,
        )

        self.assertIn(
            "AST_NODE_CYCLE",
            self.codes(validate_ast(root)),
        )

        shared = ExpressionStmt(
            sp(2, 3),
            LiteralExpr(
                sp(2, 3),
                1,
                source_id=source_id,
            ),
            source_id=source_id,
        )

        reused = Program(
            sp(),
            (shared,),
            source_id=source_id,
        )

        object.__setattr__(
            reused,
            "statements",
            (shared, shared),
        )

        self.assertIn(
            "AST_NODE_REUSED",
            self.codes(validate_ast(reused)),
        )

    def test_non_finite_literal_corruption_is_reported(self):
        source_id = SourceIdentifier.new()

        literal = LiteralExpr(
            sp(2, 3),
            1,
            source_id=source_id,
        )

        object.__setattr__(
            literal,
            "value",
            math.inf,
        )

        statement = ExpressionStmt(
            sp(2, 3),
            literal,
            source_id=source_id,
        )

        program = Program(
            sp(),
            (statement,),
            source_id=source_id,
        )

        self.assertIn(
            "AST_FIELD_INVALID",
            self.codes(validate_ast(program)),
        )

    def test_source_order_is_revalidated(self):
        source_id = SourceIdentifier.new()

        first = ExpressionStmt(
            sp(4, 5),
            LiteralExpr(
                sp(4, 5),
                1,
                source_id=source_id,
            ),
            source_id=source_id,
        )

        second = ExpressionStmt(
            sp(2, 3),
            LiteralExpr(
                sp(2, 3),
                2,
                source_id=source_id,
            ),
            source_id=source_id,
        )

        program = Program(
            sp(),
            (first,),
            source_id=source_id,
        )

        object.__setattr__(
            program,
            "statements",
            (first, second),
        )

        self.assertIn(
            "AST_SOURCE_ORDER_INVALID",
            self.codes(validate_ast(program)),
        )

    def test_all_resource_dimensions_are_bounded(self):
        source_id = SourceIdentifier.new()

        first = ExpressionStmt(
            sp(2, 3),
            LiteralExpr(
                sp(2, 3),
                1,
                source_id=source_id,
            ),
            source_id=source_id,
        )

        second = ExpressionStmt(
            sp(4, 5),
            LiteralExpr(
                sp(4, 5),
                2,
                source_id=source_id,
            ),
            source_id=source_id,
        )

        program = Program(
            sp(),
            (first, second),
            source_id=source_id,
        )

        cases = (
            (
                ASTValidationLimits(max_nodes=2),
                "AST_NODE_LIMIT_EXCEEDED",
            ),
            (
                ASTValidationLimits(max_direct_children=1),
                "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
            ),
            (
                ASTValidationLimits(max_statement_nodes=1),
                "AST_STATEMENT_LIMIT_EXCEEDED",
            ),
            (
                ASTValidationLimits(max_expression_nodes=1),
                "AST_EXPRESSION_LIMIT_EXCEEDED",
            ),
            (
                ASTValidationLimits(max_depth=2),
                "AST_DEPTH_LIMIT_EXCEEDED",
            ),
        )

        for limits, expected_code in cases:
            with self.subTest(limit=expected_code):
                self.assertIn(
                    expected_code,
                    self.codes(validate_ast(program, limits)),
                )

    def test_function_metadata_is_required_for_canonical_validation(self):
        source_id = SourceIdentifier.new()
        body = BlockStmt(
            sp(5, 9),
            (),
            source_id=source_id,
        )
        function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4),),
        )
        program = Program(
            sp(1, 10),
            (function,),
            source_id=source_id,
        )

        self.assertTrue(validate_ast(program).is_valid)

        legacy_function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            body,
            source_id=source_id,
        )
        legacy_program = Program(
            sp(1, 10),
            (legacy_function,),
            source_id=source_id,
        )

        self.assertIn(
            "AST_FUNCTION_METADATA_MISSING",
            self.codes(validate_ast(legacy_program)),
        )

    def test_function_parameter_span_count_must_match_parameters(self):
        source_id = SourceIdentifier.new()
        body = BlockStmt(
            sp(7, 9),
            (),
            source_id=source_id,
        )
        function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x", "y"),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4),),
        )
        program = Program(
            sp(1, 10),
            (function,),
            source_id=source_id,
        )

        self.assertIn(
            "AST_FUNCTION_PARAMETER_SPAN_COUNT_MISMATCH",
            self.codes(validate_ast(program)),
        )

    def test_function_metadata_must_be_contained_and_ordered(self):
        source_id = SourceIdentifier.new()

        outside_body = BlockStmt(
            sp(8, 9),
            (),
            source_id=source_id,
        )
        outside_function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            outside_body,
            source_id=source_id,
            name_span=sp(10, 11),
            parameter_spans=(sp(3, 4),),
        )
        outside_program = Program(
            sp(1, 10),
            (outside_function,),
            source_id=source_id,
        )
        self.assertIn(
            "AST_FUNCTION_METADATA_OUT_OF_RANGE",
            self.codes(validate_ast(outside_program)),
        )

        ordered_body = BlockStmt(
            sp(8, 9),
            (),
            source_id=source_id,
        )
        overlapping_function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            ordered_body,
            source_id=source_id,
            name_span=sp(1, 4),
            parameter_spans=(sp(3, 5),),
        )
        overlapping_program = Program(
            sp(1, 10),
            (overlapping_function,),
            source_id=source_id,
        )
        self.assertIn(
            "AST_FUNCTION_METADATA_ORDER_INVALID",
            self.codes(validate_ast(overlapping_program)),
        )

    def test_function_metadata_corruption_is_rejected(self):
        source_id = SourceIdentifier.new()
        body = BlockStmt(
            sp(5, 9),
            (),
            source_id=source_id,
        )
        function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4),),
        )
        object.__setattr__(function, "parameter_spans", (object(),))
        program = Program(
            sp(1, 10),
            (function,),
            source_id=source_id,
        )

        self.assertIn(
            "AST_FUNCTION_PARAMETER_SPAN_INVALID",
            self.codes(validate_ast(program)),
        )

    def test_function_parameter_spans_respect_direct_child_limit(self):
        source_id = SourceIdentifier.new()
        body = BlockStmt(
            sp(5, 9),
            (),
            source_id=source_id,
        )
        function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4),),
        )
        object.__setattr__(
            function,
            "parameter_spans",
            (sp(3, 4), sp(4, 5)),
        )
        program = Program(
            sp(1, 10),
            (function,),
            source_id=source_id,
        )

        result = validate_ast(
            program,
            ASTValidationLimits(max_direct_children=1),
        )

        self.assertFalse(result.complete)
        self.assertIn(
            "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
            self.codes(result),
        )

    def test_corrupted_function_declaration_span_does_not_crash(self):
        source_id = SourceIdentifier.new()
        body = BlockStmt(
            sp(5, 9),
            (),
            source_id=source_id,
        )
        function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x",),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4),),
        )
        program = Program(
            sp(1, 10),
            (function,),
            source_id=source_id,
        )
        object.__setattr__(function, "span", object())

        result = validate_ast(program)

        self.assertFalse(result.complete)

    def test_parameter_limit_is_counted(self):
        source_id = SourceIdentifier.new()

        body = BlockStmt(
            sp(8, 9),
            (),
            source_id=source_id,
        )

        function = FunctionDecl(
            sp(),
            "f",
            ("a", "b"),
            body,
            source_id=source_id,
        )

        program = Program(
            sp(),
            (function,),
            source_id=source_id,
        )

        result = validate_ast(
            program,
            ASTValidationLimits(max_parameters=1),
        )

        self.assertIn(
            "AST_PARAMETER_LIMIT_EXCEEDED",
            self.codes(result),
        )

    def test_resource_limits_accept_exact_boundary_and_reject_limit_minus_one(self):
        source_id = SourceIdentifier.new()

        first = ExpressionStmt(
            sp(2, 3),
            LiteralExpr(
                sp(2, 3),
                1,
                source_id=source_id,
            ),
            source_id=source_id,
        )
        second = ExpressionStmt(
            sp(4, 5),
            LiteralExpr(
                sp(4, 5),
                2,
                source_id=source_id,
            ),
            source_id=source_id,
        )
        program = Program(
            sp(1, 6),
            (first, second),
            source_id=source_id,
        )

        # This tree has:
        # 5 total nodes, depth 3, 2 expressions, 2 statements,
        # and 2 direct children at the Program root.
        cases = (
            (
                "max_nodes",
                5,
                "AST_NODE_LIMIT_EXCEEDED",
            ),
            (
                "max_depth",
                3,
                "AST_DEPTH_LIMIT_EXCEEDED",
            ),
            (
                "max_expression_nodes",
                2,
                "AST_EXPRESSION_LIMIT_EXCEEDED",
            ),
            (
                "max_statement_nodes",
                2,
                "AST_STATEMENT_LIMIT_EXCEEDED",
            ),
            (
                "max_direct_children",
                2,
                "AST_DIRECT_CHILD_LIMIT_EXCEEDED",
            ),
        )

        for field, exact, diagnostic in cases:
            with self.subTest(resource=field, boundary="below"):
                limits = ASTValidationLimits(
                    **{field: exact - 1}
                )
                result = validate_ast(program, limits)
                self.assertIn(diagnostic, self.codes(result))

            with self.subTest(resource=field, boundary="exact"):
                limits = ASTValidationLimits(
                    **{field: exact}
                )
                result = validate_ast(program, limits)
                self.assertTrue(result.is_valid)
                self.assertTrue(result.complete)

            with self.subTest(resource=field, boundary="above"):
                limits = ASTValidationLimits(
                    **{field: exact + 1}
                )
                result = validate_ast(program, limits)
                self.assertTrue(result.is_valid)
                self.assertTrue(result.complete)

    def test_parameter_limit_accepts_exact_boundary_and_rejects_below(self):
        source_id = SourceIdentifier.new()

        body = BlockStmt(
            sp(8, 10),
            (),
            source_id=source_id,
        )
        function = FunctionDecl(
            sp(1, 11),
            "f",
            ("a", "b"),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4), sp(5, 6)),
        )
        program = Program(
            sp(1, 11),
            (function,),
            source_id=source_id,
        )

        below = validate_ast(
            program,
            ASTValidationLimits(max_parameters=1),
        )
        exact = validate_ast(
            program,
            ASTValidationLimits(max_parameters=2),
        )
        above = validate_ast(
            program,
            ASTValidationLimits(max_parameters=3),
        )

        self.assertIn(
            "AST_PARAMETER_LIMIT_EXCEEDED",
            self.codes(below),
        )
        self.assertTrue(exact.is_valid)
        self.assertTrue(exact.complete)
        self.assertTrue(above.is_valid)
        self.assertTrue(above.complete)

    def test_deep_validation_is_iterative_and_stops_at_limit(self):
        source_id = SourceIdentifier.new()

        expression = LiteralExpr(
            sp(),
            1,
            source_id=source_id,
        )

        for _ in range(400):
            expression = UnaryExpr(
                sp(),
                "!",
                expression,
                source_id=source_id,
            )

        statement = ExpressionStmt(
            sp(),
            expression,
            source_id=source_id,
        )

        program = Program(
            sp(),
            (statement,),
            source_id=source_id,
        )

        result = validate_ast(program)

        self.assertFalse(result.is_valid)

        self.assertIn(
            "AST_DEPTH_LIMIT_EXCEEDED",
            self.codes(result),
        )

        self.assertFalse(result.complete)

    def test_invalid_root_is_rejected(self):
        result = validate_ast(object())

        self.assertFalse(result.is_valid)
        self.assertFalse(result.complete)

        self.assertEqual(
            result.diagnostics[0].code,
            "AST_ROOT_TYPE_INVALID",
        )

    def test_parser_depth_and_common_diagnostic_preserve_compatibility(self):
        source_id = SourceIdentifier.new()

        context = ParseContext.initial(source_id)

        self.assertEqual(context.parser_depth, 0)

        for _ in range(256):
            context = context.enter(sp())

        with self.assertRaises(ParseError) as caught:
            context.enter(sp())

        diagnostic = caught.exception.as_diagnostic()

        self.assertEqual(diagnostic.component, "Parser")
        self.assertEqual(
            diagnostic.source_location.source_id,
            source_id,
        )
        self.assertEqual(diagnostic.code, "PARSER_ERROR")

        old_style = ParseError(
            "bad syntax",
            2,
            4,
            sp(),
        )

        self.assertEqual(
            str(old_style),
            "bad syntax at line 2, column 4",
        )

        self.assertIsNone(
            old_style.as_diagnostic().source_location
        )

    def test_parameter_count_boundary_below_exact_and_above(self):
        source_id = SourceIdentifier.new()

        body = BlockStmt(
            sp(6, 9),
            (),
            source_id=source_id,
        )

        function = FunctionDecl(
            sp(1, 10),
            "f",
            ("x", "y"),
            body,
            source_id=source_id,
            name_span=sp(1, 2),
            parameter_spans=(sp(3, 4), sp(4, 5)),
        )

        program = Program(
            sp(1, 10),
            (function,),
            source_id=source_id,
        )

        below = validate_ast(
            program,
            ASTValidationLimits(max_parameters=3),
        )
        exact = validate_ast(
            program,
            ASTValidationLimits(max_parameters=2),
        )
        above = validate_ast(
            program,
            ASTValidationLimits(max_parameters=1),
        )

        self.assertTrue(below.is_valid)
        self.assertTrue(exact.is_valid)
        self.assertEqual(below.parameter_count, 2)
        self.assertEqual(exact.parameter_count, 2)

        self.assertFalse(above.is_valid)
        self.assertFalse(above.complete)
        self.assertEqual(above.parameter_count, 2)
        self.assertIn(
            "AST_PARAMETER_LIMIT_EXCEEDED",
            self.codes(above),
        )

if __name__ == "__main__":
    unittest.main()
