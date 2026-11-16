# Check section: bounded loop

Paste this as the `## Check` section of `stages/NN_<name>/CONTEXT.md` in place of the single-shot Check, then replace every line with project-real content. The example is a release-update stage, `03_draft`.

    ## Check (bounded loop: see the bounded-loop skill)
    Shape: refinement (fixed target).

    Checks, run cheapest first, every attempt, against this list only:
    | id | layer | pass condition |
    |---|---|---|
    | length | script | `wc -w < runs/<id>/03_attempt-K.md` prints 200 or less |
    | banned | script | `grep -niwf references/banned-words.txt runs/<id>/03_attempt-K.md` finds nothing |
    | features | rubric | every feature named appears in `runs/<id>/02_release-notes.md` |
    | lead | rubric | the first sentence names what changed for the reader |
    A script fail skips the rubric for that attempt. Rubric checks run in a fresh reviewer
    sub-agent given only the attempt, this table and `02_release-notes.md`.

    Ending (written before attempt 1):
    - Done: every check passes.
    - Marginal: an attempt turns no check from fail to pass → stop.
    - Budget: 3 attempts.
    - Fixed target: every attempt is judged against this table, never against the previous attempt.
    Carry: each new attempt starts from the attempt loop_decide names and changes only its failing lines.

    Files: attempt K → `runs/<id>/03_attempt-K.md`; its results → `runs/<id>/03_attempt-K_check.md`.
    After each evaluation run
    `python -I scripts/loop_decide.py runs/<id> 03 --budget 3 --output runs/<id>/03_draft.md`
    (exit 3 = again; 0 = pass; 1 = fail, the run stops; 4 = an attempt is blocked, the run stops
    and the blocker goes to a person). It writes `runs/<id>/03_check.md`.
    An attempt that cannot run, or whose rubric line a decision gate routed to a person, gets a
    check file whose first line is `blocked: <why>`.

    Human check: the owner, after the checks and before `04_send` (mails customers; cannot be undone).
    They get `03_draft.md` and `03_check.md` and answer one question:
    "Ship it as is, or name the single change it needs?"
    Answer → `runs/<id>/03_review.md`, first line `go` or `fix: <one change>`.
    Remainder (left to the human check): whether the update fits this week's news; anything said
    that should not be.
