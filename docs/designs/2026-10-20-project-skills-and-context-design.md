# Design: Project skills (handoff, zoom-out, explain, cross-review) and a CONTEXT.md domain glossary

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-project-skills-and-context-spec.md](../specs/2026-10-20-project-skills-and-context-spec.md)
- ADRs: [0004](../adr/0004-project-authored-skills.md), [0005](../adr/0005-context-md-domain-glossary.md), [0006](../adr/0006-cross-harness-review.md)

## Overview

```text
.agents/skills/<name>/SKILL.md            one source per skill (Codex, agy read it natively)
.agents/skills/<name>/agents/openai.yaml  Codex: allow_implicit_invocation: false
.claude/skills/<name> -> ../../.agents/skills/<name>   Claude Code entry point
scripts/project-skills.json               declares authored skills + entry points (no hashes)
scripts/vendored-skills.json              unchanged (pinned third-party skills)

CONTEXT.md                 template's own glossary (format: docs/templates/context.md)
docs/handoffs/             /handoff output (committed)
docs/reviews/              /cross-review reports (committed)
```

Evidence that shaped the design:

- **Codex 0.159.3, probed locally.** It tolerates Claude-only frontmatter keys. A skill with `agents/openai.yaml` set to `policy: {allow_implicit_invocation: false}` drops out of the implicit skill list, while a sibling skill without it stays listed. Explicit `$name` invocation is documented to still work.
- **Claude Code.** `disable-model-invocation: true` makes a skill user-only (`/name`). `claude -p --tools Read,Grep,Glob` restricts the available tool set.
- **Codex exec.** `codex exec -s read-only --ephemeral -o <file> -C <dir>` gives a read-only sandbox, no session persistence, the last message written to a file, and a chosen working directory.
- **agy.** `agy -p` auto-allows workspace file writes. `--mode plan` is not documented as a hard block, and there is no documented explicit-only control for skills.

## Components

| Component | Responsibility / change |
|---|---|
| `.agents/skills/handoff/` | `SKILL.md` (`argument-hint: "[what the next session will do]"`), plus `agents/openai.yaml`. Writes `docs/handoffs/YYYY-MM-DD-HHMMSS-<slug>.md` with the sections Goal, Current state, Decisions (with links), Open items, Next steps, and Suggested skills. Links existing artifacts (spec, design, ADR, plan, PR, commits) instead of copying them. Redacts secrets and personal data, and says so in the file when it redacted anything. |
| `.agents/skills/zoom-out/` | Read-only. Goes up one abstraction layer: lists the relevant modules, entry points, callers and data flow, named with `CONTEXT.md` terms, and states which files it read. Writes nothing. |
| `.agents/skills/explain/` | Re-pitches the previous answer: one or two lines of context, then the point. Uses simplified wording in the user's language, and ASD-STE100 Simplified Technical English when the answer is English. Uses `CONTEXT.md` terms (via `CONTEXT-MAP.md` when present). Writes nothing. |
| `.agents/skills/cross-review/` | `argument-hint: "<claude|codex|agy> [path to plan]"`. Details below. |
| `.claude/skills/{handoff,zoom-out,explain,cross-review}` | Relative symlinks to `../../.agents/skills/<name>`. |
| `scripts/project-skills.json` | `{"skills": [{"name": "handoff", "path": ".agents/skills/handoff", "entry_points": {".claude/skills/handoff": "../../.agents/skills/handoff"}}, ...]}` |
| `scripts/validate_template.py` | New `check_project_skills()` runs per declared skill. Details below. |
| `CONTEXT.md` | The template's glossary. Terms: Controller, Worker, Harness, Delegation, Task packet, Planning gate, PHASE 1 artifact set, Approval, Explicit-only skill, Vendored skill, Project skill, Entry point, Handoff, Cross-review, Worktree isolation. Ends with an example dialogue. |
| `docs/templates/context.md` | The format: a single-context or multi-context (`CONTEXT-MAP.md`) layout, and the rules to be opinionated, flag ambiguities, keep definitions tight, include only project-specific terms, and give an example dialogue. Written fresh, informed by the aces `CONTEXT-FORMAT.md`. |
| `AGENTS.md` | New subsection "Domain language (CONTEXT.md)" at the end of section 6 (R10). Section 9 gets one paragraph permitting `docs/handoffs/` and `docs/reviews/` writes at any time (R11), and `CONTEXT.md` is added to the permitted PHASE 1 writes. Section 7 gets a "Cross-review" note (data leaves to another vendor only on explicit instruction). |
| `docs/handoffs/.gitkeep`, `docs/reviews/.gitkeep` | Keep the directories in the repository. |
| Docs | `README.md` (skills list), `docs/HARNESSES.md` (invocation per harness: Claude `/name`, Codex `$name` or `/skills`, agy by asking for the skill by name), `docs/UPSTREAMS.md` ("Project skills" section crediting `mattpocock/skills` (MIT) for the handoff idea and aces-service as the adaptation source). |

### `check_project_skills()` in `scripts/validate_template.py`

For each skill declared in `scripts/project-skills.json`:

- `path` must be a real directory (not a symlink) that contains `SKILL.md`.
- The frontmatter, parsed with the existing `parse_frontmatter`, must have `name == directory name`, a non-empty `description`, and `disable-model-invocation: true`.
- `agents/openai.yaml` must parse with `policy.allow_implicit_invocation` set to `false`.
- Each entry point must be a symlink whose `readlink` equals the declared target.

The existing undeclared-symlink scan accepts links declared in either manifest.

The validator also:

