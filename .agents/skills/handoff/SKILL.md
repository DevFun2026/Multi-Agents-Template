---
name: handoff
description: Compact the current session into a handoff file in docs/handoffs/ so a fresh agent, in any harness, can continue the work. Use only when the user asks for a handoff.
argument-hint: "[what the next session will do]"
disable-model-invocation: true
---

# Handoff

Write one handoff file so a fresh agent can continue this work without the conversation.

## File

- Path: `docs/handoffs/YYYY-MM-DD-HHMMSS-<slug>.md`, using the current local time (`date +%Y-%m-%d-%H%M%S`).
- Slug: take it from the user's argument or, if none, from the main topic. Lowercase it, remove diacritics, replace every run of characters outside `[a-z0-9]` with `-`, trim `-` from both ends, and cut it to 40 characters. If nothing is left, use `session`.
- Never write anywhere else. Never overwrite an existing file.

## Content

Use these sections, in this order. Keep each one short.

1. **Goal**: what the work is for, and the success criteria.
2. **Current state**: what is done, what is in progress, the branch and the last commit.
3. **Decisions**: each decision in one line, with a link to the spec, design, ADR, plan, PR or commit that records it.
4. **Open items**: unresolved questions, blockers, failing checks, and approvals still needed (for example, the planning gate in `AGENTS.md`).
5. **Next steps**: numbered, each with how to verify it.
6. **Suggested skills**: the skills the next agent should use, and why.

If the user passed an argument, tailor the file to that next-session focus.

## Rules

- Link artifacts that already exist (`docs/specs/`, `docs/designs/`, `docs/adr/`, `docs/plans/`, PRs, commits, diffs). Do not copy their content.
- Use the terms in `CONTEXT.md` (or the right one via `CONTEXT-MAP.md`) when the repository has one.
- This file is committed to the repository. Never include secrets, tokens, keys, passwords, connection strings, personal data, or customer data. Replace any such value with `[REDACTED]`. If you redacted anything, say so at the end of the file.
- Write the file, then report its path. Do not commit unless the user asks.
