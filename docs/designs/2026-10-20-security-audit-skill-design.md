# Design: Vendor Cloudflare's security-audit skill for all three harnesses

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-security-audit-skill-spec.md](../specs/2026-10-20-security-audit-skill-spec.md)
- ADRs: [../adr/0003-vendor-security-audit-skill.md](../adr/0003-vendor-security-audit-skill.md)

## Overview

```text
.agents/skills/security-audit/      <- one real copy (upstream c1c8a8c + LICENSE)
   ^            ^
   |            +-- Codex  (reads .agents/skills/ natively)
   |            +-- Gemini (reads .agents/skills/ as alias of .gemini/skills/)
   |
.claude/skills/security-audit  -> ../../.agents/skills/security-audit   (symlink, Claude Code)

scripts/vendored-skills.json        <- pin + SHA-256 per file
scripts/validate_template.py        <- enforces manifest + symlink
scripts/verify-template.sh          <- also runs upstream node tests
```

Discovery paths were checked against official docs (evidence from the researcher):

- Claude Code reads `.claude/skills/<name>/` and follows a per-skill symlink (code.claude.com/docs/en/skills).
- Codex reads `.agents/skills/` from cwd up to the repo root and follows symlinks; `.codex/skills` is deprecated (Codex "build skills" docs).
- Gemini CLI reads `.gemini/skills/` or the `.agents/skills/` alias, in trusted folders only (geminicli.com/docs/cli/skills).

## Components

| Component | Responsibility / change |
|---|---|
| `.agents/skills/security-audit/**` | 20 upstream files copied byte-for-byte from `skills/security-audit/` at `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`, plus upstream root `LICENSE`. Never edited by hand. |
| `.gitattributes` | `.agents/skills/** -text` so line-ending conversion never changes vendored bytes. |
| `.claude/skills/security-audit` | Git symlink (mode 120000) to `../../.agents/skills/security-audit`. |
| `scripts/vendored-skills.json` | `{"skills": [{"name", "repo", "commit", "source_path", "dest", "entry_points": {".claude/skills/security-audit": "../../.agents/skills/security-audit"}, "files": {"<rel>": "<sha256>"}}]}`. A list, so later vendored skills reuse the format. |
| `scripts/validate_template.py` | New block: parse the manifest; require 40-hex commit and 64-hex hashes; the file set under `dest` must equal `files` exactly (no extras, symlinks inside are rejected); each SHA-256 must match; each entry point must be a symlink whose `readlink` equals the declared target and resolves to `dest`. Adds the manifest to `REQUIRED`. Vendored files are **not** added to the newline check, since upstream bytes win. |
| `scripts/test-validator-mutations.py` | `copy_repo` uses `symlinks=True` so the baseline keeps the link. New rejected cases: edit a vendored file, add an extra file, delete a file, replace the symlink with a real dir copy, retarget the symlink, corrupt a manifest hash. |
| `scripts/verify-template.sh` | `node --test .agents/skills/security-audit/*.test.cjs`, under the same rule as the existing node test: required when `REQUIRE_GEMINI_POLICY_TEST=1` (CI), otherwise warn and skip. |
| `AGENTS.md` section 12 | Short "Vendored security-audit skill" note covering R8. |
| `docs/UPSTREAMS.md` | New "Vendored skills" section: pin table, why it is vendored, update procedure (re-clone at the new ref, review the upstream diff, copy, regenerate hashes, run verify). |
| `README.md` | Line 15 becomes: upstream packs are installed separately, except the pinned `security-audit` skill vendored under `.agents/skills/`. Also lists the new paths. |
| `docs/HARNESSES.md` | One line per harness for the skill discovery path; notes Gemini's trusted-folder requirement. |

Hash regeneration is a one-off Python snippet in the update procedure, not a new script (YAGNI). The validator gives the exact mismatching file.

### Policy fit (R8)

The skill calls its coordinator the "parent" and delegates `research` (source exploration, fact verification) and `general` (broad investigation, bounded local execution) agents.

- The main session is the parent and owns the shared run files.
- `research` maps to `explorer`. `general` maps to `security-reviewer`, which has Bash but no web tools.
- Hunters and verifiers never spawn agents themselves; spawn depth stays at one.
- In guidance mode, which is the default, the skill is used as reference by the controller and `security-reviewer`.
- Full audit mode runs only on an explicit user request. The controller states a `quick` or `standard` profile, or a `budget`, before launching, because the agent count can exceed the 2–4 worker norm in section 4.
- Output goes to the skill's default `~/security-audit-skill/<repo>/run-N`, never inside this repository.

## Alternatives considered

- **Install through `bootstrap.sh` (`npx skills add` or git clone at a pin).** This matches how the other packs are installed, but the user chose vendoring. It would also need network access and the Skills CLI at bootstrap. Rejected by user choice; see ADR 0003.
- **Three real copies (`.claude/skills`, `.agents/skills`, `.gemini/skills`).** No symlinks, so it works on Windows checkouts without symlink support. But it triples the content and invites drift. Rejected, because the manifest could cover all copies but the cost is not justified.
- **Real copy in `.claude/skills`, symlink from `.agents/skills`.** This needs the same single symlink but serves only one harness natively instead of two. Rejected.
- **Git submodule.** It pins naturally, but clones need `--recursive`, it adds the whole upstream repo, and the template's tooling does not use submodules. Rejected.

## Risks

- **Supply chain.** The vendored content is prompt text plus two Node scripts. The validators use only `node:fs` and `node:path`; `child_process` appears only in the tests. All files must be reviewed in the PR diff. Mitigations: the hash manifest blocks silent edits, and `security-reviewer` reviews the change.
- **Windows without symlinks.** The Claude entry point becomes a text file, so Claude does not see the skill there. Codex and Gemini are unaffected. This is documented.
- **Gemini uncertainty.** Gemini CLI is not installed locally. Docs disagree on whether an `experimental.skills` flag is needed, and Gemini CLI is being replaced by Antigravity CLI. Gemini discovery is treated as best-effort with a manual `/skills list` check. No flag is added unless verification shows it is needed.
- **Skill intent vs policy.** The skill's full audit may launch many agents. This is mitigated by the R8 rules and the skill's own budget gate.
- **Rollback.** Delete `.agents/skills/security-audit`, the symlink, and the manifest entry, then revert the docs.

## Test strategy

- R1, R4, R5: `python3 scripts/validate_template.py`, plus `diff -r` against a fresh upstream checkout.
- R2, R5, R6: new mutation cases in `scripts/test-validator-mutations.py`.
- R7: `node --test` of the two upstream test files, through `verify-template.sh`.
- R2: manual check in Claude Code that `security-audit` is listed.
- R3: manual Codex (and Gemini, if available) skill listing.
- R8, R9: review of the doc diffs, plus a fresh `security-reviewer` pass over the whole change.
