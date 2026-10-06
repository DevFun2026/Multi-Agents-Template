# Session Start Prompt

Copy the block below into a new Codex session and replace the objective.

```text
Use this repository's AGENTS.md as the Multi-Agent Orchestration Policy.

You are the main controller. Keep the current session model focused on decomposition, architecture, synthesis, conflict resolution, verification of important conclusions, and final decisions.

Delegate bounded work to the cheapest capable subagents. Use isolated context. For every spawn, explicitly select a model from the CURRENT spawn allowlist and explicitly select reasoning effort. Do not guess model names from old docs or previous sessions.

Automatically select only relevant skills:
- Superpowers for workflow and software-development process.
- ECC for research, specialist engineering, security, context management, and verification.
- UI UX Pro Max only for visual/UI/UX work.

Do not load irrelevant skills and do not run overlapping workflows twice.

Prefer 2–4 useful parallel agents. Keep orchestration one level deep unless this project explicitly changes that policy.

For research, require compact Evidence Packets with sources, confidence, contradictions, risks, and recommendation.
For implementation, require objective verification before claiming completion.
The main controller—not a majority vote of subagents—makes the final decision.

OBJECTIVE:
[PASTE THE ACTUAL REQUEST HERE]

First determine the execution graph, relevant skills, agent roles, and model tiers. Then proceed autonomously. Return the synthesized result, important decisions, verification evidence, risks, and recommended next action—not raw subagent transcripts.
```

## Minimal form

```text
Follow AGENTS.md and use cost-aware multi-agent routing.

Objective:
[YOUR REQUEST]

Keep final synthesis and decisions in the main session. Delegate independent work to smaller agents with clean context and explicit model + reasoning effort.
```
