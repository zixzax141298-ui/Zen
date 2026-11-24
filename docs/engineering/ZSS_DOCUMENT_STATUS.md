# ZSS Document Status Overlay

**Document ID:** ZSS-STATUS-01  
**Revision:** 1  
**Authority:** Owner-directed reconciliation after implementation workstreams  
**Purpose:** Single place to read current approval / implementation / verification status for ZSS-01..ZSS-05 without rewriting normative design substance.

## Status vocabulary

| Field | Meaning |
|-------|---------|
| Document approval | Whether the design text is Owner-approved and merged |
| Implementation status | Whether corresponding code exists under authorized work |
| Verification status | Strength of test/audit evidence |
| Grammar change | Still requires explicit Owner approval |

Historical labels such as `DRAFT — AWAITING OWNER REVIEW` or `Implementation: NOT AUTHORIZED` on merged design docs were **phase markers**. They must not be read as denying later Owner approval or authorized implementation.

## Matrix

| Doc | Document approval | Implementation status | Verification status | Grammar change |
|------|-------------------|----------------------|---------------------|----------------|
| ZSS-01 | OWNER-APPROVED | Baseline design only | N/A (design) | NOT AUTHORIZED without Owner |
| ZSS-02 | See on-disk §3.1 authority notes | Governance design | N/A | NOT AUTHORIZED without Owner |
| ZSS-03 | OWNER-APPROVED | Parser implemented; conformance suite present | PARTIAL | NOT AUTHORIZED without Owner |
| ZSS-04 | OWNER-APPROVED | Semantic analyzer implemented (OQ-01..OQ-09) | PARTIAL | NOT AUTHORIZED without Owner |
| ZSS-05 | OWNER-APPROVED | Parser + semantic + runtime implemented | PARTIAL | NOT AUTHORIZED without Owner |

## Recommended header fields (ZSS-03 / 04 / 05)

Replace obsolete `Status: DRAFT` / `Implementation: NOT AUTHORIZED` blocks with:

```
**Document approval:** OWNER-APPROVED (design document merged to main)
**Implementation status:** <as in matrix above>
**Verification status:** PARTIAL
**Grammar change:** NOT AUTHORIZED without Owner approval
```

And a note:

```
Document approval ≠ implementation verification ≠ production readiness.
```

Full body text of ZSS-03/04/05 remains the design substance; this overlay does not rewrite normative rules.

## Related

- `ZSS_OQ_VERIFICATION_EVIDENCE.md` — OQ-01..OQ-09 test traceability
- `ZSS_PUBLIC_API_CONTRACT.md` — `execute` vs low-level APIs
