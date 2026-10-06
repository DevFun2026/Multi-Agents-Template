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
- project setting `worktree.baseRef = "head"` branches from the current committed HEAD instead of the remote default branch;
- uncommitted parent-checkout changes are not copied into the worktree;
- `.claude/settings.json` sets `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`;
- every project agent disallows `Agent`.

The implementer must report its worktree path and base/head refs. Reviewer has Bash and should inspect that worktree directly with `git -C <worktree> ...`; a reviewer launched from the main checkout should not assume the implementation is visible there.

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

The template deliberately separates dedicated local/web tools:

| Role | Local repo tools | Dedicated web tools | Shell may still open network |
|---|---:|---:|---:|
| explorer | yes | no | no shell in Claude/Gemini explorer |
| external researcher | no in Claude/Gemini | yes | no shell |
| reviewer | yes | no | yes |
| security reviewer | yes | no | yes |
| UI/UX reviewer | yes | no | yes |

Claude project permissions deny common `curl`/`wget` Bash commands, but this is a guardrail rather than proof of total network isolation. For an actual Bash execution boundary, use Claude Code's sandbox with explicit network restrictions/allowlists and do not allow unsandboxed Bash commands.

Gemini CLI 0.62.0 supports subagent-specific policy rules, but its **workspace policy tier is currently non-functional**. The repository therefore ships a user-policy example at `examples/gemini-user-policies/reviewer-network-deny.toml`; copy it to `~/.gemini/policies/` to apply it. It blocks direct/common wrapped `curl`/`wget` forms (including common absolute-path, `env`, and `VAR=value` prefixes) for reviewers, but it is not a full socket sandbox. Use `gemini --sandbox` when you need a stronger execution boundary.

Codex non-research roles explicitly set `web_search = "disabled"`. The Codex external researcher has live search and an instruction not to inspect local files, but current role TOML does not provide a hard local-read capability split comparable to Claude/Gemini tool lists.

## Discovery checks

### Codex

Run from project root and use:

```bash
codex doctor
```

CI tests this with a throwaway trusted `CODEX_HOME` and also requires `codex debug prompt-input` to expose a unique project-config marker, so a trust/path mistake cannot silently pass.

### Claude Code

Start from project root and confirm project agents are listed/usable. Recursion is capped by project settings.

### Gemini CLI

```text
/agents list
/agents reload
```

The second command is useful after editing agent definitions during a running session.

## Custom agent contract

These invariants apply to every agent file, including user-added roles:

1. `name` must equal the filename stem.
2. Claude/Gemini `tools` must be explicit; omission is rejected because the harness may inherit the parent/all tools.
3. Claude/Gemini roles may not combine local/shell-capable tools and dedicated web tools in the same role.
4. Gemini frontmatter remains strict and every tool name must pass the CLI-compatible tool-name validator.
5. Every `.codex/agents/*.toml` file must explicitly declare `name`, `description`, `developer_instructions`, and `web_search`.
6. A Codex role referenced from `.codex/config.toml` must use the same role name as its file.

Codex can explicitly enable live web search on a custom role, but unlike Claude/Gemini tool lists, current Codex role configuration does not give this template a hard capability split that forbids local reads in that same role.
