# Layered context — templates and procedures

Copy these, then replace every line with project-real content. Contents: Folder shapes · Layer 0 `AGENTS.md` · Layer 1 router · Layer 2 stage contract · Layer 3 belief files · Layer 3 standards · Wiring the scripts · Restructure.

## Folder shapes

**Minimal** (make a repo legible to agents):

    <repo>/
      AGENTS.md                 # Layer 0 — entry file (routes only)
      CLAUDE.md                 # one line: @AGENTS.md
      CONTEXT.md                # Layer 1 — router
      references/               # Layer 3 — factory
        standards.md            #   code + test conventions
        domain.md               #   domain terms, invariants
        app-state.md            #   beliefs: what the system does now
        decisions.md            #   beliefs: decisions in force now
      _archive/                 # retired, never read
      scripts/links.py, scripts/context_budget.py

**Pipeline** (a repeated multi-stage workflow) adds:

      stages/
        01_plan/CONTEXT.md      # Layer 2 — contract
        02_build/CONTEXT.md
        03_review/CONTEXT.md
        04_deliver/CONTEXT.md   #   includes the fold-in step
      _templates/               # blank starters: a new run is a copy (plan, PROGRESS.md)
      runs/<task-id>/           # Layer 4 — 01_plan.md, 01_check.md, 02_build.md, PROGRESS.md …

Large `references/` collections get their own `references/CONTEXT.md` router (the Layer 1 pattern, applied recursively). Monorepos: a root `AGENTS.md` + router, then one `CONTEXT.md` per package.

---

## Layer 0 — `AGENTS.md` (≤60 lines)

    # <Project>

    <One sentence: what this repo is and what leaves it.>

    ## Where things live
    | Folder | Holds |
    |---|---|
    | `CONTEXT.md` | the router — start here for any task |
    | `stages/` | the workflow, in order (one contract each) |
    | `references/` | standards, domain, current app state and decisions |
    | `runs/<task-id>/` | this task's working files |
    | `_archive/` | retired material — never read it |

    ## How to load context
    Read this file, then `CONTEXT.md`, then only your stage's contract and the Inputs it lists.

    ## Rules
    - Tests: `<exact command>`. Build: `<exact command>`. Lint: `<exact command>`.
    - Changes go <git/PR workflow>.
    - <other non-negotiables: i18n, security gates>.
    - If two context files disagree, say so and stop. Do not choose.

`CLAUDE.md` (and `GEMINI.md` if used) contains exactly one line: `@AGENTS.md`.

## Layer 1 — `CONTEXT.md` (router, ≤80 lines)

    # Router

    | If | Go to | Stop at |
    |---|---|---|
    | starting a new task | `stages/01_plan/CONTEXT.md` | the plan's check |
    | a stage's check passed | the next numbered stage | that stage's check |
    | asked for status | `runs/<task-id>/` and its `NN_check.md` files | report what exists |
    | resuming a paused task | `runs/<task-id>/PROGRESS.md` | the note's Next action |
    | a question about current behaviour | `references/app-state.md` | — |

    ## Maintenance
    Next context-hygiene review: <YYYY-MM-DD or "after 5 merged features">, owner <role>.

## Layer 2 — `stages/NN_<name>/CONTEXT.md` (contract, ≤80 lines)

    # NN_<name> — <the job in five words>

    One job: <the single thing this stage does>.

    ## Inputs
    - Working (this run): `runs/<task-id>/<NN-1>_<prev>.md`
    - Reference (every run): `references/standards.md`
    - Reference (every run): `references/decisions.md` — section "<Section name>" only
    - Example (optional): `examples/` — one real input and one good output

    Do NOT load: other stages' contracts, past `runs/`, `_archive/`, the whole `references/` folder.

    ## Process
    1. If an input is missing or empty, stop and say which.
    2. <transform, following the reference constraints>.
    3. <a step that is code names its command: run `pnpm test --filter api`>.

    ## Outputs
    - `runs/<task-id>/NN_<name>.md`

    ## Check
    <one concrete act: `pnpm test` exits 0 / a reviewer sub-agent answers <question> / the owner reads the plan>.
    A non-person check writes `runs/<task-id>/NN_check.md`, first line `pass` or `fail: <why>`. A fail stops the run.

