# Spec: Vendor Cloudflare's security-audit skill for all three harnesses

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Design: [../designs/2026-10-20-security-audit-skill-design.md](../designs/2026-10-20-security-audit-skill-design.md)
- ADR: [../adr/0003-vendor-security-audit-skill.md](../adr/0003-vendor-security-audit-skill.md)
- Plan: [../plans/2026-10-20-security-audit-skill.md](../plans/2026-10-20-security-audit-skill.md)

## Problem

The template has a `security-reviewer` role but no structured audit methodology. The user asked to add the `security-audit` skill from <https://github.com/cloudflare/security-audit-skill>. That skill gives an agent a source-first, adversarially validated audit workflow (reconnaissance, coverage-led hunting, independent validation, schema-checked findings).

Today every upstream skill pack is installed separately, not vendored (`README.md:15`, `docs/UPSTREAMS.md`). The user chose to **vendor** this skill pinned to a reviewed commit, and to make it usable from **Claude Code, Codex and Gemini CLI**.

## Goals and success criteria

1. A clone of the repository exposes the `security-audit` skill to Claude Code, Codex and Gemini CLI without any install step.
2. The vendored files are byte-identical to upstream commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`, plus the upstream MIT `LICENSE`.
3. CI fails if any vendored file is changed, added or removed without updating the pin, or if the Claude entry point is missing.
4. Running the skill does not break project policy: depth-one orchestration, role separation, no audit output written into the repo.
5. The template's documentation reflects that this one skill is vendored and explains how to update it.

## Scope

- Vendored skill directory and its harness entry points.
- A `.gitattributes` rule keeping vendored bytes exact, a pin/integrity manifest, validator checks, mutation tests, and running the upstream validator tests in CI.
- A short integration note in `AGENTS.md` (section 12) and updates to `docs/UPSTREAMS.md`, `README.md`, and `docs/HARNESSES.md`.

## Non-goals

- Modifying the upstream skill content.
- Running a security audit of this repository.
- Providing the OS-enforced sandbox the skill asks for in order to execute target code. Without it, the skill keeps leads as `needs_validation`, as designed upstream.
- Auto-updating the pin; updates stay a manual, reviewed change.
- Supporting harnesses other than the three named, including Gemini's successor Antigravity CLI.

## Requirements

| ID | Requirement |
|---|---|
| R1 | The skill lives once at `.agents/skills/security-audit/` with all 20 upstream files from `skills/security-audit/` at the pinned commit, plus the upstream `LICENSE`. |
| R2 | Claude Code discovers it through `.claude/skills/security-audit`, a relative symlink to `../../.agents/skills/security-audit`. |
| R3 | Codex and Gemini discover it through `.agents/skills/` with no extra config. |
| R4 | A manifest records upstream repo, commit, source path, and the SHA-256 of every vendored file. |
| R5 | `scripts/validate_template.py` fails on a hash mismatch, a missing or extra file, a non-symlink or wrongly targeted Claude entry, or a malformed manifest. |
| R6 | `scripts/test-validator-mutations.py` proves each R5 check rejects a mutated copy, and the baseline copy keeps the symlink. |
| R7 | `scripts/verify-template.sh` runs the upstream `*.test.cjs` with `node --test` (required in CI, skipped with a warning locally if node is absent). |
| R8 | `AGENTS.md` states how the skill maps onto project roles and limits: the controller is the skill's parent; `research` maps to `explorer`, `general` maps to `security-reviewer`; full audit mode needs an explicit user request plus a profile or budget; output stays outside the repository. |
| R9 | `README.md` and `docs/UPSTREAMS.md` document the vendoring exception, the pin, and the update procedure. |

## Acceptance criteria

- `bash scripts/verify-template.sh` passes locally and in CI.
- `diff -r` between the vendored directory and a fresh upstream checkout at the pinned commit shows only the added `LICENSE`.
- Each new mutation case is reported `[ok] mutation rejected`.
- In Claude Code, `/security-audit` appears in the skill list from this repo.
- Codex and Gemini discovery is checked manually where those CLIs are installed. Results are recorded in the completion report, or marked "not verified" if they could not be run.

## Open questions

None.
