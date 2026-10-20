# Design: cross-review asks which plan to review when several share the newest date

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-cross-review-plan-choice-spec.md](../specs/2026-10-20-cross-review-plan-choice-spec.md)
- ADRs: none (a behaviour fix inside one skill; no architecture decision)

## Overview

The "Plan" bullet in step 2 of `cross-review` changes:

- **Before:** the second argument, otherwise the newest file in `docs/plans/` by its date prefix.
- **After:**
  1. If the user gave a plan argument, use it.
  2. Otherwise find the newest date prefix among `docs/plans/*.md`. If exactly one plan has it, use that plan.
  3. If several plans have it, list them and ask the user which one to review. Stop until they answer.

  Each listed plan shows:
  - its path;
  - its `Status:` line;
  - a mark when `git status --porcelain -- <path>` shows changes.

  Plans with uncommitted changes come first, then the rest in order of `git log -1 --format=%ct -- <path>`, newest first.

The order exists only to put the likely candidate first. The user always decides. Path validation (the allowlist in step 2) applies to the chosen plan as before.

## Components

| Component | Change |
|---|---|
| `.agents/skills/cross-review/SKILL.md` | Rewrite the "Plan" bullet of step 2 as above. Nothing else changes. |

## Alternatives considered

- **Pick the most recently committed plan.** This is what happened in practice. It is wrong when the plan under review is uncommitted, which is the skill's main use case.
- **Prefer plans whose `Status` is not Approved.** It is often right, but still a guess. The user chose to always ask.
- **Pick by latest modification.** A small edit to an old plan would win.
- **Put a time in plan file names.** This changes the PHASE 1 naming convention in `AGENTS.md` for a rare case.

## Risks

- One extra question when plans tie. This is acceptable: a wrong plan would send the wrong artifacts to another provider.
- A skill-text change cannot be tested by the validator. It is checked manually (see the test strategy).

## Test strategy

- R1, R2: with the three 2026-10-20 plans, `/cross-review agy` lists all three, with their Status lines, and asks. Nothing is printed or run.
- R3: `/cross-review agy docs/plans/2026-10-20-security-audit-skill.md` goes straight to the prompt.
- Regression: `bash scripts/verify-template.sh` passes, which includes the project-skill checks on `cross-review`.
