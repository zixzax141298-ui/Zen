# Zen Installation Guide

**Version:** 0.1.0
**Status:** Initial packaging guide

## Requirements

- Python 3.10 or newer.
- pip.
- Setuptools 64 or newer for building and editable installation.

The current Zen lexer has no third-party runtime dependencies.

## Create a virtual environment

From the Zen project directory:

```bash
python -m venv .venv
```

Activate it in Termux or another POSIX shell:

```bash
source .venv/bin/activate
```

## Install Zen in editable mode

Run from the project root:

```bash
python -m pip install -e .
```

Editable installation makes the `zen` package importable while using
the source files in this working directory.

## Verify the installation

```bash
python -c "import zen; print(zen.__file__)"
```

Check the public API:

```bash
python -c "from zen import Lexer, LexerError, Token, TokenType; print('Zen API: OK')"
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Current limitations

- Only the lexer is implemented.
- Parser, AST, interpreter, and runtime are planned.
- The public API is intentionally limited to the four lexer symbols.
- This installation guide does not imply that Zen programs can yet be
  executed end-to-end.

## Packaging notes

The package distribution name is `zen-language`; the Python import name
is `zen`. The distribution name is provisional and must be reviewed
before any publication to a package index.

Setuptools is a build-time dependency. It is not listed as a Zen
runtime dependency.
