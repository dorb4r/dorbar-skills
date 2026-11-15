---
name: system-map
description: >-
  Build and keep current an agent-readable map of a software codebase: object (noun) and
  process (verb) cards on shelves under map/, each citing path:line at a commit, plus an impact
  index that includes consumers outside the tree, so later agents answer "where is X
  implemented", "how does flow Y work" and "what would a change to Z hit" without reading the
  whole repo. Use when asked to map a repo, build a codebase / system / architecture map, run
  impact analysis or blast radius on a change, onboard agents to a large codebase, or when a
  task touches an area that already has a map/ folder.
  Triggers: map this repo, codebase map, system map, architecture map, what would a change hit,
  impact analysis, blast radius, where is X implemented, onboarding agents to a large codebase.
---

# System Map

A **system map** is a shelf of cards that cite the code: what the nouns are, how they move, and what else moves if you touch one. The code stays the source of truth; the map points into it and never becomes a second spec. It is the System map form of ICM, the code-repo counterpart of the `layered-context` skill: `references/app-state.md` shrinks to a short summary that links into `map/`.

Adapted from icm-architect (MIT, (c) 2026 Jake Van Clief; see `../../LICENSE-icm-architect`).

## The rules every card obeys

1. **Cite, don't restate.** Every claim ends in a backticked repo-root `path:line`. A card says why and where; the code says what.
2. **Code wins.** When code disagrees with a comment, doc, ticket or the card itself, the card follows the code and says so.
3. **`verified:` is a date plus a commit plus citations.** `status: stale` is honest; a confident wrong date is not. No citations, no `verified`.
4. **Universe on every card:** `live` (in force), `leftover` (present, off the main path), `ghost` (named but not wired; never implement against it).
5. **Waterfalls are first-order:** `Hits` / `Does not hit` / `Outside the tree`. "Does not hit" names the tempting wrong neighbour.
6. **Small and generated where possible.** A card ≲150 lines. `_index.md` files are written by script, never by hand. A step loads ≤ ~8k tokens: router + an index + the cards it needs.

## When NOT to build one

- The tree is small (roughly under 50 source files, or one module a reader holds in their head): write one `CONTEXT.md` that routes plus a generated index, and stop.
- The person wants a workflow (use `layered-context` stages) or a design doc (that is a spec; the map only cites).
- Nobody will edit this tree again. A map that no PR keeps current rots into a confident lie.

## Answer a question from an existing map

1. Open `map/CONTEXT.md` (the router). Resolve names in its Names list.
2. **Where is X:** the cluster's `_index.md`, then the card, then the cited `path:line`.
3. **How does Y work:** `processes/_index.md`, then the process card's Steps.
4. **What would a change to Z hit:** `map/effects.md`, then every card it names, then each card's Hits and Outside the tree.
5. Before acting on a claim, open the cited line. If the card is `stale`, or `map_check.py` flags it, re-verify it first and fix the card in the same change.

Done when the answer names the cited paths it rests on and the `verified:` commit of each card used.

## Build sequence (gated)

Each step ends at a gate. Stop there; the person (or a cold walk) reads the output before the next step starts. Never move or edit the code being mapped. Detail per step: [reference.md](reference.md).

**1. Inventory. Write no cards.** List the tree (`git ls-files`, top-level dirs, entry points, manifests, CI, `.claude/`, infra). Infer nouns (types, tables, modules, config) and verbs (requests, jobs, commands, pipelines that actually run). Mark each `live` / `leftover` / `ghost`. Note every product-word vs code-name collision. Propose clusters grouped by how an editor asks, not by folder.
*Gate:* the person approves the cluster list, the name collisions, and the proposed `map/` home. Ask them now for outside consumers (other repos, services, scheduled jobs, dashboards) that hardcode anything here.

