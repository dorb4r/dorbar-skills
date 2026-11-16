# Layered context — templates and procedures

Copy these, then replace every line with project-real content. Contents: Folder shapes · Interview mode · Layer 0 `AGENTS.md` · Layer 1 router · Layer 2 stage contract · Human checks and enforcing stops · Layer 3 belief files · Layer 3 standards · Let it harden · Wiring the guards · Replication and seeded-defect tests · Restructure.

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
      .context-budget.json      # optional: this repo's own limits, each with a "why"
      .github/workflows/context.yml   # calls the shared context-guards action (no script copies)

**Pipeline** (a repeated multi-stage workflow) adds:

      stages/
        01_plan/CONTEXT.md      # Layer 2 — contract
        02_build/CONTEXT.md
        03_review/CONTEXT.md
        04_deliver/CONTEXT.md   #   includes the fold-in step
      _templates/               # blank starters: a new run is a copy (plan, PROGRESS.md)
      runs/<task-id>/           # Layer 4 — 01_plan.md, 01_check.md, 02_build.md, PROGRESS.md …

Large `references/` collections get their own `references/CONTEXT.md` router (the Layer 1 pattern, applied recursively). Monorepos: a root `AGENTS.md` + router, then one `CONTEXT.md` per package.

## Interview mode (no repo to read)

For a recurring job that ends with a person — a weekly report, client onboarding, a newsletter, packaging a recorded session. The input is the owner's head, so the survey is an interview. Which job to take first is decided before this, with **workflow-audit** (agent-workflows plugin); one request gets one audit and one interview, in that order.

If `runs/<YYYY-MM-DD>-audit-<job-slug>/01_audit.md` exists, seed the tree from it first: its steps table answers Inputs, Outputs and Checks; its labels and verdicts answer Decisions and Limits; its outcome section answers Receiver. Ask only the branches it leaves open or marks `unknown`, and adopt that run folder for the workspace.

Run the interview with the **grilling** skill, seeding the design tree with these branches:
- **Inputs** — what comes in, from where, how often; which tools you use at each point.
- **Decisions** — what you decide along the way, and which of those are taste and which have one right answer.
- **Outputs** — what goes out, in what form, named how.
- **Receiver** — who gets it and what they do next with it.
- **Checks** — where you stop to look before going on, and what you look for.
- **Limits** — where you do not want AI at all; what is sensitive; who is accountable if it goes wrong.

If grilling is not installed: ask the same branches in rounds, each question with a recommended answer.

A slower alternative start: the owner writes one paragraph per step of the job (the data it touches, the people involved, what it needs, what it does). The steps are the nodes; what passes between them is the flow.

Map the answers onto the layers:
- Each place the owner stops to check becomes a stage; its contract's Check is that human check.
- A data source gets a landing folder in the run (`runs/<id>/00_inputs/`); working notes on it get their own stage.
- A step with one right answer (counting, totalling, renaming, formatting) becomes a script; a step that reads and judges stays with the agent.
- Anything that never changes between runs (voice, templates, rules) goes in `references/`, read by every stage that needs it.
- "Where you do not want AI" and anything irreversible (sending, publishing, paying) become enforced stops (below), not just rules.

Done when every branch is answered, every pause point is a named stage with its human check, and the owner confirms the stage list.

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
    | `_archive/` | retired material — task work never reads it |

    ## How to load context
    Read this file, then `CONTEXT.md`, then only your stage's contract and the Inputs it lists.

    ## Naming
    - Runs: `runs/<YYYY-MM-DD>-<slug>/`. Stage outputs: `NN_<stage>.md`.
    - Drafts: `<slug>-draft-v<N>.md`; the accepted one drops `-draft`.
    - Exception: attempts inside a retried Check are `NN_attempt-K.md` (the bounded-loop skill,
      agent-workflows plugin); only the accepted stage output follows the names above.

    ## Rules
    - Tests: `<exact command>`. Build: `<exact command>`. Lint: `<exact command>`.
    - Changes go <git/PR workflow>.
    - <other non-negotiables: i18n, security gates>.
    - If two context files disagree, say so and stop. Do not choose.

