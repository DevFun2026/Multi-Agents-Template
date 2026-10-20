#!/usr/bin/env python3
from __future__ import annotations

import json
import os
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
        # Keep symlinks as links so the vendored-skill entry point is checked as shipped.
        symlinks=True,
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


VENDORED_SKILL = ".agents/skills/security-audit"
CLAUDE_SKILL_ENTRY = ".claude/skills/security-audit"
VENDORED_MANIFEST = "scripts/vendored-skills.json"


def replace_with_symlink(path: Path, target: str) -> None:
    path.unlink()
    path.symlink_to(target)


def flatten_claude_skill_entry(root: Path) -> None:
    entry = root / CLAUDE_SKILL_ENTRY
    entry.unlink()
    shutil.copytree(root / VENDORED_SKILL, entry)


def mutate_vendored_manifest(root: Path, fn: Callable[[dict], None]) -> None:
    path = root / VENDORED_MANIFEST
    manifest = json.loads(path.read_text(encoding="utf-8"))
    fn(manifest["skills"][0])
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def symlink_dest_parent(root: Path) -> None:
    skills = root / ".agents/skills"
    outside = root / "outside-skills"
    skills.rename(outside)
    skills.symlink_to("../outside-skills")


def plant_fifo(root: Path) -> None:
    os.mkfifo(root / VENDORED_SKILL / "pipe")


def plant_junk_dir_payload(root: Path) -> None:
    junk = root / VENDORED_SKILL / ".DS_Store"
    junk.mkdir()
    (junk / "payload.md").write_text("payload\n", encoding="utf-8")


PROJECT_SKILL = ".agents/skills/handoff"
PROJECT_MANIFEST = "scripts/project-skills.json"


def drop_project_skill(root: Path, name: str) -> None:
    path = root / PROJECT_MANIFEST
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["skills"] = [s for s in manifest["skills"] if s["name"] != name]
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def symlink_project_skill_dir(root: Path) -> None:
    skill = root / PROJECT_SKILL
    skill.rename(root / "outside-handoff")
    skill.symlink_to("../../outside-handoff")


