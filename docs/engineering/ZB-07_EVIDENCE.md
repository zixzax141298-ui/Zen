# ZEN Engineering Evidence Ledger (ZEEL)

# ZB-07 — AST Semantic Readiness & Source Identity Contract

## 1. Document Identity

Document type: Initial manual engineering evidence ledger
Milestone: ZB-07
Ledger status: REOPENED — ZB-07 v2.0 evidence in progress.
Implementation status: Historical ZB-07 implementation remains recorded below; reopened v2.0 changes are not yet verified.
Verification status: NOT_TESTED for the reopened v2.0 acceptance criteria. Historical test records below are preserved and are not evidence for the reopened patch.

Approved technical baseline commit:

`0003a9b961810510c2d67c7851ab3f2e9327c5b2`

Baseline branch: `audit/zb06-strict-ast-contract`

Initial project baseline commit: `6bb9611eeec73a6c1bd543150eedc2d151b219a0`

The approved technical baseline is on a development branch and has not been merged into main.

This document is a manually maintained evidence ledger for ZB-07.

The integrated ZEEL Engineering Evidence System is a separate strategic
proposal and is NOT_IMPLEMENTED. The existence of this document does not mean
that the integrated system exists.

## 2. Purpose

This ledger records:

- Milestone requirements.
- Acceptance criteria.
- Implementation references.
- Verification evidence.
- Technical decisions.
- Deferred and blocked work.
- Completion status.

Its purpose is to make milestone claims traceable and independently reviewable.

## 3. Evidence Rules

Every material claim must be supported by identifiable evidence.

Use these labels:

| Label | Meaning |
|---|---|
| OBSERVED | Directly inspected or measured |
| DERIVED | Logically concluded from observations |
| ASSUMED | Provisional premise not yet verified |
| UNKNOWN | Not currently established |
| NOT_TESTED | No relevant test has been executed |

Do not:
- Invent test results.
- Treat code existence as proof of correctness.
- Treat a proposed design as implemented behavior.
- Treat local tests as remote CI evidence.
- Remove failed results from the historical record.
- Claim performance or memory improvements without measurements.

## 4. Requirement Status Definitions

| Status | Meaning |
|---|---|
| NOT_STARTED | No implementation work has been established |
| IN_PROGRESS | Work has started but is incomplete |
| IMPLEMENTED | Implementation exists; verification is not implied |
| PARTIALLY_VERIFIED | Some acceptance criteria have evidence, but not all |
| VERIFIED | All defined acceptance criteria have sufficient traceable evidence |
| BLOCKED | Progress cannot continue because of a recorded blocker |
| DEFERRED | Work is intentionally postponed with a recorded reason |

A requirement may be marked VERIFIED only when:
- Its acceptance criteria are explicit.
- Relevant tests or checks were actually executed.
- Evidence is traceable to a revision or working-tree state.
- Results and limitations are recorded.
- The evidence supports the exact claim being made.

## 5. Milestone Scope

### Included

- Stable source identity.
- Immutable SourceIdentifier.
- Separation of SourceId and SourceSpan.
- Explicit legacy AST compatibility adapter.
- Source-order validation.
- Unified `validate_ast` contract.
- AST graph integrity validation.
- Cycle detection.
- Reused-node detection.
- Explicit resource accounting and limits.
- Iterative deterministic AST validation.
- Parser safety and depth distinction.
- Common diagnostic model.
- Regression testing.
- Performance and memory verification.

### Excluded

- Full Semantic Analysis implementation.
- Grammar redesign.
- Runtime rewrite.
- Optimizer or IR implementation.
- Python-Rust integration.

Any scope expansion requires a separate Change Plan and explicit Owner approval.

## 6. Requirement Register

All requirements begin as NOT_STARTED until repository evidence establishes
otherwise.

### ZB07-01 — Source Identity

Status: NOT_STARTED

Acceptance criteria:
- Source identity is explicit.
- Identity is stable within its defined compilation-unit or session scope.
- Identity does not depend on traversal order.
- Identity does not depend on object memory addresses.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-02 — Immutable SourceIdentifier

Status: NOT_STARTED

Acceptance criteria:
- SourceIdentifier has an explicit immutable contract.
- Invalid identity values are rejected.
- Equality and identity behavior are documented and tested.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-03 — SourceId and SourceSpan Separation

Status: NOT_STARTED

Acceptance criteria:
- SourceId identifies the source unit.
- SourceSpan represents a location or range within that source.
- SourceLocation combines identity and span without conflating them.
- Invalid combinations are rejected or diagnosed.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-04 — Legacy AST Compatibility Adapter

