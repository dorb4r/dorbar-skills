---
name: layered-context
description: >-
  Scaffold or restructure a layered, agent-readable context architecture (ICM — Interpretable
  Context Methodology) in a software project: an AGENTS.md entry file, a CONTEXT.md router, stage
  contracts, a references/ factory and per-run runs/ folders, so each agent or sub-agent loads only
  the context its step needs — and keep it small as the project grows (beliefs rewritten in place,
  retired material archived, budgets enforced). Use when setting up project context for agents,
  turning a bloated CLAUDE.md into layers, designing a multi-stage agent workflow, writing
  AGENTS.md / CLAUDE.md / CONTEXT.md, or deciding where plans, decisions and app state should live.
  Triggers: layered context, context architecture, ICM, AGENTS.md, CLAUDE.md setup, context
  engineering, restructure CLAUDE.md, folder-as-architecture, decisions log, context growth.
---

# Layered Context Architecture (ICM)

Structure a project's context as **files in a folder hierarchy**, so the folder structure is the architecture. One agent, or a tree of sub-agents, reads the right files at the right moment. Changing a step means editing a markdown file, not code.

Method: Interpretable Context Methodology (Van Clief & McDermott, arXiv:2603.16021), updated with the author's later practice in [icm-architect](https://github.com/RinDig/icm-architect) (MIT, © 2026 Jake Van Clief; see `LICENSE-icm-architect`) and his Clief Notes course. The context-lifecycle rules draw on Bas Rosario's *Memory Engineering* series in the same community.

## When to use / when not
- Use for: onboarding a codebase for agent work; a CLAUDE.md that has become a dump (→ **Restructure**, below); a repeated multi-stage workflow (plan → build → review → ship); keeping sub-agent context scoped.
- Climb the ladder only as far as the work needs: **chat → a skill → folders + one agent**. If the job fits one saved prompt, ship a skill instead. A workspace for something done twice is scaffolding, not architecture.
- ICM is for sequential, checked, repeatable work. Real-time multi-agent collaboration, high-concurrency serving and automated mid-pipeline branching need orchestration code.
- For a code map that answers "what would a change hit", use the sibling **system-map** skill; for periodic cleanup use **context-hygiene**; for pausing/resuming a task use **session-handoff**.

## The five layers

| Layer | File(s) | Question | Budget | Changes |
|---|---|---|---|---|
| **0** | `AGENTS.md` (+ `CLAUDE.md` = `@AGENTS.md`) | Where am I? | ≤60 lines, ~800 tok | rarely |
| **1** | `CONTEXT.md` | Where do I go? (router) | ≤80 lines | rarely |
| **2** | `stages/NN_<name>/CONTEXT.md` | What do I do here? (contract) | ≤80 lines | rarely |
| **3** | `references/` | What rules and facts apply? (**factory**) | ≤200 lines / ~2k tok per file | per decision |
| **4** | `runs/<task-id>/` | What am I working on? (**product**) | — | every run |

A step's whole load (Layer 0 + its contract + its Inputs) stays under **~8,000 tokens**. Layer 3 is reference the model obeys as constraints; Layer 4 is material it transforms. Keep them in separate folders.

`AGENTS.md` is the cross-tool entry file (Claude Code, Codex, Cursor, Gemini…). Tools that look for another name get a one-line pointer, never a second copy: `CLAUDE.md` holds `@AGENTS.md`.

## Invariants
Defaults, not dogma: break one on purpose and write why in the nearest `CONTEXT.md`.
1. **One folder, one job.** Each stage does one step and writes to its own output.
2. **Catalogs route; shelves hold.** `AGENTS.md` and `CONTEXT.md` point at content and store almost none. A routing file that grows is absorbing payload: move it to a shelf, leave a pointer.
3. **Contracts scope the load.** Every stage contract lists exact backticked Inputs (Working / Reference / Example), a `Do NOT load:` line, and stops if an input is missing.
4. **Every step ends at one concrete Check** — a command's exit code, a reviewer sub-agent, or a person. A non-person check writes `runs/<id>/NN_check.md`, first line `pass` or `fail: <why>`; a fail stops the run.
5. **One home per fact.** A link beats a copy. Links and Inputs paths are relative and must resolve (`scripts/links.py`).
6. **Status lives on disk** — what exists in `runs/<id>/` plus check verdicts. Generated indexes are rebuilt by script, never hand-edited.
7. **Plain text, first heading names the file and its job**, so `grep -rm1 '^# ' .` lists the tree.
8. **Let it harden.** A step done the same way three or four times becomes a script, and the contract names its command (`pnpm test --filter api`). Fold a stage nobody edits; split a contract that keeps growing.
9. **Agents learn from docs, not old outputs.** Curated `examples/` may be listed as Inputs; past `runs/` never are.

