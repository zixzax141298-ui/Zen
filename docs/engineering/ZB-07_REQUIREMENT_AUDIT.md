# ZB-07 Requirement Audit

Version: 1.0
Milestone: ZB-07
Status: HISTORICAL PRELIMINARY SNAPSHOT — superseded by Section 2 below
Current verification status: PARTIALLY_VERIFIED on main baseline `e425d0a2a356a3e3d87e8b56987c6b5d36ea463a`

## Evidence labels

- OBSERVED: directly inspected in the repository or measured.
- DERIVED: logically concluded from observations.
- ASSUMED: provisional and not verified.
- UNKNOWN: not established.
- NOT_TESTED: no relevant reopened test execution is recorded.

## Requirement audit

| ID | Requirement | Preliminary implementation observation | Current gap | Verification |
|---|---|---|---|---|
| ZB07-01 | Source identity | SourceIdentifier and node source_id are present | Re-run canonical consistency and malformed identity tests on reopened baseline | NOT_TESTED |
| ZB07-02 | Immutable SourceIdentifier | Frozen identifier type and explicit creation/parsing APIs are present | Re-run immutability and invalid-value tests | NOT_TESTED |
| ZB07-03 | SourceIdentifier / SourceSpan separation | SourceSpan and SourceLocation are separate types | Re-run location pairing and invalid-span tests | NOT_TESTED |
| ZB07-04 | Legacy AST adapter | Iterative non-mutating adapter is present | Confirm absent FunctionDecl metadata is not fabricated and adapted legacy data remains non-canonical | NOT_TESTED |
| ZB07-05 | Source-order validation and FunctionDecl metadata | Child source-order validation exists; FunctionDecl metadata was absent in inspected baseline | Add name_span and parameter_spans; validate presence, count, containment, ordering, and non-overlap | NOT_TESTED |
| ZB07-06 | Unified AST validation | Structured ASTValidationResult, Diagnostic, and validate_ast are present | Re-run valid, invalid, incomplete, and deterministic-result tests | NOT_TESTED |
| ZB07-07 | Node and child validation | Known-node checks, child type checks, and collection checks are present | Re-run malformed node, child, and required-field tests | NOT_TESTED |
| ZB07-08 | AST graph integrity | Iterative cycle and reused-node detection are present | Re-run direct/indirect cycle, reuse, and malformed-graph tests | NOT_TESTED |
| ZB07-09 | Span and identity integrity | Source identity and span validation are present | Integrate FunctionDecl metadata spans and verify all ordering/containment cases | NOT_TESTED |
| ZB07-10 | Resource accounting | Node, depth, expression, statement, parameter, and direct-child counters exist | Complete limit-1, exact-limit, and limit+1 tests; retain all hard ceilings | NOT_TESTED |
| ZB07-11 | Iterative deterministic validation | Explicit stack traversal and a non-gating measurement test are present | Re-run determinism and deep-tree tests; collect actual runtime and peak-memory values | NOT_TESTED |

## Cross-cutting contracts

| Contract | Observation | Verification |
|---|---|---|
| Parser depth separate from AST depth | MAX_PARSER_DEPTH and ParseContext.parser_depth are present | NOT_TESTED |
| Common diagnostic model | Diagnostic and ParseError integration are present | NOT_TESTED |
| Fingerprint compatibility | Explicit FunctionDecl fingerprint schema excludes source metadata | NOT_TESTED after FunctionDecl metadata change |
| Security boundary | SECURITY.md is excluded from this change | Must be confirmed in final Git diff |
| Resource ceilings | Existing numeric ceilings are recorded in Change Plan v2.0 | Must be checked in final diff |

## Audit conclusion

The inspected baseline contains substantial ZB-07 implementation, but this
audit does not mark any reopened requirement VERIFIED.

ZB07-05 is the principal identified implementation gap. ZB07-09 and ZB07-10
also require focused integration and boundary verification. All other
requirements require regression evidence against the reopened revision.

No test result, benchmark, memory result, or CI result is claimed by this
document.

## 2. Current Requirement Assessment — 2026-11-23

Baseline: `e425d0a2a356a3e3d87e8b56987c6b5d36ea463a`.

Evidence source: EVD-ZB07-003 and integrated PR history #18–#23.

