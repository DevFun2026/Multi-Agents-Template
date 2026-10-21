# Plan: Accept link titles on CONTEXT.md links in CONTEXT-MAP.md

- Status: Approved (2026-10-21)
- Date: 2026-10-21
- Spec: [../specs/2026-10-21-context-map-link-titles-spec.md](../specs/2026-10-21-context-map-link-titles-spec.md)
- Design: [../designs/2026-10-21-context-map-link-titles-design.md](../designs/2026-10-21-context-map-link-titles-design.md)
- ADRs: none

**Goal:** Count `CONTEXT.md` links in `CONTEXT-MAP.md` whether or not they carry a Markdown title.

## Objective and success criteria

| Spec item | Task |
|---|---|
| R1, R2, R3 | T1 |

## Scope and non-goals

As in the spec.

## Architecture decision

A shared optional title fragment on both regexes; see the design. ADRs: none.

## Execution graph

```text
T0 branch; Status lines after the user's Approval -> T1 tests then regexes (TDD) -> T2 verify + PR
```

The **Controller** does all tasks serially.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch `fix/context-map-link-titles`; Status lines | `git log -1` |
| T1 | `scripts/test-validator-mutations.py`, then `scripts/validate_template.py` | The accepted cases `context map inline link with title`, `context map reference link with single-quoted title` and `context map reference link with parenthesised title` fail before the change and pass after. The rejected case `context map links only CONTEXT.md.bak with title` is rejected with "must link at least one CONTEXT.md". |
| T2 | none | `bash scripts/verify-template.sh` passes; PR CI `verify` passes |

## Verification

- `bash scripts/verify-template.sh`
- PR CI.

## Risks and open questions

- Titles with escaped quotes are not matched (design, Risks).
- Open questions: none.
