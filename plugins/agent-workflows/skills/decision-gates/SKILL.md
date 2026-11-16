---
name: decision-gates
description: >-
  Decision-gates: replace a repeated judgement step (an LLM call whose answer is a pick-one, a
  yes/no or a rating) with a decision file: the input it reads, plain-English questions with
  fixed answer options that always include "other", and confidence thresholds applied by code
  (act at about 0.8 or above, a person at about 0.5 or below, act-and-flag between). Answers are
  stored beside the input and every human overrule becomes a test case. Use when a workflow
  triages, tags, routes, grades against a rubric, picks the best draft, gates a stage, or decides
  "done, or stop and ask?" over and over. Not for paragraph outputs (keep the LLM), exact
  counts, dates or totals (code), a one-off Check (layered-context), or retrying until checks
  pass (bounded-loop).
---

# Decision Gates

Much of any workflow is sorting: which pile does this go in, is it good enough to move on, which draft wins. When an LLM step answers with a pick from a list, a yes/no or a rating, and the step runs again and again, it is a **classifier** wearing an expensive coat: slow, costly, and liable to give two answers when asked twice. A **decision file** pins the list of piles on the wall where anyone can read it. A model returns an answer and a confidence; **code makes the call**.

In an ICM workspace the folders already hold the order and the files hold the memory; the decision file moves the last *if* out of the model's head and into the folder. It is a Check type for a stage contract built with **layered-context** (`runs/<task-id>/`, `NN_check.md` conventions assumed). Formats, the runner contract and tuning are in [reference.md](reference.md); the file to copy is [templates/decision.md](templates/decision.md).

## Which Check
| The stage's Check is… | Use |
|---|---|
| one verdict; a fail stops the run | **layered-context** (single shot, the default) |
| allowed to retry until written checks pass | **bounded-loop** |
| the same pick-one / yes-no / rating, asked over many inputs | **decision-gates** (this skill) |

## The test
A step becomes a gate when **both** hold: its answer is a pick-one, a yes/no or a rating; and it runs more than a few times. Otherwise:
- The answer is a paragraph (write, summarize, code): keep the LLM.
- Code can do it exactly (counting, dates, totals): do it in code. "Is this expense within policy?" is a gate; "what is the total?" is code.
- A handful of small items, once: one batched model call is cheaper.

## Procedure

### 1. Find the judgement steps
Walk the stage contracts, prompts and scripts for every place a model or a person picks, approves or rates. When those places live in the owner's head, run the interview with the **grilling** skill, seeding the design tree with these branches: where do you stop to check something; what answers are possible there; what happens after each answer; how often it runs; what a wrong "go" costs against a wrong "stop"; who overrules, and where they would look. (No grilling installed: ask these in rounds, each question with a recommended answer.)
**Done when** each candidate step is listed in `runs/<id>/01_gates.md` (`<id>` the run doing this setup), one line each: the step's file and line, then `gate`, `keep the LLM` or `code` with a one-line reason.

### 2. Write the decision file
Copy `templates/decision.md` to `stages/NN_<name>/decision.md` (one stage) or `references/gates/<name>.md` (shared by several). Fill in:
- **Input:** the exact file or glob it reads.
- **Questions** in plain English, one thing each. Pick-one lists fixed options and always ends with `other`; yes/no is exactly two; a rating describes every point of its scale.
- **Thresholds:** `act_at: 0.8`, `ask_below: 0.5` unless the cost of a wrong act says otherwise.
- **Actions:** what code does for each answer, and any rule that combines answers ("of the drafts rated clear, pick the one highest on curiosity"). The model gives opinions; the combining is code.

**Done when** every option maps to an action, every pick-one has `other`, and both thresholds are set.

### 3. Build the runner
Write a small script that reads any decision file, asks each question about the input through a classifier (a zero-shot classifier API, or a model call constrained to one listed option plus a 0-1 confidence), applies the thresholds and actions, and writes the answers file. One runner serves every decision file in the repo; the contract names its command.
**Done when** one command runs a decision file on one input and writes its answers file.

### 4. Store answers beside the input
In a stage, answers go to `runs/<id>/NN_decision.md`; for filed items, to `<input>.decision.md` next to the file. Each question gets its answer, confidence, route and an empty `overrule:` line, so a person can open it and correct one line.
**Done when** every input the gate ran on has an answers file a person can overrule.

### 5. Route on confidence
- At or above `act_at`: **act**.
- At or below `ask_below`: **a person decides**.
- Between: **act and flag** for a later glance.
- Any `other` answer goes to a person whatever its confidence: no listed pile fits.

As a stage Check, the runner writes `runs/<id>/NN_check.md`: first line `pass` when every question routed to act or act-and-flag (flags listed below it), or `fail: ask person — <question>: <answer> at <confidence>` when any routed to a person. A fail stops the run, per layered-context.
**Done when** the check verdict follows from the routes alone.

### 6. Turn every overrule into a test
When a person fills an `overrule:` line, append a case to `decision.tests.md` beside the decision file: the input (a frozen copy if the original will change), the question, the expected answer, the date and the role that overruled. Before any change to the decision file (wording, options, thresholds, model), replay every case; the new version ships only when it agrees with all of them.
**Done when** every overrule is a test case, and the latest edit of the decision file has a replay with zero disagreements.

Review the gate's flag and overrule rates on a rhythm, and sooner when people overrule often, using [reference.md → Tuning](reference.md#tuning).

Draws on Jake Van Clief's Clief Notes videos (the decision-file pattern over a fast classifier), restated in our own words.
