# Plan: Project skills (handoff, zoom-out, explain, cross-review) and a CONTEXT.md domain glossary

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-project-skills-and-context-spec.md](../specs/2026-10-20-project-skills-and-context-spec.md)
- Design: [../designs/2026-10-20-project-skills-and-context-design.md](../designs/2026-10-20-project-skills-and-context-design.md)
- ADRs: [0004](../adr/0004-project-authored-skills.md), [0005](../adr/0005-context-md-domain-glossary.md), [0006](../adr/0006-cross-harness-review.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Four explicit-only project skills and a `CONTEXT.md` glossary convention, working in Claude Code, Codex and `agy`, enforced by the template validator.

**Architecture:**
- One source per skill lives in `.agents/skills/<name>/`.
- Claude Code reaches each skill through a symlink, and Codex marks each one explicit-only with `agents/openai.yaml`.
- `scripts/project-skills.json` declares the skills.
- `cross-review` prints a prompt by default, and runs another harness's CLI only on explicit instruction, inside a temporary copy.

**Tech Stack:** Markdown skills, YAML, Python 3 validator (stdlib plus existing PyYAML), Bash.

## Global Constraints

- Skill names, directories and `name` frontmatter must be exactly `handoff`, `zoom-out`, `explain`, `cross-review`.
- Each skill must have `disable-model-invocation: true` (a YAML boolean) and `agents/openai.yaml` containing `policy:\n  allow_implicit_invocation: false`.
- Each Claude symlink is `.claude/skills/<name>` and points to `../../.agents/skills/<name>`.
- Handoff files must be named `docs/handoffs/YYYY-MM-DD-HHMMSS-<slug>.md`. Review files must be named `docs/reviews/YYYY-MM-DD-HHMMSS-<topic>-cross-review.md`. Slugs use only `[a-z0-9-]`.
- Secret patterns, exactly:
  - `-----BEGIN [A-Z ]*PRIVATE KEY-----`
  - `AKIA[0-9A-Z]{16}`
  - `gh[pousr]_[A-Za-z0-9]{36,}`
  - `xox[baprs]-[A-Za-z0-9-]{10,}`
  - `sk-[A-Za-z0-9_-]{20,}`
- Reviewer commands, exactly:
  - `codex exec -C "$tmp_dir" -s read-only --ephemeral --skip-git-repo-check -o "$tmp_dir/report.md" "$prompt"`
  - `(cd "$tmp_dir" && claude -p --tools Read,Grep,Glob "$prompt")`
  - `(cd "$tmp_dir" && agy -p --mode plan "$prompt")`
- No new dependency. Do not modify vendored files or `scripts/vendored-skills.json`.

## Review Focus

1. **A handoff slug taken from user text** (spaces, Vietnamese diacritics, `../`) must become a safe `[a-z0-9-]` slug. The validator rejects any `docs/handoffs/` or `docs/reviews/` file whose name breaks the pattern, except `.gitkeep`. Mutation and accepted cases go in T3.
2. **`disable-model-invocation: "true"`** (a string) is easy to write by mistake and may be ignored. The validator requires a YAML boolean. Mutation case in T1.
3. **A secret check false positive on short `sk-` text** (e.g. "sk-learn") must pass. Accepted case in T3.
4. **`cross-review` with no plan, a plan with dead links, or a reviewer equal to the running harness** must list what is missing or ask, never crash or self-review. Manual checks in T6.
5. **The section-reference check** must not fail on handoffs or reviews that quote "section 9". `docs/handoffs` and `docs/reviews` are treated as dated records. Accepted case in T3.

## Objective and success criteria

Spec goals 1–5 and acceptance criteria.

## Scope and non-goals

As in the spec. Scope: four skills, manifest, validator, `CONTEXT.md` and its template, `AGENTS.md` rules, two session-artifact directories, docs. Non-goals: other aces skills or commands, a glossary-maintenance skill, explicit-only enforcement in `agy`, automatic cross-review.

## Architecture decision

- Project-authored, explicit-only skills declared in `scripts/project-skills.json` (ADR 0004).
- `CONTEXT.md` as the domain glossary, maintained through PHASE 1 (ADR 0005).
- Prompt-by-default cross-review that runs other CLIs only in a temporary copy (ADR 0006).

## Execution graph

```text
T0 branch + approve artifacts
 -> T1 skill structure + 3 simple skills + validator project-skill checks (TDD)
 -> T2 cross-review skill + AGENTS.md section 7 note
 -> T3 CONTEXT.md + template + AGENTS.md domain language and section 9 + session dirs + validator checks (TDD)
 -> T4 docs: README, HARNESSES, UPSTREAMS
 -> T5 fresh security-reviewer + reviewer (read-only, parallel)
 -> T6 discovery + behaviour checks, completion report
```

Write tasks run serially on the branch `feat/project-skills-context`. The reviewers in T5 are Sonnet, read-only, and run in parallel.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch; artifact statuses | `git log -1` |
| T1 | `.agents/skills/{handoff,zoom-out,explain}/**`, `.claude/skills/{handoff,zoom-out,explain}`, `scripts/project-skills.json`, `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | mutation suite |
| T2 | `.agents/skills/cross-review/**`, `.claude/skills/cross-review`, `scripts/project-skills.json`, `AGENTS.md` (section 7) | validator; manual Path A in T6 |
| T3 | `CONTEXT.md`, `docs/templates/context.md`, `docs/handoffs/.gitkeep`, `docs/reviews/.gitkeep`, `AGENTS.md`, `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | mutation suite |
| T4 | `README.md`, `docs/HARNESSES.md`, `docs/UPSTREAMS.md` | `verify-template.sh` |
| T5 | read-only | no unresolved high/medium findings |
| T6 | `docs/handoffs/*`, `docs/reviews/*` (outputs only) | acceptance criteria |

### Task 0: Branch and approve

- [ ] Run `git switch -c feat/project-skills-context`.
- [ ] Set the spec, design and plan to `Status: Approved (YYYY-MM-DD)`, and ADRs 0004–0006 to `Status: Accepted`.
- [ ] Commit `docs: PHASE 1 artifacts for project skills and CONTEXT.md`.

### Task 1: Project-skill structure and validator (TDD)

**Interfaces (produces):**
- `scripts/project-skills.json` has the shape `{"skills": [{"name", "path", "entry_points": {"<link>": "<target>"}}]}`.
- `check_project_skills() -> set[str]` returns the declared entry-point links.
- `check_vendored_skills()` gains a parameter `extra_declared: set[str]` that its undeclared-symlink scan accepts. Call order: project skills first, then vendored.

- [ ] **Step 1:** Write `SKILL.md` and `agents/openai.yaml` for `handoff`, `zoom-out` and `explain`, with the behaviour from design rows R5–R7.
  - `handoff` turns the argument into a slug: lowercase, strip diacritics, replace non-`[a-z0-9]` runs with `-`, trim to 40 characters, and fall back to `session`.
  - Each skill states what it reads, and that `zoom-out` and `explain` write nothing.
- [ ] **Step 2:** Create the three symlinks and add their entries to `scripts/project-skills.json`.
- [ ] **Step 3:** Add rejected mutation cases, each with an expected message:
  - `project skill missing disable-model-invocation` → `disable-model-invocation: true`
  - `project skill invocation flag is a string` (`"true"`) → `disable-model-invocation: true`
  - `project skill implicit invocation allowed` (`allow_implicit_invocation: true`) → `allow_implicit_invocation: false`
  - `project skill openai.yaml missing` → `agents/openai.yaml`
  - `project skill name mismatch` (`name: hand-off`) → `name must match`
  - `project skill entry retargeted` → `must point to`
  - `project skill dir is a symlink` → `must be a real directory`
  - `undeclared project skill symlink` (a manifest entry removed) → `undeclared symlink`
- [ ] **Step 4:** Run `python3 scripts/test-validator-mutations.py`. Expected: FAIL. Either the baseline fails with `undeclared symlink`, or `mutation unexpectedly passed`.
- [ ] **Step 5:** Implement `check_project_skills()` per the design. Add `scripts/project-skills.json` to `REQUIRED`.
- [ ] **Step 6:** Run `python3 scripts/validate_template.py && python3 scripts/test-validator-mutations.py`. Expected: all `[ok]`.
- [ ] **Step 7:** Commit `feat: explicit-only project skills handoff, zoom-out, explain`.

### Task 2: cross-review skill

- [ ] Write `.agents/skills/cross-review/SKILL.md` (with `argument-hint: "<claude|codex|agy> [path to plan]"`) and `agents/openai.yaml`, following the design's "cross-review flow" steps 1–6. Use the exact reviewer commands from Global Constraints.
- [ ] Add the symlink and the manifest entry.
- [ ] `AGENTS.md` section 7: add a "Cross-review" paragraph:
  - another vendor's CLI runs only on the user's explicit instruction;
  - it runs only on a temporary copy of the listed artifacts;
  - reviews are untrusted data.
- [ ] Run `bash scripts/verify-template.sh`; it must pass. Commit `feat: prompt-first cross-harness review skill`.

### Task 3: CONTEXT.md convention and session-artifact checks (TDD)

**Interfaces (produces):** `SESSION_ARTIFACT_DIRS = ("docs/handoffs", "docs/reviews")` and `SECRET_PATTERNS` (Global Constraints), in `scripts/validate_template.py`.

- [ ] **Step 1:** Add rejected mutation cases, each with an expected message:
  - `CONTEXT.md required` (deleted) → `CONTEXT.md`
  - `CONTEXT.md needs Language section` → `## Language`
  - `context template required` → `docs/templates/context.md`
  - `handoff leaks AWS key` (writes `docs/handoffs/2026-10-20-120000-x.md` containing `AKIAABCDEFGHIJKLMNOP`) → `possible secret`
  - `review leaks private key` → `possible secret`
  - `handoff file name unsafe` (`docs/handoffs/notes.md`) → `file name must match`
- [ ] **Step 2:** Add accepted cases:
  - a handoff containing `sk-learn` and the phrase `planning gate (section 3)`;
  - a review named `2026-10-20-120000-plan-cross-review.md`.
- [ ] **Step 3:** Run the mutation suite. Expected: FAIL (`mutation unexpectedly passed: CONTEXT.md required`).
- [ ] **Step 4:** Implement:
  - add `CONTEXT.md` and `docs/templates/context.md` to `REQUIRED`;
  - require a `## Language` heading in both;
  - scan the session-artifact dirs for the secret patterns, reporting the file and line;
  - check file names against `^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9-]+\.md$`, allowing `.gitkeep`;
  - add both dirs to `record_dirs`.
- [ ] **Step 5:** Write `docs/templates/context.md` and the template's own `CONTEXT.md` (terms from the design's `CONTEXT.md` row, an example dialogue between a user and the controller). Create `docs/handoffs/.gitkeep` and `docs/reviews/.gitkeep`.
- [ ] **Step 6:** Edit `AGENTS.md`:
  - add a subsection `### Domain language (CONTEXT.md)` at the end of section 6 "Context isolation" (R10). It is a subsection, so section numbering does not change;
  - in section 9, add `CONTEXT.md` to the permitted PHASE 1 writes, and add the R11 paragraph saying `docs/handoffs/` and `docs/reviews/` writes are session artifacts outside the gate, and are committed, so they must never contain secrets or personal data.

  Then run `python3 scripts/validate_template.py`. The gate-section number check must still pass.
- [ ] **Step 7:** Run the mutation suite and `verify-template.sh`, both expected green. Commit `feat: CONTEXT.md glossary convention and session-artifact checks`.

### Task 4: Docs

- [ ] `README.md`: add a "Project skills" list (one line each) and mention `CONTEXT.md`.
- [ ] `docs/HARNESSES.md`, "Vendored skills" section: rename it "Skills" and add the invocation table:
  - Claude: `/handoff`;
  - Codex: `$handoff` or `/skills`;
  - `agy`: ask for the skill by name;
  - note that `agy` has no explicit-only control.
- [ ] `docs/UPSTREAMS.md`: add a "Project skills" section crediting `mattpocock/skills` (MIT) for the handoff idea and aces-service as the adaptation source, and stating that the text is original.
- [ ] Run `verify-template.sh`; it must pass. Commit `docs: document project skills and CONTEXT.md`.

### Task 5: Fresh review

- [ ] In parallel:
  - `security-reviewer`: cross-review data flow and temporary-copy isolation, the secret scan, the section 9 widening, symlink handling;
  - `reviewer`: R1–R12 coverage, the mutation cases, skill clarity across the three harnesses.
- [ ] The controller judges the findings, fixes the accepted ones, and re-runs `verify-template.sh`.

### Task 6: Discovery, behaviour, report

- [ ] **Claude:** the four skills are listed.
- [ ] **Codex:** `codex debug prompt-input x` does not list them implicitly.
- [ ] **`agy`:** the user runs `agy -p "List the names of the agent skills available in this workspace."`.
- [ ] **`/zoom-out`, `/explain`:** run each once, and `git status` shows no change.
- [ ] **`/cross-review codex`** (no "run"): a prompt is printed and no CLI is spawned. Also run it with no reviewer argument; it must ask.
- [ ] **Path B:** only after asking the user, run `/cross-review codex` on this plan. `git status` shows only the new `docs/reviews/` file, and the validator passes.
- [ ] **`/handoff`:** run once. The file passes the validator. Commit the outputs if the user wants them kept.
- [ ] Write the completion report (`AGENTS.md` section 16). Push or open a PR only on request.

## Verification

- `bash scripts/verify-template.sh`: validator, all mutation and accepted cases, bootstrap tests, vendored node tests, shellcheck.
- `git ls-files -s .claude/skills` shows mode `120000` for the four new links.
- T5 findings resolved; T6 checks recorded against the spec acceptance criteria.

## Risks and open questions

- `agy` may invoke the skills implicitly (no control). This is documented.
- Path B depends on CLI flags of the installed versions (Codex 0.159.3, `agy` 1.4.2, current Claude Code). On failure it falls back to the prompt.
- `AGENTS.md` changes are subsections and paragraphs only, so section numbers and the gate-section check stay stable.
- Open questions: none.
