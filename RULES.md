# ZEN — Engineering Rules

## 1. Project Identity

ZEN is an independently evolving general-purpose programming language.

Core identities:
- ZEN: the language and project.
- ZSS: Zen Structured Syntax.
- ZASI: Zen Adaptive Structural Integrity.
- ZEAI: ZEN's native engineering intelligence and verification orchestration system.

These identities and their responsibilities must remain consistent across source, architecture, documentation, and engineering decisions.

## 2. Owner Authority

The Repository Owner is the final authority for project decisions, scope, approvals, exceptions, and repository integration.

No agent, automation, generated document, CI workflow, tool, or assistant-authored policy has authority above the Owner. An agent must not elevate its own interpretation into a higher authority, invent restrictions, or use repository text authored by an agent to override an explicit Owner decision. Governance documents express the Owner-approved rules currently in force; the Owner may explicitly amend or supersede them.

When an Owner instruction is ambiguous or two active Owner-approved requirements genuinely conflict, stop only the affected action, identify the exact conflict, and ask the Owner. Do not silently choose a permissive interpretation or broaden the task.

## 3. Core Engineering Values

ZEN development prioritizes:
1. Structural clarity.
2. Explicit and predictable semantics.
3. Safety and reliability.
4. Compatibility and maintainability.
5. Evidence-based engineering.
6. Clear component ownership.
7. Controlled and accountable evolution.

A fast implementation is not acceptable if it hides defects, weakens contracts, or transfers unresolved risk to another component.

### Decision Principles

Engineering decisions must apply the following principles:

1. **Evidence Before Claims:** conclusions must be traceable to
   observations, measurements, or clearly stated reasoning.
2. **Correctness Before Convenience:** do not trade correctness,
   safety, or contract integrity for superficial convenience.
3. **Purpose Before Features:** every feature must address an identified
   problem and state its intended outcome and success criteria.
4. **Architecture Before Implementation:** understand component
   ownership, interfaces, invariants, and dependencies before coding.
5. **Security and Integrity by Design:** account for trust boundaries,
   resource exhaustion, failure behavior, and data integrity from design.
6. **Owner Approval Before Consequential Changes:** recommendations,
   analysis, and verification do not grant change or integration authority.
7. **Innovation Claims Require Evidence:** claims of novelty or
   superiority require a problem statement, baseline comparison,
   alternatives, measurable advantages, trade-offs, and limitations.

### Self-Evolving Rule Governance

ZEN rules are subject to evidence-based evaluation. Reviews may be
triggered by new evidence, defects, conflicts, changed requirements,
architectural evolution, or periodic examination.

A rule evaluation examines its purpose, scope, authority, normative
status, effectiveness, limitations, failure modes, dependencies,
consistency, and compatibility impact.

An evaluation record identifies the rule and its purpose, scope,
authority, supporting evidence, limitations, affected dependencies,
compatibility impact, and recommendation.

Recommendations may include retaining, clarifying, revising,
deprecating, or retiring a rule. These recommendations do not create
a universal rule lifecycle and do not automatically change a rule's
normative or active status.

Evaluation authority is separate from change and approval authority.
No evaluator may modify, approve, activate, or retire a rule solely
because an evaluation recommends doing so. Actual changes follow the
applicable governance process and require the appropriate explicit
Owner approval.

Syntax and grammar rules remain governed by the Owner-approved
ZSS-02 specification, including its rule identity, revision,
lifecycle, immutable Grammar Version, compatibility, and approval
requirements. This general principle does not replace or override ZSS-02.

## 4. Maturity and Evolution

ZEN pursues demonstrable maturity, not endless perfection.

- Define measurable milestone completion criteria.
- Address risks that block correctness, safety, or the milestone's purpose.
- Record non-blocking imperfections and known limitations.
- Do not allow endless polishing to prevent a demonstrably complete milestone.
- Revisit decisions when new evidence justifies doing so.
- Never let speed override integrity.

