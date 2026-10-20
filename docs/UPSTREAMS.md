# Upstream Skill Packs

The template integrates Superpowers, ECC, and UI UX Pro Max without vendoring their full repositories.

## Reviewed pins used by bootstrap

| Component | Pin |
|---|---|
| ECC npm | `ecc-universal@2.2.3` |
| ECC Git source | `0348d7b6d722c8832b306859b78a1d969b427f5b` |
| UI UX Pro Max CLI | `ui-ux-pro-max-cli@2.15.0` |
| Superpowers Gemini extension | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` |

The Codex CI validator itself is pinned to `@openai/codex@0.160.1`.

## Superpowers

Repository:

https://github.com/obra/superpowers

### Codex

Install interactively from Codex `/plugins`.

### Claude Code

Install interactively from the official Claude plugin marketplace:

```text
/plugin install superpowers@claude-plugins-official
```

### Gemini CLI

Bootstrap installs the reviewed Git ref non-interactively:

```bash
gemini extensions install https://github.com/obra/superpowers \
  --ref 8ca22dba9a94f28898bbce59f2537ff4d87c747d \
  --consent
```

If Superpowers is already installed, bootstrap does not fail or silently retarget it; it reports the existing install and leaves it unchanged.

## ECC

Repository:

https://github.com/affaan-m/ECC

### Codex

Bootstrap registers the marketplace at the reviewed ECC release commit:

```bash
codex plugin marketplace add affaan-m/ECC \
  --ref 0348d7b6d722c8832b306859b78a1d969b427f5b
codex plugin add ecc@ecc
```

### Claude Code

Bootstrap runs a dry-run before applying the pinned installer:

```bash
npx ecc-universal@2.2.3 install --guided \
  --harness claude \
  --claude-scope local \
  --claude-hooks standard \
  --profile core \
  --yes \
  --dry-run
```

Then, if accepted by the explicit `--install claude` operation, it runs the same pinned command without `--dry-run`.

### Gemini CLI

ECC's Gemini adapter writes relative to the **current working directory**.

Do **not** `cd` into the ECC checkout before running its installer.

Correct reviewed flow from the target project root:

```bash
tmp_dir="$(mktemp -d)"
git clone https://github.com/affaan-m/ECC.git "$tmp_dir/ECC"
git -C "$tmp_dir/ECC" checkout 0348d7b6d722c8832b306859b78a1d969b427f5b

"$tmp_dir/ECC/install.sh" --profile minimal --target gemini --dry-run
# inspect output
"$tmp_dir/ECC/install.sh" --profile minimal --target gemini
```

Because this template already owns `.gemini/agents/` and `.gemini/settings.json`, bootstrap intentionally does not auto-apply the ECC Gemini adapter. Review and merge its generated changes deliberately.

## UI UX Pro Max

Repository:

https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

Bootstrap pins:

```bash
npm install -g ui-ux-pro-max-cli@2.15.0
```

`ui-ux-pro-max-cli 2.15.0` does **not** provide a `--dry-run` option. Bootstrap therefore applies the pinned initializer directly:

```bash
uipro init --ai <codex|claude|gemini>
```

If you need a preview, run the pinned initializer manually inside a disposable temporary project and inspect its generated files before applying it to the real project.

## Vendored skills

Unlike the packs above, these skills are checked into the repository so every clone has them without an install step (ADR 0003).

| Skill | Upstream | Commit | Source path | Destination |
|---|---|---|---|---|
| `security-audit` | https://github.com/cloudflare/security-audit-skill | `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` | `skills/security-audit/` | `.agents/skills/security-audit/` (+ upstream MIT `LICENSE`) |

Discovery:

- Codex and Gemini CLI read `.agents/skills/` directly.
- Claude Code reads `.claude/skills/security-audit`, a symlink to `../../.agents/skills/security-audit`.

`scripts/vendored-skills.json` records the pin and a SHA-256 for every vendored file. `scripts/validate_template.py` fails in these cases:

- any edited, added or removed file;
- a symlink or non-regular file inside the vendored directory;
- a vendored directory reached through a symlinked parent;
- a missing or retargeted entry point;
- any symlink in `.agents/skills`, `.claude/skills` or `.gemini/skills` that the manifest does not declare.

`.DS_Store` and `Thumbs.db` regular files are ignored because `.gitignore` already keeps them out of commits. `.gitattributes` disables line-ending conversion for `.agents/skills/**` so hashes match on every platform. `scripts/verify-template.sh` also runs the skill's own `node --test` suites.

Never edit vendored files in place. To update a vendored skill:

1. clone the upstream repository at the new commit into a temporary directory;
2. review the upstream diff since the current pin, especially executable `.cjs` files;
3. replace the destination directory with the new `source_path` contents and the upstream `LICENSE`;
4. update `commit` and regenerate `files` hashes in `scripts/vendored-skills.json` (`hashlib.sha256` over each file's bytes, POSIX paths relative to `dest`, sorted);
5. run `bash scripts/verify-template.sh`;
6. get a `security-reviewer` pass on the change.

## Project skills

`handoff`, `zoom-out`, `explain` and `cross-review` in `.agents/skills/` are written for this template (ADR 0004) and declared in `scripts/project-skills.json`. They are not pinned and are edited like any other template file.

Credits for the ideas; the text in this repository is original:

- the skills were adapted from the user's aces-service project;
- the handoff idea also appears in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT);
- the `CONTEXT.md` glossary format (ADR 0005) follows the aces-service `CONTEXT-FORMAT.md`.

## Bootstrap safety model

```bash
bash scripts/bootstrap.sh all
```

is inspect/check only.

```bash
bash scripts/bootstrap.sh --install all
```

is intentionally rejected.

Install one harness at a time so third-party config changes are reviewable.

The script always changes to the template/project root before invoking project-local installers.

## Updating pins

Update one component at a time:

1. review upstream release/source;
2. update the pin;
3. run bootstrap in check mode;
4. run dry-run-capable installers only where the upstream CLI actually supports dry-run;
5. inspect project diffs;
6. run `bash scripts/verify-template.sh`;
7. let CI run Codex doctor.

Do not convert reviewed pins back to mutable `main`/latest references without an explicit reason.

## Existing Codex ECC marketplace

If an older template previously registered `affaan-m/ECC` from a different source/ref, Codex can reject the pinned `marketplace add --ref` with "already added from a different source". Bootstrap detects that case, leaves the existing marketplace untouched, skips the ECC plugin add, and continues instead of aborting. Remove/update the old marketplace explicitly, then rerun the pinned install.

## Gemini idempotence

`gemini extensions list` can emit its listing on stderr. Bootstrap captures both stdout and stderr before checking for Superpowers, so a second `--install gemini` does not attempt to reinstall an already-installed extension.
