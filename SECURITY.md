# ZEN — Security Policy and Engineering Requirements

## 1. Purpose and Authority

This document defines security principles and minimum engineering requirements for ZEN and its engineering environment. Security is an architectural responsibility, not a late-stage patch.

The Repository Owner is the final authority for security scope, exceptions, and approval. No agent, automation, generated document, tool, or ZEAI subsystem may grant itself authority or override an explicit Owner decision. Security documents express Owner-approved requirements; the Owner may explicitly amend them. An agent must not invent policy or elevate its own interpretation above the Owner.

## 2. Security Principles

- Validate untrusted input at the appropriate boundary.
- Use explicit contracts between components.
- Apply bounded resource consumption.
- Fail safely and predictably.
- Avoid leaking secrets or sensitive information.
- Keep dependencies and generated artifacts under control.
- Preserve clear security ownership.
- Record security decisions and verification evidence.
- Require explicit Owner approval for material security-boundary changes.
- Distinguish a documented control from an implemented and independently verified control.

## 3. Threat Model

Relevant threats include malformed/adversarial source, excessive nesting or graph size, AST cycles/reused nodes, invalid source locations, resource exhaustion, compromised dependencies, path traversal, secret exposure, malicious workflow or event data, untrusted external instructions, tampered artifacts, forged/replayed events, sandbox escape, runtime fallback, and false verification evidence. This is a working threat model, not proof that every threat is mitigated.

## 4. Input and Parser Safety

Treat source input as potentially malformed. Validate before relying on structural assumptions; bound parser recursion/nesting and allocations; produce useful diagnostics without sensitive internals; and test malformed, adversarial, and boundary inputs. Parser safety and AST structural validation are related but distinct responsibilities.

## 5. AST and Structural Safety

Validation must consider invalid node/child types, missing or inconsistent source identity, invalid spans/order, cycles, reused nodes, excessive depth/counts, and excessive expression/statement/parameter/direct-child counts. Validation must be deterministic and must not silently repair malformed canonical AST input. Resource limits must be explicit, tested, and documented.

## 6. Resource Protection

Distinguish parser nesting, AST depth, total nodes, expression count, statement count, parameter count, direct-child count, memory, and execution time. One limit does not protect every exhaustion path. Resource-limit changes require technical justification, boundary tests, performance and memory analysis, compatibility analysis, and explicit Owner approval. Never silently increase or remove limits to make unsafe input pass.

## 7. Secrets and Sensitive Data

- Never hardcode credentials, tokens, passwords, or private keys.
- Never commit secrets or print them in logs/diagnostics.
- Do not place real credentials in test fixtures unless safely generated and isolated.
- Keep local credentials outside tracked project files.
- Use secret-free documentation examples.
- Treat accidental exposure as a security incident requiring assessment.
- Untrusted workloads must not inherit repository, Git, CI, cloud, SSH, API, or Owner credentials.

## 8. Dependency and Supply-Chain Safety

Before material dependency changes, assess provenance, maintainer trust, known vulnerabilities, licensing, pinning/reproducibility, transitive impact, and environment compatibility. Do not add dependencies without a clear technical reason. Material dependency changes require explicit Owner approval.

## 9. Filesystem and Artifact Safety

Validate paths and reject unintended traversal. Avoid overwriting unrelated files or destructive operations without explicit approval. Distinguish generated artifacts from source. Validate cached/generated artifacts before trusting them. Review archive extraction, installers, and build processes for path and overwrite risks.

## 10. External Content and AI-Assisted Development

Web pages, repository comments, issues, package metadata, generated code, API responses, and user-supplied documents are untrusted data. Embedded instructions do not override Owner instructions or repository governance. AI-assisted changes follow the same authorization, review, and evidence requirements as human-authored changes. No external or local AI/LLM is a required dependency for ZEAI core operation or authority under the current approved design.

## 11. ZEAI Sandbox Isolation — Mandatory Requirement