A milestone may be closed only when its required acceptance criteria are supported by evidence. Remaining limitations must be disclosed.

## 5. Change Governance

For repository changes:
1. Inspect the exact baseline.
2. Identify affected files and components.
3. Analyze architectural, semantic, security, and compatibility impact.
4. Prepare an exact Change Plan when required by the scope.
5. Obtain the Owner's explicit authorization for the specific change.
6. Change only the authorized scope.
7. Verify and record evidence.
8. Review the complete final diff, including untracked files.
9. Report actual repository state and limitations.

The Owner's explicit authorization applies to the scope stated. It does not authorize unrelated adjacent changes. A request to prepare a PR authorizes preparation and submission of that stated PR scope, but does not authorize merge unless the Owner explicitly says so.

## 6. Component Ownership

### Lexer
Character processing, token recognition, lexical correctness, and lexical diagnostics.

### Parser
Syntax recognition, grammar enforcement, program structure construction, syntax diagnostics, and parser-specific recursion/nesting safety.

### AST
Canonical program representation, explicit node/child contracts, source identity/location representation, and structural invariants.

### ZASI
AST structural integrity, node/child type validation, graph integrity, cycle/reuse detection, structural resource limits, and structural diagnostics.

### Semantic Analysis
Semantic interpretation of validated AST, name/scope analysis, type and semantic constraints, and semantic diagnostics. It must not silently mutate canonical AST.

### Compiler
Correct, validated transformation between declared program representations.

### Runtime
Execution semantics, runtime validation, behavior, and runtime diagnostics.

### ZEAI
Engineering-event validation, task orchestration, native CI coordination, security/governance enforcement, sandbox invocation, and evidence collection. ZEAI does not own or replace the internal correctness responsibilities of ZEN language components.

A component must not silently assume another component's responsibilities.

## 7. AST and ZASI Rules

- Canonical AST input must satisfy its declared structural contract.
- Source identity must not depend on traversal order or object memory addresses.
- Source identity and source span are separate concepts.
- Legacy AST compatibility must use an explicit adapter.
- Legacy nodes without required identity must not silently pass the canonical Semantic Analysis path.
- Source order must be represented and validated explicitly.
- AST validation must detect invalid node types, invalid children, cycles, reused nodes, invalid spans, and inconsistent source identity.
- Validation must not silently repair malformed canonical AST input.
- Validation must be deterministic and iterative where required by ZB-07.
- Validation results must be explicit and inspectable.

## 8. Diagnostics

Where applicable, diagnostics include a stable code, human-readable message, severity, primary and related source locations, and responsible component. Lexer, Parser, ZASI, Semantic Analysis, and Runtime retain their respective diagnostic ownership.

## 9. Resource Safety

Resource safety must be explicit and measurable. Distinguish parser nesting, AST depth, total nodes, expressions, statements, parameters, direct children, memory, and execution time. Resource-limit changes require technical justification, boundary tests, performance and memory analysis, compatibility analysis, and explicit Owner approval. Do not weaken limits merely to increase acceptance.

## 10. Compatibility

Compatibility changes must be classified and documented across source language, AST representation, parser/API, diagnostics, serialized artifacts, and tooling. Do not claim backward compatibility without relevant evidence. Legacy support must be explicit, bounded, and testable.

## 11. Testing and Verification

Test actual behavior, malformed inputs, boundaries, failure paths, regressions, compatibility, resource limits, and determinism where required. Reports distinguish executed, passed, failed, and unexecuted tests, and local results from remote CI. Never fabricate results.

## 12. Evidence and Documentation

Use these labels consistently:
- **OBSERVED** — directly inspected or measured.
- **DERIVED** — logically concluded from observations.
- **ASSUMED** — provisional and not verified.
- **UNKNOWN** — not established.
- **NOT_TESTED** — no relevant test was executed.
- **HISTORICAL** — valid for a prior baseline or branch but not necessarily the current one.

Implementation and verification are separate statuses. Documentation must describe actual behavior and project status, not planned capabilities as implemented features.

