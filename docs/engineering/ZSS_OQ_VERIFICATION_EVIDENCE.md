# ZSS OQ Verification Evidence Matrix

**Document ID:** ZSS-OQ-EV-01  
**Revision:** 1  
**Baseline main:** post-PR #40  
**Purpose:** Trace Owner Questions (OQ-01..OQ-09) to implementation and tests.  
**Does not claim production readiness.**

Status key:

- **VERIFIED** — implementation + direct regression tests observed green
- **PARTIAL** — core behavior present; edge cases or formal matrix incomplete
- **NOT VERIFIED** — insufficient evidence

| OQ | Requirement (summary) | Implementation | Primary tests | Status |
|----|----------------------|----------------|---------------|--------|
| OQ-01 | Same-scope redecl rejected; nested shadowing allowed | `SemanticAnalyzer._var_decl` / `_function_decl` | `test_duplicate_*`, `test_shadowing_allowed` | VERIFIED |
| OQ-02 | Definite assignment; branch merge; symbol identity | `_initialized: set[int]` via `id(symbol)` | `test_if_*`, `test_shadow_inner_*` | VERIFIED |
| OQ-03 | Const must init; no reassignment | Semantic + runtime defense | `test_const_*` | VERIFIED |
| OQ-04 | Lexical scope; no implicit globals | `Scope` chain | undefined / nested tests | VERIFIED |
| OQ-05 | Static arity check | Call-site arity vs symbol | `test_arity_mismatch` | VERIFIED |
| OQ-06 | Only functions callable | Kind check on call | `test_not_callable` | VERIFIED |
| OQ-07 | Short-circuit; strict bool; no string+; primitive equality | `interpreter.py` | `test_short_circuit_*`, equality, string+ | VERIFIED |
| OQ-08 | Duplicate parameters rejected | Function param scan | `test_duplicate_param` | VERIFIED |
| OQ-09 | Structured diagnostics (code, span, related, source_id) | `SemanticDiagnostic` | `test_diagnostic_source_id_*`, related_span | VERIFIED |

## Known limitations

1. Formal per-production grammar conformance matrix (ZSS-03) not fully productized as a standalone tool.
2. Independent ZENTY audit may reclassify any OQ.
3. `interpret()` without prior semantic analysis is a low-level escape hatch; `execute()` is fail-closed.
4. No claim of exhaustive adversarial coverage or production hardening.

## How to re-run evidence

```bash
python -m pip install -e .
python -m compileall -q src tests
python -m pytest -q
```
