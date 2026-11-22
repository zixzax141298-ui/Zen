# ZEAI Sandbox Isolation — Contract v1

## 1. Status and Authority

**Orchestration foundation:** present in the inspected repository.
**Reviewed gVisor `runsc` backend:** NOT IMPLEMENTED.
**OS-level enforcement:** NOT IMPLEMENTED / NOT VERIFIED.
**Execution of untrusted workloads:** prohibited until the backend and every mandatory control are independently verified.

Sandbox Isolation is a mandatory ZEAI security foundation, not an optional feature. This contract records requirements; it does not claim that the current repository can safely execute untrusted code.

## 2. Approved Runtime Target and Fail-Closed Rule

The approved Linux isolation runtime target is **gVisor `runsc`**. The production backend must explicitly invoke and verify the reviewed `runsc` runtime for the exact host and policy.

- If `runsc` is missing, misconfigured, incompatible, or cannot prove any required control, reject execution.
- Never silently fall back to `runc`, ordinary host execution, or an unreviewed backend.
- A generic container runtime or a fake test backend is not a substitute for the approved production isolation boundary.
- Missing, stale, or ambiguous capability evidence means execution is unavailable.

## 3. Mandatory Controls

The backend must enforce and provide independently reviewable host-level evidence for:

1. **Process isolation:** process containment from the parent and unrelated workloads; controlled lifecycle and termination.
2. **Filesystem isolation:** access restricted to the declared workspace; no unintended host, home-directory, repository credential, or control-plane access.
3. **Network isolation:** disabled under the current contract. Network-enabled policy is rejected.
4. **Resource limits:** enforced CPU, memory, wall-clock, stdout, and stderr limits. Policy values are not proof of enforcement.
5. **Secret isolation:** no inherited environment, Git credentials, API keys, private keys, SSH credentials, CI tokens, cloud credentials, or Owner authority.

Workloads receive no Git write capability or governance approval capability.

## 4. Request Boundary

- Commands are argument vectors; shell command strings are rejected.
- Working directory must resolve inside the configured workspace.
- Environment is empty by default; explicit allowlisting is required.
- Credential-like environment names are rejected even if allowlisted.
- Stdin and output types/sizes must be validated.
- Backend capability evidence must describe enforcement, not merely declared configuration.

## 5. Resource Policy Defaults

Current policy defaults:

- Wall-clock timeout: 10 seconds.
- CPU time: 10 seconds.
- Memory: 256 MiB.
- Maximum output: 1 MiB per stream.

These are declarative policy defaults. They do not prove that a backend enforces the limits. Actual enforcement and boundary tests are required.

## 6. Verification Contract

Verification must include:

- Actual `runsc` runtime identity and version on the target host.
- Process containment and safe termination tests.
- Filesystem boundary and traversal tests.
- Network-denial tests.
- CPU, memory, timeout, and output-limit enforcement tests.
- Secret/environment non-inheritance tests.
- Missing-runtime/missing-control fail-closed tests.
- Adversarial tests against the real backend.
- Independent review of host-level evidence.

Fake-backend tests exercise orchestration and fail-closed behavior only. They do not verify OS namespaces, seccomp, cgroups, mounts, network isolation, process containment, or gVisor itself.

## 7. Current Repository Implementation Evidence

The current `src/zen/sandbox/` package contains policy, request/result/capability contracts, and orchestration. `SandboxRuntime` rejects a missing backend, missing required controls, or empty evidence before invoking execution. `SandboxPolicy` rejects network-enabled policy and declares resource defaults. The current sandbox tests use a fake backend.

No reviewed gVisor `runsc` backend or actual host-level enforcement was present in the inspected baseline. Therefore actual OS isolation remains **NOT IMPLEMENTED / NOT TESTED**. Do not market, document, or report this foundation as completed sandbox protection.
