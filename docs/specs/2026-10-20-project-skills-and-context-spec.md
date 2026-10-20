# Spec: Project skills (handoff, zoom-out, explain, cross-review) and a CONTEXT.md domain glossary

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Design: [../designs/2026-10-20-project-skills-and-context-design.md](../designs/2026-10-20-project-skills-and-context-design.md)
- ADRs:
  - [../adr/0004-project-authored-skills.md](../adr/0004-project-authored-skills.md)
  - [../adr/0005-context-md-domain-glossary.md](../adr/0005-context-md-domain-glossary.md)
  - [../adr/0006-cross-harness-review.md](../adr/0006-cross-harness-review.md)
- Plan: [../plans/2026-10-20-project-skills-and-context.md](../plans/2026-10-20-project-skills-and-context.md)

## Problem

The user's `aces-service` project uses four small skills that the template lacks:

- `handoff` compacts a session for the next agent.
- `zoom-out` gives a map of modules and callers.
- `explain` re-pitches an unclear answer.
- `cross-review` gets a second model to review the planning artifacts.

`explain` and `zoom-out` rely on a domain glossary (`CONTEXT.md`), a concept the template does not have. Those skills are Claude-only, use aces-specific paths (`docs/spec/<id>`, 8 design files, Go stack), and only `cross-review` targets Gemini. The user wants them adapted for the template and available in Claude Code, Codex and `agy` (Antigravity CLI, the successor of Gemini CLI).

## Goals and success criteria

1. The four skills are discoverable and usable from Claude Code, Codex and `agy`, from one source copy each.
2. They run only when the user invokes them, wherever the harness supports that.
3. `CONTEXT.md` is a defined project concept with a format template, a rule in `AGENTS.md`, and a filled glossary for the template itself.
4. `cross-review` never sends repository content to another model unless the user explicitly asks it to run the CLI, and the other harness cannot modify the repository.
5. CI catches a broken skill layout, a missing explicit-only marker, a missing glossary, or a likely secret in a committed handoff or review.

## Scope

- New skills under `.agents/skills/`: `handoff`, `zoom-out`, `explain`, `cross-review`. Each has Claude symlinks and Codex `agents/openai.yaml`.
- `CONTEXT.md` (template glossary) and `docs/templates/context.md` (format).
- New directories `docs/handoffs/` and `docs/reviews/`.
- `AGENTS.md` rules for domain language, session artifacts, and cross-review.
- Validator rules, mutation tests, and docs (`README.md`, `docs/HARNESSES.md`, `docs/UPSTREAMS.md`).

## Non-goals

- Porting the other aces skills, the aces 6-phase commands, RTK, or aces's coding standards.
- A skill that maintains `CONTEXT.md` automatically (the user chose rule + template only).
- Guaranteeing explicit-only invocation in `agy`, which has no documented control for it.
- Running cross-review automatically, or treating it as a mandatory gate.

## Requirements

| ID | Requirement |
|---|---|
| R1 | Each skill lives once at `.agents/skills/<name>/SKILL.md` and is written for this template, not copied verbatim. `handoff`'s idea credits `mattpocock/skills` (MIT) in `docs/UPSTREAMS.md`. |
| R2 | Claude Code reaches each skill through `.claude/skills/<name>`, a relative symlink to `../../.agents/skills/<name>`. |
| R3 | Each `SKILL.md` frontmatter has `name` equal to the directory, a `description`, and `disable-model-invocation: true`. Each skill directory has `agents/openai.yaml` with `policy.allow_implicit_invocation: false`. |
| R4 | `scripts/project-skills.json` declares the authored skills and their entry points. The validator accepts their symlinks and still rejects any undeclared symlink. |
| R5 | `handoff` writes `docs/handoffs/YYYY-MM-DD-HHMMSS-<slug>.md`. It covers goal, current state, decisions, open items, next steps and suggested skills. It links to existing artifacts rather than copying them, and never includes secrets or personal data. |
| R6 | `zoom-out` returns a read-only map of the relevant modules, entry points and callers in `CONTEXT.md` vocabulary, without writing files. |
| R7 | `explain` re-pitches the previous answer: short context first, simplified wording (ASD-STE100 when the answer is in English), `CONTEXT.md` terms. It writes no files. |
| R8 | `cross-review <reviewer> [plan]` reviews one PHASE 1 artifact set and `CONTEXT.md`. `<reviewer>` is `claude`, `codex` or `agy`, and must differ from the current harness. The default output is a paste-ready prompt. Only on the user's explicit instruction to run the CLI does it run the reviewer in a temporary copy of the artifacts, with that CLI's read-only options. The report goes to `docs/reviews/YYYY-MM-DD-HHMMSS-<topic>-cross-review.md`. It never edits the reviewed artifacts. |
| R9 | `CONTEXT.md` at the root follows `docs/templates/context.md`: a description, a `## Language` section with bold terms, one-to-two-sentence definitions, `_Avoid_` aliases, and an example dialogue. A repository with several contexts uses `CONTEXT-MAP.md`. |
| R10 | `AGENTS.md` requires agents to read `CONTEXT.md` (or `CONTEXT-MAP.md`) when it exists and to use its terms in specs, designs and plans. When `brainstorming` settles a new term, the agent adds or updates it during PHASE 1, which makes `CONTEXT.md` a permitted PHASE 1 write. |
| R11 | `AGENTS.md` section 9 permits writing `docs/handoffs/` and `docs/reviews/` files at any time. These are session artifacts, not product changes, and need no planning-gate approval. |
| R12 | The validator fails on: a skill missing or malformed against R2–R4; a missing `CONTEXT.md` or `docs/templates/context.md`, or one without `## Language`; or a line in `docs/handoffs/**` or `docs/reviews/**` matching a common secret pattern (private-key header, AWS access key ID, GitHub/Slack/OpenAI-style token). |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes locally and in CI. Each new mutation case is rejected for its own reason.
- Claude Code lists the four skills. Codex's implicit skill list (`codex debug prompt-input`) does not list them, but `$handoff` and the others are explicitly invocable. `agy` lists them as workspace skills.
- `/cross-review codex` without "run" prints a prompt and calls no CLI.
- A real CLI cross-review of this change's own artifacts leaves `git status` showing only the new report.
- `/handoff` produces a file under `docs/handoffs/` that passes the secret check.

## Open questions

None.
