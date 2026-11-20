# Changelog

All notable project changes are recorded here.
This file distinguishes implemented functionality from planned work.

## 0.1.0 — Current project baseline

### Implemented

- Initial Zen project structure and Python package configuration.
- Public API exports `Lexer`, `LexerError`, `Token`, and `TokenType`.
- Lexer support for keywords, identifiers, integer and decimal literals,
  strings, operators, punctuation, and comments.
- Newline tokens are preserved for parser use.
- Lexical errors report source line and column.
- Editable installation using `python -m pip install -e .`.
- Automated lexer and public API tests.

### Planned, not yet implemented

- Parser and abstract syntax tree.
- Semantic analysis.
- Interpreter and runtime.
- Execution of `.zen` programs.