Naming rules let an agent find "last week's draft" by path, with no index or database. Keep the block to a few lines; it is the only content the entry file holds beyond routes and rules.

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

    ## Pipeline
    | Stage | Command | Makes | Human check |
    |---|---|---|---|
    | 01_plan | — | `01_plan.md` | owner reads the plan |
    | 02_build | `pnpm test --filter api` | the change + `02_check.md` | — |
    | 03_review | — | `03_review.md` | reviewer approves the PR |

The Pipeline table is optional: one row per stage, so the whole workflow reads on one screen. Each row repeats only names; the stage contract stays the one home for its detail.

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

    Do NOT load: other stages' contracts, past `runs/`, `_archive/`, the whole `references/` folder,
    raw sources an earlier stage already distilled.

    ## Tools
    - Skills: `<skill-name>` — <when in this stage>. MCP: `<server>` — <what for>.

    ## Process
    1. If an input is missing or empty, stop and say which.
    2. <transform, following the reference constraints>.
    3. <a step that is code names its command: run `pnpm test --filter api`>.

    ## Outputs
    - `runs/<task-id>/NN_<name>.md`

    ## Check
    <one concrete act: `pnpm test` exits 0 / a reviewer sub-agent answers <question> / the owner reads the plan>.
    Human check: <who looks at what, or "none — runs through">.
    A non-person check writes `runs/<task-id>/NN_check.md`, first line `pass` or `fail: <why>`. A fail stops the run.

Notes on the contract:
- **Tools** lists only what this stage uses, so skills and MCP servers load where they are needed instead of everywhere. Omit the section when there are none.
- **Raw versus distilled.** Once a stage turns a raw source (a transcript, an export, research papers) into a distilled output, every later stage and every later run lists the distilled file as its Input. The folder structure decides what counts as signal; the agent is not asked to find it again.
- **Scripts print the next step.** A stage script ends by printing what comes next (`Next: clean raw.txt into cleaned.md — human pass`), so the run stops at the right place by itself.
- **Cheap preview before an expensive stage.** Before a stage that is slow, costly or hard to undo (render, bulk send, migration, publish), add a check on a cheap preview of its result: a timed text outline, a contact sheet of stills, a dry run, a diff. Fixing a line of text is cheaper than redoing the finished thing.

**Delivery stage — the fold-in.** Add to its Process:

    N. Fold in: merge this run's lasting decisions into `references/decisions.md` (rewrite the
       affected lines in place, with provenance); update `references/app-state.md` for any changed
       behaviour; move `runs/<task-id>/` to `_archive/runs/`; run the context guards
       (reference.md → Wiring the guards, local command) — exit 0.

## Human checks and enforcing stops

**Where a person looks.** Name the human check in every contract, and place one only where the person's taste or judgement changes the result: the script a voice will read, the storyboard before animation, the transcript before names are copied into six documents. Put it at the earliest point where an error would spread. Deterministic stages (transcribing, rendering, a passing test suite) run through without one. A human check is more than yes/no: the person may edit, cut or add, and the edited file is what the next stage reads.

**How far to run** is chosen per invocation ("only do stage 1", "run it all and stop at the review") — the stages are where it can stop.

**Enforcing stops**, weakest to strongest:
1. A "stop after each stage and wait for me" line in the router — the agent reads it and usually follows it.
2. A permission mode that asks before edits or commands (or a plan-only mode).
3. A hook, deny rule or required CI check, which blocks the action whatever the text says.

A line of text is a request. Anything that must never happen without a person — sending email, publishing, pushing to main, deploying, migrations, deleting — gets level 2 or 3, with the router line kept as the explanation.

**Check types.** A stage's Check is single-shot by default: run once, pass or fail. When a failed check may be retried with a fix, use the **bounded-loop** skill (agent-workflows plugin: budget, stop conditions, keep the best attempt). When the check is a judgement call repeated across many items, use **decision-gates** (agent-workflows plugin: confidence routing). Both plug into this contract's Check section; neither changes the contract shape.

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

## Let it harden

