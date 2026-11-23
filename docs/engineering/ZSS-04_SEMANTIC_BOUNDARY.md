# ZSS-04 — Semantic Boundary

**Document ID:** ZSS-04  
**Title:** Semantic Boundary  
**Revision:** 1  
**Status:** DRAFT — AWAITING OWNER REVIEW  
**Version:** 0.1.0-design  
**Date:** 2026-11-24  
**Project:** ZEN — Zen Structured Syntax (ZSS)  
**Scope:** Architectural boundary specification (documentation only)  
**Implementation:** NOT AUTHORIZED  
**Semantic analyzer implementation:** NOT AUTHORIZED  
**Grammar change:** NOT AUTHORIZED  

**Normative grammar authority:** Zen Language Specification v0.1.0  
(`docs/03-language-specification.md`)

---

## 1. Purpose

ZSS-04 establishes a precise architectural boundary between:

1. **Syntax validity** — whether source text conforms to the official v0.1 grammar.
2. **Semantic validity** — whether a syntactically valid program satisfies the language’s meaning-related rules.
3. **Runtime behavior** — what happens when a semantically admissible program is executed.

The goal is to prevent grammar rules, semantic rules, and runtime behavior from becoming mixed or inconsistently enforced, and to define clear component ownership **without** designing or implementing a semantic analyzer.

This document is a **design boundary specification**. It does not authorize implementation of Semantic Analysis, the Parser, the Runtime, or any production-code change.

---

## 2. Scope and Non-Goals

### 2.1 In scope

- Architectural separation of lexical, grammatical, structural, semantic, and runtime concerns.
- Classification of Zen v0.1 semantic rule categories based on existing specification evidence.
- Responsibility matrix across Lexer, Parser, AST/ZASI, Semantic Analysis, and Runtime.
- Illustrative syntax-valid / potentially-semantic-invalid examples grounded in existing text.
- Conceptual diagnostics ownership and phase ordering.
- Explicit open questions and deferred decisions.

### 2.2 Non-goals (NOT authorized)

- Semantic analyzer implementation.
- Parser or lexer implementation or modification.
- AST node changes or new AST types.
- Official grammar changes or new syntax.
- Runtime or interpreter implementation.
- Error-code registry, diagnostic API, or message-format invention beyond existing scaffolding.
- Security-policy, resource-limit, dependency, CI, or governance-file changes.
- Use of Python `eval()` / `exec()` as part of any proposed architecture.

### 2.3 Dependencies

