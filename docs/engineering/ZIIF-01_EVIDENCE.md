# ZIIF-01 — Engineering Evidence Ledger

## 1. Document Identity

Milestone: ZIIF-01 — Canonical AST Identity Fingerprint

Status: IMPLEMENTATION MERGED — REGRESSION TESTS EXPANDED; FINAL ACCEPTANCE PENDING

Verification status: LOCAL_TESTS_PASSED; REGRESSION_EXPANSION_MERGED; FINAL_ACCEPTANCE_PENDING

Baseline branch: `feature/ziif-01-ast-fingerprint`

Baseline commit: `a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676`

Historical implementation test runs were performed on an uncommitted working tree based on the baseline commit above.
The implementation was subsequently merged through PR #9 (merge commit `ea2c14841540ce236d9c74d45401e47abe9982f7`).
The PR #26 regression-test expansion was committed as `4925656` and merged into main through merge commit `803c245`.

This ledger distinguishes observed test results from unverified acceptance
criteria. Code presence and passing regression tests do not independently
prove every property of the implementation.

## 2. Evidence Rules

- OBSERVED: directly inspected or measured.
- DERIVED: logically concluded from observations.
- ASSUMED: provisional and not verified.
- UNKNOWN: not established.
- NOT_TESTED: no relevant test has been executed.

Never invent test results, commit identities, CI status, performance results,
or memory measurements.

## 3. Approved Scope

- Versioned canonical AST structural fingerprint.
- SHA-256 with domain separation.
- Explicit closed node schemas and fixed field order.
- Mandatory canonical AST validation before encoding.
- Iterative encoding.
- SourceIdentifier and SourceSpan validation without digest inclusion.
- Public API export.
- Focused regression tests.
- Dedicated Change Plan and evidence ledger.
- Limited active-milestone governance updates and ZB-07 closure record.

No parser, grammar, runtime, optimizer, security-policy, resource-limit,
dependency, or SECURITY.md changes are authorized.

## 4. Encoding Contract

Version 1 output:

`zen-ast-sha256-v1:<64 lowercase hexadecimal characters>`

The encoder uses explicit type tags, length prefixes, fixed field order,
big-endian integer magnitude, binary64 float encoding, and ordered tuples.

Source identity and source coordinates are validated but excluded from the
structural digest. Future incompatible encoding changes require a version
increase.

## 5. Implementation Register

| Item | Observed status | Evidence |
|---|---|---|
| `src/zen/ast/fingerprint.py` | Present in local working tree | Owner-provided repository inspection and successful test runs |
| AST public exports | Modified in `src/zen/ast/__init__.py` | Import smoke check: `import zen.ast` succeeded |
| Fingerprint tests | Present in local working tree | Focused test command passed |
| Change Plan | Present and updated | Repository document |
| Evidence ledger | Present and updated | This document |
| Governance references | Updated in historical implementation PR #9 | PR #9 merge: `ea2c14841540ce236d9c74d45401e47abe9982f7`; not part of current PR #2 |

## 6. Verification Register

### EVD-ZIIF01-001 — Focused tests

- Date: 2026-11-22 (+07:00).
- Exact execution time: not captured.
- Branch: `feature/ziif-01-ast-fingerprint`.
- Baseline commit: `a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676`.
- Revision tested: uncommitted local working tree based on the baseline.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0.
- Command: `python -m pytest -v tests/test_ast_identity_fingerprint.py`.
- Result: `11 passed in 0.13s`.
- Exit status: successful, as reported by the Owner.
- Execution source: locally executed by the Owner in Termux.

### EVD-ZIIF01-002 — Full regression suite

- Date: 2026-11-22 (+07:00).
- Exact execution time: not captured.
- Branch: `feature/ziif-01-ast-fingerprint`.
- Baseline commit: `a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676`.
- Revision tested: uncommitted local working tree based on the baseline.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0.
- Command: `python -m pytest -v`.
- Result: `145 passed, 68 subtests passed in 0.63s`.
- Exit status: successful, as reported by the Owner.
- Execution source: locally executed by the Owner in Termux.

### EVD-ZIIF01-003 — Public import smoke check

- Date: 2026-11-22 (+07:00).
- Command: `python -c "import zen.ast; print('AST exports loaded')"`.
- Result: `AST exports loaded`.
- Execution source: locally executed by the Owner in Termux.

### EVD-ZIIF01-004 — Repository whitespace check

- Date: 2026-11-22 (+07:00), 04:58:19 +07:00.
- Command: `git diff --check`.
- Result: no output; no whitespace errors reported.
- Baseline HEAD observed: `a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676`.

## 7. Acceptance Checklist

The following checks are limited to evidence directly reported:

- [x] Public API import smoke check succeeded.
- [x] Focused fingerprint test file passed: 11 tests.
- [x] Full local regression suite passed: 145 tests and 68 subtests.
- [x] `git diff --check` reported no whitespace errors at the recorded inspection.

The following remain pending or require more specific evidence:

