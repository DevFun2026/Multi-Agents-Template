# Design: Final cross-review fixes from the claude review

- Status: Approved (2026-10-21)
- Date: 2026-10-21
- Spec: [../specs/2026-10-21-cross-review-final-fixes-spec.md](../specs/2026-10-21-cross-review-final-fixes-spec.md)
- ADRs: no new ADR. ADR 0006 keeps its decision: a temporary copy, explicit request, read-only reviewer. It gains an update note on how cleanup works (R4).

## Overview

| Req | Change |
|---|---|
| R1 | Skill step 5.1 uses `tmp_dir="$(mktemp -d "$(cd "${TMPDIR:-/tmp}" && pwd -P)/cross-review.XXXXXX")" && echo "$tmp_dir"`. `pwd -P` resolves `/var` to `/private/var` and drops the trailing `/`. The **Controller** tells the user the printed path straight away. Verified on macOS: the old form printed `.../T//cross-review.XXXXXX`. |
| R2 | Skill step 5.7 is rewritten as an exact-match rule (spec R2). It adds a line for when `mktemp` fails. The "tell the user the path" fallback stays. |
| R3 | The validator regexes are anchored to the last segment: inline `\]\(((?:[^)\s#]*/)?CONTEXT\.md)(?:#[^)\s]*)?\)`, reference `^\s*\[[^\]]+\]:\s*<?((?:[^\s>#]*/)?CONTEXT\.md)(?:#[^\s>]*)?>?\s*$` (multiline). |
| R4 | Append to ADR 0006, under Decision 3, an "Update (2026-10-21, after acceptance)" note. Same style as the ADR 0004 update. |
| R5 | Add `### Cross-review` terms to `CONTEXT.md`: **Path B** (running the reviewing **Harness**'s CLI on a **Temporary copy**, only on explicit request) and **Temporary copy** (a `cross-review.*` directory under the system temp directory, holding only the reviewed artifacts, a prompt and an empty git repository). |

## Components

| Component | Change |
|---|---|
| `.agents/skills/cross-review/SKILL.md` | R1, R2 |
| `scripts/validate_template.py` | R3 regexes |
| `scripts/test-validator-mutations.py` | 2 rejected and 1 accepted case (spec acceptance criteria) |
| `docs/adr/0006-cross-harness-review.md` | R4 note |
| `CONTEXT.md` | R5 |
| `docs/reviews/2026-10-21-092114-cross-review-cleanup-cross-review.md` | commit as returned. It has no secrets and no local paths; the temp path appeared only in the CLI summary, not in the file. |

## Alternatives considered

- **Keep the prefix test and normalise both sides.** It still needs a shell to compute the canonical path at deletion time, and that brings back variable-based `rm`.
- **Write a new ADR.** No decision changes; an update note is proportionate.

## Risks

- The `pwd -P` form must also work on Linux. It is POSIX `pwd -P` and `${TMPDIR:-/tmp}`.
- A stricter regex could stop counting an odd but valid link form. The validator then fails with "must link at least one CONTEXT.md", which is visible, not silent.

## Test strategy

- R3: the mutation and accepted cases.
- R1: `mktemp -d -u` with the new template shows no `//`, using dry-run mode so nothing is created.
- R2, R4, R5: diff review.
