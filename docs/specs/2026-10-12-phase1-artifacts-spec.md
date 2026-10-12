# Spec: PHASE 1 produces spec, design, ADR and plan

- Status: Draft (awaiting approval)
- Date: 2026-10-12
- Design: [../designs/2026-10-12-phase1-artifacts-design.md](../designs/2026-10-12-phase1-artifacts-design.md)
- ADR: [../adr/0002-phase1-artifact-set.md](../adr/0002-phase1-artifact-set.md)
- Plan: [../plans/2026-10-12-phase1-artifacts.md](../plans/2026-10-12-phase1-artifacts.md)

## Problem

A session started from the template prompts produced only a plan file. No spec, design or ADR was written, because the template never required them:

- `AGENTS.md` section 9 only *permits* "design/spec files that the Superpowers skills themselves produce" and requires only the plan.
- Start prompts tell `brainstorming` only to "ask me the questions" and `writing-plans` to "save the plan".
- ADRs are not mentioned anywhere.
- The validator checks only the plan and the approval stop.

## Goals and success criteria

1. Every non-trivial writing task produces, before the approval stop: a **spec**, a **design**, and a **plan**. It also produces an **ADR** for each architecture decision it makes.
2. Spec and design are **separate files**:
   - the spec covers what and why;
   - the design covers how.
3. Artifacts live at fixed project paths with fixed templates, whichever skill or harness wrote them.
4. Approval covers the whole set. On approval, the ADRs move from Proposed to Accepted.
5. The validator fails if any of the following is missing:
   - the rule;
   - the prompt wording;
   - the templates;
   - a well-formed ADR.

## Scope

- `AGENTS.md`: the planning gate, the workflow, and the completion report.
- The four start prompts.
- `CLAUDE.md`, `GEMINI.md` and Codex `developer_instructions`: pointers only.
- New templates: `docs/templates/{spec,design,adr,plan}.md`.
- New artifact directories: `docs/specs/`, `docs/designs/`, `docs/adr/`, `docs/plans/`.
- The first ADRs:
  - 0001, which records the planning gate already merged;
  - 0002, which records this change.
- Validator and mutation tests.
- Docs: README, ORCHESTRATION, SESSION-EXAMPLES, and the architecture page.

## Non-goals

- Changing the approval rules, the exemptions, or the PHASE 1/PHASE 2 structure.
- Vendoring or modifying Superpowers.
- Validating the content quality of specs, designs or plans (only their structure and presence).
- Enforcing artifacts with harness hooks.

## Requirements

| ID | Requirement |
|---|---|
| R1 | AGENTS.md defines the four artifacts, their paths, and their order (spec, design + ADRs, plan) inside the planning gate. |
| R2 | ADR is mandatory when the task decides any of the following: a new dependency or major upgrade; a data model or schema; a public interface or API; a cross-cutting pattern or convention; infrastructure, deployment or a security boundary; or anything else expensive to reverse. Otherwise the ADR is optional. |
| R3 | Project paths and templates override skill default locations. A combined Superpowers design doc is split into a spec and a design. |
| R4 | The artifact size scales with the task: a few lines per section is acceptable for a small task. |
| R5 | Each PHASE 1 section in a start prompt names the spec, the design, the ADR rule and the plan, and lists them in the summary shown before the stop. |
| R6 | Approval of the plan covers the whole artifact set. After approval, each ADR's status changes from Proposed to Accepted. |
| R7 | The validator requires each of the following, and a mutation test proves each check rejects its regression: R1, R2 and R5; the four templates with their required headings; and that every `docs/adr/NNNN-*.md` has a valid `Status:`. |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes, and the new mutation cases are rejected.
- A reader of `prompts/claude-session-start.md` can see that PHASE 1 must leave four artifact types, not just a plan.
- The fresh reviewer reports no blocking findings.
- CI passes on the PR.

## Open questions

None. Two decisions were answered on 2026-10-12: spec and design are separate files, and an ADR is required only for architecture decisions.
