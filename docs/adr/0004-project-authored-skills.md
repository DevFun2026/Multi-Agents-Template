# ADR 0004: Project-authored skills live in `.agents/skills/`, explicit-only, declared in `scripts/project-skills.json`

- Status: Accepted
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-project-skills-and-context-spec.md](../specs/2026-10-20-project-skills-and-context-spec.md)
- Design: [../designs/2026-10-20-project-skills-and-context-design.md](../designs/2026-10-20-project-skills-and-context-design.md)

## Context

ADR 0003 put one vendored, hash-pinned skill at `.agents/skills/` with a Claude symlink. The validator now rejects any undeclared symlink in a skill root. The template now gains four skills written for it (`handoff`, `zoom-out`, `explain`, `cross-review`). They must work in Claude Code, Codex and `agy`, run only when the user calls them, and be editable without re-pinning hashes.

## Decision

1. Authored skills use the same layout as vendored ones:
   - source at `.agents/skills/<name>/`;
   - Claude Code entry point `.claude/skills/<name>`, a relative symlink to `../../.agents/skills/<name>`.
2. They are declared in a separate `scripts/project-skills.json` (name, path, entry points), with no hashes. `scripts/vendored-skills.json` stays the pin for third-party content only.
3. Every authored skill is explicit-only:
   - Claude Code: `disable-model-invocation: true` in `SKILL.md`.
   - Codex: `agents/openai.yaml` with `policy.allow_implicit_invocation: false`.
   - `agy`: no documented control; this is accepted as a known gap.

   Update (2026-10-20, after acceptance): a probe with `agy` 1.4.2 showed that `agy` honours `disable-model-invocation: true` the same way Claude Code does. The gap is closed in practice, though still undocumented by `agy` (see `docs/HARNESSES.md`).
4. The validator enforces the layout, the frontmatter, the Codex policy and the entry points. The undeclared-symlink rule covers both manifests.
5. Ideas taken from other projects are credited in `docs/UPSTREAMS.md`. Text is written for this template, not copied.

## Alternatives considered

- **Hash-pin authored skills in `vendored-skills.json`.** Every edit would need a hash refresh, and the file would lose its meaning as a third-party pin.
- **Real copies per harness directory.** Drift risk, rejected in ADR 0003.
- **Claude-only `.claude/skills/`.** Does not meet the all-harness requirement.

## Consequences

- Adding a project skill means adding its directory, `agents/openai.yaml`, a Claude symlink and a manifest entry. The validator says which piece is missing.
- `agy` may still invoke these skills implicitly until it offers a control.
- Two skill manifests exist, with clearly separate purposes.
