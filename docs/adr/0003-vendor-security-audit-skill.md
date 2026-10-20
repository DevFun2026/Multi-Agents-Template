# ADR 0003: Vendor the security-audit skill at a pinned commit under `.agents/skills/`

- Status: Accepted
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-security-audit-skill-spec.md](../specs/2026-10-20-security-audit-skill-spec.md)
- Design: [../designs/2026-10-20-security-audit-skill-design.md](../designs/2026-10-20-security-audit-skill-design.md)

## Context

The template installs upstream skill packs (Superpowers, ECC, UI UX Pro Max) separately and does not vendor them (`README.md`, `docs/UPSTREAMS.md`). The user wants Cloudflare's `security-audit` skill in the project, available to Claude Code, Codex and Gemini CLI, and chose to vendor it at a pinned commit.

The three harnesses discover project skills differently:

- Claude Code reads `.claude/skills/`.
- Codex reads `.agents/skills/`.
- Gemini reads `.gemini/skills/` or the `.agents/skills/` alias.

This adds a third-party dependency and a new security-relevant convention (vendored, executable content in the repo), so it needs an ADR.

## Decision

1. Vendor `skills/security-audit/` from `https://github.com/cloudflare/security-audit-skill` at commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` byte-for-byte into `.agents/skills/security-audit/`, with the upstream MIT `LICENSE`.
2. Expose it to Claude Code through one relative symlink, `.claude/skills/security-audit` pointing to `../../.agents/skills/security-audit`.
3. Record the pin and a SHA-256 per file in `scripts/vendored-skills.json`. `scripts/validate_template.py` rejects any drift.
4. Vendored files are never edited in place. Changes come only from re-vendoring a new reviewed upstream commit.
5. This is an exception for this skill, not a change to how Superpowers, ECC or UI UX Pro Max are installed.

## Alternatives considered

- **Install with `bootstrap.sh`.** This is consistent with the other packs, but it needs network access and the Skills CLI at bootstrap time, and clones do not get the skill. The user chose vendoring.
- **One real copy per harness directory.** This avoids symlinks but triples the content and risks drift.
- **Git submodule.** It pins well, but needs recursive clones, pulls the whole upstream repo, and the template's tooling does not use submodules.

## Consequences

- Every clone gets the skill immediately, and every change to it is visible in review and blocked by CI unless the pin is updated.
- The repository now carries third-party MIT content and two executable Node scripts. Updating it is a manual, reviewed task.
- Claude Code on a Windows checkout without symlink support does not see the skill.
- `.agents/skills/` becomes the canonical place for any future cross-harness vendored skill. The manifest format already supports more than one skill.
