# System map reference

Detail for the build sequence in [SKILL.md](SKILL.md). Each heading names the step that reads it.

## Target tree (step 1 proposes it, step 2 creates it)

    <repo>/
      AGENTS.md                 # entry: routes only, ≤60 lines; one row points at map/CONTEXT.md
      CLAUDE.md                 # @AGENTS.md
      references/app-state.md   # short summary that links into map/ (shape below)
      map/
        CONTEXT.md              # router ≤80 lines: where to go, clusters, names, status words
        effects.md              # change-impact index, incl. consumers outside the tree
        _templates/             # object.md, process.md (copied from this skill's templates/)
        objects/
          <cluster>/            # cards + generated _index.md
        processes/              # cards + generated _index.md; only after nouns exist
        _archive/               # retired cards; never read

- Put `map/` at the repo root (or beside existing `docs/`), never inside `src/`, and never scatter cards through the tree being mapped.
- Create `processes/` and `effects.md` only when step 4 / 5 fills them. Three verified clusters beat seven imagined ones.
- Monorepo: one `map/` at the root with a cluster per package, or one `map/` per package with the root `map/CONTEXT.md` routing to each. Pick the one that keeps a step under ~8k tokens.
- File names: kebab-case noun (`objects/billing/invoice.md`) or verb phrase (`processes/checkout-submit.md`).

## Inventory (step 1)

Write findings into the conversation or a scratch file, not into `map/`.

- **Tree and entry points:** `git ls-files | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -40`; manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`), `main`/`index`/`app` files, route tables, CLI definitions, job/queue registrations.
- **Nouns:** types and classes that cross module boundaries, DB tables / migrations / schemas, config objects, persisted files, public API payloads, events and messages.
- **Verbs:** request handlers end to end, background jobs, cron, CLI commands, build / deploy / release, data migrations, agent workflows. Only movements that run.
- **Universe:** `ghost` = declared but never called (no referrers, feature-flagged off forever, docs of functions that do not exist); `leftover` = still called, superseded by a newer path; everything else `live`. Prove ghosts with an empty `git grep -n <symbol>` across the whole repo, then ask the owner about outside callers.
- **Name collisions:** product word vs code name ("Workspace" = `Tenant`), and two code names for one thing. They go in the router's Names list.
- **Clusters:** grouped by the question an editor asks ("billing", "auth & sessions", "agent runtime"), 3-10 cards each.
- A code-graph or AST tool may draft the noun/edge list. Treat its output as proposals to verify; paste none of it into cards.

## Card sections (steps 3 and 4)

Copy [templates/object.md](templates/object.md) and [templates/process.md](templates/process.md). Every section earns its line or is deleted.

| Section | Holds | Does not hold |
|---|---|---|
| First sentence | what it is; product word and code name | history |
| Why this shape | the load-bearing reason; what breaks under the obvious simplification | a field tour |
| Shape | keys, invariants, owning files, each with `path:line` | pasted code or full schemas |
| Connected to | owns / owned-by / joins / looks-like-but-is-not, as card links | prose |
| If you change this | Hits, Does not hit, Outside the tree: first order only | the whole transitive closure |
| Surfaces | who reads / writes it | |
| See | the owning source file; at most one doc that is still true | an essay |

- **Citation format:** backticked repo-root path and line: `src/billing/invoice.ts:42` or a range `:42-60`. Cite the definition, not an import. `map_check.py` reads exactly this format.
- **Frontmatter:** `status: stub | verified | stale`; `verified: YYYY-MM-DD <short-sha>` (the commit you read, from `git rev-parse --short HEAD`); `universe`; `entity` (object) or `entry` (process); `description` (one line, shown in `_index.md`).
- **When code and words disagree:** cite the code, then one line: "Comment at `x.ts:10` says retries 3x; code retries 5x (`x.ts:31`)."
- **Over 150 lines:** split by sub-noun or move detail back to the code; a card that needs more is restating the source.

## Finding evidence in code (steps 3-5)

- Definition: LSP go-to-definition, or `git grep -n "class Invoice\b\|type Invoice\b\|interface Invoice\b"`.
- Referrers: LSP find-references, then `git grep -n -w Invoice` (catches dynamic and string uses LSP misses), then the table name, route string, env var and file path as literals.
- History and intent: `git log -S '<symbol>' --oneline`, `git log --follow -p <file> | head`, `git blame -L <a>,<b> <file>` for why a line is shaped that way.
- Runtime wiring: DI containers, plugin registries, route tables, reflection, string-keyed dispatch. Grep the string key, not only the symbol.
- Record the commit you read at (`git rev-parse --short HEAD`); a working tree with uncommitted edits to cited files is not verifiable. Commit or stash first.

## Outside consumers (step 5)

Walk it backwards: what points INTO the tree is invisible from inside the code. Search the literals (paths, binary names, endpoints, table names, env vars, package names) in:

- `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `Makefile`, pre-commit config.
- `.claude/` (agents, hooks, commands, `settings.json`), `AGENTS.md` / `CLAUDE.md` in this and sibling repos, MCP configs.
- `Dockerfile`, `docker-compose*`, Helm / k8s manifests, Terraform / Pulumi, `.env*` templates, monitoring and alert configs.
- Other services or repos: ask the owner. Org-wide code search (e.g. `gh search code '<literal>' --owner <org>`) when available.

