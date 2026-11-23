import unittest

import zen
from zen import (
    Lexer,
    LexerError,
    Token,
    TokenType,
    parse,
    ParseError,
    analyze,
    interpret,
)


class TestPackageAPI(unittest.TestCase):
    def test_public_exports_contain_core(self):
        required = {
            "Lexer",
            "LexerError",
            "Token",
            "TokenType",
            "parse",
            "ParseError",
            "analyze",
            "SemanticAnalyzer",
            "SemanticError",
            "interpret",
            "Interpreter",
            "RuntimeError",
        }
        self.assertTrue(required.issubset(set(zen.__all__)))

    def test_exported_symbols_match_package_attributes(self):
        self.assertIs(Lexer, zen.Lexer)
        self.assertIs(LexerError, zen.LexerError)
        self.assertIs(Token, zen.Token)
        self.assertIs(TokenType, zen.TokenType)
        self.assertIs(parse, zen.parse)
        self.assertIs(analyze, zen.analyze)
        self.assertIs(interpret, zen.interpret)

    def test_lexer_is_usable_through_public_api(self):
        tokens = Lexer("let answer = 42").tokenize()
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    def test_end_to_end_pipeline(self):
        prog = parse("fn f(x) { return x + 1 }\nf(41)")
        analyze(prog)
        result = interpret(prog)
        self.assertEqual(result, 42)


if __name__ == "__main__":
    unittest.main()
