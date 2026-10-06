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

Before writing project files it previews:

```bash
uipro init --ai <codex|claude|gemini> --dry-run
```

and then applies the same harness target.

## Bootstrap safety model

```bash
./scripts/bootstrap.sh all
```

is inspect/check only.

```bash
./scripts/bootstrap.sh --install all
```

is intentionally rejected.

Install one harness at a time so third-party config changes are reviewable.

The script always changes to the template/project root before invoking project-local installers.

## Updating pins

Update one component at a time:

1. review upstream release/source;
2. update the pin;
3. run bootstrap in check mode;
4. run dry-run-capable installers;
5. inspect project diffs;
6. run `./scripts/verify-template.sh`;
7. let CI run Codex doctor.

Do not convert reviewed pins back to mutable `main`/latest references without an explicit reason.
