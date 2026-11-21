# ZIIF-01 — Engineering Evidence Ledger

## 1. Document Identity

Milestone: ZIIF-01 — Canonical AST Identity Fingerprint

Status: IMPLEMENTATION APPLIED — LOCAL TESTS PASSED; FINAL REVIEW PENDING

Verification status: LOCAL_TESTS_PASSED

Baseline branch: `feature/ziif-01-ast-fingerprint`

Baseline commit: `a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676`

Working-tree identity: uncommitted changes based on the baseline commit above.
No commit SHA exists for the implementation at the time of these test runs.

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
| Governance references | Updated in this change set | Pending staged-diff review |

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

## 8. Limitations

- The recorded test runs were performed on an uncommitted local working tree.
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
