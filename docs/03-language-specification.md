# Zen Language Specification — v0.1.0

**Milestone:** ZB-05 Formal Grammar
**Status:** Formal syntax specified; parser implemented in `src/zen/parser` (see README project status)
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
| Statement ending | Newline or semicolon; final statement may end at EOF or `}` |
| Scope | Block scope |
| Error handling | Strict |
| Type system | Dynamic |
| Execution | Interpreted |
| Constant declaration | `const` requires an initializer |
| Conditions | `if` and `while` require parenthesized expressions |
| Blocks | Braces required for function and control-flow bodies |

## 4. Lexical rules

### Whitespace and newlines

Spaces and tabs are ignored between tokens.

Zen recognizes LF (`\n`), CRLF (`\r\n`), and CR (`\r`) as line endings.
Each line ending represents exactly one logical newline and emits one
`NEWLINE` token. The token lexeme preserves the original source characters.

Newlines inside block comments are preserved as `NEWLINE` tokens.
Physical newlines inside string literals are rejected.

The parser treats newlines as separators except inside parenthesized
expressions, parameter lists, and argument lists, where they act as
whitespace. A newline does not otherwise continue an expression.
An operator at the end of a line does not continue an expression by itself.

### Comments

- `//` starts a line comment and continues up to, but not including,
  the line ending.
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
- Float literals may contain at most 1,024 digits in total,
  excluding the decimal point.
- Float values must be finite.
- A numeric literal immediately followed by an ASCII letter
  or underscore is a lexical error.
- Numeric suffixes are not supported.

### Identifiers

Identifiers begin with an ASCII letter or underscore.
Subsequent characters may include ASCII letters, digits, and underscores.
An identifier may contain at most 256 characters.

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
| Float literal | 1,024 digits, excluding decimal point |

The source limit is checked before lexing and counts Unicode code points,
not encoded bytes. String limits count decoded characters; each valid escape
sequence contributes one character. Comment limits exclude opening and
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

A single `&` or `|` is invalid. Square-bracket and colon tokens are
recognized lexically but do not introduce array, indexing, type-annotation,
or object syntax in this specification.

## 5. Formal grammar

This section defines the v0.1 concrete syntax using EBNF.

### 5.1 EBNF conventions

- `A = B ;` defines a production.
- `A | B` means either alternative.
- `[ A ]` means optional.
- `{ A }` means zero or more repetitions.
- Parentheses group grammar expressions.
- Uppercase names are lexer token types.
- `NEWLINE` represents one logical line ending.

### 5.2 Program and statement boundaries

```ebnf
program          = separators, [ statement, { separators, statement },
                   [ separators ] ], EOF ;

separators       = ( NEWLINE | SEMICOLON ), { NEWLINE | SEMICOLON } ;

statement        = variable_declaration
                 | function_declaration
                 | if_statement
                 | while_statement
                 | return_statement
                 | expression_statement ;

block            = LEFT_BRACE, { separators },
                   [ statement, { separators, statement },
                     [ separators ] ],
                   RIGHT_BRACE ;
```

An empty program and an empty block are valid.

A statement must be separated from the next statement by at least one
`NEWLINE` or `SEMICOLON`. Repeated separators are permitted and do not
create empty statements. The final statement in a program may end at
`EOF`. The final statement in a block may end immediately before
`RIGHT_BRACE`.

A `NEWLINE` inside a parenthesized expression, parameter list, or
argument list is whitespace rather than a statement separator.
A semicolon is never whitespace and is not allowed inside those lists.

### 5.3 Declarations and control flow

```ebnf
variable_declaration
                 = LET, IDENTIFIER, [ ASSIGN, expression ]
                 | CONST, IDENTIFIER, ASSIGN, expression ;

function_declaration
                 = FN, IDENTIFIER, LEFT_PAREN, [ parameter_list ],
                   RIGHT_PAREN, block ;

parameter_list   = IDENTIFIER, { COMMA, IDENTIFIER } ;

if_statement     = IF, LEFT_PAREN, expression, RIGHT_PAREN, block,
                   [ else_newlines, ELSE, ( block | if_statement ) ] ;

else_newlines    = { NEWLINE } ;

while_statement  = WHILE, LEFT_PAREN, expression, RIGHT_PAREN, block ;

return_statement = RETURN, [ expression ] ;

expression_statement
                 = expression ;
```

`let` declarations may omit an initializer. `const` declarations must
include one. Function parameters are identifiers separated by commas.
Default parameters and trailing commas are not part of v0.1.

Both `if` and `while` require parentheses around their condition and braces
around their body. `else` may be followed by a block or another `if`
statement (`else if`). Newlines may appear between the closing brace of
the then-block and `else`. A semicolon may not appear in that position.

An `else` belongs to the nearest preceding `if` that does not already
have an `else`. When parsing after an `if` then-block, the parser must
check for `else` before consuming intervening newlines as ordinary
statement separators.

