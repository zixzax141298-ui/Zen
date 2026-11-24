# Zen Programming Language

**Version:** 0.1.0
**Milestone:** ZIIF-01 Canonical AST Identity Fingerprint

> Simple to write. Clear to understand. Controlled to execute.

Zen adalah bahasa pemrograman general-purpose, dynamically typed,
dan interpreted yang dirancang agar mudah dipelajari dan dikembangkan.

## Project status

| Component | Status |
|---|---|
| Language specification | Formal v0.1 grammar specified (Owner-approved) |
| Lexer | Implemented |
| AST node model | Implemented |
| Parser | Implemented (recursive-descent, resource limits) |
| Semantic analysis | Implemented (OQ-01..OQ-09) |
| Interpreter / runtime | Implemented (tree-walk, OQ-07) |
| Public API | `parse`, `analyze`, `interpret`, `execute` |
| Package configuration | Implemented |

**Maturity:** v0.1 engineering prototype. Tested via pytest (Python 3.10–3.14).
Not production-ready.

Safe high-level entry point:

```python
from zen import execute
result = execute("fn f(x) { return x + 1 }\\nf(41)")  # -> 42
```

- `execute(source)` — Parse → AST validate → Semantic (strict) → Runtime (fail-closed).
- `interpret(program)` — low-level; caller must ensure semantic validity.

## Requirements

- Python 3.10+
- No third-party runtime dependencies for the current milestone.
- Setuptools is used as a build-time packaging dependency.

## Installation

For development, create and activate a virtual environment, then run:

```bash
python -m pip install -e .
```

See [Installation Guide](docs/02-installation.md).

## Public API

Top-level exports include lexer, parser, semantic analysis, and runtime:

- `Lexer`, `LexerError`, `Token`, `TokenType`
- `parse`, `ParseError`
- `analyze`, `SemanticAnalyzer`, `SemanticError`
- `interpret`, `Interpreter`, `RuntimeError` / `ZenRuntimeError`
- `execute` — recommended high-level pipeline

Example:

```python
from zen import execute, Lexer

print(execute("1 + 2 * 3"))  # 7

tokens = Lexer("let answer = 42").tokenize()
```

## Run tests

```bash
python -m pytest -q
```

## Documentation

- [Installation Guide](docs/02-installation.md)
- [Language Specification and Formal Grammar](docs/03-language-specification.md)
- [Changelog](CHANGELOG.md)
