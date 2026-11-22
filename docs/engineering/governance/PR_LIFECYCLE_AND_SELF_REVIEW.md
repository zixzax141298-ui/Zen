# PR Lifecycle and Self-Review

## 1. Purpose

A pull request is a review boundary, not proof of correctness, approval, or completion.

## 2. Lifecycle States

Use these states precisely:

- `PREPARED` — proposed files or patch package exist locally; repository unchanged.
- `IMPLEMENTED` — approved changes have been applied to a working branch.
- `VERIFIED` — specified checks ran and evidence is recorded.
- `PUSHED` — branch changes are confirmed on the remote.
- `PR_OPEN` — a real PR URL/number has been returned by the repository host.
- `APPROVED` — required review approval is recorded.
- `MERGED` — repository host confirms merge.
- `BLOCKED` — a required operation could not proceed; state the exact reason.

Do not conflate these states. A prepared ZIP is not a PR. A branch is not a PR. A PR is not approval or merge.

## 3. PR Content

A PR should state:
- Purpose and context.
- Exact scope and exclusions.
- Files changed and rationale.
- Architectural/security/compatibility impact.
- Verification commands and actual results.
- Known risks, unknowns, and NOT_TESTED items.
- Rollback or recovery notes where applicable.

## 4. Self-Review Checklist

- [ ] Base branch and commit are correct.
- [ ] Only authorized files and behavior changed.
- [ ] Governance and Owner decisions are consistent.
- [ ] Full diff, including untracked files, reviewed.
- [ ] No secrets or unrelated generated files.
- [ ] Links and references checked.
- [ ] Tests/checks match the claims made.
- [ ] Local and remote CI are distinguished.
- [ ] Limitations and unresolved risks are explicit.
- [ ] Owner remains final approval and merge authority.

## 5. Completion

Do not report completion based only on opening a PR. Continue only within authorized scope and available permissions. Never merge unless separately authorized by the Owner.
