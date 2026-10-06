#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent.parent


def remove_yaml_field_block(text: str, key: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    prefix = f"{key}:"

    while i < len(lines):
        if lines[i].startswith(prefix):
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1

    return "\n".join(out) + "\n"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate_template.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def copy_repo(destination: Path) -> None:
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", "node_modules"),
    )


def mutate_text(root: Path, rel: str, fn: Callable[[str], str]) -> None:
    path = root / rel
    path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")


cases: list[tuple[str, Callable[[Path], None]]] = [
    (
        "codex max_depth exactness",
        lambda root: mutate_text(
            root,
            ".codex/config.toml",
            lambda s: s.replace("max_depth = 1", "max_depth = 10"),
        ),
    ),
    (
        "codex features table required",
        lambda root: mutate_text(
            root,
            ".codex/config.toml",
            lambda s: s.replace("[features]\nmulti_agent = true\n", "multi_agent = true\n"),
        ),
    ),
    (
        "gemini JSON must parse",
        lambda root: (root / ".gemini/settings.json").write_text("{ broken", encoding="utf-8"),
    ),
    (
        "claude YAML must parse",
        lambda root: mutate_text(
            root,
            ".claude/agents/explorer.md",
            lambda s: s.replace("model: haiku", "model: [broken"),
        ),
    ),
    (
        "claude tools cannot be omitted",
        lambda root: mutate_text(
            root,
            ".claude/agents/security-reviewer.md",
            lambda s: remove_yaml_field_block(s, "tools"),
        ),
    ),
    (
        "claude CSV tools are normalized before policy checks",
        lambda root: mutate_text(
            root,
            ".claude/agents/security-reviewer.md",
            lambda s: remove_yaml_field_block(s, "tools").replace(
                "model: sonnet",
                "model: sonnet\ntools: Read, Grep, Glob, Bash, WebFetch",
            ),
        ),
    ),
    (
        "gemini tools cannot be omitted",
        lambda root: mutate_text(
            root,
            ".gemini/agents/security-reviewer.md",
            lambda s: remove_yaml_field_block(s, "tools"),
        ),
    ),
    (
        "gemini researcher cannot gain shell",
        lambda root: mutate_text(
            root,
            ".gemini/agents/researcher.md",
            lambda s: s.replace("  - web_fetch", "  - web_fetch\n  - run_shell_command"),
        ),
    ),
    (
        "gemini frontmatter is strict",
        lambda root: mutate_text(
            root,
            ".gemini/agents/explorer.md",
            lambda s: s.replace("kind: local", "kind: local\nunknown_key: true"),
        ),
    ),
    (
        "gemini tool names are validated",
        lambda root: mutate_text(
            root,
            ".gemini/agents/explorer.md",
            lambda s: s.replace("  - grep_search", "  - grep_search\n  - definitely_not_a_tool"),
        ),
    ),

    (
        "claude role name must match filename and mixed local/web is rejected",
        lambda root: mutate_text(
            root,
            ".claude/agents/security-reviewer.md",
            lambda s: s.replace(
                "name: security-reviewer",
                "name: sec-review",
            ).replace(
                "  - Bash",
                "  - Bash\n  - WebFetch",
            ),
        ),
    ),
    (
        "new Claude helper cannot mix local-read and web tools",
        lambda root: (root / ".claude/agents/helper.md").write_text(
            """---
name: helper
description: Mixed-capability helper that must be rejected.
model: haiku
tools:
  - Read
  - Grep
  - WebFetch
disallowedTools: Agent
---

This helper intentionally violates the local/web separation invariant.
""",
            encoding="utf-8",
        ),
    ),
    (
        "new Gemini helper cannot mix local-read and web tools",
        lambda root: (root / ".gemini/agents/helper.md").write_text(
            """---
name: helper
description: Mixed-capability helper that must be rejected.
kind: local
tools:
  - read_file
  - web_fetch
model: flash
---

This helper intentionally violates the local/web separation invariant.
""",
            encoding="utf-8",
        ),
    ),
    (
        "new Codex role must declare web_search explicitly",
        lambda root: (
            (root / ".codex/agents/docs.toml").write_text(
                """name = "docs"
description = "Documentation helper."
sandbox_mode = "read-only"

developer_instructions = """
Review documentation only.
"""
""",
                encoding="utf-8",
            ),
            mutate_text(
                root,
                ".codex/config.toml",
                lambda s: s
                + """
[agents.docs]
description = "Documentation helper."
config_file = "agents/docs.toml"
""",
            ),
        ),
    ),
]


with tempfile.TemporaryDirectory(prefix="multi-agents-validator-") as tmp:
    base = Path(tmp)

    baseline = base / "baseline"
    copy_repo(baseline)
    result = run_validator(baseline)
    if result.returncode != 0:
        print("[fail] baseline validator failed")
        print(result.stdout)
        raise SystemExit(1)

    for index, (name, mutate) in enumerate(cases):
        case_root = base / f"case-{index}"
        copy_repo(case_root)
        mutate(case_root)
        result = run_validator(case_root)

        if result.returncode == 0:
            print(f"[fail] mutation unexpectedly passed: {name}")
            print(result.stdout)
            raise SystemExit(1)

        print(f"[ok] mutation rejected: {name}")

print("Validator mutation tests passed.")
