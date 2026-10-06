#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path
from typing import Any

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
]

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

    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break

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


def has_agent_disallow(value: Any) -> bool:
    if isinstance(value, str):
        parts = [item.strip() for item in value.split(",")]
        return "Agent" in parts
    if isinstance(value, list):
        return "Agent" in value
    return False


for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        fail(f"missing required file: {rel}")

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
            parse_toml(role_path)

if "persistent_instructions" in codex:
    fail(".codex/config.toml: persistent_instructions is ignored; use developer_instructions")
if not isinstance(codex.get("developer_instructions"), str):
    fail(".codex/config.toml: developer_instructions must be present")

agents_policy = read_text("AGENTS.md")
codex_prompt = read_text("prompts/codex-session-start.md")
if "fork_turns" not in agents_policy:
    fail("AGENTS.md: Codex spawn policy must mention fork_turns")
if "fork_turns" not in codex_prompt:
    fail("prompts/codex-session-start.md: must mention fork_turns")

claude_settings = parse_json(".claude/settings.json")
claude_env = claude_settings.get("env")
if not isinstance(claude_env, dict) or str(claude_env.get("CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH")) != "1":
    fail(".claude/settings.json: CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH must be 1")

for path in sorted((ROOT / ".claude/agents").glob("*.md")):
    rel = str(path.relative_to(ROOT))
    fm = parse_frontmatter(rel)
    for key in ("name", "description", "model"):
        if not isinstance(fm.get(key), str) or not fm.get(key):
            fail(f"{rel}: frontmatter {key!r} must be a non-empty string")
    if not has_agent_disallow(fm.get("disallowedTools")):
        fail(f"{rel}: disallowedTools must include Agent to enforce one-level delegation")

claude_impl = parse_frontmatter(".claude/agents/implementer.md")
if claude_impl.get("isolation") != "worktree":
    fail(".claude/agents/implementer.md: isolation must be worktree")

gemini_settings = parse_json(".gemini/settings.json")
experimental = gemini_settings.get("experimental")
if not isinstance(experimental, dict) or experimental.get("worktrees") is not True:
    fail(".gemini/settings.json: experimental.worktrees must be true")

for path in sorted((ROOT / ".gemini/agents").glob("*.md")):
    rel = str(path.relative_to(ROOT))
    fm = parse_frontmatter(rel)
    for key in ("name", "description", "model"):
        if not isinstance(fm.get(key), str) or not fm.get(key):
            fail(f"{rel}: frontmatter {key!r} must be a non-empty string")
    if fm.get("model") == "gemini-3-flash-preview":
        fail(f"{rel}: use the flash alias instead of stale gemini-3-flash-preview pin")

claude_research = parse_frontmatter(".claude/agents/researcher.md")
if any(tool in (claude_research.get("tools") or []) for tool in ("Read", "Grep", "Glob")):
    fail(".claude/agents/researcher.md: external researcher must not combine local file reads with web tools")

for rel in (".claude/agents/security-reviewer.md", ".claude/agents/uiux-reviewer.md"):
    fm = parse_frontmatter(rel)
    tools = set(fm.get("tools") or [])
    if tools.intersection({"WebSearch", "WebFetch"}):
        fail(f"{rel}: local reviewer must not have outbound web tools")

gemini_research = parse_frontmatter(".gemini/agents/researcher.md")
if any(tool in (gemini_research.get("tools") or []) for tool in ("read_file", "read_many_files", "glob", "grep_search")):
    fail(".gemini/agents/researcher.md: external researcher must not combine local file reads with web tools")

for rel in (".gemini/agents/security-reviewer.md", ".gemini/agents/uiux-reviewer.md"):
    fm = parse_frontmatter(rel)
    tools = set(fm.get("tools") or [])
    if tools.intersection({"google_web_search", "web_fetch"}):
        fail(f"{rel}: local reviewer must not have outbound web tools")

if "@AGENTS.md" not in read_text("CLAUDE.md"):
    fail("CLAUDE.md must import @AGENTS.md")
if "@AGENTS.md" not in read_text("GEMINI.md"):
    fail("GEMINI.md must import @AGENTS.md")

if errors:
    for error in errors:
        print(f"[fail] {error}", file=sys.stderr)
    print(f"Template validation failed with {len(errors)} error(s).", file=sys.stderr)
    raise SystemExit(1)

print("Template structural validation passed.")
