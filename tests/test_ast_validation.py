import unittest

from zen.ast import (
    AssignExpr, BinaryExpr, BlockStmt, CallExpr, ExpressionStmt, IdentifierExpr,
    IfStmt, LiteralExpr, Program, SourceSpan,
)
from zen.ast.validation import (
    count_nodes, detect_cycles, detect_reused_nodes, measure_depth,
    require_child_span, require_ordered_children,
)


def sp(a, b):
    return SourceSpan(1, a, 1, b)


class AstStructuralValidationTests(unittest.TestCase):
    def test_child_span_outside_parent_is_rejected(self):
        parent = Program(sp(1, 4), ())
        child = ExpressionStmt(sp(4, 6), LiteralExpr(sp(4, 5), 1))
        with self.assertRaises(ValueError):
            require_child_span(parent, child, "child")
        with self.assertRaises(ValueError):
            Program(sp(1, 4), (child,))

    def test_adjacent_siblings_are_accepted(self):
        first = ExpressionStmt(sp(1, 2), LiteralExpr(sp(1, 2), 1))
        second = ExpressionStmt(sp(2, 3), LiteralExpr(sp(2, 3), 2))
        parent = Program(sp(1, 3), (first, second))
        require_ordered_children(parent, parent.statements, "statements")

    def test_overlapping_siblings_are_rejected(self):
        first = ExpressionStmt(sp(1, 3), LiteralExpr(sp(1, 2), 1))
        second = ExpressionStmt(sp(2, 4), LiteralExpr(sp(3, 4), 2))
        with self.assertRaises(ValueError):
            Program(sp(1, 4), (first, second))

    def test_out_of_order_statements_are_rejected(self):
        later = ExpressionStmt(sp(3, 4), LiteralExpr(sp(3, 4), 2))
        earlier = ExpressionStmt(sp(1, 2), LiteralExpr(sp(1, 2), 1))
        with self.assertRaises(ValueError):
            Program(sp(1, 4), (later, earlier))

    def test_wrong_child_type_is_rejected(self):
        with self.assertRaises(TypeError):
            Program(sp(1, 4), (LiteralExpr(sp(1, 2), 1),))

    def test_assignment_accepts_identifier_target(self):
        target = IdentifierExpr(sp(1, 2), "x")
        value = LiteralExpr(sp(3, 4), 9)
        assignment = AssignExpr(sp(1, 4), target, value)
        self.assertIs(assignment.target, target)

    def test_assignment_rejects_non_identifier_target(self):
        with self.assertRaises(TypeError):
            AssignExpr(sp(1, 4), LiteralExpr(sp(1, 2), 1), LiteralExpr(sp(3, 4), 2))

    def test_chained_call_is_representable(self):
        name = IdentifierExpr(sp(1, 8), "factory")
        inner = CallExpr(sp(1, 10), name, ())
        outer = CallExpr(sp(1, 12), inner, ())
        self.assertIs(outer.callee, inner)

    def test_else_if_chain_is_representable(self):
        condition1 = IdentifierExpr(sp(1, 2), "a")
        condition2 = IdentifierExpr(sp(4, 5), "b")
        then1 = BlockStmt(sp(3, 4), ())
        then2 = BlockStmt(sp(6, 7), ())
        inner = IfStmt(sp(4, 8), condition2, then2, None)
        outer = IfStmt(sp(1, 8), condition1, then1, inner)
        self.assertIs(outer.else_branch, inner)

    def test_direct_and_indirect_cycles_are_detected(self):
        direct = BlockStmt(sp(1, 3), ())
        object.__setattr__(direct, "statements", (direct,))
        with self.assertRaisesRegex(ValueError, "cycle"):
            detect_cycles(direct)

        first = BlockStmt(sp(1, 5), ())
        second = BlockStmt(sp(2, 4), ())
        object.__setattr__(first, "statements", (second,))
        object.__setattr__(second, "statements", (first,))
        with self.assertRaisesRegex(ValueError, "cycle"):
            detect_cycles(first)

    def test_reused_node_is_detected(self):
        shared = ExpressionStmt(sp(1, 2), LiteralExpr(sp(1, 2), 1))
        root = Program(sp(1, 3), (shared,))
        object.__setattr__(root, "statements", (shared, shared))
        with self.assertRaisesRegex(ValueError, "reuse"):
            detect_reused_nodes(root)

    def test_count_nodes_includes_root(self):
        expression = LiteralExpr(sp(1, 2), 1)
        statement = ExpressionStmt(sp(1, 2), expression)
        program = Program(sp(1, 2), (statement,))
        self.assertEqual(count_nodes(program), 3)

    def test_measure_depth_counts_root_as_one(self):
        expression = LiteralExpr(sp(1, 2), 1)
        statement = ExpressionStmt(sp(1, 2), expression)
        program = Program(sp(1, 2), (statement,))
        self.assertEqual(measure_depth(program), 3)

    def test_ast_does_not_apply_lexical_identifier_or_operator_rules(self):
        self.assertEqual(IdentifierExpr(sp(1, 2), "").name, "")
        left = LiteralExpr(sp(1, 2), 1)
        right = LiteralExpr(sp(3, 4), 2)
        self.assertEqual(BinaryExpr(sp(1, 4), left, "not-a-lexer-token", right).operator, "not-a-lexer-token")


if __name__ == "__main__":
    unittest.main()
