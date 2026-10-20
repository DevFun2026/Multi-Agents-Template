# Plan: cross-review asks which plan to review when several share the newest date

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-cross-review-plan-choice-spec.md](../specs/2026-10-20-cross-review-plan-choice-spec.md)
- Design: [../designs/2026-10-20-cross-review-plan-choice-design.md](../designs/2026-10-20-cross-review-plan-choice-design.md)
- ADRs: none

**Goal:** `cross-review` never guesses between plans that share the newest date. It asks the user.

## Objective and success criteria

Spec goals 1–2 and acceptance criteria.

## Scope and non-goals

- Scope: the "Plan" bullet in step 2 of `.agents/skills/cross-review/SKILL.md`.
- Non-goals: plan naming, automatic choice, any other skill behaviour.

## Architecture decision

Ask the user when plans tie, listing the candidates with uncommitted ones first (design). ADRs: none.

## Execution graph

```text
T0 branch + approve -> T1 edit skill (controller, write) -> T2 verify + manual checks -> T3 PR on request
```

All tasks run serially. The controller does them; one paragraph does not justify a worker.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch `fix/cross-review-plan-choice`; Status lines of these three artifacts | `git log -1` |
| T1 | `.agents/skills/cross-review/SKILL.md` (step 2, "Plan" bullet only) | `git diff` touches only that bullet |
| T2 | none | `bash scripts/verify-template.sh` passes; the user runs the two manual checks from the spec |
| T3 | none | PR CI `verify` passes; the user merges |

### T1 detail

Replace the "Plan" bullet with the three-step rule from the design:

1. Use the plan argument if one is given.
2. Otherwise, if exactly one plan has the newest date prefix, use it.
3. Otherwise list the tied plans and ask.
   - Show each plan's path and `Status:` line, and mark plans with uncommitted changes (`git status --porcelain -- <path>`).
   - Order: uncommitted first, then by last commit (`git log -1 --format=%ct -- <path>`), newest first.
   - Do not continue until the user answers.

## Verification

- `bash scripts/verify-template.sh`
- Manual:
  - `/cross-review agy` lists the three 2026-10-20 plans and asks;
  - `/cross-review agy docs/plans/2026-10-20-security-audit-skill.md` goes straight to the prompt.

## Risks and open questions

- The skill text is checked manually only.
- Open questions: none.
