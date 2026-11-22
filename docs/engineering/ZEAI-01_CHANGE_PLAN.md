# ZEAI — Engineering Change Plan

**Project:** ZEN
**Component:** ZEAI
**Status:** Proposed; Owner approval required per implementation stage
**Current scope:** Architecture, baseline, and documentation only

## 1. Objective

Develop ZEAI as ZEN's native, deterministic, event-driven engineering intelligence and verification orchestration system. The essential core must not require an external or local AI/LLM. ZEAI coordinates the Native CI Engine, mandatory Sandbox Isolation, governance, and commit-bound evidence while preserving Owner authority.

## 2. Approved Architectural Direction

- Native code-based deterministic core.
- Event-driven execution on validated events or explicit authorized tasks.
- GitHub Actions/YAML compatibility as a bounded integration.
- Independent Native CI Engine owns verification execution and results.
- Termux and GitHub Actions are complementary development/verification environments.
- Sandbox Isolation is mandatory before untrusted code, tests, generated artifacts, or repair workloads execute.
- Approved Linux isolation target: gVisor `runsc`; fail closed, no `runc` or host fallback.
- Bounded repair may be performed only inside the approved sandbox; Owner approval is required before protected integration/merge.
- No autonomous self-approval, self-merge, or authority expansion.

These are architecture decisions, not claims that the capabilities are implemented.

## 3. Scope and Exclusions

### Design scope

- Event identity and validation contract.
- ZEAI controller/orchestration boundaries.
- Native CI Engine responsibilities.
- Sandbox contract and enforcement gate.
- Evidence identity, integrity, and result states.
- GitHub CI/YAML adapter and Termux workflow boundaries.
- Owner approval and protected integration gates.

### Not authorized by this document

- Production source modifications.
- CI workflow activation or permission changes.
- Native runner or gVisor backend implementation.
- Dependency additions or Python–Rust integration.
- Autonomous repair activation.
- Autonomous approval, merge, release, or deployment.
- Changes to ZB-07 or ZIIF-01 scope/status.
- Deployment to repositories other than ZEN.

## 4. Stage 0 — Commit-Specific Baseline and Design

Inspect exact branch/commit, governance, source/test inventory, existing Watchdog, workflows, sandbox foundation, permissions, credentials, evidence lifecycle, and recovery paths. Record unknowns and stop when evidence is sufficient to define design, scope, risks, mitigations, and tests; do not prolong audit for non-blocking curiosity.

Acceptance:
- Exact baseline and source references recorded.
- Governance reconciled with Owner decisions.
- Existing Watchdog relationship described without unsupported replacement claims.
- Sandbox requirements and current implementation gap explicit.
- Threat model, implementation stages, and tests defined.
- Owner reviews the design.

## 5. Stage 1 — ZEAI Control-Plane Foundation

After separate approval: implement bounded event validation, deterministic orchestration, permission context, task lifecycle, and commit-bound evidence contracts. Do not execute untrusted code in this stage unless the sandbox gate in Stage 2 has passed.

Acceptance:
- Invalid/forged/replayed events cannot trigger privileged tasks.
- Every task is bound to exact repository and commit identity.
- Scope and permissions are explicit.
- Results are PASS, FAIL, or INDETERMINATE.
- Evidence is reproducible and reviewable.

## 6. Stage 2 — Mandatory Sandbox Backend

After separate security Change Plan and Owner approval: implement the reviewed gVisor `runsc` backend. Prove process, filesystem, network, resource, and secret isolation for the exact target host and policy. Reject execution if `runsc` or any control/evidence is unavailable. No fallback to `runc`, ordinary host execution, or another unreviewed backend.

Acceptance:
- Actual runtime identity/version is verified.
- Host-level enforcement evidence exists for every mandatory control.
- Adversarial tests exercise the real backend.
- Missing-control and startup failures are fail-closed.
- Independent review confirms evidence.

Until this stage passes, untrusted workload execution remains disabled.

## 7. Stage 3 — Native CI Engine Integration

After Stage 1 and Stage 2 gates: integrate the independent Native CI Engine with sandbox-gated workload execution, deterministic task selection, regression/adversarial/integration checks, bounded resources, and evidence capture.

Acceptance:
- Verification results bind to exact commit and policy.
- INDETERMINATE is never PASS.
- Local Termux and remote GitHub Actions evidence are distinguished.
- Failure and recovery behavior is bounded and tested.

## 8. Stage 4 — Controlled Repair Workflow

Only after the sandbox and evidence gates pass: permit bounded repair tasks inside isolation. Repair output is a proposal until reviewed. No workload gets Git write credentials or Owner authority. Owner approval is required before protected integration or merge.

## 9. Security and Verification Contract

- Least privilege and no secret inheritance.
- Network disabled under the current sandbox contract.
- Resource controls enforced by backend, not only declared in policy.
- Native component security independently tested.
- Sandbox OS enforcement independently tested.
- No external AI/LLM dependency for core operation.
- No fabricated tests, benchmarks, or CI results.

## 10. Evidence and Reporting

Each stage produces baseline, approved scope, Change Plan, actual file ledger, exact commands/environment/exit codes, test outcomes, security and compatibility assessment, evidence references, limitations, and recovery plan where applicable. Keep local and remote CI separate.

## 11. Approval Gates

| Gate | Required approval |
|---|---|
| G0 | Owner review of architecture and baseline |
| G1 | Owner approval for control-plane implementation |
| G2 | Owner approval for gVisor backend and host-level security work |
| G3 | Owner approval for Native CI integration after sandbox gate |
| G4 | Owner approval for bounded repair workflow |

Passing a gate does not automatically authorize the next stage. The Owner retains final authority for all protected changes and merge.

## 12. Current Authorization

Current ZEAI work in this document is architecture/baseline/documentation only. No production code, CI activation, dependency addition, gVisor backend, untrusted workload execution, autonomous repair, or autonomous merge is authorized by this plan.
