# ZSS-05 — ZSS Design Specification

**Document ID:** ZSS-05  
**Title:** ZSS Design Specification  
**Revision:** 1  
**Status:** DRAFT — AWAITING OWNER REVIEW  
**Version:** 0.1.0-design  
**Date:** 2026-11-24  
**Project:** ZEN — Zen Structured Syntax (ZSS)  
**Scope:** Consolidated design specification (documentation only)  
**Implementation:** NOT AUTHORIZED  
**Parser implementation:** NOT AUTHORIZED  
**Semantic Analysis implementation:** NOT AUTHORIZED  
**Grammar change:** NOT AUTHORIZED  

**Normative language/grammar authority:** Zen Language Specification v0.1.0  
(`docs/03-language-specification.md`)

**Future implementation organization (handoff only):** Blue Strix  
Blue Strix does not hold language-design authority and may not override Owner decisions.

---

## 1. Purpose and Design Principles

### 1.1 Purpose

ZSS-05 consolidates the established and verified design foundations from
ZSS-01 through ZSS-04 into one coherent, traceable, and
implementation-evaluable design specification for Zen Structured Syntax.

It is the principal **design reference** for future ZSS implementation
work. It does not authorize that implementation.

### 1.2 Design principles

1. **Explicitness** — Official rules are documented; agents and implementers must not invent missing rules.
2. **Layer separation** — Lexical, grammatical, structural, semantic, and runtime concerns remain distinct.
3. **Traceability** — Normative statements cite authoritative sources and authority class.
4. **Evidence discipline** — OBSERVED, DERIVED, PROPOSED, ASSUMED, UNKNOWN, DEFERRED, NOT_TESTED are used consistently.
5. **Non-silent incompleteness** — Unresolved questions remain visible; they are not closed by default.
6. **Modularity** — ZSS remains internally modular and extensible without coupling to non-ZSS concerns.
7. **Authority clarity** — Owner is final authority; merged documentation is not automatically Owner-approved final text.
8. **Project isolation** — This specification is self-contained within ZSS.

### 1.3 Specification authority

| Role | Holder |
|---|---|
| Final decision authority | Owner |
| Normative grammar / stated language form | Language Specification v0.1.0 |
| Design baseline (grammar architecture) | ZSS-01 (Owner-approved design baseline) |
| Conformance design (syntax) | ZSS-03 (merged; document status DRAFT) |
| Semantic boundary design | ZSS-04 (merged; document status DRAFT) |
| Governance principles (reference) | ZSS-02 on-disk material (reconstructed draft; not sealed final wording) |
| Implementation organization (future handoff) | Blue Strix (no design authority) |

---

## 2. Scope, Non-Goals, and Project Isolation

### 2.1 In scope

- Consolidation of ZSS design boundaries and layer responsibilities.
- Grammar and conformance design references (without changing the grammar).
- AST structural design responsibilities (evidence-based).
- Semantic boundary and unresolved question register.
- Diagnostic ownership at the architectural level.
- Resource-limit documentation and enforcement-status honesty.
- Implementation handoff structure for Blue Strix.
- Requirement traceability.

### 2.2 Non-goals

- Authorizing or performing implementation of Lexer changes, Parser, Semantic Analysis, or Runtime.
- Modifying the official grammar or language specification.
- Resolving OQ-01 through OQ-09.
- Creating a diagnostic code catalog or recovery policy not already established.
- Changing resource-limit numeric values.
- Cross-project integration requirements.

### 2.3 Project isolation (mandatory)

ZSS-05 discusses **ZSS only**. It does not introduce names, requirements,
assumptions, dependencies, or integration references involving unrelated
projects, workstreams, or subsystems. Blue Strix is named solely as the
future ZSS implementation organization.

---

## 3. Source Authority Matrix

