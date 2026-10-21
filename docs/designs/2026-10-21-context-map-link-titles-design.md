# Design: Accept link titles on CONTEXT.md links in CONTEXT-MAP.md

- Status: Approved (2026-10-21)
- Date: 2026-10-21
- Spec: [../specs/2026-10-21-context-map-link-titles-spec.md](../specs/2026-10-21-context-map-link-titles-spec.md)
- ADRs: none. ADR 0005 defines `CONTEXT-MAP.md`; this only widens which link syntax counts.

## Overview

Add one shared optional title fragment to both patterns in `scripts/validate_template.py`:

```python
LINK_TITLE = r"""(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?"""
CONTEXT_MAP_LINK = re.compile(
    r"\]\(\s*<?((?:[^)\s#>]*/)?CONTEXT\.md)(?:#[^)\s>]*)?>?" + LINK_TITLE + r"\s*\)"
)
CONTEXT_MAP_REF_LINK = re.compile(
    r"^\s*\[[^\]]+\]:\s*<?((?:[^\s>#]*/)?CONTEXT\.md)(?:#[^\s>]*)?>?" + LINK_TITLE + r"\s*$",
    re.MULTILINE,
)
```

The capture group, and the path checks applied to it, stay exactly as they are.

## Components

| Component | Change |
|---|---|
| `scripts/validate_template.py` | `LINK_TITLE` and the two patterns above |
| `scripts/test-validator-mutations.py` | 3 accepted cases and 1 rejected case (spec acceptance criteria) |

## Alternatives considered

- **Use a Markdown parser library.** It is a new dependency for one check, and the template keeps the validator dependency-light.
- **Document that titles are unsupported.** Two reviewers flagged the gap, and the fix is a few characters.

## Risks

- Titles that contain their own closing quote or bracket are not matched. CommonMark allows escaped quotes in titles. Such a link would not be counted and the validator would report it, so the failure stays visible.

## Test strategy

The mutation and accepted cases listed in the spec.
