# ZSS-03 — Grammar Conformance Design

**Document ID:** ZSS-03  
**Title:** Grammar Conformance Design  
**Revision:** 1  
**Status:** DRAFT — AWAITING OWNER REVIEW  
**Project:** ZEN — Zen Structured Syntax (ZSS)  
**Scope:** Specification and verification design (documentation only)  
**Implementation:** NOT AUTHORIZED  
**Parser implementation:** NOT AUTHORIZED  
**Grammar change:** NOT AUTHORIZED  

**Normative grammar authority:** Zen Language Specification v0.1.0  
(`docs/03-language-specification.md`)  

**Baseline references:**  
- ZSS-01 — Grammar Baseline & Design Foundation (OWNER-APPROVED, preserve unchanged)  
- ZSS-02 — Governance, Rule Lifecycle & Compatibility (OWNER-APPROVED FINAL SPECIFICATION)  

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
11. A conformance verification matrix.
12. Evidence collection and acceptance criteria.

ZSS-03 is a **design and verification specification**. It does not
implement a parser, change the grammar, or alter production code.

---

## 2. Scope and Non-Goals

### 2.1 In scope

- Design of grammar conformance verification for Zen v0.1.
- Traceability from grammar productions to required test evidence.
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

### 2.3 Relationship to other workstreams

- ZSS-01 remains the immutable design baseline for existing syntax architecture.
- ZSS-02 remains the governance framework for rule identity, lifecycle, and
  Grammar Version immutability.
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
| `docs/engineering/ZSS-02_GOVERNANCE_RULE_LIFECYCLE_COMPATIBILITY.md` | Governance, rule lifecycle, compatibility |
| `docs/architecture/boundaries.md` | Component ownership boundaries |
| `AGENTS.md`, `AI_RULES.yaml`, `RULES.md`, `SECURITY.md` | Project governance and security |
| `src/zen/limits.py` | Declared numeric ceilings (AST / parser accounting) |
| `src/zen/parser/context.py`, `diagnostics.py` | Existing parser scaffolding (not a complete parser) |

All conformance claims must be traceable to the official grammar in the
language specification. ZSS-01 summaries are supporting design records;
they do not replace the EBNF.

---

## 4. Definitions

| Term | Definition |
|---|---|
| **Grammar conformance** | Observable behavior of a Parser (and its token consumer) that accepts exactly the language defined by the v0.1 EBNF and rejects inputs outside that language, with correct structure, precedence, associativity, and source mapping. |
| **Positive syntax case** | Source that the grammar accepts; a conforming parser must accept it and produce a corresponding valid AST structure. |
| **Negative syntax case** | Source that the grammar rejects; a conforming parser must reject it with a source-located syntax diagnostic and must not produce a successful Program AST for that input. |
| **Grammar production inventory** | The complete set of v0.1 EBNF productions that must be covered by positive and/or negative tests. |
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
to obtain a pass. See Section 12.

---

## 6. Grammar Production Inventory

The following productions are taken from `docs/03-language-specification.md`
§5. Every production must appear in the conformance matrix (Section 15)
with at least one positive and, where rejection is defined, negative case.

### 6.1 Program and separators

| Production ID | Production (summary) | Notes |
|---|---|---|
| G-PROG | `program` | Empty program valid; ends at EOF |
| G-SEP | `separators` | One or more NEWLINE or SEMICOLON; repeats allowed; no empty statements |
| G-STMT | `statement` | Alternatives: decl / control / return / expr-stmt |
| G-BLOCK | `block` | Empty block valid; final stmt may end before `}` |

### 6.2 Declarations and control flow

| Production ID | Production (summary) | Notes |
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

| Production ID | Production | Associativity / notes |
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
| G-ARGS | `argument_list` / `arguments` | No trailing comma |
| G-PRIMARY | `primary` | Literals, IDENTIFIER, grouping |

### 6.4 Lexical tokens relevant to syntax

Conformance tests may assume a correct Lexer for tokens listed in the
specification. Lexer non-conformance is out of scope for ZSS-03 grammar
conformance claims, but negative tests that surface as lexical errors
must be classified separately (lexical vs syntactic rejection).

---

## 7. Positive Syntax Test Cases (Design Requirements)

A conforming implementation must accept at least the following categories.
Exact fixtures are design requirements; implementation of the test suite
is not authorized by this document.

### 7.1 Minimal and empty forms

- Empty program (only optional separators then EOF).
- Empty block `{ }` and `{` + separators + `}`.
- Single expression statement ending at EOF.
- Single expression statement ending before `}`.

### 7.2 Declarations

- `let` without initializer.
- `let` with initializer.
- `const` with initializer.
- Nested declarations inside blocks.
- Function with zero parameters.
- Function with one and multiple parameters (no trailing comma).

### 7.3 Control flow

