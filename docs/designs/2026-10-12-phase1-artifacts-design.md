# Design: PHASE 1 artifact set

- Status: Draft (awaiting approval)
- Date: 2026-10-12
- Spec: [../specs/2026-10-12-phase1-artifacts-spec.md](../specs/2026-10-12-phase1-artifacts-spec.md)
- ADRs: [../adr/0002-phase1-artifact-set.md](../adr/0002-phase1-artifact-set.md)

## Overview

The planning gate in `AGENTS.md` section 9 gains an explicit artifact contract. PHASE 1 runs in this order:

```text
brainstorming (clarify with the user)
  -> spec      docs/specs/YYYY-MM-DD-<topic>-spec.md        what / why
  -> read-only investigation (explorer / researcher)
  -> design    docs/designs/YYYY-MM-DD-<topic>-design.md    how
  -> ADRs      docs/adr/NNNN-<title>.md  (Status: Proposed)  one per architecture decision
  -> writing-plans
  -> plan      docs/plans/YYYY-MM-DD-<topic>.md              tasks, links to all of the above
  -> STOP: approval covers the set; ADRs become Accepted after approval
```

## Components

| Component | Change |
|---|---|
| `AGENTS.md` section 9 | Adds a "PHASE 1 artifacts" subsection covering the table of artifacts, paths, templates and contents; the ADR-required triggers; the rule that project paths override skill defaults (split a combined Superpowers design doc); size scaling; and the ADR status flip on approval. The existing plan checklist moves into the plan template, and section 9 points to it. |
| `AGENTS.md` sections 10 and 16 | The workflow diagram shows spec, design, ADR and plan. The completion report lists the artifact paths. |
| Start prompts | PHASE 1 has five steps: (1) brainstorming → spec; (2) read-only evidence; (3) design plus ADRs for architecture decisions; (4) writing-plans → plan linking the others; (5) summary listing every artifact path, then the STOP marker. The heading becomes `PHASE 1 — CLARIFY AND PLAN (no file edits except the PHASE 1 artifacts, no implementer)`. |
| `docs/templates/` | New files `spec.md`, `design.md`, `adr.md` and `plan.md`. Each has the required headings. The templates avoid `{{ }}` so Jekyll on Pages renders them safely. |
| `docs/adr/` | `0001-mandatory-planning-gate.md` (Accepted; records the merged change) and `0002-phase1-artifact-set.md` (Proposed; becomes Accepted when this plan is approved). |
| Adapters | One sentence each in `CLAUDE.md` and `GEMINI.md`, and in Codex `developer_instructions`: "PHASE 1 leaves a spec, a design, ADRs for architecture decisions, and a plan." |
| `scripts/validate_template.py` | New checks, listed below. |
| Docs | README (start prompts and validation list), ORCHESTRATION (planning gate), SESSION-EXAMPLES (examples 2 and 3), and the `architecture.html` gate card and pipeline step 05. |

## Validator design

The new checks are:

- **AGENTS.md:**
  - mentions `docs/specs/`, `docs/designs/`, `docs/adr/`, `docs/plans/` and `docs/templates/`;
  - contains the ADR trigger sentence marker `An ADR is required`.
- **Each start prompt:** the text between the PHASE 1 heading and the PHASE 2 heading contains `spec`, `design`, `ADR` and `plan` as words.
- **Templates:** `docs/templates/{spec,design,adr,plan}.md` are added to `REQUIRED`, and each must contain its required `## ` headings:
  - spec: `Problem`, `Goals and success criteria`, `Scope`, `Non-goals`, `Requirements`, `Acceptance criteria`, `Open questions`;
  - design: `Overview`, `Components`, `Alternatives considered`, `Risks`, `Test strategy`;
  - ADR: `Context`, `Decision`, `Alternatives considered`, `Consequences`;
  - plan: `Objective and success criteria`, `Scope and non-goals`, `Architecture decision`, `Execution graph`, `Tasks`, `Verification`, `Risks and open questions`.
- **ADR files:** every `docs/adr/[0-9][0-9][0-9][0-9]-*.md` has a `- Status:` line whose value starts with `Proposed`, `Accepted`, `Deprecated`, `Superseded` or `Rejected`. ADR numbers are unique.

Mutation cases, one per check:

- AGENTS.md drops the `docs/adr/` path;
- AGENTS.md drops the ADR trigger;
- a prompt drops `design` from PHASE 1;
- a prompt drops `ADR` from PHASE 1;
- a template is deleted;
- a template loses a required heading;
- an ADR has a bad status;
- two ADRs share a number.

## Alternatives considered

- **One combined design/spec file.** Rejected by user decision. Separate files keep the what/why review apart from the how review.
- **ADR for every non-trivial task.** Rejected by user decision. It produces empty, ceremonial ADRs.
- **Keep the Superpowers default paths** (`docs/superpowers/...`). Rejected. The paths depend on the Superpowers version, Superpowers produces one combined doc, and harnesses without Superpowers would write elsewhere. Fixed project paths are stable and can be validated.
- **Enforce artifacts with a pre-implementer hook.** Rejected for now. It is harness-specific (Claude only) and outside this change's scope.

## Risks

- Superpowers `brainstorming` may still write its own combined doc at its default path. Mitigation: AGENTS.md states that project paths override skill defaults, and that a combined doc is split into a spec and a design.
- The process is heavier for small, non-trivial tasks. Mitigation: R4 allows a few lines per section, and trivial tasks remain exempt.
- The keyword checks are presence checks only. A prompt could mention "design" without requiring it. This is acceptable for a template validator, and the fresh review covers the wording.

## Test strategy

TDD:

1. Add the validator checks and mutation cases first.
2. Confirm the validator fails on the current tree (red).
3. Change the policy, prompts, templates and ADRs until it passes (green).
4. Run `verify-template.sh`, a fresh reviewer, and CI.
