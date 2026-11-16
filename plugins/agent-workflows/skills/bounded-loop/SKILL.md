---
name: bounded-loop
description: >-
  Bounded-loop: let a stage's Check retry under a written stop rule. Each reason someone would
  say "again" becomes a pass/fail check; the ending (all checks pass, no check improving, or a
  try budget, default 3) is written before attempt 1; every attempt is judged against the
  original checks; the best attempt is returned, not the last; one human check sits after the
  automated checks and before anything irreversible. Use when an agent's output keeps getting
  rerun by hand, when a stage contract's Check should allow retries, or when setting up an
  unattended refinement or research run. Not for a single-shot Check (layered-context), a
  repeated pick-one / yes-no / rating judgement (decision-gates), or running a prompt on an
  interval (loop).
---

# Bounded Loop

A loop is act, evaluate, decide, repeat, and the **evaluator** is the whole job: a second attempt with nothing judging between attempts is the same dice rolled again. A loop can only climb as high as the written bar, so this skill writes three things before anything runs: the checks, the ending, and the one human check.

It adds a retry form to the **Check** of a stage contract built with **layered-context** (Layer 2 contracts, `runs/<task-id>/`, the `NN_check.md` verdict). Outside ICM, the same Check section pasted into one prompt works the same way. Formats, the research shape and worked conversions are in [reference.md](reference.md); the contract block is [templates/check-section.md](templates/check-section.md).

## Which Check
| The stage's Check is… | Use |
|---|---|
| one verdict; a fail stops the run | **layered-context** (single shot, the default) |
| allowed to retry until written checks pass | **bounded-loop** (this skill) |
| the same pick-one / yes-no / rating, asked over many inputs | **decision-gates** |

A loop is earned when the output has been sent back more than once for reasons you can name. Below that, keep the single shot.

## Procedure
`NN` is the stage number, `<id>` the run. Steps 1-5 write the contract's Check section once; steps 6-7 run per task.

### 1. Count the agains
Collect every reason the output was sent back: review comments, the owner's memory, and past `fix:` lines (`grep -h '^fix:' runs/*/NN_review.md _archive/runs/*/NN_review.md`; this mining is an audit, so it may search `_archive/` read-only, per layered-context's "Archive, don't load" rule). When the reasons live in the owner's head, run the interview with the **grilling** skill, seeding the design tree with these branches: which output gets rerun most; what was wrong before each rerun; which step after this one cannot be undone; what must never leave without a person reading it; how many attempts are worth paying for. (No grilling installed: ask these in rounds, each question with a recommended answer.)
**Done when** every reason is written in the owner's words, one per line, in `stages/NN_<name>/agains.md`.

### 2. Convert each reason into a check
Each check is **pass/fail**, never a score; does **one job**; and every fail **names its line**. It must be runnable on the attempt alone plus named lookup inputs. "Too long" becomes a number a script counts; tone becomes two good examples plus a banned-words list; an adjective the system can only guess at ("professional") is not a check. Whatever will not convert is the **remainder**: it goes to the human check, not into the loop. The producer never grades its own attempt: the evaluator is a script, a failing test written first, or a reviewer sub-agent that sees only the attempt and the checks.
**Done when** every line of `agains.md` is either a row (id, evaluator, pass condition) in the checks table of the Check section in `stages/NN_<name>/CONTEXT.md` (from [templates/check-section.md](templates/check-section.md)) or listed on its `Remainder` line.

### 3. Layer the evaluators
Order them cheapest first: **script gate** (tests, build, lint, counts, banned words) → **rubric** (reviewer sub-agent, pass/fail per line) → **one human check**. A script fail goes straight into the carry without spending a rubric call. A rubric line run over many items can itself be a **decision-gates** question.
**Done when** each row of that checks table in `stages/NN_<name>/CONTEXT.md` names its layer and its exact command or reviewer brief.

### 4. Write the ending before attempt 1
Name the shape. A fixed target you could list in advance is **refinement**; when the answer is the thing being looked for, it is **research** (saturation ending, reference.md). A task needing both is two loops in two stages. A refinement ending is four lines:
- **Done:** every check passes.
- **Marginal:** an attempt turns no check from fail to pass → stop.
- **Budget:** 3 attempts, then stop (a different number carries its reason).
- **Fixed target:** every attempt is judged against the original list, never against the previous attempt. **Drift** never announces itself.
**Done when** the Check section holds the shape, the four lines and a budget number.

### 5. Place the human check
One human check, after everything countable and before the first irreversible step (send, publish, merge to main, deploy, delete, spend); never between attempts. The person receives the best attempt plus `NN_check.md` and answers one pre-written question with two exits: `go`, or `fix: <one change>`. Their answer goes to `runs/<id>/NN_review.md`, first line `go` or `fix: <one change>`.
**Done when** the Check section's `Human check:` line names the person, the irreversible step, the question and the review file.

### 6. Run the loop
Run `scripts/loop_decide.py` from this skill's folder (the repo keeps no copy). For attempt K = 1, 2, …:
1. Write `runs/<id>/NN_attempt-K.md`. Attempt 1 works from the stage Inputs; each later attempt starts from the attempt `loop_decide.py` names and changes only what its failing lines name (the **carry**).
2. Evaluate it against the full original list → `runs/<id>/NN_attempt-K_check.md` (format in reference.md).
3. Run `python -I <bounded-loop skill dir>/scripts/loop_decide.py runs/<id> NN --budget 3 --output runs/<id>/NN_<name>.md`. Exit 3: go again with the printed carry. Exit 0, 1 or 4: the loop has ended.

An attempt that cannot run (a missing credential, a tool absent) or whose rubric line a **decision-gates** question routed to a person is **blocked**, not failed: its check file's first line is `blocked: <why>`, and `loop_decide.py` stops with exit 4 (reference.md → Blocked is not failing).

**Done when** `loop_decide.py` exits 0, 1 or 4, `NN_check.md` exists, and on exit 0 or 1 the stage output is the **best attempt, not the last**.

### 7. Hand back and learn
Exit 1 means a fail: the run stops (layered-context rule) and the handback is the best attempt with every check's result. Exit 4 means blocked: the run stops and the blocker goes to a person; once it is answered, re-evaluate that attempt (overwriting its check file) and rerun `loop_decide.py`. Exit 0 with an irreversible step next goes to the human check. A `fix:` answer is applied to the stage output itself, outside the loop's budget; the full original list is re-run on it (results in `runs/<id>/NN_fix_check.md`) and it returns to the same human check. The same fix named in two runs is a missing check: write it into the contract's list.
**Done when** `NN_review.md` exists for any run that reached the human check, and every fix named twice is a check.

When every gate passed and the output was still wrong, the circuit did what was written: look for the one missing check, found at the human check, and add it. The fix is almost never more attempts.

Draws on Bas Rosario's Loop Engineering series (Clief Notes community), with supporting points from two David's Corner lessons (the Hermes tips grid and the systems-engineering essay), restated in our own words.