| Dependency | Status used by this document |
|---|---|
| ZSS-01 Grammar Baseline | OWNER-APPROVED design baseline on main; preserved |
| ZSS-02 Governance reference | On-disk file self-labeled reconstructed draft; used as governance **reference** only (see ZSS-03 §3.1 pattern) |
| ZSS-03 Grammar Conformance Design | Merged into main (PR #31); design reference for syntax-side boundaries |
| Language Specification v0.1.0 | Sole normative grammar authority; primary evidence for semantic vs syntax statements |
| `docs/architecture/boundaries.md` | Component ownership baseline |

**Roadmap context (design only):** ZSS-01 → ZSS-02 → ZSS-03 → **ZSS-04** → ZSS-05.  
ZSS-05 is not specified here and is not authorized by this document.

---

## 3. Normative Terminology

| Term | Definition |
|---|---|
| **Lexical validity** | Source characters form a legal token stream under lexer rules (including lexical resource limits). |
| **Grammar validity** | A token stream matches the official v0.1 EBNF (syntax acceptance). |
| **AST structural validity** | A constructed AST satisfies declared structural contracts (node/child types, spans, ordering, cycles/reuse, structural limits). |
| **Semantic validity** | A structurally valid AST satisfies the language’s meaning-related rules (names, scopes, declaration constraints, context rules, and other rules assigned to Semantic Analysis). |
| **Runtime validity / behavior** | Observable execution outcomes of a program that has passed prior phases, including dynamic failures and evaluation rules. |
| **Semantic Analysis** | The architectural phase responsible for semantic validity; **not implemented** in the current repository baseline. |
| **Evidence labels** | OBSERVED, DERIVED, ASSUMED, UNKNOWN, NOT_TESTED, DEFERRED (per project governance). |

---

## 4. Architectural Principles

### 4.1 Why syntax and semantics must be separate

- The grammar answers **form**: “Is this a legal arrangement of tokens?”
- Semantics answers **meaning constraints**: “Given a legal form, do names, scopes, and context rules hold?”
- Runtime answers **execution**: “What happens when this program runs?”

Mixing these layers produces:

- Grammar rules that secretly encode meaning (hard to evolve).
- Semantic rules that reject purely structural errors (wrong diagnostic owner).
- Runtime checks that mask missing static semantic rules (late, inconsistent failure).

**Principle:** Each layer owns its failures and must not silently absorb another layer’s responsibilities.

### 4.2 Layer ownership (summary)

| Layer | Owns | Must not own |
|---|---|---|
| Lexer | Tokens, lexical limits, lexical diagnostics | Grammar structure, meaning, execution |
| Parser | Grammar matching, syntax diagnostics, parse-time resource accounting | Meaning rules, structural graph integrity of arbitrary AST graphs, execution |
| AST + ZASI | Structural contracts on constructed trees | Proof of grammar conformance; semantic meaning |
| Semantic Analysis | Meaning rules on validated AST | Re-parsing source; rewriting grammar; silent AST mutation of canonical structure |
| Runtime | Execution behavior and dynamic failures | Static name/scope design; grammar acceptance |

### 4.3 Evidence basis

Statements below that restate the language specification or ZSS-01 are **OBSERVED** from those documents. Classifications of “not yet specified” are **OBSERVED** gaps in the same sources. No new language rule is introduced as normative by this document.

---

## 5. Validity Categories and Responsible Layer

| Category | Question | Responsible layer | Downstream depends on success |
|---|---|---|---|
| Lexical validity | Are tokens well-formed? | Lexer | Parser |
| Grammar validity | Does the token stream match the EBNF? | Parser | AST construction from parse |
| AST structural validity | Is the tree structurally sound? | AST contracts + ZASI validation | Semantic Analysis |
| Semantic validity | Do meaning rules hold? | Semantic Analysis | Runtime (when both exist) |
| Runtime behavior | What happens during execution? | Runtime | End user / host |

**OBSERVED** (language specification §8 architecture; ZSS-01 §6–§9; boundaries.md): intended pipeline is  
Source → Lexer → Parser → AST → Semantic Analysis → Interpreter → Runtime.

**OBSERVED** implementation status: Lexer and AST/ZASI foundations exist; complete Parser and Semantic Analysis do **not**.

---

## 6. Semantic Rule Categories (Zen v0.1)

Categories are drawn only from existing specification text. Status values:

- **Explicitly specified** — stated as a language rule in the official specification or approved baseline.
- **Implied** — strongly indicated but not fully specified as an enforceable semantic rule set.
- **Not yet specified** — called out as belonging to semantic analysis / future design, without complete rules.
- **Deferred** — intentionally left for later design (including ZSS-05 or later work).

| Category | Status | Evidence summary |
|---|---|---|
| Identifier as assignment **target form** | **Explicitly specified (syntax)** | Grammar restricts assignment LHS to bare `IDENTIFIER` (language specification §5.4). This is **not** a semantic-only rule. |
| `const` requires initializer | **Explicitly specified (syntax)** | Grammar: `CONST, IDENTIFIER, ASSIGN, expression` (language specification §5.3). |
| `let` optional initializer | **Explicitly specified (syntax)** | Grammar allows omitted initializer. |
| Block scope | **Explicitly specified (design decision)** | Official v0.1 decision: block scope (language specification §3; ZSS-01). Detailed resolution algorithm **not yet specified**. |
| Exact declaration / redeclaration rules | **Not yet specified** | Language specification §6; ZSS-01 §10.2. |
| Uninitialized variable read | **Not yet specified** | ZSS-01 §10.2. |
| Constant reassignment after binding | **Not yet specified** | ZSS-01 §10.2 (distinct from syntactic presence of initializer). |
| Name resolution | **Not yet specified** | Language specification §6; ZSS-01 §10.2. |
| Function arity (argument count) validation | **Not yet specified** | ZSS-01 §10.2. |
| `return` outside a function | **Implied semantic / explicit boundary** | Grammar permits `return` wherever a statement is allowed; “Later semantic analysis must reject `return` outside a function” (language specification §5.3). |
| Whether a value is callable | **Not yet specified (semantic/runtime)** | Language specification §5.4; ZSS-01 §10.2. |
| Logical short-circuit | **Not yet specified (runtime/semantic evaluation)** | ZSS-01 §10.2; grammar defines grouping only. |
| Truthiness | **Not yet specified** | ZSS-01 §10.2. |
| Type coercion | **Not yet specified** | ZSS-01 §10.2. |
| Division by zero | **Not yet specified (runtime)** | ZSS-01 §10.2. |
| Cross-type equality behavior | **Not yet specified** | ZSS-01 §10.2. |
| Parameter uniqueness within one function | **Not yet specified** | No complete semantic rule in v0.1 text (**UNKNOWN** beyond absence). |
| Nested function / first-class function rules | **Not yet specified / Deferred** | Beyond current v0.1 executable model. |

**Rule for this document:** categories marked **Not yet specified** or **Deferred** must not be treated as enforceable official rules until a later Owner-approved semantic specification exists.

---

## 7. Responsibility Matrix

| Component | Owns | Must not own | Expected input | Expected output | Downstream |
|---|---|---|---|---|---|
| **Lexer** | Tokenization; lexical limits; lexical diagnostics | Grammar; semantics; runtime | Source text | Token stream or lexical error | Parser |
| **Parser** | Grammar matching; syntax diagnostics; parse nesting/node accounting | Semantic meaning; silent repair of invalid AST graphs; runtime | Token stream | AST (on success) or syntax diagnostic | AST validation / Semantic Analysis |
| **AST model** | Immutable node data; declared structural fields | Proving source matched grammar | Construction by Parser (future) | Structured program representation | ZASI, Semantic Analysis |
| **ZASI / AST validation** | Structural integrity (types, spans, order, cycles, reuse, structural limits) | Grammar conformance proof; semantic meaning | AST | Validation result / structural diagnostics | Semantic Analysis |
| **Semantic Analysis** | Meaning rules (when specified and implemented) | Re-lexing/re-parsing as authority; grammar redesign; silent mutation of canonical AST | Structurally valid AST | Semantic findings / semantic diagnostics; admissibility for runtime | Runtime |
| **Runtime** | Execution of admissible programs; dynamic errors | Static scope design; grammar acceptance | Semantically admissible program representation | Execution results / runtime errors | Host / user |

**Critical boundary (OBSERVED from ZSS-01 / ZSS-03 / boundaries.md):**

- AST validation success ≠ grammar conformance.
- Grammar success ≠ semantic validity.
- Semantic success (when defined) ≠ absence of all runtime failures.

---

## 8. Syntax-Valid but Potentially Semantically Invalid Examples

Examples use only rules grounded in existing text. Where the semantic rule is incomplete, the example is **illustrative / unresolved**, not normative rejection policy.

### 8.1 `return` outside a function

```zen
return 1
```

| Aspect | Classification |
|---|---|
| Syntactic validity | **Valid** under statement productions (language specification §5.3) |
| Semantic concern | `return` outside function — specification states semantic analysis **must** reject |
| Reporting layer | Semantic Analysis (when implemented) |
| Rule status | **Implied / directed** by language specification §5.3; detailed diagnostic contract **not yet fully specified** |

### 8.2 Use of an identifier with no visible declaration

```zen
let x = y
```

| Aspect | Classification |
|---|---|
| Syntactic validity | **Valid** (`let` with initializer expression that is an identifier) |
| Semantic concern | Whether `y` must be resolved / declared |
| Reporting layer | Semantic Analysis (if name-resolution rules so decide) |
| Rule status | **Not yet specified** (language specification §6) |

### 8.3 Reassignment to a name bound with `const` (illustrative)

```zen
const n = 1
n = 2
```

| Aspect | Classification |
|---|---|
| Syntactic validity | **Valid** as two statements: `const` decl + assignment to bare identifier |
| Semantic concern | Constant reassignment |
| Reporting layer | Semantic Analysis (if rules so decide) |
| Rule status | **Not yet specified** (ZSS-01 §10.2) |

### 8.4 Call with “wrong” argument count (illustrative)

```zen
fn f(a) { return a }
f(1, 2)
```

| Aspect | Classification |
|---|---|
| Syntactic validity | **Valid** (function decl + call with argument list) |
| Semantic concern | Arity mismatch |
| Reporting layer | Semantic Analysis and/or Runtime depending on future rules |
| Rule status | **Not yet specified** (ZSS-01 §10.2) |

### 8.5 Assignment target form (contrast — syntax, not semantic-only)

```zen
(a) = 1
```

| Aspect | Classification |
|---|---|
| Syntactic validity | **Invalid** — assignment target must be bare `IDENTIFIER` (grammar) |
| Reporting layer | **Parser** (grammar rejection) |
| Rule status | **Explicitly specified (syntax)** |

This contrast case must not be moved into Semantic Analysis.

---

## 9. Diagnostics Boundary

| Kind | Owner | Typical trigger |
|---|---|---|
| Lexical diagnostics | Lexer | Bad token, lexical limit, unterminated comment/string |
| Syntax diagnostics | Parser | Production mismatch, syntax resource limit |
| Structural diagnostics | ZASI / AST validation | Invalid node graph, span contract break, structural limit |
| Semantic diagnostics | Semantic Analysis | Meaning-rule violations (when specified) |
| Runtime errors | Runtime | Dynamic failures during execution |

**Design expectations (architectural, not an API spec):**

- Diagnostics should identify **responsible component**.
- Source location should be available where the phase has source mapping (lexer/parser already oriented this way; AST carries spans).
- Existing parser scaffolding includes `ParseError` with location fields (**OBSERVED**). A full cross-phase diagnostic catalog is **DEFERRED**.

Do not invent a global error-code registry in this document.

---

## 10. AST and Semantic Analysis Relationship

### 10.1 Consumption without grammar change

Semantic Analysis, when authorized and implemented, is expected to **consume** a structurally validated AST that corresponds to the official grammar. It must not:

- Redefine grammar productions.
- Treat AST structural validation as grammar proof.
- Silently mutate canonical AST in ways forbidden by existing architecture (ZASI / RULES.md principles).

### 10.2 Architectural expectations (non-implementing)

| Concern | Expectation |
|---|---|
| Source locations | Prefer existing span / identity contracts on AST nodes |
| Identifier references | Resolution is a semantic concern; AST may hold identifier spellings/spans without resolving binding |
| Scope information | Derived by Semantic Analysis under block-scope decision; not a Parser duty |
| Semantic findings | Explicit, inspectable results (pass/fail + diagnostics) — exact schema **DEFERRED** |
| Error reporting | Semantic-owned diagnostics; not reclassified as syntax errors |

No new AST node types are introduced by ZSS-04.

---

## 11. Phase Ordering and Failure Boundaries

Conceptual sequence (**OBSERVED** intended architecture; phases not all implemented):

1. **Lex** — fail closed on lexical error.  
2. **Parse** — requires successful token stream; fail closed on syntax error.  
3. **AST structural validation** — applies to constructed trees; fail closed on structural contract break when validation is required by the consuming path.  
4. **Semantic Analysis** — requires structurally valid AST; fail closed on specified semantic violations (when phase exists).  
5. **Runtime** — requires prior phase success under the project’s strict error-handling decision; may still fail dynamically.

**Strict error handling (OBSERVED):** language specification §7 — first lexical, syntax, semantic, or runtime error stops the current program.

**NOT_TESTED / NOT implemented:** end-to-end pipeline enforcement for parse + semantic + runtime.

---

## 12. Compatibility and Future Extensibility

- ZSS-04 must not couple future independently governed ZEN subsystems to unapproved Semantic Analysis internals.
- Contracts between Parser, AST/ZASI, Semantic Analysis, and Runtime should remain **explicit**.
- Grammar Version evolution remains under ZSS-02 **principles** (reference only for reconstructed on-disk text) and Owner approval.
- New semantic rules require Owner-approved specification before implementation authorization.

---

## 13. Open Questions and Deferred Decisions

| ID | Question | Why it matters | Existing evidence | Decision required | Blocks ZSS-05? |
|---|---|---|---|---|---|
| OQ-01 | Exact redeclaration rules in the same scope | Determines semantic acceptance of repeated `let`/`fn` names | Spec §6; ZSS-01 §10.2 | Owner-approved semantic rule set | **Likely yes** for a semantic-spec milestone |
| OQ-02 | Uninitialized `let` read behavior | Static error vs runtime error vs defined value | ZSS-01 §10.2 | Explicit rule + phase assignment | Likely yes |
| OQ-03 | `const` reassignment rule details | Static rejection policy | ZSS-01 §10.2 | Explicit rule | Likely yes |
| OQ-04 | Name-resolution algorithm (shadowing, globals, parameters) | Core of Semantic Analysis | Spec §6; block scope decision | Full resolution specification | Yes |
| OQ-05 | Function arity checking phase | Semantic vs runtime | ZSS-01 §10.2 | Phase assignment + rule | Likely yes |
| OQ-06 | Callability checking phase | Semantic vs runtime | Spec §5.4 | Phase assignment | Likely yes |
| OQ-07 | Evaluation rules (short-circuit, truthiness, coercion, ÷0, equality) | Runtime semantics | ZSS-01 §10.2 | Runtime/semantic specification | Partially; may split across milestones |
| OQ-08 | Parameter name uniqueness | Local binding integrity | Absence in v0.1 text | Confirm rule or explicit non-rule | Preferred before analyzer design |
| OQ-09 | Semantic diagnostic catalog | Tooling and conformance | Parser scaffolding only | Design when analyzer authorized | No (can follow) |
| OQ-10 | Relationship of ZSS-05 to semantic rule specification vs analyzer design | Sequencing | Roadmap mention only | Owner milestone definition | Defines ZSS-05 itself |

No open question above is silently resolved by ZSS-04.

---

## 14. Relationship to ZSS-01 … ZSS-05

| Document | Relationship |
|---|---|
| ZSS-01 | Baseline for architecture, unresolved semantic list, component separation — preserved |
| ZSS-02 | Governance reference only; not rewritten |
| ZSS-03 | Syntax conformance design; ZSS-04 does not reopen grammar conformance tests |
| **ZSS-04** | Semantic **boundary** (this document) |
| ZSS-05 | Future work; not authorized or specified here |

---

## 15. Change-Control Rules

1. This document does not modify the official grammar, ZSS-01, ZSS-02, or ZSS-03 text except by reference.
2. Semantic rule completion requires a separate Owner-approved specification and separate implementation authorization.
3. Revisions to ZSS-04 require Owner review; revision number increases.
4. Conflicts with the official language specification: the specification wins; this document must be corrected.
5. Governance conflicts: stop and request Owner clarification.

---

## 16. Document History

| Revision | Date | Status | Summary |
|---|---|---|---|
| 1 | 2026-11-24 | DRAFT — AWAITING OWNER REVIEW | Initial Semantic Boundary design specification |

---

**End of ZSS-04 — Semantic Boundary**

**Authority:** This document defines architectural boundaries only. It does not authorize Semantic Analysis implementation, parser implementation, grammar changes, runtime implementation, or production-code modification. Owner approval is required before treating ZSS-04 as finalized and before any ZSS-05 or implementation phase.
