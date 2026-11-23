# ZSS-03 — Grammar Conformance Design

**Document ID:** ZSS-03  
**Title:** Grammar Conformance Design  
**Revision:** 2  
**Status:** DRAFT — AWAITING OWNER REVIEW  
**Project:** ZEN — Zen Structured Syntax (ZSS)  
**Scope:** Specification and verification design (documentation only)  
**Implementation:** NOT AUTHORIZED  
**Parser implementation:** NOT AUTHORIZED  
**Grammar change:** NOT AUTHORIZED  

**Normative grammar authority:** Zen Language Specification v0.1.0  
(`docs/03-language-specification.md`)  

**Baseline references:**  
- ZSS-01 — Grammar Baseline & Design Foundation (OWNER-APPROVED design baseline merged into main; preserve unchanged)  
- ZSS-02 — Governance, Rule Lifecycle & Compatibility (see §3.1 for precise authority status of the on-disk file)

---

## 1. Purpose

ZSS-03 defines how an implementation of the Zen Parser (and related
syntax pipeline components) can **demonstrate conformance** with the
approved Zen v0.1 grammar.

It establishes:

1. The inventory of grammar productions that must be exercised.
2. Positive and negative syntax test requirements.
3. Grammar-to-AST correspondence verification rules.
4. Operator precedence and associativity verification.
5. Statement separator, newline, and block-boundary rules.
6. Nested conditional and `else`-association rules.
7. Assignment parsing boundaries.
8. Strict component responsibility boundaries (Lexer / Parser / AST / ZASI / Semantic Analysis).
9. Parser diagnostics, source span, and source identity requirements.
10. Resource-limit and adversarial syntax testing.
11. A conformance verification matrix with **per-production** traceability.
12. Evidence collection and acceptance criteria.

ZSS-03 is a **design and verification specification**. It does not
implement a parser, change the grammar, or alter production code.

---

## 2. Scope and Non-Goals

### 2.1 In scope

- Design of grammar conformance verification for Zen v0.1.
- Traceability from each official grammar production to designed
  conformance cases.
- Explicit separation of Lexer, Parser, AST, ZASI, and Semantic Analysis
  responsibilities for conformance claims.
- Resource-boundary and adversarial syntax test design.
- Acceptance criteria and evidence classification for future parser work.

### 2.2 Out of scope (explicitly NOT authorized by this document)

- Parser implementation.
- Lexer modification.
- AST node definition changes.
- ZASI / validation contract changes.
- Semantic analysis implementation.
- Runtime or interpreter work.
- Grammar production changes.
- Resource-limit increases.
- Changes to AGENTS.md, AI_RULES.yaml, RULES.md, or SECURITY.md.
- CI configuration changes.
- Any production code modification.
- Modification of ZSS-01 or ZSS-02 source documents.

### 2.3 Relationship to other workstreams

- ZSS-01 remains the immutable design baseline for existing syntax architecture.
- ZSS-02 material is used as a **governance reference** under the constraints
  in §3.1; ZSS-03 does not rewrite or re-approve ZSS-02.
- ZB-07 and ZIIF-01 remain PAUSED; their existing contracts must be preserved
  and are not modified by ZSS-03.
- Future independently governed ZEN subsystems must not be coupled to
  ZSS-03 internal verification machinery.

---

## 3. Normative References

| Reference | Role |
|---|---|
| `docs/03-language-specification.md` (v0.1.0) | **Sole normative grammar authority** |
| `docs/engineering/ZSS-01_GRAMMAR_BASELINE.md` | Approved design baseline; must remain unchanged |
| `docs/engineering/ZSS-02_GOVERNANCE_RULE_LIFECYCLE_COMPATIBILITY.md` | Governance reference material (see §3.1) |
| `docs/architecture/boundaries.md` | Component ownership boundaries |
| `AGENTS.md`, `AI_RULES.yaml`, `RULES.md`, `SECURITY.md` | Project governance and security |
| `src/zen/limits.py` | Declared numeric ceilings (AST / parser accounting) |
| `src/zen/parser/context.py`, `diagnostics.py` | Existing parser scaffolding (not a complete parser) |

All conformance claims must be traceable to the official grammar in the
language specification. ZSS-01 summaries are supporting design records;
they do not replace the EBNF.

### 3.1 ZSS-02 authority status (evidence-based)

The on-disk file `docs/engineering/ZSS-02_GOVERNANCE_RULE_LIFECYCLE_COMPATIBILITY.md`
carries the status label **REVIEW REQUIRED — RECONSTRUCTED DRAFT** and
states that its current wording has **not** been verified as a verbatim
copy of any Owner-approved Revision 2 text.

Therefore ZSS-03 distinguishes:

1. **Historical design direction** for ZSS-02 governance topics, as
   reflected in AGENTS.md / AI_RULES.yaml active-milestone entries
   (Owner-approved workstream framing).
2. **Approval status of an original ZSS-02 specification** (not re-proven
   by this document).
3. **Verification status of the exact reconstructed file** currently in
   the repository: **not verified as final sealed text**.

