# Plan: Vendor Cloudflare's security-audit skill for all three harnesses

- Status: Approved (2026-10-20)
- Date: 2026-10-20
- Spec: [../specs/2026-10-20-security-audit-skill-spec.md](../specs/2026-10-20-security-audit-skill-spec.md)
- Design: [../designs/2026-10-20-security-audit-skill-design.md](../designs/2026-10-20-security-audit-skill-design.md)
- ADRs: [../adr/0003-vendor-security-audit-skill.md](../adr/0003-vendor-security-audit-skill.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every clone exposes Cloudflare's `security-audit` skill to Claude Code, Codex and Gemini CLI, pinned and integrity-checked in CI.

**Architecture:** One byte-identical copy lives at `.agents/skills/security-audit/`, read natively by Codex and Gemini. Claude Code reaches it through a relative symlink. A JSON manifest pins the commit and per-file SHA-256, and `validate_template.py` enforces it.

**Tech Stack:** Python 3 (validator and mutation tests), Bash, Node 24 (`node --test`), Git symlinks.

## Global Constraints

- Upstream: `https://github.com/cloudflare/security-audit-skill`, commit `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`, source path `skills/security-audit/`.
- Destination `.agents/skills/security-audit/` holds the 20 upstream files plus `LICENSE`, with no other files.
- Claude entry point: `.claude/skills/security-audit` is a symlink whose `readlink` is exactly `../../.agents/skills/security-audit`.
- Vendored bytes are never edited, reformatted, or added to the newline check.
- No new runtime or dev dependency. The validator uses only the Python stdlib plus the existing PyYAML.
- Audit output never goes inside this repository.

## Review Focus

1. **Line-ending conversion** (`core.autocrlf=true` on Windows) rewrites vendored bytes, so hashes mismatch on a clean clone. Expected: a `.gitattributes` rule `.agents/skills/** -text` keeps the bytes exact (T1).
2. **macOS `.DS_Store` / `Thumbs.db`** inside the vendored dir on a dev machine. Expected: the validator ignores exactly these OS-junk names, which `.gitignore` already lists, and treats any other extra file as a failure. An accepted-case test covers this (T2).
3. **A symlink inside the vendored dir** pointing outside the repo. Expected: rejected even if it is listed in the manifest (T2).
4. **Manifest keys with `..` or absolute paths.** Expected: rejected before any file is opened (T2).
5. **Symlink flattened into a real directory** (`copytree` without `symlinks=True`, a zip download, or Windows). Expected: the validator reports "must be a symlink" with the path. The mutation baseline must preserve the link, or every case passes for the wrong reason (T2).

## Objective and success criteria

Spec goals 1–5 and acceptance criteria.

## Scope and non-goals

As in the spec. Scope: the vendored dir, the symlink, the manifest, the validator, mutation tests, verify script, `.gitattributes`, and docs. Non-goals: editing upstream content, auditing this repo, providing a sandbox, auto-updates, and Antigravity CLI.

## Architecture decision

Vendor at a pin into `.agents/skills/` with a Claude symlink and a hash manifest. See the design and ADR 0003. Rejected: install through bootstrap, three real copies, git submodule.

## Execution graph

```text
T0 branch + approve artifacts (controller, write)
 -> T1 vendor + manifest + symlink + .gitattributes (write)
 -> T2 validator checks, TDD via mutation tests (write)
 -> T3 run upstream node tests in verify script (write)
 -> T4 docs: AGENTS.md section 12, UPSTREAMS, README, HARNESSES (write)
 -> T5 fresh security-reviewer + reviewer (read-only, parallel) -> controller judgment
 -> T6 manual discovery checks + completion report (controller)
```

All write tasks run serially in one branch (Sonnet implementer or the controller, depending on the execution method chosen). T5 reviewers are Sonnet, read-only, and run in parallel.

## Tasks

| # | Files | Test |
|---|---|---|
| T0 | branch `feat/security-audit-skill`; set spec/design/plan `Approved`, ADR 0003 `Accepted` | `git log -1` shows the artifact commit |
| T1 | `.agents/skills/security-audit/**`, `.claude/skills/security-audit` (symlink), `scripts/vendored-skills.json`, `.gitattributes` | `diff -r` against the upstream checkout shows only `LICENSE`; `git ls-files -s` shows mode `120000` for the symlink |
| T2 | `scripts/validate_template.py`, `scripts/test-validator-mutations.py` | `python3 scripts/test-validator-mutations.py`: new cases rejected, junk-file case accepted |
| T3 | `scripts/verify-template.sh` | `bash scripts/verify-template.sh` runs both upstream tests and they pass |
| T4 | `AGENTS.md`, `docs/UPSTREAMS.md`, `README.md`, `docs/HARNESSES.md` | `validate_template.py` still passes; doc review in T5 |
| T5 | read-only | reviewer reports with no unresolved high findings |
| T6 | none | Claude lists `security-audit`; Codex/Gemini results recorded |

### Task 0: Branch and approve artifacts

- [ ] `git switch -c feat/security-audit-skill`
- [ ] Set spec, design and plan to `Status: Approved (YYYY-MM-DD)` and ADR 0003 to `Status: Accepted`.
- [ ] Commit `docs: PHASE 1 artifacts for vendoring the security-audit skill`.

### Task 1: Vendor files, manifest, symlink

**Files:** create `.agents/skills/security-audit/` (21 files), `.claude/skills/security-audit` (symlink), `scripts/vendored-skills.json`, `.gitattributes`.

**Interfaces (produces):** manifest shape used by T2:

```json
{"skills": [{
  "name": "security-audit",
  "repo": "https://github.com/cloudflare/security-audit-skill",
  "commit": "c1c8a8c1471069fb0e188eeaff69b8e8db6564a8",
  "source_path": "skills/security-audit",
  "dest": ".agents/skills/security-audit",
  "entry_points": {".claude/skills/security-audit": "../../.agents/skills/security-audit"},
  "files": {"SKILL.md": "<sha256>", "LICENSE": "<sha256>", "...": "..."}
}]}
```

`files` keys are POSIX paths relative to `dest`, sorted. The file uses 2-space indentation and a trailing newline.

- [ ] Fresh `git clone` into the scratchpad, then `git -C <clone> checkout c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` and confirm `git rev-parse HEAD` matches.
- [ ] Copy `<clone>/skills/security-audit/*` and `<clone>/LICENSE` into `.agents/skills/security-audit/`.
- [ ] `ln -s ../../.agents/skills/security-audit .claude/skills/security-audit`
- [ ] Write `.gitattributes` with `.agents/skills/** -text`.
- [ ] Generate the manifest with an inline `python3 -I` snippet (`hashlib.sha256` over each file's bytes).
- [ ] Verify: `diff -r <clone>/skills/security-audit .agents/skills/security-audit` reports only `Only in ...: LICENSE`; `cmp <clone>/LICENSE .agents/skills/security-audit/LICENSE` is silent; `python3 scripts/validate_template.py` still passes.
- [ ] Commit `feat: vendor cloudflare security-audit skill at c1c8a8c`.

### Task 2: Validator enforces the manifest (TDD)

**Files:** modify `scripts/test-validator-mutations.py` (`copy_repo`, `cases`, `accepted_cases`) and `scripts/validate_template.py` (new block before the final `if errors:`; add `"scripts/vendored-skills.json"` to `REQUIRED`).

**Interfaces:** consumes the T1 manifest. Produces `check_vendored_skills() -> None`, which appends messages to the existing `errors` through `fail()`.

- [ ] **Step 1:** In `copy_repo`, pass `symlinks=True` to `shutil.copytree`.
- [ ] **Step 2:** Add rejected cases. Each one's mutation must make the validator exit non-zero:
  - `vendored file edited`: append `"\n"` to `.agents/skills/security-audit/SKILL.md`.
  - `vendored extra file`: write `.agents/skills/security-audit/EXTRA.md`.
  - `vendored file removed`: unlink `.agents/skills/security-audit/HUNTING.md`.
  - `vendored symlink inside dest`: replace `ATTACK-CLASSES.md` with a symlink to `/etc/hosts`.
  - `claude entry flattened`: replace the `.claude/skills/security-audit` symlink with a `copytree` of the target.
  - `claude entry retargeted`: re-point the symlink to `../../docs`.
  - `manifest hash corrupted`: change one hash in `scripts/vendored-skills.json` to `"0" * 64`.
  - `manifest commit malformed`: set `commit` to `"main"`.
  - `manifest path traversal`: add the key `"../README.md"` to `files`.
- [ ] **Step 3:** Add accepted case `vendored dir with OS junk`: write `.agents/skills/security-audit/.DS_Store`.
- [ ] **Step 4:** Run `python3 scripts/test-validator-mutations.py`. Expected: FAIL with `mutation unexpectedly passed: vendored file edited`.
- [ ] **Step 5:** Implement `check_vendored_skills()`:
  - Load the manifest with `parse_json`.
  - Require `commit` to match `^[0-9a-f]{40}$` and each hash to match `^[0-9a-f]{64}$`.
  - Reject `files` keys that are absolute or contain a `..` part.
  - Walk `dest` with `os.walk(followlinks=False)`. Fail on any symlink (file or dir). Ignore only the names `.DS_Store` and `Thumbs.db`.
  - Require the found set to equal the key set, and report missing and extra files by name.
  - Compare SHA-256 values.
  - For each entry point, require `Path.is_symlink()`, `os.readlink == target`, and that the resolved path equals `(ROOT / dest).resolve()`.
  - Call it at module level, next to the other checks.
- [ ] **Step 6:** Run `python3 scripts/validate_template.py && python3 scripts/test-validator-mutations.py`. Expected: all `[ok]`, ending with `Validator mutation tests passed.`
- [ ] **Step 7:** Commit `feat: validator pins vendored skills by hash and symlink`.

### Task 3: Run upstream tests

**Files:** modify `scripts/verify-template.sh`.

- [ ] Inside the existing `if command -v node` branch, add `node --test .agents/skills/security-audit/validate-findings.test.cjs .agents/skills/security-audit/validate-coverage-ledger.test.cjs`. The else-branches already fail in CI (`REQUIRE_GEMINI_POLICY_TEST=1`) and warn locally. Update the warn text to mention both tests.
- [ ] Run `bash scripts/verify-template.sh`. Expected: the node test summary shows `# fail 0`, then `Template verification passed for Codex + Claude Code + Gemini CLI.` `shellcheck` stays clean.
- [ ] Commit `ci: run vendored security-audit validator tests`.

### Task 4: Documentation

**Files:** `AGENTS.md` (section 12), `docs/UPSTREAMS.md`, `README.md` (line 15 and the file list near line 229), `docs/HARNESSES.md`.

- [ ] `AGENTS.md` section 12: add a subsection "Vendored security-audit skill" with the R8 rules from the design ("Policy fit"), in at most 8 bullets.
- [ ] `docs/UPSTREAMS.md`: add a "Vendored skills" section with:
  - a pin table (repo, commit, source path, dest);
  - the reason it is vendored (user decision, ADR 0003);
  - the update procedure: clone the new ref, review the upstream diff, replace files, regenerate the manifest, run `verify-template.sh`, and run a `security-reviewer` pass.
- [ ] `README.md`: reword line 15 to state the exception, and list `.agents/skills/` and `scripts/vendored-skills.json`.
- [ ] `docs/HARNESSES.md`: add one line per harness for the skill discovery path. Note Gemini's trusted-folder requirement and that the Claude symlink needs `core.symlinks` on Windows.
- [ ] Run `bash scripts/verify-template.sh` and expect it to pass. Commit `docs: document vendored security-audit skill`.

### Task 5: Fresh review

- [ ] In parallel:
  - `security-reviewer` (Sonnet) on supply chain, the validator's symlink and path handling, and the vendored `.cjs` files;
  - `reviewer` (Sonnet) on correctness, mutation coverage, and doc accuracy.
  Both get the branch name, base `d9dc7b7` and head ref.
- [ ] The controller judges the findings, fixes any it accepts, and re-runs `verify-template.sh`.

### Task 6: Manual discovery and report

- [ ] Claude Code: start a session in the repo and confirm `security-audit` is listed.
- [ ] Codex (local `codex-cli 0.159.3`): run `codex debug prompt-input x | grep -c security-audit` and expect it to be greater than 0. Otherwise record that it was not verified.
- [ ] Gemini: not installed locally. Record as "not verified".
- [ ] Write the completion report (AGENTS.md section 16). Push and open a PR only if the user asks.

## Verification

- `bash scripts/verify-template.sh`, which covers the validator, mutation tests, upstream node tests, bootstrap test, and shellcheck.
- `diff -r` against the upstream checkout at the pin.
- `git ls-files -s .claude/skills/security-audit` shows mode `120000`.
- T5 review findings resolved.
- Spec acceptance criteria checked one by one in the completion report.

## Risks and open questions

- Gemini discovery is unverified locally, and it is unclear whether an `experimental.skills` flag is needed. No flag is added unless verification proves it necessary.
- Windows checkouts without symlink support lose the Claude entry point. This is documented, not solved.
- Open questions: none.
