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

PHASE 1 — CLARIFY AND PLAN (no file edits except the plan/spec files, no implementer):
1. Invoke the Superpowers brainstorming skill and ask me the questions that change the design.
2. Use read-only workers only where their evidence informs the plan.
3. Invoke the Superpowers writing-plans skill and save the plan. Include: success criteria, scope/non-goals, architecture decision, execution graph with read/write classification, worker roles, ordered tasks with exact files and tests, verification plan, risks, open questions.
4. Summarize the plan and give its path, then STOP and wait for explicit user approval. Do not start PHASE 2 in the same turn.

PHASE 2 — EXECUTE (only after I approve the plan):
Delegate safely, verify important conclusions, and return the synthesized result rather than raw agent transcripts. If the plan must change materially, stop and ask again.
```

Use `/agents list` to confirm project agents are discovered. Use `/agents reload` after changing agent definitions in a running session.
