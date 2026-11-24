# Changelog

All notable project changes are recorded here.
This file distinguishes implemented functionality from specified syntax
and planned work.

## [Unreleased] — post-PR #40

### Documentation
- ZSS-03 / ZSS-04 / ZSS-05 status headers: document approval vs implementation vs verification.
- Added `docs/engineering/ZSS_OQ_VERIFICATION_EVIDENCE.md` (OQ-01..OQ-09 evidence matrix).

## [Unreleased] — post-PR #39 residuals

### Fixed
- Semantic diagnostics now propagate `source_id` from the `Program` AST.
- Stronger diagnostic field assertions (related_span, source_id).
- Runtime function equality rejected under OQ-07 primitive-only equality (regression tests).

### Documentation
- Added `docs/engineering/ZSS_PUBLIC_API_CONTRACT.md` (`execute` vs low-level APIs).

## [0.1.0] — ZSS pipeline (through PR #39)

### Added
- Recursive-descent parser with resource limits and depth protection.
- Semantic analyzer (OQ-01..OQ-09) with symbol-identity definite assignment.
- Tree-walk interpreter (OQ-07: short-circuit, strict Boolean, no string+, primitive equality).
- Public `execute()` fail-closed pipeline.
- Grammar/semantic/runtime regression suite (pytest, Python 3.10–3.14).

### Changed
- CI runs compileall + pytest only (Ruff/Bandit removed per Owner directive).
- README reflects implemented components (not “parser planned”).
