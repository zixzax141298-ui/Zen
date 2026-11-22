# Owner Report Standard

Every task report must be concise, evidence-based, and explicit about what did and did not happen.

## Required Sections

### 1. Task and Authorization

State the requested task, exact Owner-authorized scope, and exclusions.

### 2. Baseline

State repository, branch, exact commit SHA, and working-tree state. If unavailable, mark UNKNOWN.

### 3. Change Ledger

List actual added, modified, deleted, and renamed files based on Git output. If only a local patch package was prepared, say so and do not call it a repository change.

### 4. Rationale and Impact

For each material change, identify the source requirement/evidence and summarize architecture, security, and compatibility impact.

### 5. Verification

List exact commands, environment, exit codes, test totals, failures, and unexecuted checks. Distinguish local verification from remote CI. Never infer test success.

### 6. PR and Repository State

State actual branch, push, PR number/URL, review state, and merge state. Use `BLOCKED` with the exact error when an operation fails. Never invent links or claim a PR from a local file package.

### 7. Risks and Unknowns

List unresolved risks, assumptions, unknowns, and NOT_TESTED behavior.

### 8. Conclusion

Use an accurate state such as PREPARED, IMPLEMENTED, VERIFIED, PR_OPEN, MERGED, or BLOCKED. Do not use “complete” when required work remains.
