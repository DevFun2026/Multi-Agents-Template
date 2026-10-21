# ADR 0006: Cross-harness review is prompt-by-default and runs other CLIs only in a temporary copy

- Status: Accepted
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-project-skills-and-context-spec.md](../specs/2026-10-20-project-skills-and-context-spec.md)
- Design: [../designs/2026-10-20-project-skills-and-context-design.md](../designs/2026-10-20-project-skills-and-context-design.md)

## Context

A second model reviewing the PHASE 1 artifacts before approval catches blind spots of the controller's model. The template already supports three harnesses (Claude Code, Codex, `agy`), so one can review another's plan. Running another vendor's CLI crosses two boundaries:

- **Data leaves to another provider.** This is a network and data boundary (`AGENTS.md` sections 7 and 12).
- **The other CLI can modify files.** `agy -p` auto-allows workspace writes, and its plan mode is not a documented hard block.

## Decision

1. `/cross-review <reviewer>` takes a reviewer harness (`claude`, `codex`, `agy`) that must differ from the running one.
2. By default it only prints a self-contained, paste-ready review prompt. It runs a CLI only when the user explicitly says to run it. CLI availability is never permission.
3. When it does run a CLI, it copies only the reviewed artifact files into a fresh `mktemp -d` directory and runs the reviewer there with read-only options:
   - Codex: `exec -s read-only --ephemeral -C <tmp>`;
   - Claude: `-p --tools Read,Grep,Glob`;
   - `agy`: `-p --mode plan`, with the copy as its cwd.

   The skill then writes the report itself and deletes the copy.

   Update (2026-10-21, after acceptance): deletion is a separate, best-effort step.
   - It runs `rm -rf -- '<path>'` only on the exact canonical path that `mktemp` printed in that run.
   - If a harness safety check blocks the command, the skill reports the path to the user instead.
   - The decision itself (a temporary copy, an explicit request, a read-only reviewer) is unchanged.
   - Details are in `.agents/skills/cross-review/SKILL.md`, step 5.
4. Reports go to `docs/reviews/` and are committed. The skill never edits the reviewed artifacts. Writing to `docs/reviews/` and `docs/handoffs/` is permitted at any time and is outside the planning gate.
5. Cross-review is optional. It is not part of the approval stop.

## Alternatives considered

- **Run the CLI by default.** It is faster, but sends repository content to another vendor on every call. The user declined it.
- **Run the CLI against the real checkout with read-only flags.** Safe for Claude and Codex, but not provable for `agy`.
- **A fixed reviewer harness.** Simpler, but wastes the template's multi-harness design and fails when that harness is the running one.

## Consequences

- No repository data leaves without an explicit instruction, and the reviewer cannot change the repository.
- Path B depends on CLI flags that may change. Failures fall back to the prompt.
- Committed reviews and handoffs need a secret-pattern check in the validator.