ZSS-03 uses the available ZSS-02 material as a **governance reference**
for principles (rule identity, lifecycle concepts, Grammar Version
immutability direction, directional compatibility, migration governance
separation). It does **not** claim that the exact reconstructed file has
received final approval of its current wording.

ZSS-03 does not modify the ZSS-02 file. Any resolution of the
reconstructed-draft status is Owner-owned work outside this document.

---

## 4. Definitions

| Term | Definition |
|---|---|
| **Grammar conformance** | Observable behavior of a Parser (and its token consumer) that accepts exactly the language defined by the v0.1 EBNF and rejects inputs outside that language, with correct structure, precedence, associativity, and source mapping. |
| **Positive syntax case** | Source that the grammar accepts; a conforming parser must accept it and produce a corresponding valid AST structure. |
| **Negative syntax case** | Source that the grammar rejects; a conforming parser must reject it with a source-located syntax diagnostic and must not produce a successful Program AST for that input. |
| **Grammar production inventory** | The complete set of v0.1 EBNF productions that must be covered by positive and/or negative tests. |
| **Designed case** | A conformance case specified in this document; not yet executed. Status remains **NOT_TESTED** until a parser exists and tests run. |
| **Component boundary** | The exclusive ownership of a responsibility by Lexer, Parser, AST, ZASI, Semantic Analysis, or Runtime. |
| **Evidence classification** | One of: OBSERVED, DERIVED, ASSUMED, UNKNOWN, NOT_TESTED (per AGENTS.md / RULES.md). |
| **Parser scaffolding** | Existing `ParseContext` and `ParseError` foundations; these do **not** constitute a grammar parser. |

---

## 5. Architectural Principles for Conformance

### 5.1 Grammar authority

The approved Zen Language Specification v0.1.0 is the sole normative
source of syntax. No conformance document, test suite, or implementation
may introduce new syntax or silently reinterpret existing productions.

If precedence, associativity, newline behavior, separators, or `else`
association appears ambiguous relative to the EBNF:

1. Record the ambiguity.
2. Identify the affected production(s).
3. Explain impact on parsing and AST shape.
4. Mark the item **UNRESOLVED**.
5. Request Owner / specification-authority clarification.

**Do not guess.**

### 5.2 Component responsibility boundaries

| Component | Owns | Does not own |
|---|---|---|
| **Lexer** | Character/token recognition, lexical limits, NEWLINE emission, lexical diagnostics | Grammatical structure, statement boundaries, AST construction |
| **Parser** | Grammatical structure, production matching, precedence/associativity, statement/block boundaries, `else` association, assignment disambiguation, parser nesting/node accounting, syntax diagnostics with source location | Lexical validity, semantic meaning, runtime behavior, silent AST repair |
| **AST** | Immutable canonical node data, declared structural contracts (child types, spans, ordering) | Proof that source matched the grammar |
| **ZASI / AST validation** | Structural integrity of a constructed AST (types, cycles, reuse, span containment, structural limits) | Source grammar conformance |
| **Semantic Analysis** | Meaning of a validated AST (names, scopes, arity, etc.) | Syntax acceptance/rejection |
| **Runtime** | Execution of a semantically valid program | Syntax or structural validation |

**Critical rule:** AST validation proving structural integrity of a tree
does **not** prove that the tree was produced by a grammar-conformant
parse of source text. Grammar conformance is a Parser responsibility.

### 5.3 Security and resource safety

Existing resource ceilings must be preserved. Conformance testing must
include boundary cases at or beyond limits without raising those limits
to obtain a pass. See Section 14.

---

## 6. Grammar Production Inventory

The following productions are taken from `docs/03-language-specification.md`
§5. Each production has a stable **Production ID** used in the
conformance matrix (Section 15).

### 6.1 Program and separators

| Production ID | Official production name | Notes |
|---|---|---|
| G-PROG | `program` | Empty program valid; ends at EOF |
| G-SEP | `separators` | One or more NEWLINE or SEMICOLON; repeats allowed; no empty statements |
| G-STMT | `statement` | Alternatives: decl / control / return / expr-stmt |
| G-BLOCK | `block` | Empty block valid; final stmt may end before `}` |

### 6.2 Declarations and control flow

| Production ID | Official production name | Notes |
|---|---|---|
| G-VAR | `variable_declaration` | `let` optional init; `const` requires init |
| G-FN | `function_declaration` | `fn` name (params) block |
| G-PARAMS | `parameter_list` | Identifiers, comma-separated; no trailing comma; no defaults |
| G-IF | `if_statement` | Parenthesized condition + block; optional else |
| G-ELSE-NL | `else_newlines` | Zero or more NEWLINE only |
| G-WHILE | `while_statement` | Parenthesized condition + block |
| G-RETURN | `return_statement` | Optional expression; expression must start before next separator/EOF/`}` |
| G-EXPR-STMT | `expression_statement` | Bare expression |

### 6.3 Expressions (precedence ladder)

