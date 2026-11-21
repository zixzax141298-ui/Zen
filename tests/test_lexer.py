import unittest

from src.zen.lexer import Lexer, LexerError, TokenType


class LexerTests(unittest.TestCase):

    def test_empty_source(self):
        tokens = Lexer("").tokenize()
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_keywords(self):
        tokens = Lexer(
            "let const fn if else while true false null return"
        ).tokenize()

        expected = [
            TokenType.LET, TokenType.CONST, TokenType.FN,
            TokenType.IF, TokenType.ELSE, TokenType.WHILE,
            TokenType.TRUE, TokenType.FALSE, TokenType.NULL,
            TokenType.RETURN, TokenType.EOF,
        ]

        self.assertEqual([t.type for t in tokens], expected)

    def test_identifier(self):
        token = Lexer("user_name42").tokenize()[0]

        self.assertEqual(token.type, TokenType.IDENTIFIER)
        self.assertEqual(token.literal, "user_name42")

    def test_numbers(self):
        tokens = Lexer("0 42 3.14").tokenize()

        self.assertEqual(
            [t.type for t in tokens[:-1]],
            [
                TokenType.INTEGER,
                TokenType.INTEGER,
                TokenType.FLOAT,
            ],
        )

        self.assertEqual(
            [t.literal for t in tokens[:-1]],
            [0, 42, 3.14],
        )

    def test_strings(self):
        tokens = Lexer(r"""'hello' "line\nnext" "quote: \"" """).tokenize()

        self.assertEqual(
            [t.literal for t in tokens[:-1]],
            ["hello", "line\nnext", 'quote: "'],
        )

    def test_line_comment_preserves_newline(self):
        tokens = Lexer("let x = 1 // comment\nprint(x)").tokenize()

        self.assertIn(
            TokenType.NEWLINE,
            [t.type for t in tokens],
        )

    def test_block_comment_preserves_newline(self):
        tokens = Lexer("a/* comment\ncontinued */b").tokenize()

        self.assertEqual(
            [t.type for t in tokens],
            [
                TokenType.IDENTIFIER,
                TokenType.NEWLINE,
                TokenType.IDENTIFIER,
                TokenType.EOF,
            ],
        )

    def test_operators(self):
        source = "+ - * / % = == != < <= > >= ! && ||"
        tokens = Lexer(source).tokenize()

        expected = [
            TokenType.PLUS, TokenType.MINUS,
            TokenType.STAR, TokenType.SLASH,
            TokenType.PERCENT, TokenType.ASSIGN,
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL,
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.BANG, TokenType.AND, TokenType.OR,
            TokenType.EOF,
        ]

        self.assertEqual([t.type for t in tokens], expected)

    def test_punctuation(self):
        source = "() {} [] , : ;"
        tokens = Lexer(source).tokenize()

        expected = [
            TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE,
            TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET,
            TokenType.COMMA, TokenType.COLON,
            TokenType.SEMICOLON, TokenType.EOF,
        ]

        self.assertEqual([t.type for t in tokens], expected)

    def test_illegal_character_location(self):
        with self.assertRaises(LexerError) as context:
            Lexer("let x = 1\n@").tokenize()

        self.assertEqual(context.exception.line, 2)
        self.assertEqual(context.exception.column, 1)

    def test_unterminated_block_comment(self):
        with self.assertRaises(LexerError):
            Lexer("/* never closed").tokenize()

    def test_unterminated_string(self):
        with self.assertRaises(LexerError):
            Lexer('"never closed').tokenize()

    def test_unknown_escape(self):
        with self.assertRaises(LexerError):
            Lexer(r'"bad\q"').tokenize()

    def test_single_ampersand_rejected(self):
        with self.assertRaises(LexerError):
            Lexer("a & b").tokenize()

    def test_token_location_after_newline(self):
        tokens = Lexer("\n  let").tokenize()
        token = next(t for t in tokens if t.type == TokenType.LET)

        self.assertEqual(token.line, 2)
        self.assertEqual(token.column, 3)



    def test_integer_1024_digits_accepted(self):
        source = "9" * 1024
        token = Lexer(source).tokenize()[0]

        self.assertEqual(token.type, TokenType.INTEGER)
        self.assertEqual(len(token.lexeme), 1024)

    def test_integer_1025_digits_rejected(self):
        source = "9" * 1025

        with self.assertRaises(LexerError):
            Lexer(source).tokenize()

    def test_float_1024_digits_accepted(self):
        source = "1." + "2" * 1023
        token = Lexer(source).tokenize()[0]

        self.assertEqual(token.type, TokenType.FLOAT)
        self.assertTrue(token.literal < float("inf"))

    def test_float_1025_digits_rejected(self):
        source = "1." + "2" * 1024

        with self.assertRaises(LexerError):
            Lexer(source).tokenize()

    def test_non_finite_float_rejected(self):
        source = "9" * 309 + ".0"

        with self.assertRaises(LexerError) as context:
            Lexer(source).tokenize()

        self.assertIn("finite", context.exception.message)

    def test_unknown_escape_points_to_backslash(self):
        source = '"abc\\\n'

        with self.assertRaises(LexerError) as context:
            Lexer(source).tokenize()

        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 5)

    def test_tokenize_can_be_called_repeatedly(self):
        lexer = Lexer("let answer = 42")

        first = lexer.tokenize()
        second = lexer.tokenize()

        self.assertEqual(first, second)
        self.assertEqual(
            sum(token.type == TokenType.EOF for token in second),
            1,
        )

    def test_numeric_suffixes_rejected(self):
        for source in ("123abc", "123_foo", "1.2ms", "123true"):
            with self.subTest(source=source):
                with self.assertRaises(LexerError):
                    Lexer(source).tokenize()

    def test_nul_character_rejected(self):
        with self.assertRaises(LexerError):
            Lexer("abc\x00def").tokenize()



    def test_lf_newline_position_and_lexeme(self):
        tokens = Lexer("a\nb").tokenize()
        self.assertEqual(tokens[1].lexeme, "\n")
        self.assertEqual((tokens[1].line, tokens[1].column), (1, 2))
        self.assertEqual((tokens[2].line, tokens[2].column), (2, 1))

    def test_crlf_is_one_newline(self):
        tokens = Lexer("a\r\nb").tokenize()
        self.assertEqual(tokens[1].type, TokenType.NEWLINE)
        self.assertEqual(tokens[1].lexeme, "\r\n")
        self.assertEqual((tokens[2].line, tokens[2].column), (2, 1))

    def test_cr_only_is_one_newline(self):
        tokens = Lexer("a\rb").tokenize()
        self.assertEqual(tokens[1].type, TokenType.NEWLINE)
        self.assertEqual(tokens[1].lexeme, "\r")
        self.assertEqual((tokens[2].line, tokens[2].column), (2, 1))

    def test_mixed_newline_styles(self):
        tokens = Lexer("a\r\nb\rc\nd").tokenize()
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        self.assertEqual([t.lexeme for t in newlines], ["\r\n", "\r", "\n"])
        self.assertEqual([(t.line, t.column) for t in newlines],
                         [(1, 2), (2, 2), (3, 2)])
        self.assertEqual((tokens[-1].line, tokens[-1].column), (4, 2))

    def test_tab_counts_as_one_column(self):
        token = Lexer("\tlet").tokenize()[0]
        self.assertEqual((token.line, token.column), (1, 2))

    def test_unicode_codepoint_counts_as_one_column(self):
        tokens = Lexer('"😀" x').tokenize()
        identifier = next(t for t in tokens if t.type == TokenType.IDENTIFIER)
        self.assertEqual((identifier.line, identifier.column), (1, 5))

    def test_line_comment_preserves_cr_newline(self):
        tokens = Lexer("a // comment\rb").tokenize()
        newline = next(t for t in tokens if t.type == TokenType.NEWLINE)
        self.assertEqual(newline.lexeme, "\r")
        self.assertEqual((tokens[-2].line, tokens[-2].column), (2, 1))

    def test_block_comment_preserves_crlf_and_cr(self):
        tokens = Lexer("a/*x\r\ny\rz*/b").tokenize()
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        self.assertEqual([t.lexeme for t in newlines], ["\r\n", "\r"])
        self.assertEqual([(t.line, t.column) for t in newlines],
                         [(1, 5), (2, 2)])
        self.assertEqual((tokens[-2].line, tokens[-2].column), (3, 4))

    def test_escaped_newline_is_not_physical_newline(self):
        tokens = Lexer(r'"first\nsecond"').tokenize()
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "first\nsecond")

    def test_physical_newline_inside_string_is_rejected(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                with self.assertRaises(LexerError):
                    Lexer('"first' + newline + 'second"').tokenize()

    def test_error_location_after_crlf(self):
        with self.assertRaises(LexerError) as context:
            Lexer("a\r\n@").tokenize()
        self.assertEqual((context.exception.line, context.exception.column), (2, 1))

    def test_eof_location_after_newline(self):
        for newline in ("\n", "\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                eof = Lexer("a" + newline).tokenize()[-1]
                self.assertEqual((eof.line, eof.column), (2, 1))

    def test_eof_location_without_newline(self):
        eof = Lexer("abc").tokenize()[-1]
        self.assertEqual((eof.line, eof.column), (1, 4))


    def test_single_character_operator_error_locations(self):
        cases = [
            ("a & b", (1, 3)),
            ("a | b", (1, 3)),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                with self.assertRaises(LexerError) as context:
                    Lexer(source).tokenize()
                self.assertEqual(
                    (context.exception.line, context.exception.column),
                    expected,
                )

    def test_unterminated_block_comment_location(self):
        with self.assertRaises(LexerError) as context:
            Lexer("a\n /* open").tokenize()

        self.assertEqual(
            (context.exception.line, context.exception.column),
            (2, 2),
        )

    def test_unterminated_string_location(self):
        with self.assertRaises(LexerError) as context:
            Lexer('a\n"open').tokenize()

        self.assertEqual(
            (context.exception.line, context.exception.column),
            (2, 1),
        )

    def test_unknown_escape_location_points_to_backslash(self):
        with self.assertRaises(LexerError) as context:
            Lexer('"abc\\q"').tokenize()

        self.assertEqual(
            (context.exception.line, context.exception.column),
            (1, 5),
        )

    def test_numeric_suffix_error_location(self):
        with self.assertRaises(LexerError) as context:
            Lexer("12abc").tokenize()

        self.assertEqual(
            (context.exception.line, context.exception.column),
            (1, 3),
        )

    def test_numeric_range_error_locations(self):
        cases = [
            ("x " + "9" * 1025, (1, 3)),
            ("x " + "1." + "2" * 1024, (1, 3)),
            ("x " + "9" * 309 + ".0", (1, 3)),
        ]
        for source, expected in cases:
            with self.subTest(source_length=len(source)):
                with self.assertRaises(LexerError) as context:
                    Lexer(source).tokenize()
                self.assertEqual(
                    (context.exception.line, context.exception.column),
                    expected,
                )

    def test_dangling_escape_location(self):
        with self.assertRaises(LexerError) as context:
            Lexer('"abc\\').tokenize()

        self.assertEqual(
            (context.exception.line, context.exception.column),
            (1, 1),
        )

    def test_error_locations_are_consistent_across_newline_styles(self):
        newlines = {
            "LF": "\n",
            "CRLF": "\r\n",
            "CR": "\r",
        }
        cases = [
            ("illegal character", lambda nl: ("a" + nl + "@", (2, 1))),
            ("unterminated string", lambda nl: ('"abc' + nl + "def", (1, 1))),
            ("unterminated comment", lambda nl: ("a" + nl + "/* open", (2, 1))),
            ("unknown escape", lambda nl: ('a' + nl + '"x\\q"', (2, 3))),
        ]

        for newline_name, newline in newlines.items():
            for case_name, build_case in cases:
                source, expected = build_case(newline)
                with self.subTest(newline=newline_name, case=case_name):
                    with self.assertRaises(LexerError) as context:
                        Lexer(source).tokenize()
                    self.assertEqual(
                        (context.exception.line, context.exception.column),
                        expected,
                    )


class TokenSafetyTests(unittest.TestCase):
    def test_token_attributes_are_frozen(self):
        from src.zen.lexer import Token

        token = Token(TokenType.INTEGER, "42", 42, 1, 1)

        with self.assertRaises(AttributeError):
            token.lexeme = "99"

    def test_token_rejects_invalid_type(self):
        from src.zen.lexer import Token

        with self.assertRaises(TypeError):
            Token("INTEGER", "42", 42, 1, 1)

    def test_token_rejects_invalid_lexeme(self):
        from src.zen.lexer import Token

        with self.assertRaises(TypeError):
            Token(TokenType.INTEGER, 42, 42, 1, 1)

    def test_token_rejects_mutable_literal(self):
        from src.zen.lexer import Token

        for value in ([], {}, set(), object()):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(TypeError):
                    Token(TokenType.STRING, '"x"', value, 1, 1)

    def test_token_rejects_boolean_literal(self):
        from src.zen.lexer import Token

        with self.assertRaises(TypeError):
            Token(TokenType.TRUE, "true", True, 1, 1)

    def test_token_rejects_non_finite_float(self):
        from src.zen.lexer import Token

        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Token(TokenType.FLOAT, "1.0", value, 1, 1)

    def test_token_rejects_invalid_line_and_column(self):
        from src.zen.lexer import Token

        for field, value in (
            ("line", 0),
            ("line", -1),
            ("line", True),
            ("column", 0),
            ("column", -1),
            ("column", False),
        ):
            with self.subTest(field=field, value=value):
                args = {
                    "type": TokenType.IDENTIFIER,
                    "lexeme": "name",
                    "literal": "name",
                    "line": 1,
                    "column": 1,
                }
                args[field] = value
                with self.assertRaises(ValueError):
                    Token(**args)

    def test_token_accepts_valid_literal_types(self):
        from src.zen.lexer import Token

        for value in (None, 42, 3.14, "hello"):
            with self.subTest(value=value):
                token = Token(
                    TokenType.IDENTIFIER, "name", value, 1, 1
                )
                self.assertEqual(token.literal, value)

    def test_tokenize_returns_independent_lists(self):
        lexer = Lexer("let answer = 42")

        first = lexer.tokenize()
        second = lexer.tokenize()

        self.assertIsNot(first, second)
        self.assertEqual(first, second)

    def test_mutating_tokenize_result_does_not_corrupt_cache(self):
        lexer = Lexer("let answer = 42")

        first = lexer.tokenize()
        original_count = len(first)

        first.clear()

        second = lexer.tokenize()

        self.assertEqual(len(second), original_count)
        self.assertEqual(second[-1].type, TokenType.EOF)
        self.assertEqual(
            sum(token.type == TokenType.EOF for token in second),
            1,
        )

if __name__ == "__main__":
    unittest.main()
