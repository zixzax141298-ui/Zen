ZEAI — Defense in Depth: Native Component Security & Sandbox Isolation

Status

OWNER APPROVED — ARCHITECTURAL DESIGN

This document records the approved architectural direction for layered security in ZEN and ZEAI.

This approval is limited to architecture and design. It does not authorize implementation, production changes, security-policy modifications, or scope expansion.

1. Core Principle

ZEN shall apply Defense in Depth through two complementary security layers:

1. Native Component Security.
2. Execution Isolation through ZEAI Sandbox Isolation.

Neither layer replaces the responsibility of the other.

Every component must enforce its own correctness, validation, and security contracts. Sandbox Isolation must contain the impact of workloads during execution.

2. Native Component Ownership

Component| Security and correctness responsibility
Lexer| Character processing, token recognition, lexical validation, input boundaries, lexical diagnostics
Parser| Grammar enforcement, syntax validation, nesting and recursion protection, syntax diagnostics
AST| Canonical representation, node and child contracts, source identity, structural invariants
ZASI| AST structural integrity, graph validation, cycle and reuse detection, structural resource limits
Semantic Analysis| Semantic validation, symbol and scope checks, type constraints, semantic diagnostics
Compiler| Correct and validated transformation of program representations
Runtime| Execution semantics, runtime validation, execution behavior and diagnostics

A component must not silently assume another component's responsibilities.

Security defects must be addressed at the correct architectural layer rather than hidden through unrelated workarounds.

3. ZEAI Sandbox Isolation

Sandbox Isolation is a mandatory security foundation for ZEAI workloads involving untrusted code, tests, generated artifacts, or bounded repair operations.

Its responsibilities include enforced boundaries for:

- Process isolation.
- Filesystem and workspace access.
- Network access.
- CPU, memory, wall-clock and output limits.
- Secret and credential isolation.
- Workload cleanup and containment.

The target Linux isolation runtime is gVisor "runsc".

The execution policy is fail-closed:

- Missing or unproven mandatory controls must prevent execution.
- No silent fallback to "runc".
- No fallback to ordinary host execution.
- Capability claims must be independently reviewable.
- A policy declaration alone is not evidence of OS-level enforcement.

4. ZEAI Security Responsibilities

Subsystem| Responsibility
ZEAI Controller| Task orchestration, policy evaluation and authorization
Native CI Engine| Contract, regression, adversarial and integration verification
Sandbox Isolation| Workload containment and execution boundaries
Evidence Engine| Traceable records of verification and enforcement evidence
Owner| Final authority for protected changes and merge approval

ZEAI must not self-approve protected changes, bypass governance, or grant itself additional authority.

5. Required Verification Separation

Two independent verification questions must be answered:

A. Native Component Security

Does each component satisfy its own declared contracts and security requirements?

Examples:

- Malformed Lexer input.
- Parser nesting and recursion boundaries.
- Invalid AST node and child structures.
- AST cycles and reused nodes.
- Semantic validation failures.
- Compiler transformation correctness.
- Runtime safety and resource behavior.

B. Sandbox Enforcement

Does the execution environment actually enforce the required isolation controls?

Examples:

- Process containment.
- Filesystem boundary enforcement.
- Network isolation.
- Resource enforcement.
- Secret isolation.
- Fail-closed behavior when a control is unavailable.

Passing component tests does not prove OS isolation. Passing Sandbox tests does not prove component correctness.

Both require independent evidence.

6. Current Implementation Status

OBSERVED:

- Sandbox foundation and orchestration contracts exist in "src/zen/sandbox/".
- The current runtime rejects execution when no reviewed backend is configured.
- The existing contract explicitly states that OS enforcement is not implemented.

NOT IMPLEMENTED:

- Reviewed gVisor "runsc" backend.
- Actual host-level process and filesystem isolation.
- Enforced network and resource boundaries.

NOT TESTED:

- Independent host-level isolation verification.
- Adversarial tests proving actual OS enforcement.

The existence of the Sandbox foundation must not be represented as completed Sandbox Isolation.

7. Architectural Constraints

This design does not authorize:

- Lexer, Parser, AST, ZASI, Semantic Analysis, Compiler, or Runtime modifications.
- Grammar or language-semantic changes.
- Changes to existing resource ceilings.
- Changes to ZB-07 or ZIIF-01 scope or status.
- New dependencies or Python–Rust integration.
- Automatic merge or Owner approval bypass.
- Implementation of the gVisor backend.

Each implementation stage requires its own baseline, impact analysis, Change Plan, explicit Owner approval, and verification evidence.

8. Acceptance Criteria for Future Implementation

The future implementation must demonstrate:

1. Every mandatory isolation control is enforced by the actual backend.
2. Missing controls cause execution rejection.
3. No weaker runtime fallback is possible.
4. Workloads cannot access unauthorized filesystem paths or secrets.
5. Network and resource boundaries are enforced by the host-level runtime.
6. Adversarial tests exercise the real isolation boundary.
7. Evidence is independently reviewable and tied to the tested host and policy.
8. Native component security remains independently verified.
9. Owner approval remains mandatory for protected integration and merge.

9. Final Architectural Decision

ZEN adopts Native Component Security + Execution Isolation as complementary layers of its security architecture.

Every component remains responsible for its own integrity. ZEAI Sandbox Isolation protects the execution environment and limits the impact of untrusted workloads.

This document records an approved architectural direction, not a claim of completed implementation or verified security enforcement.
