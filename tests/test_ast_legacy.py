import unittest

from zen.ast import (
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
    validate_ast,
)

from zen.ast.legacy import adapt_legacy_ast
from zen.ast.traversal import iter_child_nodes


def sp(start=1, end=10):
    return SourceSpan(1, start, 1, end)


def legacy_program():
    expression = BinaryExpr(
        sp(),
        LiteralExpr(sp(2, 3), 1),
        "+",
        LiteralExpr(sp(4, 5), 2),
    )

    statement = ExpressionStmt(sp(), expression)

    return Program(sp(), (statement,))


class LegacyAstAdapterTests(unittest.TestCase):

    def test_adapter_clones_tree_and_preserves_original(self):
        original = legacy_program()
        source_id = SourceIdentifier.new()

        adapted = adapt_legacy_ast(original, source_id)

        self.assertIsNot(adapted, original)
        self.assertEqual(adapted.source_id, source_id)

        self.assertEqual(
            adapted.statements[0].source_id,
            source_id,
        )

        self.assertEqual(
            adapted.statements[0].expression.source_id,
            source_id,
        )

        self.assertIsNone(original.source_id)
        self.assertIsNone(original.statements[0].source_id)

        self.assertTrue(validate_ast(adapted).is_valid)

    def test_adapter_requires_explicit_source_identifier(self):
        with self.assertRaises(TypeError):
            adapt_legacy_ast(
                legacy_program(),
                "not-an-id",
            )

    def test_adapter_refuses_to_overwrite_existing_identity(self):
        source_id = SourceIdentifier.new()

        program = Program(
            sp(),
            (),
            source_id=source_id,
        )

        with self.assertRaisesRegex(ValueError, "overwrite"):
            adapt_legacy_ast(
                program,
                SourceIdentifier.new(),
            )

    def test_adapter_handles_every_canonical_node_shape(self):
        statements = (
            VarDecl(
                sp(1, 10),
                "v",
                LiteralExpr(sp(5, 6), 1),
                False,
            ),

            FunctionDecl(
                sp(11, 20),
                "f",
                ("x",),
                BlockStmt(
                    sp(15, 19),
                    (
                        ReturnStmt(
                            sp(16, 18),
                            LiteralExpr(sp(17, 18), 2),
                        ),
                    ),
                ),
            ),

            IfStmt(
                sp(21, 40),
                IdentifierExpr(sp(22, 23), "c"),
                BlockStmt(sp(24, 30), ()),
                BlockStmt(sp(31, 39), ()),
            ),

            WhileStmt(
                sp(41, 50),
                IdentifierExpr(sp(42, 43), "w"),
                BlockStmt(sp(44, 49), ()),
            ),

            ReturnStmt(sp(51, 55), None),

            ExpressionStmt(
                sp(56, 64),
                CallExpr(
                    sp(57, 63),
                    IdentifierExpr(sp(57, 59), "f"),
                    (LiteralExpr(sp(61, 62), 3),),
                ),
            ),

            ExpressionStmt(
                sp(65, 70),
                UnaryExpr(
                    sp(65, 70),
                    "!",
                    IdentifierExpr(sp(67, 68), "x"),
                ),
            ),

            ExpressionStmt(
                sp(71, 77),
                GroupingExpr(
                    sp(71, 77),
                    LiteralExpr(sp(73, 74), 4),
                ),
            ),

            ExpressionStmt(
                sp(78, 85),
                AssignExpr(
                    sp(78, 85),
                    IdentifierExpr(sp(79, 80), "x"),
                    LiteralExpr(sp(82, 83), 5),
                ),
            ),

            ExpressionStmt(
                sp(86, 95),
                BinaryExpr(
                    sp(86, 95),
                    LiteralExpr(sp(87, 88), 6),
                    "+",
                    LiteralExpr(sp(90, 91), 7),
                ),
            ),
        )

        original = Program(sp(1, 100), statements)
        source_id = SourceIdentifier.new()

        adapted = adapt_legacy_ast(original, source_id)

        self.assertTrue(validate_ast(adapted).is_valid)
        self.assertEqual(adapted.source_id, source_id)

        stack = [adapted]

        while stack:
            node = stack.pop()

            self.assertEqual(node.source_id, source_id)

            stack.extend(iter_child_nodes(node))

    def test_adapter_rejects_cycles_and_reused_nodes(self):
        cyclic_block = BlockStmt(sp(), ())

        object.__setattr__(
            cyclic_block,
            "statements",
            (cyclic_block,),
        )

        cyclic = Program(sp(), (cyclic_block,))

        with self.assertRaisesRegex(ValueError, "cycle"):
            adapt_legacy_ast(
                cyclic,
                SourceIdentifier.new(),
            )

        shared = ExpressionStmt(
            sp(2, 3),
            LiteralExpr(sp(2, 3), 1),
        )

        reused = Program(sp(), (shared,))

        object.__setattr__(
            reused,
            "statements",
            (shared, shared),
        )

        with self.assertRaises(ValueError):
            adapt_legacy_ast(
                reused,
                SourceIdentifier.new(),
            )


if __name__ == "__main__":
    unittest.main()