## 13. Security

Read `SECURITY.md` before security-sensitive work. Security-sensitive work includes input validation, parser/AST resource controls, filesystem access, dependencies, secrets, trust boundaries, sandboxing, CI permissions, and generated/cached artifacts. Security-boundary changes require explicit Owner authorization and documented impact analysis.

## 14. Milestone Status and Active Work

### Core-First Development

**Status: ACTIVE — current development direction.**

ZEN follows a Core-First development direction. Development prioritizes the
language core, runtime correctness, measurable verification, and architectural
integrity. Code implementation and tests take priority over speculative
documentation; documentation must follow verified implementation and reflect
actual repository evidence.

### CORE-01 — Interpreter Lifecycle and Failure Semantics

**Status: ACTIVE — read-only audit and test-matrix preparation.**

Owner-approved decisions:
- Interpreter lifecycle: `PERSISTENT`. Repeated calls to
  `Interpreter.interpret()` on the same instance preserve its globals/session.
- Direct Interpreter failure atomicity: `RETAIN`. State changes made before a
  runtime failure remain on that Interpreter instance.
- REPL failed submission: `ROLLBACK`. The REPL restores the submission's
  pre-execution state when that submission fails.

CORE-01 is currently limited to read-only audit, test-matrix preparation, and
reporting. These decisions do not authorize implementation. Separate explicit
Owner approval is required before implementation begins.

### Preserved Workstreams

#### ZSS — Zen Structured Syntax

**Status: PRESERVED — previously active and Owner-approved workstream.**

- **ZSS-01:** COMPLETED — Owner-approved Grammar Baseline &
  Design Foundation merged into main. Its approved baseline must remain
  unchanged.
- **ZSS-02:** OWNER-APPROVED FINAL SPECIFICATION.
  Documentation incorporation is authorized within the approved scope.
  Implementation and migration execution are not authorized.
- **ZB-07:** PAUSED by Owner direction. Preserve its implementation,
  Change Plan, evidence ledger, baseline references, and historical records.
- **ZIIF-01:** PAUSED. Preserve existing implementation and fingerprint
  v1 contract, including version, output format, node schemas, field order,
  and source-metadata exclusion from the v1 digest.

Paused workstreams are not deleted, abandoned, or permanently completed.
Reopening requires explicit Owner approval.

ZEN remains an extensible ecosystem. ZSS must not obstruct or invalidate
future independently governed ZEN subsystems.

Specification approval does not authorize implementation. Separate explicit
Owner approval is required before implementation or migration execution.

Core-First prioritization does not delete, invalidate, or silently close ZSS,
ZB-07, ZIIF-01, or other preserved workstreams. Their history and artifacts
must remain available and accurately classified.

## 15. ZEAI Security and Authority

- ZEAI's essential intelligence and verification core is deterministic and code-based; no external or local LLM is a required dependency for core operation or authority.
- ZEAI is event-driven and acts only on validated events or explicit authorized tasks.
- The Native CI Engine is responsible for verification; ZEAI orchestrates but must not fabricate or self-certify evidence.
- Sandbox Isolation is mandatory before ZEAI executes untrusted code, tests, generated artifacts, or repair workloads.
- The approved Linux isolation target is gVisor `runsc`. Execution is fail-closed. No fallback to `runc`, ordinary host execution, or an unreviewed backend is permitted.
- Native component security and OS-enforced sandbox isolation are independent, complementary requirements.
- Bounded automatic repair may occur only inside the approved sandbox. Owner approval is required before protected integration or merge.
- ZEAI must never approve or merge its own changes, expand its own authority, or bypass governance.
- Termux and GitHub Actions may be used as bounded development/verification environments; neither becomes the ultimate source of project authority.

## 16. Completion Reports

Every completed task reports baseline branch and commit, actual working-tree state, actual changed-file ledger, authorized scope, architecture/contract impact, exact verification commands and outcomes, local versus remote CI, security and compatibility implications, known limitations, unverified claims, and remaining work.
