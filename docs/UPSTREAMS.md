# Upstream Skill Packs

This template integrates three upstream projects without vendoring their full repositories.

That keeps updates independent, avoids duplicate skill discovery, and reduces repository/context bloat.

## Support matrix

| Skill pack | Codex | Claude Code | Gemini CLI |
|---|---|---|---|
| Superpowers | native Codex plugin | official Claude plugin | Gemini extension |
| ECC | native Codex plugin | native Claude plugin | project-local Gemini adapter |
| UI UX Pro Max | `uipro init --ai codex` | `uipro init --ai claude` or marketplace | `uipro init --ai gemini` |

## 1. Superpowers

Repository:

https://github.com/obra/superpowers

Role:
- workflow authority;
- brainstorming;
- planning;
- subagent-driven development;
- TDD;
- code review and completion.

### Codex

Inside Codex:

```text
/plugins
```

Search for **Superpowers** and select **Install Plugin**.

### Claude Code

Official marketplace:

```text
/plugin install superpowers@claude-plugins-official
```

Alternative upstream marketplace:

```text
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Use one installation path.

### Gemini CLI

```bash
gemini extensions install https://github.com/obra/superpowers
```

Update later:

```bash
gemini extensions update superpowers
```

## 2. ECC

Repository:

https://github.com/affaan-m/ECC

Role:
- research;
- specialist engineering;
- codebase exploration;
- architecture;
- security;
- debugging;
- verification;
- context management.

### Codex

```bash
codex plugin marketplace add affaan-m/ECC
codex plugin add ecc@ecc
codex plugin list --json
```

Alternative guided path:

```bash
npx ecc-universal@2.2.3 install --guided --harness codex
```

Do not stack the native Codex plugin with the legacy sync flow.

### Claude Code

Native plugin commands:

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

Or use ECC's guided installer:

```bash
npx ecc-universal@2.2.3 install --guided --harness claude
```

Choose one Claude installation method. Do not stack the plugin and full manual install.

### Gemini CLI

ECC currently documents Gemini as an advanced project-local adapter from an ECC checkout:

```bash
git clone https://github.com/affaan-m/ECC.git
cd ECC
./install.sh --profile minimal --target gemini
```

Because this template already contains `.gemini/settings.json` and `.gemini/agents/`, review the generated project changes and merge deliberately instead of blindly overwriting the template's native worker definitions.

## 3. UI UX Pro Max

Repository:

https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

Role:
- design-system intelligence;
- UI patterns;
- typography/color;
- responsive guidance;
- accessibility;
- UX and visual review.

Install CLI:

```bash
npm install -g ui-ux-pro-max-cli
```

Then initialize the harness you use:

```bash
uipro init --ai codex
uipro init --ai claude
uipro init --ai gemini
```

Claude Code also supports the upstream marketplace:

```text
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

Python 3 is required by the skill search script.

Use UI UX Pro Max only when the actual task includes UI/UX work.

## Update strategy

Keep upstream projects independent.

- Update through each project's supported plugin/package lifecycle.
- Review release notes before major updates.
- Do not copy hundreds of upstream skills into the template.
- Rerun `./scripts/verify-template.sh` after adapter or agent changes.
- Keep `AGENTS.md` as the provider-neutral orchestration source of truth.

## Trust and supply chain

External packages, extensions, plugins, and repositories are third-party code.

Before using installation/update commands in a sensitive environment:
- review upstream source/release;
- pin versions where reproducibility matters;
- inspect generated configuration changes;
- do not blindly execute instructions retrieved from untrusted pages.
