# ZEAI Sandbox Isolation — Contract v1

## Status

Implementation foundation: **present**.
OS enforcement backend: **NOT IMPLEMENTED**.

The runtime intentionally refuses to execute workloads until a reviewed
backend proves every mandatory isolation control. This document does not
claim that the current repository can safely execute untrusted code.

## Scope

The sandbox package is standalone under `src/zen/sandbox/`.
It does not modify lexer, parser, AST, fingerprint, grammar,
or existing resource ceilings.

It defines policy, request/result contracts, capability evidence,
and a fail-closed orchestration boundary.

## Mandatory controls

A future backend must prove all of the following for the exact host and policy:

- Process isolation from the parent process and unrelated workloads.
- Filesystem isolation, restricted to the declared workspace.
- Network isolation. Network-enabled policies are rejected.
- Enforced CPU, memory, wall-clock, and output limits.
- Secret isolation: no inherited environment, Git credentials,
  API keys, private keys, or governance authority.

A backend capability report is not permission to trust an unsupported claim.
Its evidence must describe host-level enforcement and be independently
reviewable. Missing controls or missing evidence must stop execution.

## Request boundary

- Commands are argument vectors; shell command strings are rejected.
- Working directory must resolve inside the configured workspace.
- Environment variables are empty by default and require explicit allowlisting.
- Credential-like environment names are rejected even if allowlisted.
- Workloads receive no Git write capability or governance approval capability.

## Resource policy

Defaults: 10-second wall-clock timeout, 10 CPU seconds,
256 MiB memory, and 1 MiB per output stream.

These are policy defaults, not proof that a backend enforces them.
The backend must enforce and report resource controls.

## Verification

Run:

`python -m unittest discover -s tests -v`

Fake-backend tests exercise orchestration and fail-closed behavior only.
They do not verify OS namespaces, seccomp, cgroups, network isolation,
filesystem mounts, or actual process containment.

Those remain **NOT_TESTED** until a platform-specific backend
and independent host-level tests are approved.
