#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
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
    ".editorconfig",
    ".gitignore",
    ".github/workflows/template-check.yml",
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
    "scripts/vendored-skills.json",
    "scripts/project-skills.json",
    "docs/templates/spec.md",
    "docs/templates/design.md",
    "docs/templates/adr.md",
    "docs/templates/plan.md",
    "docs/templates/context.md",
    "scripts/bootstrap.sh",
    "scripts/verify-template.sh",
    "scripts/test-bootstrap.py",
    "scripts/test-validator-mutations.py",
    "scripts/test-gemini-policy.mjs",
    "scripts/gen-gemini-policy.py",
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


# Tools that neither touch local files/shell nor reach the network. A role
# that has any network-capable tool may only add tools from this set; every
# other tool, including ones this validator has never heard of (PowerShell,
# Monitor, NotebookEdit, LSP, a future tool, ...), counts as local-capable.
CLAUDE_INERT_TOOLS = {"TodoWrite", "AskUserQuestion", "EnterPlanMode", "ExitPlanMode"}


def claude_tool_capabilities(tools: set[str]) -> tuple[set[str], set[str]]:
    """Return (local-capable, network-capable) tool entries.

    Network-capable: dedicated web tools, any MCP tool (`mcp__<server>` or
    `mcp__<server>__<tool>`), and the `*` wildcard. Local-capable: every
    other tool that is not explicitly inert. `*` counts as both.
    """
    local: set[str] = set()
    network: set[str] = set()
    for tool in tools:
        base = tool.split("(", 1)[0].strip()
        if base == "*":
            local.add(tool)
            network.add(tool)
        elif base in CLAUDE_WEB_TOOLS or base.startswith("mcp__"):
            network.add(tool)
        elif base not in CLAUDE_INERT_TOOLS:
            local.add(tool)
    return local, network


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


GEMINI_MCP_TOOLS = {"read_mcp_resource", "list_mcp_resources"}
# Built-ins that neither touch local files/shell nor reach the network. A
# role with any network-capable tool may only add tools from this set; any
# other tool (including activate_skill, which loads files from disk) counts as
# local-capable.
GEMINI_INERT_TOOLS = {
    "write_todos",
    "ask_user",
    "enter_plan_mode",
    "exit_plan_mode",
    "update_topic",
    "complete_task",
    "get_internal_docs",
    "tracker_create_task",
    "tracker_update_task",
    "tracker_get_task",
    "tracker_list_tasks",
    "tracker_add_dependency",
    "tracker_visualize",
}


def gemini_tool_capabilities(tools: set[str]) -> tuple[set[str], set[str]]:
    """Return (local-capable, network-capable) tool entries.

    Gemini 0.62.0 expands `*` to every parent tool (including web_fetch and
    run_shell_command) and `mcp_*` to every MCP tool. Network-capable: web
    tools, MCP tools (`mcp_...`, read/list_mcp_resource(s)) and
    `discovered_tool_...` entries, which run external commands. Local-capable:
    every other tool that is not explicitly inert. `*` counts as both.
    """
    local: set[str] = set()
    network: set[str] = set()
    for tool in tools:
        if tool == "*":
            local.add(tool)
            network.add(tool)
        elif (
            tool in GEMINI_WEB_TOOLS
            or tool in GEMINI_MCP_TOOLS
            or tool.startswith("mcp_")
            or tool.startswith("discovered_tool_")
        ):
            network.add(tool)
        elif tool not in GEMINI_INERT_TOOLS:
            local.add(tool)
    return local, network


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


# Mirrors Gemini CLI 0.62.0 `isSafeRegExp` (packages/core policy loader).
# Gemini silently drops any commandRegex rule that fails this check, so a
# pattern that is valid regex can still provide zero protection.
GEMINI_NESTED_QUANTIFIER = re.compile(r"\([^)]*[*+?{].*\)[*+?{]")
GEMINI_MAX_REGEX_LENGTH = 2048
GEMINI_DOUBLED_CLASS_ESCAPE = re.compile(r"\\\\[sSdDwWbBtnr]")


