# ADR 0002: PHASE 1 produces a spec, a design, ADRs and a plan at fixed project paths

- Status: Proposed
- Date: 2026-10-12
- Spec: [../specs/2026-10-12-phase1-artifacts-spec.md](../specs/2026-10-12-phase1-artifacts-spec.md)
- Design: [../designs/2026-10-12-phase1-artifacts-design.md](../designs/2026-10-12-phase1-artifacts-design.md)

## Context

The planning gate (ADR 0001) stops sessions before writing code, but the only artifact it requires is a plan. A real session confirmed this: it left a plan and no spec, design or ADR.

The location of the Superpowers skill output depends on the skill's version, and Superpowers produces one combined design doc. Harnesses without Superpowers have no artifact convention at all.

## Decision

- PHASE 1 of every non-trivial writing task leaves these artifacts, built from the templates in `docs/templates/`:
  - `docs/specs/YYYY-MM-DD-<topic>-spec.md` (what and why);
  - `docs/designs/YYYY-MM-DD-<topic>-design.md` (how);
  - `docs/plans/YYYY-MM-DD-<topic>.md`.
- An ADR at `docs/adr/NNNN-<title>.md` is required only when the task makes an architecture decision. That covers:
  - a new dependency or major upgrade;
  - a data model or schema;
  - a public interface or API;
  - a cross-cutting pattern or convention;
  - infrastructure, deployment or a security boundary;
  - any other choice that is expensive to reverse.
- Project paths override skill defaults. A combined skill design doc is split into the spec and the design.
- Plan approval covers the whole set. ADRs are written as Proposed and become Accepted after approval.

## Alternatives considered

- A single combined spec/design file. Rejected: the user chose separate review of what/why and of how.
- An ADR for every non-trivial task. Rejected: it produces ceremonial ADRs.
- Superpowers default locations. Rejected: they depend on the skill version, they combine the documents, and they do not apply on harnesses without Superpowers.

## Consequences

- PHASE 1 output can be reviewed in a predictable place, and the validator checks its structure.
- Small non-trivial tasks carry more paperwork. The templates allow short sections.
- Superpowers output may need splitting or moving. AGENTS.md states this explicitly.
