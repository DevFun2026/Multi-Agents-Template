# Orchestration Guide

## Goal

The template optimizes for **quality per total token/cost**, not for the maximum number of agents.

The strongest session model should spend its context on decisions that are difficult to recover from: problem framing, architecture, synthesis, conflict resolution, and final judgment.

## Decision graph

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

## Role selection

### explorer

Use when the controller does not yet know where behavior lives.

Typical output:
- execution path;
- relevant files;
- symbols/interfaces;
- likely test locations;
- constraints the implementer must preserve.

### researcher

Use when current external or documentation evidence matters.

Useful parallel angles:
- official/primary evidence;
- implementation evidence;
- alternatives;
- failure modes and counterarguments.

### implementer

Use only after scope and acceptance criteria are stable enough to avoid large rework.

Give it:
- exact objective;
- allowed files/scope;
- relevant contracts;
- tests to run;
- definition of done.

### reviewer

Use after implementation or for risky design proposals.

A reviewer should be fresh enough to challenge assumptions rather than defend the implementation.

### security reviewer

Use for auth/authz, secrets, payments, cryptography, untrusted input, file/network access, infrastructure permissions, dependency/supply-chain changes, and sensitive data.

### UI/UX reviewer

Use only when visual/product interaction quality is part of the task.

Persist a design system or explicit design constraints before several implementers work on different components.

## Model-tier routing

Do not encode stale model names in repository policy.

At dispatch time, inspect the currently supported child-model options and map them to these logical tiers:

```text
CHEAP  -> search, discovery, simple tests, repetitive edits
MID    -> normal research, implementation, debugging, integration
STRONG -> architecture, security, hard review, conflict resolution
MAIN   -> synthesis, cross-domain judgment, final decision
```

Always set reasoning effort explicitly together with the model.

Suggested effort:
- low/medium for mechanical work;
- medium for normal research/implementation;
- high for security, subtle review, difficult debugging, or architecture.

## Context packet template

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

## Evidence packet template

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

Escalate when:
- evidence conflicts;
- the lower-tier child fails repeatedly for materially different reasons;
- security or data integrity is involved;
- architecture affects several subsystems;
- the decision is expensive to reverse.

Do not escalate merely because a task is long.