Status: NOT_STARTED

Acceptance criteria:
- Legacy compatibility is explicit.
- Adapter behavior is documented.
- Legacy nodes lacking canonical identity cannot silently enter the canonical
  Semantic Analysis path.
- Compatibility behavior has tests.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-05 — Source-Order Validation

Status: NOT_STARTED

Acceptance criteria:
- Declaration name, parameters, and body order is represented explicitly.
- Invalid order is detected.
- Valid source order is preserved.
- Boundary and regression cases are tested.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-06 — Unified AST Validation Contract

Status: NOT_STARTED

Acceptance criteria:
- `validate_ast(program, limits=...)` has an explicit contract.
- Validation returns a structured ASTValidationResult.
- Validation failures are inspectable.
- Validation does not silently repair malformed canonical AST input.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-07 — Node and Child Type Validation

Status: NOT_STARTED

Acceptance criteria:
- Invalid node types are detected.
- Invalid child types are detected.
- Missing required children are detected.
- Validation results are deterministic.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-08 — AST Graph Integrity

Status: NOT_STARTED

Acceptance criteria:
- Cycles are detected.
- Reused nodes are detected where uniqueness is required.
- Traversal terminates safely on malformed graphs.
- Valid tree structures remain accepted.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-09 — Source Span and Identity Integrity

Status: NOT_STARTED

Acceptance criteria:
- Invalid spans are detected.
- Source identity consistency is checked.
- Overlap and ordering rules are explicit.
- Related diagnostics identify relevant source locations.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-10 — Resource Accounting and Limits

Status: NOT_STARTED

Acceptance criteria:
- Node count is bounded.
- Structural depth is bounded.
- Expression and statement counts are bounded.
- Parameter and direct-child counts are bounded.
- Limits have boundary tests.
- Limit changes require impact analysis and Owner approval.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-11 — Iterative Deterministic Validation

Status: NOT_STARTED

Acceptance criteria:
- Validation does not rely on unbounded recursive traversal.
- Traversal order is deterministic.
- Accounting avoids unnecessary repeated work.
- Performance characteristics are measured where relevant.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-12 — Parser Safety and Depth Distinction

Status: NOT_STARTED

Acceptance criteria:
- Parser recursion or nesting depth is distinguished from AST depth.
- AST structural depth is independently accounted for.
- Total node count is independently accounted for.
- Boundary and adversarial tests are present.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-13 — Common Diagnostic Model

Status: NOT_STARTED

Acceptance criteria:
- Diagnostic code is stable.
- Message and severity are explicit.
- Primary and related locations are supported where applicable.
- Component ownership is clear.
- Compatibility with existing ParseError behavior is considered.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

### ZB07-14 — Regression, Performance, and Memory Verification

Status: NOT_STARTED

Acceptance criteria:
- Existing regression tests pass.
- New requirement tests pass.
- Failure paths and boundaries are tested.
- Performance claims have actual measurements.
- Memory claims have actual measurements.
- Remaining limitations are documented.

Implementation reference: UNKNOWN
Verification reference: UNKNOWN
Notes: No completion claim established.

## 7. Verification Evidence Register

Every verification entry must contain enough information to reproduce or
independently inspect the result.

| Field | Required information |
|---|---|
| Evidence ID | Unique evidence identifier |
| Date and time | Actual execution time and timezone |
| Requirements | Requirement IDs covered |
| Revision | Commit or working-tree identity |
| Environment | OS, Python version, dependencies, relevant configuration |
| Command | Exact command executed |
| Exit code | Actual exit code |
| Result | Actual observed outcome |
| Execution source | Local, CI, or other identified environment |
| Limitations | Known gaps or conditions |

### EVD-ZB07-001 — Baseline regression suite

- Date and time: 2026-11-21 21:58:27 to 21:58:29 +07:00
- Requirements: Existing regression suite at the approved ZB-07 technical baseline. This is ZB-06 regression evidence, not verification of all ZB-07 requirements.
- Revision: `0003a9b961810510c2d67c7851ab3f2e9327c5b2`
- Branch: `audit/zb06-strict-ast-contract`
- Environment: Termux on Android; Python 3.14.10; pytest 9.2.0.
- Command: `python -m pytest -v`
- Exit code: `0`
- Result: `111 passed, 58 subtests passed in 0.33s`
- Execution source: Locally executed by the Owner in Termux.
- Working-tree state: No tracked modifications were reported. Untracked governance documents and backup files were present.
- Related baseline inspection: HEAD matched `origin/audit/zb06-strict-ast-contract`.
- Limitations: This evidence covers the existing regression suite only. It does not establish completion of ZB-07 requirements, cross-platform compatibility, performance, or memory claims.

