---
type: object
cluster: {cluster}
universe: live          # live | leftover | ghost
status: stub            # stub | verified | stale
verified: {YYYY-MM-DD} {short-sha}   # required when status is verified; keep the old value when stale
entity: {repo-root path of the owning file}
description: {one line: what it is, for the generated _index.md}
---

# {Name}

{One sentence. If the product word and the code name differ, say both: "Workspace (code: `Tenant`)".}

## Why this shape

{The load-bearing why, not a field tour. What would break if it were the obvious simpler shape.}

## Shape

- {keys, invariants, constraints, owning files: each line ends with its citation}

Citations: `{path}:{line}` (repo-root paths; `{path}:{start}-{end}` for a range)

## Connected to

- **owns:**
- **owned-by:**
- **joins:**
- **looks-like-but-is-not:** {the near-twin an editor will confuse it with}

## If you change this

- **Hits:** {first-order only: each a card link or a cited path}
- **Does not hit:** {the obvious next noun that is the wrong one, and why}
- **Outside the tree:** {CI workflow, `.claude/` hook or agent, infra config, other service or repo that hardcodes it; "none found (searched: ...)" is a valid entry}

## Surfaces

| Surface | Role |
|---|---|
| {service, job, UI, agent, person} | {reads / writes / none} |

## See

- Source: `{path}`