| Source | Path / identity | Authority class | Use in ZSS-05 |
|---|---|---|---|
| Language Specification v0.1.0 | `docs/03-language-specification.md` | **Normative** | Grammar and stated language decisions |
| ZSS-01 | `docs/engineering/ZSS-01_GRAMMAR_BASELINE.md` | **Owner-approved design baseline** | Architecture baseline; preserve unchanged |
| ZSS-02 | `docs/engineering/ZSS-02_GOVERNANCE_RULE_LIFECYCLE_COMPATIBILITY.md` | **Reference (reconstructed draft)** | Governance principles only; not sealed final wording |
| ZSS-03 | `docs/engineering/ZSS-03_GRAMMAR_CONFORMANCE_DESIGN.md` | **Merged draft** (status: DRAFT — AWAITING OWNER REVIEW) | Conformance design; production traceability |
| ZSS-04 | `docs/engineering/ZSS-04_SEMANTIC_BOUNDARY.md` | **Merged draft** (status: DRAFT — AWAITING OWNER REVIEW) | Semantic boundary; OQ register |
| Architecture boundaries | `docs/architecture/boundaries.md` | Architecture reference | Component ownership |
| Limits module | `src/zen/limits.py` | **OBSERVED** implementation constants | Numeric ceilings as coded |
| Parser scaffolding | `src/zen/parser/` | **OBSERVED** foundations; not a complete parser | Context / diagnostics scaffolding only |

**Rule:** A merged PR does not by itself elevate a document from DRAFT to Owner-approved final.

---

## 4. Architecture and Processing Boundaries

Intended conceptual pipeline (**OBSERVED** from language specification §8,
ZSS-01, ZSS-04):

Source → Lexer → Parser → AST → Semantic Analysis → Interpreter → Runtime

### 4.1 Layer summary

| Layer | Responsibility | Input | Output | Must not own |
|---|---|---|---|---|
| **Lexical Analysis** | Tokenization; lexical limits; lexical diagnostics | Source text | Token stream or lexical error | Grammar structure; meaning; execution |
| **Grammar / Parsing** | EBNF matching; syntax diagnostics; parse resource accounting | Token stream | AST (success) or syntax diagnostic | Semantic meaning; silent structural repair; runtime |
| **AST structural representation** | Immutable program structure; declared contracts | Parser construction (when implemented) | Structured tree | Proof of grammar match; semantic binding |
| **AST structural validation (ZASI)** | Types, spans, order, cycles, reuse, structural limits | AST | Validation result / structural diagnostics | Grammar conformance; semantic meaning |
| **Semantic Analysis** | Meaning rules (when specified and implemented) | Structurally valid AST | Semantic findings / diagnostics | Re-parsing as authority; grammar redesign; silent canonical AST mutation |
| **Runtime** | Execution of admissible programs; dynamic errors | Semantically admissible representation | Results / runtime errors | Static scope design; grammar acceptance |

### 4.2 Established invariants (design-level)

- AST validation success ≠ grammar conformance (**OBSERVED** ZSS-01 / ZSS-03 / ZSS-04).
- Grammar success ≠ semantic validity.
- Semantic success (when defined) ≠ absence of all runtime failures.
- Strict error handling: first lexical, syntax, semantic, or runtime error stops the current program (**OBSERVED** language specification §7).

### 4.3 Implementation status (honest)

| Component | Status |
|---|---|
| Lexer | **Implemented** (OBSERVED) |
| Parser (complete grammar) | **Not implemented**; scaffolding exists |
| Canonical AST model | **Implemented** |
| AST structural validation | **Implemented** foundations |
| Semantic Analysis | **Not implemented** |
| Interpreter / Runtime | **Not implemented** |

---

## 5. Grammar and Conformance

### 5.1 Normative grammar

The sole normative concrete syntax is the v0.1 EBNF in
`docs/03-language-specification.md` §5.

ZSS-05 does **not** modify, reinterpret, or extend that grammar.

### 5.2 Production inventory (design reference)

Productions documented for conformance design include (ZSS-03 / language
specification):  
`program`, `separators`, `statement`, `block`, `variable_declaration`,
`function_declaration`, `parameter_list`, `if_statement`, `else_newlines`,
`while_statement`, `return_statement`, `expression_statement`,
`expression`, `assignment`, `logical_or`, `logical_and`, `equality`,
`comparison`, `term`, `factor`, `unary`, `call`, `argument_list`,
`arguments`, `primary`.

