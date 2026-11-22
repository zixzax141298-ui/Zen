# ZB-07 Gap Analysis

Version: 1.0
Milestone: ZB-07
Status: PRELIMINARY — based on source inspection
Verification: NOT_TESTED for reopened v2.0

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
