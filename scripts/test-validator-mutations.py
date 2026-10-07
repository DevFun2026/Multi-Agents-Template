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


def write_claude_agent(root: Path, name: str, tools: str) -> None:
    (root / f".claude/agents/{name}.md").write_text(
        f"""---
name: {name}
description: Custom helper used by the validator mutation suite.
model: haiku
tools: {tools}
disallowedTools: Agent
---

Custom helper.
""",
        encoding="utf-8",
    )


def write_gemini_agent(root: Path, name: str, tools: list[str]) -> None:
    tool_lines = "\n".join(f'  - "{tool}"' for tool in tools)
    (root / f".gemini/agents/{name}.md").write_text(
        f"""---
name: {name}
description: Custom helper used by the validator mutation suite.
kind: local
tools:
{tool_lines}
model: flash
---

Custom helper.
""",
        encoding="utf-8",
    )


GEMINI_POLICY = "examples/gemini-user-policies/reviewer-network-deny.toml"
# The pattern shipped before the fix: Gemini 0.62.0 drops it as a potential
# ReDoS (nested quantifier), so the "wrapped" rules never loaded.
DROPPED_BY_GEMINI_REGEX = (
    r"(^|[;&|]\\s*)(env\\s+)?([A-Za-z_][A-Za-z0-9_]*=[^ \\t;&|]+\\s+)*"
    r"(/[^ \\t;&|]+/)?(curl|wget)(\\s|$)"
)


def replace_first_policy_regex(root: Path, new_regex: str) -> None:
    def edit(text: str) -> str:
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith("commandRegex = "):
                lines[i] = f"commandRegex = '''{new_regex}'''\n"
                return "".join(lines)
        raise AssertionError("no commandRegex rule found in Gemini policy example")

    mutate_text(root, GEMINI_POLICY, edit)


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
                '''name = "docs"
description = "Documentation helper."
sandbox_mode = "read-only"

developer_instructions = """
Review documentation only.
"""
''',
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

    (
        "gemini wildcard tools grant local and web access",
        lambda root: write_gemini_agent(root, "helper", ["*"]),
    ),
    (
        "gemini local read cannot be combined with all MCP tools",
        lambda root: write_gemini_agent(root, "helper", ["read_file", "mcp_*"]),
    ),
    (
        "gemini local read cannot be combined with one MCP tool",
        lambda root: write_gemini_agent(root, "helper", ["read_file", "mcp_fetch_fetch"]),
    ),
    (
        "gemini shell cannot be combined with discovered tools",
        lambda root: write_gemini_agent(root, "helper", ["run_shell_command", "discovered_tool_fetch"]),
    ),
    (
        "claude local read cannot be combined with an MCP tool",
        lambda root: write_claude_agent(root, "helper", "Read, Grep, mcp__fetch__fetch"),
    ),
    (
        "claude Bash specifier cannot be combined with an MCP server",
        lambda root: write_claude_agent(root, "helper", "Bash(git diff *), mcp__fetch"),
    ),
    (
        "claude PowerShell counts as local and cannot be combined with WebFetch",
        lambda root: write_claude_agent(root, "helper", "PowerShell, WebFetch"),
    ),
    (
        "claude Monitor counts as local and cannot be combined with WebFetch",
        lambda root: write_claude_agent(root, "helper", "Monitor, WebFetch"),
    ),
    (
        "claude NotebookEdit counts as local and cannot be combined with WebSearch",
        lambda root: write_claude_agent(root, "helper", "NotebookEdit, WebSearch"),
    ),
    (
        "claude unknown future tool counts as local",
        lambda root: write_claude_agent(root, "helper", "FutureFileTool, WebFetch"),
    ),
    (
        "gemini read_mcp_resource is network-capable",
        lambda root: write_gemini_agent(root, "helper", ["read_file", "read_mcp_resource"]),
    ),
    (
        "gemini list_mcp_resources is network-capable",
        lambda root: write_gemini_agent(root, "helper", ["glob", "list_mcp_resources"]),
    ),
    (
        "gemini activate_skill counts as local",
        lambda root: write_gemini_agent(root, "helper", ["activate_skill", "web_fetch"]),
    ),
    (
        "gemini policy regex that Gemini drops as ReDoS is rejected",
        lambda root: replace_first_policy_regex(root, DROPPED_BY_GEMINI_REGEX),
    ),
    (
        "gemini policy regex with a quantified group is rejected",
        lambda root: replace_first_policy_regex(root, r'(env\s+)?(curl|wget)(\s|")'),
    ),
    (
        "gemini policy regex anchored with ^ is rejected",
        lambda root: replace_first_policy_regex(root, r'^[^\s"]*/(curl|wget)(\s|")'),
    ),
    (
        "gemini policy regex with doubled backslashes is rejected",
        lambda root: replace_first_policy_regex(root, r'[^\\s"]*/(curl|wget)(\\s|")'),
    ),
    (
        "gemini policy regex must compile",
        lambda root: replace_first_policy_regex(root, r'[^\s"*/(curl|wget'),
    ),

    (
        "text files require final newline",
        lambda root: (root / "AGENTS.md").write_text(
            (root / "AGENTS.md").read_text(encoding="utf-8").rstrip("\n"),
            encoding="utf-8",
        ),
    ),
]


# Valid custom roles that must keep passing, so the invariants are not
# satisfied by rejecting everything.
accepted_cases: list[tuple[str, Callable[[Path], None]]] = [
    (
        "web/MCP-only Gemini researcher is allowed",
        lambda root: write_gemini_agent(root, "docs-researcher", ["web_fetch", "mcp_docs_search"]),
    ),
    (
        "local-only Gemini helper is allowed",
        lambda root: write_gemini_agent(root, "lister", ["list_directory", "glob"]),
    ),
    (
        "web/MCP-only Claude researcher is allowed",
        lambda root: write_claude_agent(root, "docs-researcher", "WebFetch, mcp__docs__search"),
    ),
    (
        "Claude web researcher may keep an inert TodoWrite tool",
        lambda root: write_claude_agent(root, "docs-researcher", "WebSearch, WebFetch, TodoWrite"),
    ),
    (
        "Gemini web researcher may keep inert write_todos and get_internal_docs",
        lambda root: write_gemini_agent(root, "docs-researcher", ["web_fetch", "write_todos", "get_internal_docs"]),
    ),
    (
        "Gemini policy regex may use a doubled backslash before a quote",
        lambda root: replace_first_policy_regex(root, r'\\"(curl|wget)\\"'),
    ),
    (
        "local-only Claude helper is allowed",
        lambda root: write_claude_agent(root, "lister", "Read, Glob"),
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

    for index, (name, mutate) in enumerate(accepted_cases):
        case_root = base / f"accepted-{index}"
        copy_repo(case_root)
        mutate(case_root)
        result = run_validator(case_root)

        if result.returncode != 0:
            print(f"[fail] valid custom role unexpectedly rejected: {name}")
            print(result.stdout)
            raise SystemExit(1)

        print(f"[ok] valid custom role accepted: {name}")

print("Validator mutation tests passed.")
