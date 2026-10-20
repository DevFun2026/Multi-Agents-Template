# Plan: Fixes from the first agy cross-review

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-cross-review-fixes-spec.md](../specs/2026-10-20-cross-review-fixes-spec.md)
- Design: [../designs/2026-10-20-cross-review-fixes-design.md](../designs/2026-10-20-cross-review-fixes-design.md)
- ADRs: none

**Goal:** Path B works with `agy`, and the five other confirmed review findings are fixed.

## Objective and success criteria

Spec goals 1–2 and acceptance criteria.

## Scope and non-goals

- **Scope:** `cross-review` skill, validator, mutation tests, `CONTEXT.md`.
- **Non-goals:** dated records, a full reviewer sandbox, findings #1, #5, #7, #10, #11 and #12.

## Architecture decision

Code catches up with ADRs 0005 and 0006 (design). ADRs: none.

## Execution graph

```text
T0 branch + approve -> T1 validator (TDD) -> T2 skill + CONTEXT.md -> T3 verify + Path B smoke run (with user go-ahead) -> T4 PR
```

The controller does everything serially; the change is small.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch `fix/cross-review-findings`; Status lines of these three artifacts | `git log -1` |
| T1 | `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | new cases red, then green |
| T2 | `.agents/skills/cross-review/SKILL.md`, `CONTEXT.md` | `verify-template.sh` |
| T3 | none (`docs/reviews/` output only) | Path B `agy` run returns a review; `git status` shows only the report |
| T4 | none | PR CI passes |

### T1 detail (TDD)

1. Add the rejected cases, each with its expected message:
   - `CONTEXT.md and map both missing` → `CONTEXT.md or CONTEXT-MAP.md is required`
   - `context map links a missing CONTEXT.md` → `linked context file is missing`
   - `map-linked CONTEXT.md without Language` → `## Language`
   - `review name without cross-review suffix` (`docs/reviews/2026-10-20-120000-notes.md`) → `file name must match`
2. Add the accepted case `CONTEXT-MAP.md-only repository`: delete root `CONTEXT.md`, then write `CONTEXT-MAP.md` linking `./docs/ctx/CONTEXT.md` and a `docs/ctx/CONTEXT.md` that contains `## Language`.
3. Run `python3 scripts/test-validator-mutations.py`. Expected: FAIL.
4. Implement R3 and R4 per the design.
5. Run it again. Expected: all `[ok]`.
6. Commit.

### T2 detail

- **Skill step 5:**
  - add `git -C "$tmp_dir" init -q` after `mktemp`;
  - change the `agy` row to `agy --mode plan --sandbox -p "$(cat "$prompt_file")"`;
  - add a note that flags go before `-p`.
- **Skill step 6:** rename the last section to `## Suggested next actions`.
- **`CONTEXT.md`:** add **Delegation** under Roles.
- Run `bash scripts/verify-template.sh`, then commit.

### T3 detail

Ask the user before running, because Path B sends data to Google. Run `/cross-review agy docs/plans/2026-10-20-cross-review-fixes.md` Path B, following the updated skill. If `--sandbox` blocks file reads, drop it, record why in the skill, and re-run once.

## Verification

- `bash scripts/verify-template.sh`
- Path B smoke run with `git status` clean except for the new report.
- PR CI `verify` passes.

## Risks and open questions

- `agy --sandbox` behaviour in headless mode is unverified; T3 checks it.
- Open questions: none.
