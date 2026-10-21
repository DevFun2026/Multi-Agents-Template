# Cross-review: cross-review-final-fixes

- Generated: 2026-10-21T10:25:00+07:00
- Reviewer: agy (read-only cross-review)
- Path: B (CLI run in a temporary copy)
- Plan: docs/plans/2026-10-21-cross-review-final-fixes.md
- Artifacts reviewed:
  - Plan: docs/plans/2026-10-21-cross-review-final-fixes.md
  - Spec: docs/specs/2026-10-21-cross-review-final-fixes-spec.md
  - Design: docs/designs/2026-10-21-cross-review-final-fixes-design.md
  - ADRs: none new (update note on ADR 0006)
  - Domain glossary: CONTEXT.md

## Findings

### 1. Validator regexes reject valid CommonMark links with titles
- **Severity:** major
- **Type:** correctness
- **File and section:** [2026-10-21-cross-review-final-fixes-design.md](../../docs/designs/2026-10-21-cross-review-final-fixes-design.md#L14), section "Overview" (R3)
- **Change to make:** The reference-link regex `^\s*\[[^\]]+\]:\s*<?((?:[^\s>#]*/)?CONTEXT\.md)(?:#[^\s>]*)?>?\s*$` strictly anchors the line end (`\s*$`) immediately after the URL or fragment. In standard Markdown (CommonMark §4.7), reference definitions may include optional link titles (e.g., `[c]: ./docs/ctx/CONTEXT.md#language "Glossary"` or `'title'` or `(title)`). Likewise, the inline regex `\]\(((?:[^)\s#]*/)?CONTEXT\.md)(?:#[^)\s]*)?\)` forbids trailing title strings before the closing parenthesis `\)`. If any reference or inline link uses a title, the validator will fail to count it and reject valid maps with "must link at least one CONTEXT.md". Update both regexes to allow optional whitespace and optional CommonMark title patterns (`(?:\s+["'(].*?["')])?`) before the closing delimiter/end-of-line.

### 2. Cleanup path lacks explicit shell quoting and regex anchoring
- **Severity:** major
- **Type:** security
- **File and section:** [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md#L50), section "Requirements" (R2) & [2026-10-21-cross-review-final-fixes-design.md](../../docs/designs/2026-10-21-cross-review-final-fixes-design.md#L13), section "Overview" (R2)
- **Change to make:** R2 requires that the path contains "no `'`", intending for the Controller to wrap the target path in single quotes when invoking `rm -rf`. However, neither the spec nor the design provides the exact command template for step 5.7 or mandates single-quoting. If `$TMPDIR` contains whitespace (e.g. `/Users/First Last/tmp`), an unquoted or double-quoted command executed by the Controller could perform word splitting on a destructive command (`rm -rf`). In addition, the pattern `cross-review.[A-Za-z0-9]{6}` lacks `^`/`$` anchors and leaves `.` unescaped, allowing unintended directory matches. Update R2 in both files to specify the exact anchored regex `^cross-review\.[A-Za-z0-9]{6}$` and mandate the literal single-quoted deletion command: `rm -rf '<canonical-path>'`.

### 3. Missing functional verification for R2 cleanup safety checks
- **Severity:** major
- **Type:** traceability
- **File and section:** [2026-10-21-cross-review-final-fixes.md](../../docs/plans/2026-10-21-cross-review-final-fixes.md#L42-L44), section "Tasks" (T2) & "Verification"
- **Change to make:** While R1 is tested using dry-run `mktemp -d -u ...`, Task T2 tests R2 only via `grep -n 'byte-identical'` to check text presence in `SKILL.md`. The design reduces R2 to "diff review", and the plan explicitly notes that "cleanup steps are proven fully only by the next real Path B run." A core destructive safety mechanism should not be deferred to production without verification. Add an automated test step or validation test in T2 verifying that Step 5.7's validation logic properly rejects non-matching paths (relative paths, paths containing `..` or `'`, invalid suffix patterns, and empty output).

### 4. Subshell canonicalization failure modes and missing abort on failed `mktemp`
- **Severity:** major
- **Type:** edge-case
- **File and section:** [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md#L49-L50), section "Requirements" (R1, R2) & [2026-10-21-cross-review-final-fixes-design.md](../../docs/designs/2026-10-21-cross-review-final-fixes-design.md#L12-L13), section "Overview" (R1, R2)
- **Change to make:** In `$(cd "${TMPDIR:-/tmp}" && pwd -P)/cross-review.XXXXXX`: (1) if `$TMPDIR` is set to an inaccessible or nonexistent directory, `cd` fails and the subshell produces empty output, leaving `/cross-review.XXXXXX` in root `/`; (2) if `CDPATH` is set in the environment, `cd` prints the target directory to stdout, corrupting the path template. Furthermore, while R2 states "If `mktemp` failed, there is nothing to clean", neither spec nor design defines what Path B does if `mktemp` fails. Update Design R1 to neutralize `CDPATH` and handle directory errors (`(CDPATH= cd "${TMPDIR:-/tmp}" 2>/dev/null || cd /tmp) && pwd -P`). In Spec R1/R2 and Design R1/R2, explicitly state that if `mktemp` exits non-zero or produces empty output, the Controller must immediately halt Path B and report the error without proceeding to file copy.

### 5. Incomplete test coverage for inline link fragments
- **Severity:** minor
- **Type:** traceability
- **File and section:** [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md#L58-L64), section "Acceptance criteria" & [2026-10-21-cross-review-final-fixes.md](../../docs/plans/2026-10-21-cross-review-final-fixes.md#L41), section "Tasks" (T1)
- **Change to make:** Spec R3 mandates that both inline and reference-style links count when pointing to `CONTEXT.md` and strip optional `#fragment`. However, the acceptance criteria and Plan Task T1 only include a test case for a reference link with a fragment (`[c]: ./docs/ctx/CONTEXT.md#language`). Add a corresponding accepted test case for an inline link with a fragment (e.g. `[context](./docs/ctx/CONTEXT.md#language)`) to the spec acceptance criteria and Plan Task T1.

### 6. Target section drift in CONTEXT.md
- **Severity:** minor
- **Type:** drift
- **File and section:** [2026-10-21-cross-review-final-fixes-design.md](../../docs/designs/2026-10-21-cross-review-final-fixes-design.md#L16), section "Overview" (R5)
- **Change to make:** Design R5 states "Add `### Cross-review` terms to `CONTEXT.md`". In [CONTEXT.md](../../CONTEXT.md#L51-L88), terms are organized under `### Roles`, `### Planning`, and `### Skills`. **Cross-review**, **Path B**, and **Temporary copy** belong under `### Skills`. Update Design R5 and the Components table to specify adding the terms under `### Skills` instead of introducing an undeclared `### Cross-review` heading.

### 7. Non-standard Harness naming and informal terminology
- **Severity:** minor
- **Type:** terminology
- **File and section:** [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md#L11-L26), sections "Problem" & "Goals", and [2026-10-21-cross-review-final-fixes.md](../../docs/plans/2026-10-21-cross-review-final-fixes.md#L43), section "Tasks" (T3)
- **Change to make:** The artifacts refer to the reviewing Harness as `claude` (e.g., "The first Path B run with `claude` as the reviewer", "The `claude` report"). [CONTEXT.md](../../CONTEXT.md#L9-L11) defines the Harness as **Claude Code**. Use **Claude Code** when referring to the Harness or report entity (retaining `claude` only when referring to the CLI binary name). Additionally, replace informal references like "creates the copy" in Spec R1 with the defined term **Temporary copy**.

## Suggested next actions

- Update [2026-10-21-cross-review-final-fixes-design.md](../../docs/designs/2026-10-21-cross-review-final-fixes-design.md) and [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md) to support link titles in the R3 regexes, anchor the R2 regex (`^cross-review\.[A-Za-z0-9]{6}$`), mandate literal single-quoting (`rm -rf '<path>'`), make `mktemp` subshell directory resolution safe against `CDPATH`/invalid `TMPDIR`, and require an immediate abort if `mktemp` fails.
- Update [2026-10-21-cross-review-final-fixes.md](../../docs/plans/2026-10-21-cross-review-final-fixes.md) (Task T2) to include explicit automated test cases verifying that Step 5.7's validation logic rejects non-matching paths before running live cleanup.
- Update [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md) (Acceptance criteria) and [2026-10-21-cross-review-final-fixes.md](../../docs/plans/2026-10-21-cross-review-final-fixes.md) (Task T1) to add test coverage for inline links containing `#fragment`.
- Align [2026-10-21-cross-review-final-fixes-design.md](../../docs/designs/2026-10-21-cross-review-final-fixes-design.md) and [2026-10-21-cross-review-final-fixes-spec.md](../../docs/specs/2026-10-21-cross-review-final-fixes-spec.md) with [CONTEXT.md](../../CONTEXT.md) by targeting `### Skills` for glossary terms and standardizing references to **Claude Code** and **Temporary copy**.
