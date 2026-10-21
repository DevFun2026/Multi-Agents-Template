# Plan: Final cross-review fixes from the claude review

- Status: Approved (2026-10-21)
- Date: 2026-10-21
- Spec: [../specs/2026-10-21-cross-review-final-fixes-spec.md](../specs/2026-10-21-cross-review-final-fixes-spec.md)
- Design: [../designs/2026-10-21-cross-review-final-fixes-design.md](../designs/2026-10-21-cross-review-final-fixes-design.md)
- ADRs: none new; update note on ADR 0006

**Goal:** Exact-match cleanup on a canonical path, anchored context links, and the ADR, skill and glossary in agreement.

## Objective and success criteria

| Spec item | Task |
|---|---|
| R1, R2 | T2 |
| R3 | T1 |
| R4, R5 | T3 |
| Goal 4 (commit the report) | T3 |

## Scope and non-goals

As in the spec.

## Architecture decision

No new decision; see the design. ADRs: none new.

## Execution graph

```text
T0 branch; Status after the user's Approval -> T1 validator (TDD) -> T2 skill -> T3 ADR note, glossary, report -> T4 verify + PR
```

The **Controller** does all tasks serially.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch `fix/cross-review-final`; set Status lines after the user's **Approval** | `git log -1` |
| T1 | `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | Rejected: `context map links only CONTEXT.md.bak`, `context map links only NOTCONTEXT.md` (both "must link at least one CONTEXT.md"). Accepted: `context map reference link with fragment`. Red, then green. |
| T2 | `.agents/skills/cross-review/SKILL.md` | `mktemp -d -u "$(cd "${TMPDIR:-/tmp}" && pwd -P)/cross-review.XXXXXX"` prints no `//`. `grep -n 'pwd -P'` and `grep -n 'byte-identical'` each find the new text. |
| T3 | `docs/adr/0006-cross-harness-review.md`, `CONTEXT.md`, the `claude` report | `verify-template.sh` passes |
| T4 | none | PR CI `verify` passes |

## Verification

- `bash scripts/verify-template.sh`
- The T2 checks.
- PR CI.

## Risks and open questions

- The cleanup steps are proven fully only by the next real Path B run.
- Open questions: none.
