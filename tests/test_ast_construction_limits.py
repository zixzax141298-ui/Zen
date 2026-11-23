import unittest
from unittest.mock import patch

from zen.ast import (
    BlockStmt,
    CallExpr,
    FunctionDecl,
    IdentifierExpr,
    Program,
    SourceSpan,
)
from zen.ast.nodes import _tuple_of


def span():
    return SourceSpan(1, 1, 1, 2)


class ASTConstructionLimitTests(unittest.TestCase):

    def test_bounded_iterable_stops_after_first_excess_item(self):
        consumed = []

        def values():
            for value in range(100):
                consumed.append(value)
                yield value

        with self.assertRaises(ValueError):
            _tuple_of(
                values(),
                "items",
                child_collection=False,
                max_items=2,
            )

        self.assertEqual(consumed, [0, 1, 2])

    def test_exact_iterable_limit_is_accepted(self):
        result = _tuple_of(
            iter((1, 2)),
            "items",
            child_collection=False,
            max_items=2,
        )
        self.assertEqual(result, (1, 2))

    def test_program_rejects_generator_at_first_excess_item(self):
        consumed = []

        def statements():
            for value in range(3):
                consumed.append(value)
                yield object()

        with patch("zen.ast.nodes.MAX_DIRECT_CHILDREN", 2):
            with self.assertRaises(ValueError):
                Program(span(), statements())

        self.assertEqual(consumed, [0, 1, 2])

    def test_block_rejects_generator_at_first_excess_item(self):
        consumed = []

        def statements():
            for value in range(3):
                consumed.append(value)
                yield object()

        with patch("zen.ast.nodes.MAX_DIRECT_CHILDREN", 2):
            with self.assertRaises(ValueError):
                BlockStmt(span(), statements())

        self.assertEqual(consumed, [0, 1, 2])

    def test_function_parameters_are_bounded(self):
        consumed = []

        def parameters():
            for value in range(3):
                consumed.append(value)
                yield f"p{value}"

        body = BlockStmt(span(), ())

        with patch("zen.ast.nodes.MAX_DIRECT_CHILDREN", 2):
            with self.assertRaises(ValueError):
                FunctionDecl(span(), "f", parameters(), body)

        self.assertEqual(consumed, [0, 1, 2])

    def test_call_arguments_reserve_callee_slot(self):
        consumed = []

        def arguments():
            for value in range(2):
                consumed.append(value)
                yield object()

        callee = IdentifierExpr(span(), "f")

        with patch("zen.ast.nodes.MAX_DIRECT_CHILDREN", 2):
            with self.assertRaises(ValueError):
                CallExpr(span(), callee, arguments())

        self.assertEqual(consumed, [0, 1])


if __name__ == "__main__":
    unittest.main()