### EVD-ZB07-002 — Local ZB-07 regression run

- Date: 2026-11-22 (+07:00).
- Exact execution time: Not captured.
- Requirements: Regression evidence for the current local ZB-07 working tree; this result does not independently verify every acceptance criterion.
- Revision: HEAD `ef8ea901910f56388053c4be550ed1066b458df2`; ZB-07 changes were uncommitted working-tree modifications.
- Branch: `feature/zb07-source-identity-validation`.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0; editable package installation.
- Command: `python -m pytest -v`.
- Result: `134 passed, 68 subtests passed in 0.62s`.
- Execution source: Locally executed by the Owner in Termux.
- Additional smoke check: `from zen import Lexer` successfully tokenized `let answer = 42`.
- Limitations: This is pre-commit working-tree evidence, not post-push or remote CI evidence. It does not establish that every ZB-07 acceptance criterion is satisfied. Termux performance and memory measurements have not yet been recorded. Cross-platform behavior has not been established.

## 8. Technical Decision Register

Record decisions that materially affect architecture, contracts, compatibility,
security, or resource behavior.

| Decision ID | Topic | Status | Evidence / Rationale | Owner Approval |
|---|---|---|---|---|
| ZB07-D01 | Technical baseline | ACCEPTED | Owner approved `0003a9b961810510c2d67c7851ab3f2e9327c5b2`; HEAD and remote branch matched during inspection; regression evidence EVD-ZB07-001 recorded. | YES — Owner approval, 2026-11-21 |

Decision status values:
- PROPOSED
- ACCEPTED
- SUPERSEDED
- REJECTED

Do not mark a decision ACCEPTED when approval is required but has not been
recorded.

## 9. Deferred Work

The following remain outside ZB-07:

| Work | Status | Reason |
|---|---|---|
| Full Semantic Analysis | DEFERRED | Separate milestone |
| Grammar redesign | DEFERRED | Outside approved scope |
| Runtime rewrite | DEFERRED | Outside approved scope |
| Optimizer / IR | DEFERRED | Outside approved scope |
| Python-Rust integration | DEFERRED | Requires later architecture readiness |

Deferred work must not be silently introduced into ZB-07.

## 10. Blocked Work Register

No blocker is established in this initial ledger.

When a blocker occurs, record:
- Blocker ID.
- Affected requirement.
- Exact description.
- Evidence.
- Impact.
- Required decision or action.
- Owner approval reference, where applicable.

## 11. Definition of Done

ZB-07 may be considered complete only when:

- [ ] All approved requirements have implementation evidence.
- [ ] Source identity contract is stable and tested.
- [ ] SourceId and SourceSpan are separate and tested.
- [ ] Legacy AST compatibility is explicit and tested.
- [ ] Source-order validation is tested.
- [ ] Unified AST validation contract is implemented.
- [ ] Graph integrity checks are tested.
- [ ] Resource limits and boundary tests are established.
- [ ] Iterative deterministic validation is verified.
- [ ] Parser and AST depth are independently addressed.
- [ ] Diagnostic ownership and structure are verified.
- [ ] Existing regression tests pass.
- [ ] New tests pass.
- [ ] Performance and memory claims have evidence where applicable.
- [ ] Documentation matches actual implementation.
- [ ] Remaining limitations are recorded.
- [ ] Final repository diff has been reviewed.
- [ ] Owner has reviewed the completion report.

A checked item must be backed by evidence. Do not check items merely because
implementation is planned or code appears to exist.

## 12. Change History

| Date | Change | Evidence |
|---|---|---|
| Initial creation | Created initial manual ZB-07 evidence ledger | Document initialization only; no implementation or verification claim |
| 2026-11-21 | Recorded Owner-approved technical baseline and regression evidence | ZB07-D01; EVD-ZB07-001 |


## 13. ZB-07 Closure Record

**Status:** CLOSED — scope-qualified.

### Observed implementation and repository history

- Implementation commit: `a6f3770f50dd5f7cb637cd7239220f07eecf6414`.
- Pull request: #8, merged into `main`.
- Post-merge `main` commit: `a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676`.
- Post-push Termux test result on the matching local and remote commit:
  `134 passed, 68 subtests passed`.
- The Owner reported that the post-push local and remote commit identities
  matched during verification.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0.