| Production ID | Official production name | Associativity / notes |
|---|---|---|
| G-EXPR | `expression` | = `assignment` |
| G-ASSIGN | `assignment` | Right-assoc; target = bare IDENTIFIER only |
| G-OR | `logical_or` | Left |
| G-AND | `logical_and` | Left |
| G-EQ | `equality` | Left (`==` `!=`) |
| G-CMP | `comparison` | Left (`<` `<=` `>` `>=`) |
| G-TERM | `term` | Left (`+` `-`) |
| G-FACTOR | `factor` | Left (`*` `/` `%`) |
| G-UNARY | `unary` | Right (`!` `-`) |
| G-CALL | `call` | Left; chainable |
| G-ARGLIST | `argument_list` | `( [arguments] )` |
| G-ARGS | `arguments` | expression { `,` expression }; no trailing comma |
| G-PRIMARY | `primary` | Literals, IDENTIFIER, grouping |

### 6.4 Lexical tokens relevant to syntax

Conformance tests may assume a correct Lexer for tokens listed in the
specification. Lexer non-conformance is out of scope for ZSS-03 grammar
conformance claims, but negative tests that surface as lexical errors
must be classified separately (lexical vs syntactic rejection).

---

## 7. Positive Syntax Test Cases (Design Requirements)

A conforming implementation must accept at least the following categories.
Exact fixtures are **designed** requirements; implementation of the test
suite is not authorized by this document. Case IDs (P-*) map into the
matrix in Section 15.

### 7.1 Minimal and empty forms

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-PROG-01 | Empty program (optional separators then EOF) | `program` |
| P-BLOCK-01 | Empty block `{ }` | `block` |
| P-BLOCK-02 | Block with only separators then `}` | `block` |
| P-EXPR-STMT-01 | Single expression statement ending at EOF | `expression_statement` |
| P-EXPR-STMT-02 | Single expression statement ending before `}` | `expression_statement` |

### 7.2 Declarations

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-VAR-01 | `let` without initializer | `variable_declaration` |
| P-VAR-02 | `let` with initializer | `variable_declaration` |
| P-VAR-03 | `const` with initializer | `variable_declaration` |
| P-VAR-04 | Nested declarations inside blocks | `variable_declaration`, `block` |
| P-FN-01 | Function with zero parameters | `function_declaration` |
| P-FN-02 | Function with one parameter | `function_declaration`, `parameter_list` |
| P-FN-03 | Function with multiple parameters (no trailing comma) | `function_declaration`, `parameter_list` |

### 7.3 Control flow

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-IF-01 | `if (cond) { }` without else | `if_statement` |
| P-IF-02 | `if (cond) { } else { }` | `if_statement` |
| P-IF-03 | `if (cond) { } else if (cond2) { }` | `if_statement` |
| P-IF-04 | `if … else if … else { }` | `if_statement` |
| P-ELSE-NL-01 | Zero or more NEWLINE between then-block `}` and `else` | `else_newlines` |
| P-WHILE-01 | `while (cond) { }` | `while_statement` |
| P-NEST-01 | Nested if/while inside blocks | `if_statement`, `while_statement`, `block` |

### 7.4 Return

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-RET-01 | `return` with no expression, ended by NEWLINE / SEMICOLON / `}` / EOF | `return_statement` |
| P-RET-02 | `return` with expression beginning before next separator | `return_statement` |

### 7.5 Expressions — precedence and associativity

| Case ID | Designed positive input (summary) | Primary production(s) |
|---|---|---|
| P-ASSIGN-01 | `a = b = 3` right-associative | `assignment` |
| P-OR-01 | `a || b || c` left-associative | `logical_or` |
| P-AND-01 | `a && b && c` left-associative | `logical_and` |
| P-EQ-01 | Equality chain left-associative | `equality` |
| P-CMP-01 | Comparison chain left-associative | `comparison` |
| P-TERM-01 | `a + b - c` left-associative | `term` |
| P-FACTOR-01 | `a * b / c % d` left-associative | `factor` |
| P-UNARY-01 | `!!x`, `--x` as stacked unaries (right-assoc) | `unary` |
| P-CALL-01 | `f()()` chained calls | `call`, `argument_list` |
| P-ARGS-01 | Multi-argument call without trailing comma | `arguments` |
| P-PRIMARY-01 | Literals, identifier, `(a + b)` grouping | `primary` |
| P-MIX-01 | Mixed precedence e.g. `a + b * c`, `!a && b`, `-f()` | multiple expression productions |

### 7.6 Newlines as whitespace inside lists

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-NL-01 | Parenthesized grouping with internal newlines | `primary` (grouping) |
| P-NL-02 | Parameter list with internal newlines | `parameter_list` |
| P-NL-03 | Argument list with internal newlines | `argument_list`, `arguments` |

### 7.7 Separators

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-SEP-01 | Multiple consecutive NEWLINE and/or SEMICOLON between statements | `separators` |
| P-SEP-02 | Two statements on one line separated by SEMICOLON | `separators`, `statement` |
| P-SEP-03 | Final statement without trailing separator before EOF or `}` | `program`, `block` |

### 7.8 Official valid examples

