# Spec: cross-review temporary-copy cleanup and CONTEXT-MAP reference links

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Design: [../designs/2026-10-20-cross-review-cleanup-design.md](../designs/2026-10-20-cross-review-cleanup-design.md)
- ADRs: none (refinements inside ADR 0005 and ADR 0006)
- Plan: [../plans/2026-10-20-cross-review-cleanup.md](../plans/2026-10-20-cross-review-cleanup.md)

## Problem

The first Path B run with Codex surfaced two gaps.

1. **Cleanup was blocked.** The `cross-review` skill cleans its temporary copy with `trap 'rm -rf "$tmp_dir"' EXIT` inside one shell script. Claude Code's safety check blocked that run before it started. It refuses an `rm -rf` on a shell variable inside a script it cannot analyse. A **Controller** following the skill cannot run Path B there unless it drops the cleanup step.
2. **Reference-style links are not checked.** The Codex report ([docs/reviews/2026-10-20-130949-cross-review-fixes-cross-review.md](../reviews/2026-10-20-130949-cross-review-fixes-cross-review.md), finding 2) notes that the validator reads only inline Markdown links in `CONTEXT-MAP.md`. A reference-style link (`[x]: ./ctx/CONTEXT.md`) next to an inline link is not checked.

That Codex report is still uncommitted.

## Goals and success criteria

1. Path B never needs `rm -rf` on a shell variable, and still never leaves repository data behind silently.
2. Every `CONTEXT.md` link in `CONTEXT-MAP.md`, inline or reference-style, is validated.
3. The Codex report is committed.

## Scope

- `.agents/skills/cross-review/SKILL.md`, step 5
- `scripts/validate_template.py`
- `scripts/test-validator-mutations.py`
- `docs/reviews/2026-10-20-130949-cross-review-fixes-cross-review.md`

## Non-goals

- Making the temporary copy a sandbox.
- Other Markdown link forms (autolinks, HTML).
- The Codex findings judged moot or wrong (1 and 3).

## Requirements

| ID | Requirement |
|---|---|
| R1 | Path B creates the copy with `mktemp -d "${TMPDIR:-/tmp}/cross-review.XXXXXX"` and records the absolute path it printed. The script that runs the reviewer contains no `rm`. |
| R2 | After the report is written, or after a failure, cleanup is a separate command, `rm -rf -- '<the literal absolute path>'`, run only if that path starts with the temp directory and its last component starts with `cross-review.`. If the harness blocks or asks and nobody approves, leave the copy and tell the user its path. |
| R3 | The validator reads `CONTEXT.md` links from both inline links (`[x](path)`) and reference definitions (`[x]: path`) in `CONTEXT-MAP.md`, and applies the existing checks to each. |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes.
- A new rejected mutation case: a map with a valid inline link plus a reference-style link to a missing `CONTEXT.md`, failing with "missing or unsafe".
- A new accepted case: a map that uses only a reference-style link to a valid `CONTEXT.md`.
- The skill's step 5 contains no `trap` and no `rm` on a variable.
- The Codex report is committed.

## Open questions

None.
