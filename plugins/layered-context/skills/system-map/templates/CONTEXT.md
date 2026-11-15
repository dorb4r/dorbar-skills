# Map: {project} system map (router)

Agent-readable map of this codebase. The code is the source of truth; every card cites it at a commit. This file routes; it holds no facts about the system beyond names.

Mapped at: `{short-sha}` on {YYYY-MM-DD}. Cards carry their own `verified:` line; trust a card's date, not this one.

## Where to go

| You need | Open |
|---|---|
| Where X lives / what X is | `objects/<cluster>/_index.md`, then the card |
| How flow Y works | `processes/_index.md`, then the card |
| What a change to Z hits | [effects.md](effects.md), then each card it names |
| A term you do not recognise | Names below |

## Clusters

| Cluster | Covers | Index |
|---|---|---|
| {cluster} | {one line} | [objects/{cluster}/_index.md](objects/{cluster}/_index.md) |

## Names (product word = code name)

- {Workspace} = `{Tenant}` (`{path}:{line}`)

## Status words

- **live**: in force; implement and cite against it. **leftover**: still present, not the main path. **ghost**: named but not wired; never implement against it.
- **verified** (date + commit + citations) · **stale** (code moved since; re-verify before relying) · **stub** (named, not filled).

## Rules for this folder

- Cite, never restate: a card points at the code that owns a fact. When code and a comment or doc disagree, the code wins and the card says so.
- `_index.md` files are generated: `python -I {skill}/scripts/index.py map/objects/<cluster> map/processes`. Never hand-edit them.
- A PR that changes a mapped path updates its card in the same PR (keep-current rule in the root `AGENTS.md`).
- Check: `python -I {skill}/scripts/map_check.py map` and `python -I {layered-context}/scripts/links.py map`.