| Case ID | Designed positive input (summary) | Primary production |
|---|---|---|
| P-SPEC-01 | Valid examples from language specification §5.7 | multiple |

---

## 8. Negative Syntax Test Cases (Design Requirements)

A conforming parser must reject the following categories with a
source-located syntax diagnostic and must not return a successful
`Program` AST for the input. Case IDs (N-*) map into Section 15.

### 8.1 Declaration and parameter errors

| Case ID | Designed negative input (summary) | Primary production |
|---|---|---|
| N-VAR-01 | `const` without initializer | `variable_declaration` |
| N-PARAMS-01 | Parameter list with trailing comma | `parameter_list` |
| N-IF-01 | Missing parentheses around `if` condition | `if_statement` |
| N-IF-02 | Missing braces for `if` body | `if_statement` |
| N-WHILE-01 | Missing parentheses around `while` condition | `while_statement` |
| N-WHILE-02 | Missing braces for `while` body | `while_statement` |
| N-FN-01 | Missing braces for function body | `function_declaration` |

### 8.2 Statement boundary errors

| Case ID | Designed negative input (summary) | Primary production |
|---|---|---|
| N-SEP-01 | Two statements on the same line without SEMICOLON | `separators`, `statement` |
| N-ELSE-01 | SEMICOLON between then-block and `else` | `if_statement`, `else_newlines` |

### 8.3 Assignment boundary errors

| Case ID | Designed negative input (summary) | Primary production |
|---|---|---|
| N-ASSIGN-01 | `(a) = 1` | `assignment` |
| N-ASSIGN-02 | `f() = 1` | `assignment` |
| N-ASSIGN-03 | `1 = 2` | `assignment` |
| N-ASSIGN-04 | `a + b = 3` | `assignment` |

These must fail at parse time (grammar restriction), not only at
semantic analysis.

### 8.4 Expression / call errors

| Case ID | Designed negative input (summary) | Primary production |
|---|---|---|
| N-ARGS-01 | Trailing comma in argument list | `arguments` |
| N-BAL-01 | Unbalanced parentheses or braces | multiple |
| N-TOK-01 | Unexpected token where a production requires a specific token | multiple |

### 8.5 Official invalid examples

| Case ID | Designed negative input (summary) | Primary production |
|---|---|---|
| N-SPEC-01 | Invalid examples from language specification §5.7 | multiple |

### 8.6 Return expression boundary

| Case ID | Designed negative / boundary input (summary) | Primary production |
|---|---|---|
| N-RET-01 | Newline immediately after `return` ends the return; following line is not part of the return expression | `return_statement` |

### 8.7 Productions without a meaningful standalone negative case

Some productions are pure structure or pure positive grouping rules.
For those, the matrix records **N/A — no distinct standalone negative**
rather than inventing an invalid rule:

- `expression` (alias of `assignment` entry)
- Individual binary levels may share negative coverage via unbalanced
  operators / unexpected tokens (N-TOK-01) rather than a unique
  production-specific negative

### 8.8 Classification note

If rejection occurs in the Lexer (e.g. unknown escape, unterminated
string, resource limit), the case is **lexical rejection**, not grammar
conformance failure. Grammar-negative tests assume a successful token
stream up to the syntactic error, or document the expected phase.

---

## 9. Grammar-to-AST Correspondence

The intended mapping is fixed by the language specification §5.5 and
ZSS-01 §7. Conformance requires that a successful parse produce nodes
of the following kinds (names as in `src/zen/ast/nodes.py`):

| Grammar construct | AST node |
|---|---|
| Program | `Program` |
| Variable declaration | `VarDecl` |
| Function declaration | `FunctionDecl` |
| Block | `BlockStmt` |
| if / else | `IfStmt` |
| while | `WhileStmt` |
| return | `ReturnStmt` |
| Expression statement | `ExpressionStmt` |
| Literal | `LiteralExpr` |
| Identifier | `IdentifierExpr` |
| Grouping | `GroupingExpr` |
| Prefix operator | `UnaryExpr` |
| Binary operator | `BinaryExpr` |
| Assignment | `AssignExpr` |
| Function call | `CallExpr` |

**Structural contracts that conformance tests must verify:**

- `AssignExpr.target` is always `IdentifierExpr`.
- `IfStmt.else_branch` is `BlockStmt`, `IfStmt`, or `None`.
- `CallExpr` callee is an expression; arguments are an ordered sequence.
- Node spans are half-open; child spans contained in parent; siblings
  ordered and non-overlapping (per existing AST contracts).

AST structural validation (ZASI) may be used **after** a successful parse
to check integrity. It must not be used as a substitute for proving that
the source matched the grammar.

---

## 10. Operator Precedence and Associativity

Normative table (from language specification; parsing/grouping only):

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

Conformance requires positive tests that observe the resulting AST shape
(or an equivalent structured parse tree) matching this table. Runtime
evaluation order, short-circuiting, and type behavior are **not**
grammar-conformance concerns.

---

## 11. Statement Separators, Newlines, Blocks, Conditionals, Assignment

### 11.1 Statement separators