- `if (cond) { }` without else.
- `if (cond) { } else { }`.
- `if (cond) { } else if (cond2) { }`.
- `if (cond) { } else if (cond2) { } else { }`.
- Newlines (zero or more) between then-block `}` and `else`.
- `while (cond) { }`.
- Nested if/while inside blocks.

### 7.4 Return

- `return` with no expression, ended by NEWLINE / SEMICOLON / `}` / EOF.
- `return` with expression on the same logical statement (expression begins before next separator).

### 7.5 Expressions — precedence and associativity

Positive cases must establish the grouping required by the precedence table
in the language specification §5.4:

| Level | Form | Required grouping example (illustrative) |
|---:|---|---|
| 1 | Assignment | `a = b = 3` → `a = (b = 3)` |
| 2 | `\|\|` | `a \|\| b \|\| c` → `(a \|\| b) \|\| c` |
| 3 | `&&` | left-associative chain |
| 4 | `==` `!=` | left-associative chain |
| 5 | comparisons | left-associative chain |
| 6 | `+` `-` | left-associative chain |
| 7 | `*` `/` `%` | left-associative chain |
| 8 | unary `!` `-` | right-associative (`!!x`, `--x` as two unaries) |
| 9 | calls | `f()()` chainable |
| 10 | primary / grouping | `(a + b) * c` |

Mixed-precedence cases (e.g. `a + b * c`, `!a && b`, `-f()`) must match
the table.

### 7.6 Newlines as whitespace inside lists

- Parenthesized grouping with internal newlines.
- Parameter lists with internal newlines.
- Argument lists with internal newlines.

### 7.7 Separators

- Multiple consecutive NEWLINE and/or SEMICOLON between statements.
- Two statements on one line separated by SEMICOLON.
- Final statement without trailing separator before EOF or `}`.

### 7.8 Official valid examples

The valid examples in language specification §5.7 must be accepted
(subject to Lexer success).

---

## 8. Negative Syntax Test Cases (Design Requirements)

A conforming parser must reject the following categories with a
source-located syntax diagnostic and must not return a successful
`Program` AST for the input.

### 8.1 Declaration and parameter errors

- `const` without initializer.
- Function parameter list with trailing comma.
- Missing parentheses around `if` / `while` condition.
- Missing braces for `if` / `while` / function body.

### 8.2 Statement boundary errors

- Two statements on the same line without SEMICOLON.
- SEMICOLON between then-block and `else`.

### 8.3 Assignment boundary errors

- Assignment to non-identifier targets: `(a) = 1`, `f() = 1`, `1 = 2`,
  `a + b = 3`.
- These must fail at parse time (grammar restriction), not only at
  semantic analysis.

### 8.4 Expression / call errors

- Trailing comma in argument list.
- Unbalanced parentheses or braces.
- Unexpected tokens where a production requires a specific token.

### 8.5 Official invalid examples

The invalid examples in language specification §5.7 must be rejected.

### 8.6 Return expression boundary

- A newline immediately after `return` must end the return statement;
  a following expression on the next line is a separate statement (or
  error if not a valid statement), not part of the return expression.

### 8.7 Classification note

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
| 2 | `\|\|` | Left |
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

---

## 15. Conformance Verification Matrix

Status values for future execution evidence: **NOT_TESTED** (default until
a parser and tests exist), **PASS**, **FAIL**, **BLOCKED**, **N/A**.

Evidence labels: **OBSERVED**, **DERIVED**, **ASSUMED**, **UNKNOWN**, **NOT_TESTED**.

