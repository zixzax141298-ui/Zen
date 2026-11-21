# ZEN — Engineering Rules

## 1. Project Identity

ZEN is an independently evolving general-purpose programming language.

Core identities:
- ZEN: the language and project.
- ZSS: Zen Structured Syntax.
- ZASI: Zen Adaptive Structural Integrity.

These identities must remain consistent across source code, architecture,
documentation, and engineering decisions.

## 2. Core Engineering Values

ZEN development prioritizes:

1. Structural clarity.
2. Explicit and predictable semantics.
3. Safety and reliability.
4. Compatibility and maintainability.
5. Evidence-based engineering.
6. Clear component ownership.
7. Controlled and accountable evolution.

A fast implementation is not acceptable if it hides defects, weakens contracts,
or transfers unresolved risk to another component.

## 3. Maturity and Evolution Principle

ZEN pursues demonstrable maturity, not endless perfection.

Rules:
- Define measurable milestone completion criteria.
- Address risks that block correctness, safety, or the milestone's purpose.
- Record non-blocking imperfections and known limitations.
- Do not allow endless polishing to prevent a demonstrably complete milestone.
- Revisit decisions when new evidence justifies doing so.
- Never let speed override integrity.

A milestone may be closed only when its required acceptance criteria are supported
by evidence. Remaining limitations must be disclosed.

## 4. Authority and Change Governance

The Owner has final authority over project decisions.

Before repository modifications:
1. Inspect the baseline.
2. Identify affected files and components.
3. Analyze architectural, semantic, security, and compatibility impact.
4. Prepare an exact Change Plan.
5. Obtain explicit Owner approval.
6. Implement only the approved scope.
7. Verify and record evidence.
8. Review the final changes.

Approval for one change does not authorize unrelated or adjacent changes.

Commit, push, merge, release, publication, and deployment require separate
explicit authorization.

If governance documents conflict, stop the affected work and ask the Owner.
Do not silently select the more permissive interpretation.

## 5. Component Ownership

### Lexer
Responsible for:
- Character-level processing.
- Token recognition.
- Lexical correctness.
- Lexical diagnostics.

### Parser
Responsible for:
- Syntax recognition.
- Grammar enforcement.
- Program structure construction.
- Syntax diagnostics.
- Parser-specific recursion and nesting safety.

### AST
Responsible for:
- Canonical program representation.
- Explicit node and child contracts.
- Source identity and source-location representation.
- Structural invariants.

### ZASI
Responsible for:
- AST structural integrity.
- Node and child type validation.
- Graph integrity.
- Cycle and reused-node detection.
- Structural resource limits.
- Structural diagnostics.

### Semantic Analysis
Responsible for:
- Semantic interpretation of validated AST.
- Name and scope analysis.
- Type and semantic constraints.
- Semantic diagnostics.

Semantic Analysis must consume validated AST input and must not silently mutate
the canonical AST.

### Runtime
Responsible for:
- Execution of semantically valid programs.
- Runtime behavior and runtime diagnostics.

A component must not silently assume another component's responsibilities.

## 6. AST and ZASI Rules

- Canonical AST input must satisfy its declared structural contract.
- Source identity must not depend on traversal order or object memory addresses.
- Source identity and source span are separate concepts.
- Legacy AST compatibility must use an explicit adapter.
- Legacy nodes without required identity must not silently pass the canonical
  Semantic Analysis path.
- Source order must be represented and validated explicitly.
- AST validation must detect invalid node types, invalid children, cycles,
  reused nodes, invalid spans, and inconsistent source identity.
- Validation must not silently repair malformed canonical AST input.
- Validation must be deterministic and iterative where required by ZB-07.
- Validation results must be explicit and inspectable.

## 7. Diagnostics

Diagnostics must have a consistent model.

Where applicable, a diagnostic includes:
- Stable diagnostic code.
- Human-readable message.
- Severity.
- Primary source location.
- Related source locations.
- Responsible component.

Ownership:
- Lexer: lexical diagnostics.
- Parser: syntax diagnostics.
- ZASI: AST structural diagnostics.
- Semantic Analysis: semantic diagnostics.
- Runtime: runtime diagnostics.

Compatibility exceptions may remain where needed, but must not obscure the
underlying diagnostic contract.

## 8. Resource Safety

