# Cross-review: cross-review-cleanup

- Generated: 2026-10-21T09:38:55+07:00
- Reviewer: claude (read-only cross-review)
- Path: B (CLI run in a temporary copy)
- Plan: docs/plans/2026-10-20-cross-review-cleanup.md
- Artifacts reviewed: docs/plans/2026-10-20-cross-review-cleanup.md, docs/specs/2026-10-20-cross-review-cleanup-spec.md, docs/designs/2026-10-20-cross-review-cleanup-design.md, CONTEXT.md; ADRs: none

## Findings

### Blocker

None.

### Major

1. **Major · correctness · plan, Tasks T2 and Verification (also spec, Acceptance criteria)**
   The T2 check `grep -nE 'trap|rm -rf "\$' .agents/skills/cross-review/SKILL.md` can fail when it should pass, and pass when it should fail.
   - **It fails on the intended text.** The design's step 5.2 tells the skill to say "Do not add a `trap` or any `rm`". If that sentence goes into SKILL.md, the grep matches `trap` and fails.
   - **It misses the forbidden pattern.** It does not match `rm -rf -- "$tmp_dir"`, which is the `--` form the design itself uses. It also misses `rm -fr`, `rm -r`, and an unquoted `rm -rf $x`.
   - **It checks the wrong scope.** It searches the whole file, but the acceptance criterion is about "step 5".

   **What to change:** Make the check say what is actually forbidden, for example `grep -nE "trap .*EXIT|rm +-[a-zA-Z]*r[a-zA-Z]* +(-- +)?[\"']?\\$"`, limited to the step 5/6 section. Or avoid the word "trap" in SKILL.md. Add a manual diff-review step to the plan, which the design's Test strategy already calls for.

2. **Major · correctness / edge-case · spec R2; design, Overview step 4**
   The safety check is "path starts with the temp directory" plus "last component starts with `cross-review.`". That is a string-prefix test on a path that may not be in canonical form:
   - On macOS, `$TMPDIR` is `/var/folders/.../T/`, and `/var` is a symlink to `/private/var`. This review copy itself shows up under both `/var/folders/...` and `/private/var/folders/...`. A prefix check against the other form fails, cleanup gets skipped, and copies pile up. That is the failure the design's "Never clean up" alternative rejects.
   - `$TMPDIR` ends with `/`, so `"${TMPDIR:-/tmp}/cross-review.XXXXXX"` gives a `//` in the path. String comparisons then become fragile.
   - A bare prefix test also accepts `/tmpfoo/...` and paths containing `..` segments.
   - The spec doesn't say who runs the check. If a shell runs it, it needs a variable, which brings back the pattern the change removes. If the **Controller** runs it, it is an unstated model judgment.

   **What to change:** Replace the prefix rule with an exact-match rule. The cleanup path must be byte-identical to the path `mktemp` printed in this run. It must be absolute, contain no `..`, and its last component must match `cross-review.[A-Za-z0-9]{6}`. State that the **Controller** does the comparison against the recorded output. Add a fallback for paths that cannot be single-quoted safely: if the path contains `'`, don't delete it; report it.

3. **Major · correctness / drift · plan, R3 regex in design Overview "Validator (R3)"**
   The pattern `^\s*\[[^\]]+\]:\s*<?([^\s>]*CONTEXT\.md)>?` has no end anchor.
   - **It can accept a link to a different file.** A definition like `[x]: ./ctx/CONTEXT.md.bak` or `./ctx/CONTEXT.mdx` captures `./ctx/CONTEXT.md`. The validator then checks a file the link does not point to, which defeats Goal 2.
   - **It matches the wrong filenames.** `[^\s>]*` also accepts `./ctx/NOTCONTEXT.md`.
   - **It skips some links without warning.** Angle-bracket destinations with spaces (`<./my ctx/CONTEXT.md>`) are ignored. So are lowercase `context.md` links, which resolve on case-insensitive macOS filesystems.

   **What to change:** Require a path-segment boundary before `CONTEXT.md`, and whitespace, `>`, `#` or end of line after it. Strip any `#fragment` before the checks. Pick and document one behaviour for case variants. Add a rejected mutation case for `CONTEXT.md.bak`.

4. **Major · traceability / assumption · spec header ("refinements inside ADR 0005 and ADR 0006"); design header; planning-gate rule 2**
   Both headers say nothing here changes ADR 0005 or ADR 0006, but neither ADR is in the artifact set, so the claim can't be checked. The change moves Path B from guaranteed cleanup (`trap … EXIT`) to best-effort cleanup that may leave the copy behind. If ADR 0006 records guaranteed removal of the temporary copy as part of its trust-boundary decision, this changes a security-boundary decision. Rule 2 would then require an ADR amendment or a superseding ADR.

   **What to change:** Quote the relevant decision lines from ADR 0006 (and 0005) in the design. Or include the ADRs in the review set. If ADR 0006 promises cleanup, add an ADR update to the plan.

5. **Major · drift / assumption · Status lines of all three artifacts; plan, Execution graph and T0**
   All three artifacts already say `Status: Approved (2026-10-20)`, but T0 says "branch + approve" and edits the Status lines. CONTEXT.md defines **Approval** as an explicit user message accepting *that plan version* without conditions. Approval is not a **Controller** task. A cross-review before approval means the set can't already be approved, and any revision from this review would need a fresh **Approval**.

   **What to change:**
   - Set Status to `Draft` / `In review` until the user's **Approval** message exists.
   - Remove "approve" from T0.
   - Record the approval date only after it happens.
   - If the set really was approved earlier, say this review is post-approval and that any revision resets **Approval**.

