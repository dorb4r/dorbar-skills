---
name: context-hygiene
description: >-
  Audit and compact an existing layered-context (ICM) workspace in a repo so agents load only
  current beliefs: measure always-loaded files against budget, merge duplicated facts to one
  home, rewrite stale or conflicting decisions in place, archive shipped plans, then prove the
  map with a fresh-session test and schedule the next review. Use when AGENTS.md, CLAUDE.md,
  CONTEXT.md, decisions.md or app-state.md have grown, when agents act on an outdated or
  contradictory entry, after a batch of merged features, or when a scheduled context review is
  due. Triggers: context hygiene, context cleanup, compact context, context bloat, stale
  decisions, conflicting decisions, prune AGENTS.md / CLAUDE.md, context review, swamp.
---

# Context Hygiene

Every feature adds lines to the always-loaded files, and every agent pays for those lines on every load. Left alone, the files become a **swamp**: three versions of one decision, a plan for work that shipped months ago, and an agent that confidently picks the wrong one. The opposite failure, forgetting decisions, is real too. The resolution: **base files hold current beliefs only; history lives in git and `_archive/`, which nothing routes to.** A smaller file that is true beats a complete file that contradicts itself.

This skill is the recurring maintenance pass for a workspace built with the sibling `layered-context` skill. Its conventions (layers, budgets, belief-line format, `_archive/`) are assumed here; the belief-line format and every recipe below are in [reference.md](reference.md).

