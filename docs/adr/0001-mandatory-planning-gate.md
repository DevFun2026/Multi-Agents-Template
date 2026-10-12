# ADR 0001: A mandatory planning gate stops every writing task for approval

- Status: Accepted
- Date: 2026-10-12
- Recorded after the fact for PR #3 (merged 2026-10-12). No separate spec or design was written at the time; the PR description holds the analysis.

## Context

Sessions started from the template prompts went straight to code. The prompts ended with "plan … then execute and return the result", and AGENTS.md ranked Superpowers below user and policy instructions. That ranking let "execute" legitimately override the approval stop in the Superpowers `brainstorming` skill.

## Decision

AGENTS.md section 9 defines a planning gate:

- clarify with `brainstorming`;
- gather read-only evidence;
- plan with `writing-plans`;
- then STOP and wait for explicit user approval before any other write or implementer spawn.

Every start prompt is split into PHASE 1 (plan, then stop) and PHASE 2 (execute after approval). The validator enforces the gate text, the prompt structure, the adapter pointers and the section references.

## Alternatives considered

- **Rely on Superpowers alone.** Rejected: the project's priority order let start prompts override its gates.
- **Claude Code plan mode only.** Rejected as the only mechanism: it is Claude-specific, while the template serves Codex and Gemini CLI too. It remains an optional extra safeguard.

## Consequences

- Every non-trivial writing task costs one extra user round-trip.
- The gate is instruction-level, not a hard harness guarantee.
- ADR 0002 extends the gate with a required artifact set.
