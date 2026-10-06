#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required for template validation. "
        "Install dev requirements with: python3 -m pip install -r requirements-dev.txt"
    ) from exc


ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".codex/config.toml",
    ".codex/agents/explorer.toml",
    ".codex/agents/researcher.toml",
    ".codex/agents/implementer.toml",
    ".codex/agents/reviewer.toml",
    ".codex/agents/security-reviewer.toml",
    ".codex/agents/uiux-reviewer.toml",
    ".claude/settings.json",
    ".claude/agents/explorer.md",
    ".claude/agents/researcher.md",
    ".claude/agents/implementer.md",
    ".claude/agents/reviewer.md",
    ".claude/agents/security-reviewer.md",
    ".claude/agents/uiux-reviewer.md",
    ".gemini/settings.json",
    ".gemini/agents/explorer.md",
    ".gemini/agents/researcher.md",
    ".gemini/agents/implementer.md",
    ".gemini/agents/reviewer.md",
    ".gemini/agents/security-reviewer.md",
    ".gemini/agents/uiux-reviewer.md",
    "prompts/session-start.md",
    "prompts/codex-session-start.md",
    "prompts/claude-session-start.md",
    "prompts/gemini-session-start.md",
    "docs/HARNESSES.md",
    "docs/ORCHESTRATION.md",
    "docs/SESSION-EXAMPLES.md",
    "docs/UPSTREAMS.md",
    "scripts/bootstrap.sh",
    "scripts/verify-template.sh",
    "scripts/test-bootstrap.py",
    "scripts/test-validator-mutations.py",
    "examples/gemini-user-policies/reviewer-network-deny.toml",
]

CODEX_EXPECTED_WEB_SEARCH = {
    "explorer": "disabled",
    "researcher": "live",
    "implementer": "disabled",
    "reviewer": "disabled",
    "security-reviewer": "disabled",
    "uiux-reviewer": "disabled",
}

CLAUDE_LOCAL_CAPABLE_TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "Bash"}
CLAUDE_WEB_TOOLS = {"WebSearch", "WebFetch"}

CLAUDE_EXPECTED_TOOLS: dict[str, set[str]] = {
    "explorer": {"Read", "Grep", "Glob"},
    "researcher": {"WebSearch", "WebFetch"},
    "implementer": {"Read", "Grep", "Glob", "Write", "Edit", "Bash"},
    "reviewer": {"Read", "Grep", "Glob", "Bash"},
    "security-reviewer": {"Read", "Grep", "Glob", "Bash"},
    "uiux-reviewer": {"Read", "Grep", "Glob", "Bash"},
}

GEMINI_FRONTMATTER_KEYS = {
    "kind",
    "name",
    "description",
    "display_name",
    "tools",
    "mcp_servers",
    "model",
    "temperature",
    "max_turns",
    "timeout_mins",
}

GEMINI_BUILTIN_TOOLS = {
    "glob",
    "write_todos",
    "write_file",
    "google_web_search",
    "web_fetch",
    "replace",
    "run_shell_command",
    "grep_search",
    "read_many_files",
    "read_file",
    "list_directory",
    "activate_skill",
    "ask_user",
    "tracker_create_task",
    "tracker_update_task",
    "tracker_get_task",
    "tracker_list_tasks",
    "tracker_add_dependency",
    "tracker_visualize",
    "get_internal_docs",
    "enter_plan_mode",
    "exit_plan_mode",
    "update_topic",
    "complete_task",
    "invoke_agent",
    "read_mcp_resource",
    "list_mcp_resources",
}

GEMINI_LOCAL_CAPABLE_TOOLS = {
    "read_file",
    "read_many_files",
    "list_directory",
    "glob",
    "grep_search",
    "write_file",
    "replace",
    "run_shell_command",
}
GEMINI_WEB_TOOLS = {"google_web_search", "web_fetch"}