### 5.3 Conformance expectations

From ZSS-03 (merged draft):

- Positive and negative designed cases with production-level traceability.
- Precedence and associativity per language specification table.
- Statement separators, newline rules, `else` association, assignment
  lookahead constraints as specified.
- All execution evidence remains **NOT_TESTED** until a parser exists and
  tests run.
- AST structural validation must not be claimed as grammar-conformance proof.

### 5.4 Supported vs unsupported syntax (v0.1)

**Supported form (normative grammar):** declarations (`let`/`const`/`fn`),
`if`/`else`/`while`, `return`, expressions with defined operators, calls,
grouping, comments, specified literals.

**Not introduced by v0.1 grammar as language features:** arrays/indexing,
type annotations, objects, trailing commas in parameter/argument lists,
unary plus, exponent notation, etc. Lexical recognition of some tokens
(e.g. brackets, colon) must not be read as full language support
(**OBSERVED** language specification / ZSS-01).

---

## 6. AST and Structural Representation

### 6.1 Responsibilities

- Canonical immutable node model for program structure.
- Source spans (half-open) and structural contracts (child types, containment,
  sibling order, non-overlap).
- Structural resource limits distinct from parser nesting accounting.

### 6.2 Grammar-to-AST correspondence (design mapping)

As documented in the language specification §5.5 and ZSS-01: Program,
VarDecl, FunctionDecl, BlockStmt, IfStmt, WhileStmt, ReturnStmt,
ExpressionStmt, LiteralExpr, IdentifierExpr, GroupingExpr, UnaryExpr,
BinaryExpr, AssignExpr, CallExpr.

`AssignExpr.target` is `IdentifierExpr` (matches grammar).  
`IfStmt.else_branch` may be block, nested `IfStmt`, or none.

This mapping does **not** prove a parser exists.

### 6.3 Structural vs semantic validity

Structural validity is ZASI/AST contract satisfaction.  
Semantic validity is meaning-rule satisfaction (ZSS-04).  
They are not interchangeable.

---

## 7. Semantic Boundary

Primary source: ZSS-04 (merged draft).

### 7.1 Syntax-level constraints (not semantic-only)

Examples **explicitly** grammar-owned:

- Assignment target must be bare `IDENTIFIER`.
- `const` requires initializer in the grammar.
- Parenthesized conditions and braced bodies for `if`/`while`/`fn`.

### 7.2 Semantic categories (status preserved)

| Category | Status |
|---|---|
| Block scope (decision) | Explicit design decision; resolution algorithm not fully specified |
| Redeclaration rules | Not yet specified |
| Uninitialized `let` read | Not yet specified |
| `const` reassignment after binding | Not yet specified |
| Name resolution | Not yet specified |
| Function arity validation | Not yet specified |
| `return` outside function | Directed to Semantic Analysis by language specification |
| Callability | Not yet specified (semantic/runtime) |
| Evaluation rules (short-circuit, truthiness, coercion, ÷0, equality) | Not yet specified |

No category above is newly decided by ZSS-05.

---

## 8. Error and Diagnostic Boundaries

| Kind | Owner |
|---|---|
| Lexical | Lexer |
| Syntax | Parser |
| Structural | AST validation / ZASI |
| Semantic | Semantic Analysis (when implemented) |
| Runtime | Runtime |

Existing parser scaffolding includes located `ParseError` (**OBSERVED**).  
A full cross-phase diagnostic catalog is **DEFERRED** (ZSS-04 OQ-09).

ZSS-05 does not invent error codes, severity policy, or recovery strategy.

---

## 9. Resource and Safety Constraints

### 9.1 Specified numeric ceilings (do not change here)

From language specification / ZSS-01 / `src/zen/limits.py` (**OBSERVED** values):

