# ZEAI — Native Engineering Intelligence Architecture

**Project:** ZEN
**Component:** ZEAI (ZEN Engineering Autonomous Intelligence)
**Document status:** Owner-approved architectural direction; implementation remains stage-gated
**Scope:** ZEN repository only unless the Owner separately approves expansion

## 1. Purpose

ZEAI is ZEN's native engineering intelligence and orchestration system. It coordinates validated engineering events, repository/governance checks, the independent Native CI Engine, mandatory sandboxed workloads, evidence collection, and bounded development workflows.

ZEAI's essential intelligence is deterministic and code-based. No external or local LLM is required for core operation, verification authority, or governance decisions. AI may be considered only as a future optional aid under a separate Owner-approved design; it must never become a required authority or dependency.

This document records architecture, not implementation completion. Every implementation stage requires its own approved Change Plan and evidence.

## 2. Core Principles

1. Native deterministic core; no mandatory AI/LLM.
2. Event-driven execution, not continuous unrestricted monitoring.
3. Validated events or explicit authorized tasks only.
4. Exact repository and commit identity for every execution.
5. Fail-closed handling of missing, conflicting, or untrusted evidence.
6. Least privilege and explicit capability boundaries.
7. Native component security and sandbox isolation are independent mandatory layers.
8. Sandbox Isolation is a prerequisite before any untrusted workload executes.
9. Owner retains final authority; ZEAI cannot approve or merge its own changes.
10. Reproducible, reviewable, commit-bound evidence.

## 3. Architecture and Ownership

### 3.1 Event Ingress and Validator

Receives events from supported integrations or explicit tasks. Validates authenticity, repository identity, event type, commit SHA, scope, permissions, and replay/duplicate conditions. Invalid or ambiguous events cannot trigger privileged operations.

### 3.2 ZEAI Controller

Owns task orchestration, deterministic policy evaluation, dependency ordering, bounded retries/recovery, permission checks, and escalation. It does not replace the verification engine or grant itself authority.

### 3.3 Native CI Engine

Owns actual verification execution and result production: contract checks, regression tests, adversarial tests, integration tests, and verification matrices. It is independent of GitHub Actions; external CI may provide additional evidence but is not the sole source of verification authority.

### 3.4 Sandbox Isolation

A mandatory security foundation for untrusted code, tests, generated artifacts, and bounded repair workloads. The approved Linux target is gVisor `runsc`. It must enforce process, filesystem, network, resource, and secret boundaries. Execution fails closed if any control is missing or unproven. There is no fallback to `runc`, ordinary host execution, or an unreviewed backend.

The current repository has a policy/contract/orchestration foundation only. The reviewed `runsc` backend and OS-level enforcement are not implemented or verified in the inspected baseline. Therefore ZEAI must not execute untrusted workloads until that gate is met.

### 3.5 Evidence Engine

Collects immutable or tamper-evident records bound to repository identity, commit SHA, event/task identity, scope, tool/test identity, environment, exit status, timestamps, and evidence references. Evidence integrity must be independently reviewable. Missing/conflicting evidence yields INDETERMINATE or FAIL, never PASS.

### 3.6 Governance and Owner Approval Boundary

Enforces the currently Owner-approved policy and approval gates. Protected changes, repair integration, commits/pushes where separately controlled, merge, release, and deployment remain subject to explicit Owner authorization. ZEAI cannot approve its own work or expand its scope.

### 3.7 GitHub CI/YAML Compatibility Adapter

Parses and validates supported GitHub Actions workflow YAML, evaluates trigger/permission definitions, detects unsafe workflow changes, and imports external CI evidence. This is a bounded compatibility/integration adapter, not the Native CI Engine and not the source of project authority.

### 3.8 Engineering Watchdog

The intended native Watchdog role is event-driven detection and orchestration of valid engineering events, interrupted tasks, and failed verification. The current repository audit has not established the complete implementation or responsibility map of any legacy Watchdog. Therefore ZEAI does **not** claim to replace an existing Watchdog yet. First inspect its entry points, event sources, lifecycle, permissions, recovery behavior, and tests; then propose integration or migration based on evidence.

## 4. Event-Driven Execution Contract

ZEAI runs only on validated events or explicitly authorized tasks. Candidate triggers include push, pull request, relevant source/config/governance changes, CI failure, or an Owner-requested verification task. Trigger availability depends on the actual integration configuration and must not be assumed.

