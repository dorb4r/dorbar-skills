# Decision gates: formats and reference

Contents: Where gates pay · Writing questions · The runner contract · Confidence · Answers file · Tests file · As a stage Check · Inside a bounded loop · Tuning.

## Where gates pay

Each of these is a pick-one, a yes/no or a rating, asked many times:
- **Triage:** what is this, and where does it go?
- **Stage gates:** is this good enough to move to the next stage?
- **Pick the best:** rate every draft on named scales; code picks the winner.
- **Tagging and filing**, including "which of these copies of a figure is the current one?"
- **Rubric grading:** one yes/no or rating per rubric line.
- **Leak checks:** does this mention a client by name? Asked before anything ships.
- **Staleness:** is this doc out of date against `<source>`?
- **Routing for agents:** which file or skill should load next?
- **Done or ask:** is the task actually finished, or should the agent stop and ask?

## Writing questions

- One question, one thing. "Is it clear and short?" is two questions.
- Options are fixed and mutually exclusive. The classifier cannot invent a pile that is not listed, so every pick-one ends with `other`.
- A rating describes every point of the scale in words, not just its ends.
- Ask about the input, not the action: "Does it name a receiver?" rather than "Should we send it back?". The action table maps answers to actions.
- Several questions can be asked about the same input in one runner call.

## The runner contract

One script per repo (written once, on request) that:
1. Reads a decision file and the input it names; stops with a message if the input is missing or empty.
2. Asks each question through the classifier and gets back exactly one listed option plus a confidence in [0, 1]. With a general LLM, constrain the output (structured output or a tool schema with an enum per question); free text is rejected and retried once, then routed to a person.
3. Applies thresholds, the `other` rule and the action table in code.
4. Writes the answers file and, in a stage, `NN_check.md`.
5. Exits 0 when nothing routed to a person, 1 otherwise.

`--replay decision.tests.md` runs every test case and prints each disagreement as `case <n>: expected <a>, got <b> at <conf>`; exit 0 only with zero disagreements.

## Confidence

The routing rule is only as good as the number it reads.
- A classifier trained for calibration means its 0.8 is right about 80% of the time across many answers. Any single answer can still be wrong, which is why the number is kept and stored.
- A general LLM's self-stated confidence is not calibrated. Treat the thresholds as provisional and let the tests file measure them: the share of act-routed answers that people overrule is the real error rate.
- Raise `act_at` where acting is irreversible or a wrong act is costly; lower `ask_below` only when the person's queue cannot keep up and the tests show low-confidence answers are mostly right.

## Answers file

    # Decision answers: triage, inbox/2026-11-14-plan.md
    decision: stages/03_triage/decision.md (as of <commit>)
    run: 2026-11-16 14:02, runner scripts/decide.py

    - kind: plan (1.00) → act
      overrule:
    - receiver: no (0.91) → act
      overrule:
    - readiness: 2 (0.59) → act, flagged
      overrule:

A person overrules by filling the line (`overrule: 1, by the owner, 2026-11-16`) and leaving the original answer in place.

## Tests file

`decision.tests.md`, beside the decision file:

    # Tests: triage decision
    _Every human overrule, as a case. Replay before any change to decision.md._

    ## case 1 (2026-11-16, by the owner)
    input: tests/inputs/2026-11-14-plan.md
    readiness: 1

    ## case 2 (2026-11-18, by platform-team)
    input: tests/inputs/support-ticket-0412.md
    kind: question

Inputs that may change or be archived are copied into `tests/inputs/` beside the decision file, so a case replays the same text forever.

## As a stage Check

In `stages/NN_<name>/CONTEXT.md`:

    ## Check (decision gate: see the decision-gates skill)
    Run `python -I scripts/decide.py stages/NN_<name>/decision.md runs/<id>/<input>`.
    It writes `runs/<id>/NN_decision.md` and `runs/<id>/NN_check.md`: `pass` when every answer
    routed to act or act-and-flag (flags listed), `fail: ask person — …` otherwise. A fail stops the run;
    the person answers in the `overrule:` lines, which become cases in `decision.tests.md`.

The decision file is listed under the contract's Inputs as Reference, so the gate's rules are read from the folder, not remembered.

## Inside a bounded loop

A rubric line in a **bounded-loop** Check can be a gate question. The question's pass option at act confidence reports `pass <id>`; any other answer reports `fail <id>: <answer> at <confidence>`. A person-routed answer (at or below `ask_below`, or `other`) marks the attempt **blocked**: its check file's first line is `blocked: ask person — <question>: <answer> at <confidence>`, and `loop_decide.py` stops the loop with exit 4 (bounded-loop reference → Blocked is not failing). The person answers in the `overrule:` line; that attempt is then re-evaluated before the loop goes on.

## Tuning

Look at the answers files and the tests file together, per question:
- **Overruled often:** reword it, add the missing option, or split it into two questions.
- **`other` piling up:** a pile is missing; add it as an option.
- **Flagged answers almost never overruled:** lower `act_at` a step and replay the tests.
- **Act-routed answers overruled:** raise `act_at`, or the question is unclear.
- **A question code could answer exactly:** move it to code and delete it from the file.
