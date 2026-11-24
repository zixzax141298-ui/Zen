"""Parser nesting depth protection."""
from __future__ import annotations

import pytest

from zen.limits import MAX_PARSER_DEPTH
from zen.parser import ParseError, parse


def test_deep_unary_controlled():
    src = "-" * (MAX_PARSER_DEPTH + 5) + "1"
    with pytest.raises(ParseError, match="nesting depth"):
        parse(src)


def test_deep_grouping_controlled():
    n = MAX_PARSER_DEPTH + 5
    src = "(" * n + "1" + ")" * n
    with pytest.raises(ParseError, match="nesting depth"):
        parse(src)


def test_moderate_grouping_ok():
    n = 40
    src = "(" * n + "1" + ")" * n
    prog = parse(src)
    assert prog is not None


def test_shallow_unary_ok():
    parse("---1")
