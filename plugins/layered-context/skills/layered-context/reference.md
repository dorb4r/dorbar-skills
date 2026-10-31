# Layer templates

Copy these, then replace every line with project-real content. Keep each file short and single-purpose.

## Folder shapes

**Minimal** (make a repo legible to agents):

    <repo>/
      CLAUDE.md                 # Layer 0 — identity
      CONTEXT.md                # Layer 1 — router / map
      references/               # Layer 3 — the factory
        standards.md            #   coding + testing conventions
        app-state.md            #   living: what the system does now
        domain.md               #   domain terms / invariants

**Pipeline** (a multi-step agent workflow):

    <repo>/<workspace>/
      CLAUDE.md                 # Layer 0 — identity
      CONTEXT.md                # Layer 1 — router
      stages/
        01_<area>/CONTEXT.md    # Layer 2 — contract (+ output/)
        02_<area>/CONTEXT.md
        ...
      references/               # Layer 3 — factory (standards, domain, app-state, souls)
      _config/                  # Layer 3 — routing, caps, decisions
      runs/<task_id>/           # Layer 4 — per-run working artifacts

---

## Layer 0 — `CLAUDE.md` (identity)

    # <Project> — agent identity

    **Where you are.** <one line: what this repo/workspace is and how it's organized.>

    **How to load context (load only what your step needs):**
    - Layer 0: this file — identity.
    - Layer 1: `CONTEXT.md` — where each kind of work lives.
    - Layer 2: `stages/NN_*/CONTEXT.md` — your step's contract (if a pipeline).
    - Layer 3: `references/` — standards, domain, app-state (the factory).
    - Layer 4: `runs/<id>/` — this task's working files (the product).

    **Rules that override convenience:**
    - Tests: <exact command>. Build: <exact command>. (Never the raw tool if the project wraps it.)
    - Changes go <git/PR workflow>.
    - <other non-negotiables: i18n, security gates, style>.

## Layer 1 — `CONTEXT.md` (router)

    # Router — where work lives

    | Area / stage | Owner | Produces |
    |--------------|-------|----------|
    | <area> | <role/agent> | <output> |
    | ... | | |

    ## Who does what
    - <how work is picked up / who spawns whom, if multi-agent>.

    ## Config & reference
    `references/standards.md` · `references/app-state.md` · `_config/…`

## Layer 2 — `stages/NN_<area>/CONTEXT.md` (contract)

    # Stage NN — <name>

    **Owner:** <role / soul file>
    **One job:** <the single thing this stage does>.

    ## Inputs
    - Layer 4: <the prior stage's output file(s)>.
    - Layer 3: <the reference files this stage reads — name them explicitly>.

    ## Process
    1. <step>
    2. <step>

    ## Outputs
    - `runs/<task_id>/NN_<area>.md` — <what it writes>.

    ## Gate
    - <the condition to advance; escalate to a human on ambiguity.>

## Layer 3 — `references/app-state.md` (living knowledge base)

    # <Project> — current behavior  (living knowledge base)

    **Keep current.** <who/when updates this — e.g. the delivery stage, on every ship.>
    _Last updated: <date> — verify against code before relying on any single claim._

    ## What it is
    <one paragraph.>

    ## Key areas
    - <subsystem>: <how it behaves, endpoints/screens, invariants.>

    ## Conventions
    - Tests: <command>. <other durable facts.>

## Layer 3 — `references/standards.md`

    # Standards

    ## Code
    - <patterns to match, with a pointer to an exemplar file.>

    ## Tests
    - <how to run; what "done" means.>

    ## Review
    - <what blocks a change vs. a nit.>

---

## Fill order
1. Survey the repo. 2. `CLAUDE.md`. 3. `CONTEXT.md`. 4. `references/standards.md` + `app-state.md`. 5. Stage contracts (if a pipeline). 6. `.gitkeep` the `runs/` folder. 7. Name who keeps `app-state.md` current.
