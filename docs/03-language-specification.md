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

Spaces and tabs are ignored.

Zen recognizes LF (`\n`), CRLF (`\r\n`), and CR (`\r`) as line endings. Each line ending represents exactly one logical newline and emits one `NEWLINE` token. The token lexeme preserves the original source characters.

Newlines inside block comments are preserved as `NEWLINE` tokens. Physical newlines inside string literals are rejected.

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

### Resource limits

The lexer enforces the following limits to bound source-processing memory
and work. Counts are measured in Python Unicode code points unless stated
otherwise.

| Resource | Maximum |
|---|---:|
| Source text | 2,097,152 characters |
| Identifier | 256 characters |
| Decoded string value | 1,048,576 characters |
| Single comment body | 1,048,576 characters |
| Non-EOF tokens | 262,144 tokens |
| Integer literal | 1,024 digits |
| Float literal | 1,024 digits, excluding the decimal point |

The source limit is checked before lexing and counts Unicode code points,
not encoded bytes. String limits count decoded characters; each valid escape
sequence contributes one character. Comment limits exclude the opening and
closing delimiters. For comment counting, CRLF contributes two source
characters even though it represents one logical newline.

The token limit counts every emitted non-EOF token, including `NEWLINE`
tokens preserved from block comments. The `EOF` token is not counted.

Exceeding a limit is a lexical error; input is never silently truncated.
Source-size errors point to line 1, column 1. Identifier, string, and
comment limit errors point to the start of the affected lexeme or comment.

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
