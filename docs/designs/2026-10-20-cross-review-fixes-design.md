# Design: Fixes from the first agy cross-review

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-cross-review-fixes-spec.md](../specs/2026-10-20-cross-review-fixes-spec.md)
- ADRs: none. ADR 0006 already makes Path B read-only, in a temporary copy, and on explicit request. ADR 0005 already allows `CONTEXT-MAP.md`. These fixes make the code match those decisions.

## Overview

| Req | Change |
|---|---|
| R1 | Cross-review step 5 table: `(cd "$tmp_dir" && agy --mode plan --sandbox -p "$(cat "$prompt_file")")`. A note says `-p` takes the next token as the prompt, so it must come last. `--sandbox` is `agy`'s terminal sandbox. Headless `agy` already denies shell commands that need approval; this adds a second layer. |
| R2 | In step 5.1, after `mktemp -d`, add `git -C "$tmp_dir" init -q`. Codex keeps `--skip-git-repo-check`, which is now redundant but harmless. |
| R3 | Remove `CONTEXT.md` from `REQUIRED`. New check: if root `CONTEXT-MAP.md` exists, every relative `*.md` link in it whose name is `CONTEXT.md` must exist, must not be a symlink, must stay inside the repository, and must contain `## Language`. Otherwise root `CONTEXT.md` must exist with `## Language`. If neither exists, fail with `CONTEXT.md or CONTEXT-MAP.md is required`. `docs/templates/context.md` stays required. |
| R4 | The session-artifact name check uses a per-directory pattern. `docs/handoffs` keeps the current one. `docs/reviews` requires the `-cross-review.md` suffix. |
| R5 | Add **Delegation** under "Roles" in `CONTEXT.md`: "The **Controller** handing one bounded task to a **Worker** through a **Task packet**." with `_Avoid_: offloading, outsourcing`. |
| R6 | Report contract in the skill: `## Suggested next actions` replaces `## Handoff: suggested next actions`. |

## Components

| Component | Responsibility / change |
|---|---|
| `.agents/skills/cross-review/SKILL.md` | R1, R2, R6 |
| `scripts/validate_template.py` | R3, R4 |
| `scripts/test-validator-mutations.py` | Rejected cases: `CONTEXT.md` and map both missing; map linking a missing `CONTEXT.md`; map-linked `CONTEXT.md` without `## Language`; review name without the suffix. Accepted case: root `CONTEXT.md` replaced by a `CONTEXT-MAP.md` that links `docs/ctx/CONTEXT.md`. |
| `CONTEXT.md` | R5 |

## Alternatives considered

- **Pass the `agy` prompt with `-p='…'`.** This works, but quoting a multi-line prompt that way is fragile. Putting the flags first is simpler.
- **Leave `CONTEXT.md` required and document the map as an add-on.** This contradicts ADR 0005.
- **A per-reviewer `git init`.** One init for all reviewers is simpler and harmless.

## Risks

- `agy --sandbox` behaviour in headless mode is not fully documented. If it blocks file reads, the Path B smoke run shows it, and the fix is to drop the flag and record why.
- The `CONTEXT-MAP.md` link parsing is deliberately simple: Markdown `[..](path)` links ending in `CONTEXT.md`.

## Test strategy

- R3, R4: mutation and accepted cases, each asserting its own message.
- R1, R2: one Path B smoke run with `agy` on this plan, after the user agrees, then `git status`.
- R5, R6: diff review.
