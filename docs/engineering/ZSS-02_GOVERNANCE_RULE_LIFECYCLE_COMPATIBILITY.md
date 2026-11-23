# ZSS-02 — Governance, Rule Lifecycle & Compatibility

**Document ID:** ZSS-02
**Revision:** 2
**Status:** OWNER-APPROVED (CONSOLIDATED RESULT)
**Owner Approval:** APPROVED
**Approval Basis:** Explicit Owner approval through GitHub merge (PR #30). The Owner has explicitly approved the consolidated ZSS-02 result.
**Approval Status:** The merged document is approved by the Owner.
**Merge Evidence:** PR #30 merged 2026-11-23T16:59:35Z (head `98d2998f6dee8b1fe711525ca944b22adc7c2f21`).
**Project:** ZEN — Zen Structured Syntax
**Scope:** Governance and Specification
**Implementation:** NOT AUTHORIZED
**Migration Execution:** NOT AUTHORIZED

> PROVENANCE NOTE: This on-disk text is a reconstructed consolidation based on recovered decisions. It has **not** been verified as a verbatim copy of any earlier Owner-approved Revision 2 wording. Owner approval applies to the **consolidated ZSS-02 result** as merged. Verbatim historical identity with a prior Revision 2 text remains **unverified**.

## 1. Purpose

This specification establishes the governance framework for syntax
rules and Grammar Versions within Zen Structured Syntax (ZSS).

It defines authority boundaries, rule identity and revision governance,
rule lifecycle, governance artifacts, immutable Rule Manifests,
Grammar Version immutability, directional compatibility, migration
governance, and auditability.

ZSS-02 establishes governance requirements. It does not implement
a Registry, Parser, migration engine, or runtime subsystem.

## 2. Scope and Boundaries

ZSS-02 governs the lifecycle and governance of syntax rules and
Grammar Versions.

It covers rule identity, revision, approval, activation, deprecation,
supersession, retirement, Grammar Version composition, compatibility
assessment, migration governance, and historical traceability.

ZSS must remain an extensible component of the ZEN ecosystem.
Its governance must not obstruct independently governed ZEN subsystems.

ZSS-02 does not modify the approved ZSS-01 Grammar Baseline.

## 3. Authority Model

ZSS adopts three distinct authority roles.

### 3.1 Decision Authority

Determines whether a governance proposal, rule change, or Grammar
Version is legitimately approved.

### 3.2 Normative Authority

Establishes the authoritative technical meaning of syntax rules.

The Grammar Specification is the normative source for rule definitions.

### 3.3 Implementation Authority

Implements approved specifications and maintains conformance.

Implementation does not grant authority to redefine approved
normative requirements or bypass governance decisions.

These authorities are conceptually distinct. Their implementation,
delegation, and authorization mechanisms remain subject to further
governance decisions.

## 4. Governance Artifacts

ZSS recognizes four principal governance artifacts.

### 4.1 Rule Registry

The Rule Registry is the authoritative index for rule identity,
revision references, governance status, historical status, and
relevant version relationships.

The Registry must not become an alternative normative definition
of syntax.

Every Registry status must be traceable to its corresponding
Governance Record or authoritative governance decision.

### 4.2 Grammar Specification

The Grammar Specification is the sole normative source defining
syntax rules and their technical requirements.

A Registry entry does not replace the normative specification.

### 4.3 Governance Record

The Governance Record establishes the legitimacy and provenance
of governance decisions, including approvals and lifecycle transitions.

### 4.4 Verification Evidence

Verification Evidence records proof that applicable requirements
have been checked.

Verification evidence and approval decisions are distinct.
Verification does not independently grant governance approval.

## 5. Rule Identity and Revision

Every syntax rule must have a permanent and unique Rule ID.

The following concepts must remain distinct:

- Rule ID: permanent identity of a syntax rule.
- Rule Revision: immutable revision of that rule.
- Grammar Version: approved grammar composition containing
  specific rule revisions.

A Rule ID must never be reassigned to an unrelated rule.

An existing Rule Revision must not be silently overwritten.

A normative change requires a new revision or an appropriately
governed replacement.

Historical revisions must remain traceable.

## 6. Rule Lifecycle

The governance lifecycle includes:

PROPOSED
UNDER_REVIEW
VERIFIED
APPROVED
ACTIVE

Additional lifecycle states include:

- REJECTED
- WITHDRAWN
- DEPRECATED
- SUPERSEDED
- RETIRED

Lifecycle transitions must have a legitimate governance basis
and preserve historical traceability.

### 6.1 Deprecated

A Deprecated rule remains historically valid and identifiable,
but its use is discouraged or subject to an explicit warning.

Deprecation does not itself mean that the rule has been replaced.

### 6.2 Superseded

A Superseded rule has been replaced by another rule or an explicitly
identified successor.

The replacement relationship must be recorded and traceable.

Superseded is distinct from Deprecated and Retired.

### 6.3 Retired

A Retired rule is no longer eligible for use in new Grammar Versions
under the applicable governance decision.

Its historical identity and records must remain available.

### 6.4 Rejected and Withdrawn

Rejected indicates that a proposal did not receive approval.

Withdrawn indicates that a proposal was withdrawn from consideration.

Neither state permits silent activation.

## 7. Rule Evolution

Rule evolution must preserve identity, revision history,
and governance provenance.

A rule change must identify:

- Affected Rule ID.
- Relevant previous revision.
- Proposed revision or replacement.
- Normative change.
- Affected Grammar Versions.
- Compatibility implications.
- Required approval.
- Verification evidence.

Breaking changes require explicit governance approval.

Conflicting rule definitions must not be resolved through silent
precedence, implementation convenience, or undocumented interpretation.

## 8. Immutable Rule Manifest

Every approved Grammar Version must have an associated
immutable Rule Manifest.

The manifest records all Rule IDs and exact Rule Revisions
included in that Grammar Version.

The manifest must:

1. Identify the complete rule composition.
2. Reference corresponding Registry identities and revisions.
3. Be sealed after approval.
4. Preserve its historical contents.
5. Support integrity verification.
6. Support historical reconstruction.

A sealed manifest must never be silently updated.

A change to the rule composition requires a new manifest
associated with the appropriately governed Grammar Version.

The exact serialization, canonicalization, digest, hash,
and signature mechanisms remain deferred technical decisions.

## 9. Grammar Version Immutability

Every ratified Grammar Version is permanently immutable.

An approved Grammar Version must never be:

- Edited in place.
- Overwritten.
- Rewritten to represent a later grammar.
- Silently corrected.
- Reused for a different grammar composition.

Corrections and evolution must produce a new governed version
or artifact.

Historical versions must remain available for audit and reconstruction.

Historical errors must be handled through explicit correction records
rather than deletion or modification of the historical artifact.

A Grammar Version's support status may change without changing
its immutable historical content.

Immutability applies to the historical Grammar Version artifact.
It does not prohibit legitimate changes to governance metadata,
support status, or associated governance records.

## 10. Compatibility Governance

Compatibility is directional.

It must always be evaluated using an explicit pair:

Source Grammar Version -> Target Grammar Version

Compatibility in the reverse direction must be evaluated separately.

A compatibility result in one direction does not automatically
establish compatibility in the opposite direction.

The Compatibility Matrix governs assessment across relevant dimensions:

- Syntax.
- Semantics.
- AST.
- Parser.
- Source validity.
- Behavioral compatibility.

Recognized assessment outcomes include:

- COMPATIBLE
- INCOMPATIBLE
- CONDITIONALLY_COMPATIBLE
- INDETERMINATE
- NOT_APPLICABLE

An assessment must be supported by relevant manifests
and verification evidence.

The precise compatibility classification perspective,
detailed test procedures, and formal classification rules remain deferred.

## 11. Migration Governance

Migration is governed as a controlled process.

Its lifecycle includes:

ASSESSMENT
PLANNING
PROPOSAL
APPROVAL
EXECUTION
VERIFICATION
COMPLETION

The existence of an Execution stage does not grant authorization
to execute a migration.

Execution requires separate explicit authorization
from the appropriate authority.

A Migration Record must provide traceability.

Its conceptual fields include:

- migration_id
- source_version
- target_version
- compatibility
- change_set
- approval_record
- verification_evidence
- migration_status

Migration records must preserve historical information.

Migration must not silently alter the meaning of an approved
Grammar Version or bypass governance requirements.

## 12. Governance Consistency

The following invariants apply:

1. Rule IDs must be unique and permanent.
2. A Rule Revision must belong to a valid Rule ID.
3. An active rule must have a normative definition.
4. Registry status must have traceable governance provenance.
5. An approved Grammar Version must have an associated
   immutable Rule Manifest.
6. A sealed manifest must not be modified.
7. Activation requires legitimate approval.
8. Compatibility claims require explicit assessment.
9. Reverse compatibility must not be inferred automatically.
10. Migration must not bypass explicit authorization.
11. Historical governance records must remain traceable.
12. Conflicts must be resolved through explicit governance decisions.

## 13. Auditability and Reproducibility

ZSS governance must support historical inspection and reconstruction.

A reviewer must be able to trace:

- A Rule ID to its revisions.
- A revision to its normative definition.
- A lifecycle transition to its governance decision.
- A Registry status to its Governance Record.
- A Grammar Version to its Rule Manifest.
- A compatibility assessment to its source and target versions.
- A migration to its approval and verification evidence.

A reconstruction claim requires sufficient integrity
and historical evidence.

When evidence is insufficient, the result must remain INDETERMINATE.

Historical records must not be silently rewritten.

## 14. Acceptance Criteria

ZSS-02 governance is satisfied when the specification establishes:

1. The Three Authority Model.
2. The distinct roles of Registry, Grammar Specification,
   Governance Record, and Verification Evidence.
3. Permanent Rule ID identity.
4. Immutable Rule Revision history.
5. Explicit Rule lifecycle states and transition provenance.
6. Distinction between Deprecated, Superseded, and Retired.
7. Immutable Rule Manifest per approved Grammar Version.
8. Permanent Grammar Version immutability.
9. Directional compatibility governance.
10. Explicit migration governance and authorization separation.
11. Traceability and auditability of governance decisions.
12. Preservation of historical records.
13. Protection of independently governed ZEN subsystems.
14. Separation between specification approval
    and implementation authorization.

## 15. Deferred Technical Decisions

The following decisions are intentionally deferred:

- Registry serialization format.
- Manifest serialization format.
- Governance Record and Verification Evidence storage.
- Canonicalization procedures.
- Hash and digest algorithms.
- Digital signature mechanisms.
- Detailed semantic-versioning rules, including 0.x behavior.
- Formal lifecycle transition implementation.
- Delegation and authorization mechanisms.
- Compatibility test procedures.
- Compatibility classification perspective and detailed semantics.
- Migration Record storage and implementation.
- Audit retention mechanisms.
- Recovery and integrity investigation procedures.

Deferral does not invalidate the normative governance principles
established in this specification.

These details must be resolved through separately governed
specification or implementation work.

## 16. Explicit Non-Goals and Boundaries

ZSS-02 does not authorize:

- Parser implementation.
- Lexer modification.
- AST modification.
- ZASI or ZEAI implementation changes.
- Changes to the approved ZSS-01 Grammar Baseline.
- Registry implementation.
- Migration execution.
- Automatic rule activation.
- Automatic compatibility approval.
- Changes to unrelated ZEN subsystems.
- Repository-wide architectural restructuring.

ZSS-02 is a governance specification, not an implementation plan.

## 17. Document Governance and Approval

Document: ZSS-02 — Governance, Rule Lifecycle & Compatibility

Revision: 2

Owner Approval: APPROVED (consolidated result via GitHub merge PR #30).

This reconstructed text incorporates the recovered corrections:

- CR-01: Registry status must be traceable to its Governance Record
  or underlying governance decision.
- CR-02: Superseded must be explicitly distinguished from other
  lifecycle states and preserve its replacement relationship.
- CR-03: Compatibility classification perspective remains deferred.
- CR-04: Migration lifecycle execution is not authorization
  to execute a migration.
- CR-05: Immutable historical Grammar Version content is distinct
  from mutable governance metadata.

Owner approval applies to the consolidated ZSS-02 result as merged.
Verbatim identity with any earlier Revision 2 manuscript remains unverified.
This document does not authorize implementation, migration execution, or
changes to other workstreams.

Any future revision must follow the applicable governance
and approval process.

---

END OF ZSS-02 REVISION 2 (OWNER-APPROVED CONSOLIDATED RESULT)
