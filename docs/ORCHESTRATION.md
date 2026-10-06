# Orchestration Guide

## Goal

Optimize for **quality per total token/cost**, not for maximum agent count.

The strongest main-session model should spend its context on problem framing, architecture, synthesis, conflict resolution, verification, and final judgment.

## Shared decision graph

```text
Is the task substantial?
 |
 +-- no -> main handles it directly
 |
 +-- yes
       |
       +-- Can independent work packets be isolated?
             |
             +-- no -> main or one specialist agent
             |
             +-- yes -> 2-4 focused agents in parallel
                            |
                            +-> compact evidence/results
                            |
                        main synthesis
                            |
                    verification/review
                            |
                       final decision
```

## Native harness mapping

| Logical role | Codex | Claude Code | Gemini CLI |
|---|---|---|---|
| Main controller | session model | session model | session model |
| Cheap explorer/researcher | dynamic allowed child model | Haiku project agent | Flash project agent |
| Implementation | dynamic cheap/mid child | Sonnet project agent | Flash project agent |
| Review | dynamic mid/strong child | Sonnet project agent | Flash project agent + main re-check when risky |
| Architecture/final judgment | main | main | main |
| Agent recursion | max_depth=1 | policy: one level | natively blocked for local subagents |

### Codex

Project roles live in `.codex/agents/`.

At every spawn:
- use a model from the CURRENT spawn allowlist;
- explicitly set model and reasoning effort;
- prefer clean isolated context.

### Claude Code

Project roles live in `.claude/agents/`.

This template uses:
- Haiku for explorer/researcher;
- Sonnet for implementer/reviewer/security/UIUX;
- main session for architecture and final decisions.

The role files are a cost-aware default. Escalate only when the main controller decides the task warrants it.

### Gemini CLI

Project roles live in `.gemini/agents/`.

This template uses a Flash-class model for workers. Gemini local subagents run in isolated contexts and cannot call other subagents, which matches the one-level orchestration policy.

For difficult architecture, ambiguous security findings, or conflicting evidence, the main session must independently re-check the worker output.

## Role selection

### explorer

Use when the controller does not yet know where behavior lives.

Return execution path, relevant files, symbols/interfaces, likely tests, and constraints.

### researcher

Use when current external or documentation evidence matters.

Parallel research angles can include official sources, implementation evidence, alternatives, and failure modes.

### implementer

Use only after scope and acceptance criteria are stable enough to avoid large rework.

Give exact objective, allowed scope, contracts, tests, and definition of done.

### reviewer

Use after implementation or for risky design proposals. A fresh reviewer should challenge assumptions rather than defend implementation choices.

### security reviewer

Use for auth/authz, secrets, payments, cryptography, untrusted input, file/network access, infrastructure permissions, dependency/supply-chain changes, and sensitive data.

### UI/UX reviewer

Use only when visual/product interaction quality is part of the task. Persist a design system or explicit constraints before several implementers work in parallel.

## Logical model tiers

```text
CHEAP  -> search, discovery, simple tests, repetitive edits
MID    -> normal research, implementation, debugging, integration
STRONG -> security-sensitive review, hard debugging, conflict resolution
MAIN   -> architecture, synthesis, cross-domain judgment, final decision
```

The logical tier is stable even when provider model names change.

## Context packet

```text
Objective:
...

Relevant context:
- ...

Files/resources:
- ...

Constraints:
- ...

Acceptance criteria:
- ...

Expected output:
...
```

Avoid forwarding the complete parent transcript.

## Evidence packet

```text
Findings
- ...

Evidence
- source/path:
- support:

Confidence
- high | medium | low

Contradictions
- ...

Risks
- ...

Recommendation
- ...
```

## Escalation

Escalate when evidence conflicts, the cheaper worker is insufficient, security/data integrity is involved, architecture spans several subsystems, or the decision is expensive to reverse.

Do not escalate merely because a task is long.
