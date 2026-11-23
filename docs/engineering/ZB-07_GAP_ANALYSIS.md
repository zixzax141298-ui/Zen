# ZB-07 Gap Analysis

Version: 1.0
Milestone: ZB-07
Status: HISTORICAL PRELIMINARY SNAPSHOT — superseded by Section 6 below
Current baseline: `e425d0a2a356a3e3d87e8b56987c6b5d36ea463a`

## 1. Purpose

This document separates existing implementation from missing contract work.
It does not claim runtime correctness or successful verification.

## 2. Identified gaps

### GAP-ZB07-01 — FunctionDecl source metadata

Observed:
- FunctionDecl has name, parameters, and body.
- It does not expose name_span or parameter_spans in the inspected baseline.
- Canonical validation therefore cannot establish the full declaration-name,
  parameter, and body source-order contract.

Required:
- Add keyword-only optional name_span and parameter_spans.
- Preserve old positional constructor calls.
- Require both fields for canonical validation.
- Validate span types, parameter count, declaration containment, order, and
  non-overlap.
- Do not represent these spans as AST child nodes.

### GAP-ZB07-02 — Legacy adapter behavior with missing FunctionDecl metadata

Observed:
- The adapter clones nodes iteratively using dataclasses.replace.
- It does not currently invent FunctionDecl metadata.

Required:
- Legacy pre-validation must permit both metadata fields to be absent.
- A partially present or malformed metadata pair must be rejected.
- The adapter must preserve supplied metadata exactly.
- The adapted tree must still fail canonical validation if metadata remains
  absent.
- The adapter must never infer source offsets from function names or parameter
  strings.

### GAP-ZB07-03 — Boundary-test completeness

Observed:
- Existing tests cover several over-limit conditions.
- Existing hard ceilings are already defined.
- The test suite does not establish a complete limit-1 / exact / limit+1
  matrix for every independently configurable AST validation dimension.

Required:
- Add focused boundary tests for total nodes, AST depth, expression nodes,
  statement nodes, parameter count, and direct-child count.
- Add parser-depth and parser-node-count boundary tests.
- Do not increase production ceilings to make tests pass.

### GAP-ZB07-04 — Fingerprint regression protection

Observed:
- The fingerprint encoder uses an explicit closed FunctionDecl schema:
  name, parameters, and body.
- SourceIdentifier and SourceSpan are excluded from the v1 digest.

Required:
- Keep FunctionDecl source metadata outside the v1 fingerprint schema.
- Add a regression proving metadata-coordinate differences do not alter the
  structural fingerprint when the AST structure and values are otherwise
  identical.
- Do not change the fingerprint version or encoding format.

### GAP-ZB07-05 — Verification evidence

Observed:
- A non-gating performance/memory measurement test exists.
- Its existence is not a measurement result.
- Previous historical test results do not verify the reopened patch.

Required:
- Run the full regression suite in Termux after the Owner applies the patch.
- Run the measurement test and record actual output.
- Record environment, exact commands, exit codes, and tested revision.
- Keep remote CI status separate from local Termux results.

## 3. Existing implementation areas requiring regression verification

The following areas were present in the inspected baseline:
- SourceIdentifier and SourceLocation.
- AST node source identity.
- Legacy AST adapter.
- Iterative traversal.
- Structured AST validation result and diagnostics.
- Child type and source-order validation.
- Cycle and reused-node detection.
- AST resource counters.
- Parser-depth separation.
- Iterative fingerprint encoding.

These are implementation observations, not VERIFIED statuses.

## 4. Scope controls

Do not:
- Redesign grammar or parser implementation.
- Increase resource ceilings.
- Change SECURITY.md.
- Add dependencies.
- Change the fingerprint v1 schema.
- Start ZIIF-01 follow-on work.
- Add identity registry, manifest, lineage, or synchronization features.
- Modify runtime, semantic analysis, optimizer, or IR.

## 5. Conclusion

The primary implementation gap is FunctionDecl source metadata and its
canonical validation contract. Legacy compatibility, resource boundary
coverage, fingerprint regression protection, and reopened verification
evidence must be completed before ZB-07 can close.

## 6. Current Gap Reconciliation — 2026-11-23

Baseline: `e425d0a2a356a3e3d87e8b56987c6b5d36ea463a`.

