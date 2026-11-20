import unittest

import zen
from zen import Lexer, LexerError, Token, TokenType


class TestPackageAPI(unittest.TestCase):
    def test_public_exports_are_exact(self):
        self.assertEqual(
            zen.__all__,
            ["Lexer", "LexerError", "Token", "TokenType"],
        )

    def test_exported_symbols_match_package_attributes(self):
        self.assertIs(Lexer, zen.Lexer)
        self.assertIs(LexerError, zen.LexerError)
        self.assertIs(Token, zen.Token)
        self.assertIs(TokenType, zen.TokenType)

    def test_lexer_is_usable_through_public_api(self):
        tokens = Lexer("let answer = 42").tokenize()
        self.assertEqual(tokens[-1].type, TokenType.EOF)


if __name__ == "__main__":
    unittest.main()
