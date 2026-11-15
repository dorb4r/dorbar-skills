---
type: review
description: {Which artifact was compared against the bundle, and when.}
status: open   # open · resolved
---

# Gap review: {artifact} against {bundle}

**Artifact:** `{path or URL}`, version {date or commit}. **Bundle plan:** [plan](../plan.md).
**Scope:** {the concepts compared: all in the plan, or a named subset}.

## Missing (in the bundle, absent from the artifact)

| Concept | Why it matters here | Where it would go |
|---|---|---|
| [{concept}](../concepts/{slug}.md) | {one line} | {section of the artifact} |

## Conflicting (the artifact says otherwise)

| Concept | The artifact says | The source says | Resolve by |
|---|---|---|---|
| [{concept}](../concepts/{slug}.md) | {artifact location}: {paraphrase} | {paraphrase, cited (key position)} | {fix the artifact, or ask the speaker} |

## Fine (covered and consistent)

- [{concept}](../concepts/{slug}.md): {artifact location}

## Not in the sources

- {What the artifact asserts that no source supports: keep as the author's own, or cut.}