A `return` without an expression returns no value. Its optional
expression must begin before the next `NEWLINE`, `SEMICOLON`,
`RIGHT_BRACE`, or `EOF` token. A newline immediately after `return`
therefore ends that return statement.

The grammar permits `return` wherever a statement is syntactically
allowed. Later semantic analysis must reject `return` outside a function.

### 5.4 Expressions and precedence

The following grammar encodes operator precedence from lowest to highest.
Binary operators at each repeated level associate left-to-right.
Assignment associates right-to-left.

```ebnf
expression       = assignment ;

assignment       = IDENTIFIER, ASSIGN, assignment
                 | logical_or ;

logical_or       = logical_and, { OR, logical_and } ;

logical_and      = equality, { AND, equality } ;

equality         = comparison, { ( EQUAL | NOT_EQUAL ), comparison } ;

comparison       = term,
                   { ( LESS | LESS_EQUAL | GREATER | GREATER_EQUAL ), term } ;

term             = factor, { ( PLUS | MINUS ), factor } ;

factor           = unary, { ( STAR | SLASH | PERCENT ), unary } ;

unary            = ( BANG | MINUS ), unary
                 | call ;

call             = primary, { argument_list } ;

argument_list    = LEFT_PAREN, [ arguments ], RIGHT_PAREN ;

arguments        = expression, { COMMA, expression } ;

primary          = TRUE
                 | FALSE
                 | NULL
                 | INTEGER
                 | FLOAT
                 | STRING
                 | IDENTIFIER
                 | LEFT_PAREN, expression, RIGHT_PAREN ;
```

Assignment is deliberately restricted to a bare `IDENTIFIER`, matching
the current `AssignExpr` AST model. Chained assignment such as
`a = b = 3` is parsed right-to-left. Assignment to a literal, grouped
expression, call result, or other expression is invalid.

The parser must use one-token lookahead to distinguish assignment from
an identifier expression. If the current token is `IDENTIFIER` and the
immediately following token is `ASSIGN`, it parses an assignment.
Otherwise, it parses a logical expression. The parser must not skip
`NEWLINE` or `SEMICOLON` during this decision.

Function calls may be chained because a call result may itself be called.
Arguments are comma-separated; trailing commas are unsupported.

The grammar permits a call suffix after a `primary` expression or a
previous call result. For example, `factory()()` is syntactically valid.
`-factory()` means unary minus applied to the call result, while
`(-factory)()` is a call whose callee is a grouped unary expression.
Whether a value is actually callable is a semantic/runtime question.
Unary operators are `!` and `-`; unary plus is unsupported.

| Precedence | Operators / form | Associativity |
|---:|---|---|
| 1 (lowest) | `=` assignment | Right |
| 2 | `||` | Left |
| 3 | `&&` | Left |
| 4 | `==`, `!=` | Left |
| 5 | `<`, `<=`, `>`, `>=` | Left |
| 6 | `+`, `-` | Left |
| 7 | `*`, `/`, `%` | Left |
| 8 | Prefix `!`, `-` | Right |
| 9 | Function call `(...)` | Left |
| 10 (highest) | Literals, identifiers, grouping | — |

This table specifies parsing and grouping only. Runtime type compatibility,
numeric coercion, comparison behavior, logical short-circuit behavior,
division-by-zero behavior, and assignment evaluation are semantic/runtime
decisions and are not defined by the grammar.

### 5.5 Grammar-to-AST correspondence

The following table describes the intended correspondence between
grammar constructs and the AST node model currently present in
`src/zen/ast/nodes.py`. This is a design reference only. It does not
mean that a parser or AST construction pipeline is implemented.

| Grammar construct | Intended AST node |
|---|---|
| Program | `Program` |
| Variable declaration | `VarDecl` |
| Function declaration | `FunctionDecl` |
| Block | `BlockStmt` |
| `if` / `else` | `IfStmt` |
| `while` | `WhileStmt` |
| `return` | `ReturnStmt` |
| Expression statement | `ExpressionStmt` |
| Literal | `LiteralExpr` |
| Identifier | `IdentifierExpr` |
| Grouped expression | `GroupingExpr` |
| Prefix operator | `UnaryExpr` |
| Binary operator | `BinaryExpr` |
| Assignment | `AssignExpr` |
| Function call | `CallExpr` |

`IfStmt.else_branch` can represent a `BlockStmt`, another `IfStmt`,
or `None`, which supports `else if` chains. `AssignExpr.target` is an
`IdentifierExpr`, matching the grammar's bare-identifier restriction.
`CallExpr` stores its callee as an expression and its arguments as a
tuple of expressions.

AST nodes carry `SourceSpan` information. The parser implementation
must define and test how token positions are combined into node spans.
This correspondence does not claim that this behavior exists yet.

### 5.6 Newline and `else` handling