- Separators = one or more of NEWLINE or SEMICOLON.
- Repeated separators do not create empty statements.
- Final program statement may end at EOF.
- Final block statement may end immediately before `RIGHT_BRACE`.
- Two statements on the same line require a SEMICOLON between them.

### 11.2 Newline behavior

- At statement level: NEWLINE is a separator.
- Inside parenthesized expressions, parameter lists, and argument lists:
  NEWLINE is whitespace.
- A newline does **not** continue an expression outside those contexts.
- An operator at end-of-line does **not** by itself continue the expression.
- SEMICOLON is never treated as whitespace inside those lists.

### 11.3 Block boundaries

- Empty blocks are valid.
- Closing brace ends the final statement without requiring an extra separator.

### 11.4 Nested conditionals and `else` association

- `else` binds to the nearest preceding `if` that does not already have an `else`.
- Zero or more NEWLINE tokens may appear between the then-block’s closing
  brace and `else`.
- A SEMICOLON in that position is invalid.
- After parsing an `if` then-block, the parser must check for `else` **before**
  consuming intervening newlines as ordinary statement separators.
- `else if` is supported via `else` followed by `if_statement`.

### 11.5 Assignment parsing boundaries

- Assignment target is a bare IDENTIFIER only.
- Disambiguation: if current token is IDENTIFIER and the **immediately
  following** token is ASSIGN, parse assignment; otherwise parse as
  logical expression.
- The parser must **not** skip NEWLINE or SEMICOLON during this one-token
  lookahead decision.
- Chained assignment is right-associative.

### 11.6 Return expression boundary

- Optional expression after `return` must begin before the next NEWLINE,
  SEMICOLON, RIGHT_BRACE, or EOF.
- A newline immediately after `return` ends the return statement.

---

## 12. Lexer / Parser / AST Validation Boundaries (Conformance View)

| Concern | Responsible component | Conformance implication |
|---|---|---|
| Token forms, NEWLINE emission, lexical limits | Lexer | Assumed correct for pure syntax tests; lexical failures classified separately |
| Production matching, structure, precedence, separators, else, assignment lookahead | Parser | Core of grammar conformance |
| Node types, span containment, sibling order, structural limits, cycles/reuse | AST + ZASI | Post-parse integrity only; not proof of source grammar match |
| Names, scopes, arity, const assignment, callability | Semantic Analysis | Out of grammar conformance scope |

**Forbidden claims:**

- “AST validation passed ⇒ grammar conformant.”
- “Lexer accepted the tokens ⇒ program is syntactically valid.”
- Moving grammar enforcement into generic AST validation.

---

## 13. Parser Diagnostics, Source Span, and Source Identity

### 13.1 Diagnostics

- Every syntax rejection must produce a source-located diagnostic.
- Existing scaffolding: `ParseError` (message, line, column, optional span,
  optional source_id) and `as_diagnostic()` mapping to component `"Parser"`.
- Exact diagnostic **code catalog** and recovery strategy remain to be
  specified with parser implementation; ZSS-03 requires only that failures
  are located and attributed to the Parser.
- Strict error handling (language specification §7): first syntax error
  stops the current program parse; silent skipping of malformed input is
  forbidden.

### 13.2 Source spans

- Half-open coordinates: start inclusive, end exclusive.
- Parser implementation must define and test how token positions combine
  into node spans (language specification §5.5).
- Child containment and sibling ordering remain AST/ZASI contracts.

### 13.3 Source identity

- Canonical AST validation requires consistent `SourceIdentifier` on nodes
  (per existing ZB-07 / AST contracts). Parser construction of AST must
  supply identity consistently with those contracts when a parser is
  implemented. ZSS-03 does not reopen ZB-07.

---

## 14. Parser Resource-Limit and Adversarial Syntax Testing

### 14.1 Declared ceilings (must not be increased by this work)

From `src/zen/limits.py` and language specification / ZSS-01:

| Limit | Value | Owner |
|---|---:|---|
| `MAX_PARSER_DEPTH` | 256 | Parser accounting |
| `MAX_AST_NODES` (parser node accounting) | 1,000,000 | Parser accounting |
| `MAX_AST_DEPTH` | 256 | AST structural |
| `MAX_DIRECT_CHILDREN` | 262,144 | AST structural |
| `MAX_EXPRESSION_NODES` | 262,144 | AST structural |
| `MAX_STATEMENT_NODES` | 262,144 | AST structural |

Lexer limits remain with the Lexer.

### 14.2 Required boundary / adversarial categories

Conformance design requires tests (when a parser exists) for:

1. Deep nesting of blocks / parentheses / calls approaching `MAX_PARSER_DEPTH`.
2. Nesting that exceeds `MAX_PARSER_DEPTH` → located ParseError; no silent accept.
3. Large statement collections approaching collection / node ceilings.
4. Large argument / parameter collections approaching ceilings.
5. Long expression chains approaching expression-node limits.
6. Malformed nested input (unbalanced delimiters, truncated constructs).
7. Unexpected end-of-file mid-production.
8. Excessive token sequences (in cooperation with Lexer token limits).
9. Adversarial separator patterns (extreme runs of NEWLINE/SEMICOLON).
10. Adversarial `else` / newline mixtures and invalid semicolon-before-else.

