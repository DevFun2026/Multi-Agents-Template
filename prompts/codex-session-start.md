# Codex Session Start

```text
Follow AGENTS.md and .codex/config.toml.

Act as the MAIN CONTROLLER. Keep the current session model for decomposition, architecture, synthesis, conflict resolution, and final decisions.

For EVERY spawned child:
1. set fork_turns: "none" by default (or a deliberately small integer when recent context is truly required);
2. select a model from the CURRENT spawn allowlist;
3. explicitly select reasoning effort.

Do not spawn a child with full inherited history when the purpose is cheaper model routing or context isolation.

Parallelize read-only explorer/research/review tasks when useful. Codex children share the same project directory, so serialize workspace-writing implementers unless separate worktrees/workspaces have deliberately been prepared.

Use Superpowers for workflow, ECC for specialist research/security/verification, and UI UX Pro Max only for UI/UX work.

OBJECTIVE:
[PASTE REQUEST HERE]

If the objective needs no file changes (research, review, a question), do the read-only work and report; the approval stop below applies only to work that writes.

PHASE 1 — CLARIFY AND PLAN (no file edits except the PHASE 1 artifacts, no implementer):
1. Invoke the Superpowers brainstorming skill, ask me the questions that change the design, then write the spec to docs/specs/YYYY-MM-DD-<topic>-spec.md (template: docs/templates/spec.md).
2. Use explorer/researcher children only where read-only evidence informs the plan.
3. Write the design to docs/designs/YYYY-MM-DD-<topic>-design.md (template: docs/templates/design.md), plus one ADR per architecture decision in docs/adr/NNNN-<title>.md with Status: Proposed (template: docs/templates/adr.md). With no architecture decision, write "ADRs: none".
4. Invoke the Superpowers writing-plans skill and write the plan to docs/plans/YYYY-MM-DD-<topic>.md (template: docs/templates/plan.md), linking the spec, design and ADRs. Include: success criteria, scope/non-goals, architecture decision, execution graph with read/write classification, child roles with model/effort tiers, ordered tasks with exact files and tests, verification plan, risks, open questions.
5. Summarize the plan and list the path of every artifact, then STOP and wait for explicit user approval. Do not start PHASE 2 in the same turn.

PHASE 2 — EXECUTE (only after I approve the plan):
First set the task's ADRs to Status: Accepted. Route work by cost tier, execute, verify, and return only the synthesized result and important evidence. If the plan must change materially, stop and ask again.
```
