# Plan: cross-review temporary-copy cleanup and CONTEXT-MAP reference links

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-cross-review-cleanup-spec.md](../specs/2026-10-20-cross-review-cleanup-spec.md)
- Design: [../designs/2026-10-20-cross-review-cleanup-design.md](../designs/2026-10-20-cross-review-cleanup-design.md)
- ADRs: none

**Goal:** Path B cleanup that no safety check has to block, every `CONTEXT-MAP.md` link checked, and the Codex report committed.

## Objective and success criteria

Spec goals 1–3 and acceptance criteria.

## Scope and non-goals

- **Scope:** the skill's step 5, the validator, mutation tests, the Codex report.
- **Non-goals:** sandboxing, other link forms, Codex findings 1 and 3.

## Architecture decision

Cleanup is a separate command on a literal, checked path. The validator parses reference-style links. See the design. ADRs: none.

## Execution graph

```text
T0 branch + approve -> T1 validator (TDD) -> T2 skill step 5 -> T3 commit report + verify -> T4 PR
```

The controller does all tasks serially.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch `fix/cross-review-cleanup`; Status lines of these artifacts | `git log -1` |
| T1 | `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | `context map reference link to a missing CONTEXT.md` is rejected with "missing or unsafe"; `CONTEXT-MAP.md with only a reference-style link` is accepted; red before the change, green after |
| T2 | `.agents/skills/cross-review/SKILL.md` | `grep -nE 'trap|rm -rf "\$' .agents/skills/cross-review/SKILL.md` returns nothing; `verify-template.sh` passes |
| T3 | `docs/reviews/2026-10-20-130949-cross-review-fixes-cross-review.md` | the validator passes |
| T4 | none | PR CI `verify` passes |

## Verification

- `bash scripts/verify-template.sh`
- The `grep` check in T2.
- PR CI.

## Risks and open questions

- The new cleanup steps are proven only by the next real Path B run.
- Open questions: none.
