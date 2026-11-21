# ZB-07 Change Plan — AST Semantic Readiness & Source Identity Contract

## Document status

Owner-approved implementation scope. This document describes the proposed
patch package; it does not claim that the patch has been applied to the
repository or verified in Termux.

## 1. Repository baseline

- Approved technical baseline:
  `0003a9b961810510c2d67c7851ab3f2e9327c5b2`.
- Current GitHub `main` observed during preparation:
  `ef8ea901910f56388053c4be550ed1066b458df2`.
- Owner's Termux branch at inspection:
  `docs/security-policy-pr`, HEAD
  `b0eda55a23f75a5048d46799020dd4b8509104d8`.
- The Termux branch is an ancestor of current GitHub `main`; it is one
  commit behind and has no file delta against that `main` ref.
- GitHub comparison from the approved technical baseline to current
  `main` shows five commits, changing only `AGENTS.md`, `AI_RULES.yaml`,
  `RULES.md`, `SECURITY.md`, and `docs/engineering/ZB-07_EVIDENCE.md`.
  No source or test files changed in that comparison.
- Termux's cached `origin/main` was `65af564`; fetch is required before
  creating the implementation branch.
- Five untracked `.backup` files were reported in Termux. They are
  outside scope and must be preserved.

## 2. Objective

Introduce a stable logical-compilation-unit source identity contract while
preserving the existing source-span coordinate contract and staged
compatibility for legacy AST construction.

Provide one deterministic, iterative validation entry point that verifies
canonical AST identity, shape, source order, graph integrity, and bounded
resource use.

## 3. Approved design decisions

1. One source input represents one Logical Compilation Unit.
2. `SourceIdentifier` identifies that compilation unit; it is not a
   source range, node identity, memory address, content hash, or semantic
   fingerprint.
3. A new identifier is allocated only through an explicit caller action.
   Continuation requires the caller to pass the previously retained
   identifier. There is no implicit identity reuse or silent replacement.
4. Every node in one canonical `Program` must carry the same
   `SourceIdentifier`. A mixed or missing identity fails validation.
5. `SourceSpan` remains a coordinate range only. `SourceLocation` pairs
   one `SourceIdentifier` with one `SourceSpan`.
6. Migration is staged. Existing positional AST constructors remain
   usable as legacy construction paths; `source_id` is keyword-only and
   optional at construction. Such nodes are not canonical until explicitly
   adapted and validated.
7. `adapt_legacy_ast` requires an explicit `SourceIdentifier`, validates
   the old tree, returns a cloned tree, and never mutates the input or
   overwrites an existing identity.
8. `validate_ast(program, limits=...)` returns a structured result and
   never repairs or mutates malformed input.
9. AST traversal and validation are iterative and deterministic. Cycles
   and reused node objects are rejected.
10. Parser nesting depth is a separate accounting dimension from final
    AST structural depth. The initial parser-depth ceiling remains 256,
    matching the previous shared numeric ceiling; no existing limit is
    raised or weakened.
11. Diagnostics use a common structured model while preserving the
    existing `ParseError` message, line, column, span, and string
    representation.
12. The Lexer does not allocate compilation-unit identity. The
    caller/parser context supplies it explicitly.

## 4. Identity trust boundary and deferred identity architecture

`SourceIdentifier` is an opaque, immutable token. Its default allocator
uses a UUID4-backed string; `parse()` validates the token representation
only. Neither operation proves registry membership, issuer authenticity,
or continuity history. This patch does not create an Identity Registry
and must not claim registry-verified identity continuity.

The previously selected long-term identity architecture remains
design-only in this patch: central Identity Registry, portable Identity
Manifest, persistent entity identity, build-scoped node identity, global
`NodeIdentifier`, lineage/reconciliation, lifecycle records, offline
replica synchronization, transaction conflict handling, and atomic
Identity Consistency Groups.

Multi-origin provenance and transitive lineage are also not implemented
here. Python object identity is used only for in-memory graph
cycle/reuse detection and is never persisted as a node identity.

These exclusions preserve the approved ZB-07 source-identity
implementation scope; they do not reject the strategic architecture
decisions.

## 5. Files in scope

### Source code

- New `src/zen/ast/source_identity.py`.
- New `src/zen/ast/source_location.py`.
- New `src/zen/ast/legacy.py`.
- Update `src/zen/ast/source_span.py` documentation only; coordinate
  semantics remain unchanged.
- Update `src/zen/ast/nodes.py` with keyword-only optional source
  identity and derived location.
