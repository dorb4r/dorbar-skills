---
type: process
universe: live          # live | leftover | ghost
status: stub            # stub | verified | stale
verified: {YYYY-MM-DD} {short-sha}   # required when status is verified
entry: {repo-root path:line where the movement starts: route, CLI command, job, handler}
consumes: []            # links to object cards, e.g. [../objects/{cluster}/{card}.md]
produces: []
description: {one line, for the generated _index.md}
---

# {process-name}

{One sentence: the movement, not the nouns.}

## Input → Movement → Output

{Three sentences: what comes in, what happens, what leaves.}

## Why this shape

{What would break if the obvious shortcut existed: the retry, the queue, the second write.}

## Steps

1. {What happens. `{path}:{line}`}
2. {Next hop. `{path}:{line}`}

## If you change this

- **Hits:**
- **Does not hit:**
- **Outside the tree:**

## Surfaces

| Surface | Role |
|---|---|
| {who triggers it, who sees the result} | {role} |

## See

- Objects: {links to the consumes / produces cards}
- Source: `{path}`