| Limit | Typical value | Domain |
|---|---:|---|
| Source text | 2,097,152 code points | Lexer |
| Identifier length | 256 | Lexer |
| Non-EOF tokens | 262,144 | Lexer |
| `MAX_PARSER_DEPTH` | 256 | Parser accounting |
| `MAX_AST_NODES` | 1,000,000 | Parser accounting / AST |
| `MAX_AST_DEPTH` | 256 | AST structural |
| `MAX_DIRECT_CHILDREN` | 262,144 | AST structural |
| `MAX_EXPRESSION_NODES` | 262,144 | AST structural |
| `MAX_STATEMENT_NODES` | 262,144 | AST structural |

### 9.2 Enforcement status

| Area | Status |
|---|---|
| Lexer limits | Enforced by implemented lexer (**OBSERVED** design claim; detailed test evidence not re-executed in this drafting session → verification **NOT_TESTED** here) |
| Parser depth/node accounting | Scaffolding present; full grammar parser absent → end-to-end parse enforcement **NOT** complete |
| AST structural limits | Validation paths exist in codebase; not a substitute for parse-time grammar limits |

Do not claim enforcement exists solely because a number is documented.

Security principles from the language specification remain applicable to
future runtime design (no `eval`/`exec` of Zen source; restricted early
runtimes). ZSS-05 does not modify security policy documents.

---

## 10. Compatibility and Evolution

- Grammar Version immutability and rule lifecycle follow **principles**
  referenced via ZSS-02 material without treating reconstructed wording as
  sealed final text.
- Normative grammar changes require Owner-approved process; ZSS-05 does not
  perform them.
- Directional compatibility claims require explicit assessment and evidence.
- ZSS internal interfaces should remain explicit so layers can evolve without
  silent responsibility transfer.

No new backward-compatibility guarantee is invented here.

---

## 11. Requirement Traceability (selected)

| Req. ID | Statement | Source | Authority | Classification |
|---|---|---|---|---|
| R-GRAM-01 | v0.1 EBNF is sole normative concrete syntax | Language spec §5 | Normative | Normative |
| R-SEP-01 | Statement separators are NEWLINE or SEMICOLON | Language spec §5.2 | Normative | Normative |
| R-ASSIGN-01 | Assignment target is bare IDENTIFIER | Language spec §5.4 | Normative | Normative |
| R-ELSE-01 | `else` binds to nearest unmatched `if` | Language spec §5.3 / §5.6 | Normative | Normative |
| R-RET-SEM-01 | `return` outside function is for Semantic Analysis | Language spec §5.3 | Normative direction | Normative boundary |
| R-CONF-01 | Grammar conformance is Parser responsibility | ZSS-03 / ZSS-01 | Merged draft / baseline | Design |
| R-AST-01 | Structural validation ≠ grammar proof | ZSS-01 / ZSS-03 / ZSS-04 | Baseline / drafts | Design |
| R-SEM-01 | Name resolution rules not fully specified | Language spec §6; ZSS-04 | Normative gap | Unresolved |
| R-LIM-01 | Resource ceilings must not be silently raised | ZSS-01; governance | Baseline / governance | Normative process |

Additional rows may be derived from ZSS-03 matrix case IDs without restating
the entire matrix.

---

## 12. Implementation Handoff (Blue Strix)

### 12.1 Role

Blue Strix is the designated organization for **future** ZSS implementation
handoff evaluation. It does **not** gain authority to change approved
language behavior or to resolve Owner-owned open questions by unilateral
default.

### 12.2 Layer handoff summary

| Layer | Preconditions | Postconditions (when done) | Blocked by |
|---|---|---|---|
| Lexer | Existing implementation baseline | Token stream per spec | — |
| Parser | Normative grammar; ZSS-03 design cases | Grammar-conformant AST or syntax diagnostic | Implementation authorization |
| AST/ZASI | Existing contracts | Structural validity results | — |
| Semantic Analysis | Structurally valid AST; Owner-specified semantic rules | Semantic diagnostics / admissibility | **OQ-01…OQ-08** (and related) |
| Runtime | Semantically admissible program; runtime rules | Execution results | OQ-07 and runtime design authorization |

### 12.3 Classification of handoff content

