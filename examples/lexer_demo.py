"""Demonstrate the implemented Zen Lexer public API."""

from zen import Lexer


def main() -> None:
    source = "let answer = 42"
    for token in Lexer(source).tokenize():
        print(token)


if __name__ == "__main__":
    main()
