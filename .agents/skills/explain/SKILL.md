---
name: explain
description: Re-pitch the previous answer because it did not land - short context first, then the point, in simplified language and the project's domain terms. Writes nothing. Use only when the user asks for it.
argument-hint: "[what was unclear]"
disable-model-invocation: true
---

# Explain

The user did not understand your last answer. Re-pitch it.

1. Read the domain language: `CONTEXT.md`, or the right context via `CONTEXT-MAP.md`, when the repository has one.
2. Start with one or two sentences of context: where we are and what problem the answer solves.
3. Then give the point, in short sentences:
   - one idea per sentence;
   - active voice;
   - concrete nouns;
   - no unexplained jargon.
   - When you answer in English, follow ASD-STE100 Simplified Technical English. In another language, keep the same discipline.
4. Use glossary terms exactly. If you must use a term that is not in the glossary, define it in one line.
5. If the user said what was unclear, answer that part first.
6. End with one question that checks understanding, or with the single next action.

Rules:

- Answer in the user's language.
- Do not add new content that was not in the previous answer, unless the user needs it to understand.
- This skill writes no files.
