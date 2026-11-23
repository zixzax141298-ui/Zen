# ZIIF-01 — Canonical AST Identity Fingerprint

## 1. Document Status

Milestone: ZIIF-01
Status: IMPLEMENTATION MERGED — REGRESSION TESTS EXPANDED; LOCAL TESTS PASSED; FINAL ACCEPTANCE PENDING
Historical implementation baseline branch: feature/ziif-01-ast-fingerprint
Historical implementation baseline commit: a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676
Implementation merge: PR #9, ea2c14841540ce236d9c74d45401e47abe9982f7
Regression-test PR: #26, commit `4925656`, merged into `main` via merge commit `803c245`.

This document records the approved implementation scope. It does not
constitute evidence that implementation or tests have passed.

## 2. Objective

Provide a deterministic, versioned SHA-256 structural fingerprint for a
canonical Zen AST.

The fingerprint identifies the encoded AST structure and values. It is not
a semantic-equivalence proof, authorship proof, authenticity proof, or
source-provenance proof.

## 3. Public Contract

Public API:

- `fingerprint_ast(program: Program) -> str`
- `ASTFingerprintError`
- `FINGERPRINT_VERSION`
- `FINGERPRINT_PREFIX`

Version 1 output format:

`zen-ast-sha256-v1:<64 lowercase hexadecimal characters>`

Fingerprint generation must call `validate_ast` first.

Generation must fail closed if validation is invalid or incomplete. Diagnostic
codes are retained on `ASTFingerprintError`.

## 4. Canonical Encoding

Version 1 uses:

- SHA-256.
- A fixed domain separator.
- An explicit version byte.
- Explicit node type tags.
- Explicit, closed node schemas.
- Fixed field order for every supported node type.
- Length-prefixed UTF-8 strings and byte sequences.
- Explicit primitive type tags.
- Big-endian binary64 float encoding.
- Sign plus big-endian magnitude integer encoding.
- Length-prefixed tuples with order preserved.
- Explicit representation of optional `None` values.
- An iterative encoder; no recursive AST encoding.

The encoder must not use generic dataclass introspection.

The supported node schema is defined explicitly in
`src/zen/ast/fingerprint.py`.

Any future incompatible encoding change requires a new fingerprint version.

## 5. Source Metadata

`SourceIdentifier` and `SourceSpan` are validated by `validate_ast`.

They are intentionally excluded from the structural digest. Two structurally
identical ASTs with different valid source identifiers or source spans must
produce the same version 1 fingerprint.

This does not establish source authenticity or provenance.

## 6. Scope

Included:

- Add `src/zen/ast/fingerprint.py`.
- Export the fingerprint API from `src/zen/ast/__init__.py`.
- Add `tests/test_ast_identity_fingerprint.py`.
- Add this Change Plan and a dedicated evidence ledger.
- Update active milestone references in governance documentation.
- Record ZB-07 closure evidence without rewriting historical test claims.

Excluded:

- AST node or grammar changes.
- Parser implementation or changes.
- Semantic analysis implementation.
- Runtime changes.
- Optimizer or IR implementation.
- Resource-limit changes.
- Security-policy changes.
- Dependency additions.
- Python-Rust integration.
- Changes to `SECURITY.md`.

The governance-document updates listed in the included historical scope
belong to implementation PR #9. They are not part of the current
documentation-only PR #2.

## 7. Validation and Failure Behavior

The AST must pass the existing canonical `validate_ast` contract.

Invalid source identity, mismatched source identity, invalid spans, invalid
children, cycles, reused nodes, unsupported node types, or incomplete
validation must prevent fingerprint generation.

The encoder must reject values outside its closed schema.

## 8. Acceptance Criteria

- [x] Public API is exported. (Source inspection and historical import smoke check.)
- [x] Output format is versioned and deterministic. (Existing regression tests.)
- [x] Encoding uses SHA-256 and domain separation. (Source inspection and PR #26 domain/version regression test.)
- [x] Every current canonical AST node type has an explicit declared schema. (PR #26 mapping test; runtime encoding of every node is not independently established.)
- [x] Declared field order is fixed and mapping is tested. (PR #26; exhaustive runtime field encoding remains unverified.)
- [ ] Primitive types have distinct encodings.
- [ ] Integer encoding does not require decimal string conversion.
  (Keep pending until the implementation constraint is verified directly;
  a large-integer regression alone does not establish every aspect of this
  requirement.)
- [x] Float encoding preserves signed zero. (Existing regression test.)
- [x] Tuple ordering is preserved. (PR #26 regression test.)
- [x] Optional None marker is explicitly represented. (PR #26 direct marker test.)
- [x] Source identity and spans are validated but excluded from the digest. (Existing regression tests.)
- [ ] Invalid or incomplete ASTs fail closed.
- [x] Encoding is iterative. (Existing nested-expression regression test.)
- [x] Regression and new tests pass in the Owner's Termux environment: 19 focused tests; 189 tests and 87 subtests in the full suite.
- [ ] Final diff contains no out-of-scope changes.

No acceptance criterion may be marked VERIFIED without corresponding
execution evidence.

## 9. Verification Plan

The Owner will run:

`python -m pytest -v`

The exact command, environment, exit code, result, branch, and commit must be
recorded after execution.

Remote CI and local Termux results must remain distinct.

No performance or memory improvement is claimed by this milestone.

## 10. Change Control

No commit, push, merge, release, or deployment is authorized by this document.

Any scope expansion requires a separate Change Plan and explicit Owner approval.


## 11. Post-Merge Verification Record — PR #26

PR #26 (`Complete ZIIF-01 fingerprint regression tests`) was merged into
`main`.

- Test commit: `4925656`.
- Merge commit: `803c245`.
- Focused fingerprint tests: 19 passed in 0.18s.
- Full local suite: 189 passed, 87 subtests passed in 0.97s.
- Environment: Android / Termux; Python 3.14.10; pytest 9.2.0.
- Syntax check: passed.
- `git diff --check`: clean.
- Test execution was performed locally by the Owner.

These results are local evidence and must not be represented as remote CI
results.

## 12. Remaining Acceptance Work

The following criteria remain pending:

- Complete primitive encoding coverage.
- Independent runtime encoding tests for every canonical node type.
- Complete invalid/incomplete AST failure-mode matrix.
- Final complete diff and implementation-contract review.
- Final acceptance decision.

Governance status reconciliation is not included in this PR. The current
governance documents have separate authority and require separately approved
changes. This Change Plan does not modify or override them.

The successful PR #26 test run does not automatically mark ZIIF-01 as
finally accepted.
