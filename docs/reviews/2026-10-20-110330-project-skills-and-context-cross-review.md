# Cross-review: project-skills-and-context

- Generated: 2026-10-20T11:12:00+07:00
- Reviewer: agy (read-only cross-review)
- Path: B (CLI run in a temporary copy)
- Plan: docs/plans/2026-10-20-project-skills-and-context.md
- Artifacts reviewed:
  - docs/plans/2026-10-20-project-skills-and-context.md
  - docs/specs/2026-10-20-project-skills-and-context-spec.md
  - docs/designs/2026-10-20-project-skills-and-context-design.md
  - docs/adr/0004-project-authored-skills.md
  - docs/adr/0005-context-md-domain-glossary.md
  - docs/adr/0006-cross-harness-review.md
  - CONTEXT.md

## Findings

### 1. Premature approval status violates planning-gate rules
- **Severity**: blocker
- **Type**: drift
- **File and section**:
  - `docs/specs/2026-10-20-project-skills-and-context-spec.md`, header (line 3)
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, header (line 3)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, header (line 3) & Task 0 (lines 87–92)
  - `docs/adr/0004-project-authored-skills.md`, header (line 3)
  - `docs/adr/0005-context-md-domain-glossary.md`, header (line 3)
  - `docs/adr/0006-cross-harness-review.md`, header (line 3)
- **Change to make**: The planning gate mandates that no implementation occurs before user approval, and `CONTEXT.md` defines **Approval** as an explicit user message accepting the plan without conditions. All six documents currently claim `Status: Approved (2026-10-20)` or `Status: Accepted` before user approval has been received. Furthermore, Plan Task 0 redundantly schedules setting them to `Approved`/`Accepted` during implementation. Change the status in all six artifacts to `Status: Proposed` or `Status: In Review`. In Task 0, retain the step updating them to `Approved`/`Accepted` only once approval is granted.

### 2. Path B execution fails in bare temporary copy and malforms agy CLI arguments
- **Severity**: blocker
- **Type**: correctness
- **File and section**:
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "cross-review flow" (step 5, lines 78–84)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, "Global Constraints" (lines 33–36)
- **Change to make**: Step 5 copies artifact files into `tmp_dir=$(mktemp -d)` and runs reviewer CLIs. While Codex is passed `--skip-git-repo-check`, Claude Code (`claude -p`) requires a valid git repository and will terminate with an error inside an uninitialized `mktemp -d` directory. Additionally, the invocation `(cd "$tmp_dir" && agy -p --mode plan "$prompt")` places `--mode plan` immediately after `-p`, causing `agy`'s print/prompt option `-p` to ingest `--mode` as its prompt argument. Update step 5 and the Global Constraints to initialize a temporary git repository (`git init -q`) in `$tmp_dir` so git-dependent harnesses execute cleanly, and correct the `agy` command argument order (e.g. `agy --mode plan -p "$prompt"`).

### 3. Unbounded tool execution and network access for agy in Path B
- **Severity**: major
- **Type**: security
- **File and section**:
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "Overview" (line 27), "cross-review flow" (step 5)
  - `docs/adr/0006-cross-harness-review.md`, "Context" (line 13) & "Decision" (line 22)
- **Change to make**: The design notes that `agy -p` auto-allows workspace writes and acknowledges that `--mode plan` is not a documented hard block. While isolating files in `tmp_dir` prevents write collisions with the host repository, `agy` provides tools like `run_command` and network access that `--mode plan` does not disable. Untrusted input or prompt injection in reviewed planning artifacts could trigger shell command execution or read sensitive files outside `tmp_dir` (e.g., `~/.ssh`, `~/.aws`). Unlike Claude (restricted via `--tools Read,Grep,Glob`) or Codex (sandboxed with `-s read-only`), `agy` has no tool restriction specified. Update ADR 0006 and `AGENTS.md` section 7 to explicitly document this trust boundary limitation, restrict `agy` tool access where supported, and warn users prior to executing Path B with `agy`.

