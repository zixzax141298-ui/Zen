# ZIIF-01 — Canonical AST Identity Fingerprint

## 1. Document Status

Milestone: ZIIF-01
Status: APPROVED — IMPLEMENTATION APPLIED; LOCAL TESTS PASSED; FINAL REVIEW PENDING
Baseline branch: feature/ziif-01-ast-fingerprint
Baseline commit: a62f4e904adfc9f9ae1e2d15b1d0d8e57fc5d676

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

## 7. Validation and Failure Behavior

The AST must pass the existing canonical `validate_ast` contract.

Invalid source identity, mismatched source identity, invalid spans, invalid
children, cycles, reused nodes, unsupported node types, or incomplete
validation must prevent fingerprint generation.

The encoder must reject values outside its closed schema.

## 8. Acceptance Criteria

- [ ] Public API is exported.
- [ ] Output format is versioned and deterministic.
- [ ] Encoding uses SHA-256 and domain separation.
- [ ] Every current canonical AST node type has an explicit schema.
- [ ] Field order is fixed and tested.
- [ ] Primitive types have distinct encodings.
- [ ] Integer encoding does not require decimal string conversion.
- [ ] Float encoding preserves signed zero.
- [ ] Tuple ordering is preserved.
- [ ] Optional values are represented explicitly.
- [ ] Source identity and spans are validated but excluded from the digest.
- [ ] Invalid or incomplete ASTs fail closed.
- [ ] Encoding is iterative.
- [ ] Regression and new tests pass in the Owner's Termux environment.
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
