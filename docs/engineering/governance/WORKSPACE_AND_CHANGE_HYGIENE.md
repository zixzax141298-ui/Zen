# Workspace and Change Hygiene

## 1. Objective

Keep the repository understandable, reviewable, reproducible, and free of unexplained files or unrelated changes.

## 2. Baseline Before Work

Record:
- Repository and target branch.
- Exact base commit SHA.
- Working-tree status, including untracked files.
- Relevant governance and task documents.
- Existing files and directories that may be affected.

Do not assume a clean workspace without checking it.

## 3. File Discipline

- Add a file only when it has a clear project purpose and owner-approved location.
- Modify the smallest coherent set of existing files.
- Delete or move files only with explicit scope and justification.
- Do not create duplicate documents that compete as sources of truth.
- Do not leave temporary scripts, logs, caches, archives, or generated outputs in the repository unless explicitly part of the deliverable.
- Do not use broad staging commands such as `git add .` or `git add -A` when precise staging is required.

## 4. Change Ledger

For every task, derive the ledger from actual Git output:
- Added files.
- Modified files.
- Deleted files.
- Renamed/moved files.
- Untracked files.

For each entry, state why it changed and which requirement or evidence supports it. Do not reconstruct a ledger from memory or from an intended plan.

## 5. Diff Review

Review:
- Complete diff, not only the summary.
- Whitespace and accidental formatting changes.
- Links and references.
- Duplicate or contradictory policy statements.
- Secrets and sensitive data.
- Scope creep and unrelated changes.
- New files omitted from the review.

Run `git diff --check` where a Git workspace is available. Record if it was not run.

## 6. Verification and Cleanliness

Run only checks appropriate to the approved scope. Record exact commands and outcomes. After work, inspect status and diff again. Do not claim the workspace is clean unless verified. Do not claim tests passed unless executed against the stated commit and environment.