**Delivery stage — the fold-in.** Add to its Process:

    N. Fold in: merge this run's lasting decisions into `references/decisions.md` (rewrite the
       affected lines in place, with provenance); update `references/app-state.md` for any changed
       behaviour; move `runs/<task-id>/` to `_archive/runs/`; run
       `python -I scripts/context_budget.py --provenance` and `python -I scripts/links.py` — both exit 0.

**Enforcing stops**, weakest to strongest: a "stop after each stage" line in the router; a permission mode that asks before edits; a hook or required CI check for anything irreversible (push to main, deploy, migrations).

## Layer 3 — belief files: `references/decisions.md`, `references/app-state.md`

State what is true **now**. One bullet per belief, grouped by the moment it is needed (heading names the trigger), each ending in provenance:

    # Decisions in force

    _Beliefs, not records: rewrite a line when it changes; history lives in git. Reviewed: 2026-11-15._

    ## Data layer (read before touching persistence)
    - Postgres is the only primary store; no new databases without an ADR-level discussion
      (since 2026-09-02, by platform-team, ref #88)
    - Cache is Valkey, accessed only through `src/cache/` (since 2026-11-03, by platform-team, ref #142;
      recheck: if managed Redis pricing changes)

    ## API (read before adding endpoints)
    - …

Rules:
- A changed decision **replaces** its line the same day; never add "Update:" below it.
- No provenance → no trust: a line without a date and a source cannot be doubted, so it cannot be corrected.
- Keep the always-loaded part small; detail goes in a deeper file behind one pointer line.
- Contracts point at the section they need (`references/decisions.md` — section "Data layer"), not the whole file.
- `app-state.md` cites code (`src/cache/index.ts:12`) and states `verified at <commit>, <date>`; code wins over comments. For a large codebase, keep it a short summary that links into a `map/` built with the **system-map** skill.

## Layer 3 — `references/standards.md`

    # Standards

    ## Code
    - <patterns to match, with a pointer to an exemplar file>

    ## Tests
    - <how to run; what "done" means>

    ## Review
    - <what blocks a change vs. a nit>

---

## Wiring the scripts

Both scripts are standard-library Python, run with `-I`, and treat the folder above `scripts/` as the root.

- `links.py` (from icm-architect, MIT): every relative link, `@import` and Inputs path resolves.
- `context_budget.py`: file budgets, per-stage step load, and (`--provenance`) belief-line hygiene. Override budgets in `.context-budget.json`.

CI (GitHub Actions step):

    - name: Context guards
      run: |
        python -I scripts/links.py
        python -I scripts/context_budget.py --provenance

Or pre-commit, as a local hook running the same two commands.

---

## Restructure — turning an existing dump into layers

1. **Inventory, move nothing.** List the tree. For each context file note what it is, when it was last touched (`git log -1 --format=%cd -- <file>`), and its size.
2. **Find the hidden shape.** The mess usually contains a real workflow or a real set of references that grew without a skeleton: extract it, don't replace it.
3. **Classify every file** (and every section of a monolithic CLAUDE.md):
   - **catalog** → `AGENTS.md` / `CONTEXT.md` (routing only)
   - **contract** → a stage `CONTEXT.md`
   - **factory** → `references/` (stable rules, current beliefs)
   - **product** → `runs/<task-id>/` (plans, drafts, task notes)
   - **dead** → stale, duplicated or superseded → proposed for `_archive/`, never deleted
4. **Find every referrer before proposing a move.** `grep -rn "<filename>"` across the repo; CI workflows; `.claude/` agents, hooks, commands and settings; docs sites; scripts; other repos and scheduled jobs (ask the owner — nothing in the tree names them). A file with a live referrer moves only if every referrer is updated in the same change.
5. **Propose before moving.** Present the target tree and a migration map (old path → new path, role, referrers). Get approval.
6. **Migrate on a branch.** `git mv` (history follows). Before renaming, check case-folded collisions (`context.md` vs `CONTEXT.md` on macOS/Windows). Verify parity (file count, content), dedupe toward one home per fact, convert decisions to belief format, reduce `CLAUDE.md` to `@AGENTS.md`.
7. **Validate:** both scripts exit 0, then the walk test.
