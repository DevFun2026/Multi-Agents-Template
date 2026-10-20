# <Context name>

<!-- Copy to CONTEXT.md at the repository root (ADR 0005). One or two sentences:
     what this context is and why it exists.
     Several bounded contexts? Put one CONTEXT.md in each context's directory and
     list them in a root CONTEXT-MAP.md (format below). -->

## Language

<!-- Only terms specific to this project. General programming concepts (timeout,
     retry, error type) do not belong, even if the code uses them a lot.
     Group terms under ### subheadings when clusters emerge; a flat list is fine. -->

**<Term>**:
<What it IS, in one or two sentences. Bold other terms to show relationships and cardinality, e.g. "a **Condo** has many **Units**".>
_Avoid_: <synonyms people use for the same thing>

## Flagged ambiguities

<!-- A word used for two different things, and the resolution chosen. -->

- "<word>" was used for both **<Term A>** and **<Term B>**. Resolution: <which word means what>.

## Example dialogue

<!-- A short exchange between a developer and a domain expert that uses the terms
     naturally and shows the boundaries between related concepts. -->

> **Dev:** ...
>
> **Domain expert:** ...

<!-- Rules:
     - Be opinionated: pick one word per concept; list the others under _Avoid_.
     - Keep definitions tight: what the thing is, not what it does.
     - Update this file in PHASE 1 when brainstorming settles a new or changed term.

     CONTEXT-MAP.md format (multi-context repositories only):

     # Context map

     ## Contexts

     - [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders

     ## Relationships

     - **Ordering → Billing**: Ordering emits `OrderPlaced`; Billing consumes it.
-->
