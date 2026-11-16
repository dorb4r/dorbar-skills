---
name: parallel-branches
description: >-
  Parallel branches: fan work out to several sub-agents and merge it back without conflicting
  facts. Cut by deliverable, test every pair of branches for hidden dependencies, promote
  shared facts into one approved facts sheet, brief each branch with only its brief + the
  sheet, then merge in a designed convergence stage that lists every difference before ruling
  on each. Use when splitting a job into parallel workers (a docs package, a multi-file feature,
  research by several agents), when parallel outputs came back contradicting each other, or when
  designing the merge of independent drafts. Not for dependent steps (sequential stages in
  layered-context), a code review through several lenses (multi-lens-review), or briefing one
  sub-agent on a paused task (session-handoff).
---

# Parallel branches

A **branch** is one worker producing one deliverable on its own. Branches never talk to each other, so any fact two of them need and nobody gave them gets invented twice, differently. The method: find those facts before anything runs, settle them once upstream, and treat the merge as a decision stage, not a "combine and smooth" step.

Draws on Bas Rosario's Graph Engineering series (Clief Notes community), restated in our own words.

## When to fan out, and when not
Default to **one worker**. Fan out only for one of three reasons, named in writing: the pieces are genuinely independent; the work exceeds one worker's attention; or the pieces would write over each other in one session.
- Dependent work (B needs A's output) is a **sequence**: lay it out as numbered stages with the **layered-context** skill.
- ICM stages run one lane at a time. A parallel stage is a deliberate break of that default: say why in the run's `NN_cut.md`.

## Where it lives (ICM)
The fan-out lives inside one hosting stage, and every file takes that stage's number `NN` (stage `03_docs` → `03_cut.md`, `03_facts.md`, …; a run with no `stages/` uses `01`).
```
runs/<task-id>/
  NN_cut.md                      # reasons, branches, pair tests, arrows, edges
  NN_facts.md                    # the approved facts sheet (status line on top)
  NN_branches/<name>/brief.md    # run in parallel: exactly what crosses into the branch
  NN_branches/<name>/return.md   # the deliverable (or a pointer to it) + "Facts I lacked"
  NN_merge.md                    # cross-read list, then differences, then rulings
  NN_check.md                    # first line `pass` or `fail: <why>`
```
Templates for each file are in `templates/`. Worked examples and edge cases are in [reference.md](reference.md).

## Procedure

### 1. Cut by deliverable
Start `NN_cut.md` from `templates/cut.md`. List the deliverables (a document, a module, a report section), one branch each. Cut by *what gets delivered*, never by phase ("research" then "write" is a sequence, not two branches). Each branch writes to its own location; no two branches write the same file.
**Done when** `NN_cut.md` names the fan-out reason and every branch has one deliverable and one write path that no other branch shares.

### 2. Run the three dependency tests on every pair
For N branches there are N·(N-1)/2 pairs; give each pair a row in `NN_cut.md` (format: [reference.md](reference.md#pair-table)):
- **Question test:** what would branch A ask mid-task? Does the answer live in branch B?
- **Shared-fact test:** do A and B both state the same fact (a name, a number, a date, an interface, a decision)?
- **Order-flip test:** if B finished first, would A write anything differently?

Each yes is an **arrow**. Treat every arrow one of three ways: **sequence** it (the answer becomes an upstream step), **share** it (one approved artifact goes to both), or **merge** the two branches (they keep asking each other questions, so they are one branch).
**Done when** every pair has a row with all three answers and every arrow has a treatment. No arrows anywhere: recheck step 1 for a phase cut.

### 3. Write and approve the facts sheet (fan-out gate)
Every shared fact goes into `runs/<id>/NN_facts.md`, from `templates/facts.md`: one line per fact, a status line on top (`draft` / `approved by <who>, <date>` / `superseded`). The owner approves it. This is the one gate before fan-out; one read protects every branch.
**Done when** the sheet's status reads `approved by <person>` and every shared-fact arrow from step 2 appears on it.

### 4. Write the edges
For each branch write `NN_branches/<name>/brief.md` from `templates/brief.md`: audience, form, length, done-when, the write path, and the sheet's path. That brief plus the sheet is **all** that crosses: no chat history, no sibling drafts. The return is part of the contract: the deliverable plus a **"Facts I lacked"** list, one line per fact: `- <fact> → stopped | placeholder: <what stands in>`. A branch never guesses; it stops or leaves a visible placeholder.
**Edge test:** hand one brief and the sheet to a fresh sub-agent and ask only "what would you need to ask before starting?". Each question is a missing brief line or a missed arrow.
**Done when** every brief passes the edge test with no question whose answer exists elsewhere in the run.

### 5. Write the cross-read list (before anything runs)
Start `NN_merge.md` from `templates/merge.md` with **five or fewer** questions the finished whole must answer the same way everywhere (who it is for, what it leads with, what the reader does next, which interface wins). Written now, because questions written after the drafts arrive defend the draft you liked.
**Done when** the list exists in `NN_merge.md` and its timestamp is before dispatch. Briefs and sheet are now frozen.

### 6. Dispatch in parallel
Spawn one sub-agent per branch in a single message so they run together. Each gets its brief path and the sheet path, nothing else. It writes `return.md` from `templates/return.md`.
Then read every "Facts I lacked" list. A lacked fact goes **up**: amend the sheet, re-approve it, rerun every branch it affects. Nobody patches a draft sideways.
**Done when** every branch has a `return.md` and every lacked fact is either on the re-approved sheet (affected branches rerun) or ruled irrelevant in `NN_merge.md`.

### 7. Merge (its own stage)
Run the merge as a stage with the contract in [reference.md](reference.md#merge-stage). In order:
1. Read each return **alone** against its own brief. A branch is judged on its job, never for differing from siblings it never saw.
2. Read them **side by side** against the cross-read list. **List every difference before fixing any.**
3. **Rule** each difference with a name on it: **pick one** (and say why), **give the overlap one owner**, or **send it up** (the sheet changes, affected branches rerun). A contradiction of fact always goes up.
4. Treat a point that several branches reached independently as stronger evidence; it cannot be an echo.

Never blend, average or "smooth" drafts; a smoothed difference is a decision nobody made.
**Check:** a reviewer sub-agent that produced no branch confirms every difference has a ruling and the merged output applies each one; it writes `NN_check.md`. The owner's read comes last, before anything irreversible (publish, send, merge to main).
**Done when** `NN_check.md` reads `pass` and the owner has read the merged result. Lasting decisions from the rulings fold into `references/decisions.md` at delivery, per **layered-context**.

## Rules that hold every run
- No two branches write the same place.
- Briefs and sheet are frozen at dispatch; any change goes through the top and reruns the affected branches.
- The worker that produced a result never approves it.
- A blocked branch stops and lists what it lacks; it never guesses.
