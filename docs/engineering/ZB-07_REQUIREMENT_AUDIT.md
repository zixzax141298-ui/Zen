# ZB-07 Requirement Audit

Version: 1.0
Milestone: ZB-07
Status: PRELIMINARY — implementation inspection only
Verification status: NOT_TESTED for reopened ZB-07 v2.0

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
