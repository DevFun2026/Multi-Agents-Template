# Spec: Fixes from the first agy cross-review

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Design: [../designs/2026-10-20-cross-review-fixes-design.md](../designs/2026-10-20-cross-review-fixes-design.md)
- ADRs: none (refinements inside ADR 0005 and ADR 0006)
- Plan: [../plans/2026-10-20-cross-review-fixes.md](../plans/2026-10-20-cross-review-fixes.md)

## Problem

The first real **Cross-review**, `agy` on the project-skills artifact set ([report](../reviews/2026-10-20-110330-project-skills-and-context-cross-review.md)), confirmed six problems:

- **#2:** `agy -p --mode plan "<prompt>"` fails, because `-p` takes the next token as its prompt. This failed in the first Path B run. The report also says `claude -p` may need a git repository in the temporary copy; that is unverified.
- **#3:** the `agy` reviewer runs with no terminal restriction beyond its headless defaults.
- **#4:** the validator requires a root `CONTEXT.md`, but ADR 0005 also allows a repository with only a `CONTEXT-MAP.md`.
- **#6:** review file names are not required to end in `-cross-review.md`.
- **#8:** `CONTEXT.md` lacks the term **Delegation**, which the design listed.
- **#9:** cross-review reports use a "Handoff" heading, which clashes with the glossary term **Handoff**.

## Goals and success criteria

1. Path B with `agy` runs and returns a review.
2. Each of the six problems is fixed, and fixes 4 and 6 are covered by mutation tests.

## Scope

- `.agents/skills/cross-review/SKILL.md`
- `scripts/validate_template.py`
- `scripts/test-validator-mutations.py`
- `CONTEXT.md`

## Non-goals

- Re-reviewing or editing the dated records (old specs, designs, ADRs, plans, reports).
- A full sandbox for reviewers.
- The report findings judged invalid, already done or by design: #1, #5, #7, #10, #11, #12.

## Requirements

| ID | Requirement |
|---|---|
| R1 | The `agy` reviewer command is `agy --mode plan --sandbox -p "<prompt>"`. Every flag comes before `-p`. |
| R2 | Path B runs `git init -q` in the temporary copy before calling any reviewer, so harnesses that expect a repository work. |
| R3 | The validator accepts a root `CONTEXT.md`, or a root `CONTEXT-MAP.md` whose linked `CONTEXT.md` files all exist. It requires `## Language` in each `CONTEXT.md` it checks. It fails when neither root file exists. |
| R4 | Files in `docs/reviews/` must match `^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9-]+-cross-review\.md$`. Handoff names are unchanged. |
| R5 | `CONTEXT.md` defines **Delegation**. |
| R6 | The report contract's last section is `## Suggested next actions`. Existing reports keep their wording. |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes, with mutation cases for R3 and R4 that each fail for their own reason. There is also an accepted case for a `CONTEXT-MAP.md`-only repository.
- With the user's go-ahead, one Path B run of `agy` on this plan returns a review, and `git status` shows only the new report.

## Open questions

None.