**Rule:** Do not raise limits to make tests pass. Boundary tests must
demonstrate rejection or safe handling at the declared ceilings.

| Case ID | Designed boundary / adversarial focus |
|---|---|
| B-DEPTH-01 | Parser depth at ceiling |
| B-DEPTH-02 | Parser depth over ceiling → reject |
| B-NODES-01 | Node-count at ceiling |
| B-NODES-02 | Node-count over ceiling → reject |
| B-ADV-01 | Malformed nesting / unexpected EOF |
| B-ADV-02 | Extreme separator runs |
| B-ADV-03 | Adversarial else/newline/semicolon mixtures |

---

## 15. Conformance Verification Matrix

### 15.1 Status and evidence conventions

| Status value | Meaning |
|---|---|
| **DESIGNED** | Case specified in this document; no execution yet |
| **NOT_TESTED** | No relevant test executed against a parser implementation |
| **PASS** / **FAIL** / **BLOCKED** | Reserved for future OBSERVED execution evidence |
| **N/A** | Not applicable (documented limitation, not a missing invention) |

Evidence labels remain: **OBSERVED**, **DERIVED**, **ASSUMED**, **UNKNOWN**, **NOT_TESTED**.

A row marked DESIGNED + NOT_TESTED means the case is specified but has
never been executed. It is **not** verification evidence.

### 15.2 Per-production traceability matrix

Each official production has explicit positive case ID(s), negative case
ID(s) where applicable, expected syntactic outcome, and verification status.

| Prod. ID | Official production | Positive case IDs | Negative case IDs | Expected syntactic outcome | Status |
|---|---|---|---|---|---|
| G-PROG | `program` | P-PROG-01, P-SEP-03, P-SPEC-01 | N-SEP-01, N-SPEC-01, N-BAL-01 | Accept empty/non-empty program ending at EOF; reject malformed top-level structure | DESIGNED / NOT_TESTED |
| G-SEP | `separators` | P-SEP-01, P-SEP-02, P-SEP-03 | N-SEP-01 | Accept ≥1 NEWLINE/SEMICOLON repeats; no empty statements; reject same-line stmts without `;` | DESIGNED / NOT_TESTED |
| G-STMT | `statement` | P-VAR-*, P-FN-*, P-IF-*, P-WHILE-01, P-RET-*, P-EXPR-STMT-* | N-SEP-01, N-SPEC-01 | Accept each statement alternative; reject invalid statement boundaries | DESIGNED / NOT_TESTED |
| G-BLOCK | `block` | P-BLOCK-01, P-BLOCK-02, P-VAR-04, P-NEST-01 | N-IF-02, N-WHILE-02, N-FN-01, N-BAL-01 | Accept empty/non-empty blocks; final stmt may end before `}` | DESIGNED / NOT_TESTED |
| G-VAR | `variable_declaration` | P-VAR-01, P-VAR-02, P-VAR-03, P-VAR-04 | N-VAR-01 | Accept `let` ± init and `const` with init; reject `const` without init | DESIGNED / NOT_TESTED |
| G-FN | `function_declaration` | P-FN-01, P-FN-02, P-FN-03 | N-FN-01 | Accept `fn` name (params) block; reject missing body braces | DESIGNED / NOT_TESTED |
| G-PARAMS | `parameter_list` | P-FN-02, P-FN-03, P-NL-02 | N-PARAMS-01 | Accept comma-separated identifiers; reject trailing comma | DESIGNED / NOT_TESTED |
| G-IF | `if_statement` | P-IF-01, P-IF-02, P-IF-03, P-IF-04, P-NEST-01 | N-IF-01, N-IF-02, N-ELSE-01 | Accept parenthesized cond + block ± else; reject missing `()`/`{}`; reject `;` before else | DESIGNED / NOT_TESTED |
| G-ELSE-NL | `else_newlines` | P-ELSE-NL-01, P-IF-02 | N-ELSE-01 | Accept zero or more NEWLINE before `else`; reject SEMICOLON in that position | DESIGNED / NOT_TESTED |
| G-WHILE | `while_statement` | P-WHILE-01, P-NEST-01 | N-WHILE-01, N-WHILE-02 | Accept parenthesized cond + block; reject missing `()`/`{}` | DESIGNED / NOT_TESTED |
| G-RETURN | `return_statement` | P-RET-01, P-RET-02 | N-RET-01 | Accept optional expr starting before next separator; newline after `return` ends stmt | DESIGNED / NOT_TESTED |
| G-EXPR-STMT | `expression_statement` | P-EXPR-STMT-01, P-EXPR-STMT-02 | N-TOK-01 | Accept bare expression as statement | DESIGNED / NOT_TESTED |
| G-EXPR | `expression` | P-ASSIGN-01, P-MIX-01 | N/A — entry alias of assignment | Parses as `assignment` | DESIGNED / NOT_TESTED |
| G-ASSIGN | `assignment` | P-ASSIGN-01 | N-ASSIGN-01..04 | Right-assoc; bare IDENTIFIER target only; reject non-identifier LHS | DESIGNED / NOT_TESTED |
| G-OR | `logical_or` | P-OR-01, P-MIX-01 | N/A — covered by N-TOK-01 / N-BAL-01 when malformed | Left-associative `||` chains | DESIGNED / NOT_TESTED |
| G-AND | `logical_and` | P-AND-01, P-MIX-01 | N/A — covered by N-TOK-01 / N-BAL-01 when malformed | Left-associative `&&` chains | DESIGNED / NOT_TESTED |
| G-EQ | `equality` | P-EQ-01, P-MIX-01 | N/A — covered by N-TOK-01 / N-BAL-01 when malformed | Left-associative `==` `!=` | DESIGNED / NOT_TESTED |
| G-CMP | `comparison` | P-CMP-01, P-MIX-01 | N/A — covered by N-TOK-01 / N-BAL-01 when malformed | Left-associative comparisons | DESIGNED / NOT_TESTED |
| G-TERM | `term` | P-TERM-01, P-MIX-01 | N/A — covered by N-TOK-01 / N-BAL-01 when malformed | Left-associative `+` `-` | DESIGNED / NOT_TESTED |
| G-FACTOR | `factor` | P-FACTOR-01, P-MIX-01 | N/A — covered by N-TOK-01 / N-BAL-01 when malformed | Left-associative `*` `/` `%` | DESIGNED / NOT_TESTED |
| G-UNARY | `unary` | P-UNARY-01, P-MIX-01 | N/A — covered by N-TOK-01 when malformed | Right-associative `!` `-` | DESIGNED / NOT_TESTED |
| G-CALL | `call` | P-CALL-01, P-MIX-01 | N-ASSIGN-02 | Chainable calls; call result may be callee | DESIGNED / NOT_TESTED |
| G-ARGLIST | `argument_list` | P-CALL-01, P-ARGS-01, P-NL-03 | N-ARGS-01, N-BAL-01 | `( [arguments] )` form | DESIGNED / NOT_TESTED |
| G-ARGS | `arguments` | P-ARGS-01, P-NL-03 | N-ARGS-01 | Comma-separated expressions; no trailing comma | DESIGNED / NOT_TESTED |
| G-PRIMARY | `primary` | P-PRIMARY-01, P-NL-01 | N-BAL-01, N-TOK-01 | Literals, IDENTIFIER, grouping | DESIGNED / NOT_TESTED |