1. **Established requirements** — Normative language specification + Owner-approved ZSS-01 baseline.  
2. **Derived technical requirements** — Traceable from those sources without new behavior.  
3. **Proposed recommendations** — Process/structure only; not language rules (marked PROPOSED if used).  
4. **Owner decisions still required** — OQ-01 through OQ-09.

### 12.4 Acceptance posture for implementers

- Do not treat DRAFT ZSS-03/ZSS-04 text as final Owner-approved sealed design without Owner confirmation.
- Do not treat unresolved OQs as free choice of language semantics.
- Escalate any decision that changes language behavior to Owner.
- Conformance claims require OBSERVED execution evidence.

---

## 13. Unresolved Questions Register (OQ-01 … OQ-09)

Identifiers and intent preserved from ZSS-04. **None are resolved by ZSS-05.**

| ID | Question | Status | Design impact | Implementation impact | Owner decision required | Blocks complete Semantic Analysis? |
|---|---|---|---|---|---|---|
| OQ-01 | Exact redeclaration rules in the same scope | Unresolved | High | Analyzer rules incomplete | **Yes** | **Yes** |
| OQ-02 | Uninitialized `let` read behavior | Unresolved | High | Phase/rule unknown | **Yes** | **Yes** |
| OQ-03 | `const` reassignment rule details | Unresolved | High | Static policy missing | **Yes** | **Yes** |
| OQ-04 | Name-resolution algorithm (shadowing, globals, parameters) | Unresolved | Critical | Core analyzer missing | **Yes** | **Yes** |
| OQ-05 | Function arity checking phase | Unresolved | High | Semantic vs runtime | **Yes** | Likely |
| OQ-06 | Callability checking phase | Unresolved | High | Semantic vs runtime | **Yes** | Likely |
| OQ-07 | Evaluation rules (short-circuit, truthiness, coercion, division by zero, equality) | Unresolved | High | Runtime/semantic split | **Yes** | Partial |
| OQ-08 | Parameter name uniqueness | Unresolved | Medium | Binding integrity | Preferred | Preferred |
| OQ-09 | Semantic diagnostic catalog | Deferred | Medium | Tooling | When analyzer authorized | No |

**OQ-10** (ZSS-04) concerned the definition of ZSS-05 versus semantic-spec versus analyzer design. This document defines ZSS-05 as **design consolidation only**, not as resolution of OQ-01…OQ-09 and not as analyzer implementation authorization.

**Safe independent work without resolving OQs:** documentation; lexer maintenance within approved scope; AST structural work already authorized elsewhere; conformance *design* without false PASS claims.  
**Not safe without Owner decisions:** claiming a complete semantic language definition; shipping Semantic Analysis that invents answers to OQ-01…OQ-08.

---

## 14. Acceptance Criteria for This Document

ZSS-05 (this revision) is **READY FOR OWNER REVIEW** when:

1. ZSS-01…ZSS-04 inspected and statuses accurately stated.  
2. Normative grammar authority unchanged.  
3. Layer responsibilities consistent and non-overlapping.  
4. OQ-01…OQ-09 visible and unresolved.  
5. No invented language behavior.  
6. Project isolation respected.  
7. Blue Strix role limited to implementation organization.  
8. Document status remains **DRAFT — AWAITING OWNER REVIEW**.

This does **not** mean OWNER-APPROVED or FINAL.

---

## 15. Explicit Exclusions

ZSS-05 does not:

- Modify production code, grammar, language specification, security policies, or resource-limit values.
- Rewrite ZSS-01, ZSS-02, ZSS-03, or ZSS-04.
- Resolve OQ-01…OQ-09.
- Authorize Parser, Semantic Analysis, or Runtime implementation.
- Introduce non-ZSS project dependencies.

---

## 16. Document History

| Revision | Date | Status | Summary |
|---|---|---|---|
| 1 | 2026-11-24 | DRAFT — AWAITING OWNER REVIEW | Initial consolidated ZSS Design Specification |

---

**End of ZSS-05 — ZSS Design Specification**

**Authority:** Design consolidation only. Not Owner-approved final. Not implementation authorization. Owner retains final authority over scope, language behavior, approval, and merge of any future implementation work.
