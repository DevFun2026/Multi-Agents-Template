---
name: zoom-out
description: Go up one layer of abstraction and map the modules, entry points and callers around the code under discussion, in the project's domain language. Read-only. Use only when the user asks to zoom out.
argument-hint: "[area, file or symbol]"
disable-model-invocation: true
---

# Zoom out

The user does not know this area of the code well. Go up one layer of abstraction and give them a map.

1. Find the area: the user's argument, or else the code discussed most recently.
2. Read the domain language first: `CONTEXT.md`, or the right context via `CONTEXT-MAP.md`, when the repository has one.
3. Read only what you need to answer:
   - the area's own modules;
   - their entry points;
   - their callers;
   - what they call.
4. Answer with:
   - **Purpose**: one or two sentences, in glossary terms.
   - **Map**: the relevant modules and how they connect (callers → area → dependencies). Use a short list or a small diagram.
   - **Entry points**: where control or data enters the area.
   - **Data flow**: the main path through it, in a few steps.
   - **Read**: the files you read, as `path:line` links, so the user can follow along.

Rules:

- This skill is read-only. Do not edit, create or delete files, and do not run commands that change state.
- Use glossary terms. When the code uses a different name for a glossary term, give both once.
- Say what you did not read, if it limits the map.
