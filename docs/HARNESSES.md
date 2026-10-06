# Harness Support

This template supports Codex, Claude Code, and Gemini CLI with one shared orchestration policy and native adapters.

## Shared source of truth

`AGENTS.md` defines the provider-neutral policy.

Harness entrypoints:

- Codex -> `AGENTS.md` + `.codex/config.toml`
- Claude Code -> `CLAUDE.md` imports `AGENTS.md`
- Gemini CLI -> `GEMINI.md` imports `AGENTS.md`

Do not maintain three independent copies of the orchestration policy.

## Agent locations

| Harness | Project agents |
|---|---|
| Codex | `.codex/agents/*.toml` |
| Claude Code | `.claude/agents/*.md` |
| Gemini CLI | `.gemini/agents/*.md` |

## Cost routing

### Codex

Model availability is session/build dependent, so model names are intentionally not pinned in project role files.

The controller selects a current allowed child model and reasoning effort at spawn time.

### Claude Code

The included roles use stable Claude model tiers:
- explorer/researcher: `haiku`
- implementer/reviewer/security/UIUX: `sonnet`
- main session: user-selected high-capability model

### Gemini CLI

The included local agents use `gemini-3-flash-preview` as the worker model.

Why:
- separate context loop protects the main conversation;
- Flash is appropriate for high-volume bounded work;
- main Gemini still makes architecture and final decisions.

If that model name changes in a future Gemini CLI release, update the `model:` line in `.gemini/agents/*.md` after checking current supported models.

## Native differences

Do not force identical mechanics across providers.

- Codex exposes per-spawn model + reasoning effort and project TOML agent roles.
- Claude Code project subagents use Markdown/YAML profiles and model tiers such as Haiku/Sonnet.
- Gemini CLI local subagents use Markdown/YAML profiles, separate context loops, tool isolation, and cannot recursively call other agents.

The policy is portable; the execution mechanism is native.

## Verify discovery

### Codex

Start Codex from repository root and confirm the project config is trusted/loaded.

### Claude Code

Start Claude Code from repository root. Project agents under `.claude/agents/` should be available to the controller.

### Gemini CLI

Run:

```text
/agents list
```

If files were added while Gemini CLI was already running:

```text
/agents reload
```

## Recommended main-session strategy

Select the strongest model you actually want to pay for as the main session model.

Then let the project route high-volume work to cheaper workers.

This pattern is most useful when the task contains enough independent work to amortize delegation overhead.