def gemini_regex_problem(pattern: str) -> str | None:
    # Gemini prepends the JSON args prefix before compiling the rule.
    full = '"command":"' + pattern
    try:
        re.compile(full)
    except re.error as exc:
        return f"commandRegex does not compile: {exc}"
    if len(full) > GEMINI_MAX_REGEX_LENGTH:
        return f"commandRegex longer than {GEMINI_MAX_REGEX_LENGTH} characters is dropped by Gemini"
    if GEMINI_NESTED_QUANTIFIER.search(full):
        return (
            "commandRegex looks like a nested quantifier; Gemini drops it as "
            "'Unsafe regex pattern (potential ReDoS)'. Keep quantified tokens out of quantified groups"
        )
    if pattern.startswith("^") or "(^" in pattern:
        return 'commandRegex is matched after the "command":" JSON prefix, so ^ can never match'
    # `\\s`, `\\d`, ... is the classic mistake of TOML-escaping inside a
    # literal string: it matches a literal backslash followed by a letter.
    # A doubled backslash before a quote (`\\"`) is legitimate and required:
    # quotes in the command appear JSON-escaped as \" in the matched text.
    if GEMINI_DOUBLED_CLASS_ESCAPE.search(pattern):
        return (
            "commandRegex contains a doubled backslash before a character class "
            "(e.g. \\\\s); TOML literal strings need a single backslash"
        )
    return None


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


# Planning gate: no harness may go from objective straight to code. The
# policy must define the gate, every adapter must point at it, and every start
# prompt must stop for approval inside PHASE 1, before the PHASE 2 heading.
PLANNING_STOP_MARKER = "STOP and wait for explicit user approval"
PLANNING_SKILLS = ("brainstorming", "writing-plans")
START_PROMPTS = (
    "prompts/session-start.md",
    "prompts/codex-session-start.md",
    "prompts/claude-session-start.md",
    "prompts/gemini-session-start.md",
)
PHASE_1_HEADING = re.compile(r"^PHASE 1\b.*\bno file edits\b.*$", re.MULTILINE)
PHASE_2_HEADING = re.compile(r"^PHASE 2\b.*\bonly after\b.*$", re.MULTILINE)
# Gate references must use the form "planning gate (section N)" or
# "planning gate (AGENTS.md section N)" so renumbering cannot leave them stale.
GATE_SECTION_REF = re.compile(r"planning gate \((?:AGENTS\.md )?section (\d+)\)", re.IGNORECASE)

gate_heading = re.search(r"^## (\d+)\. Planning gate\b", agents_policy, re.MULTILINE)
if not gate_heading:
    fail("AGENTS.md: must define a numbered '## N. Planning gate' section")
for required in (*PLANNING_SKILLS, PLANNING_STOP_MARKER):
    if required not in agents_policy:
        fail(f"AGENTS.md: planning gate must mention {required!r}")

for rel in START_PROMPTS:
    text = read_text(rel)
    for required in PLANNING_SKILLS:
        if required not in text:
            fail(f"{rel}: must name the Superpowers {required!r} skill")
    plan = PHASE_1_HEADING.search(text)
    execute = PHASE_2_HEADING.search(text)
    if not plan:
        fail(f"{rel}: needs a 'PHASE 1' heading line that forbids file edits ('no file edits')")
    if not execute:
        fail(f"{rel}: needs a 'PHASE 2' heading line that runs 'only after' approval")
    if plan and execute:
        if plan.start() > execute.start():
            fail(f"{rel}: PHASE 1 must come before PHASE 2")
        elif PLANNING_STOP_MARKER not in text[plan.end():execute.start()]:
            fail(f"{rel}: PHASE 1 must end with {PLANNING_STOP_MARKER!r} before the PHASE 2 heading")

codex_instructions = codex.get("developer_instructions", "")
gate_pointers = {
    "CLAUDE.md": read_text("CLAUDE.md"),
    "GEMINI.md": read_text("GEMINI.md"),
    ".codex/config.toml developer_instructions": codex_instructions if isinstance(codex_instructions, str) else "",
}
for rel, text in gate_pointers.items():
    if "planning gate" not in text.lower():
        fail(f"{rel}: must point at the AGENTS.md planning gate")