- **Same fix twice → fix the file.** When you correct the same thing in two runs, the cause is a contract, a reference or a template. Edit that file; every later run picks it up. Do not carry the correction in your head or in a run.
- **Script a step only when the answer is the same every time**, not when it depends on taste. Ask the agent to write it into `scripts/`, then run it on an input you already did by hand and diff the two outputs. A wrong script is wrong the same way every run, so check it properly once. Only then does the contract name its command.
- **Instruction edits are config changes.** Changing a contract, a reference rule or `AGENTS.md` changes later behaviour. Change one rule at a time, rerun the same task on the same input, and keep the before/after output diff in the run folder. Keep the change only if the result improved against the same criteria.

---

## Wiring the guards

The guards live in one place: this skill's `scripts/` in `dorb4r/dorbar-skills` (public), with their license beside them. Product repos **use** them, pinned to a commit SHA; they never copy them, so a fix lands everywhere by bumping one SHA.

- `links.py` (adapted from icm-architect, MIT): every relative link, `@import` and Inputs path resolves; `#section` is stripped; inputs outside `runs/` must exist.
- `context_budget.py`: file budgets, step load for every `CONTEXT.md` with an Inputs heading, and belief-line provenance (`references/decisions*`, `references/app-state*`, globbed; none found is a failure).
- `context_guards.py`: runs both; exit 1 if either fails.

Inputs format both scripts parse: a heading starting with "Inputs", then bullets of backticked paths; a path may end in `#section`; a bullet starting "Do NOT load" is skipped.

**The repo keeps only its config.** `.context-budget.json` overrides limits, each with a reason:

    {"CONTEXT.md": {"lines": 80, "tokens": 1000, "why": "<reason, who, date>"},
     "belief_globs": ["references/decisions/**/*.md"]}

**CI** — `.github/workflows/context.yml`:

    name: context
    on:
      pull_request:
      push:
        branches: [main]
    permissions:
      contents: read
    jobs:
      guards:
        name: context guards
        runs-on: ubuntu-latest
        timeout-minutes: 5
        steps:
          - uses: actions/checkout@v4
          - uses: dorb4r/dorbar-skills/.github/actions/context-guards@<commit sha>  # layered-context@<version>
            with:
              blocking: "true"      # "false" while the repo is mid-migration: warn only
              # root: "."  skip: "vendor docs-site"  provenance: "true"

**Local** (same code, same pin):

    uvx --from "git+https://github.com/dorb4r/dorbar-skills@<commit sha>#subdirectory=plugins/layered-context/skills/layered-context/scripts" context-guards

`pipx run --spec "<same git URL>" context-guards` works too. An agent with this skill installed runs `python3 -I <this skill's dir>/scripts/context_guards.py <repo root>`.

**Updating the pin.** Bump the SHA in the workflow (and any local alias) in its own PR; the guard output in that PR shows what the new version flags. The action's self-test (`tests/context-guards/`) runs in `dorbar-skills` before any SHA is published.

---

## Replication and seeded-defect tests

Both run in a fresh sub-agent with no conversation context, after the walk test passes.

**Replication** — checks the output is reproducible, not just that the map navigates. Give it only the workspace's markdown files and one sample input the owner has already processed:

    You have this workspace and one input: <path>. Start at AGENTS.md, follow only its pointers,
    and run the job end to end, stopping at each human check as the contracts say. Write outputs
    where the contracts say. List every point where you had to guess, and what you guessed.

Diff its output against the owner's. Each difference and each listed guess is an assumption that lives in someone's head: write it into the contract or reference that should hold it, then rerun. Automate a stage that still needs a person only after its output stays consistent across many runs.

**Seeded defect** — checks the disagreement rule fires. Build the scratch copy from the working tree, so uncommitted approved edits are in it: `scratch=$(mktemp -d) && rsync -a --exclude .git ./ "$scratch/"` from the repo root. Run the test there, then delete it (`rm -rf "$scratch"`). In that copy, plant one contradiction: change a value in one reference so it disagrees with another file or with a contract (a send day, a port, a style rule). Then ask the fresh agent for a task that depends on it. Pass: it quotes both lines and stops. Fail: it silently picks one — make the rule in `AGENTS.md` more prominent or move the conflicting fact to one home, then retest.

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
7. **Validate:** the context guards exit 0, then the walk test.