Resource safety must be explicit and measurable.

Distinguish:
- Parser recursion or nesting depth.
- AST structural depth.
- Total AST node count.
- Expression count.
- Statement count.
- Parameter count.
- Direct-child count.

Validation should avoid unnecessary repeated traversal and quadratic behavior.
Performance and memory claims require actual measurements.

Changes to resource limits require:
- A technical reason.
- Boundary tests.
- Performance considerations.
- Memory considerations.
- Compatibility impact analysis.
- Explicit Owner approval before implementation.

Do not weaken safety limits merely to increase the number of accepted programs.

## 9. Compatibility

Compatibility changes must be classified and documented.

Consider:
- Source-language compatibility.
- AST representation compatibility.
- Parser/API compatibility.
- Diagnostic compatibility.
- Serialized artifact compatibility.
- Tooling and test compatibility.

Do not claim backward compatibility without relevant evidence.

Legacy support must be explicit, bounded, and testable.

## 10. Testing and Verification

Tests must verify actual behavior, not merely implementation structure.

Required practices:
- Test normal and malformed inputs.
- Test boundary values.
- Test failure paths.
- Test regression behavior.
- Test compatibility paths.
- Test resource limits.
- Test deterministic behavior where required.
- Measure performance and memory when making related claims.

Every report must distinguish:
- Tests actually executed.
- Tests that passed.
- Tests that failed.
- Tests not executed.
- Local results and remote CI results.

Never fabricate test results, benchmarks, or CI status.

## 11. Evidence and Documentation

Use these labels:

- OBSERVED: directly inspected or measured.
- DERIVED: logically concluded from observations.
- ASSUMED: provisional and not verified.
- UNKNOWN: not established.
- NOT_TESTED: no relevant test has been executed.

Implementation and verification are separate statuses.

The file `docs/engineering/ZB-07_EVIDENCE.md` is the initial manual evidence
ledger for ZB-07. It records requirements, decisions, and verification evidence.

The integrated ZEEL Engineering Evidence System is a separate strategic proposal.
It is not implemented merely because the manual ledger exists.

Documentation must describe actual behavior and actual project status.
Do not describe planned features as implemented features.

## 12. Security

Read `SECURITY.md` before security-sensitive work.

Security-sensitive changes include:
- Input validation.
- Parser and AST resource controls.
- Filesystem access.
- Dependency and supply-chain changes.
- Secret handling.
- Trust boundaries.
- Generated or cached artifact handling.

Do not weaken security boundaries without explicit Owner approval and documented
impact analysis.

## 13. Active Milestone: ZB-07

**ZB-07 — AST Semantic Readiness & Source Identity Contract**

Approved technical baseline:
`0003a9b961810510c2d67c7851ab3f2e9327c5b2`
Baseline branch: `audit/zb06-strict-ast-contract`
Initial project baseline: `6bb9611eeec73a6c1bd543150eedc2d151b219a0`

Approved scope:
- Stable source identity.
- Immutable SourceIdentifier.
- SourceId and SourceSpan separation.
- Explicit legacy AST adapter.
- Source-order validation.
- Unified validate_ast contract.
- AST graph integrity validation.
- Cycle and reused-node detection.
- Explicit resource accounting and limits.
- Iterative deterministic validation.
- Parser safety and depth distinction.
- Common diagnostic model.
- Regression, performance, and memory verification.

Out of scope:
- Full Semantic Analysis implementation.
- Grammar redesign.
- Runtime rewrite.
- Optimizer or IR implementation.
- Python-Rust integration.

Do not expand the milestone without a separate Change Plan and Owner approval.

## 14. Long-Term Architecture Roadmap

The following are strategic proposals, not implemented features or automatic
implementation authorization:

1. Contract-First Architecture.
2. Deterministic Reproducibility.
3. Capability & Effect System.
4. Compatibility Intelligence.
5. ZASI Evolution Intelligence.
6. Architecture Observatory.
7. Proof-Carrying Artifacts.
8. Integrated ZEEL Engineering Evidence System.

Each proposal requires its own design, justification, impact analysis, and
approval before implementation.

## 15. Final Engineering Rule

Every material engineering decision must be explainable, traceable, and
verifiable.

Do not hide defects, invent evidence, silently change contracts, or broaden
approved scope.
