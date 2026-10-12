# Gemini CLI Session Start

```text
Follow GEMINI.md and the imported AGENTS.md policy.

Act as the MAIN CONTROLLER. Keep the current Gemini session model for architecture, synthesis, conflict resolution, and final decisions.

Use project agents in .gemini/agents/. They use the flash alias for lower-cost isolated context.

Parallelize read-only workers when useful. Serialize workspace-writing implementers inside one session because local subagents share the active working tree.

For truly parallel write work, use separate top-level Gemini sessions in separate git worktrees; experimental.worktrees is enabled for that capability.

Independently re-check architecture, security-sensitive conclusions, and conflicting evidence in the main session.

Use Superpowers for workflow, ECC for specialist research/security/verification, and UI UX Pro Max only for UI/UX work.

OBJECTIVE:
[PASTE REQUEST HERE]

If the objective needs no file changes (research, review, a question), do the read-only work and report; the approval stop below applies only to work that writes.

PHASE 1 — CLARIFY AND PLAN (no file edits except the PHASE 1 artifacts, no implementer):
1. Invoke the Superpowers brainstorming skill, ask me the questions that change the design, then write the spec to docs/specs/YYYY-MM-DD-<topic>-spec.md (template: docs/templates/spec.md).
2. Use read-only workers only where their evidence informs the plan.
3. Write the design to docs/designs/YYYY-MM-DD-<topic>-design.md (template: docs/templates/design.md), plus one ADR per architecture decision in docs/adr/NNNN-<title>.md with Status: Proposed (template: docs/templates/adr.md). With no architecture decision, write "ADRs: none".
4. Invoke the Superpowers writing-plans skill and write the plan to docs/plans/YYYY-MM-DD-<topic>.md (template: docs/templates/plan.md), linking the spec, design and ADRs. Include: success criteria, scope/non-goals, architecture decision, execution graph with read/write classification, worker roles, ordered tasks with exact files and tests, verification plan, risks, open questions.
5. Summarize the plan and list the path of every artifact, then STOP and wait for explicit user approval. Do not start PHASE 2 in the same turn.

PHASE 2 — EXECUTE (only after I approve the plan):
First set the task's ADRs to Status: Accepted. Delegate safely, verify important conclusions, and return the synthesized result rather than raw agent transcripts. If the plan must change materially, stop and ask again.
```

Use `/agents list` to confirm project agents are discovered. Use `/agents reload` after changing agent definitions in a running session.
