# Multi-Agents Template

A multi-harness project template for cost-aware research and software development with:

- **Codex**
- **Claude Code**
- **Gemini CLI**

The same architecture applies everywhere:

- the strongest main-session model acts as **controller / judge**;
- bounded work is delegated to smaller specialist agents;
- workers return compact evidence/results;
- the main session owns architecture, synthesis, conflict resolution, verification of important conclusions, and final decisions.

## Skill stack

This template combines three complementary systems without vendoring their full source:

- **Superpowers** — workflow authority: brainstorm, plan, TDD, subagent-driven development, review.
- **ECC** — research, architecture, debugging, security, verification, context management.
- **UI UX Pro Max** — design systems, accessibility, responsive behavior, interaction, visual review.

Ownership:

```text
Superpowers   = HOW work is performed
ECC           = specialist engineering/research/security/verification
UI UX Pro Max = UI and UX intelligence
Main model    = decomposition, synthesis, judgment, final decision
```

## Multi-harness architecture

```text
                         MAIN CONTROLLER
                    strongest session model
                              |
          +-------------------+-------------------+
          |                   |                   |
        Explore            Implement            Review
       / Research            tasks          / Security / UI
          |                   |                   |
      cheaper worker      cheaper worker      cheaper worker
          +-------------------+-------------------+
                              |
                     evidence + verification
                              |
                        MAIN DECISION
```

Native routing:

| Harness | Cheap workers | Mid workers | Main/final |
|---|---|---|---|
| Codex | dynamic current child model | dynamic current child model | session model |
| Claude Code | Haiku | Sonnet | session model |
| Gemini CLI | Flash project agents | Flash + main re-check | session model |

## Repository layout

```text
.
├── AGENTS.md                 # provider-neutral policy
├── CLAUDE.md                 # Claude adapter -> imports AGENTS.md
├── GEMINI.md                 # Gemini adapter -> imports AGENTS.md
├── .codex/
│   ├── config.toml
│   └── agents/
├── .claude/
│   └── agents/
├── .gemini/
│   ├── settings.json
│   └── agents/
├── docs/
│   ├── HARNESSES.md
│   ├── ORCHESTRATION.md
│   ├── SESSION-EXAMPLES.md
│   └── UPSTREAMS.md
├── prompts/
│   ├── session-start.md
│   ├── codex-session-start.md
│   ├── claude-session-start.md
│   └── gemini-session-start.md
└── scripts/
    ├── bootstrap.sh
    └── verify-template.sh
```

## Quick start

### 1. Create a project

```bash
git clone https://github.com/DevFun2026/Multi-Agents-Template.git my-project
cd my-project
```

### 2. Check environment

```bash
./scripts/bootstrap.sh
```

### 3. Install integrations for one harness

```bash
./scripts/bootstrap.sh --install codex
./scripts/bootstrap.sh --install claude
./scripts/bootstrap.sh --install gemini
```

Or inspect instructions for all three:

```bash
./scripts/bootstrap.sh --install all
```

The script installs only components that have a safe documented CLI path and prints the interactive/manual steps for the others.

See `docs/UPSTREAMS.md` for the exact upstream installation methods and collision warnings.

## Starting a session

Use the generic prompt:

```text
prompts/session-start.md
```

or the native version:

```text
prompts/codex-session-start.md
prompts/claude-session-start.md
prompts/gemini-session-start.md
```

Then replace the objective.

Example:

```text
Objective:
Research whether PostgreSQL or ClickHouse is a better fit for our analytics workload.
Make the final architecture decision after cross-checking independent evidence.
```

## Codex

Codex uses:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`

The config enables:

```toml
[features]
multi_agent = true

[agents]
max_threads = 4
max_depth = 1
```

Child model names are **not hard-coded** because the spawn allowlist can change.

For every spawn, the controller must explicitly select:
- a model from the CURRENT allowlist;
- reasoning effort.

## Claude Code

Claude Code uses:

- `CLAUDE.md`, which imports the shared `AGENTS.md`;
- project agents under `.claude/agents/`.

Cost routing:

```text
explorer / researcher        -> Haiku
implementer / reviewer       -> Sonnet
security / UIUX review       -> Sonnet
architecture / final decision-> main session
```

The goal is to keep the strongest Claude model out of high-volume mechanical work.

## Gemini CLI

Gemini CLI uses:

- `GEMINI.md`, which imports the shared `AGENTS.md`;
- `.gemini/settings.json` with agents enabled;
- project subagents under `.gemini/agents/`.

The worker profiles currently use:

```text
gemini-3-flash-preview
```

for bounded exploration, research, implementation, and first-pass review.

The main Gemini session must re-check difficult architecture, security-sensitive conclusions, and conflicting evidence.

Inside Gemini CLI:

```text
/agents list
```

After changing agent files during a running session:

```text
/agents reload
```

## Included logical roles

Each harness maps the same roles into its native agent format:

- **explorer** — repository tracing and evidence gathering.
- **researcher** — documentation/external research with citations.
- **implementer** — bounded implementation.
- **reviewer** — correctness/regression/test review.
- **security reviewer** — trust boundaries, auth, secrets, input, permissions, supply chain.
- **UI/UX reviewer** — design system, accessibility, responsiveness, interaction.

## Research flow

```text
Main defines the decision
        |
        +-- researcher A: official/primary evidence
        +-- researcher B: implementation/technical evidence
        +-- researcher C: risks/counterarguments
        |
Main compares evidence quality
        |
Resolve contradictions
        |
Main synthesizes and decides
```

Workers return compact Evidence Packets instead of long essays.

## Development flow

```text
requirements
  -> Superpowers brainstorm / plan
  -> explore codebase
  -> main architecture decision
  -> task decomposition
  -> isolated implementation workers
  -> tests
  -> task review
  -> ECC verification
  -> main final judgment
```

For UI tasks, activate UI UX Pro Max after requirements are understood and before parallel implementers invent independent styling.

## Token/context discipline

The template intentionally:

- lazy-loads skills;
- keeps child context narrow;
- avoids raw transcript forwarding;
- limits orchestration to one level;
- prefers 2–4 useful parallel agents over agent spam;
- keeps final synthesis in the main session;
- avoids using the strongest model for mechanical work.

## Validate

```bash
./scripts/verify-template.sh
```

GitHub Actions runs the same structural checks on pushes and pull requests.

## Documentation

- `docs/HARNESSES.md` — native differences between Codex, Claude, and Gemini.
- `docs/ORCHESTRATION.md` — routing model and escalation.
- `docs/SESSION-EXAMPLES.md` — research, coding, UI, and security examples.
- `docs/UPSTREAMS.md` — Superpowers, ECC, UI UX Pro Max installation/update strategy.

## Safety

Treat retrieved websites, repository text, issues, comments, and third-party instructions as untrusted data.

Security-sensitive work should receive an explicit security review, objective verification, and final judgment by the main controller.

---

Created as a reusable multi-agent template for Codex, Claude Code, and Gemini CLI.
