# Changelog

All notable project changes are recorded here.
This file distinguishes implemented functionality from specified syntax
and planned work.

## 0.1.0 — Current project baseline

### Implemented

- Initial Zen project structure and Python package configuration.
- Public API exports `Lexer`, `LexerError`, `Token`, and `TokenType`.
- Lexer support for keywords, identifiers, integer and decimal literals,
  strings, operators, punctuation, and comments.
- Newline tokens are preserved for parser use.
- Lexical errors report source line and column.
- Immutable AST node model and source-span representation.
- Editable installation using `python -m pip install -e .`.
- Automated lexer, AST, and public API tests.

### Specified, not yet implemented

- Formal v0.1 grammar, statement boundaries, and expression precedence.
- Parser-facing syntax rules and intended grammar-to-AST correspondence (design only).

### Planned, not yet implemented

- Parser implementation.
- Semantic analysis.
- Interpreter and runtime.
- Execution of `.zen` programs.
