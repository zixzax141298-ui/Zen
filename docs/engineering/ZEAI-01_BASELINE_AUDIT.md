# ZEAI — Repository Baseline Audit

**Project:** ZEN
**Component:** ZEAI
**Audit date:** 2026-11-22
**Baseline branch:** `main`
**Baseline commit:** `e2ee74254e56b1193089e83a8a19b37713dd47c8`
**Audit mode:** Read-only repository inspection
**Status:** Documentation/source-surface baseline; not a full security audit
**Implementation authorization:** Not granted by this audit

## 1. Purpose and Method

This audit refreshes the ZEAI baseline against the exact `main` commit above. It inspects the current governance files, ZEAI design documents, sandbox package files, sandbox tests, and repository listings. It does not claim a complete source audit, full workflow inventory, live host isolation test, or penetration test.

## 2. Repository and Governance Evidence

**OBSERVED:** `main` points to `e2ee74254e56b1193089e83a8a19b37713dd47c8` at the time inspected.

**OBSERVED:** `AGENTS.md`, `AI_RULES.yaml`, `RULES.md`, and `SECURITY.md` exist at the repository root.

**OBSERVED:** `AGENTS.md` and `AI_RULES.yaml` state ZB-07 is REOPENED and highest priority, and ZIIF-01 is PAUSED pending ZB-07 completion. The current `RULES.md` at this baseline still says ZB-07 CLOSED and ZIIF-01 ACTIVE. This is a real governance inconsistency. The proposed replacement `RULES.md` in this patch reconciles it to the current Owner-approved state; do not change milestone implementation based on this documentation patch.

**OBSERVED:** `AGENTS.md` requires Owner approval for repository documentation changes and separately lists commit/push/merge/release/deployment as approval-controlled operations. This Owner-directed patch authorizes only the listed documentation scope and PR preparation; it does not authorize merge.

## 3. ZEN Language Baseline

**OBSERVED from root `README.md`:** language v0.1 grammar is specified; Lexer, AST node model, and package configuration are reported implemented; public API exports Lexer only; Parser is reported not implemented; Semantic Analysis, Interpreter, and Runtime are planned.

This is README-reported status, not a complete source/test capability audit. A formal grammar or AST model does not prove parser or runtime availability.

## 4. Active Milestones

**OBSERVED from `AGENTS.md` and `AI_RULES.yaml`:**

- ZB-07: REOPENED; highest active milestone; implementation and verification in progress under `docs/engineering/ZB-07_CHANGE_PLAN.md` v2.0.
- ZIIF-01: PAUSED until reopened ZB-07 completion; preserve existing implementation and fingerprint v1 contract.

**OBSERVED conflict:** current `RULES.md` contradicts those two governance sources. This patch updates `RULES.md` to align. No ZB-07/ZIIF-01 source implementation is changed.

## 5. Sandbox Source Baseline

**OBSERVED:** `src/zen/sandbox/` contains `__init__.py`, `contracts.py`, `policy.py`, and `runtime.py`.

**OBSERVED in `contracts.py`:** defines required controls for process isolation, filesystem isolation, network isolation, resource limits, and secret isolation; backend protocol exposes `probe` and `execute`.

**OBSERVED in `policy.py`:** policy defaults are 10 seconds wall-clock, 10 CPU seconds, 256 MiB memory, and 1 MiB per output stream; network-enabled policy is rejected; workspace path containment is checked. These are policy values, not proof of backend enforcement.

**OBSERVED in `runtime.py`:** execution rejects a missing backend; rejects shell command strings; constrains cwd to workspace; filters environment variables; rejects missing required capability controls and empty evidence before backend execution; validates output types/limits.

**OBSERVED in `tests/test_sandbox.py`:** tests use a fake backend for policy and orchestration behavior, including fail-closed cases.

**NOT IMPLEMENTED / NOT VERIFIED:** a reviewed gVisor `runsc` backend, actual host process/filesystem isolation, enforced network and resource boundaries, and independent host-level enforcement evidence.

**DERIVED:** the current package is a fail-closed orchestration foundation. It is not a completed sandbox runtime and must not execute untrusted workloads until the real `runsc` backend and all required controls pass independent verification.

## 6. ZEAI Architecture Baseline

**OBSERVED:** the repository contains `ZEAI-01_ARCHITECTURE.md`, `ZEAI-01_CHANGE_PLAN.md`, `ZEAI-01_THREAT_MODEL.md`, `ZEAI_DEFENSE_IN_DEPTH.md`, and `ZEAI_SANDBOX_ISOLATION.md`.

**Owner-approved design direction:** native deterministic/code-based core; no mandatory external/local LLM; event-driven execution; independent Native CI Engine; GitHub CI/YAML compatibility; Termux and GitHub Actions as complementary engineering environments; mandatory Sandbox Isolation using gVisor `runsc`; fail-closed with no `runc` or host fallback; bounded repair only inside isolation and Owner approval before integration/merge.

These are architecture decisions, not claims that the corresponding capabilities are implemented.

## 7. Watchdog and CI Baseline

**UNKNOWN:** complete implementation and responsibility map of any legacy Watchdog has not been established by this audit. ZEAI must not claim it replaces the legacy Watchdog until source entry points, event sources, lifecycle, permissions, recovery, and tests are inspected.

**UNKNOWN:** a complete inventory of `.github/workflows`, workflow permissions/triggers, branch protection, runner configuration, and current CI run evidence was not completed in this documentation-focused audit. No claim is made that CI is present or absent.

## 8. Risk and Readiness Table

| Area | Evidence status | Assessment / next action |
|---|---|---|
| Governance milestone state | OBSERVED | `RULES.md` conflicts with `AGENTS.md`/`AI_RULES.yaml`; reconcile through approved docs patch |
| ZEN language capabilities | OBSERVED from README only | Source/test inventory still needed for definitive status |
| Sandbox orchestration | OBSERVED | Fail-closed foundation exists; not a production isolation backend |
| gVisor `runsc` backend | NOT IMPLEMENTED / NOT VERIFIED | Blocking prerequisite before untrusted workload execution |
| Process/filesystem/network/resource/secret enforcement | NOT TESTED at OS level | Require real-host tests and independent evidence |
| Legacy Watchdog | UNKNOWN | Inspect source and tests before integration/replacement claim |
| GitHub Actions configuration | UNKNOWN | Inspect full tree/workflows and permissions before relying on CI |
| Commit-bound evidence engine | Design requirement | Implementation and integrity guarantees not verified |
| Autonomous merge | Prohibited | Preserve Owner-controlled integration |

## 9. Audit Exit Criteria

For the present design review, enough evidence is available to define architecture, immediate scope, critical security prerequisite, major risks, mitigations, and verification gates. Remaining unknowns are recorded above. Do not extend this audit indefinitely; resolve those unknowns when preparing the corresponding implementation Change Plan.

Before any ZEAI implementation stage, refresh the baseline SHA and inspect only the source/workflow/permission areas required by that stage. Record exact paths, commit, environment, commands, and outcomes.

## 10. Conclusion and Authorization

The current repository has a sandbox policy/contract/orchestration foundation that fails closed without a reviewed backend. It does not yet have verified gVisor `runsc` OS enforcement. The current `RULES.md` has a genuine milestone-status conflict with `AGENTS.md` and `AI_RULES.yaml`. The ZEAI architecture documents require correction to make sandbox a prerequisite and to avoid unsupported Watchdog replacement claims.

This audit supports documentation reconciliation and continued staged design. It does not establish readiness to execute untrusted workloads or authorize ZEAI production implementation, CI activation, dependency changes, autonomous repair, or merge.
