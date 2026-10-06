# Upstream Skill Packs

This template integrates three upstream projects without copying their repositories into this one.

That keeps updates independent, avoids duplicated skill discovery, and reduces repository/context bloat.

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

### Codex installation

Current Superpowers documentation recommends installing through the Codex plugin interface:

```text
/plugins
```

Search for **Superpowers**, then select **Install Plugin**.

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

### Native Codex plugin

```bash
codex plugin marketplace add affaan-m/ECC
codex plugin add ecc@ecc
codex plugin list --json
```

Alternative guided installation:

```bash
npx ecc-universal@2.2.3 install --guided --harness codex
```

Choose one ECC installation method for Codex. Do not stack the native plugin and legacy sync installation.

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

### Codex installation

```bash
npm install -g ui-ux-pro-max-cli
uipro init --ai codex
```

Python 3 is required by the skill's search script.

Use this skill only when the actual task includes UI/UX work.

## Update strategy

Keep upstream projects independent.

Suggested maintenance:
- update plugins through their supported plugin/package lifecycle;
- review upstream release notes before major updates;
- rerun `./scripts/verify-template.sh` after changing local orchestration files;
- do not copy all upstream skill files into this repository unless you intentionally fork and maintain them.

## Trust and supply chain

External packages and repositories are third-party code.

Before using update/install commands in a sensitive environment:
- review the upstream repository/release;
- pin versions where reproducibility matters;
- inspect changes before updating;
- do not blindly execute installation snippets retrieved from untrusted pages.
