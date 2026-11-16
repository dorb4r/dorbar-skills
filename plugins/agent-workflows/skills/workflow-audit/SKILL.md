---
name: workflow-audit
description: >-
  Audit a recurring job before automating it: take it apart step by step, label each step code /
  rule / model / person, score impact and risk, give each step a verdict (AUTOMATE / HYBRID /
  MANUAL), and end with what to build: a layered-context pipeline, one skill, a script, or
  nothing. Runs first: its audit file hands the chosen job to layered-context, which lays it out.
  Use when someone wants to automate a job or build an agent or "AI for X", asks whether a task
  is worth AI, or brings a frustration instead of a spec. Not for laying out a workflow already
  chosen (layered-context) or turning chat corrections into a skill (corrections-to-skill).
---

# Workflow audit

Decide **what** to automate before anyone builds. Most of a working system is ordinary software and stated rules; the model is the small part where language or judgment is genuinely needed, and a person keeps every call that binds someone. The audit makes that split explicit, step by step, so the build that follows is the smallest one that works, or no build at all.

## What this skill owns, and what it hands off
- **Owns:** the outcome brief, the step labels, the impact/risk scores, the verdicts, and the choice of what to build. Its product is one file: `runs/<id>/01_audit.md`.
- **Interview mechanics** belong to **grilling** (step 1 supplies only the branches).
- **Laying out the build** belongs to **layered-context** (pipeline shape), **corrections-to-skill** (one skill from chat corrections) or **skill-creator**. This skill runs first and stops at the hand-off; it writes no stages, skills or scripts. For a pipeline, layered-context's Interview mode reads `01_audit.md` and asks only what it leaves open.
- Retry discipline inside a step belongs to **bounded-loop**; repeated judgment calls with confidence routing to **decision-gates**; independent deliverables to **parallel-branches**.

## The four labels
Every step gets exactly one. Definitions, tests and edge cases: [reference.md](reference.md#labels).
- **code**: the same operation every time, no decision (an export, a query, a format check, an existing app feature).
- **rule**: a decision you can write as if/then on the inputs.
- **model**: needs language read or written, or a prediction from data. A prediction is a trained model's job, not a chat model's.
- **person**: commits someone, needs taste, or must be answered for.

Expect most steps to land on code and rule. Jake Van Clief's 60/30/10 (roughly: data and thinking / existing tools and rules / model calls) is a sanity check on the finished table, not a quota.

## Procedure
Create `runs/<YYYY-MM-DD>-audit-<job-slug>/` at the repo root (layered-context adopts it later if the repo has no layered context yet). Copy [templates/audit.md](templates/audit.md) to `01_audit.md` and fill it section by section.

### 1. Frame the job
Run the interview with the **grilling** skill, seeding the design tree with these branches:
- **Outcome:** who the result is for; what they do next with it (decide, send, fix); where the information comes from today; what breaks when it goes wrong, and who feels it.
- **Baseline brief:** who does the job now and how often; time per *accepted* result, corrections included; the target (what improves, by how much, over what trial); what must stay true for a result to count; who reviews it and maintains the workflow.
- **Worth:** which of revenue up, cost down or risk down it serves, in a number or a range.
- **The steps as done today:** each step's input, output, and who or what does it.

If grilling is not installed, ask these branches in rounds, each question with a recommended answer.
**Done when** sections 1-2 of the audit hold an answer for every field: a number, or `unknown: measure by <how>`. Ask someone who does the work to challenge the baseline and the quality bar before step 3.

### 2. Check it is worth building
Answer in section 3, each with evidence (a doc link, a release note, a tried feature):
- Does an app already in use do this, or most of it?
- Is the next model or platform release likely to ship it as a built-in? If yes, would the benefit until then repay the build?
- Would something cheaper do: a template, a spreadsheet, a weekly manual paste, a person?
- No worth line from step 1, for business work, is a stop.

**Done when** each question has an answer with its evidence. If any answer ends the audit, jump to step 6 with verdict **nothing** and the reason.

### 3. Label every step
Break the job into steps small enough that each has one input, one output and one check (usually 4-10). Give each a label with a one-line reason. Then challenge the table, writing each answer in section 5:
- Could any **model** step be a rule or code? A fixed sequence with no decision is code; a model there adds cost and variance.
- Is any **person** judgment handed to a model with no review point?
- Which steps would still be right if the model were swapped tomorrow?
- Is a model choosing tools in a loop (an agent) only where the next action depends on the input and no rule can pick it?

**Done when** every row has a label and a reason, and all four challenges are answered.

### 4. Pick the smallest mechanism and its check
For each step choose the smallest part that does it: prompt, skill, connector or MCP, hook, script, plugin, existing app feature, or a person ([reference.md](reference.md#mechanisms)). Leave out any part with no job. Write each step's check so it separates **present** from **verified** (a date field exists vs the date is right): name a missing-value and a wrong-value case it must catch.
**Done when** every row has one mechanism and a check that names both cases.

### 5. Score and decide
Score **impact** (value of a right result) and **risk** (cost of a wrong one) 1-5, each with a reason. Apply the four risk conditions and their floors, then give each step **AUTOMATE**, **HYBRID** or **MANUAL** ([reference.md](reference.md#scoring)). Every HYBRID step names its reviewer and where the halt is enforced (a permission mode, a hook, a required check), never a folder or a file alone.
**Done when** every row has both scores with reasons, a verdict, and, for HYBRID, a reviewer and an enforcement point.

### 6. Hand off
Pick one outcome and write it in section 6 with its reason ([reference.md](reference.md#hand-off)): **nothing** (with a recheck date), **a script**, **a skill**, or **a pipeline** (layered-context, Pipeline shape). Name the first version to build: the smallest slice that proves the outcome, and the trial measure from step 1 that will judge it.
Have a reviewer sub-agent with no conversation context read `01_audit.md` against the [audit check](reference.md#audit-check) and write `01_check.md`, first line `pass` or `fail: <why>`. Show the owner the table and the hand-off; their confirmation ends the audit.
**Done when** `01_check.md` says `pass`, the owner confirmed, and, if the repo keeps `references/decisions.md`, the verdict's lasting part is one belief line there (format: layered-context), e.g. `- Invoice reminders: HYBRID, finance lead approves each send (since 2026-11-16, by finance-ops, ref runs/2026-11-16-audit-invoice-chasing)`.

## After the first runs
Compare time per accepted result and correction rate against the baseline at the trial's end; [reference.md](reference.md#trial) has the review. A model step that keeps doing the same thing the same way is now a code step: re-label it and let it harden (layered-context, invariant 8).

Draws on Jake Van Clief's Clief Notes course and talks (60/30/10, the four outcome questions, the platform-absorption question, computational orchestration) and on David Vogel's and Laura L.'s community lessons (outcome brief, mechanism map, impact/risk audit), restated in our own words.