- Exact post-push execution timestamp: not captured.
- Remote CI result: not established by this evidence record.

### Closure qualification

This record closes ZB-07 against its approved implementation scope and
the evidence reported above. It does not assert that every aspirational
performance or memory objective has been measured, that cross-platform
behavior has been verified, or that remote CI passed.

Historical evidence entries above remain unchanged.


## 14. Reopening Record — ZB-07 v2.0

**Current status:** REOPENED — highest active milestone.

**Authority:** Owner-approved ZB-07 Change Plan v2.0.

**Priority:** ZB-07 is the highest active milestone. ZIIF-01 follow-on work
is paused until ZB-07 completion. Existing ZIIF-01 implementation and its
fingerprint v1 contract must be preserved.

### Reopened baseline

- Repository: `zixzax141298-ui/Zen`.
- Owner-reported working branch before patch application:
  `feature/ziif-01-ast-fingerprint`.
- Owner-reported local HEAD:
  `cc166718d9c61f77afb861e2e3e57e19d9708975`.
- Owner-reported `origin/main`:
  `ea2c14841540ce236d9c74d45401e47abe9982f7`.
- Owner-reported working tree at the baseline check: clean.
- The historical branch `feature/zb07-source-identity-validation` is not
  the base for the reopened work because it predates the current main line.

These are baseline observations reported during preparation. The Owner must
confirm the fetched remote SHA before creating the implementation branch.

### Reopened implementation observations

Preliminary source inspection found existing implementation for source
identity, the legacy adapter, unified validation, graph checks, resource
accounting, parser-depth separation, and iterative traversal. This is an
implementation inspection only; it is not proof that all requirements are
correct or verified.

The FunctionDecl source metadata contract was incomplete in the inspected
baseline. ZB07-05 therefore remains a specific implementation and verification
focus.

### Reopened evidence status

| Requirement | Preliminary implementation observation | Reopened verification |
|---|---|---|
| ZB07-01 | Present | NOT_TESTED |
| ZB07-02 | Present | NOT_TESTED |
| ZB07-03 | Present | NOT_TESTED |
| ZB07-04 | Present; metadata compatibility needs explicit tests | NOT_TESTED |
| ZB07-05 | INCOMPLETE in inspected baseline | NOT_TESTED |
| ZB07-06 | Present | NOT_TESTED |
| ZB07-07 | Present | NOT_TESTED |
| ZB07-08 | Present | NOT_TESTED |
| ZB07-09 | PARTIAL; FunctionDecl metadata integration required | NOT_TESTED |
| ZB07-10 | PARTIAL; complete boundary matrix required | NOT_TESTED |
| ZB07-11 | Iterative implementation and non-gating measurement test present | NOT_TESTED |

### Reopened verification record

No reopened v2.0 test result is recorded here yet.

The following must be added only after actual execution:
- Exact branch and commit.
- Exact environment and Python version.
- Exact commands and exit codes.
- Actual test totals and failures.
- Performance runtime and peak-memory observations.
- Local versus remote CI result.
- Complete changed-file ledger from actual Git output.

Historical evidence entries and the earlier scope-qualified closure record
remain unchanged. They must not be relabeled as verification of the reopened
v2.0 work.

### Reopened completion gate

ZB-07 remains OPEN until every approved acceptance criterion has traceable
implementation and verification evidence, the complete diff is reviewed,
and the Owner approves the final completion report.


## 15. Owner-Approved Baseline Reconciliation — 2026-11-23

**Decision:** ZB07-D02 — ACCEPTED.

- Owner approval: 2026-11-23.
- Repository: `zixzax141298-ui/Zen`.
- Approved baseline: `8fa9a65efc534eb23d7fc63141100429bd169000`.
- Implementation branch: `feature/zb07-v2-completion`.
- Owner-reported local HEAD: `8fa9a65efc534eb23d7fc63141100429bd169000`.
- Owner-reported fetched `origin/main`: `8fa9a65efc534eb23d7fc63141100429bd169000`.
- Owner-reported working tree at branch creation: clean.
- Branch creation: from the exact `origin/main` commit above.
- Previous preparation baseline `ea2c148...` is superseded for
  this reopened implementation; its historical records remain unchanged.
- Scope: baseline/documentation reconciliation only.
- No source-code verification or ZB-07 completion is implied.
- No commit, push, merge, or PR creation is authorized by this
  baseline decision alone.

The baseline values are based on the Owner's Termux output.
They must be rechecked against Git before implementation and commit.