The status PARTIALLY_VERIFIED means that relevant implementation and
regression evidence exist, but this audit does not establish complete
criterion-by-criterion acceptance.

| ID | Official requirement | Current implementation/evidence | Remaining verification | Status |
|---|---|---|---|---|
| ZB07-01 | Source identity | SourceIdentifier and AST node source identity; identity validation tests are included in the regression suite | Complete malformed, missing, mixed and consistency case traceability | PARTIALLY_VERIFIED |
| ZB07-02 | Immutable SourceIdentifier | Immutable identifier implementation; immutability and invalid-value tests are included in the suite | Map every identifier creation/parsing acceptance condition to evidence | PARTIALLY_VERIFIED |
| ZB07-03 | SourceIdentifier / SourceSpan separation | Separate SourceSpan and SourceLocation contracts | Complete valid/invalid location-pairing and span boundary traceability | PARTIALLY_VERIFIED |
| ZB07-04 | Legacy AST adapter | Explicit iterative adapter; legacy compatibility tests are included in the suite | Confirm all non-mutation, absent-metadata and malformed-pair cases against acceptance criteria | PARTIALLY_VERIFIED |
| ZB07-05 | Source-order validation and FunctionDecl metadata | PR #18 metadata validation; PR #19 fingerprint regression; source-order and related-location coverage in PR #23 | Complete traceability for presence, count, containment, ordering, non-overlap and legacy behavior | PARTIALLY_VERIFIED |
| ZB07-06 | Unified AST validation | ASTValidationResult, Diagnostic and validate_ast implementation; regression suite passed | Map valid, invalid, incomplete and deterministic-result contracts individually | PARTIALLY_VERIFIED |
| ZB07-07 | Node and child validation | Node, child-type and collection validation; regression suite passed | Complete malformed-node and required-field acceptance mapping | PARTIALLY_VERIFIED |
| ZB07-08 | AST graph integrity | Iterative cycle and reused-node detection; graph tests included in regression suite | Confirm direct/indirect cycles, reuse and malformed graph cases against full acceptance criteria | PARTIALLY_VERIFIED |
| ZB07-09 | Span and identity integrity | Span and identity validation; PR #23 related-location diagnostics for identity mismatch, containment and sibling overlap | Complete source-span and identity edge-case traceability | PARTIALLY_VERIFIED |
| ZB07-10 | Resource accounting | Node, depth, expression, statement, parameter and direct-child accounting; PR #20–#22 boundary work | Confirm limit-1, exact-limit and limit+1 for every independently configurable dimension | PARTIALLY_VERIFIED |
| ZB07-11 | Iterative deterministic validation | Iterative traversal, deep-validation and non-gating measurement test; EVD-ZB07-003 records local measurements | Complete deterministic behavior and performance/memory acceptance mapping | PARTIALLY_VERIFIED |

### Cross-cutting contracts

| Contract | Evidence | Status |
|---|---|---|
| Parser depth separate from AST depth | ParseContext boundary implementation and regression suite | PARTIALLY_VERIFIED |
| Common diagnostic model | Diagnostic and ParseError integration; parser and AST regression suite | PARTIALLY_VERIFIED |
| Fingerprint compatibility | PR #19 and `test_function_source_metadata_is_excluded_from_v1_fingerprint` | PARTIALLY_VERIFIED |
| Security boundary | SECURITY.md excluded from approved scope; final diff check still required | NOT_YET_FINAL_REVIEWED |
| Resource ceilings | Existing boundary tests; final diff must confirm no numeric ceiling changes | NOT_YET_FINAL_REVIEWED |
| Remote CI | No current-baseline CI result recorded in EVD-ZB07-003 | UNKNOWN |
| Cross-platform verification | No independent platform run recorded | NOT_TESTED |

### Audit conclusion

The historical preliminary audit identified FunctionDecl source metadata
as the principal implementation gap. That implementation gap has since
been addressed in the integrated PR history, including bounded validation
and fingerprint-v1 regression protection.

This does not make ZB07-05 fully verified. The complete acceptance
criteria still require traceable evidence.

Resource boundary completeness, legacy compatibility traceability,
cross-cutting contract review and final diff review also remain open.

The preliminary audit above is retained as a historical snapshot.
This section is the current assessment on the recorded main baseline.