### 15.3 Cross-cutting matrix rows

| ID | Requirement | Related productions / refs | Positive | Negative / boundary | Component | Status |
|---|---|---|---|---|---|---|
| C-ELSE-BIND | `else` binds to nearest unmatched `if` | G-IF, Spec §5.3, §5.6 | P-IF-03, P-IF-04 | — | Parser | DESIGNED / NOT_TESTED |
| C-ASSIGN-LA | Assignment lookahead does not skip NL/`;` | G-ASSIGN, Spec §5.4 | P-ASSIGN-01 | — | Parser | DESIGNED / NOT_TESTED |
| C-NL-WS | NL is whitespace inside `()` / params / args | Spec §5.2, §5.6 | P-NL-01..03 | `;` inside those lists (N-TOK / design) | Parser | DESIGNED / NOT_TESTED |
| C-SPEC-POS | Official §5.7 valid examples | Spec §5.7 | P-SPEC-01 | — | Parser | DESIGNED / NOT_TESTED |
| C-SPEC-NEG | Official §5.7 invalid examples | Spec §5.7 | — | N-SPEC-01 | Parser | DESIGNED / NOT_TESTED |
| C-AST-MAP | Grammar→AST node mapping | Spec §5.5 | successful parses of P-* | — | Parser+AST | DESIGNED / NOT_TESTED |
| C-DIAG | Source-located syntax diagnostics | Spec §7 | — | all N-* | Parser | DESIGNED / NOT_TESTED |
| C-NOSKIP | No silent skip of malformed input | Spec §7 | — | N-BAL-01, N-TOK-01, B-ADV-* | Parser | DESIGNED / NOT_TESTED |
| C-DEPTH | Parser depth limit enforced | limits.py, G-* nesting | B-DEPTH-01 | B-DEPTH-02 | Parser | DESIGNED / NOT_TESTED |
| C-NODES | Parser node-count limit enforced | limits.py | B-NODES-01 | B-NODES-02 | Parser | DESIGNED / NOT_TESTED |
| C-ADV | Adversarial / malformed nesting | §14 | — | B-ADV-01..03 | Parser | DESIGNED / NOT_TESTED |
| C-BOUND | AST validation ≠ grammar proof | Boundaries §12 | Design rule | — | Process | DESIGNED (rule) |

---

## 16. Evidence Collection and Acceptance Criteria

### 16.1 Evidence rules

- A planned or designed test is **NOT_TESTED** until executed.
- Source inspection of grammar text is **OBSERVED** for the specification,
  not runtime verification of an implementation.