1. At statement level, `NEWLINE` and `SEMICOLON` are separators.
2. Within parentheses used for grouping expressions, `if` and `while`
   conditions, parameter lists, or call argument lists, `NEWLINE` is
   ignored as whitespace.
3. A newline does not continue an expression outside parentheses.
4. `else` may be separated from its preceding then-block by zero or more
   newlines. A semicolon between the then-block and `else` is invalid.
5. A closing brace ends the final statement in its block without requiring
   an additional separator.
6. A statement cannot be followed by another statement on the same line
   without a semicolon.
7. An `else` binds to the nearest preceding unmatched `if`.
8. The parser checks for `else` before consuming newlines following an
   `if` then-block as statement separators.
9. A `return` expression must begin before the next `NEWLINE`,
   `SEMICOLON`, `RIGHT_BRACE`, or `EOF`.
10. Assignment disambiguation uses the immediate next token after an
    `IDENTIFIER`; newline and semicolon tokens are not skipped.

### 5.7 Examples

Valid examples:

```zen
let answer = 40 + 2
const label = "Zen"

fn add(a, b) {
    return a + b
}

if (answer >= 42) {
    let status = "ready"
} else {
    let status = "waiting"
}

while (answer > 0) {
    answer = answer - 1
}

let total = add(
    10,
    20
)
```

Invalid examples:

```zen
const missing_value
if answer > 0 { }
while (true) do_something
let value = 1 let next = 2
(a + b) = 3
fn bad(a, ) { }
```

## 5.8 AST resource and structural constraints

The AST model has explicit structural resource contracts. Parser enforcement is
required when a parser is implemented; the presence of constants and parser
context scaffolding does not mean a parser currently enforces these limits.

| Limit | Value | Meaning |
|---|---:|---|
| `MAX_AST_NODES` | 1,000,000 | Maximum total AST nodes for one `Program`. |
| `MAX_AST_DEPTH` | 256 | Maximum structural nesting depth of an AST. |
| `MAX_DIRECT_CHILDREN` | 262,144 | Maximum number of direct children in one collection. |
| `MAX_EXPRESSION_NODES` | 262,144 | Maximum nodes in one expression tree. |
| `MAX_STATEMENT_NODES` | 262,144 | Maximum nodes in one statement tree. |

AST depth is structural: the root node has depth 1, and each child edge adds
one level. A valid AST is a finite tree. `Program` has no parent; every other
node has exactly one parent. Cycles and reuse of the same Python node object at
multiple child locations are invalid. Node identity for reuse checks is based
on `id(node)`, not structural equality.

Every node has a source span using half-open coordinates: `start` is inclusive
and `end` is exclusive. A child span must be contained by its parent span.
Direct siblings must be in source order and must not overlap; adjacent siblings
are valid when the previous child's `end` equals the next child's `start`.

The parser owns grammar validity, AST resource-limit enforcement, and
source-located diagnostics. The AST owns immutable node data and structural
invariants such as child types, span containment, sibling ordering, and direct
collection bounds. AST validation helpers can additionally detect graph cycles
and node reuse for tests, AST loading, and transformation validation; those
checks are not automatically run for every node construction. User-facing
limit violations must be reported as parser diagnostics with source locations.

## 6. Scope and semantic constraints

Zen uses block scope. Exact declaration, redeclaration, name-resolution,
and constant-assignment rules belong to semantic analysis and must be
specified before that phase is implemented.

The grammar does not determine whether an identifier is declared,
whether a constant is reassigned, or whether a function call refers to
a valid callable value.

## 7. Error handling

Strict error handling: the first lexical, syntax, semantic, or runtime
error stops the current program.

Lexical errors include source line and column. Parser errors must include
source location information and must not silently skip malformed input.
The exact parser diagnostic format will be specified with parser
implementation.

## 8. Architecture

Source → Lexer → Parser → AST → Semantic Analysis
→ Interpreter → Runtime

## 9. Implementation status

### Implemented

- Token definitions
- Keywords and identifiers
- Integer and float literals
- String literals and escapes
- Operators and punctuation
- C-style comments
- Newline tokens
- Strict lexical errors with locations
- Immutable AST node model and source spans
- AST structural validation

### Specified but not yet implemented

- Formal v0.1 grammar and expression precedence
- AST resource-limit enforcement by a parser (limits and context scaffolding exist; no parser enforcement is implemented)
- Parser

### Planned

- Semantic analysis
- Interpreter
- Runtime and variables
- Execution of `.zen` programs
- Functions and control-flow execution
- Arrays and objects
- Module system
- Standard library

A syntax rule being specified does not mean it is already executable.
A planned feature must not be advertised as implemented. Square-bracket
tokens do not mean arrays or indexing are supported.

## 10. Security principles

Zen must not use Python `eval()` or `exec()` to execute Zen source.
Early runtimes must not expose unrestricted shell, filesystem,
or network access.

A restricted interpreter is not automatically a secure OS sandbox.\n