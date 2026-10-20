# Spec: cross-review asks which plan to review when several share the newest date

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Design: [../designs/2026-10-20-cross-review-plan-choice-design.md](../designs/2026-10-20-cross-review-plan-choice-design.md)
- ADRs: none
- Plan: [../plans/2026-10-20-cross-review-plan-choice.md](../plans/2026-10-20-cross-review-plan-choice.md)

## Problem

Without a plan argument, `cross-review` reviews "the newest file in `docs/plans/` by its date prefix". Plan names carry only a date (`YYYY-MM-DD-<topic>.md`), so several plans can tie.

On 2026-10-20 there were two: `security-audit-skill` and `project-skills-and-context`. The skill had no rule for that case, and the agent guessed: it picked the most recently committed plan. Guessing is wrong in the skill's main use case. A plan under review before **Approval** is usually uncommitted, so a commit-time rule would skip it, and the wrong artifacts would be sent to another model.

## Goals and success criteria

1. When more than one plan shares the newest date prefix and no plan argument is given, the skill asks the user which plan to review. It never guesses.
2. Behaviour is unchanged when exactly one plan has the newest date, or when the user passes a plan path.

## Scope

Step 2 ("Collect the artifacts") of `.agents/skills/cross-review/SKILL.md`.

## Non-goals

- Changing plan file names (for example, adding a time to them).
- Choosing automatically by `Status`, modification time or commit time.
- Any other `cross-review` behaviour.

## Requirements

| ID | Requirement |
|---|---|
| R1 | If no plan argument is given and two or more `docs/plans/*.md` files share the newest date prefix, the skill lists them and asks the user to choose. It does not collect artifacts or print a prompt until the user answers. |
| R2 | Each listed plan shows its path, its `Status` line, and whether it has uncommitted changes. Plans with uncommitted changes come first, then the rest in the order of their last commit, newest first. |
| R3 | With exactly one newest plan, or with a plan argument, the skill proceeds as before without asking. |

## Acceptance criteria

- With the three plans dated 2026-10-20 (the two already on `main` plus this task's plan), `/cross-review agy` lists all three with their Status and asks. It prints no prompt and runs no CLI.
- `/cross-review agy docs/plans/2026-10-20-security-audit-skill.md` proceeds to the prompt without asking.
- `bash scripts/verify-template.sh` passes.

## Open questions

None.
