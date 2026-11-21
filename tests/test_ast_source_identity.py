import unittest
from dataclasses import FrozenInstanceError

from zen.ast import (
    LiteralExpr,
    SourceIdentifier,
    SourceLocation,
    SourceSpan,
)


class SourceIdentityTests(unittest.TestCase):

    def test_new_and_explicit_continuity(self):
        first = SourceIdentifier.new()
        restored = SourceIdentifier.parse(str(first))

        self.assertEqual(restored, first)
        self.assertNotEqual(SourceIdentifier.new(), first)

    def test_identifier_is_immutable(self):
        source_id = SourceIdentifier.new()

        with self.assertRaises(
            (FrozenInstanceError, AttributeError)
        ):
            source_id.value = "changed"

    def test_invalid_identifier_values_are_rejected(self):
        values = (
            "",
            " padded ",
            "with space",
            "line\nbreak",
            "x" * 129,
        )

        for value in values:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    SourceIdentifier(value)

        with self.assertRaises(TypeError):
            SourceIdentifier(42)

    def test_source_location_separates_identity_from_span(self):
        source_id = SourceIdentifier.new()
        span = SourceSpan(1, 2, 1, 5)

        location = SourceLocation(source_id, span)

        self.assertEqual(location.source_id, source_id)
        self.assertEqual(location.span, span)

        self.assertEqual(
            (location.start_line, location.start_column),
            (1, 2),
        )

    def test_legacy_node_constructor_remains_compatible(self):
        span = SourceSpan(1, 1, 1, 2)

        legacy = LiteralExpr(span, 42)

        self.assertIsNone(legacy.source_id)
        self.assertIsNone(legacy.location)

        source_id = SourceIdentifier.new()

        canonical = LiteralExpr(
            span,
            42,
            source_id=source_id,
        )

        self.assertEqual(
            canonical.location,
            SourceLocation(source_id, span),
        )


if __name__ == "__main__":
    unittest.main()
