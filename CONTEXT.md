# Multi-agent orchestration template

The language of this template: how one main session (the **Controller**) plans, delegates to **Workers**, and verifies work across three **Harnesses**. Projects built from the template replace these terms with their own domain (see `docs/templates/context.md`).

## Language

### Roles

**Harness**:
A coding-agent program that runs a model with tools: Claude Code, Codex, or Antigravity CLI (`agy`, successor of Gemini CLI).
_Avoid_: client, agent app, IDE

**Controller**:
The main session in a **Harness**. It owns decomposition, architecture, security judgment, integration and the final decision.
_Avoid_: orchestrator, lead agent, parent (except inside a vendored skill that uses that word)

**Worker**:
A delegated agent that the **Controller** spawns for one bounded task. It never spawns other agents.
_Avoid_: subagent, child, helper

**Role**:
A named **Worker** definition with fixed tools and a cost tier: explorer, researcher, implementer, reviewer, security-reviewer, uiux-reviewer.
_Avoid_: persona, agent type

**Delegation**:
The **Controller** handing one bounded task to a **Worker** through a **Task packet**.
_Avoid_: offloading, outsourcing

**Task packet**:
The minimal brief a **Worker** receives: objective, constraints, exact paths, contracts, acceptance criteria and expected output.
_Avoid_: prompt dump, transcript

### Planning

**Planning gate**:
The rule that no write outside the **PHASE 1 artifact set** and no implementer spawn happens before **Approval** (`AGENTS.md` section 9).
_Avoid_: approval step, review gate

**PHASE 1 artifact set**:
The spec, design, ADRs and plan written under `docs/` before **Approval**. One **Approval** covers the whole set.
_Avoid_: planning docs, design docs

**Approval**:
An explicit user message, sent after the plan summary and artifact paths, that accepts that plan version without conditions.
_Avoid_: sign-off, OK (a conditional reply is not an **Approval**)

**Worktree isolation**:
A separate git working tree for one writing **Worker**, so parallel writers never share files.
_Avoid_: sandbox (that is an OS-level control)

### Skills

**Skill**:
A folder with a `SKILL.md` that a **Harness** loads as instructions.
_Avoid_: plugin, command

**Vendored skill**:
A third-party **Skill** copied byte-for-byte at a pinned commit and hash-checked (`scripts/vendored-skills.json`).
_Avoid_: installed skill

**Project skill**:
A **Skill** written for this template and declared in `scripts/project-skills.json`.
_Avoid_: custom skill, local skill

**Explicit-only skill**:
A **Skill** that runs only when the user invokes it, never on the model's own choice, wherever the **Harness** supports that.
_Avoid_: manual skill, slash command

**Entry point**:
The path where a **Harness** finds a **Skill**. For Claude Code it is a symlink in `.claude/skills/`.
_Avoid_: alias, shortcut

**Handoff**:
A committed file in `docs/handoffs/` that lets a fresh session continue the work without the conversation.
_Avoid_: summary, notes

**Cross-review**:
A review of one **PHASE 1 artifact set** by a model in a different **Harness**, saved in `docs/reviews/`.
_Avoid_: second opinion, peer review

**Path B**:
The **Cross-review** mode that runs the reviewing **Harness**'s CLI on a **Temporary copy**. It happens only when the user explicitly asks for it. Path A, the default, only prints the prompt.
_Avoid_: CLI mode, auto-review

**Temporary copy**:
A `cross-review.*` directory under the system temp directory. It holds only the reviewed artifacts, the prompt and an empty git repository, and is deleted by a separate exact-path command after **Path B**.
_Avoid_: sandbox (it is not one), scratch repo

## Flagged ambiguities

- "agent" was used for the **Harness**, the **Controller** and a **Worker**. Resolution: say which one; use "agent" alone only for the general idea.
- "parent" appears in the vendored `security-audit` skill. Inside that skill it means the **Controller**.
- "subagent" is Claude Code's own name for a **Worker** and appears in harness-specific text (`CLAUDE.md`, `.claude/agents/`). Keep it there; use **Worker** in specs, plans and task packets.

## Example dialogue

> **User:** Can a reviewer start fixing the plan while I read it?
>
> **Controller:** No. A reviewer is a **Worker** with read-only tools, and nothing changes before your **Approval**. If you want a second opinion first, run `/cross-review codex`. The **Cross-review** goes to `docs/reviews/`, and I revise the **PHASE 1 artifact set** if you agree with it.
>
> **User:** And if I stop for today?
>
> **Controller:** Run `/handoff`. The **Handoff** links the plan and lists the next steps, so a session in any **Harness** can pick it up.