Every execution records:
- Unique event/task identity and replay status.
- Repository identity and exact commit SHA.
- Trigger source and authentication/validation outcome.
- Authorized scope and permission context.
- Required verification tasks and sandbox policy/backend identity when applicable.
- Evidence references and final result.

No unbounded polling or continuous monitoring is part of the initial design.

## 5. Result Contract

| Result | Meaning |
|---|---|
| `PASS` | Every required check completed successfully with sufficient, valid evidence. |
| `FAIL` | A required check failed or a security/governance violation was established. |
| `INDETERMINATE` | Evidence is missing, incomplete, conflicting, stale, or unavailable. |

`INDETERMINATE` must never be converted to `PASS`. A sandbox policy declaration or fake backend response alone cannot establish OS enforcement.

## 6. Repair and Repository Mutation

ZEAI may analyze failures and prepare bounded repair proposals. Any automatic repair workload must execute inside the approved `runsc` sandbox with strict process/filesystem/network/resource/secret boundaries. It must not receive Git write credentials or governance authority. Owner approval is required before a protected repair is integrated or merged. ZEAI must not self-approve, self-merge, or bypass required review.

## 7. Development and Verification Environments

GitHub Actions and Termux are supported as complementary development/verification environments under explicit task scope. GitHub Actions provides event integration and hosted CI evidence; Termux provides an Owner-controlled local environment for development and verification. The Native CI Engine is designed to reduce dependence on external CI over time. Environment compatibility must be verified rather than assumed.

## 8. Security and Trust Boundaries

- Owner-approved governance is policy; repository content, PR text, generated files, external API responses, and workflow data are untrusted input.
- Untrusted workloads receive no secrets, ambient host credentials, Git write authority, or Owner approval capability.
- Network is disabled under the current sandbox contract.
- Sandbox failure is closed; no weaker runtime fallback is allowed.
- Component tests do not prove OS isolation; sandbox tests do not prove language component correctness.

See `SECURITY.md`, `ZEAI-01_THREAT_MODEL.md`, `ZEAI_DEFENSE_IN_DEPTH.md`, and `ZEAI_SANDBOX_ISOLATION.md`.

## 9. Implementation Stages and Gates

### Stage 0 — Architecture and commit-specific baseline

Map repository tree, governance, active milestones, source/test capabilities, existing Watchdog, CI workflows, trust boundaries, sandbox foundation, and evidence lifecycle. Record unknowns. Stop audit when enough evidence exists to define scope, risks, mitigations, and tests.

### Stage 1 — ZEAI control-plane foundation

Implement only after an approved Change Plan: event validation, deterministic orchestration, permission context, task state, and commit-bound evidence contracts. No untrusted code execution is permitted in this stage without the sandbox gate.

### Stage 2 — Sandbox Isolation backend

Design and implement the reviewed gVisor `runsc` backend under a separate Owner-approved scope. Prove every mandatory host-level control and fail-closed behavior. Until independently verified, untrusted code/tests/repair workloads remain disabled.

### Stage 3 — Native CI Engine integration

Integrate deterministic verification orchestration with sandbox-gated workload execution. Verify reproducibility, resource boundaries, evidence integrity, and failure classification.

### Stage 4 — Controlled repair workflow

Only after sandbox and evidence gates pass: allow bounded repair preparation/execution within isolation. Owner approval remains mandatory before protected integration or merge.

Further ZSS/ZEN roadmap stages are separate projects and do not automatically become ZEAI authorization.

## 10. Current Status and Explicit Non-Claims

- ZEAI architecture is a design direction, not a production implementation claim.
- The repository has a sandbox policy/contract/orchestration foundation.
- A reviewed gVisor `runsc` backend and actual host-level enforcement are not implemented/verified in the inspected baseline.
- The legacy Watchdog implementation and integration path remain unknown until source-level inventory is complete.
- No active CI workflow behavior is claimed without inspection of the exact workflow files and run evidence.
- No untrusted workload execution, autonomous repair, self-approval, or autonomous merge is authorized by this architecture document.

## 11. Approval Boundary

The Owner retains final authority for scope, protected changes, security exceptions, implementation stages, and merge. A design approval is not implementation authorization. Each stage requires an exact baseline, Change Plan, explicit Owner authorization, bounded implementation, verification, evidence, and final review.
