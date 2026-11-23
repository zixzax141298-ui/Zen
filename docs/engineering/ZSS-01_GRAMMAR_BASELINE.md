# ZSS-01 — Grammar Baseline & Design Foundation

**Project:** ZEN Programming Language
**Workstream:** ZSS — Zen Structured Syntax
**Document Type:** Engineering Design Baseline
**Status:** OWNER-APPROVED DESIGN BASELINE
**Owner Approval:** APPROVED
**Approval Basis:** Explicit Owner approval through GitHub merge (PR #29).
**Approval Status:** The merged document is approved by the Owner.
**Merge Evidence:** PR #29 merged 2026-11-23T09:59:57Z (head `ef9975bd437c1e11c00dbb00a4786b72040c1815`).
**Development Mode:** Documentation-only
**Official Grammar:** Zen Language Specification v0.1.0
**Repository:** zixzax141298-ui/Zen

> Note: Owner approval of this design baseline does not claim that Parser or Semantic Analysis implementation is complete.

---

## 1. Purpose

ZSS-01 establishes the design baseline for the existing ZEN syntax
architecture before further syntax design begins.

Its objectives are to:

1. Identify the official language and grammar identity.
2. Record the existing grammar and lexical rules.
3. Establish the relationship between grammar, Lexer, Parser, and AST.
4. Distinguish implemented infrastructure from unimplemented components.
5. Separate syntax rules from semantic and runtime behavior.
6. Establish principles for future ZSS design.
7. Prevent undocumented or unauthorized language changes.

This document summarizes the existing baseline. It does not replace
or modify the official language specification.

## 2. Language Identity

| Layer | Identity | Status |
|---|---|---|
| Programming language | ZEN / Zen | Existing |
| Syntax design workstream | ZSS — Zen Structured Syntax | Project designation |
| Formal grammar | Zen Language Specification v0.1.0 | Specified |
| Lexical architecture | Zen Lexer | Implemented |
| Abstract syntax tree | Canonical Zen AST | Implemented |
| AST structural validation | ZASI foundation | Implemented |
| AST fingerprint | ZIIF-01 | Existing |
| Parser | Zen Parser | Not implemented |
| Semantic analysis | Zen Semantic Analysis | Not implemented |
| Interpreter/runtime | Zen Runtime | Not implemented |

ZSS is the engineering workstream responsible for designing and
maintaining ZEN's syntax architecture.

ZSS does not independently change the authority of the official grammar.

## 3. Official Language Characteristics

According to `docs/03-language-specification.md`:

| Area | Official v0.1 decision |
|---|---|
| Language purpose | General-purpose |
| Type system | Dynamically typed |
| Execution model | Interpreted |
| Scope | Block scope |
| Error handling | Strict |
| Comments | C-style |
| Statement separators | Newline or semicolon |
| Final program statement | May end at EOF |
| Final block statement | May end before `}` |
| Variable declaration | `let` |
| Constant declaration | `const`; initializer required |
| Function declaration | `fn` |
| Conditions | Parenthesized expressions |
| Function/control-flow bodies | Braced blocks |

**Official motto:** Simple to write. Clear to understand.
Controlled to execute.

These are existing v0.1 decisions, not proposals.

## 4. Existing Syntax Inventory

### 4.1 Keywords

- `let`
- `const`
- `fn`
- `if`
- `else`
- `while`
- `true`
- `false`
- `null`
- `return`

### 4.2 Operators

| Category | Operators |
|---|---|
| Arithmetic | `+`, `-`, `*`, `/`, `%` |
| Assignment | `=` |
| Equality | `==`, `!=` |
| Comparison | `<`, `<=`, `>`, `>=` |
| Logical | `&&`, `||` |
| Unary | `!`, `-` |

### 4.3 Punctuation

- Parentheses: `(`, `)`
- Braces: `{`, `}`
- Brackets: `[`, `]`
- Comma: `,`
- Colon: `:`
- Semicolon: `;`

The Lexer recognizes square brackets and colon, but the official
grammar does not define array, indexing, type-annotation, or object
syntax.

Lexical recognition must not be interpreted as official language support.

## 5. Formal Grammar Characteristics

The official specification defines v0.1 concrete syntax using EBNF.

It covers:

- Program and block structure.
- Variable declarations.
- Function declarations and parameters.
- Conditional statements.
- Loops.
- Return statements.
- Expression statements.
- Expression precedence and associativity.
- Function calls and grouping.
- Assignment restrictions.
- Newline behavior.
- `else` binding.
- Valid and invalid examples.

### 5.1 Statement Boundaries

Established rules:

1. Newline and semicolon are statement separators.
2. Repeated separators are permitted.
3. Repeated separators do not create empty statements.
4. The final program statement may end at EOF.
5. The final block statement may end immediately before `}`.
6. Two statements on the same line require a semicolon between them.

### 5.2 Newline Behavior

Newline is not universally whitespace.

Inside specified parenthesized expressions, parameter lists, and
argument lists, newlines act as whitespace.

In other statement contexts, newline acts as a statement separator.

A newline does not independently continue an expression. An operator
at the end of a line does not automatically continue that expression.

### 5.3 Conditional Behavior

- `if` requires a parenthesized condition.
- `while` requires a parenthesized condition.
- Both require braced bodies.
- `else` may follow a then-block after zero or more newlines.
- A semicolon cannot separate a then-block from `else`.
- `else` binds to the nearest preceding unmatched `if`.
- `else if` is supported by the grammar.

### 5.4 Expression Precedence and Associativity

The grammar defines precedence from lowest to highest:

| Level | Expression form | Associativity |
|---:|---|---|
| 1 | Assignment `=` | Right |
| 2 | Logical OR `||` | Left |
| 3 | Logical AND `&&` | Left |
| 4 | Equality `==`, `!=` | Left |
| 5 | Comparison `<`, `<=`, `>`, `>=` | Left |
| 6 | Addition and subtraction | Left |
| 7 | Multiplication, division, modulo | Left |
| 8 | Unary `!`, `-` | Right |
| 9 | Function calls | Left |
| 10 | Primary expressions | — |

Assignment targets are restricted to bare identifiers.

Chained assignment is right-associative.

Function-call suffixes may be chained.

The grammar determines syntactic grouping, not runtime evaluation
behavior.

### 5.5 Grammar Authority

The complete EBNF and official examples in
`docs/03-language-specification.md` remain authoritative.

This document summarizes the baseline and does not reproduce or
replace the complete grammar.

## 6. Existing Architecture

The intended processing architecture is:

**Source Code → Lexer → Parser → AST → Semantic Analysis
→ Interpreter → Runtime**

### 6.1 Lexer — Implemented

The Lexer is responsible for:

- Token recognition.
- Keyword recognition.
- Operator and punctuation recognition.
- Identifier processing.
- Numeric literal processing.
- String and escape processing.
- Comment processing.
- Newline recognition.
- Lexical error reporting.
- Lexical resource limits.

It recognizes LF, CRLF, and CR line endings.

The Lexer enforces source, identifier, string, comment, token-count,
and numeric-literal limits.

### 6.2 Parser — Not Implemented

The formal grammar is specified, but the complete Parser is not
implemented.

Existing foundations include:

- `ParseContext`: immutable parser accounting for nesting depth
  and AST node count.
- `ParseError`: source-located parser error representation.

These foundations do not constitute a grammar parser.

They do not prove end-to-end parsing or grammar conformance.

### 6.3 AST — Implemented

The canonical AST model contains 15 node types.

It uses immutable node structures with source spans.

The AST represents program structure independently from the Parser
implementation.

### 6.4 AST Validation — Implemented

AST validation checks:

- Root and node types.
- Child types.
- Collection constraints.
- Source identity.
- Source spans.
- Parent-child span containment.
- Sibling ordering.
- Graph cycles.
- Reused node objects.
- Structural resource limits.
- Function declaration metadata.

AST validation does not replace grammar parsing.

## 7. Grammar-to-AST Correspondence

The intended correspondence between the official grammar and the
existing AST model is:

| Grammar construct | AST node |
|---|---|
| Program | `Program` |
| Variable declaration | `VarDecl` |
| Function declaration | `FunctionDecl` |
| Block | `BlockStmt` |
| If / else | `IfStmt` |
| While | `WhileStmt` |
| Return | `ReturnStmt` |
| Expression statement | `ExpressionStmt` |
| Literal | `LiteralExpr` |
| Identifier | `IdentifierExpr` |
| Grouping | `GroupingExpr` |
| Prefix operator | `UnaryExpr` |
| Binary operator | `BinaryExpr` |
| Assignment | `AssignExpr` |
| Function call | `CallExpr` |

Important structural contracts:

- `AssignExpr.target` is an `IdentifierExpr`, matching the grammar's
  bare-identifier restriction.
- `CallExpr` stores its callee as an expression and its arguments
  as a tuple.
- `IfStmt.else_branch` supports a block, another `IfStmt`, or `None`.
- For legacy construction, `FunctionDecl.name_span` and `parameter_spans` may be omitted; canonical AST validation requires both metadata fields.
- AST nodes carry source spans. During legacy construction, `source_id` may be absent; canonical AST validation requires every node to have a valid `SourceIdentifier` matching the root node's source identity.

This correspondence is a design mapping.

It does not claim that a Parser or source-to-AST pipeline exists.

## 8. Resource and Structural Constraints

Limits are separated by component responsibility.

### 8.1 Lexer Limits

| Resource | Maximum |
|---|---:|
| Source text | 2,097,152 Unicode code points |
| Identifier | 256 characters |
| Decoded string value | 1,048,576 characters |
| Single comment body | 1,048,576 source characters |
| Non-EOF tokens | 262,144 |
| Integer literal | 1,024 digits |
| Float literal | 1,024 digits, excluding decimal point |

The Lexer rejects inputs exceeding these limits rather than silently
truncating them.

Token count includes emitted non-EOF tokens, including preserved
newline tokens from block comments.

### 8.2 Parser Accounting Limits

| Resource | Maximum |
|---|---:|
| Parser nesting depth (`MAX_PARSER_DEPTH`) | 256 |
| Parser AST node accounting (`MAX_AST_NODES`) | 1,000,000 |

`ParseContext` provides these accounting primitives.

Their existence does not prove that a complete Parser enforces them.

### 8.3 AST Validation Limits

| Resource | Maximum |
|---|---:|
| Total AST nodes | 1,000,000 |
| AST structural depth | 256 |
| Direct children per collection | 262,144 |
| Expression nodes | 262,144 |
| Statement nodes | 262,144 |
| Function parameters | 262,144 |

AST structural depth and Parser nesting depth are separate
measurements, even though their current configured ceilings are equal.

The canonical AST must be a finite tree.

Cycles and reuse of the same node object at multiple child locations
are invalid.

Child spans must be contained by their parent spans, and sibling
spans must be ordered and non-overlapping.

The Parser must later enforce its parsing and construction limits
and report source-located syntax/resource diagnostics.

AST validation enforces its own structural contract.

## 9. Syntax, Semantics, and Runtime Boundaries

This separation is fundamental to ZEN architecture.

### 9.1 Syntax

Syntax determines whether source code follows the official grammar.

Examples:

- Declaration structure.
- Function-call structure.
- Valid parentheses and braces.
- Permitted assignment targets.

### 9.2 Semantics

Semantics determines whether a syntactically valid program has
valid meaning.

Decisions requiring explicit semantic specification include:

- Reading an uninitialized variable.
- Constant reassignment.
- Variable redeclaration.
- Name resolution.
- Scope lookup.
- Function argument-count validation.
- Returning outside a function.

### 9.3 Runtime

Runtime defines execution behavior.

Examples requiring explicit runtime decisions include:

- Logical short-circuit behavior.
- Truthiness.
- Type coercion.
- Division by zero.
- Equality across different value types.
- Whether a runtime value is callable.

A Parser must not silently decide semantic or runtime behavior.

## 10. Established Decisions and Unresolved Questions

### 10.1 Established Decisions

- Dynamically typed language.
- Interpreted execution model.
- Block scope.
- Strict error handling.
- `const` requires initialization.
- Braced function and control-flow bodies.
- Explicit expression precedence and associativity.
- Identifier-only assignment targets.
- Canonical 15-node AST model.
- Source identity and source span contracts.
- Explicit lexical, parser-accounting, and AST structural limits.

### 10.2 Unresolved Semantic and Runtime Questions

1. Exact redeclaration behavior.
2. Uninitialized variable read behavior.
3. Constant reassignment semantics.
4. Name resolution rules.
5. Function arity validation.
6. Logical short-circuit evaluation.
7. Truthiness rules.
8. Type coercion.
9. Division-by-zero behavior.
10. Cross-type equality behavior.
11. Runtime callability rules.

These are not missing grammar productions.

They require explicit decisions in their appropriate architectural layer.

## 11. ZSS Design Principles

Future ZSS architecture must preserve the following principles.

### 11.1 Explicitness

Every official language rule must be documented.

The compiler must not invent missing rules.

### 11.2 Determinism

The same valid source structure must have a predictable
syntactic interpretation.

### 11.3 Unambiguity

Grammar must not leave unresolved competing syntactic interpretations.

### 11.4 Traceability

Every syntax construct must be traceable to:

- An official grammar production.
- A lexical representation.
- An intended AST representation.
- A documented semantic boundary.

### 11.5 Accountability

Every rule must have a clear authority.

Every structural contract must have a defined validation
responsibility.

Every implementation claim must have evidence.

### 11.6 Compatibility

New syntax proposals must account for existing grammar, Lexer,
AST, and ZIIF contracts.

### 11.7 AI Understandability

Specifications should be structured so humans, compilers,
development tools, and AI agents can interpret them consistently.

AI interpretation is not authority to override official specifications.

## 12. Security and Reliability Principles

The language specification establishes that:

- Zen source must not be executed using Python `eval()` or `exec()`.
- Early runtimes must not expose unrestricted shell, filesystem,
  or network access.
- A restricted interpreter must not automatically be described
  as a secure operating-system sandbox.

Future ZSS design must preserve the distinction between
language-level safety and operating-system isolation.

## 13. Scope Restrictions

ZSS-01 does not authorize:

- Replacing Grammar v0.1.0.
- Adding new official syntax.
- Changing Lexer behavior.
- Implementing the Parser.
- Changing AST node definitions.
- Changing AST validation contracts.
- Changing ZIIF-01.
- Implementing semantic analysis.
- Implementing the interpreter or runtime.
- Changing governance documents.
- Changing production code.

Any such work requires a separate design decision and explicit
Owner authorization.

## 14. Future Design Direction

Future ZSS work must build on this baseline rather than bypass it.

Candidate design areas include:

- Syntax architecture.
- Grammar conformance.
- Syntax-to-AST traceability.
- Semantic boundaries.
- Language evolution and compatibility.
- AI-readable language specifications.

These are design areas only.

They do not authorize implementation or establish approved
future milestones.

## 15. Acceptance

- [x] Official grammar source identified.
- [x] Existing language characteristics documented.
- [x] Lexer implementation status identified.
- [x] Parser accounting foundations distinguished from Parser
      implementation.
- [x] Canonical AST correspondence documented.
- [x] AST validation responsibilities documented.
- [x] Resource limits separated by responsibility.
- [x] Syntax, semantics, and runtime boundaries documented.
- [x] Established decisions separated from unresolved questions.
- [x] No new official syntax introduced.
- [x] No implementation or governance change included.
- [x] Owner approval received.

---

**End of ZSS-01 — Grammar Baseline & Design Foundation**

**Authority:** This document records the Owner-approved ZSS-01
design baseline. It does not supersede the official language
specification or authorize implementation outside its stated scope.
