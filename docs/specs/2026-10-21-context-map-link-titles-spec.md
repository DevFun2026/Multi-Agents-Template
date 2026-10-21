# Spec: Accept link titles on CONTEXT.md links in CONTEXT-MAP.md

- Status: Approved (2026-10-21)
- Date: 2026-10-21
- Design: [../designs/2026-10-21-context-map-link-titles-design.md](../designs/2026-10-21-context-map-link-titles-design.md)
- ADRs: none (a parser detail inside ADR 0005)
- Plan: [../plans/2026-10-21-context-map-link-titles.md](../plans/2026-10-21-context-map-link-titles.md)

## Problem

Both reviewers in the 2026-10-21 Path B run reported the same gap: `agy` (finding 1) and `codex` (finding 2), in `docs/reviews/2026-10-21-10214*-cross-review-final-fixes-cross-review.md`. The validator's `CONTEXT-MAP.md` link patterns reject valid Markdown links that carry a title, such as `[c]: ./ctx/CONTEXT.md "Glossary"` or `[c](./ctx/CONTEXT.md 'Glossary')`. A map that uses titles fails with "must link at least one CONTEXT.md", even though its links are correct.

## Goals and success criteria

1. Inline and reference-style `CONTEXT.md` links are counted whether or not they have a title.
2. Every existing rule keeps working: the last segment must be exactly `CONTEXT.md`, the fragment is dropped, and paths must be safe.

## Scope

`scripts/validate_template.py` and `scripts/test-validator-mutations.py`.

## Non-goals

- Other Markdown link forms: autolinks, HTML, nested brackets.
- A full CommonMark parser.

## Requirements

| ID | Requirement |
|---|---|
| R1 | A title in any of the three link-title forms is accepted after the destination, separated by whitespace: `"…"`, `'…'` or `(…)`. This applies to inline links and to reference definitions. |
| R2 | An optional `<…>` around the destination is still accepted. |
| R3 | The last-segment rule, fragment stripping and path checks are unchanged. |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes.
- Accepted cases:
  - inline link with a double-quoted title and a fragment;
  - reference definition with a single-quoted title;
  - reference definition with a parenthesised title.
- Rejected case: a map whose only link is `[x](./docs/ctx/CONTEXT.md.bak "t")` fails with "must link at least one CONTEXT.md".

## Open questions

None.