Record each hit twice: a row in `effects.md` and a line under **Outside the tree** on the card it lands on. Write the commands run under "Searched:" so the next agent knows what was not covered.

## Fan-out brief (step 3 on a large repo)

One sub-agent per cluster, run in parallel; they share nothing but the router and templates. Brief each with:

    Map the <cluster> cluster of <repo> at commit <sha>.
    Read: map/CONTEXT.md, map/_templates/object.md, the stub cards in map/objects/<cluster>/.
    Code to read: <paths>. Write ONLY inside map/objects/<cluster>/. Do not edit code or other clusters.
    For each stub: fill every section; cite repo-root `path:line`; set status verified with
    `verified: <date> <sha>` only if every Shape line has a citation, else leave stub or stale.
    Hits / Does not hit: first order. Note any reference that points into another cluster as a
    card link, and any outside consumer you find.
    Done when: every stub is verified or has a one-line reason it is not, and
    `python -I <skill>/scripts/map_check.py map` reports nothing for your cluster.
    Report: cards written, cross-cluster links you assumed, open questions.

Merge pass (one agent, after all return): resolve cross-cluster links, dedupe cards two agents both wrote (one home per fact), regenerate every `_index.md`, run `map_check.py` and `links.py`, spot-verify two cards per cluster against the code.

## `references/app-state.md` summary shape (step 2)

The map replaces the long-form app-state. Keep it a page that answers "what does the system do now" and links down. Each bullet ends with provenance so `context_budget.py --provenance` passes.

    # <Project> current behavior (summary; detail in map/)

    **Keep current.** The delivery step updates this and the touched cards on every ship.

    - <Subsystem>: <one line of behavior>. See [map/objects/<cluster>/_index.md](../map/objects/{cluster}/_index.md). (since YYYY-MM-DD, <sha>)
    - <Main flow>: <one line>. See [map/processes/<flow>.md](../map/processes/{flow}.md). (since YYYY-MM-DD, <sha>)

## Keep-current rule (step 7)

Paste into the root `AGENTS.md` (one line) and into the delivery / fold-in stage contract (the block):

    - Map: before changing code, open its card via `map/CONTEXT.md`; a PR that changes a mapped path updates that card.

    ## Gate: map current
    1. Run `python -I <skill>/scripts/map_check.py map --since <base-branch>`.
    2. For each "re-verify" line, open the card, re-read the cited lines, then either update
       citations + `verified: <today> <sha>` or set `status: stale` with one line on what moved.
    3. New noun or flow: add a card from `map/_templates/`, an `effects.md` row if impact changed,
       and regenerate `_index.md`.
    4. Done when `map_check.py` exits 0 or every remaining line is a deliberate `stale`.

## Walk test (step 6)

A cold agent with no memory of the repo:

1. From the root `AGENTS.md`, is `map/CONTEXT.md` one hop away?
2. From the router alone, can it say what each colliding name means?
3. One object card: does it cite source at a commit, state the why, and give Hits / Does not hit?
4. From `effects.md`: for a stated change, can it name what is hit inside and outside the tree, and what is not?
5. Follow one citation: does it land on the definition the card describes?
6. Do `AGENTS.md` + router + one index + two cards stay under ~8k tokens?

A failure is fixed by splitting or moving files, not by adding a "how to read this map" essay.

## Failure modes

- Aspiration, tickets or design docs mapped as `live`. They are `ghost` until code wires them.
- Cards that paraphrase the code at length: a second spec that drifts. Point at the owning line instead.
- `verified` with no commit, or a commit nobody read at. Prefer `stale`.
- Empty `processes/` or `effects.md` scaffolded "for later".
- Hand-edited `_index.md`: overwritten on the next run, and wrong until then.
- An impact index that only walks outward: CI, hooks, infra and other repos break silently.
- Later sessions reading all of `objects/`: the router and indexes exist so a step loads three files, not thirty.
- Mapping without keep-current wired: the map is right for one week and wrong after.
