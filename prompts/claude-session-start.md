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

PHASE 1 — CLARIFY AND PLAN (no file edits except the PHASE 1 artifacts, no implementer):
1. Invoke the Superpowers brainstorming skill, ask me the questions that change the design, then write the spec to docs/specs/YYYY-MM-DD-<topic>-spec.md (template: docs/templates/spec.md).
2. Use explorer/researcher only where read-only evidence informs the plan.
3. Write the design to docs/designs/YYYY-MM-DD-<topic>-design.md (template: docs/templates/design.md), plus one ADR per architecture decision in docs/adr/NNNN-<title>.md with Status: Proposed (template: docs/templates/adr.md). With no architecture decision, write "ADRs: none".
4. Invoke the Superpowers writing-plans skill and write the plan to docs/plans/YYYY-MM-DD-<topic>.md (template: docs/templates/plan.md), linking the spec, design and ADRs. Include: success criteria, scope/non-goals, architecture decision, execution graph with read/write classification, agent roles and cost tiers, ordered tasks with exact files and tests, verification plan, risks, open questions.
5. Summarize the plan and list the path of every artifact, then STOP and wait for explicit user approval. Do not start PHASE 2 in the same turn.

PHASE 2 — EXECUTE (only after I approve the plan):
First set the task's ADRs to Status: Accepted and its spec, design and plan to Status: Approved. Delegate cost-effectively, pass each implementer's worktree path and base/head refs to a fresh reviewer, verify the real diff/tests, and return the synthesized result rather than raw agent transcripts. If the plan must change materially, stop and ask again.
```
