
# ZEAI-01 — Security Threat Model

**Project:** ZEN  
**Component:** ZEAI  
**Document Type:** Security Threat Model  
**Status:** Proposed — Owner Review Required  
**Classification:** Engineering Security Design  
**Implementation Authorization:** Not Granted

---

## 1. Purpose

This document defines the preliminary security threat model for ZEAI.

ZEAI is intended to become the native engineering intelligence system of ZEN.

Because ZEAI may eventually inspect repositories, process engineering events, execute verification tasks, and coordinate controlled development operations, its security architecture must be established before implementation.

This document defines design requirements only.

It does not authorize production implementation.

## 2. Security Objectives

ZEAI must preserve:

1. Repository integrity.
2. Governance integrity.
3. Source code integrity.
4. Secret confidentiality.
5. Verification evidence integrity.
6. Execution isolation.
7. Owner authority.
8. Availability of essential engineering workflows.

## 3. Threat Actors

Potential threat sources include:

- Malicious external contributors.
- Compromised dependency packages.
- Malicious pull request content.
- Forged or replayed events.
- Compromised credentials.
- Malicious workflow modifications.
- Incorrect internal execution logic.
- Accidental operator actions.

Threat classification must be based on evidence and realistic attack paths, not assumptions about an individual.

## 4. Trust Boundaries

ZEAI must distinguish these trust domains:

### 4.1 Trusted Governance Domain

Contains repository governance and explicitly authorized policies.

Protection requirements:

- Restricted modification.
- Explicit review.
- Version-controlled history.
- Owner-controlled authority.

### 4.2 Repository Source Domain

Contains application source, tests, documentation, and configuration.

Repository content must not automatically be treated as trusted instructions.

### 4.3 External Event Domain

Contains incoming GitHub events and external integration data.

All external events must be validated before they trigger privileged operations.

### 4.4 Untrusted Execution Domain

Contains code from untrusted branches, pull requests, and external contributions.

This domain must be isolated from secrets and privileged repository operations.

### 4.5 ZEAI Control Domain

Contains event validation, orchestration, verification policy, and evidence handling.

Its authority must be restricted by explicit policy and Owner approval.

## 5. Threat Register

| ID | Threat | Potential Impact | Required Mitigation |
|---|---|---|---|
| T-01 | Forged event | Unauthorized execution | Event authentication and validation |
| T-02 | Replay attack | Repeated privileged actions | Event identity and replay protection |
| T-03 | Malicious PR code | Runner compromise | Isolated execution |
| T-04 | Secret exposure | Credential compromise | Secret isolation and least privilege |
| T-05 | Workflow tampering | Unauthorized CI behavior | Protected workflow review |
| T-06 | Governance tampering | Loss of policy integrity | Owner-controlled protection |
| T-07 | Evidence manipulation | False PASS result | Commit-bound evidence integrity |
| T-08 | Dependency compromise | Supply-chain compromise | Dependency verification |
| T-09 | Resource exhaustion | CI disruption | Execution limits and quotas |
| T-10 | Unauthorized repair | Source integrity compromise | Sandbox and Owner approval |
| T-11 | Autonomous merge | Unreviewed repository changes | Prohibit autonomous merge |
| T-12 | Incorrect result classification | Unsafe acceptance | Fail-closed result contract |

## 6. Event Security

Every event must be checked for:

- Authenticity.
- Expected repository identity.
- Event type.
- Commit identity.
- Authorized scope.
- Replay or duplicate conditions.
- Permission context.

Invalid or ambiguous events must not initiate privileged execution.

## 7. Execution Isolation

Untrusted code must not execute in a privileged environment.

Future execution architecture must provide:

- Isolated execution environments.
- Restricted filesystem access.
- Restricted network access.
- Resource limits.
- Time limits.
- Process termination controls.
- No access to repository secrets.
- No privileged host credentials.

The exact sandbox implementation requires a separate technical design and security review.

## 8. Secret Protection

Mandatory requirements:

1. Never store secrets in source code.
2. Never expose secrets to untrusted pull requests.
3. Never print secrets in logs.
4. Apply least-privilege credentials.
5. Restrict credential lifetime where possible.
6. Separate read-only and write permissions.
7. Rotate compromised credentials.
8. Audit sensitive access.

## 9. Evidence Integrity

Every verification result must be associated with:

- Repository identity.
- Exact commit SHA.
- Event identity.
- Execution scope.
- Tool and test identity.
- Execution outcome.
- Evidence references.

Missing, conflicting, or unverifiable evidence must produce INDETERMINATE or FAIL, never PASS.

## 10. ZEAI Authority Restrictions

ZEAI must never:

- Approve its own changes.
- Merge its own changes.
- Modify protected governance without authorization.
- Expand its own permissions.
- Bypass required security checks.
- Treat untrusted repository content as privileged instructions.
- Execute unbounded repairs.
- Claim successful verification without evidence.

The Repository Owner retains final authority.

## 11. Failure and Recovery Security

Future implementation must address:

- Interrupted execution.
- Corrupted temporary state.
- Failed verification.
- Runner compromise.
- Evidence loss.
- Credential exposure.
- Partial repair operations.

Recovery procedures must preserve repository integrity and must not bypass approval gates.

## 12. Security Validation Requirements

Before implementation approval, the design must be reviewed for:

- Threat coverage.
- Trust boundary completeness.
- Permission minimization.
- Event validation.
- Replay protection.
- Secret isolation.
- Sandbox requirements.
- Evidence integrity.
- Failure handling.
- Recovery procedures.

A documented threat model is not proof that these controls have been implemented or tested.

## 13. Residual Risks

Some risks cannot be fully eliminated by architecture documentation alone.

Residual risks must be recorded, assessed, and explicitly accepted by the appropriate authority before production deployment.

Critical unresolved security risks must block the affected implementation stage.

## 14. Authorization Boundary

**Threat model status:** Proposed  
**Security implementation:** Not authorized  
**Production changes:** Not authorized  
**Security exceptions:** Not authorized  
**Autonomous repair:** Not authorized  
**Autonomous merge:** Prohibited  
**Final authority:** Repository Owner

---

**End of ZEAI-01 Security Threat Model**
