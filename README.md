# Zen Programming Language

**Version:** 0.1.0
**Milestone:** ZIIF-01 Canonical AST Identity Fingerprint

> Simple to write. Clear to understand. Controlled to execute.

Zen adalah bahasa pemrograman general-purpose, dynamically typed,
dan interpreted yang dirancang agar mudah dipelajari dan dikembangkan.

## Project status

| Component | Status |
|---|---|
| Language specification | Formal v0.1 grammar specified |
| Lexer | Implemented |

| AST node model | Implemented |



| Package configuration | Implemented |
| Public API | Lexer exports only |
| Parser | Not implemented |
| Semantic analysis | Planned |
| Interpreter | Planned |
| Runtime | Planned |

The formal grammar defines the intended v0.1 syntax. It does not mean
that Zen source programs can already be parsed or executed.

## Requirements

- Python 3.10+
- No third-party runtime dependencies for the current lexer milestone.
- Setuptools is used as a build-time packaging dependency.

## Installation

For development, create and activate a virtual environment, then run:

```bash
python -m pip install -e .
```

See [Installation Guide](docs/02-installation.md).

## Public API

The initial public API exports:

- `Lexer`
- `LexerError`
- `Token`
- `TokenType`

The AST node model is currently available from `zen.ast`; it is not yet
part of the top-level `zen` public API.

Example:

```python
from zen import Lexer

tokens = Lexer("let answer = 42").tokenize()
for token in tokens:
    print(token)
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Documentation

- [Installation Guide](docs/02-installation.md)
- [Language Specification and Formal Grammar](docs/03-language-specification.md)
- [Changelog](CHANGELOG.md)