if gate_heading:
    gate_number = gate_heading.group(1)
    # Living docs only: dated records (ADRs, plans, specs, designs) keep the
    # wording they were approved with and are not rewritten on renumbering.
    record_dirs = {ROOT / "docs" / name for name in ("adr", "plans", "specs", "designs", "handoffs", "reviews")}
    for path in sorted({ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "GEMINI.md", ROOT / "README.md",
                        *ROOT.glob("docs/**/*"), *ROOT.glob("prompts/*.md")}):
        if not path.is_file() or path.suffix not in {".md", ".html"} or record_dirs & set(path.parents):
            continue
        for match in GATE_SECTION_REF.finditer(path.read_text(encoding="utf-8")):
            if match.group(1) != gate_number:
                fail(
                    f"{path.relative_to(ROOT)}: planning gate reference says section "
                    f"{match.group(1)}, but AGENTS.md defines it as section {gate_number}"
                )


# PHASE 1 artifacts: the gate must leave a spec, a design, ADRs for
# architecture decisions, and a plan at fixed project paths, built from the
# templates in docs/templates/ (ADR 0002).
ARTIFACT_DIRS = ("docs/specs/", "docs/designs/", "docs/adr/", "docs/plans/")
ADR_TRIGGER_MARKER = "An ADR is required"
TEMPLATE_HEADINGS = {
    "docs/templates/spec.md": (
        "Problem", "Goals and success criteria", "Scope", "Non-goals",
        "Requirements", "Acceptance criteria", "Open questions",
    ),
    "docs/templates/design.md": (
        "Overview", "Components", "Alternatives considered", "Risks", "Test strategy",
    ),
    "docs/templates/adr.md": ("Context", "Decision", "Alternatives considered", "Consequences"),
    "docs/templates/plan.md": (
        "Objective and success criteria", "Scope and non-goals", "Architecture decision",
        "Execution graph", "Tasks", "Verification", "Risks and open questions",
    ),
}
# One concrete status per ADR; an unedited template line ("Proposed | Accepted | ...")
# does not count.
ADR_STATUS = re.compile(
    r"^- Status: (Proposed|Accepted|Deprecated|Superseded|Rejected)\b[^|\n]*$", re.MULTILINE
)
ADR_FILENAME = re.compile(r"^\d{4}-[a-z0-9][a-z0-9-]*\.md$")
PHASE_2_ACCEPT_MARKER = "Status: Accepted"


for required in (*ARTIFACT_DIRS, "docs/templates/", ADR_TRIGGER_MARKER):
    if required not in agents_policy:
        fail(f"AGENTS.md: planning gate must define PHASE 1 artifacts ({required!r} missing)")

for rel in START_PROMPTS:
    text = read_text(rel)
    plan = PHASE_1_HEADING.search(text)
    execute = PHASE_2_HEADING.search(text)
    if not (plan and execute and plan.start() < execute.start()):
        continue
    phase_1 = text[plan.start():execute.start()]
    for required in ARTIFACT_DIRS:
        if required not in phase_1:
            fail(f"{rel}: PHASE 1 must name the {required} artifact")
    if PHASE_2_ACCEPT_MARKER not in text[execute.start():]:
        fail(f"{rel}: PHASE 2 must start by setting the task's ADRs to {PHASE_2_ACCEPT_MARKER!r}")

for rel, headings in TEMPLATE_HEADINGS.items():
    path = ROOT / rel
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    for heading in headings:
        if not re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE):
            fail(f"{rel}: template must contain the heading '## {heading}'")

