# Design: cross-review temporary-copy cleanup and CONTEXT-MAP reference links

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-cross-review-cleanup-spec.md](../specs/2026-10-20-cross-review-cleanup-spec.md)
- ADRs: none. ADR 0006 sets the temporary-copy model; ADR 0005 sets `CONTEXT-MAP.md`. Nothing here changes either decision.

## Overview

**Skill, step 5 (R1, R2):**

1. Create the copy: `mktemp -d "${TMPDIR:-/tmp}/cross-review.XXXXXX"`. Note the absolute path it prints, for example `/var/folders/.../T/cross-review.Ab12Cd`.
2. Run `git init -q`, copy the artifacts, write the prompt and run the reviewer. Use that literal path, or a variable assigned once in the same command. Do not add a `trap` or any `rm`.
3. Save the report (step 6).
4. Cleanup is its own command, with the literal path, after checking that the path is under the temp directory and named `cross-review.*`:
   `rm -rf -- '/var/folders/.../T/cross-review.Ab12Cd'`
5. If the harness refuses or prompts and nobody approves, stop trying. Tell the user the path so they can delete it.

This keeps every deletion a single, fully resolved path that a person or a safety check can read. The copy holds only the listed artifacts, which are already committed or about to be reviewed, so leaving it briefly is low risk.

**Validator (R3):**

- Add a reference-definition pattern `^\s*\[[^\]]+\]:\s*<?([^\s>]*CONTEXT\.md)>?` (multiline) next to the inline pattern.
- Collect links from both patterns, de-duplicate them, and keep the order.
- Apply the existing checks to each link: safe relative path, not a symlink, inside the repository, contains `## Language`.

## Components

| Component | Change |
|---|---|
| `.agents/skills/cross-review/SKILL.md` | Step 5 sub-steps 1, 5 and 6 rewritten as above. The step 6 failure path also ends with the same cleanup rule. |
| `scripts/validate_template.py` | `CONTEXT_MAP_REF_LINK` pattern; links merged from both patterns. |
| `scripts/test-validator-mutations.py` | One rejected case, one accepted case (see the spec's acceptance criteria). |
| `docs/reviews/2026-10-20-130949-cross-review-fixes-cross-review.md` | Committed as returned. |

## Alternatives considered

- **Keep `trap … rm -rf` and ask the user to approve the prompt.** The check showed this cannot be approved inside an unanalysable script, and in an unattended session it fails outright.
- **Never clean up.** Copies would pile up in the temp directory, and the skill would quietly leave review material on disk.
- **Use a fixed project directory, such as `tmp/cross-review/`.** It is inside the repository (gitignored). The reviewer's working directory would then sit inside the repository tree, which ADR 0006 avoids.

## Risks

- A harness may still prompt before the separate `rm -rf`. The fallback is to tell the user the path.
- Reference definitions inside code blocks would also be parsed. That is acceptable: the result is a stricter check, not a looser one.

## Test strategy

- R3: the mutation and accepted cases.
- R1, R2: review the skill diff (no `trap`, no `rm` on a variable). The next real Path B run follows the new steps; no extra provider call is made just for this change.