The original GAP-ZB07 identifiers and definitions are retained. This
section updates their status using integrated PR history and EVD-ZB07-003.
The earlier preliminary sections remain historical records.

### GAP-ZB07-01 — FunctionDecl source metadata

**Implementation status: RESOLVED IN INTEGRATED IMPLEMENTATION.**
**Verification status: PARTIALLY_VERIFIED.**

Evidence:
- PR #18 bounded FunctionDecl metadata validation.
- Canonical validation covers required metadata and parameter-span
  constraints.
- PR #23 adds related diagnostic locations for span/identity conflicts.
- Regression suite passed on the recorded main baseline.

Remaining:
- Complete acceptance mapping for keyword-only optional metadata,
  positional constructor compatibility, metadata presence, span types,
  parameter count, containment, order and non-overlap.
- Confirm all related cases in the final verification matrix.

### GAP-ZB07-02 — Legacy adapter behavior with missing FunctionDecl metadata

**Implementation status: IMPLEMENTED IN CURRENT INTEGRATION.**
**Verification status: PARTIALLY_VERIFIED.**

The adapter and legacy compatibility tests are present in the integrated
implementation and regression suite.

Remaining:
- Trace both-absent metadata behavior.
- Trace partially present and malformed metadata rejection.
- Confirm supplied metadata is preserved exactly.
- Confirm adapted trees without required metadata still fail canonical
  validation.
- Confirm no source offsets are inferred from names or parameter strings.

No metadata invention is permitted.

### GAP-ZB07-03 — Boundary-test completeness

**Implementation status: PARTIALLY ADDRESSED.**
**Verification status: PARTIALLY_VERIFIED.**

Evidence:
- PR #20 enforces ParseContext initial depth and node resource bounds.
- PR #21 covers parameter accounting boundaries.
- PR #22 covers aggregate parameter accounting.
- Existing AST limit tests cover additional resource dimensions.

Remaining:
- Complete the limit-1, exact-limit and limit+1 matrix for total nodes,
  AST depth, expression nodes, statement nodes, parameter count and
  direct-child count.
- Complete corresponding parser-depth and parser-node-count coverage.
- Do not increase production ceilings to make tests pass.

### GAP-ZB07-04 — Fingerprint regression protection

**Implementation status: IMPLEMENTED.**
**Verification status: PARTIALLY_VERIFIED.**

Evidence:
- PR #19 adds regression protection for FunctionDecl source metadata
  exclusion from the fingerprint-v1 structural digest.
- `test_function_source_metadata_is_excluded_from_v1_fingerprint`
  passed in the recorded regression suite.

Remaining:
- Preserve the existing fingerprint-v1 schema, encoding and digest
  contract.
- Retain the regression test in the final acceptance traceability.

No fingerprint version or encoding change is authorized.

### GAP-ZB07-05 — Verification evidence

**Implementation status: EVIDENCE RECORDED.**
**Verification status: PARTIALLY_VERIFIED.**

EVD-ZB07-003 records:
- Python 3.14.10 on Android / Termux, Linux aarch64.
- `py_compile` completed without reported error.
- `unittest`: 176 tests, OK.
- Full pytest: 176 passed, 87 subtests passed.
- Standalone performance test: 1 passed.
- 2,001-node measurements from two separate executions.
- Matching local HEAD and origin/main at the recorded baseline.

Remaining:
- Exact execution time and separately captured exit codes were not
  recorded.
- Remote CI status is not established by local Termux results.
- Cross-platform behavior is not established.
- Performance values must remain observations, not improvement claims.
- Final diff and acceptance traceability remain required.

## 7. Remaining Milestone Gaps

1. Complete acceptance-criterion mapping for ZB07-01 through ZB07-11.
2. Complete resource boundary matrix for every applicable dimension.
3. Finish legacy adapter and FunctionDecl metadata edge-case traceability.
4. Review fingerprint-v1 and resource-ceiling preservation in the final diff.
5. Keep local Termux, remote CI and cross-platform evidence distinct.
6. Complete final repository review and Owner-approved completion report.

## 8. Conclusion

The historical FunctionDecl metadata implementation gap is resolved in
the integrated implementation. Fingerprint regression protection and
several resource-boundary changes are also integrated.

The remaining work is requirement-level verification, complete boundary
coverage, evidence traceability and final review.

ZB-07 remains IN_PROGRESS and OPEN. This reconciliation does not declare
the milestone complete.