- requires `CONTEXT.md` and `docs/templates/context.md` (added to `REQUIRED`), each containing a `## Language` heading;
- scans `docs/handoffs/**` and `docs/reviews/**` for these secret patterns: `-----BEGIN [A-Z ]*PRIVATE KEY-----`, `AKIA[0-9A-Z]{16}`, `gh[pousr]_[A-Za-z0-9]{36,}`, `xox[baprs]-[A-Za-z0-9-]{10,}`, `sk-[A-Za-z0-9_-]{20,}`;
- adds `docs/handoffs` and `docs/reviews` to the dated-record directories that the planning-gate section-reference check skips.

### cross-review flow

1. **Resolve the plan.** Use the argument, or else the newest `docs/plans/*.md`. Collect the spec, design and ADRs the plan links to, plus `CONTEXT.md` and `AGENTS.md` section 9. List any that are missing.
2. **Check the reviewer.** `<reviewer>` must be `claude`, `codex` or `agy`, and differ from the running harness. If it is missing or the same as the running harness, ask the user.
3. **Build one self-contained prompt**, whatever the path. Lenses:
   - forward traceability (spec → design → ADR → plan) and backward drift;
   - terminology versus `CONTEXT.md`;
   - correctness;
   - edge cases;
   - security and trust boundaries;
   - challenged assumptions.

   Each finding carries a severity (`blocker`, `major` or `minor`), a type, a file and section, and a fix. The report must follow the contract in step 6.
4. **Path A, the default:** print the prompt in one code block, with paths and the report filename resolved. Offer to save the reviewer's answer if the user pastes it back. Never run a CLI because it is installed.
5. **Path B, only when the user says to run the CLI:**
   - Copy the collected files, keeping their relative paths, into `tmp_dir=$(mktemp -d)`.
   - Run the reviewer with its cwd set to that copy:
     - `codex exec -C "$tmp_dir" -s read-only --ephemeral --skip-git-repo-check -o "$tmp_dir/report.md" "$prompt"`
     - `(cd "$tmp_dir" && claude -p --tools Read,Grep,Glob "$prompt")`
     - `(cd "$tmp_dir" && agy -p --mode plan "$prompt")`
   - Capture stdout (Codex: `report.md`), write the report, and delete `$tmp_dir`.
   - If the CLI is missing or errors, say so and fall back to Path A. Never write a partial report.
6. **Report** at `docs/reviews/YYYY-MM-DD-HHMMSS-<topic>-cross-review.md`. The header lists the generation time, the reviewer harness, the plan, the artifacts reviewed (missing ones marked), and the path (A or B). Then the ranked findings, then "Handoff — suggested next actions". The skill never edits the reviewed artifacts.

## Alternatives considered

- **Real copies in `.claude/skills/` as well as `.agents/skills/`.** This duplicates content and invites drift. Rejected, same as ADR 0003.
- **Add authored skills to `vendored-skills.json` with hashes.** Every local edit would require hash regeneration, which is a pin built for third-party content. Rejected in favour of a separate declaration file (ADR 0004).
- **Let `cross-review` run the CLI by default.** The user chose prompt-by-default. Running by default sends repo content to another vendor on every call.
- **Run the reviewer CLI against the real checkout.** `agy -p` can write workspace files and `--mode plan` is not a documented hard block. A temporary copy makes "cannot modify the repo" hold for all three reviewers (ADR 0006).
- **A glossary-maintenance skill.** The user chose rule + template only.
- **`tmp/handoffs/` (gitignored).** The user chose committed `docs/handoffs/`. The secret-pattern check and redaction rule reduce the risk.

## Risks

- **`agy` has no explicit-only control**, so it may load these skills on its own. Impact is low: three of them write nothing or only a handoff file, and `cross-review` only prints a prompt unless told to run. This is documented.
- **Committed handoffs or reviews may leak sensitive context** that a regex does not catch, such as internal hostnames or customer names. Mitigation: the redaction rule in `handoff`, and a reminder in `AGENTS.md` that these files are committed.
- **Cross-review data exposure.** Path B sends the artifacts to another vendor. It runs only on explicit instruction, and only the listed artifact files are copied, never the whole repository.
- **CLI flag drift** between versions. The commands live in one skill file; Path B failures fall back to Path A.
- **Section 9 change.** Permitting `docs/handoffs/` and `docs/reviews/` writes before approval widens the gate slightly. It is bounded to those two directories and those file types.
- **Rollback:** remove the four skill directories, symlinks, manifest, `CONTEXT.md` and template, revert the `AGENTS.md` and validator changes.

## Test strategy

- **R2–R4, R12 (structure).** Mutation cases:
  - a missing `disable-model-invocation`;
  - `allow_implicit_invocation: true`;
  - a name mismatch;
  - a missing `openai.yaml`;
  - a retargeted Claude link;
  - an undeclared skill symlink;
  - a skill dir that is a symlink;
  - a missing `CONTEXT.md`;
  - `CONTEXT.md` without `## Language`;
  - a fake AWS key planted in `docs/handoffs/`.

  Each case asserts its own error message. An accepted case: a handoff containing a harmless `sk-` prefix shorter than 20 characters.
- **R1–R3, discovery.**
  - Claude lists the four skills.
  - `codex debug prompt-input` does not list them implicitly.
  - `agy -p "List the names of the agent skills available in this workspace."` lists them. The user runs this, because it calls a model.
- **R5–R8, behaviour.**
  - Run `/handoff` once and check that the file passes the validator.
  - Run `/zoom-out` and `/explain` once, and check with `git status` that they wrote nothing.
  - Run `/cross-review codex` (Path A) and check that no process was spawned.
  - Run one Path B review of this change's own artifacts, with the user's go-ahead, and check that `git status` shows only the report.
- **R9–R11.** Review of the doc diffs, plus a fresh `security-reviewer` pass on cross-review and the secret check.
