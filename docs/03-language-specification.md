# Zen Language Specification — v0.1.0

**Milestone:** Z1 Lexer
**Status:** Initial specification
**Source extension:** `.zen`

## 1. Purpose

Zen adalah bahasa pemrograman general-purpose, dynamically typed,
dan interpreted. Zen dirancang agar mudah dipelajari, dibaca,
dan dikembangkan secara bertahap.

**Motto:** Simple to write. Clear to understand.
Controlled to execute.

## 2. Core principles

- Readability
- Predictability
- Simplicity
- Modularity
- Safety
- Evidence-based implementation

## 3. Official v0.1 decisions

| Area | Decision |
|---|---|
| Comments | C-style `//` and `/* ... */` |
| Statement ending | Optional semicolon; newline is primary separator |
| Scope | Block scope |
| Error handling | Strict |
| Type system | Dynamic |
| Execution | Interpreted |

## 4. Lexical rules

### Whitespace and newlines

Spaces, tabs, and carriage returns are ignored.
Newlines are preserved as `NEWLINE` tokens.

### Comments

- `//` starts a line comment.
- `/* ... */` starts and ends a block comment.
- Block comments do not nest.
- Newlines inside block comments are preserved.
- An unterminated block comment is an error.

### Strings

Single-quoted and double-quoted strings are supported.

Supported escapes:

- `\\`
- `\"`
- `\'`
- `\n`
- `\r`
- `\t`

Strings cannot cross physical lines. Unknown escapes are errors.

### Numbers

Supported:
- Integers: `0`, `42`
- Decimal floats: `3.14`

Not supported in v0.1:
- Exponent notation
- Numeric separators
- Leading-dot floats such as `.5`

Numeric literal limits:

- Integer literals may contain at most 1,024 digits.
- Float literals may contain at most 1,024 digits in total;
  the decimal point is not counted.
- Float values must be finite.
- A numeric literal immediately followed by an ASCII letter
  or underscore is a lexical error.
- Numeric suffixes are not supported in v0.1.

### Identifiers

Identifiers begin with an ASCII letter or underscore.
Subsequent characters may include ASCII letters, digits, and underscores.

### Keywords

`let`, `const`, `fn`, `if`, `else`, `while`,
`true`, `false`, `null`, `return`

### Operators

`+ - * / % = == != < <= > >= ! && ||`

### Punctuation

`( ) { } [ ] , : ;`

A single `&` or `|` is invalid.

## 5. Statement boundaries

A newline is the primary statement separator.
A semicolon may also terminate a statement.

The Lexer preserves newlines. The Parser will determine whether
a newline is a valid statement boundary in context.

## 6. Scope

Zen uses block scope. Exact declaration and redeclaration rules
will be specified before semantic analysis is implemented.

## 7. Error handling

Strict error handling: the first lexical, syntax, semantic,
or runtime error stops the current program.

Lexical errors include source line and column.

## 8. Architecture

Source → Lexer → Parser → AST → Semantic Analysis
→ Interpreter → Runtime

## 9. Implementation status

### Implemented in Z1

- Token definitions
- Keywords and identifiers
- Integer and float literals
- String literals and escapes
- Operators and punctuation
- C-style comments
- Newline tokens
- Strict lexical errors with locations

### Planned

- Parser and AST
- Semantic analysis
- Interpreter
- Runtime and variables
- Functions and control flow
- Arrays and objects
- Module system
- Standard library

A planned feature must not be advertised as implemented.

## 10. Security principles

Zen must not use Python `eval()` or `exec()` to execute Zen source.
Early runtimes must not expose unrestricted shell, filesystem,
or network access.

A restricted interpreter is not automatically a secure OS sandbox.