## When to use
- A base file is over budget, or `context_budget.py` exits 1.
- An agent acted on a superseded decision, or two context files disagree.
- Several features merged since the last review, or the review date in `CONTEXT.md` has passed.
- After a model or harness upgrade: prune instructions the new model follows unprompted (the "Model default" [stale signal](reference.md#stale-signals)), so each upgrade costs fewer tokens.
- Before handing the repo to a new person or a new agent setup.

## When not to use
- No layered context exists yet: run `layered-context` to scaffold it.
- One wrong line you already know about: fix it in place now, with provenance; no audit needed.
- Restructuring a non-ICM folder into ICM: that is icm-architect's Restructure mode.

## Ground rules
- **Code wins.** When a context line and the code disagree, the code is the truth and the line is rewritten. When you cannot tell which is right, record the conflict for the human and leave both lines untouched.
- **Rewrite, never stack.** A changed belief replaces its old line in place, with fresh provenance.
- **Archive, then delete only generated runs.** Retired context moves to `_archive/`; only generated `runs/` artifacts nobody will reopen are deleted. Originals, sources, vendored files and other people's files stay exactly as they are.
- **Nothing moves before approval** (step 4). Steps 1-3 only read and write the audit run folder.
- Paths: `$LC` below means this skill's sibling, `../layered-context/` relative to this file. `$ROOT` is the workspace root (where `AGENTS.md` lives).

## Procedure

Create the audit's own run folder first: `runs/<YYYY-MM-DD>-context-hygiene/`. Every step writes its finding file there, so the audit is itself an edit surface the human can read and correct. Confirm the tree is in git with a clean working tree; if not, stop and ask, because git is where removed history survives.

### 1. Measure
Run both scripts from anywhere:
```
python -I $LC/scripts/context_budget.py $ROOT --provenance
python -I $LC/scripts/links.py $ROOT
```
Write `01_measure.md`: every over-budget file (lines, tokens, budget), every stage whose step load exceeds ~8k tokens, every provenance failure, every broken link or Inputs path. Then list files that no `CONTEXT.md` or `AGENTS.md` routes to (unrouted outside `_archive/`, `_templates/`, `runs/`).
**Done when** both scripts' complete output is captured and every flagged item appears in `01_measure.md` with its numbers.

### 2. Find duplicates
For each base file (`AGENTS.md`, `CONTEXT.md`, every `references/*.md`, every stage `CONTEXT.md`), pull its load-bearing nouns and numbers (commands, ports, versions, limits, names, URLs) and grep for each across the tree (recipe in [reference.md](reference.md#duplicate-hunt)). A fact found in 2+ files is a duplicate even when the copies agree today.
Write `02_duplicates.md`: one row per fact: the fact, every file and line holding it, the chosen **one home** (the file whose job the fact is), and the pointer that replaces each other copy. Content found in a routing file (`AGENTS.md`, any `CONTEXT.md`) gets a home on a shelf and a pointer back.
**Done when** every load-bearing noun and number from every base file has been grepped, and each duplicate has exactly one home.

### 3. Find stale and conflicting lines
Read every line of the belief files (`decisions.md`, `app-state.md`) and the routers, and flag each signal from the [stale-signal list](reference.md#stale-signals): stacked `Update:` lines, entries without provenance, a `recheck:` whose date or trigger has passed, two lines that disagree, plans or specs for shipped work still in `references/`, routes to folders that are gone, and instructions the current model already follows unprompted. **Verify every factual line against the code** (grep the symbol, read the config, run the command); a line the code contradicts is stale, whatever its date.
Write `03_stale.md`: line, file, signal, evidence (file:line or command output), proposed rewrite or removal.
**Done when** every bullet in both belief files carries a verdict (`current`, `rewrite`, `remove`, or `conflict: ask human`) backed by evidence.

### 4. Propose, approve, apply
Turn steps 1-3 into `04_proposal.md` using the [proposal format](reference.md#proposal-format): each change with old path, new path or new text, action (rewrite in place / pointer / move to `_archive/` / delete generated run), and referrers found. Before proposing any move, grep the tree for every path that points at the file; a file with a live referrer moves only with every referrer updated in the same change. Show the projected budget after the changes.
Present the proposal and **stop for the human's approval**. Apply only approved items; superseded belief lines are removed (optionally appended, with their old provenance, to `_archive/decisions-history.md`, which nothing routes to). Re-run both scripts.
**Done when** the human approved, every approved item is applied, `context_budget.py --provenance` and `links.py` both exit 0 (or each remaining failure is listed in `04_proposal.md` with the reason it stays).

### 5. Fresh-session test
Spawn a sub-agent with no conversation context (prompt in [reference.md](reference.md#fresh-session-prompt)). It starts at `AGENTS.md` and answers: what is this repo, what is in progress, what is next, and where it would go for two real tasks you name, one recent and one rare. It lists every file it opened, in order.
Compare against the truth (the code, open PRs, the human). A wrong or hedged answer, a file opened that the task did not need, or more than two hops from `AGENTS.md` to the right contract is a **map** failure: fix the route or the pointer wording, not by adding explanation, then re-run the test.
Then run the three [planted-fact tests](reference.md#planted-fact-tests), each in a fresh session: **recall** (asked about three belief lines before any task, it answers with their content), **correct** (one belief changed in a scratch copy of the working tree, the answer changes with it), **remove** (one belief deleted there, it says the context does not state it instead of inventing it). Write `05_fresh_session.md` with every run's answers and file lists.
**Done when** a fresh run answers all questions correctly, opens only routed files, and all three planted-fact tests pass.

### 6. Schedule the next review
Add or update one line in the root `CONTEXT.md` (format in [reference.md](reference.md#review-line)): the next review date and the trigger, whichever comes first. Default cadence: monthly, or after 5 merged features. Check that the delivery stage contract carries the [fold-in rule](reference.md#fold-in-rule) so each ship updates beliefs in place; add it if missing (that edit goes through the step-4 approval like any other).
Write `06_check.md`, first line `pass` or `fail: <why>`, then a three-line summary: tokens before, tokens after, next review.
**Done when** the review line exists, the delivery contract has the fold-in rule, and `06_check.md` is written.

## Guardrails
- **Smaller over complete.** When a line costs a seat on every load and you hesitate over whether it earns it, it moves to a drawer file behind one pointer, or to `_archive/`.
- **Fold what is unused, split what keeps growing.** A stage nobody edits can merge into its neighbour; a contract that grows every review gets split. Propose both in step 4.
- **Restart is cheap.** If a file needs more rewrites than keeps, propose replacing it with a fresh one that copies over only the lines marked `current`.

Credits: adapted in part from icm-architect (MIT, (c) 2026 Jake Van Clief). Persistence, retrieval and correction ideas after Bas Rosario's Memory Engineering series and Jake Van Clief's Clief Notes course (Foundation and David's Corner lessons), restated in our own words.