def write_session_artifact(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def corrupt_first_hash(skill: dict) -> None:
    first = sorted(skill["files"])[0]
    skill["files"][first] = "0" * 64


def move_phase_2_before_phase_1(text: str) -> str:
    phase_1 = text.index("PHASE 1 —")
    phase_2 = text.index("PHASE 2 —")
    block_end = text.index("```", phase_2)
    block = text[phase_2:block_end].rstrip("\n") + "\n\n"
    text = text[:phase_2] + text[block_end:]
    return text[:phase_1] + block + text[phase_1:]


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
        "AGENTS.md planning gate section is required",
        lambda root: mutate_text(
            root,
            "AGENTS.md",
            lambda s: s.replace(". Planning gate", ". Planning notes"),
        ),
    ),
    (
        "AGENTS.md planning gate must stop for approval",
        lambda root: mutate_text(
            root,
            "AGENTS.md",
            lambda s: s.replace("STOP and wait for explicit user approval", "Continue"),
        ),
    ),
    (
        "start prompt without an approval stop is rejected",
        lambda root: mutate_text(
            root,
            "prompts/claude-session-start.md",
            lambda s: s.replace("STOP and wait for explicit user approval", "Continue"),
        ),
    ),
    (
        "start prompt with PHASE headings swapped is rejected",
        lambda root: mutate_text(
            root,
            "prompts/session-start.md",
            lambda s: s.replace("PHASE 1", "PHASE X").replace("PHASE 2", "PHASE 1").replace("PHASE X", "PHASE 2"),
        ),
    ),
    (
        "start prompt with the PHASE 2 block above PHASE 1 is rejected",
        lambda root: mutate_text(root, "prompts/session-start.md", move_phase_2_before_phase_1),
    ),
    (
        "start prompt must name the writing-plans skill",
        lambda root: mutate_text(
            root,
            "prompts/gemini-session-start.md",
            lambda s: s.replace("writing-plans", "planning"),
        ),
    ),
    (
        "PHASE 2 heading must wait for approval",
        lambda root: mutate_text(
            root,
            "prompts/codex-session-start.md",
            lambda s: s.replace(" (only after I approve the plan)", ""),
        ),
    ),
    (
        "PHASE 1 heading must forbid edits",
        lambda root: mutate_text(
            root,
            "prompts/claude-session-start.md",
            lambda s: s.replace("(no file edits except the PHASE 1 artifacts, no implementer)", "(edit as needed)"),
        ),
    ),
    (
        "approval stop outside PHASE 1 is rejected",
        lambda root: mutate_text(
            root,
            "prompts/claude-session-start.md",
            lambda s: s.replace("then STOP and wait for explicit user approval", "then continue").replace(
                "OBJECTIVE:", "STOP and wait for explicit user approval.\n\nOBJECTIVE:"
            ),
        ),
    ),
    (
        "harness adapter must reference the planning gate",
        lambda root: mutate_text(
            root,
            "GEMINI.md",
            lambda s: s.replace("planning gate", "workflow"),
        ),
    ),
    (
        "codex developer_instructions must reference the planning gate",
        lambda root: mutate_text(
            root,
            ".codex/config.toml",
            lambda s: s.replace("planning gate", "workflow"),
        ),
    ),
    (
        "stale planning gate section number is rejected",
        lambda root: mutate_text(
            root,
            "CLAUDE.md",
            lambda s: s.replace("planning gate (section 9)", "planning gate (section 10)"),
        ),
    ),
    (
        "AGENTS.md must define the docs/adr/ artifact path",
        lambda root: mutate_text(root, "AGENTS.md", lambda s: s.replace("docs/adr/", "docs/decisions/")),
    ),
    (
        "AGENTS.md must state when an ADR is required",
        lambda root: mutate_text(root, "AGENTS.md", lambda s: s.replace("An ADR is required", "An ADR may help")),
    ),
    (
        "PHASE 1 must name the design artifact",
        lambda root: mutate_text(
            root, "prompts/claude-session-start.md", lambda s: s.replace("docs/designs/", "docs/")
        ),
    ),
    (
        "PHASE 1 must name the ADR artifact",
        lambda root: mutate_text(
            root, "prompts/gemini-session-start.md", lambda s: s.replace("docs/adr/", "docs/")
        ),
    ),
    (
        "artifact template is required",
        lambda root: (root / "docs/templates/design.md").unlink(),
    ),
    (
        "artifact template must keep its required headings",
        lambda root: mutate_text(
            root, "docs/templates/spec.md", lambda s: s.replace("## Acceptance criteria", "## Done")
        ),
    ),
    (
        "ADR must have a valid status",
        lambda root: mutate_text(
            root, "docs/adr/0001-mandatory-planning-gate.md", lambda s: s.replace("- Status: Accepted", "- Status: Maybe")
        ),
    ),
    (
        "ADR numbers must be unique",
        lambda root: shutil.copy(
            root / "docs/adr/0002-phase1-artifact-set.md", root / "docs/adr/0002-duplicate.md"
        ),
    ),
    (
        "misnamed ADR file is rejected",
        lambda root: shutil.copy(
            root / "docs/adr/0002-phase1-artifact-set.md", root / "docs/adr/0003_misnamed.md"
        ),
    ),
    (
        "unedited ADR template status is rejected",
        lambda root: mutate_text(
            root,
            "docs/adr/0001-mandatory-planning-gate.md",
            lambda s: s.replace("- Status: Accepted", "- Status: Proposed | Accepted | Rejected"),
        ),
    ),
    (
        "PHASE 2 must accept the task's ADRs",
        lambda root: mutate_text(
            root,
            "prompts/codex-session-start.md",
            lambda s: s.replace("First set the task's ADRs to Status: Accepted and its spec, design and plan to Status: Approved. ", ""),
        ),
    ),

    (
        "text files require final newline",
        lambda root: (root / "AGENTS.md").write_text(
            (root / "AGENTS.md").read_text(encoding="utf-8").rstrip("\n"),
            encoding="utf-8",
        ),
    ),
    (
        "vendored file edited",
        lambda root: mutate_text(root, f"{VENDORED_SKILL}/SKILL.md", lambda s: s + "\n"),
    ),
    (
        "vendored extra file",
        lambda root: (root / VENDORED_SKILL / "EXTRA.md").write_text("extra\n", encoding="utf-8"),
    ),
    (
        "vendored file removed",
        lambda root: (root / VENDORED_SKILL / "HUNTING.md").unlink(),
    ),
    (
        "vendored symlink inside dest",
        lambda root: replace_with_symlink(root / VENDORED_SKILL / "ATTACK-CLASSES.md", "/etc/hosts"),
    ),
    (
        "claude skill entry flattened into a directory",
        flatten_claude_skill_entry,
    ),
    (
        "claude skill entry retargeted",
        lambda root: replace_with_symlink(root / CLAUDE_SKILL_ENTRY, "../../docs"),
    ),
    (
        "vendored manifest hash corrupted",
        lambda root: mutate_vendored_manifest(root, corrupt_first_hash),
    ),
    (
        "vendored manifest commit malformed",
        lambda root: mutate_vendored_manifest(root, lambda skill: skill.update(commit="main")),
    ),
    (
        "vendored manifest path traversal",
        lambda root: mutate_vendored_manifest(
            root, lambda skill: skill["files"].update({"../README.md": "0" * 64})
        ),
    ),
    (
        "vendored manifest required",
        lambda root: (root / VENDORED_MANIFEST).unlink(),
    ),
    (
        "vendored dest replaced by a symlink",
        lambda root: (
            (root / VENDORED_SKILL).rename(root / "outside-skill"),
            (root / VENDORED_SKILL).symlink_to("../../outside-skill"),
        ),
    ),
    (
        "vendored dest behind a symlinked parent",
        symlink_dest_parent,
    ),
    (
        "vendored directory symlink inside dest",
        lambda root: (root / VENDORED_SKILL / "linked-dir").symlink_to("../../../docs"),
    ),
    (
        "vendored FIFO inside dest",
        plant_fifo,
    ),
    (
        "vendored junk-named directory hides a payload",
        plant_junk_dir_payload,
    ),
    (
        "vendored manifest entry_points required",
        lambda root: mutate_vendored_manifest(root, lambda skill: skill.pop("entry_points")),
    ),
    (
        "vendored manifest root must be an object",
        lambda root: (root / VENDORED_MANIFEST).write_text("[]\n", encoding="utf-8"),
    ),
    (
        "undeclared symlink in a skill root",
        lambda root: (root / ".claude/skills/other").symlink_to("/etc"),
    ),
    (
        "project skill missing disable-model-invocation",
        lambda root: mutate_text(
            root, f"{PROJECT_SKILL}/SKILL.md", lambda s: s.replace("disable-model-invocation: true\n", "")
        ),
    ),
    (
        "project skill invocation flag is a string",
        lambda root: mutate_text(
            root,
            f"{PROJECT_SKILL}/SKILL.md",
            lambda s: s.replace("disable-model-invocation: true", 'disable-model-invocation: "true"'),
        ),
    ),
    (
        "project skill implicit invocation allowed",
        lambda root: mutate_text(
            root, f"{PROJECT_SKILL}/agents/openai.yaml", lambda s: s.replace("false", "true")
        ),
    ),
    (
        "project skill openai.yaml missing",
        lambda root: (root / PROJECT_SKILL / "agents/openai.yaml").unlink(),
    ),
    (
        "project skill name mismatch",
        lambda root: mutate_text(
            root, f"{PROJECT_SKILL}/SKILL.md", lambda s: s.replace("name: handoff", "name: hand-off")
        ),
    ),
    (
        "project skill entry retargeted",
        lambda root: replace_with_symlink(root / ".claude/skills/handoff", "../../.agents/skills/zoom-out"),
    ),
    (
        "project skill dir is a symlink",
        symlink_project_skill_dir,
    ),
    (
        "undeclared project skill symlink",
        lambda root: drop_project_skill(root, "explain"),
    ),
    (
        "CONTEXT.md required",
        lambda root: (root / "CONTEXT.md").unlink(),
    ),
    (
        "CONTEXT.md needs Language section",
        lambda root: mutate_text(root, "CONTEXT.md", lambda s: s.replace("## Language", "## Terms")),
    ),
    (
        "context template required",
        lambda root: (root / "docs/templates/context.md").unlink(),
    ),
    (
        "handoff leaks AWS key",
        lambda root: write_session_artifact(
            root, "docs/handoffs/2026-10-20-120000-x.md", "# Handoff\n\nkey AKIAABCDEFGHIJKLMNOP\n"
        ),
    ),
    (
        "review leaks private key",
        lambda root: write_session_artifact(
            root,
            "docs/reviews/2026-10-20-120000-x-cross-review.md",
            "# Review\n\n-----BEGIN RSA PRIVATE KEY-----\n",
        ),
    ),
    (
        "handoff file name unsafe",
        lambda root: write_session_artifact(root, "docs/handoffs/notes.md", "# Notes\n"),
    ),
]

