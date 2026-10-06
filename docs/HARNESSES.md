# Harness Support

This template uses one provider-neutral policy (`AGENTS.md`) with native adapters for Codex, Claude Code, and Gemini CLI.

## Codex

Project roles:

```text
.codex/agents/*.toml
```

Critical spawn behavior:

- child model/effort routing requires a clean or deliberately bounded fork;
- default template rule is `fork_turns: "none"`;
- a small integer is acceptable when a little recent context is genuinely needed;
- after choosing `fork_turns`, explicitly set child model + reasoning effort.

If full history is inherited, the runtime may inherit the parent model/effort and reject overrides.

Codex child agents share the same project directory. Read-only workers may run in parallel; workspace-writing implementers are serialized unless separate worktrees/workspaces are deliberately prepared.

The project config uses `developer_instructions`; `persistent_instructions` is intentionally not used because current Codex ignores it in project config.

## Claude Code

Project roles:

```text
.claude/agents/*.md
```

Routing:

- explorer/researcher -> Haiku-class
- implementer/reviewers -> Sonnet-class
- final architecture/judgment -> main session

Isolation/backstops:

- implementer has `isolation: worktree`;
- `.claude/settings.json` sets `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`;
- every project agent disallows `Agent`.

Reviewer has Bash so it can inspect the real diff and run local tests/checks rather than trusting a pasted summary.

Claude model validation intentionally accepts any non-empty model string; the template does not reject valid newer aliases/full model IDs.

## Gemini CLI

Project roles:

```text
.gemini/agents/*.md
```

Workers use:

```yaml
model: flash
```

The alias is intentional so current Gemini CLI promotion can move to the current Flash model rather than freezing a concrete preview model.

Gemini local subagents have separate conversation contexts and cannot recursively invoke subagents, but workspace-writing subagents in one main session share the active working tree.

`.gemini/settings.json` enables `experimental.worktrees`, which enables top-level worktree management. It does **not** mean each local subagent automatically gets its own worktree.

Therefore:

- parallelize read-only workers;
- serialize local write workers;
- use separate top-level `gemini --worktree ...` sessions for real parallel write isolation.

Gemini's built-in system behavior may prefer delegation more aggressively than this project policy. Project instructions cannot override stronger harness/system instructions, so skipping delegation for tiny tasks is best-effort.

## Network/data separation

The template deliberately separates local and external evidence:

| Role | Local repo read | Outbound web |
|---|---:|---:|
| explorer | yes | no |
| external researcher | no | yes |
| reviewer | yes | no |
| security reviewer | yes | no |
| UI/UX reviewer | yes | no |

This reduces the chance that untrusted repository content can directly drive an outbound request containing local data.

## Discovery checks

### Codex

Run from project root and use:

```bash
codex doctor
```

CI tests this with a throwaway trusted `CODEX_HOME`.

### Claude Code

Start from project root and confirm project agents are listed/usable. Recursion is capped by project settings.

### Gemini CLI

```text
/agents list
/agents reload
```

The second command is useful after editing agent definitions during a running session.
