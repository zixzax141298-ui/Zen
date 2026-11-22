# ZEAI — Defense in Depth: Native Component Security and Sandbox Isolation

**Status:** OWNER-APPROVED ARCHITECTURAL DESIGN
**Implementation status:** Partial orchestration foundation only; OS isolation not implemented/verified

## 1. Core Decision

ZEN security uses two complementary and independently verified layers:

1. **Native Component Security** — each language/engineering component enforces its own contracts and validation.
2. **Execution Isolation** — ZEAI Sandbox Isolation contains the impact of untrusted workloads.

Neither layer replaces the other. Passing component tests does not prove OS isolation; passing sandbox tests does not prove language component correctness.

## 2. Native Component Responsibilities

| Component | Responsibility |
|---|---|
| Lexer | Character processing, token recognition, lexical validation, input boundaries, diagnostics |
| Parser | Grammar/syntax enforcement, nesting and recursion protection, syntax diagnostics |
| AST | Canonical representation, node/child contracts, source identity, structural invariants |
| ZASI | AST structural integrity, graph validation, cycle/reuse detection, structural limits |
| Semantic Analysis | Semantic validation, symbol/scope checks, type constraints, diagnostics |
| Compiler | Correct transformation between validated representations |
| Runtime | Execution semantics, runtime validation, resource behavior, diagnostics |
| ZEAI | Event validation, orchestration, verification coordination, sandbox invocation, evidence collection; not a replacement for component contracts |

## 3. Mandatory Sandbox Isolation

Sandbox Isolation is a mandatory foundation before ZEAI runs untrusted code, tests, generated artifacts, or bounded repair workloads.

The approved Linux target is **gVisor `runsc`**. The backend must prove actual enforcement for the exact host and policy across:

- Process containment and termination.
- Filesystem/workspace isolation.
- Network isolation (network disabled under the current contract).
- CPU, memory, wall-clock, and output limits.
- Secret/credential isolation.

Missing or unproven controls must reject execution. There is no silent fallback to `runc`, ordinary host execution, or a weaker backend. A capability declaration or policy object alone is not OS enforcement evidence.

## 4. ZEAI Responsibility Separation

| Subsystem | Responsibility |
|---|---|
| ZEAI Controller | Task orchestration, deterministic policy evaluation, authorization checks |
| Native CI Engine | Actual contract, regression, adversarial, and integration verification |
| Sandbox Isolation | OS-enforced workload containment |
| Evidence Engine | Commit-bound, reviewable verification and enforcement records |
| Owner | Final authority for protected changes, exceptions, and merge |

## 5. Independent Verification Questions

### A. Native Component Security

Does each component meet its own declared contract? Examples include malformed Lexer input, parser depth boundaries, invalid AST node/child structures, cycles/reused nodes, semantic rejection, compiler correctness, and runtime resource behavior.

### B. Sandbox Enforcement

Does the actual host runtime enforce process, filesystem, network, resource, and secret boundaries? Verify the real `runsc` backend, not only a fake backend.

Both answers require independent evidence tied to the tested commit, host, and policy.

## 6. Current Repository Evidence

**OBSERVED:** `src/zen/sandbox/` contains `contracts.py`, `policy.py`, and `runtime.py`. The runtime rejects execution when no backend is configured, rejects missing required capability controls or empty capability evidence, and validates request/environment/workspace constraints. `tests/test_sandbox.py` uses a fake backend to exercise policy/orchestration behavior.

**NOT IMPLEMENTED / NOT VERIFIED:** Reviewed gVisor `runsc` backend; actual host process and filesystem isolation; enforced network and resource boundaries; independent host-level proof.

The fake backend is test scaffolding, not a production isolation backend. The current foundation must not be described as completed Sandbox Isolation.

## 7. Architectural Constraints

- Preserve component ownership and existing contracts.
- Do not change grammar, AST semantics, or resource ceilings as part of sandbox work without separate Owner approval.
- Do not add dependencies or Python–Rust integration without an approved Change Plan.
- Do not execute untrusted workloads before the `runsc` enforcement gate passes.
- No autonomous merge or Owner-approval bypass.

## 8. Future Acceptance Criteria

1. Mandatory controls are enforced by actual `runsc` backend.
2. Missing controls reject execution.
3. No weaker runtime fallback exists.
4. Workloads cannot access unauthorized filesystem paths or secrets.
5. Network and resource boundaries are host-enforced.
6. Adversarial tests exercise the real isolation boundary.
7. Evidence is independently reviewable and tied to host, commit, and policy.
8. Native component security remains independently verified.
9. Owner approval remains mandatory for protected integration and merge.

## 9. Final Decision

Native Component Security and ZEAI Sandbox Isolation are both mandatory and complementary. This document records an approved architectural direction, not completed implementation or verified enforcement.