## Scaffold procedure
1. **Survey — don't invent.** Read the repo: stack, exact test/build/lint commands, git workflow, existing docs and agent files. Ask the owner only what the code can't tell you.
2. **Pick the shape** (see `reference.md` → Folder shapes): *Minimal* (Layers 0, 1, 3) to make a repo legible; *Pipeline* (adds Layer 2 stages + Layer 4 runs) for a repeated workflow. Build the smallest structure that carries today's work; add folders when the work asks for them.
3. **Write Layer 0 `AGENTS.md`** from the template: identity, where things live, how to load context, non-negotiable rules, and the **disagreement rule**. Create `CLAUDE.md` as the pointer.
4. **Write Layer 1 `CONTEXT.md`**: the routing table — "if X just happened, go to Y, stop at Z".
5. **Write Layer 2 contracts** (pipeline only): one `stages/NN_<name>/CONTEXT.md` each, from the template.
6. **Build Layer 3 `references/`**: `standards.md`, `domain.md`, `app-state.md`, `decisions.md` — the last two in **belief format** (next section). Real content only; a file no step loads is dead weight.
7. **Create Layer 4** `runs/.gitkeep` and `_archive/` (with a one-line `README.md`: retired, never read). Plans live in `runs/<id>/`, never in `references/`.
8. **Wire the guards**: copy `scripts/links.py` and `scripts/context_budget.py` from this skill into the repo's `scripts/` and run both in CI or pre-commit (`reference.md` → Wiring the scripts).
9. **Wire the lifecycle**: add the **fold-in** step to the delivery stage (next section) and name who owns it.
10. **Walk test** (below). Done when it passes and both scripts exit 0.

## Context lifecycle: keep the base small as features pile up
The base files every agent loads must not grow with the feature count. The trade-off "know every decision vs. drown in conflicting ones" dissolves once **knowing** and **loading** are separate: agents load what is true *now*; history stays in git and `_archive/`, reachable on demand.

- **Beliefs, not records.** `references/decisions.md` and `app-state.md` state current truth only. Each entry is one bullet ending in provenance — `(since 2026-11-03, by platform-team, ref #142)` — plus `recheck: <trigger>` when it is expected to change.
- **Correct in place, the same day.** A changed decision replaces its line. Stacked "Update:" lines are how conflicts are born; `context_budget.py --provenance` flags them.
- **Disagreement rule** (in `AGENTS.md`): *If two context files disagree, say so and stop. Do not choose.* The agent surfaces the conflict; a human fixes the file.
- **Fold-in at delivery.** When a task ships, its delivery stage: merges the run's lasting decisions into `decisions.md` (rewriting, not appending), updates `app-state.md` for changed behaviour, moves the run folder to `_archive/runs/`, and re-runs both scripts.
- **Archive, don't load.** `_archive/` is excluded from every route and every Inputs list. Superseded decisions live in git history (optionally `_archive/decisions-history.md`).
- **Budgets are the alarm.** A file over budget is split or compacted, never waved through. Run **context-hygiene** on a rhythm (monthly, or every N shipped features) and whenever the walk test fails.

## Restructure mode (an existing dump)
Inventory first, move nothing; classify every file as catalog / contract / factory / product / dead; find every referrer (including CI, `.claude/` config, other repos); present a migration map and get approval; then `git mv` on a branch, verify, archive the dead, leave pointers. Full procedure: `reference.md` → Restructure.

## The walk test
Spawn a fresh sub-agent with no conversation context and ask it to work cold:
- *What is this repo, what is in progress, what is next?* — answered from `AGENTS.md` plus at most two more reads.
- *Where do you go for task X?* — for two or three real tasks; have it list every file it opened.
- *Status of run Y?* — stated purely from what exists on disk and the check verdicts.
- Pick any stage: can it name exact Inputs, the job, the output and the Check?

Wrong answers or wandering reads mean the map is vague: tighten the routing row or split the file, then rerun. Rerun the walk test on every PR that changes the structure.

## Templates
Copy-paste skeletons for every layer file, the belief-format decisions file, folder shapes, the restructure procedure and CI wiring are in **`reference.md`**. Start from those, then replace every line with project-real content.
