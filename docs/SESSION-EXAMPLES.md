# Session Examples

## 1. Research decision

Prompt:

```text
Follow AGENTS.md.

Objective:
Compare PostgreSQL and ClickHouse for an analytics system with high ingest volume and interactive aggregate queries. Make a recommendation.
```

Expected routing:

```text
MAIN
├─ researcher: PostgreSQL official capabilities
├─ researcher: ClickHouse official capabilities
├─ researcher: operational/cost/failure-mode comparison
└─ optional reviewer: challenge assumptions

MAIN -> compare evidence -> decision
```

## 2. Existing codebase feature

Prompt:

```text
Follow AGENTS.md.

Objective:
Add API rate limiting to this service without breaking existing authentication or tests.
```

Expected routing:

```text
MAIN
├─ explorer: locate request/auth path + tests
├─ researcher: framework-native rate-limit behavior if docs are needed
└─ security reviewer: identify bypass/trust-boundary risks

MAIN -> design
  -> implementer: bounded change
  -> reviewer
  -> tests/verification
  -> MAIN final
```

## 3. UI feature

Prompt:

```text
Follow AGENTS.md.

Objective:
Build the account settings page from the product requirements. It must be responsive and WCAG-aware.
```

Expected routing:

```text
MAIN
├─ explorer: identify frontend stack and design-system files
└─ UI UX Pro Max: establish design direction

MAIN -> freeze design constraints
├─ implementer: page/component implementation
└─ uiux reviewer: accessibility/responsive/interaction review

verification -> MAIN final
```

## 4. Security review

Prompt:

```text
Follow AGENTS.md.

Objective:
Review the repository for token exfiltration, unsafe local-disk scanning, secret leakage, and risky network behavior.
```

Expected routing:

```text
MAIN
├─ explorer: enumerate entry points, network clients, filesystem access
├─ security reviewer: secrets/auth/exfiltration analysis
├─ researcher: verify third-party dependency behavior when necessary
└─ reviewer: challenge false positives / missing cases

MAIN -> evidence reconciliation -> risk-ranked conclusion
```

## 5. When not to spawn

Do not spawn agents for work such as:
- renaming one variable;
- explaining a known local function already in context;
- changing a tiny config value;
- answering a simple deterministic question.

The goal is not agent count. The goal is better total efficiency.
