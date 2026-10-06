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

OBJECTIVE:
[PASTE REQUEST HERE]

Plan, delegate cost-effectively, verify the real diff/tests, and return the synthesized result rather than raw agent transcripts.
```