| ID | Requirement | Grammar / ref | Positive | Negative | Component | Status |
|---|---|---|---|---|---|---|
| C-01 | Empty program accepted | G-PROG | Yes | — | Parser | NOT_TESTED |
| C-02 | Empty block accepted | G-BLOCK | Yes | — | Parser | NOT_TESTED |
| C-03 | Separators (NEWLINE/SEMICOLON, repeats) | G-SEP | Yes | Same-line without `;` | Parser | NOT_TESTED |
| C-04 | `let` / `const` forms | G-VAR | Yes | `const` no init | Parser | NOT_TESTED |
| C-05 | Function + parameter list | G-FN, G-PARAMS | Yes | Trailing comma | Parser | NOT_TESTED |
| C-06 | `if` / `else` / `else if` | G-IF, G-ELSE-NL | Yes | Missing `()` or `{}`; `;` before else | Parser | NOT_TESTED |
| C-07 | `else` nearest unmatched `if` | Spec §5.3, §5.6 | Yes | — | Parser | NOT_TESTED |
| C-08 | Newlines before `else` allowed | G-ELSE-NL | Yes | — | Parser | NOT_TESTED |
| C-09 | `while` form | G-WHILE | Yes | Missing `()` or `{}` | Parser | NOT_TESTED |
| C-10 | `return` optional expr boundary | G-RETURN | Yes | Expr after newline not part of return | Parser | NOT_TESTED |
| C-11 | Assignment right-assoc, bare ID only | G-ASSIGN | Yes | Non-identifier LHS | Parser | NOT_TESTED |
| C-12 | Assignment lookahead no skip NL/`;` | Spec §5.4 | Yes | — | Parser | NOT_TESTED |
| C-13 | Precedence table grouping | G-OR…G-PRIMARY | Yes | — | Parser | NOT_TESTED |
| C-14 | Unary right-assoc; calls chainable | G-UNARY, G-CALL | Yes | — | Parser | NOT_TESTED |
| C-15 | NL whitespace inside `()` / params / args | Spec §5.2, §5.6 | Yes | `;` inside those lists | Parser | NOT_TESTED |
| C-16 | Official §5.7 valid examples | Spec §5.7 | Yes | — | Parser | NOT_TESTED |
| C-17 | Official §5.7 invalid examples | Spec §5.7 | — | Yes | Parser | NOT_TESTED |
| C-18 | Grammar→AST node mapping | Spec §5.5 | Yes | — | Parser+AST | NOT_TESTED |
| C-19 | Source-located syntax diagnostics | Spec §7 | — | Yes | Parser | NOT_TESTED |
| C-20 | No silent skip of malformed input | Spec §7 | — | Yes | Parser | NOT_TESTED |
| C-21 | Parser depth limit enforced | limits.py | Boundary | Over-limit reject | Parser | NOT_TESTED |
| C-22 | Parser node-count limit enforced | limits.py | Boundary | Over-limit reject | Parser | NOT_TESTED |
| C-23 | Adversarial / malformed nesting | §14 | — | Yes | Parser | NOT_TESTED |
| C-24 | AST validation ≠ grammar proof | Boundaries | Design rule | — | Process | NOT_TESTED |

Additional rows may be added only for productions or rules already present
in the approved grammar; new syntax must not be introduced here.

---

## 16. Evidence Collection and Acceptance Criteria

### 16.1 Evidence rules

- A planned test is **NOT_TESTED**.
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
2. Every listed grammar concern is traced to the official v0.1 grammar or
   explicitly marked UNRESOLVED with affected production and impact.
3. Component boundaries are consistent with AGENTS.md, RULES.md,
   boundaries.md, and ZSS-01.
4. No new syntax or grammar reinterpretation is introduced.
5. Resource ceilings are preserved; adversarial categories are specified.
6. Verification matrix and evidence rules are defined.
7. Document remains documentation-only (no production code change).

### 16.3 Acceptance criteria for a future grammar-conformant Parser

(Not authorized by this document; stated for traceability.)

A Parser implementation may be claimed grammar-conformant for v0.1 only when:

1. Matrix rows C-01–C-23 have OBSERVED execution evidence with PASS
   (or documented N/A with justification).
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
| OI-05 | ZSS-02 reconstructed draft wording vs sealed Owner text | NOTE | ZSS-02 file is labeled reconstructed review draft; governance principles used here are those stated in AGENTS.md / AI_RULES.yaml active milestone entries |

No open issue in this list authorizes a grammar change.

---

## 18. Change-Control Rules

1. This document does not modify ZSS-01 or the official language specification.
2. Normative grammar changes require a new governed Grammar Version process
   under ZSS-02 principles and explicit Owner approval.
3. Revisions to ZSS-03 itself require Owner review; revision number must
   increase; prior revision retained in history.
4. Implementation of a parser or conformance test suite requires separate
   explicit Owner authorization beyond approval of this design document.
5. Resource-limit changes require technical justification, boundary tests,
   and Owner approval (SECURITY.md / RULES.md).
6. Conflicts between this document and the official grammar: the official
   grammar wins; this document must be corrected.
7. Conflicts with governance documents: stop and request Owner clarification.

---

## 19. Compatibility with ZSS-01 and ZSS-02

### 19.1 ZSS-01

- Preserves language identity, production summaries, precedence table,
  separator/newline/else/assignment rules, AST correspondence, and
  resource separation.
- Does not alter the baseline or claim parser existence.
- Extends the baseline with explicit conformance verification design only.

### 19.2 ZSS-02

- Treats v0.1 grammar as the current normative Grammar Specification artifact.
- Does not implement Registry, Manifest, or migration machinery.
- Does not authorize activation of new rules or versions.
- Maintains separation of Decision / Normative / Implementation authority.

### 19.3 Ecosystem extensibility

ZSS-03 verification machinery (when later implemented) must remain modular:
conformance evidence for ZSS must not force coupling of future ZEN
subsystems to ZSS-internal test harness details.

---

## 20. Document History

| Revision | Date | Status | Summary |
|---|---|---|---|
| 1 | 2026-11-24 | DRAFT — AWAITING OWNER REVIEW | Initial Grammar Conformance Design; documentation-only |

---

**End of ZSS-03 — Grammar Conformance Design**

**Authority:** This document is a design specification for grammar
conformance verification. It does not supersede the official language
specification, does not modify ZSS-01, and does not authorize parser
implementation, grammar changes, or production code modification.
Owner approval is required before any implementation phase.