### 4. Multi-context CONTEXT-MAP.md broken by validator requirements
- **Severity**: major
- **Type**: traceability
- **File and section**:
  - `docs/specs/2026-10-20-project-skills-and-context-spec.md`, R9 & R12 (lines 58, 61)
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "check_project_skills() in scripts/validate_template.py" (line 59)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Task 3 step 4 (line 144)
- **Change to make**: Spec R9, Design line 41, and ADR 0005 support multi-context repositories by allowing a root `CONTEXT-MAP.md` that points to per-context glossaries. However, Spec R12, Design line 59, and Plan Task 3 step 4 hardcode root `CONTEXT.md` as an unconditional requirement in `REQUIRED` inside `scripts/validate_template.py`. A multi-context repository utilizing `CONTEXT-MAP.md` without a root `CONTEXT.md` will fail validation. Update R12, the Design, and Plan Task 3 to specify that the validator accepts either a root `CONTEXT.md` or a root `CONTEXT-MAP.md` (mapping to valid context files), each containing a `## Language` heading.

### 5. Contradiction regarding agy explicit-only capability across artifacts
- **Severity**: major
- **Type**: drift
- **File and section**:
  - `docs/adr/0004-project-authored-skills.md`, Decision item 3 (lines 21–23)
  - `docs/specs/2026-10-20-project-skills-and-context-spec.md`, Non-goals (line 43)
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, Risks (line 98)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Non-goals (line 53), Task 4 (line 164), Risks (line 194)
- **Change to make**: ADR 0004 contains a post-acceptance update asserting: "a probe with `agy` 1.4.2 showed that `agy` honours `disable-model-invocation: true`... The gap is closed in practice". In contrast, the Spec (Non-goals), Design (Risks), Plan (Non-goals, Task 4, Risks), and even ADR 0004's own Consequences section (line 36) all state that `agy` has no documented explicit-only control and accept implicit invocation as a known gap. Reconcile this contradiction across all documents: either adjust the Spec, Design, and Plan to reflect the empirical probe findings (noting that vendor documentation remains uncommitted), or update ADR 0004 to remove the assertion that the gap is closed.

### 6. Review file naming convention unenforced by validator regex
- **Severity**: major
- **Type**: edge-case
- **File and section**:
  - `docs/specs/2026-10-20-project-skills-and-context-spec.md`, R8 (line 57)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Global Constraints (line 26) & Task 3 step 4 (line 147)
- **Change to make**: Spec R8 and Plan Global Constraints mandate that cross-review reports follow `docs/reviews/YYYY-MM-DD-HHMMSS-<topic>-cross-review.md`. However, Plan Task 3 step 4 applies a single regex across both session directories: `^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9-]+\.md$`. Under this check, invalid review filenames lacking `-cross-review.md` (e.g. `docs/reviews/2026-10-20-120000-notes.md`) pass validation. Update Task 3 step 4 and `scripts/validate_template.py` to validate `docs/reviews/` files specifically against `^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9]+-cross-review\.md$`, and add a mutation test case asserting failure when `-cross-review` is absent.

### 7. Relative markdown link resolution in cross-review artifact collection
- **Severity**: major
- **Type**: edge-case
- **File and section**:
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "cross-review flow" (step 1, line 65)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Task 2 (line 120)
- **Change to make**: Step 1 collects artifacts linked in the plan and states: "Accept only validated repository-relative paths under `docs/{specs,designs,adr,plans}/` or a `CONTEXT.md`/`CONTEXT-MAP.md`." In practice, markdown plans link related artifacts relative to the plan file itself (e.g. `[../specs/...](...)` or `[0004](../adr/...)`). A naive check against `docs/...` will reject all relative links as invalid and drop them. Specify in Design step 1 and the skill instructions that link targets must be resolved relative to the plan file's directory before validating that the canonical path resides within permitted repository directories.

### 8. Missing Delegation term in CONTEXT.md and glossary list drift
- **Severity**: minor
- **Type**: terminology
- **File and section**:
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, Component table (line 40)
  - `CONTEXT.md`, lines 7–28
- **Change to make**: Design line 40 explicitly specifies the required glossary terms for `CONTEXT.md`: "Terms: Controller, Worker, Harness, Delegation, Task packet...". However, `CONTEXT.md` omits `Delegation` and defines `Role` (which was omitted from the Design list). Add `Delegation` (with its definition and avoided synonyms) to `CONTEXT.md`, and align the Design component table to include both `Delegation` and `Role`.

### 9. Terminology collision using "Handoff" as section heading in review reports
- **Severity**: minor
- **Type**: terminology
- **File and section**:
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "cross-review flow" (step 6, line 85)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Review Focus 1 (line 40)
  - `CONTEXT.md`, lines 69–72
