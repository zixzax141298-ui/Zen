# ZEAI — Security Threat Model

**Status:** Owner-approved design requirements; implementation and enforcement remain separately unverified
**Scope:** ZEN repository ZEAI architecture

## 1. Purpose

Identify realistic threats to ZEAI's event processing, orchestration, Native CI Engine, sandbox, evidence, repository, and Owner approval boundaries. This is a design threat model, not a penetration test or certification.

## 2. Security Objectives

Preserve repository and governance integrity, source integrity, secret confidentiality, verification evidence integrity, execution isolation, Owner authority, and availability of essential engineering workflows.

## 3. Trust Domains

1. **Owner governance domain:** Owner-approved policies and explicit authorization. Highest project authority.
2. **ZEAI control domain:** event validation, orchestration, policy evaluation, and evidence coordination. Limited by Owner-approved policy.
3. **Native CI domain:** deterministic verification logic and result production.
4. **Sandbox workload domain:** untrusted source, tests, generated code/artifacts, and repair tasks. No secrets or privileged repository authority.
5. **Repository data domain:** source, tests, docs, workflow files, comments, and metadata. Data is not privileged instruction.
6. **External integration domain:** GitHub events, APIs, CI results, package metadata, and other external responses. Untrusted until validated.

No agent or subsystem may elevate itself above the Owner.

## 4. Threat Register

| ID | Threat | Impact | Required mitigation |
|---|---|---|---|
| T-01 | Forged event or repository identity | Unauthorized task execution | Authenticate and validate event, repository, ref, commit, scope, and permissions |
| T-02 | Event replay or duplicate delivery | Repeated side effects | Stable event IDs, replay detection, idempotent task handling |
| T-03 | Malicious PR/source/test code | Host or runner compromise | Mandatory gVisor `runsc` sandbox; no untrusted host execution |
| T-04 | Sandbox runtime unavailable | Unsafe fallback execution | Fail closed; no `runc` or host fallback |
| T-05 | Sandbox escape or incomplete boundary | Host/workspace compromise | Host-level control evidence, adversarial tests, independent review, least privilege |
| T-06 | Filesystem traversal or mount leakage | Host/repository data exposure | Workspace-scoped filesystem, path validation, restricted mounts |
| T-07 | Network egress | Data exfiltration or command-and-control | Network disabled by current contract; reject network-enabled policy |
| T-08 | Resource exhaustion | Host/CI denial of service | Enforced CPU, memory, wall-clock, and output limits |
| T-09 | Secret/credential inheritance | Credential compromise | Empty-by-default environment, deny credential-like variables, no inherited Git/CI/cloud/SSH secrets |
| T-10 | Workflow or governance tampering | Unauthorized privileged behavior | Protected review, least privilege, Owner approval |
| T-11 | Evidence tampering or stale evidence | False PASS | Commit-bound, scope-bound, integrity-protected evidence; stale/missing evidence is INDETERMINATE |
| T-12 | Compromised dependency | Supply-chain compromise | Provenance/vulnerability/license review and approved dependency changes |
| T-13 | Unbounded or unauthorized repair | Source integrity loss | Bounded repair in sandbox; Owner approval before integration/merge |
| T-14 | ZEAI self-approval or self-merge | Loss of Owner control | Prohibit self-approval/merge; Owner remains final authority |
| T-15 | Prompt/instruction injection in repository or external data | Policy override | Treat content as data; only Owner-approved governance defines authority |
| T-16 | Incorrect result classification | Unsafe acceptance | `PASS`/`FAIL`/`INDETERMINATE`; never promote uncertainty to PASS |
| T-17 | Watchdog migration assumption | Missed events or duplicate authority | Inspect existing Watchdog before claiming replacement or migration |

## 5. Event Security

Before a privileged task, validate event authenticity, repository identity, event type, exact commit SHA, authorized scope, permission context, replay/duplicate status, and allowed task type. Invalid, stale, conflicting, or ambiguous events must not initiate privileged work.

## 6. Mandatory Sandbox Security

The approved Linux runtime target is gVisor `runsc`. It must enforce, for the exact host and policy:

- Process isolation and lifecycle/termination controls.
- Filesystem isolation to the declared workspace.
- Network isolation; network-enabled policies are rejected by the current contract.
- CPU, memory, wall-clock, and output limits.
- Secret isolation, with no inherited environment or ambient credentials.

If `runsc` is unavailable or any control/evidence is missing, execution is rejected. There is no fallback to `runc`, ordinary host execution, or an unreviewed backend. Fake-backend tests do not prove OS-level enforcement.

## 7. Secret and Permission Security

Untrusted workloads receive no repository secrets, Git write credentials, CI tokens, cloud keys, SSH credentials, or Owner approval capabilities. Read/write permissions must be separated and minimized. Sensitive access must be auditable; compromised credentials must be revoked/rotated.

## 8. Evidence Integrity

Every result binds repository identity, commit SHA, event/task identity, authorized scope, sandbox/backend policy when applicable, tool/test identity, execution environment, exit result, and evidence references. Missing, conflicting, stale, or unverifiable evidence yields `INDETERMINATE` or `FAIL`, never `PASS`.

## 9. Failure and Recovery

Address interrupted execution, partial task state, corrupted workspace, failed verification, runner compromise, evidence loss, and credential exposure. Terminate safely, preserve evidence, clean temporary state without deleting unrelated data, and escalate to Owner. Recovery must not bypass approval gates.

## 10. Verification Requirements

Before enabling untrusted workload execution, verify actual gVisor `runsc` operation on the target host, process containment, filesystem boundary, network denial, resource enforcement, secret isolation, fail-closed startup/runtime behavior, and adversarial cases. Independently verify Native Component Security. Neither layer substitutes for the other.

## 11. Residual Risk and Status

The sandbox orchestration foundation exists, but the reviewed gVisor backend and OS enforcement are not implemented/verified in the inspected baseline. This is a blocking prerequisite for untrusted workload execution. Residual risks must be recorded and accepted by the Owner before production deployment; critical unresolved risks block the affected stage.

## 12. Authorization

This threat model defines requirements only. It does not authorize production implementation, sandbox backend deployment, autonomous repair, self-approval, or merge. The Owner retains final authority.