adr_numbers: dict[str, str] = {}
for path in sorted((ROOT / "docs/adr").glob("*")):
    rel = str(path.relative_to(ROOT))
    if path.name == "README.md":
        continue
    if not ADR_FILENAME.match(path.name):
        fail(f"{rel}: ADR files must be named NNNN-<kebab-title>.md")
        continue
    if not ADR_STATUS.search(path.read_text(encoding="utf-8")):
        fail(f"{rel}: needs a '- Status:' line of Proposed, Accepted, Deprecated, Superseded or Rejected")
    number = path.name[:4]
    if number in adr_numbers:
        fail(f"{rel}: ADR number {number} is already used by {adr_numbers[number]}")
    adr_numbers[number] = rel


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

    local_tools, network_tools = claude_tool_capabilities(tools)
    if local_tools and network_tools:
        fail(
            f"{rel}: agent must not combine local/shell tools {sorted(local_tools)} with "
            f"network-capable web/MCP/wildcard tools {sorted(network_tools)}"
        )

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

    local_tools, network_tools = gemini_tool_capabilities(tools)
    if local_tools and network_tools:
        fail(
            f"{rel}: agent must not combine local/shell tools {sorted(local_tools)} with "
            f"network-capable web/MCP/wildcard tools {sorted(network_tools)}"
        )

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
    prefix_subagents = {
        rule.get("subagent")
        for rule in rules
        if isinstance(rule, dict)
        and rule.get("toolName") == "run_shell_command"
        and rule.get("decision") == "deny"
        and set(rule.get("commandPrefix", [])) >= {"curl", "wget"}
    }
    regex_subagents = {
        rule.get("subagent")
        for rule in rules
        if isinstance(rule, dict)
        and rule.get("toolName") == "run_shell_command"
        and rule.get("decision") == "deny"
        and isinstance(rule.get("commandRegex"), str)
        and "curl|wget" in rule.get("commandRegex", "")
    }
    for index, rule in enumerate(rules, start=1):
        if not isinstance(rule, dict) or not isinstance(rule.get("commandRegex"), str):
            continue
        problem = gemini_regex_problem(rule["commandRegex"])
        if problem:
            fail(
                "examples/gemini-user-policies/reviewer-network-deny.toml: "
                f"rule #{index} ({rule.get('name', 'unnamed')}): {problem}"
            )
    if not expected_subagents.issubset(prefix_subagents):
        fail("Gemini reviewer user-policy example must deny curl/wget prefixes for all reviewer roles")
    if not expected_subagents.issubset(regex_subagents):
        fail("Gemini reviewer user-policy example must include wrapped curl/wget regex rules for all reviewer roles")