- **Change to make**: `CONTEXT.md` defines a **Handoff** specifically as a committed file in `docs/handoffs/` enabling a fresh session to continue work. Using `"Handoff — suggested next actions"` as a section title inside review reports creates an ambiguous synonym collision. Rename this section in Design step 6 and the review prompt template to `## Suggested next actions` or `## Review handoff: suggested next actions`.

### 10. Omission of Google AI / Gemini API keys from secret detection patterns
- **Severity**: minor
- **Type**: security
- **File and section**:
  - `docs/specs/2026-10-20-project-skills-and-context-spec.md`, R12 (line 61)
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "check_project_skills() in scripts/validate_template.py" (line 60)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, "Global Constraints" (lines 27–32)
- **Change to make**: The secret patterns in R12 and `scripts/validate_template.py` scan for AWS, GitHub, Slack, and OpenAI (`sk-...`) tokens, but omit Google AI / Gemini API keys (`AIzaSy[0-9A-Za-z_-]{33}`). Because `agy` (Antigravity CLI, successor to Gemini CLI) is one of the three primary template harnesses, add `AIzaSy[0-9A-Za-z_-]{33}` to `SECRET_PATTERNS` across the Spec, Design, Plan, and validator test suite.

### 11. Self-review collision in Plan Task 6 verification step
- **Severity**: minor
- **Type**: traceability
- **File and section**:
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Task 6 (lines 181–182)
- **Change to make**: Task 6 specifies: "only after asking the user, run `/cross-review codex` on this plan." Spec R8 and ADR 0006 mandate that `<reviewer>` must differ from the running harness. If Task 6 is executed from within Codex, `/cross-review codex` will be rejected by the skill's own precondition check. Update Task 6 to specify running `/cross-review <reviewer>` where `<reviewer>` is dynamically selected to differ from the executing harness.

### 12. Underspecified topic extraction for review filenames
- **Severity**: minor
- **Type**: edge-case
- **File and section**:
  - `docs/specs/2026-10-20-project-skills-and-context-spec.md`, R8 (line 57)
  - `docs/designs/2026-10-20-project-skills-and-context-design.md`, "cross-review flow" (step 6, line 85)
  - `docs/plans/2026-10-20-project-skills-and-context.md`, Task 2 (line 120)
- **Change to make**: While `handoff` explicitly details how its slug is generated and normalized from user text, `cross-review` leaves the derivation of `<topic>` in `YYYY-MM-DD-HHMMSS-<topic>-cross-review.md` unspecified. Specify in Design step 6 and Plan Task 2 that `<topic>` is derived by stripping date prefixes and `.md` from the resolved plan filename, sanitizing runs of non-alphanumeric characters to `-`, and defaulting to `plan` if unresolved.

## Handoff: suggested next actions

- **Reset document approval statuses and fix Path B execution**: Revert `Status: Approved` / `Status: Accepted` across `docs/specs/2026-10-20-project-skills-and-context-spec.md`, `docs/designs/2026-10-20-project-skills-and-context-design.md`, `docs/plans/2026-10-20-project-skills-and-context.md`, and ADRs 0004–0006 to `Status: Proposed` or `Status: In Review` until actual user approval; update `tmp_dir` setup with `git init` and fix `agy` flag argument order in `docs/designs/2026-10-20-project-skills-and-context-design.md` and `docs/plans/2026-10-20-project-skills-and-context.md`.
- **Align agy trust boundary and explicit-only behavior**: Document the lack of execution sandboxing for `agy` in `docs/adr/0006-cross-harness-review.md` and `docs/designs/2026-10-20-project-skills-and-context-design.md`, and resolve the contradiction between ADR 0004's probe update and the open gap stated in `docs/specs/2026-10-20-project-skills-and-context-spec.md` and `docs/plans/2026-10-20-project-skills-and-context.md`.
- **Fix validator rules and link resolution**: In `docs/specs/2026-10-20-project-skills-and-context-spec.md`, `docs/designs/2026-10-20-project-skills-and-context-design.md`, and `docs/plans/2026-10-20-project-skills-and-context.md`, allow `CONTEXT-MAP.md` in validation, enforce `-cross-review.md` on review filenames, add `AIzaSy` Google API key detection, and define relative plan link resolution.
- **Synchronize glossary terms**: Add `Delegation` to `CONTEXT.md` and align the terms list in `docs/designs/2026-10-20-project-skills-and-context-design.md`.
