import unittest
from dataclasses import FrozenInstanceError

from zen.ast import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    ExpressionStmt,
    IdentifierExpr,
    LiteralExpr,
    Program,
    SourceSpan,
    VarDecl,
)


def span(
    start_line=1,
    start_column=1,
    end_line=1,
    end_column=2,
):
    return SourceSpan(start_line, start_column, end_line, end_column)


class SourceSpanTests(unittest.TestCase):
    def test_accepts_valid_single_line_span(self):
        self.assertEqual(span(), SourceSpan(1, 1, 1, 2))

    def test_accepts_multiline_span(self):
        self.assertEqual(
            span(1, 3, 2, 1),
            SourceSpan(1, 3, 2, 1),
        )

    def test_accepts_empty_span(self):
        self.assertEqual(
            span(2, 4, 2, 4),
            SourceSpan(2, 4, 2, 4),
        )

    def test_rejects_zero_position(self):
        with self.assertRaises(ValueError):
            SourceSpan(0, 1, 1, 1)

    def test_rejects_end_before_start(self):
        with self.assertRaises(ValueError):
            SourceSpan(2, 1, 1, 5)

    def test_rejects_non_integer_position(self):
        with self.assertRaises(TypeError):
            SourceSpan(1, 1, 1, 2.5)

    def test_source_positions_compare_lexicographically(self):
        from zen.ast import SourcePosition
        self.assertLess(SourcePosition(1, 9), SourcePosition(2, 1))
        self.assertLess(SourcePosition(2, 1), SourcePosition(2, 2))

    def test_span_contains_half_open_child(self):
        parent = span(1, 1, 2, 1)
        child = span(1, 2, 2, 1)
        self.assertTrue(parent.contains(child))
        self.assertFalse(child.contains(parent))

    def test_span_is_immutable(self):
        location = span()
        with self.assertRaises(FrozenInstanceError):
            location.start_line = 3


class AstNodeTests(unittest.TestCase):
    def test_program_normalizes_statements_to_tuple(self):
        declaration = VarDecl(span(), "answer", None, False)
        program = Program(span(), [declaration])
        self.assertEqual(program.statements, (declaration,))
        self.assertIsInstance(program.statements, tuple)

    def test_ast_node_is_immutable(self):
        expression = LiteralExpr(span(), 42)
        with self.assertRaises(FrozenInstanceError):
            expression.value = 7

    def test_assignment_target_must_be_identifier(self):
        with self.assertRaises(TypeError):
            AssignExpr(span(), LiteralExpr(span(), 1), LiteralExpr(span(), 2))

    def test_call_arguments_are_immutable_tuple(self):
        callee = IdentifierExpr(span(1, 1, 1, 2), "sum")
        argument = LiteralExpr(span(1, 3, 1, 4), 1)
        call = CallExpr(span(1, 1, 1, 4), callee, [argument])
        self.assertEqual(call.arguments, (argument,))
        self.assertIsInstance(call.arguments, tuple)

    def test_binary_expression_rejects_invalid_operand(self):
        with self.assertRaises(TypeError):
            BinaryExpr(span(), "not-an-expression", "+", LiteralExpr(span(), 1))

    def test_block_rejects_expression_as_statement(self):
        with self.assertRaises(TypeError):
            BlockStmt(span(), [LiteralExpr(span(), 1)])

    def test_expression_statement_accepts_expression(self):
        expression = IdentifierExpr(span(), "answer")
        statement = ExpressionStmt(span(), expression)
        self.assertIs(statement.expression, expression)

    def test_literal_accepts_immutable_zen_values(self):
        for value in (None, True, False, 0, 42, 1.5, "zen"):
            with self.subTest(value=value):
                self.assertEqual(LiteralExpr(span(), value).value, value)

    def test_literal_rejects_mutable_values(self):
        for value in ([1, 2], {"answer": 42}, {1, 2}, bytearray(b"zen")):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    LiteralExpr(span(), value)

    def test_literal_rejects_arbitrary_python_objects(self):
        with self.assertRaises(TypeError):
            LiteralExpr(span(), object())

    def test_literal_rejects_non_finite_floats(self):
        for value in (float("inf"), float("-inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    LiteralExpr(span(), value)


if __name__ == "__main__":
    unittest.main()
