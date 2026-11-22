import unittest

from zen.ast import ExpressionStmt, LiteralExpr, Program, SourceSpan
from zen.limits import MAX_AST_DEPTH, MAX_AST_NODES, MAX_DIRECT_CHILDREN, MAX_PARSER_DEPTH
from zen.parser import ParseContext, ParseError


def span():
    return SourceSpan(1, 1, 1, 2)


class AstLimitsTests(unittest.TestCase):
    def test_program_below_node_limit_can_be_created(self):
        node = LiteralExpr(span(), 1)
        statement = ExpressionStmt(span(), node)
        program = Program(span(), (statement,))
        self.assertEqual(program.statements, (statement,))
        self.assertIs(program.statements[0].expression, node)

    def test_direct_child_collection_limit_is_enforced(self):
        statement = ExpressionStmt(span(), LiteralExpr(span(), 1))
        with self.assertRaisesRegex(ValueError, "MAX_DIRECT_CHILDREN"):
            Program(span(), (statement,) * (MAX_DIRECT_CHILDREN + 1))

    def test_parser_context_rejects_node_limit_plus_one_with_location(self):
        context = ParseContext(depth=0, node_count=MAX_AST_NODES)
        with self.assertRaises(ParseError) as caught:
            context.track_node(span())
        self.assertEqual((caught.exception.line, caught.exception.column), (1, 1))
        self.assertEqual(caught.exception.span, span())

    def test_parser_context_rejects_depth_limit_plus_one_with_location(self):
        context = ParseContext(depth=MAX_AST_DEPTH, node_count=0)
        with self.assertRaises(ParseError) as caught:
            context.enter(span())
        self.assertEqual((caught.exception.line, caught.exception.column), (1, 1))
        self.assertEqual(caught.exception.span, span())

    def test_parser_depth_boundary_minus_one_exact_and_plus_one(self):
        below = ParseContext(depth=MAX_PARSER_DEPTH - 1, node_count=0)
        exact = below.enter(span())

        self.assertEqual(exact.parser_depth, MAX_PARSER_DEPTH)

        with self.assertRaises(ParseError):
            exact.enter(span())

    def test_parser_node_count_boundary_minus_one_exact_and_plus_one(self):
        below = ParseContext(
            depth=0,
            node_count=MAX_AST_NODES - 1,
        )
        exact = below.track_node(span())

        self.assertEqual(exact.node_count, MAX_AST_NODES)

        with self.assertRaises(ParseError):
            exact.track_node(span())

    def test_context_initial_and_increment_operations_are_immutable(self):
        initial = ParseContext.initial()
        self.assertEqual((initial.depth, initial.node_count), (0, 0))
        self.assertEqual(initial.enter().depth, 1)
        self.assertEqual(initial.track_node().node_count, 1)
        self.assertEqual((initial.depth, initial.node_count), (0, 0))