- [ ] Every current canonical AST node schema independently covered by tests.
- [ ] Fixed field ordering exhaustively verified.
- [ ] Tuple ordering and optional-value encoding independently verified.
- [ ] Domain-separation behavior independently tested.
- [ ] All primitive encodings exhaustively tested.
- [ ] Every invalid or incomplete AST failure mode independently tested.
- [ ] Final complete staged diff reviewed.
- [ ] Commit created and verified.
- [ ] Remote branch push and remote SHA independently verified.

Passing the regression suite is not treated as proof of every individual
acceptance criterion.

### PR #26 checklist reconciliation — 2026-11-23

The original checklist above records the evidence position before PR #26.
The following items received additional regression evidence in PR #26:

- Domain separator and version byte inclusion: covered by a dedicated regression test.
- Tuple ordering: covered by a dedicated regression test.
- Explicit `None` marker: covered by a direct marker assertion.
- Declared schemas and field order: the mapping test checks declarations for all 15 canonical node types.

The following remain unverified:

- Runtime encoding behavior independently exercised for every canonical node type.
- Exhaustive runtime field-order behavior.
- Complete primitive encoding matrix.
- Complete invalid/incomplete AST failure-mode matrix.

The historical checklist is retained rather than rewritten so the evidence
history remains auditable.

## 8. Limitations

- Historical PR #9 test runs were performed on an uncommitted local working tree. PR #26 has separate committed-test evidence recorded in Sections 10–12.
- No implementation commit SHA existed at the time of those test runs.
- No remote CI result is recorded.
- No performance or memory improvement is claimed.
- No cross-platform verification is claimed.
- A structural fingerprint does not prove semantic equivalence, authorship,
  authenticity, provenance, execution safety, or program behavior.
- The exact execution time of the focused and full test runs was not captured.

## 9. Change Control and Next Verification

The Owner separately authorized the commit and push workflow in conversation.
That authorization does not authorize merge, release, deployment, or scope
expansion.

Before commit:
- Review the complete staged diff.
- Confirm only approved files are staged.
- Confirm no backup files or `SECURITY.md` are included.
- Re-run the required tests if implementation files change.

After commit and push, record the actual commit SHA and verify that the remote
branch resolves to the same SHA. Do not claim remote verification before
observing the remote reference.


## 10. EVD-ZIIF01-005 — PR #26 Focused Regression Tests

- Date: 2026-11-23 (+07:00).
- PR: #26 — Complete ZIIF-01 fingerprint regression tests.
- Test branch: `feature/ziif01-test-completion`.
- Test commit: `4925656`.
- Merge commit on main: `803c245`.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0.
- Command: `PYTHONPATH=src python -m pytest tests/test_ast_identity_fingerprint.py -v`.
- Result: `19 passed in 0.18s`.
- Additional syntax check: `python -m py_compile tests/test_ast_identity_fingerprint.py` succeeded.
- Additional whitespace check: `git diff --check` produced no errors.
- Execution source: locally executed by the Owner in Termux.

The expanded tests cover:
- Domain separator and version byte inclusion.
- Tuple ordering.
- Explicit `None` marker.
- Declared schemas and field order for all 15 canonical node types.
- Missing required FunctionDecl metadata.
- Invalid AST child type.

The schema test verifies the declared schema mapping. It does not
independently exercise runtime encoding for every node type.

## 11. EVD-ZIIF01-006 — Full Regression Suite After PR #26

- Date: 2026-11-23 (+07:00).
- Branch: `feature/ziif01-test-completion`.
- Tested commit: `4925656`.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0.
- Command: `PYTHONPATH=src python -m pytest -v`.
- Result: `189 passed, 87 subtests passed in 0.97s`.
- Execution source: locally executed by the Owner in Termux.

This result is local Termux evidence. It is not a remote CI result.

## 12. EVD-ZIIF01-007 — PR #26 Merge and Repository State

- PR: #26.
- Title: `Complete ZIIF-01 fingerprint regression tests`.
- Observed status: merged.
- Merge commit: `803c245`.
- Test commit: `4925656`.
- Files changed by PR #26: `tests/test_ast_identity_fingerprint.py` only.
- Change: 229 insertions.
- Owner-provided post-push repository output showed the local branch tracking
  `origin/feature/ziif01-test-completion` with a clean working tree.
- The Owner's GitHub screenshot showed PR #26 as merged into `main`.

## 13. Remaining Evidence Gaps

The following are not established as complete by PR #26:

- Independent runtime encoding coverage for every canonical node type.
- Exhaustive primitive encoding coverage.
- Complete invalid/incomplete AST failure-mode matrix.
- Final independent review of the complete ZIIF-01 implementation contract.
- Remote CI verification for the relevant historical implementation and
  test commits.
- Governance status reconciliation.

The governance files are intentionally outside the scope of PR #26 and
the current documentation-only PR #2.

## 14. Current Acceptance Position

PR #26 expands regression coverage and passes the Owner's local full suite.
It does not by itself establish final ZIIF-01 acceptance.

Final acceptance remains pending until the remaining contract, failure-mode,
evidence, and governance questions have been reviewed and resolved under
separately authorized scope.