**2. Catalog.** Create `map/` from [templates/](templates/): `CONTEXT.md` router (≤80 lines), `_templates/object.md` and `process.md`, one stub card (frontmatter only, `status: stub`) per approved noun. Generate indexes: `python -I <this-skill>/scripts/index.py map/objects/<cluster> ...`. Add one routing row to the root `AGENTS.md` and replace `references/app-state.md` with the summary shape in reference.md.
*Gate:* cold walk: "where do I go to understand X?" lands on a card in two hops from `AGENTS.md`; `python -I ../layered-context/scripts/links.py map` passes.

**3. Nouns.** Fill object cards: Why this shape, Shape with citations, Connected to, If you change this, Surfaces. Find referrers with `git grep -n`, `rg`, LSP references, `git log -S`. For a large repo, fan out: one sub-agent per cluster, each writing only its own cluster folder (brief in reference.md). Then one merge pass: dedupe, cross-link, regenerate indexes.
*Gate:* every card in the batch is `verified` (date + commit + citations) or explicitly `stub`/`stale`; `python -I <this-skill>/scripts/map_check.py map` passes; the person spot-reads two cards against the code.

**4. Verbs.** Process cards only for movements that run: Input → Movement → Output, numbered Steps each with a citation, `consumes:` / `produces:` linking object cards. Start from real entry points (routes, CLI commands, queue consumers, cron, CI jobs).
*Gate:* each process card's Steps can be followed hop by hop through the cited lines; `map_check.py` and `links.py` pass.

**5. Impact index.** Write `map/effects.md` from [templates/effects.md](templates/effects.md): "if you change X, open these cards". Then walk it backwards: search for paths, names and endpoints pointing in from CI workflows, `.claude/` agents/hooks/settings, Dockerfiles, IaC, env files, and the owner's list of other services and repos. Record each consumer on `effects.md` and on the card it lands on.
*Gate:* for three changes the person names, effects.md lists what each hits and what it does not, including anything outside the tree; the searched commands are written down.

**6. Re-verify and walk.** Re-check every load-bearing Hits / Does not hit against the code (wrong waterfalls cost more than missing cards). Run the walk test in reference.md. Measure the step load with `python -I ../layered-context/scripts/context_budget.py .`.
*Gate:* walk test passes; `map_check.py`, `links.py` and `context_budget.py` exit 0.

**7. Wire keep-current.** Add the keep-current rule (reference.md) to the root `AGENTS.md` and to the delivery / fold-in step: a PR that changes a mapped path updates its card in the same PR, and the delivery step runs `map_check.py map --since <base>` and re-verifies every flagged card.
*Gate:* the rule is in `AGENTS.md`; a dry run of `map_check.py --since HEAD~5` on the current branch reports only cards that really cite changed paths.

## Keep it current (every later change)

- Before editing a mapped area: open its card, follow the cited lines, trust code over card.
- After editing: `git diff --name-only <base>` against the cards' cited paths (`map_check.py map --since <base>` does this). Re-verify each flagged card: update citations, `verified:` date and commit, or set `status: stale` with one line saying what moved.
- New noun or flow: copy from `map/_templates/`, add a row to `effects.md` if it changes impact, regenerate the index.
- Removed code: set the card `ghost` or move it to `_archive/` (never read); never leave a `live` card citing a deleted path.

## Scripts

- `scripts/index.py` (vendored from icm-architect, MIT): writes `_index.md` per folder from card frontmatter (title, description, status).
- `scripts/map_check.py`: flags verified cards without date+commit or citations, missing paths, lines past end of file, cited paths changed since the card's commit (or `--since REF`), cards over 150 lines.
- `../layered-context/scripts/links.py`: every relative link and `consumes:` / `produces:` path resolves.
- `../layered-context/scripts/context_budget.py`: entry, router and step-load budgets.

## Reference

[reference.md](reference.md): target tree, card section rules, finding evidence in code, outside-consumer checklist, fan-out brief, `app-state.md` summary shape, keep-current rule text, walk test, failure modes. Read at the step that needs it.
