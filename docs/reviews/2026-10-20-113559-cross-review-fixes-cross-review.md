# Cross-review: cross-review-fixes

- Generated: 2026-10-20T11:37:00+07:00
- Reviewer: agy (read-only cross-review)
- Path: B (CLI run in a temporary copy)
- Plan: docs/plans/2026-10-20-cross-review-fixes.md
- Artifacts reviewed:
  - Plan: docs/plans/2026-10-20-cross-review-fixes.md
  - Spec: docs/specs/2026-10-20-cross-review-fixes-spec.md
  - Design: docs/designs/2026-10-20-cross-review-fixes-design.md
  - ADRs: none
  - Domain glossary: CONTEXT.md

## Findings

### 1. Premature implementation of R5 in `CONTEXT.md` prior to plan approval
- **Severity**: blocker
- **Type**: correctness
- **File and section**: `CONTEXT.md`, section `## Language -> ### Roles`; `docs/plans/2026-10-20-cross-review-fixes.md`, section `## Tasks -> T2 detail`
- **Detail**: The planning gate rule requires that nothing is implemented outside the planning artifact set before explicit user approval ("no write outside the PHASE 1 artifact set and no implementer spawn happens before Approval"). `CONTEXT.md` lines 25–27 already contain the verbatim definition of **Delegation** that Spec R5 mandates and Plan T2 detail specifies to add. This constitutes an unapproved premature code modification. Furthermore, if Task T2 is executed as written ("add Delegation under Roles"), it will produce duplicate definitions of **Delegation** in `CONTEXT.md`.
- **Change to make**: Revert the unapproved edits to `CONTEXT.md` so the repository state remains untouched until approval, or if pre-existing, update Spec R5, Design R5, and Plan T2 to acknowledge the existing state and verify rather than append.

### 2. Artifact status stamped as "Approved" ahead of user gate
- **Severity**: blocker
- **Type**: drift
- **File and section**: `docs/specs/2026-10-20-cross-review-fixes-spec.md`, header; `docs/designs/2026-10-20-cross-review-fixes-design.md`, header; `docs/plans/2026-10-20-cross-review-fixes.md`, header and section `## Execution graph` / `## Tasks -> T0`
- **Detail**: All three artifacts record `- Status: Approved (2026-10-20)`. In `CONTEXT.md`, **Approval** is strictly defined as an explicit user message sent after reviewing the plan summary and paths without conditions. Stamping the artifacts as approved while they are still in cross-review violates the planning gate. Moreover, the execution graph and Task T0 list `approve` as an internal controller action (`T0 branch + approve -> T1...`), conflating an external user decision gate with a task step.
- **Change to make**: Change `- Status: Approved (2026-10-20)` to `Status: Draft` (or `Pending approval`) in all three documents. Remove `approve` from T0 and the execution graph, stating explicitly that implementation begins only after the user's unconditional approval.

### 3. Vacuous validation pass in R3 when `CONTEXT-MAP.md` contains no `CONTEXT.md` links
- **Severity**: major
- **Type**: edge-case
- **File and section**: `docs/designs/2026-10-20-cross-review-fixes-design.md`, section `## Overview` (R3); `docs/specs/2026-10-20-cross-review-fixes-spec.md`, section `## Requirements` (R3)
- **Detail**: The design states: "if root `CONTEXT-MAP.md` exists, every relative `*.md` link in it whose name is `CONTEXT.md` must exist, must not be a symlink, must stay inside the repository, and must contain `## Language`." If a repository contains an empty `CONTEXT-MAP.md` or links markdown files not named `CONTEXT.md`, the condition is vacuously true. The validator would accept a repository with zero context definitions and no `## Language` section, directly violating R3's requirement that the validator enforce `## Language` in repository context files.
- **Change to make**: Update the design and validator specification to require that if `CONTEXT-MAP.md` is present, it must contain at least one valid relative link to a `CONTEXT.md` file. Add a mutation test case in Plan T1 for `CONTEXT-MAP.md with zero CONTEXT.md links`.

### 4. Permissive plan contingency silently drops Spec Requirement R1
- **Severity**: major
- **Type**: drift
- **File and section**: `docs/plans/2026-10-20-cross-review-fixes.md`, section `## Tasks -> T3 detail` and `## Risks and open questions`; `docs/specs/2026-10-20-cross-review-fixes-spec.md`, section `## Requirements` (R1)
- **Detail**: Spec R1 requires `agy --mode plan --sandbox -p "<prompt>"` to remediate Problem #3 ("the agy reviewer runs with no terminal restriction beyond its headless defaults"). However, Plan T3 states: "If `--sandbox` blocks file reads, drop it, record why in the skill, and re-run once." Allowing an automated or unilateral removal of `--sandbox` during verification leaves Problem #3 unaddressed and breaks Spec R1 without a formal spec revision or re-approval.
- **Change to make**: Reconcile Spec R1 and Plan T3. If `--sandbox` behavior in headless mode is unknown and risky, run an isolated spike or define explicit fallback criteria in Spec R1 (and ADR justification) rather than allowing verification to quietly discard a spec requirement.

