"""Non-gating local timing and memory observation for iterative validation."""

import time
import tracemalloc
import unittest

from zen.ast import (
    ExpressionStmt,
    LiteralExpr,
    Program,
    SourceIdentifier,
    SourceSpan,
    validate_ast,
)


class AstValidationMeasurementTests(unittest.TestCase):

    def test_validation_measurement_wide_program(self):
        count = 1000
        source_id = SourceIdentifier.new()

        statements = tuple(
            ExpressionStmt(
                SourceSpan(
                    1,
                    index * 2 + 1,
                    1,
                    index * 2 + 2,
                ),
                LiteralExpr(
                    SourceSpan(
                        1,
                        index * 2 + 1,
                        1,
                        index * 2 + 2,
                    ),
                    index,
                    source_id=source_id,
                ),
                source_id=source_id,
            )
            for index in range(count)
        )

        program = Program(
            SourceSpan(1, 1, 1, count * 2 + 1),
            statements,
            source_id=source_id,
        )

        tracemalloc.start()

        started = time.perf_counter()
        result = validate_ast(program)
        elapsed = time.perf_counter() - started

        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.assertTrue(result.is_valid)
        self.assertEqual(
            result.nodes_visited,
            count * 2 + 1,
        )
        self.assertGreaterEqual(elapsed, 0)
        self.assertGreater(peak_bytes, 0)

        print(
            "AST_VALIDATION_METRICS "
            f"nodes={result.nodes_visited} "
            f"elapsed_seconds={elapsed:.6f} "
            f"validation_peak_bytes={peak_bytes}"
        )


if __name__ == "__main__":
    unittest.main()
