---
name: layered-context
description: >-
  Scaffold a layered, agent-readable context architecture (ICM — Interpretable Context
  Methodology) onto a software project: a CLAUDE.md identity layer, a CONTEXT.md router,
  reference "factory" files, and per-run working areas, so an agent (or a tree of sub-agents)
  loads only the context each task needs instead of one monolithic prompt. Use when setting up
  or standardizing project context for agents, onboarding a codebase for agent work, designing a
  multi-stage agent workflow/pipeline, creating or refactoring CLAUDE.md / CONTEXT.md structure,
  or when asked how to organize instructions/knowledge so sub-agents stay focused.
  Triggers: layered context, context architecture, ICM, CLAUDE.md setup, context engineering,
  agent context scaffolding, project context layers, folder-as-architecture.
---

# Layered Context Architecture (ICM)

Structure a project's context as **files in a folder hierarchy**, so the folder structure itself is the architecture. One agent — or a tree of sub-agents — reads the right files at the right moment and does work that would otherwise need an orchestration framework. No framework, no code to change a step: you rename a folder, edit a markdown file, add a folder.

This is **Interpretable Context Methodology** (Van Clief & McDermott, arXiv:2603.16021), applied as a reusable scaffold. Use it to make any codebase legible to agents without a monolithic CLAUDE.md that rots as it grows.

## When to use
- Onboarding a codebase for agent work, or standardizing how agents read a project.
- Designing a multi-stage agent workflow (research → plan → build → review → ship).
- A CLAUDE.md has grown into an everything-dump and needs to become layered.
- You want sub-agents that each get a small, scoped context instead of the whole repo.

## When NOT to use
- A throwaway one-off task — the scaffold is overhead you won't recoup.
- Pure human documentation (a README for people) — that's not this.

## The five layers

Load only the layers a given step needs. Lower layers are the biggest and loaded last.

| Layer | File(s) | Question | Changes between runs? |
|-------|---------|----------|------------------------|
| **0** | `CLAUDE.md` | Where am I? (identity) | no |
| **1** | `CONTEXT.md` | Where do I go? (router / map) | no |
| **2** | `<area>/CONTEXT.md` | What do I do here? (the area's contract) | no |
| **3** | `references/` (+ `_config/`, `shared/`) | What rules apply? — the **factory** | no (stable) |
| **4** | `runs/<id>/` (or `output/`) | What am I working with? — the **product** | **yes** (every run) |

The Layer 3 / Layer 4 split is the one people get wrong. **Layer 3 is reference** the model *internalizes as constraints* ("write like this, follow these conventions"). **Layer 4 is working material** the model *processes as input* ("turn this research into a plan"). Keep them in separate folders so the model receives already-sorted context.

## The five principles
1. **One area, one job.** Each stage/area does a single step and writes its output to its own folder. A step that fetches data does not also format it.
2. **Plain text is the interface.** Markdown and JSON between steps — no binary state, no database coupling. Any tool and any human can read or edit any file.
3. **Load only what the step needs.** This is *prevention*, not compression: never load the irrelevant context in the first place. Give each area an explicit **Inputs** list naming which Layer-3/4 files it reads.
4. **Every output is an edit surface.** Each step writes a file a human can open, inspect, and edit before the next step runs.
5. **Configure the factory once; run it many times.** Layer 3 (standards, souls, domain knowledge) is set up once. Each run produces a new Layer-4 deliverable using the same factory.

## Scaffold procedure

1. **Survey first — don't invent.** Read the repo: stack, test/build commands, git workflow, existing docs, naming conventions, any existing CLAUDE.md. The scaffold must describe the *real* project.
2. **Pick the shape.** Minimal (a repo to make legible): Layers 0, 1, 3. Pipeline (a multi-step workflow): add Layer 2 as numbered area folders and Layer 4 run folders. See `reference.md` for both.
3. **Write Layer 0 — `CLAUDE.md`:** identity, where things live, how to load context (the layer order), and the **non-negotiable rules** (exact test/build commands, git/PR workflow, i18n, security gates). Short.
4. **Write Layer 1 — `CONTEXT.md`:** the map. The areas/stages, who or what owns each, and pointers into Layer 3. This is routing, not content.
5. **Write Layer 2 (only if there's a workflow):** one folder per area/stage; number them if ordered (`01_…`, `02_…`). Each gets a `CONTEXT.md` **contract**: `Inputs` / `Process` / `Outputs` / `Gate`. The Inputs list is the scoping mechanism — it names exactly which files to load.
6. **Build Layer 3 — `references/`:** coding/testing standards, domain knowledge, a **living `app-state.md`** (what the system does now), reference material, and any agent "souls". This is the factory; keep it stable and authoritative.
7. **Create Layer 4 — `runs/` (or `output/`):** the per-task folder where artifacts accumulate. Commit a `.gitkeep`; real artifacts are produced per run.
8. **Fill with real content, not placeholders.** Every file earns its place. Keep each one short and single-purpose; a file no step loads is dead weight.
9. **Wire keep-current.** Name who updates `app-state.md` and the standards (e.g. "the delivery step updates `app-state.md` on every ship"). Stale reference is worse than none.

## Rules & anti-patterns
- **No monolith.** Don't pile everything into one CLAUDE.md — that's the long-context rot this prevents. Split by layer and area.
- **Don't cross the 3/4 streams.** Per-run artifacts never go in `references/`; stable reference never goes in `runs/`.
- **Scope inputs explicitly.** An area without an Inputs list forces the agent to load everything or guess. Always list inputs.
- **Keep it diffable.** Plain text, version-controlled, one concept per file. If a human can't open and edit it, it's the wrong format.
- **Sequential stages, parallel within.** The pipeline (Layer 2 order) is sequential with review gates; fan out sub-agents *inside* a stage or *across* independent tasks, not across one task's stages.

## Adapting by project type
- **Service / backend:** Layer 2 areas by concern (api, data, auth, infra); `app-state.md` lists endpoints + invariants.
- **App / frontend:** areas by surface (screens, state, i18n); standards capture design tokens + accessibility rules.
- **Library:** often no Layer 2 — Layers 0/1/3 plus a `references/api.md` is enough.
- **Monorepo:** a top-level Layer 0/1, then a nested `CONTEXT.md` per package (the router pattern, applied recursively).

## Templates
Copy-paste skeletons for every layer file (CLAUDE.md, CONTEXT.md router, stage contract, app-state, references) are in **`reference.md`** next to this file. Start from those, then replace every line with project-real content.