### 5. Subshell working directory expansion breaks relative `$prompt_file` paths
- **Severity**: major
- **Type**: correctness
- **File and section**: `docs/designs/2026-10-20-cross-review-fixes-design.md`, section `## Overview` (R1); `docs/plans/2026-10-20-cross-review-fixes.md`, section `## Tasks -> T2 detail`
- **Detail**: The proposed command is `(cd "$tmp_dir" && agy --mode plan --sandbox -p "$(cat "$prompt_file")")`. Because command substitution occurs within the subshell after `cd "$tmp_dir"` executes, any relative path supplied in `$prompt_file` will be evaluated relative to `$tmp_dir` rather than the caller's working directory, causing `cat` to fail with `No such file or directory`.
- **Change to make**: Specify that `$prompt_file` must be resolved to an absolute path before running the subshell, or expand the prompt into a shell variable before changing directories: `prompt_content="$(cat "$prompt_file")" && (cd "$tmp_dir" && agy --mode plan --sandbox -p "$prompt_content")`.

### 6. Missing mutation tests in Plan T1 for symlinks, path traversal, and dual-file states
- **Severity**: major
- **Type**: traceability
- **File and section**: `docs/plans/2026-10-20-cross-review-fixes.md`, section `## Tasks -> T1 detail`; `docs/designs/2026-10-20-cross-review-fixes-design.md`, section `## Overview` (R3)
- **Detail**: Design R3 introduces explicit security constraints for `CONTEXT-MAP.md` links ("must not be a symlink, must stay inside the repository"). However, Plan T1 details only 4 rejection cases (both missing, missing file, missing Language header, bad review suffix). It omits test cases for symlinks, path traversal (`../outside/CONTEXT.md`), and the edge case where both `CONTEXT.md` and `CONTEXT-MAP.md` exist.
- **Change to make**: Expand Plan T1 detail to include rejected mutation test cases verifying that symlinked context files and directory traversal attempts outside the repository are rejected, and define the expected validator behavior when both root files are present.

### 7. Unverified premise that `git init -q` satisfies harness repository checks
- **Severity**: minor
- **Type**: assumption
- **File and section**: `docs/specs/2026-10-20-cross-review-fixes-spec.md`, section `## Problem` (#2) and `## Requirements` (R2); `docs/designs/2026-10-20-cross-review-fixes-design.md`, section `## Overview` (R2)
- **Detail**: Spec Problem #2 acknowledges that whether `claude -p` requires a git repository in the temporary copy is "unverified". Running `git init -q` creates an empty repository without commits, an initial branch HEAD, or staged files. If a harness executes `git rev-parse HEAD`, `git log`, or `git diff HEAD`, it will still fail.
- **Change to make**: Clarify in Design Risks that if harnesses perform git inspection beyond checking for the existence of `.git/`, an initial dummy commit (`git commit --allow-empty -m "init"`) or staging copied files may be necessary.

### 8. Structural misplacement of "Delegation" and informal terminology
- **Severity**: minor
- **Type**: terminology
- **File and section**: `docs/specs/2026-10-20-cross-review-fixes-spec.md`, section `## Requirements` (R5); `docs/designs/2026-10-20-cross-review-fixes-design.md`, section `## Overview` (R5); `docs/plans/2026-10-20-cross-review-fixes.md`, sections `## Execution graph` and `## Tasks`
- **Detail**: In `CONTEXT.md`, **Role** is defined as "A named Worker definition with fixed tools and a cost tier...". Requirement R5 places **Delegation** (a communication mechanism/action) under `### Roles`. Furthermore, the artifacts frequently use the informal phrase "smoke run" (Design line 36; Plan line 27, 39, 66) which is not defined in `CONTEXT.md`.
- **Change to make**: Position **Delegation** under a more appropriate section in `CONTEXT.md` (e.g. `### Roles & Delegation` or `### Planning`). Replace informal terms like "smoke run" with "verification run" or add them to the glossary.

### 9. Hidden and non-markdown file handling omitted in `docs/reviews/` validation
- **Severity**: minor
- **Type**: edge-case
- **File and section**: `docs/designs/2026-10-20-cross-review-fixes-design.md`, section `## Overview` (R4); `docs/plans/2026-10-20-cross-review-fixes.md`, section `## Tasks -> T1 detail`
- **Detail**: Design R4 mandates that files in `docs/reviews/` strictly match `^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9-]+-cross-review\.md$`. If standard repository maintenance files (such as `.gitkeep`) or OS metadata files (such as `.DS_Store`) exist in `docs/reviews/`, a naive directory listing check will fail the entire repository validation.
- **Change to make**: Specify in the design and plan that the validator ignores dotfiles and non-markdown entries when enforcing naming patterns in `docs/reviews/`.

## Suggested next actions

- Reconcile `CONTEXT.md` by reverting the premature addition of **Delegation** (or adjusting R5/T2 to reflect existing state), and update the headers of `docs/specs/2026-10-20-cross-review-fixes-spec.md`, `docs/designs/2026-10-20-cross-review-fixes-design.md`, and `docs/plans/2026-10-20-cross-review-fixes.md` from `Approved` to `Draft`.
- Update `docs/designs/2026-10-20-cross-review-fixes-design.md` to prevent vacuous passes on empty `CONTEXT-MAP.md` files (require at least one context link), fix the `$prompt_file` subshell evaluation bug, and account for ignored hidden files in `docs/reviews/`.
- Amend `docs/plans/2026-10-20-cross-review-fixes.md` to add the missing mutation test cases in Task T1 (symlinks, path traversal, empty map) and align Task T3 with `docs/specs/2026-10-20-cross-review-fixes-spec.md` so that `--sandbox` is not dropped without explicit criteria.
