---
name: reel-creator
description: >-
  Take a vertical short-form video (Instagram Reel, TikTok, YouTube Short) from idea to a finished
  CapCut edit through checked stages: brief, ideas mined from real client material, a beat-sheet
  script with a hook and a turn, a footage match or a shoot card for what's missing, a measured
  music map, a CapCut build from code with sound design, a cold review and a learning loop. Also
  breaks down reference reels into reusable lessons. Use when asked to make, plan, script, shoot,
  edit or review a reel/short/TikTok, to come up with reel ideas, to learn from a reel someone
  sent, or when reels "have no soul", feel generic, or don't perform.
---

# reel-creator

Reels are made in stages, and nothing moves on until a stage's check passes. The skill is the
**factory** (stage contracts, craft references, studied examples, tools). Each project keeps its own
**brand file, decisions and runs**. The concept carries a reel; editing serves it (`examples/README.md`).

## Where things live
| Path | Holds |
|---|---|
| `CONTEXT.md` | the router: start here for any task |
| `stages/NN_<name>/CONTEXT.md` | one contract per stage: Inputs, job, Outputs, Check |
| `references/` | craft rules: story, formats, hooks, script, shooting, music, sound, editing, CapCut, review, tools |
| `examples/` | studied reference reels, one lesson each |
| `templates/project/` | what a project needs: `AGENTS.md`, `references/brand.md`, `references/decisions.md` |
| `templates/run/` | blank starters for a run's files |
| `tools/` | `build_reel.py`, `capcut_mac.py`, `beatgrid.py`, `reel_breakdown.py` (uv project) |
| `{project}/runs/<YYYY-MM-DD>-<slug>/` | one reel's working files (in the project, never here) |

## How to load context
Read this file, then `CONTEXT.md`, then only your stage's contract and the Inputs it lists.
`{project}` is the folder holding the project's `AGENTS.md` (ask the owner if unknown); `{run}` is
the run folder under it. Inputs paths are relative to the contract file; every other path in this
skill (references, examples, commands) is relative to the skill root, and **commands run from the skill root**.

## Rules
- Stop after each stage that names a human check, and wait. One question at a time.
- True stories only: real people, real order, real words. Unknown facts are questions, never guesses.
- Consent for every identifiable person; the project's banned material never appears.
- Downloads, publishing, scheduling and exports happen only on the owner's explicit request.
- Never quit CapCut; close projects with menu → Back to home page. Never overwrite the owner's hand edits.
- Tools: from the skill root, `uv run --project tools python tools/<script>.py …`. Install nothing new without asking.
- If two context files disagree, say so and stop. Do not choose.
