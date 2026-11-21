import unittest

from zen.ast import CallExpr, IdentifierExpr, LiteralExpr, SourceSpan
from zen.ast.traversal import iter_child_nodes


def sp(a, b):
    return SourceSpan(1, a, 1, b)


class AstTraversalTests(unittest.TestCase):
    def test_children_are_yielded_deterministically(self):
        callee = IdentifierExpr(sp(1, 2), "f")
        first = LiteralExpr(sp(3, 4), 1)
        second = LiteralExpr(sp(5, 6), 2)
        call = CallExpr(sp(1, 7), callee, (first, second))
        self.assertEqual(tuple(iter_child_nodes(call)), (callee, first, second))
        self.assertEqual(tuple(iter_child_nodes(call)), (callee, first, second))

    def test_none_and_non_node_fields_are_not_yielded(self):
        callee = IdentifierExpr(sp(1, 2), "f")
        call = CallExpr(sp(1, 4), callee, ())
        children = tuple(iter_child_nodes(call))
        self.assertEqual(children, (callee,))
        self.assertTrue(all(child is not None for child in children))

    def test_non_node_input_is_rejected(self):
        with self.assertRaises(TypeError):
            tuple(iter_child_nodes(object()))


if __name__ == "__main__":
    unittest.main()