# Vendored-skill cases must fail for their own rule, not an incidental error.
expected_messages: dict[str, str] = {
    "vendored file edited": "does not match the pinned SHA-256",
    "vendored extra file": "unexpected file",
    "vendored file removed": "missing file",
    "vendored symlink inside dest": "must not be a symlink",
    "claude skill entry flattened into a directory": "must be a symlink to",
    "claude skill entry retargeted": "must point to",
    "vendored manifest hash corrupted": "does not match the pinned SHA-256",
    "vendored manifest commit malformed": "full 40-hex commit",
    "vendored manifest path traversal": "unsafe file path",
    "vendored manifest required": "vendored-skills.json",
    "vendored dest replaced by a symlink": "must be a real directory",
    "vendored dest behind a symlinked parent": "symlinked parent",
    "vendored directory symlink inside dest": "must not be a symlink",
    "vendored FIFO inside dest": "must be a regular file",
    "vendored junk-named directory hides a payload": "unexpected file",
    "vendored manifest entry_points required": "'entry_points' must be a non-empty object",
    "vendored manifest root must be an object": "JSON root must be an object",
    "undeclared symlink in a skill root": "undeclared symlink",
    "project skill missing disable-model-invocation": "disable-model-invocation: true",
    "project skill invocation flag is a string": "disable-model-invocation: true",
    "project skill implicit invocation allowed": "allow_implicit_invocation: false",
    "project skill openai.yaml missing": "agents/openai.yaml",
    "project skill name mismatch": "name must match",
    "project skill entry retargeted": "must point to",
    "project skill dir is a symlink": "must be a real directory",
    "undeclared project skill symlink": "undeclared symlink",
    "CONTEXT.md required": "CONTEXT.md",
    "CONTEXT.md needs Language section": "## Language",
    "context template required": "docs/templates/context.md",
    "handoff leaks AWS key": "possible secret",
    "review leaks private key": "possible secret",
    "handoff file name unsafe": "file name must match",
}
assert set(expected_messages) <= {name for name, _ in cases}, "expected_messages names an unknown case"


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
    (
        "OS junk files inside the vendored skill are ignored",
        lambda root: (root / VENDORED_SKILL / ".DS_Store").write_bytes(b"\x00junk"),
    ),
    (
        "handoff with short sk- text and a gate section reference",
        lambda root: write_session_artifact(
            root,
            "docs/handoffs/2026-10-20-120000-session.md",
            "# Handoff\n\nUses sk-learn; see the planning gate (section 3) of an older policy.\n",
        ),
    ),
    (
        "well-named cross-review report",
        lambda root: write_session_artifact(
            root, "docs/reviews/2026-10-20-120000-plan-cross-review.md", "# Cross-review: plan\n"
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

        expected = expected_messages.get(name)
        if expected is not None and expected not in result.stdout:
            print(f"[fail] mutation rejected for the wrong reason: {name} (expected {expected!r})")
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
