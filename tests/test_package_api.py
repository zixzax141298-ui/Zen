import unittest

import zen
from zen import (
    Lexer,
    LexerError,
    Token,
    TokenType,
    parse,
    analyze,
    interpret,
    execute,
)


class TestPackageAPI(unittest.TestCase):
    def test_public_exports_contain_core(self):
        required = {
            "Lexer", "LexerError", "Token", "TokenType",
            "parse", "ParseError", "analyze", "SemanticAnalyzer",
            "SemanticError", "interpret", "Interpreter",
            "RuntimeError", "execute",
        }
        self.assertTrue(required.issubset(set(zen.__all__)))

    def test_end_to_end_pipeline(self):
        result = execute("fn f(x) { return x + 1 }\nf(41)")
        self.assertEqual(result, 42)

    def test_execute_semantic_failure(self):
        with self.assertRaises(zen.SemanticError):
            execute("return 1")

    def test_execute_parse_failure(self):
        with self.assertRaises(zen.ParseError):
            execute("let = 1")

    def test_lexer_usable(self):
        tokens = Lexer("let answer = 42").tokenize()
        self.assertEqual(tokens[-1].type, TokenType.EOF)


if __name__ == "__main__":
    unittest.main()