# Vendored skills must stay byte-identical to the pinned upstream commit
# (ADR 0003). Their bytes are upstream's, so they are not in the newline check.
VENDORED_MANIFEST = "scripts/vendored-skills.json"
PROJECT_SKILLS_MANIFEST = "scripts/project-skills.json"
# OS junk that .gitignore already keeps out of commits; skipped only as regular files.
VENDORED_IGNORED_NAMES = {".DS_Store", "Thumbs.db"}
VENDORED_SKILL_ROOTS = (".agents/skills", ".claude/skills", ".gemini/skills")
SHA1_HEX = re.compile(r"^[0-9a-f]{40}$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


def is_safe_relative(rel: str) -> bool:
    path = PurePosixPath(rel)
    return bool(rel) and not path.is_absolute() and ".." not in path.parts and "\\" not in rel


def check_vendored_skills(extra_declared: set[str]) -> None:
    manifest = parse_json(VENDORED_MANIFEST)
    skills = manifest.get("skills")
    if not isinstance(skills, list) or not skills:
        fail(f"{VENDORED_MANIFEST}: 'skills' must be a non-empty list")
        return

    declared_links: set[str] = set(extra_declared)
    for skill in skills:
        if not isinstance(skill, dict):
            fail(f"{VENDORED_MANIFEST}: each skill entry must be an object")
            continue
        name = skill.get("name", "<unnamed>")
        label = f"{VENDORED_MANIFEST}: {name}"

        for key in ("name", "repo", "source_path", "dest"):
            if not isinstance(skill.get(key), str) or not skill[key]:
                fail(f"{label}: '{key}' must be a non-empty string")
        if not SHA1_HEX.match(str(skill.get("commit", ""))):
            fail(f"{label}: 'commit' must be a full 40-hex commit")

        dest_rel = skill.get("dest")
        files = skill.get("files")
        if not isinstance(dest_rel, str) or not is_safe_relative(dest_rel):
            fail(f"{label}: 'dest' must be a safe relative path")
            continue
        if not isinstance(files, dict) or not files:
            fail(f"{label}: 'files' must be a non-empty object")
            continue

        dest = ROOT / dest_rel
        if dest.is_symlink() or not dest.is_dir():
            fail(f"{label}: {dest_rel} must be a real directory")
            continue
        # A symlinked parent (for example .agents/skills) would serve files from outside the repo.
        if dest.resolve() != ROOT.resolve() / dest_rel:
            fail(f"{label}: {dest_rel} must not be reached through a symlinked parent")
            continue

        expected: dict[str, str] = {}
        for rel, digest in files.items():
            if not isinstance(rel, str) or not is_safe_relative(rel):
                fail(f"{label}: unsafe file path {rel!r}")
            elif not isinstance(digest, str) or not SHA256_HEX.match(digest):
                fail(f"{label}: {rel}: hash must be 64-hex SHA-256")
            else:
                expected[rel] = digest

        found: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(dest, followlinks=False):
            current = Path(dirpath)
            for entry in dirnames + filenames:
                path = current / entry
                rel = path.relative_to(dest).as_posix()
                if path.is_symlink():
                    fail(f"{label}: {dest_rel}/{rel} must not be a symlink")
                    # Counted as found so the symlink rule alone reports it.
                    found.add(rel)
                elif path.is_dir():
                    continue
                elif not path.is_file():
                    fail(f"{label}: {dest_rel}/{rel} must be a regular file")
                    found.add(rel)
                elif entry not in VENDORED_IGNORED_NAMES:
                    found.add(rel)

        for rel in sorted(found - set(files)):
            fail(f"{label}: unexpected file {dest_rel}/{rel}")
        for rel in sorted(set(expected) - found):
            fail(f"{label}: missing file {dest_rel}/{rel}")
        for rel in sorted(set(expected) & found):
            actual = hashlib.sha256((dest / rel).read_bytes()).hexdigest()
            if actual != expected[rel]:
                fail(f"{label}: {dest_rel}/{rel} does not match the pinned SHA-256")

        entry_points = skill.get("entry_points")
        if not isinstance(entry_points, dict) or not entry_points:
            fail(f"{label}: 'entry_points' must be a non-empty object")
            continue
        for link_rel, target in entry_points.items():
            link = ROOT / link_rel
            if not is_safe_relative(link_rel) or not isinstance(target, str):
                fail(f"{label}: invalid entry point {link_rel!r}")
            elif not link.is_symlink():
                fail(f"{label}: {link_rel} must be a symlink to {target}")
            elif os.readlink(link) != target:
                fail(f"{label}: {link_rel} must point to {target}, not {os.readlink(link)}")
            else:
                declared_links.add(link_rel)

    # Every symlink in a skill root must be a declared entry point.
    for root_rel in VENDORED_SKILL_ROOTS:
        skill_root = ROOT / root_rel
        if not skill_root.is_dir():
            continue
        for entry in sorted(skill_root.iterdir()):
            rel = entry.relative_to(ROOT).as_posix()
            if entry.is_symlink() and rel not in declared_links:
                fail(f"undeclared symlink {rel}: declare it in {PROJECT_SKILLS_MANIFEST} or {VENDORED_MANIFEST}")



# Project-authored skills (ADR 0004): explicit-only in every harness that
# supports it, declared in scripts/project-skills.json, not hash-pinned.


def check_project_skills() -> set[str]:
    declared: set[str] = set()
    manifest = parse_json(PROJECT_SKILLS_MANIFEST)
    skills = manifest.get("skills")
    if not isinstance(skills, list) or not skills:
        fail(f"{PROJECT_SKILLS_MANIFEST}: 'skills' must be a non-empty list")
        return declared

    for skill in skills:
        if not isinstance(skill, dict):
            fail(f"{PROJECT_SKILLS_MANIFEST}: each skill entry must be an object")
            continue
        name = skill.get("name")
        path_rel = skill.get("path")
        label = f"{PROJECT_SKILLS_MANIFEST}: {name}"
        if not isinstance(name, str) or not isinstance(path_rel, str) or not is_safe_relative(path_rel):
            fail(f"{label}: 'name' and a safe relative 'path' are required")
            continue

        entry_points = skill.get("entry_points")
        if not isinstance(entry_points, dict) or not entry_points:
            fail(f"{label}: 'entry_points' must be a non-empty object")
            entry_points = {}
        for link_rel, target in entry_points.items():
            link = ROOT / link_rel
            if not is_safe_relative(link_rel) or not isinstance(target, str):
                fail(f"{label}: invalid entry point {link_rel!r}")
            elif not link.is_symlink():
                fail(f"{label}: {link_rel} must be a symlink to {target}")
            elif os.readlink(link) != target:
                fail(f"{label}: {link_rel} must point to {target}, not {os.readlink(link)}")
            elif link.parent.is_symlink() or link.parent.resolve() != ROOT.resolve() / Path(link_rel).parent:
                fail(f"{label}: {link_rel} must sit in a real directory, not behind a symlink")
            elif link.resolve() != (ROOT / path_rel).resolve():
                fail(f"{label}: {link_rel} must resolve to {path_rel}")
            else:
                declared.add(link_rel)

        skill_dir = ROOT / path_rel
        if skill_dir.is_symlink() or not skill_dir.is_dir():
            fail(f"{label}: {path_rel} must be a real directory")
            continue
        if skill_dir.resolve() != ROOT.resolve() / path_rel:
            fail(f"{label}: {path_rel} must not be reached through a symlinked parent")
            continue

        for file_rel in ("SKILL.md", "agents/openai.yaml"):
            if (skill_dir / file_rel).is_symlink():
                fail(f"{label}: {path_rel}/{file_rel} must not be a symlink")
        if not (skill_dir / "SKILL.md").is_file():
            fail(f"{label}: {path_rel}/SKILL.md is required")
            continue
        frontmatter = parse_frontmatter(f"{path_rel}/SKILL.md")
        if frontmatter.get("name") != skill_dir.name:
            fail(f"{label}: SKILL.md name must match the directory name {skill_dir.name!r}")
        if not isinstance(frontmatter.get("description"), str) or not frontmatter["description"].strip():
            fail(f"{label}: SKILL.md needs a non-empty description")
        # YAML 1.1 reads "yes"/"on" as true; other harnesses may not, so require the literal.
        if frontmatter.get("disable-model-invocation") is not True or not re.search(
            r"^disable-model-invocation: true[ \t]*$", read_text(f"{path_rel}/SKILL.md"), re.MULTILINE
        ):
            fail(f"{label}: SKILL.md must set disable-model-invocation: true (the literal YAML boolean)")

        openai_rel = f"{path_rel}/agents/openai.yaml"
        if not (ROOT / openai_rel).is_file():
            fail(f"{label}: {openai_rel} is required (Codex explicit-only policy)")
            continue
        try:
            openai = yaml.load(read_text(openai_rel), Loader=UniqueKeyLoader) or {}
        except yaml.YAMLError as exc:
            fail(f"{openai_rel}: invalid YAML: {exc}")
            continue
        policy = openai.get("policy") if isinstance(openai, dict) else None
        if (
            not isinstance(policy, dict)
            or policy.get("allow_implicit_invocation") is not False
            or not re.search(r"^[ \t]+allow_implicit_invocation: false[ \t]*$", read_text(openai_rel), re.MULTILINE)
        ):
            fail(f"{openai_rel}: policy must set allow_implicit_invocation: false")

    return declared


def declared_skill_dirs() -> set[str]:
    """Skill directories named by either manifest; malformed manifests are reported elsewhere."""
    dirs: set[str] = set()
    for rel, key in ((PROJECT_SKILLS_MANIFEST, "path"), (VENDORED_MANIFEST, "dest")):
        try:
            skills = json.loads((ROOT / rel).read_text(encoding="utf-8")).get("skills", [])
        except (OSError, ValueError, AttributeError):
            continue
        for skill in skills if isinstance(skills, list) else []:
            if isinstance(skill, dict) and isinstance(skill.get(key), str):
                dirs.add(skill[key])
    return dirs


check_vendored_skills(check_project_skills())

# Every real directory in a skill root must be a declared skill (ADR 0004), so
# an undeclared skill cannot skip the explicit-only checks.
_declared_dirs = declared_skill_dirs()
for root_rel in VENDORED_SKILL_ROOTS:
    skill_root = ROOT / root_rel
    if not skill_root.is_dir() or skill_root.is_symlink():
        continue
    for entry in sorted(skill_root.iterdir()):
        rel = entry.relative_to(ROOT).as_posix()
        if entry.is_dir() and not entry.is_symlink() and rel not in _declared_dirs:
            fail(f"undeclared skill directory {rel}: declare it in {PROJECT_SKILLS_MANIFEST} or {VENDORED_MANIFEST}")


# CONTEXT.md is the domain glossary (ADR 0005): a root CONTEXT.md, or a root
# CONTEXT-MAP.md that links one CONTEXT.md per bounded context.
# Only links whose last path segment is exactly CONTEXT.md count; a #fragment is dropped.
# An optional Markdown link title: "...", '...' or (...).
LINK_TITLE = r"""(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?"""
CONTEXT_MAP_LINK = re.compile(
    r"\]\(\s*<?((?:[^)\s#>]*/)?CONTEXT\.md)(?:#[^)\s>]*)?>?" + LINK_TITLE + r"\s*\)"
)
CONTEXT_MAP_REF_LINK = re.compile(
    r"^\s*\[[^\]]+\]:\s*<?((?:[^\s>#]*/)?CONTEXT\.md)(?:#[^\s>]*)?>?" + LINK_TITLE + r"\s*$",
    re.MULTILINE,
)


def require_language_section(rel: str) -> None:
    if not re.search(r"^## Language\s*$", read_text(rel), re.MULTILINE):
        fail(f"{rel}: needs a '## Language' section")


context_files: list[str] = ["docs/templates/context.md"] if (ROOT / "docs/templates/context.md").is_file() else []
if (ROOT / "CONTEXT-MAP.md").is_file():
    map_text = read_text("CONTEXT-MAP.md")
    # Inline links and reference definitions, de-duplicated in order.
    links = list(dict.fromkeys(CONTEXT_MAP_LINK.findall(map_text) + CONTEXT_MAP_REF_LINK.findall(map_text)))
    if not links:
        fail("CONTEXT-MAP.md: must link at least one CONTEXT.md")
    for link in links:
        rel = os.path.normpath(link.removeprefix("./"))
        path = ROOT / rel
        if not is_safe_relative(rel) or path.is_symlink() or not path.is_file() or ROOT.resolve() not in path.resolve().parents:
            fail(f"CONTEXT-MAP.md: linked context file is missing or unsafe: {link}")
        else:
            context_files.append(Path(rel).as_posix())
elif (ROOT / "CONTEXT.md").is_file():
    context_files.append("CONTEXT.md")
else:
    fail("CONTEXT.md or CONTEXT-MAP.md is required at the repository root")
for rel in context_files:
    require_language_section(rel)


# Handoffs and cross-review reports are committed session artifacts
# (ADR 0006): safe file names and no obvious secrets. The secret patterns are
# a heuristic backstop, not a guarantee; the skills must redact first.
SESSION_ARTIFACT_NAMES = {
    "docs/handoffs": re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9-]+\.md$"),
    "docs/reviews": re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}-[a-z0-9-]+-cross-review\.md$"),
}
SESSION_ARTIFACT_DIRS = tuple(SESSION_ARTIFACT_NAMES)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\."),
    re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{20,}=*"),
)

