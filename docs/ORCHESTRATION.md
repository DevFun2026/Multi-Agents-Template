# Orchestration Guide

## Core rule

Optimize **quality per total context/cost**, not agent count.

## Execution graph

```text
MAIN CONTROLLER
  |
  +-- independent read-only tasks -> parallel workers when useful
  |
  +-- workspace-writing tasks
        |
        +-- isolated worktrees/workspaces -> may parallelize carefully
        |
        +-- shared working tree -> serialize writers
  |
  -> review actual work product
  -> objective verification
  -> main synthesis/final decision
```

## Codex context/model routing

Every cost-routed Codex spawn should specify:

```text
fork_turns: "none"
model: <current allowed child model>
reasoning_effort: <explicit effort>
```

A small integer may be used instead of `"none"` when recent context is necessary.

The order matters conceptually: first choose a bounded fork, then choose the cheaper model/effort. Full inherited history defeats the intended isolation/cost mechanism.

## Claude routing

- read-only explorer/research -> Haiku-class
- implement/review -> Sonnet-class
- main -> architecture/final judgment

Claude implementers use worktree isolation. Recursive project-agent spawning is blocked by both project env depth and `disallowedTools: Agent`.

## Gemini routing

All template workers use `model: flash`.

Conversation context is isolated per local subagent, but working-tree writes are not. Serialize Gemini implementers in one session. Use separate top-level worktree sessions for parallel writers.

## Task packet

```text
Objective:
...

Relevant context:
- minimal, non-sensitive context only

Files/resources:
- ...

Constraints/contracts:
- ...

Acceptance criteria:
- ...

Expected output:
...
```

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

## Review contract

A fresh reviewer should inspect the work product itself.

Preferred inputs:

- working tree / worktree access;
- exact base/head refs when applicable;
- acceptance criteria.

Do not make the reviewer depend solely on an implementer's prose summary.

## External research contract

External researchers get web access but no repository read tools.

The controller provides only enough non-sensitive context to phrase the research question. Local evidence comes from explorer/reviewer roles.

## Escalation

Escalate when:

- evidence conflicts;
- a cheaper worker is insufficient;
- security/data integrity is involved;
- architecture spans several subsystems;
- the decision is expensive to reverse.

Do not escalate merely because a task is long.
