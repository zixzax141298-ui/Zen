"""Zen v0.1.0 — Z1 Lexer."""

import math
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    EOF = auto()
    NEWLINE = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()

    LET = auto()
    CONST = auto()
    FN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    RETURN = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    BANG = auto()
    AND = auto()
    OR = auto()

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: object
    line: int
    column: int

    def __post_init__(self):
        if not isinstance(self.type, TokenType):
            raise TypeError("type must be a TokenType")

        if type(self.lexeme) is not str:
            raise TypeError("lexeme must be a string")

        if self.literal is not None:
            if type(self.literal) not in (int, float, str):
                raise TypeError(
                    "literal must be int, float, str, or None"
                )

            if type(self.literal) is float and not math.isfinite(self.literal):
                raise ValueError("literal float must be finite")

        if type(self.line) is not int or self.line <= 0:
            raise ValueError("line must be a positive integer")

        if type(self.column) is not int or self.column <= 0:
            raise ValueError("column must be a positive integer")


class LexerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(
            f"{message} at line {line}, column {column}"
        )


KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "return": TokenType.RETURN,
}

SINGLE = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "=": TokenType.ASSIGN,
    "<": TokenType.LESS,
    ">": TokenType.GREATER,
    "!": TokenType.BANG,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    "[": TokenType.LEFT_BRACKET,
    "]": TokenType.RIGHT_BRACKET,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
}

DOUBLE = {
    "==": TokenType.EQUAL,
    "!=": TokenType.NOT_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
    "&&": TokenType.AND,
    "||": TokenType.OR,
}


class Lexer:
    def __init__(self, source):
        if not isinstance(source, str):
            raise TypeError("source must be a string")

        self.source = source
        self.tokens = []
        self._finished = False
        self.current = 0
        self.line = 1
        self.column = 1
        self.start = 0
        self.start_line = 1
        self.start_column = 1

    def _at_end(self):
        return self.current >= len(self.source)

    def _peek(self):
        if self._at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _advance(self):
        char = self.source[self.current]
        self.current += 1

        # LF, CRLF, and CR each represent one logical newline.
        # Token lexemes retain the original source characters.
        if char == "\r":
            if not self._at_end() and self.source[self.current] == "\n":
                self.current += 1

            self.line += 1
            self.column = 1
            return "\n"

        if char == "\n":
            self.line += 1
            self.column = 1
            return "\n"

        self.column += 1
        return char

    def _match(self, expected):
        if self._at_end() or self._peek() != expected:
            return False

        self._advance()
        return True

    def _add(self, token_type, literal=None):
        lexeme = self.source[self.start:self.current]

        self.tokens.append(
            Token(
                token_type,
                lexeme,
                literal,
                self.start_line,
                self.start_column,
            )
        )

    def tokenize(self):
        if self._finished:
            return self.tokens.copy()

        while not self._at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line, self.column)
        )
        self._finished = True
        return self.tokens.copy()

    def _scan_token(self):
        char = self._advance()

        if char in " \t":
            return

        if char == "\n":
            self._add(TokenType.NEWLINE)
            return

        # Single-line comment
        if char == "/" and self._peek() == "/":
            while self._peek() not in ("\r", "\n", "\0"):
                self._advance()
            return

        # Block comment
        if char == "/" and self._peek() == "*":
            self._advance()
            self._block_comment()
            return

        # Strings
        if char in ('"', "'"):
            self._string(char)
            return

        # Numbers
        if char.isascii() and char.isdigit():
            self._number()
            return

        # Identifiers and keywords
        if char.isascii() and (char.isalpha() or char == "_"):
            self._identifier()
            return

        # Two-character operators
        pair = char + self._peek()

        if pair in DOUBLE:
            self._advance()
            self._add(DOUBLE[pair])
            return

        # Single-character tokens
        if char in SINGLE:
            self._add(SINGLE[char])
            return

        if char in "&|":
            raise LexerError(
                f"Unexpected character {char!r}; "
                f"use {char * 2!r}",
                self.start_line,
                self.start_column,
            )

        raise LexerError(
            f"Unexpected character {char!r}",
            self.start_line,
            self.start_column,
        )

    def _block_comment(self):
        comment_line = self.start_line
        comment_column = self.start_column

        while not self._at_end():
            if self._peek() == "*" and self._peek_next() == "/":
                self._advance()
                self._advance()
                return

            if self._peek() in ("\r", "\n"):
                self.start = self.current
                self.start_line = self.line
                self.start_column = self.column
                self._advance()
                self._add(TokenType.NEWLINE)
            else:
                self._advance()

        raise LexerError(
            "Unterminated block comment",
            comment_line,
            comment_column,
        )

    def _string(self, quote):
        chars = []

        escapes = {
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "\\": "\\",
            '"': '"',
            "'": "'",
        }

        while not self._at_end():
            char_line = self.line
            char_column = self.column
            char = self._advance()

            if char == quote:
                self._add(TokenType.STRING, "".join(chars))
                return

            if char == "\n":
                raise LexerError(
                    "Unterminated string",
                    self.start_line,
                    self.start_column,
                )

            if char == "\\":
                if self._at_end():
                    break

                escaped = self._advance()

                if escaped not in escapes:
                    raise LexerError(
                        f"Unknown escape sequence: \\{escaped}",
                        char_line,
                        char_column,
                    )

                chars.append(escapes[escaped])
            else:
                chars.append(char)

        raise LexerError(
            "Unterminated string",
            self.start_line,
            self.start_column,
        )

    def _number(self):
        while self._peek().isascii() and self._peek().isdigit():
            self._advance()

        is_float = False

        if (
            self._peek() == "."
            and self._peek_next().isascii()
            and self._peek_next().isdigit()
        ):
            is_float = True
            self._advance()

            while self._peek().isascii() and self._peek().isdigit():
                self._advance()

        text = self.source[self.start:self.current]

        # Numeric suffixes are not supported in Zen v0.1.
        next_char = self._peek()
        if next_char.isascii() and (
            next_char.isalpha() or next_char == "_"
        ):
            raise LexerError(
                "Numeric literal cannot be immediately followed "
                "by an identifier",
                self.line,
                self.column,
            )

        if is_float:
            digit_count = len(text) - 1

            if digit_count > 1024:
                raise LexerError(
                    "Float literal exceeds 1024 digits",
                    self.start_line,
                    self.start_column,
                )

            value = float(text)

            if not math.isfinite(value):
                raise LexerError(
                    "Float literal must be finite",
                    self.start_line,
                    self.start_column,
                )

            self._add(TokenType.FLOAT, value)
        else:
            if len(text) > 1024:
                raise LexerError(
                    "Integer literal exceeds 1024 digits",
                    self.start_line,
                    self.start_column,
                )

            self._add(TokenType.INTEGER, int(text))

    def _identifier(self):
        while True:
            char = self._peek()

            if char.isascii() and (char.isalnum() or char == "_"):
                self._advance()
            else:
                break

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)

        literal = None if token_type != TokenType.IDENTIFIER else text

        self._add(token_type, literal)
