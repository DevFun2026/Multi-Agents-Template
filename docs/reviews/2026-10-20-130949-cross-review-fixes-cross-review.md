# Cross-review: cross-review-fixes

- Generated: 2026-10-20T06:53:45Z
- Reviewer: codex (read-only cross-review)
- Path: B (CLI run in a temporary copy)
- Plan: docs/plans/2026-10-20-cross-review-fixes.md
- Artifacts reviewed: docs/plans/2026-10-20-cross-review-fixes.md, docs/specs/2026-10-20-cross-review-fixes-spec.md, docs/designs/2026-10-20-cross-review-fixes-design.md, CONTEXT.md; ADRs: none

## Findings

- **Major — security — `docs/designs/2026-10-20-cross-review-fixes-design.md`, “Overview” and “Risks”; `docs/plans/2026-10-20-cross-review-fixes.md`, “T3 detail”:** The design adds `agy --sandbox` as a second security layer, then permits dropping it if it blocks file reads. That changes the reviewer’s security boundary, but the artifacts provide no ADR for this decision. Add an ADR or identify the exact existing ADR decision that covers the sandbox and its fallback; define the conditions for disabling it and how the resulting run remains within the approved trust boundary.

- **Major — correctness — `docs/designs/2026-10-20-cross-review-fixes-design.md`, “Overview” (R3) and “Risks”; `docs/specs/2026-10-20-cross-review-fixes-spec.md`, R3:** The proposed parser checks only simple relative Markdown links ending in `CONTEXT.md`. A map with no recognized links, or links to `CONTEXT.md` in unsupported forms, could pass without validating the context files the spec requires. Define how all context links are identified; reject unsupported or empty maps, and test multiple links, external or absolute links, and path traversal or symlink cases.

- **Minor — drift — `docs/plans/2026-10-20-cross-review-fixes.md`, “T2 detail”; `docs/specs/2026-10-20-cross-review-fixes-spec.md`, R5:** The plan says to add **Delegation** to `CONTEXT.md`, but the reviewed `CONTEXT.md` already defines **Delegation** under Roles with the specified definition and _Avoid_ term. Remove the redundant task or state what remains to change so the plan reflects the current artifact.

## Suggested next actions

- Resolve the `agy --sandbox` ADR coverage and fallback policy in the design and plan before implementation.
- Tighten R3’s map parsing rules and add tests for empty, unsupported, multiple-link, and unsafe-path cases.
- Update the plan’s T2 task to account for the existing Delegation definition.