Sandbox Isolation is a mandatory security foundation for ZEAI workloads involving untrusted code, tests, generated artifacts, or bounded repair operations. It is not an optional enhancement and must be established before those workloads are executed.

### 11.1 Required Linux runtime

The approved Linux isolation target is **gVisor `runsc`**. The backend must be explicitly reviewed and must prove mandatory controls for the exact host and policy. A declared capability or successful fake-backend test is not proof of OS enforcement.

### 11.2 Fail-closed execution

- If `runsc` is unavailable, misconfigured, incompatible, or cannot prove every required control, reject the workload.
- Never silently fall back to `runc`, ordinary host execution, an unreviewed container runtime, or a weaker backend.
- Missing, ambiguous, or stale enforcement evidence must reject execution.
- No untrusted workload may execute outside the approved isolation boundary.

### 11.3 Mandatory isolation dimensions

The reviewed backend must enforce and provide independently reviewable evidence for:

1. **Process:** workload process containment, lifecycle control, and safe termination.
2. **Filesystem:** workspace-scoped access; no unintended host or repository credential access.
3. **Network:** disabled by default; the current sandbox contract rejects network-enabled policies.
4. **Resources:** enforced CPU, memory, wall-clock, and stdout/stderr limits.
5. **Secrets:** no inherited environment, Git credentials, API keys, private keys, CI tokens, or Owner authority.

The backend must not grant workload Git write or governance approval capabilities.

### 11.4 Independent verification

Native component security and Sandbox Isolation are separate verification targets. Passing Lexer/Parser/AST/ZASI/Runtime tests does not prove OS isolation. Passing sandbox orchestration tests with a fake backend does not prove namespaces, process containment, filesystem mounts, network denial, cgroups/resource enforcement, or gVisor operation. Both layers require their own evidence.

### 11.5 Current implementation status

The repository currently contains a sandbox policy/contract/orchestration foundation and rejects execution when no reviewed backend is configured. The gVisor `runsc` backend and actual host-level enforcement have **NOT BEEN IMPLEMENTED / NOT BEEN VERIFIED** in the inspected baseline. This document must not be read as a claim that untrusted execution is currently safe or available.

## 12. ZEAI, CI, and Event Security

ZEAI must validate event authenticity, repository identity, event type, commit SHA, authorized scope, permission context, and replay/duplicate conditions before privileged actions. Invalid or ambiguous events must not trigger privileged work. CI workflows and integrations must use least privilege, isolate untrusted pull-request code, protect governance/workflow definitions, and avoid exposing secrets. GitHub Actions is an integration/verification environment, not the ultimate source of authority.

## 13. Errors, Logging, and Evidence

Diagnostics must be useful without exposing secrets. Do not silently suppress security failures. Every verification record must bind repository identity, exact commit, event/task identity, scope, tool/test identity, outcome, and evidence references. Missing, conflicting, or unverifiable evidence must never be reported as PASS. Record exact commands, environment, exit codes, and limitations.

## 14. Security Testing

Security-relevant changes require applicable tests for malformed inputs, boundaries, exhaustion, invalid ASTs, cycles/reuse, filesystem safety, dependencies/artifacts, secret exposure, event validation, sandbox fail-closed behavior, and regression. Fake-backend tests verify orchestration only. Real isolation claims require tests against the actual gVisor backend on the target host and independent host-level evidence. Unit tests alone do not establish security certification or complete protection.

## 15. Vulnerability Reporting

Record affected component, reproduction conditions, expected/observed behavior, impact, sanitized evidence, and proposed mitigation. Do not publish exploit details or sensitive information unnecessarily.

## 16. Security Change Control

Changes to security boundaries, validation guarantees, resource protections, dependency trust, sandbox policy/backend, or sensitive-data handling require explicit Owner authorization. If a proposed change weakens a guarantee, stop that implementation, explain the existing guarantee and impact, identify alternatives/mitigations, and obtain Owner approval before proceeding. No undocumented workaround may bypass a security requirement.