6. **Major · traceability · plan, Tasks and Verification**
   Nothing verifies the core of R1 and R2:
   - that `mktemp` output is recorded,
   - that the cleanup check exists,
   - that the step 6 failure path also ends with cleanup (design, Components),
   - that the "tell the user the path" fallback is present.

   T2 only checks for the absence of strings. The plan's "Objective" just points at the spec instead of mapping R1, R2 and R3 to tasks.

   **What to change:** Add a requirement-to-task/test table (R1→T2, R2→T2, R3→T1, Goal 3→T3). Give T2 positive checks: grep for `mktemp -d`, for the `rm -rf -- '` literal form, and for the fallback wording in both the success and failure paths. Include the skill-diff review the design names.

### Minor

7. **Minor · edge-case · spec, Goal 1 and R2; design, Overview steps 4–5**
   Goal 1 says copies are never left behind "silently". That doesn't hold in some cases:
   - The session can end, be interrupted, or lose the recorded path through context compaction between steps 1 and 4.
   - If `mktemp` itself fails, there is no path to clean, and the failure path doesn't say to skip cleanup.
   - Copies from earlier failed runs are never reported.

   **What to change:** Have step 1 tell the user the copy path straight away. Say that cleanup is skipped when `mktemp` fails. Optionally, have step 5 list any existing `${TMPDIR}/cross-review.*` directories and report them, without deleting them.

8. **Minor · traceability · design, Components (SKILL.md row) vs Overview**
   The table says "Step 5 sub-steps 1, 5 and 6 rewritten as above", but the Overview has sub-steps 1–5 and uses "step 6" for "Save the report". It's unclear which existing sub-steps change.

   **What to change:** Number the rewritten sub-steps to match SKILL.md and name the failure-path location exactly.

9. **Minor · traceability · spec R3; plan T1**
   R3 says "applies the existing checks to each" link, but the tests only cover a *missing* file reached through a reference link. Unsafe paths (`../`, absolute), symlinks, and a target without `## Language` are untested for reference definitions. "Red before the change" for the accepted case assumes the current validator rejects a map that has no inline links, and that premise isn't stated.

   **What to change:** Add at least one unsafe-path or symlink rejection case for a reference definition. State the current behaviour that makes the accepted case red today, or drop "red before" for that case.

10. **Minor · assumption · design, Risks ("code blocks … stricter, not looser")**
    Parsing reference definitions inside fenced code blocks can falsely reject a valid map that contains an example in a code block, such as template documentation. "Stricter" is not free.

    **What to change:** Either skip fenced and indented code blocks, or state that examples in `CONTEXT-MAP.md` must not use the reference syntax.

11. **Minor · security · design, Components ("Committed as returned"); plan T3**
    The Codex report is output from an external model. It may contain local absolute paths (temp-copy paths, usernames) or text taken from the prompt. Committing it "as returned" without review publishes that content. Also, T3's check ("the validator passes") doesn't show the validator looks at `docs/reviews/` at all.

    **What to change:** Add a T3 step to scan the report for secrets and local paths before committing. Name the check that actually covers `docs/reviews/`.

12. **Minor · assumption · spec, Non-goals ("Codex findings judged moot or wrong (1 and 3)")**
    No reason is recorded for setting aside findings 1 and 3, so a later review may raise them again.

    **What to change:** Add one line per finding to the spec giving the reason.

13. **Minor · terminology · all three artifacts vs CONTEXT.md**
    - "Path B", "temporary copy" / "the copy" and "safety check" are used throughout but not defined in CONTEXT.md.
    - "Codex report" is a synonym for a saved **Cross-review**.
    - "reviewer" here means an external **Harness**'s model, while CONTEXT.md uses reviewer for a **Role** (a **Worker**).
    - The plan says "the controller" instead of **Controller**.

    **What to change:** Add **Path B** and **Temporary copy** to CONTEXT.md (or link to where they are defined). Call the report "the Codex **Cross-review**". Say "the reviewing **Harness**" for Path B. Use the **Controller** term consistently.

14. **Minor · assumption · design, Overview closing paragraph**
    "The copy holds only the listed artifacts … low risk" leaves things out. The copy also holds the prompt, a `.git`, the reviewer's output, and anything the reviewing **Harness** wrote. Unapproved draft content can stay in the OS temp directory until the OS cleans it.

    **What to change:** List the full contents of the copy and keep the risk statement to that.

## Suggested next actions

- **Plan:** set Status back to pre-approval and remove "approve" from T0 (finding 5). Replace the T2 grep with a scoped positive and negative check that matches the design's own wording (finding 1). Add a requirement-to-task table and checks for R1/R2 (finding 6).
- **Spec R2 and design step 4:** replace the prefix check with an exact match against the recorded `mktemp` output, covering the `/var` vs `/private/var` and `//` cases (finding 2). Add the edge cases from finding 7.
- **Design validator regex and T1 tests:** anchor the `CONTEXT.md` match, handle fragments, and add the `CONTEXT.md.bak` and unsafe-path reference cases (findings 3, 9, 10).
- **Spec and design headers:** quote or attach ADR 0006/0005 to back up the "no ADR change" claim, or add an ADR update if guaranteed cleanup was part of ADR 0006 (finding 4). Then fix the smaller terminology and report-hygiene items (findings 11–14).
