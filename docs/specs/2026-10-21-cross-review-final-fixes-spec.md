# Spec: Final cross-review fixes from the claude review

- Status: Approved (2026-10-21)
- Date: 2026-10-21
- Design: [../designs/2026-10-21-cross-review-final-fixes-design.md](../designs/2026-10-21-cross-review-final-fixes-design.md)
- ADRs: none new; an update note on [ADR 0006](../adr/0006-cross-harness-review.md)
- Plan: [../plans/2026-10-21-cross-review-final-fixes.md](../plans/2026-10-21-cross-review-final-fixes.md)

## Problem

The first Path B run with `claude` as the reviewer ([report](../reviews/2026-10-21-092114-cross-review-cleanup-cross-review.md)) confirmed five issues.

- **#2 Cleanup path check.** `mktemp -d "${TMPDIR:-/tmp}/cross-review.XXXXXX"` prints `/var/folders/.../T//cross-review.XXXXXX` on macOS. The path has `//`, and `/var` is a symlink to `/private/var`. A "starts with the temp directory" test on that string is fragile.
- **#3 Reference-link regex.** The regex for reference-style links in `CONTEXT-MAP.md` is not anchored. `./ctx/CONTEXT.md.bak` and `./ctx/NOTCONTEXT.md` are read as `CONTEXT.md` links.
- **#4 ADR 0006 wording.** ADR 0006 says the skill "deletes the copy", but cleanup is now best-effort with a fallback to reporting the path.
- **#7 Silent leftovers.** The copy can be left silently if the session ends early. There is also no rule for a failing `mktemp`.
- **#13 Missing glossary terms.** **Path B** and **Temporary copy** are used everywhere but missing from `CONTEXT.md`.

The report itself is uncommitted.

## Goals and success criteria

1. Cleanup deletes exactly the directory that `mktemp` created in this run, or nothing.
2. Only links whose last path segment is exactly `CONTEXT.md` count as context links.
3. ADR 0006, the skill and the glossary agree.
4. The `claude` report is committed.

## Scope

- `.agents/skills/cross-review/SKILL.md`
- `scripts/validate_template.py`
- `scripts/test-validator-mutations.py`
- `docs/adr/0006-cross-harness-review.md` (update note only)
- `CONTEXT.md`
- `docs/reviews/2026-10-21-092114-cross-review-cleanup-cross-review.md`

## Non-goals

The report's other findings, with reasons:

- #1 and #6: they concern the wording of an approved plan's checks; the shipped skill is correct.
- #5: post-approval false positive.
- #8–#12 and #14: cosmetic, or already recorded in PR #11.

## Requirements

| ID | Requirement |
|---|---|
| R1 | Path B creates the copy with `mktemp -d "$(cd "${TMPDIR:-/tmp}" && pwd -P)/cross-review.XXXXXX"`, which gives a canonical physical path with no `//`. The skill tells the user that path right away. |
| R2 | Cleanup runs only if the path is byte-identical to the one `mktemp` printed in this run, is absolute, contains no `..` segment and no `'`, and has a last component matching `cross-review.[A-Za-z0-9]{6}`. The **Controller** makes this comparison against the recorded output. If `mktemp` failed, there is nothing to clean. |
| R3 | Inline and reference-style `CONTEXT-MAP.md` links count only when the path's last segment is exactly `CONTEXT.md`. An optional `#fragment` is stripped. |
| R4 | ADR 0006 gets an update note: cleanup is a separate, best-effort step on a literal path, and if it is blocked the path is reported. The decision itself is unchanged. |
| R5 | `CONTEXT.md` defines **Path B** and **Temporary copy**. |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes.
- New rejected mutation cases:
  - a map whose only link is `./docs/ctx/CONTEXT.md.bak`, with a valid `docs/ctx/CONTEXT.md` present;
  - a map whose only link is `./docs/ctx/NOTCONTEXT.md`.

  Both fail with "must link at least one CONTEXT.md".
- New accepted case: a reference link with a fragment, `[c]: ./docs/ctx/CONTEXT.md#language`.
- The `claude` report is committed.

## Open questions

None.
