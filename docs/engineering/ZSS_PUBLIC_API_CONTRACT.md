# ZSS Public API Contract

**Document ID:** ZSS-API-01  
**Revision:** 1  
**Status:** Engineering contract (describes current implementation)  
**Applies to:** Zen package public surface at `src/zen`

## 1. High-level pipeline — `execute(source)`

Fail-closed sequence:

1. Type-check `source` is `str`
2. Lex + parse → `Program` AST (`ParseError` / `LexerError` on failure)
3. Structural AST validation (`ValueError` on invalid AST)
4. Semantic analysis strict (`SemanticError` on any ERROR diagnostic)
5. Tree-walk interpret (`ZenRuntimeError` / `RuntimeError` on runtime failure)

Callers who use `execute` need not call `analyze` or `validate_ast` themselves.

## 2. Low-level APIs

| API | Guarantees | Caller responsibility |
|-----|------------|------------------------|
| `parse(source)` | Syntax-valid AST or raises | Does not semantic-check |
| `analyze(program)` | List of diagnostics | Does not execute |
| `interpret(program)` | Evaluates AST | Caller must ensure semantic validity |
| `Interpreter` | Stateful evaluation | Same as `interpret` |

Calling `interpret` on a program that was never analyzed may raise runtime errors for conditions that semantic analysis would have rejected earlier (undefined names, bad arity, etc.), or may produce undefined behavior relative to the language rules.

## 3. Exceptions

- `LexerError`, `ParseError` — lexical/syntactic
- `SemanticError` — semantic (from `analyze_strict` / `execute`)
- `ZenRuntimeError` (`RuntimeError` alias) — controlled runtime faults
- `ValueError` — AST validation failure inside `execute`
- `TypeError` — non-string source

Raw Python `RecursionError` must not escape `parse()` for inputs within declared resource policy; it is converted to `ParseError`.

## 4. Maturity

v0.1 engineering prototype. Not production-ready.