- Passing AST structural tests on hand-built trees does **not** count as
  grammar-conformance evidence.
- Never claim PASS without actual execution evidence against a parser
  implementation under test.
- Record exact commands, environment, and exit codes when tests are run
  (per AGENTS.md / RULES.md).

### 16.2 Acceptance criteria for ZSS-03 (this document)

ZSS-03 (design) is complete when:

1. All sections required by the Owner task brief are present.
2. Every official v0.1 production has an explicit matrix row with case IDs.
3. ZSS-02 on-disk authority status is described without overstating
   approval of the reconstructed file wording.
4. Component boundaries are consistent with AGENTS.md, RULES.md,
   boundaries.md, and ZSS-01.
5. No new syntax or grammar reinterpretation is introduced.
6. Resource ceilings are preserved; adversarial categories are specified.
7. Verification matrix and evidence rules are defined.
8. Document remains documentation-only (no production code change).

### 16.3 Acceptance criteria for a future grammar-conformant Parser

(Not authorized by this document; stated for traceability.)

A Parser implementation may be claimed grammar-conformant for v0.1 only when:

1. Per-production matrix rows and cross-cutting rows have OBSERVED
   execution evidence with PASS (or documented N/A with justification).
2. No resource limit was raised to obtain PASS.
3. Diagnostics for negative cases are source-located and Parser-attributed.
4. Successful parses produce AST shapes consistent with Section 9 and the
   precedence table.
5. Owner has explicitly authorized the implementation and the conformance
   claim review.

---

## 17. Open Issues and Unresolved Items

| ID | Item | Status | Notes |
|---|---|---|---|
| OI-01 | Exact parser diagnostic code catalog and message stability | UNRESOLVED | Deferred to parser implementation design; must remain Parser-owned |
| OI-02 | Precise algorithm for combining token spans into every AST node span | UNRESOLVED | Spec requires definition and tests at implementation time |
| OI-03 | Whether any residual ambiguity exists in interaction of `else_newlines` with following statement separators in edge multi-if layouts | ASSUMED clear by “nearest unmatched if” + “check else before consuming NL as separators”; mark UNRESOLVED if counterexample found | Do not invent resolution |
| OI-04 | Serialization of conformance evidence into a future ZEEL/ledger system | DEFERRED | ZEEL remains proposal/not implemented |
| OI-05 | Verification of exact ZSS-02 reconstructed file wording vs any Owner-sealed text | OPEN | On-disk file self-labels as reconstructed draft; ZSS-03 treats it as governance reference only (§3.1) |

No open issue in this list authorizes a grammar change.

---

## 18. Change-Control Rules

1. This document does not modify ZSS-01 or the official language specification.
2. Normative grammar changes require a new governed Grammar Version process
   under ZSS-02 **principles** (as referenced, not as a claim of sealed
   reconstructed text) and explicit Owner approval.
3. Revisions to ZSS-03 itself require Owner review; revision number must
   increase; prior revision retained in history.
4. Implementation of a parser or conformance test suite requires separate
   explicit Owner authorization beyond approval of this design document.
5. Resource-limit changes require technical justification, boundary tests,
   and Owner approval (SECURITY.md / RULES.md).
6. Conflicts between this document and the official grammar: the official
   grammar wins; this document must be corrected.
7. Conflicts with governance documents: stop and request Owner clarification.
8. ZSS-02 source file must not be silently edited by ZSS-03 work.

---

## 19. Compatibility with ZSS-01 and ZSS-02

### 19.1 ZSS-01

- Preserves language identity, production summaries, precedence table,
  separator/newline/else/assignment rules, AST correspondence, and
  resource separation.
- Does not alter the baseline or claim parser existence.
- Extends the baseline with explicit conformance verification design only.

### 19.2 ZSS-02

- Uses available ZSS-02 material as a **governance reference** under §3.1.
- Does not claim that the exact reconstructed on-disk wording is a verified
  final sealed specification text.
- Does not implement Registry, Manifest, or migration machinery.
- Does not authorize activation of new rules or versions.
- Maintains conceptual separation of Decision / Normative / Implementation
  authority as described in the reference material and AGENTS.md.

### 19.3 Ecosystem extensibility

ZSS-03 verification machinery (when later implemented) must remain modular:
conformance evidence for ZSS must not force coupling of future ZEN
subsystems to ZSS-internal test harness details.

---

## 20. Document History

| Revision | Date | Status | Summary |
|---|---|---|---|
| 1 | 2026-11-24 | DRAFT — AWAITING OWNER REVIEW | Initial Grammar Conformance Design; documentation-only |
| 2 | 2026-11-24 | DRAFT — AWAITING OWNER REVIEW | Correct ZSS-02 authority wording; expand per-production case IDs and matrix traceability |

---

**End of ZSS-03 — Grammar Conformance Design**

**Authority:** This document is a design specification for grammar
conformance verification. It does not supersede the official language
specification, does not modify ZSS-01, does not re-approve or rewrite
ZSS-02, and does not authorize parser implementation, grammar changes, or
production code modification. Owner approval is required before any
implementation phase.
