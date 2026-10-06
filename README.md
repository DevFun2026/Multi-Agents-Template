# Multi-Agents Template

A multi-harness project template for cost-aware research and software development with **Codex**, **Claude Code**, and **Gemini CLI**.

The main-session model is the controller/judge. Cheaper workers handle bounded work; the main session keeps architecture, synthesis, conflict resolution, high-risk verification, and final decisions.

## Skill stack

- **Superpowers** — workflow/process authority.
- **ECC** — specialist research, engineering, security, verification, and context management.
- **UI UX Pro Max** — UI/UX intelligence.

The upstream skill packs are installed separately; this repository does not vendor them.

## Native routing

| Harness | Lower-cost workers | Write isolation | Final judgment |
|---|---|---|---|
| Codex | dynamic child model from current allowlist | shared cwd; serialize writers by default | main session |
| Claude Code | Haiku for explore/research, Sonnet for implement/review | implementer uses worktree | main session |
| Gemini CLI | `flash` alias | local subagents share active tree; serialize writers | main session |

## Important Codex rule

For **every** child spawn intended to save context/cost:

```text
fork_turns: "none"
model: <current allowed child model>
reasoning_effort: <appropriate effort>
```

A deliberately small integer may replace `"none"` when a little recent context is required.

Do **not** omit `fork_turns`: full-history forks can inherit the parent model/effort and refuse model overrides, defeating the template's main Codex cost mechanism.

## Repository layout

```text
.
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── .codex/
│   ├── config.toml
│   └── agents/
├── .claude/
│   ├── settings.json
│   └── agents/
├── .gemini/
│   ├── settings.json
│   └── agents/
├── docs/
├── prompts/
├── requirements-dev.txt
└── scripts/
    ├── bootstrap.sh
    ├── validate_template.py
    └── verify-template.sh
```

## Quick start

```bash
git clone https://github.com/DevFun2026/Multi-Agents-Template.git my-project
cd my-project
```

Inspect environment/integration plans without changing anything:

```bash
bash scripts/bootstrap.sh
bash scripts/bootstrap.sh codex
bash scripts/bootstrap.sh claude
bash scripts/bootstrap.sh gemini
bash scripts/bootstrap.sh all
```

Install **one** harness at a time:

```bash
bash scripts/bootstrap.sh --install codex
bash scripts/bootstrap.sh --install claude
bash scripts/bootstrap.sh --install gemini
```

`--install all` is intentionally rejected. Installing all three in one command makes third-party changes harder to inspect and can cause config collisions.

The bootstrap script always changes to the repository root before invoking project-local installers.

## Pinned bootstrap inputs

The current template pins the automatable third-party inputs it controls:

- ECC npm/release: **2.2.3**
- ECC reviewed source commit: `0348d7b6d722c8832b306859b78a1d969b427f5b`
- UI UX Pro Max CLI: **2.15.0**
- Superpowers Gemini extension source: `8ca22dba9a94f28898bbce59f2537ff4d87c747d`

Native marketplace installs that are intentionally interactive are documented rather than silently mutated.

## Claude behavior

Claude project agents live under `.claude/agents/`.

- explorer/researcher -> Haiku-class
- implementer/reviewers -> Sonnet-class
- implementer -> `isolation: worktree`
- project worktree base -> committed `HEAD`, not `origin/main`
- all project agents -> `disallowedTools: Agent`
- project settings -> `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`
- project permissions deny common `curl` / `wget` Bash commands

Uncommitted changes in the parent checkout are not copied into Claude worktrees. The controller must pass the implementer's worktree path plus base/head refs to a fresh reviewer; reviewing the main checkout can otherwise show an empty diff.

## Gemini behavior

Gemini project agents live under `.gemini/agents/` and use:

```yaml
model: flash
```

This keeps the current Flash alias upgrade path instead of pinning a stale concrete preview model.

`.gemini/settings.json` enables experimental worktree support for **top-level Gemini sessions**. It does not magically give each local subagent a different worktree. Therefore write agents inside one session are serialized.

For truly parallel write work, start separate top-level Gemini sessions with separate worktrees.

Gemini may have stronger built-in delegation preferences than project instructions; small-task non-delegation is therefore best-effort on Gemini.

## Network/data separation

To reduce accidental exfiltration paths:

- local **explorer** has repository tools but no dedicated web tools;
- external **researcher** is web-only in Claude/Gemini; Codex keeps this as an instruction-level restriction because its role sandbox can still read local files;
- local **security/UI reviewers** have no dedicated web tools.

"No dedicated web tools" is **not** the same as "no network." Claude `Bash` and Gemini `run_shell_command` can still execute network-capable binaries. Claude project settings deny common `curl`/`wget` commands. For Gemini CLI 0.62.0, workspace policies are currently non-functional, so copy the provided user-policy example to `~/.gemini/policies/` if you want that guardrail:

```text
examples/gemini-user-policies/reviewer-network-deny.toml
```

That policy blocks common fetch commands for reviewer roles; it is not a full network sandbox.

## Start prompts

Use:

```text
prompts/session-start.md
prompts/codex-session-start.md
prompts/claude-session-start.md
prompts/gemini-session-start.md
```

## Validation

Install validator dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run:

```bash
bash scripts/verify-template.sh
```

Validation now:

- parses Codex TOML with `tomllib` on Python 3.11+ or pinned `tomli` on Python 3.9/3.10;
- parses Gemini/Claude JSON;
- parses Claude/Gemini YAML frontmatter with PyYAML and requires explicit `tools`;
- checks exact `max_depth == 1`;
- verifies Codex role `config_file` targets;
- rejects ignored `persistent_instructions`;
- checks Claude recursion/worktree controls;
- mirrors Gemini's strict local-agent frontmatter keys/tool names and role-specific tool sets;
- runs Bash syntax checks and shellcheck when installed.

GitHub Actions additionally installs **Codex CLI 0.160.1**, creates a throwaway trusted `CODEX_HOME`, positively asserts a project-only marker through `codex debug prompt-input`, then runs `codex doctor` and fails on ignored config keys or malformed agent roles. The verification wrapper also runs mutation tests proving dangerous config changes are rejected.

## CI hardening

- `actions/checkout` is pinned to a full commit SHA.
- push CI runs only on `main`; pull requests use the PR event, avoiding duplicate same-repo feature-branch runs.
- shellcheck runs in CI.

## Docs

- `docs/HARNESSES.md` — real native behavior and limitations.
- `docs/ORCHESTRATION.md` — concurrency/model/context routing.
- `docs/UPSTREAMS.md` — pinned install/update strategy.
- `docs/SESSION-EXAMPLES.md` — examples.

---

The goal is not maximum agent count. The goal is the best final decision for the least total context/cost without pretending the three harnesses behave identically.