GEMINI_EXPECTED_TOOLS: dict[str, set[str]] = {
    "explorer": {"read_file", "read_many_files", "list_directory", "glob", "grep_search"},
    "researcher": {"google_web_search", "web_fetch"},
    "implementer": {
        "read_file",
        "read_many_files",
        "list_directory",
        "glob",
        "grep_search",
        "write_file",
        "replace",
        "run_shell_command",
    },
    "reviewer": {
        "read_file",
        "read_many_files",
        "list_directory",
        "glob",
        "grep_search",
        "run_shell_command",
    },
    "security-reviewer": {
        "read_file",
        "read_many_files",
        "list_directory",
        "glob",
        "grep_search",
        "run_shell_command",
    },
    "uiux-reviewer": {
        "read_file",
        "read_many_files",
        "list_directory",
        "glob",
        "grep_search",
        "run_shell_command",
    },
}


errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read_text(rel: str) -> str:
    path = ROOT / rel
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"{rel}: cannot read: {exc}")
        return ""


def parse_toml(rel: str) -> dict[str, Any]:
    text = read_text(rel)
    if not text:
        return {}
    try:
        value = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        fail(f"{rel}: invalid TOML: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(f"{rel}: TOML root must be a table")
        return {}
    return value


def parse_json(rel: str) -> dict[str, Any]:
    text = read_text(rel)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"{rel}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(f"{rel}: JSON root must be an object")
        return {}
    return value


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader: yaml.Loader, node: yaml.Node, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.YAMLError(f"duplicate key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping,
)


def parse_frontmatter(rel: str) -> dict[str, Any]:
    text = read_text(rel)
    if not text:
        return {}

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{rel}: missing opening YAML frontmatter delimiter")
        return {}

    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if end is None:
        fail(f"{rel}: missing closing YAML frontmatter delimiter")
        return {}

    raw = "\n".join(lines[1:end])
    try:
        value = yaml.load(raw, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        fail(f"{rel}: invalid YAML frontmatter: {exc}")
        return {}

    if not isinstance(value, dict):
        fail(f"{rel}: YAML frontmatter must be a mapping")
        return {}

    return value


def normalize_claude_tools(value: Any, rel: str) -> list[str]:
    if value is None:
        fail(f"{rel}: tools must be declared explicitly; omission inherits parent/all tools")
        return []

    if isinstance(value, str):
        tools = [item.strip() for item in value.split(",") if item.strip()]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        tools = [item.strip() for item in value if item.strip()]
    else:
        fail(f"{rel}: tools must be a YAML list or comma-separated string")
        return []

    if not tools:
        fail(f"{rel}: tools must not be empty")
    return tools


def normalize_disallowed_tools(value: Any, rel: str) -> list[str]:
    if value is None:
        fail(f"{rel}: disallowedTools must explicitly include Agent")
        return []

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return [item.strip() for item in value if item.strip()]

    fail(f"{rel}: disallowedTools must be a list or comma-separated string")
    return []


def is_valid_gemini_tool_name(name: str) -> bool:
    if name in GEMINI_BUILTIN_TOOLS:
        return True

    if name.startswith("discovered_tool_"):
        return True

    if name == "*":
        return True

    if name == "mcp_*":
        return True

    if not name.startswith("mcp_"):
        return False

    rest = name[4:]
    if rest.startswith("_") or "_" not in rest:
        return False

    server, tool = rest.split("_", 1)
    slug = re.compile(r"^[a-z0-9_.:-]+$", re.IGNORECASE)

    if not server or not slug.fullmatch(server):
        return False
    if tool == "*":
        return True
    if not tool or re.fullmatch(r"_*", tool):
        return False
    return bool(slug.fullmatch(tool))


def normalize_gemini_tools(value: Any, rel: str) -> list[str]:
    if value is None:
        fail(f"{rel}: tools must be declared explicitly; omission inherits parent/all tools")
        return []

    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{rel}: Gemini tools must be a YAML list of strings")
        return []

    tools = [item.strip() for item in value if item.strip()]
    if not tools:
        fail(f"{rel}: tools must not be empty")

    for tool in tools:
        if not is_valid_gemini_tool_name(tool):
            fail(f"{rel}: invalid Gemini tool name: {tool}")

    return tools


for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        fail(f"missing required file: {rel}")


# Codex
codex = parse_toml(".codex/config.toml")
features = codex.get("features")
agents = codex.get("agents")

if not isinstance(features, dict) or features.get("multi_agent") is not True:
    fail(".codex/config.toml: [features].multi_agent must be true")

if not isinstance(agents, dict):
    fail(".codex/config.toml: [agents] table is required")
else:
    if agents.get("max_depth") != 1:
        fail(".codex/config.toml: [agents].max_depth must equal integer 1 exactly")
    if not isinstance(agents.get("max_threads"), int) or agents.get("max_threads", 0) < 1:
        fail(".codex/config.toml: [agents].max_threads must be a positive integer")

    for name, role in agents.items():
        if name in {"max_depth", "max_threads", "default_subagent_model", "default_subagent_reasoning_effort"}:
            continue
        if not isinstance(role, dict):
            continue
        config_file = role.get("config_file")
        if not isinstance(config_file, str) or not config_file:
            fail(f".codex/config.toml: agent role {name!r} must define config_file")
            continue
        role_path = f".codex/{config_file}"
        if not (ROOT / role_path).is_file():
            fail(f".codex/config.toml: agent role {name!r} points to missing {role_path}")
        else:
            role_file = parse_toml(role_path)
            role_file_name = role_file.get("name")
            if isinstance(role_file_name, str) and role_file_name != name:
                fail(
                    f"{role_path}: name {role_file_name!r} must match declared "
                    f"Codex role name {name!r}"
                )

if "persistent_instructions" in codex:
    fail(".codex/config.toml: persistent_instructions is ignored; use developer_instructions")
if not isinstance(codex.get("developer_instructions"), str):
    fail(".codex/config.toml: developer_instructions must be present")

for path in sorted((ROOT / ".codex/agents").glob("*.toml")):
    rel = str(path.relative_to(ROOT))
    role = parse_toml(rel)
    expected_name = path.stem
    role_name = role.get("name")

    if role_name != expected_name:
        fail(f"{rel}: name must equal filename stem {expected_name!r}")

    if not isinstance(role.get("description"), str) or not role.get("description", "").strip():
        fail(f"{rel}: description must be a non-empty string")

    if not isinstance(role.get("developer_instructions"), str) or not role.get("developer_instructions", "").strip():
        fail(f"{rel}: developer_instructions must be a non-empty string")

    if "web_search" not in role:
        fail(f"{rel}: web_search must be declared explicitly")

for name, expected_web_search in CODEX_EXPECTED_WEB_SEARCH.items():
    rel = f".codex/agents/{name}.toml"
    role = parse_toml(rel)
    if role.get("web_search") != expected_web_search:
        fail(
            f"{rel}: default role web_search must be {expected_web_search!r}"
        )

agents_policy = read_text("AGENTS.md")
codex_prompt = read_text("prompts/codex-session-start.md")
if "fork_turns" not in agents_policy:
    fail("AGENTS.md: Codex spawn policy must mention fork_turns")
if "fork_turns" not in codex_prompt:
    fail("prompts/codex-session-start.md: must mention fork_turns")


# Claude
claude_settings = parse_json(".claude/settings.json")
claude_env = claude_settings.get("env")
if not isinstance(claude_env, dict) or str(claude_env.get("CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH")) != "1":
    fail(".claude/settings.json: CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH must be 1")

worktree = claude_settings.get("worktree")
if not isinstance(worktree, dict) or worktree.get("baseRef") != "head":
    fail(".claude/settings.json: worktree.baseRef must be \"head\"")

permissions = claude_settings.get("permissions")
denies = permissions.get("deny") if isinstance(permissions, dict) else None
if not isinstance(denies, list):
    fail(".claude/settings.json: permissions.deny must be a list")
else:
    for rule in ("Bash(curl:*)", "Bash(wget:*)"):
        if rule not in denies:
            fail(f".claude/settings.json: permissions.deny must include {rule}")

for path in sorted((ROOT / ".claude/agents").glob("*.md")):
    rel = str(path.relative_to(ROOT))
    fm = parse_frontmatter(rel)

    for key in ("name", "description", "model"):
        if not isinstance(fm.get(key), str) or not fm.get(key):
            fail(f"{rel}: frontmatter {key!r} must be a non-empty string")

    name = fm.get("name")
    expected_name = path.stem
    if name != expected_name:
        fail(f"{rel}: name must equal filename stem {expected_name!r}")

    tools = set(normalize_claude_tools(fm.get("tools"), rel))
    disallowed = set(normalize_disallowed_tools(fm.get("disallowedTools"), rel))

    if tools & CLAUDE_LOCAL_CAPABLE_TOOLS and tools & CLAUDE_WEB_TOOLS:
        fail(f"{rel}: agent must not combine local/shell tools with web tools")

    if "Agent" not in disallowed:
        fail(f"{rel}: disallowedTools must include Agent")

    if isinstance(name, str) and name in CLAUDE_EXPECTED_TOOLS and tools != CLAUDE_EXPECTED_TOOLS[name]:
        fail(
            f"{rel}: tools must equal {sorted(CLAUDE_EXPECTED_TOOLS[name])}; "
            f"got {sorted(tools)}"
        )

claude_impl = parse_frontmatter(".claude/agents/implementer.md")
if claude_impl.get("isolation") != "worktree":
    fail(".claude/agents/implementer.md: isolation must be worktree")


# Gemini
gemini_settings = parse_json(".gemini/settings.json")
experimental = gemini_settings.get("experimental")
if not isinstance(experimental, dict) or experimental.get("worktrees") is not True:
    fail(".gemini/settings.json: experimental.worktrees must be true")

for path in sorted((ROOT / ".gemini/agents").glob("*.md")):
    rel = str(path.relative_to(ROOT))
    fm = parse_frontmatter(rel)

    unknown_keys = set(fm) - GEMINI_FRONTMATTER_KEYS
    if unknown_keys:
        fail(f"{rel}: unknown Gemini frontmatter keys: {sorted(unknown_keys)}")

    for key in ("name", "description", "model"):
        if not isinstance(fm.get(key), str) or not fm.get(key):
            fail(f"{rel}: frontmatter {key!r} must be a non-empty string")

    kind = fm.get("kind", "local")
    if kind != "local":
        fail(f"{rel}: kind must be local")

    name = fm.get("name")
    expected_name = path.stem
    if name != expected_name:
        fail(f"{rel}: name must equal filename stem {expected_name!r}")

    tools = set(normalize_gemini_tools(fm.get("tools"), rel))

    if tools & GEMINI_LOCAL_CAPABLE_TOOLS and tools & GEMINI_WEB_TOOLS:
        fail(f"{rel}: agent must not combine local/shell tools with web tools")

    if fm.get("model") == "gemini-3-flash-preview":
        fail(f"{rel}: use the flash alias instead of stale gemini-3-flash-preview pin")

    if isinstance(name, str) and name in GEMINI_EXPECTED_TOOLS and tools != GEMINI_EXPECTED_TOOLS[name]:
        fail(
            f"{rel}: tools must equal {sorted(GEMINI_EXPECTED_TOOLS[name])}; "
            f"got {sorted(tools)}"
        )


# Shared docs/config invariants
if "@AGENTS.md" not in read_text("CLAUDE.md"):
    fail("CLAUDE.md must import @AGENTS.md")
if "@AGENTS.md" not in read_text("GEMINI.md"):
    fail("GEMINI.md must import @AGENTS.md")

gemini_policy = parse_toml("examples/gemini-user-policies/reviewer-network-deny.toml")
rules = gemini_policy.get("rule")
if not isinstance(rules, list) or len(rules) < 3:
    fail("examples/gemini-user-policies/reviewer-network-deny.toml: expected reviewer deny rules")
else:
    expected_subagents = {"reviewer", "security-reviewer", "uiux-reviewer"}
    present_subagents = {
        rule.get("subagent")
        for rule in rules
        if isinstance(rule, dict)
        and rule.get("toolName") == "run_shell_command"
        and rule.get("decision") == "deny"
        and set(rule.get("commandPrefix", [])) >= {"curl", "wget"}
    }
    if not expected_subagents.issubset(present_subagents):
        fail("Gemini reviewer user-policy example must deny curl/wget for all reviewer roles")

gitignore = read_text(".gitignore")
for ignored in (".claude/worktrees/", ".gemini/worktrees/"):
    if ignored not in gitignore:
        fail(f".gitignore must include {ignored}")


if errors:
    for error in errors:
        print(f"[fail] {error}", file=sys.stderr)
    print(f"Template validation failed with {len(errors)} error(s).", file=sys.stderr)
    raise SystemExit(1)

print("Template structural validation passed.")
