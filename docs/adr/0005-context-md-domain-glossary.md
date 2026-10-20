# ADR 0005: `CONTEXT.md` is the project's domain glossary

- Status: Accepted
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-project-skills-and-context-spec.md](../specs/2026-10-20-project-skills-and-context-spec.md)
- Design: [../designs/2026-10-20-project-skills-and-context-design.md](../designs/2026-10-20-project-skills-and-context-design.md)

## Context

Specs, designs, plans and agent answers drift between synonyms. One example is "worker", "subagent" and "child" for the same role. `explain` and `zoom-out` need a shared vocabulary to answer in. The aces-service project solved this with a root `CONTEXT.md` glossary, and with `CONTEXT-MAP.md` for repositories that have several bounded contexts. The template has no such concept.

## Decision

1. A repository built from the template keeps its domain language in a root `CONTEXT.md`. A repository with several contexts uses a root `CONTEXT-MAP.md` that points to one `CONTEXT.md` per context.
2. The format is fixed by `docs/templates/context.md`:
   - a one-to-two-sentence description;
   - a `## Language` section with bold terms, tight definitions and `_Avoid_` aliases;
   - optional grouping;
   - flagged ambiguities;
   - an example dialogue.
3. `AGENTS.md` requires agents to read the glossary when it exists and to use its terms in specs, designs, plans and answers. When `brainstorming` settles a new or changed term, the agent updates `CONTEXT.md` during PHASE 1. `CONTEXT.md` is a permitted PHASE 1 write.
4. The template ships its own `CONTEXT.md` for orchestration terms. The validator requires it and the format template, each with a `## Language` heading.
5. There is no dedicated maintenance skill. Upkeep happens inside the existing Superpowers workflow.

## Alternatives considered

- **Glossary inside `AGENTS.md`.** This mixes policy with vocabulary and grows the always-loaded instructions.
- **A maintenance skill (glossary sync or grill).** It overlaps Superpowers `brainstorming`, the process authority. The user declined it.
- **No shipped glossary, format only.** New users would get no working example, and `explain`/`zoom-out` would have nothing to use in the template itself.

## Consequences

- One more file to keep current. Stale terms are possible because no tool enforces content.
- PHASE 1 may now touch `CONTEXT.md` before approval. This is a slight widening of the gate.
- Projects built from the template should replace the template's terms with their own domain.
