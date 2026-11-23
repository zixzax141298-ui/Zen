# ZB-07 Verification Matrix

Version: 1.0
Milestone: ZB-07
Status: PARTIALLY_VERIFIED — acceptance remains open.
Baseline: `e425d0a2a356a3e3d87e8b56987c6b5d36ea463a`
Evidence: `EVD-ZB07-003`

## 1. Status definitions

- VERIFIED: every approved acceptance criterion has sufficient traceable
  implementation and verification evidence.
- PARTIALLY_VERIFIED: relevant implementation and some verification
  evidence exist, but complete acceptance coverage is not established.
- NOT_TESTED: no relevant test execution is recorded.
- UNKNOWN: available evidence is insufficient to establish the claim.

A passing full regression suite does not automatically verify every
individual requirement.

## 2. Official requirement matrix

| ID | Official requirement | Implementation / evidence reference | Remaining verification | Status |
|---|---|---|---|---|
| ZB07-01 | Source identity | SourceIdentifier, AST node source_id and identity validation | Complete malformed, missing, mixed and consistency case traceability | PARTIALLY_VERIFIED |
| ZB07-02 | Immutable SourceIdentifier | Immutable identifier implementation and regression tests | Map creation, parsing, immutability and invalid-value acceptance criteria | PARTIALLY_VERIFIED |
| ZB07-03 | SourceIdentifier / SourceSpan separation | Separate SourceSpan and SourceLocation contracts | Complete location pairing and invalid-span edge-case mapping | PARTIALLY_VERIFIED |
| ZB07-04 | Legacy AST adapter | Explicit iterative non-mutating adapter | Verify absent, partial and malformed FunctionDecl metadata behavior; no inferred offsets | PARTIALLY_VERIFIED |
| ZB07-05 | Source-order validation and FunctionDecl metadata | PR #18 metadata validation; PR #19 fingerprint regression; PR #23 related diagnostic locations | Complete presence, count, containment, ordering, non-overlap and compatibility mapping | PARTIALLY_VERIFIED |
| ZB07-06 | Unified AST validation | ASTValidationResult, Diagnostic and validate_ast | Map valid, invalid, incomplete and deterministic-result criteria | PARTIALLY_VERIFIED |
| ZB07-07 | Node and child validation | Known-node, child-type and collection validation | Complete malformed node, child and required-field coverage mapping | PARTIALLY_VERIFIED |
| ZB07-08 | AST graph integrity | Iterative cycle and reused-node detection | Map direct/indirect cycle, reused-node and malformed-graph criteria | PARTIALLY_VERIFIED |
| ZB07-09 | Span and identity integrity | Source identity/span checks and PR #23 related locations | Complete span order, containment, overlap and identity edge-case mapping | PARTIALLY_VERIFIED |
| ZB07-10 | Resource accounting | AST and parser counters; PR #20, #21 and #22 | Complete limit-1, exact-limit and limit+1 matrix for every applicable dimension | PARTIALLY_VERIFIED |
| ZB07-11 | Iterative deterministic validation | Iterative traversal, deep validation and measurement test | Complete determinism, deep-tree and performance/memory acceptance mapping | PARTIALLY_VERIFIED |

## 3. Cross-cutting contracts

| Contract | Evidence | Status |
|---|---|---|
| Parser depth separate from AST depth | ParseContext implementation and regression suite | PARTIALLY_VERIFIED |
| Common diagnostic model | Diagnostic and ParseError integration | PARTIALLY_VERIFIED |
| Fingerprint-v1 compatibility | PR #19 and FunctionDecl metadata exclusion regression | PARTIALLY_VERIFIED |
| Resource ceilings unchanged | Existing boundary tests; final diff review required | NOT_YET_FINAL_REVIEWED |
| SECURITY.md unchanged | Approved scope excludes SECURITY.md; final diff review required | NOT_YET_FINAL_REVIEWED |
| Remote CI | No current-baseline CI evidence recorded | UNKNOWN |
| Cross-platform behavior | No independent platform execution recorded | NOT_TESTED |

## 4. Recorded local evidence

- Date: 2026-11-23 (+07:00); exact execution time not captured.
- Environment: Android / Termux, Linux aarch64.
- Python: 3.14.10.
- Baseline: `e425d0a2a356a3e3d87e8b56987c6b5d36ea463a`.
- `py_compile`: completed without reported error.
- `unittest discover`: 176 tests, OK.
- Full pytest: 176 passed, 87 subtests passed.
- Standalone performance test: 1 passed.
- Measurement: 2,001 nodes, 0.177319 seconds, 281,497 peak bytes.
- Detailed evidence and limitations: `docs/engineering/ZB-07_EVIDENCE.md`,
  EVD-ZB07-003.

The measurement is a local observation, not a cross-device benchmark.
The separate measurement during unittest discovery is recorded separately
in the Evidence Ledger. Neither measurement establishes improvement.

## 5. Remaining verification gates

1. Complete requirement-level traceability for ZB07-01 through ZB07-11.
2. Complete limit-1, exact-limit and limit+1 coverage for applicable
   resource dimensions.
3. Complete legacy adapter and FunctionDecl metadata edge-case review.
4. Verify fingerprint-v1 schema and resource ceilings remain unchanged.
5. Record remote CI and cross-platform results only when actually available.
6. Review the complete final diff, including all six approved documents.
7. Obtain Owner approval of the final completion report.

ZB-07 remains OPEN. This matrix does not authorize milestone closure.