for dir_rel in SESSION_ARTIFACT_DIRS:
    session_dir = ROOT / dir_rel
    if not session_dir.is_dir():
        continue
    for path in sorted(session_dir.rglob("*")):
        rel = path.relative_to(ROOT).as_posix()
        if path.is_symlink() or path.is_dir():
            if path.is_symlink():
                fail(f"{rel}: session artifacts must not be symlinks")
            continue
        if path.name == ".gitkeep" or path.name in VENDORED_IGNORED_NAMES:
            continue
        if path.parent != session_dir or not SESSION_ARTIFACT_NAMES[dir_rel].match(path.name):
            fail(f"{rel}: file name must match {SESSION_ARTIFACT_NAMES[dir_rel].pattern} directly under {dir_rel}/")
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                fail(f"{rel}:{lineno}: possible secret; redact it before committing")


template_text_files: set[Path] = {
    ROOT / rel for rel in REQUIRED if (ROOT / rel).is_file()
}
for pattern in (
    ".claude/agents/*.md",
    ".codex/agents/*.toml",
    ".gemini/agents/*.md",
):
    template_text_files.update(ROOT.glob(pattern))

for path in sorted(template_text_files):
    try:
        data = path.read_bytes()
    except OSError as exc:
        fail(f"{path.relative_to(ROOT)}: cannot read bytes for newline check: {exc}")
        continue
    if data and not data.endswith(b"\n"):
        fail(f"{path.relative_to(ROOT)}: text file must end with a newline")

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
