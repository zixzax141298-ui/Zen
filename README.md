# Zen Programming Language

**Version:** 0.1.0
**Milestone:** Z1 Lexer

> Simple to write. Clear to understand. Controlled to execute.

Zen adalah bahasa pemrograman general-purpose, dynamically typed,
dan interpreted yang dirancang agar mudah dipelajari dan dikembangkan.

## Project status

| Component | Status |
|---|---|
| Language specification | Initial version |
| Lexer | Implemented |
| Lexer tests | 37 tests |
| AST node model | Implemented |
| AST tests | 18 tests |
| Package/API tests | 3 tests |
| Total test methods | 58 |
| Package configuration | Implemented |
| Public API | Lexer exports only |
| Parser | Planned |
| Semantic analysis | Planned |
| Interpreter | Planned |
| Runtime | Planned |

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
- [Language Specification](docs/03-language-specification.md)
- [Changelog](CHANGELOG.md)
