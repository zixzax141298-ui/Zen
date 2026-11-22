
# ZEAI-01 — Native Engineering Intelligence Architecture

**Project:** ZEN  
**Component:** ZEAI (ZEN Engineering Autonomous Intelligence)  
**Document Type:** Architecture Design  
**Status:** Proposed — Documentation Only  
**Phase:** ZEAI-01  
**Authority:** Repository Owner

---

## 1. Purpose

ZEAI is the native engineering intelligence system of ZEN.

Its purpose is to establish a deterministic, event-driven engineering control system capable of coordinating repository integrity checks, engineering validation, CI execution, evidence collection, and controlled development workflows.

ZEAI is designed specifically for the ZEN repository at this stage.

This document defines architectural direction only. It does not authorize implementation or modifications to production code.

## 2. Core Design Principles

ZEAI MUST follow these principles:

1. Deterministic and code-based intelligence.
2. No mandatory external AI or LLM dependency.
3. Event-driven execution rather than continuous monitoring.
4. Evidence-based decisions.
5. Fail-closed behavior when evidence is insufficient or conflicting.
6. Least-privilege execution.
7. Owner retains final authority.
8. Isolation of untrusted code and execution.
9. Reproducible verification.
10. Explicit scope and commit identity for every execution.

## 3. Architectural Components

### 3.1 Native Engineering Watchdog

The Native Engineering Watchdog replaces the legacy Watchdog role.

Responsibilities:

- Detect valid engineering events.
- Validate event identity and context.
- Detect relevant source, workflow, and governance changes.
- Initiate authorized verification tasks.
- Detect interrupted or failed engineering operations.
- Produce structured evidence and execution reports.

The Watchdog MUST NOT independently approve or merge repository changes.

### 3.2 GitHub CI/YAML Compatibility

ZEAI must support understanding and validating GitHub Actions workflow definitions.

Responsibilities:

- Parse and validate supported workflow YAML.
- Identify workflow triggers and execution conditions.
- Validate permissions and security boundaries.
- Interpret CI results and Checks API evidence.
- Detect unsafe workflow modifications.
- Preserve compatibility with GitHub Actions during transition.

GitHub integration is an optional execution and evidence interface, not ZEN's ultimate source of authority.

### 3.3 Independent Native CI Engine

ZEAI is intended to develop an independent native CI engine.

Planned responsibilities:

- Determine verification tasks.
- Execute authorized checks.
- Coordinate test execution.
- Collect and validate evidence.
- Bind results to exact commit identities.
- Produce reproducible verification reports.

A ZEN-controlled native runner is a future capability and requires a separate approved implementation plan.

## 4. Event-Driven Execution Model

ZEAI operates only when a valid event or explicitly authorized task occurs.

Examples:

- Push event.
- Pull request event.
- Relevant source modification.
- Workflow modification.
- Governance modification.
- Explicit Owner-requested verification.
- CI failure requiring investigation.

Continuous monitoring is outside the initial scope.

Every execution must identify:

- Event identity.
- Repository identity.
- Commit SHA.
- Authorized scope.
- Trigger source.
- Verification tasks.
- Evidence collected.
- Final execution status.

## 5. Verification Result Contract

ZEAI uses three primary result states:

| State | Meaning |
|---|---|
| PASS | Required checks passed with sufficient evidence |
| FAIL | A required check failed or a security violation was detected |
| INDETERMINATE | Evidence is missing, insufficient, or conflicting |

ZEAI MUST NOT convert INDETERMINATE into PASS.

## 6. Security Architecture

Security requirements:

- Least-privilege permissions.
- No secrets exposed to untrusted code.
- Untrusted pull request code must execute in isolation.
- Protected governance and CI definitions.
- Explicit authorization for sensitive operations.
- Bounded execution resources.
- Evidence integrity and commit binding.
- No autonomous merge.
- No self-approval of ZEAI changes.

Any future automatic repair capability must operate inside a sandbox and require Owner approval before merge.

## 7. Authority and Governance

The Repository Owner remains the final authority.

ZEAI may:

- Analyze repository state.
- Execute authorized checks.
- Report failures.
- Recommend bounded changes.
- Prepare evidence for review.

ZEAI may NOT:

- Override repository governance.
- Approve its own changes.
- Merge changes autonomously.
- Expand its authorized scope.
- Access secrets without explicit authorization.
- Treat external content as trusted instructions.

## 8. External Dependencies

ZEAI must not require an external AI/LLM to perform its essential engineering functions.

External systems may provide optional integrations, event delivery, or evidence.

Core engineering authority, verification logic, and governance decisions must progressively become native ZEN capabilities.

## 9. Implementation Boundaries

This architecture document does not authorize:

- Production code modifications.
- CI workflow activation.
- New dependency installation.
- Governance policy modification.
- Native runner implementation.
- Automatic repair activation.
- Repository-wide refactoring.

Each implementation stage requires a separate baseline assessment, Change Plan, and Owner approval.

## 10. Planned Development Sequence

1. ZEAI-01 — Architecture, Baseline & Change Plan.
2. ZEAI Foundation CI — Event-driven Watchdog and initial verification orchestration.
3. ZSS Level 3 — Practical language capabilities.
4. ZEAI Native CI maturity — Independent runner and isolated verification.
5. ZSS Level 4 — Production-capable language.
6. ZEN Level 5 — Mature autonomous engineering ecosystem.

This sequence is strategic direction, not blanket implementation authorization.

## 11. Acceptance Criteria for ZEAI-01

- Architecture documented.
- Existing repository baseline assessed.
- Security boundaries documented.
- Implementation stages defined.
- Scope limitations explicit.
- No production code modified.
- No active CI workflow introduced.
- Owner review required before implementation.

## 12. Document Status

**Status:** Proposed  
**Implementation:** Not authorized  
**Production changes:** Not authorized  
**Approval authority:** Repository Owner