- Update `src/zen/ast/__init__.py` exports.
- Update `src/zen/ast/traversal.py` to reject malformed non-node child
  values instead of silently skipping them.
- Update `src/zen/ast/validation.py` with the unified
  result/diagnostic/limits contract and iterative validation.
- Update `src/zen/limits.py` with a separately named parser-depth
  ceiling; existing numeric ceilings remain unchanged.
- Update `src/zen/parser/context.py`,
  `src/zen/parser/diagnostics.py`, and `src/zen/parser/__init__.py`
  for parser-depth separation and diagnostic integration.

### Tests

- New `tests/test_ast_source_identity.py`.
- New `tests/test_ast_legacy.py`.
- New `tests/test_ast_validation_contract.py`.
- New `tests/test_ast_validation_performance.py`.
- Existing AST, traversal, validation, limits, lexer, and package API
  tests remain regression requirements.

### Documentation

- New `docs/engineering/ZB-07_CHANGE_PLAN.md`.
- Update `docs/engineering/ZB-07_EVIDENCE.md`.
- Update `README.md` milestone and status; remove stale test-count
  claims that have not been remeasured.

No other files are authorized by this Change Plan.

## 6. Compatibility

- Existing AST constructor positional arguments remain unchanged.
- Existing legacy nodes can still be constructed without `source_id`,
  but `validate_ast` rejects them as canonical input.
- Legacy conversion is explicit and non-mutating.
- Existing `ParseContext(depth, node_count)` and
  `ParseError(message, line, column, span)` positional forms remain valid.
- `ParseContext.depth` continues to mean parser nesting depth;
  `parser_depth` is an explicit alias.
- Top-level `zen` exports and Lexer behavior are unchanged.

## 7. Resource policy

Existing values remain unchanged:

- `MAX_AST_NODES=1_000_000`
- `MAX_AST_DEPTH=256`
- `MAX_DIRECT_CHILDREN=262_144`
- `MAX_EXPRESSION_NODES=262_144`
- `MAX_STATEMENT_NODES=262_144`

`MAX_PARSER_DEPTH=256` is introduced as a separately named dimension
with the same initial ceiling.

Validation callers may tighten limits but cannot raise them above the
hard ceilings. Parameter accounting reuses `MAX_DIRECT_CHILDREN`;
no new numeric parameter ceiling is introduced.

## 8. Verification plan

1. `python -m py_compile src/zen/ast/*.py src/zen/parser/*.py`
2. `python -m pytest -q`
3. `python -m unittest discover -s tests -v`
4. `python -m pytest -q -s tests/test_ast_validation_performance.py`
5. Review `git diff --check`, `git diff --stat`, and the complete diff,
   including untracked files.
6. Record actual Termux Python/OS versions, exact commands, exit codes,
   test totals, and performance/memory measurements in the evidence
   ledger only after execution.

A passing isolated draft harness is not a substitute for repository
tests in Termux or remote CI.

## 9. Acceptance criteria

- Source identity is immutable, explicit, and separate from `SourceSpan`.
- Canonical AST validation rejects missing, malformed, or inconsistent
  source identity.
- Legacy adaptation is explicit, bounded, deterministic, non-mutating,
  and rejects malformed graphs.
- Source ordering, child types, spans, cycles, and reused nodes are
  validated.
- Resource dimensions are independently accounted for with existing
  hard ceilings.
- Parser depth and AST depth are distinct named dimensions.
- Validation is iterative, deterministic, and returns inspectable
  diagnostics/results.
- Existing regression tests and new tests pass in Termux.
- Performance/memory measurements are recorded without unsupported
  improvement claims.
- Documentation reflects actual test evidence and remaining limitations.

## 10. Explicit exclusions

No grammar redesign, full Semantic Analysis, runtime rewrite,
optimizer/IR, Python–Rust integration, Lexer contract change,
new dependencies, numeric limit increase, Identity Registry
implementation, node/entity identity persistence,
manifest/reconciliation/synchronization implementation, ZSA/ZSRA,
Red/Blue/Purple Team, ZEPI, or automatic repair.

## 11. Execution boundary

The patch is to be applied on
`feature/zb07-source-identity-validation`, based on the current fetched
`origin/main`.

No changes are to be made on `main` or the active security-policy
branch. Commit, push, PR creation, merge, release, and deployment are
not performed by this preparation package.

Owner will first apply the text patch in Termux and return actual test
output for review.
