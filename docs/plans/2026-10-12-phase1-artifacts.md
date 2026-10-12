# Plan: PHASE 1 artifact set (spec, design, ADR, plan)

- Status: Awaiting approval
- Date: 2026-10-12
- Spec: [../specs/2026-10-12-phase1-artifacts-spec.md](../specs/2026-10-12-phase1-artifacts-spec.md)
- Design: [../designs/2026-10-12-phase1-artifacts-design.md](../designs/2026-10-12-phase1-artifacts-design.md)
- ADRs: [../adr/0002-phase1-artifact-set.md](../adr/0002-phase1-artifact-set.md)

Note: Superpowers is not installed in the session that wrote this plan. The clarify and plan steps were done manually, as AGENTS.md section 9 requires in that case.

## Objective and success criteria

PHASE 1 must leave a spec, a design, ADRs for architecture decisions, and a plan at fixed paths, and the validator must enforce this. Success criteria are spec R1–R7 and the spec's acceptance criteria.

## Scope and non-goals

The scope and non-goals are as listed in the spec. The approval rules and the PHASE 1/PHASE 2 structure stay unchanged.

## Architecture decision

ADR 0002: fixed project paths and templates, spec and design as separate files, ADRs only for architecture decisions, and project paths overriding skill defaults. The alternatives rejected are listed in the design and in the ADR.

## Execution graph

```text
T1 validator checks + mutation tests (red)        write   main session
T2 templates docs/templates/*.md                   write   main session
T3 ADR 0001 (Accepted) + flip ADR 0002 to Accepted write   main session
T4 AGENTS.md section 9/10/16                       write   main session
T5 four start prompts                              write   main session
T6 CLAUDE.md, GEMINI.md, .codex/config.toml        write   main session
T7 README, ORCHESTRATION, SESSION-EXAMPLES, architecture.html   write   main session
T8 verify-template.sh (green) + screenshots        read    main session
T9 fresh review of the diff                        read    reviewer (Sonnet)
T10 fix findings, commit, push, PR, CI green, merge to main     write   main session
```

The tasks run serially because all of them write to the same working tree. Only the T9 review is delegated: the edits are small and coupled, so an implementer worker would cost more context than it saves.

## Tasks

| # | Files | Test |
|---|---|---|
| T1 | `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | The validator fails on the current tree and lists the missing artifacts. Each of the 8 new mutation cases is defined. |
| T2 | `docs/templates/spec.md`, `design.md`, `adr.md`, `plan.md` | The template-heading checks pass, and the "template loses heading" mutation is rejected. |
| T3 | `docs/adr/0001-mandatory-planning-gate.md`, `docs/adr/0002-phase1-artifact-set.md` | The ADR status and uniqueness checks pass. The bad-status and duplicate-number mutations are rejected. |
| T4 | `AGENTS.md` | The artifact paths, the ADR trigger marker, and the existing gate checks all pass. |
| T5 | `prompts/*.md` | PHASE 1 names spec, design, ADR and plan. The existing PHASE ordering checks still pass. |
| T6 | `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml` | The gate-pointer checks pass, and `.codex/config.toml` parses. |
| T7 | `README.md`, `docs/ORCHESTRATION.md`, `docs/SESSION-EXAMPLES.md`, `docs/architecture.html` | The section-reference check passes. Desktop and mobile screenshots of the changed sections look correct. |
| T8 | n/a | `bash scripts/verify-template.sh` passes. |
| T9 | n/a | The reviewer reports no blocking findings, or the findings are fixed. |
| T10 | git, PR | CI `verify` passes. The PR is merged into `main` with a merge commit. |

## Verification

- TDD order: T1 must be red before T2–T7, and green afterwards.
- `bash scripts/verify-template.sh` passes locally, and CI passes on the PR.
- A fresh reviewer inspects the diff against `main`.
- After the merge, the Pages build log lists the new docs.

## Risks and open questions

- The design lists the risks: Superpowers default paths, heavier PHASE 1 for small tasks, and keyword-only checks.
- There are no open questions. The spec/design split and the ADR trigger were decided by the user on 2026-10-12.
