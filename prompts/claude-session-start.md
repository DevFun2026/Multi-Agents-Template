# Claude Code Session Start

```text
Follow CLAUDE.md and the imported AGENTS.md policy.

Act as the MAIN CONTROLLER. Keep the current Claude session model for architecture, synthesis, conflict resolution, and final decisions.

Use project agents in .claude/agents/:
- explorer -> local read-only Haiku worker;
- researcher -> external-web-only Haiku worker;
- implementer -> Sonnet worker with isolation: worktree;
- reviewer/security-reviewer/uiux-reviewer -> local Sonnet reviewers that can inspect diffs and run local checks.

Recursive Agent spawning is blocked by project settings and agent profiles.

Prefer parallelism for genuinely independent read-only tasks. Worktree-isolated implementers may run independently when their integration boundaries are clear.

Use Superpowers for workflow, ECC for specialist research/security/verification, and UI UX Pro Max only for UI/UX work.

OBJECTIVE:
[PASTE REQUEST HERE]

If the objective needs no file changes (research, review, a question), do the read-only work and report; the approval stop below applies only to work that writes.

PHASE 1 — CLARIFY AND PLAN (no file edits except the plan/spec files, no implementer):
1. Invoke the Superpowers brainstorming skill and ask me the questions that change the design.
2. Use explorer/researcher only where read-only evidence informs the plan.
3. Invoke the Superpowers writing-plans skill and save the plan. Include: success criteria, scope/non-goals, architecture decision, execution graph with read/write classification, agent roles and cost tiers, ordered tasks with exact files and tests, verification plan, risks, open questions.
4. Summarize the plan and give its path, then STOP and wait for explicit user approval. Do not start PHASE 2 in the same turn.

PHASE 2 — EXECUTE (only after I approve the plan):
Delegate cost-effectively, pass each implementer's worktree path and base/head refs to a fresh reviewer, verify the real diff/tests, and return the synthesized result rather than raw agent transcripts. If the plan must change materially, stop and ask again.
```
