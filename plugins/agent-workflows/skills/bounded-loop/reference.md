# Bounded loop: formats and reference

Contents: Files in a run · Attempt check file · `loop_decide.py` · Converting agains into checks · The reviewer brief · Where the human check goes · Research shape · Blocked is not failing · ICM's own Audit and Checkpoint blocks.

## Files in a run

    runs/<id>/
      03_attempt-1.md          # attempt 1 (stage Inputs only)
      03_attempt-1_check.md    # its result on every original check
      03_attempt-2.md          # starts from the attempt loop_decide named, changes only the failing lines
      03_attempt-2_check.md
      03_check.md              # the loop's verdict, written by loop_decide.py
      03_draft.md              # the stage output: a copy of the best attempt
      03_review.md             # the human check: `go` or `fix: <one change>`
      03_fix_check.md          # only after a `fix:`: the original list re-run on the fixed output

Attempts stay in the run folder until fold-in moves the run to `_archive/runs/`, like every other run file. Later stages list only the stage output (`03_draft.md`) as Input, never the attempts.

## Attempt check file

First line: the attempt's own verdict (`pass`, or `fail: <ids>`). Then one line per original check, in the contract's order:

    fail: features, lead
    - pass length
    - fail features: "bulk export" is named but absent from 02_release-notes.md (paragraph 2)
    - pass banned
    - fail lead: first sentence describes the team, not what changed for the reader

Check ids are short, stable and match the contract (`[A-Za-z0-9_.-]`). A fail's text names the line, paragraph, file:line or test name it failed on; the carry can only fix what evaluate names.

## `loop_decide.py`

Deterministic bookkeeping for the Decide step, so the rule is applied the same way every run.
- **Fixed target, enforced:** the ids reported by attempt 1 are the original list. An attempt that reports a different set exits 2 and must be re-evaluated against the full list.
- **Best:** the most checks passed; a tie goes to the earlier attempt (less drift).
- **Order of rules:** best passes everything → done (exit 0). Otherwise budget reached → stop (exit 1). Otherwise the latest attempt turned no check from fail to pass compared with the one before → marginal stop (exit 1). Otherwise exit 3 with the carry: which attempt to start from and its failing lines.
- **Blocked:** any attempt whose check file's first line is `blocked: <why>` ends the loop before the other rules: exit 4, `NN_check.md` first line `fail: blocked at attempt K: <why>`, nothing copied to the stage output.
- On exit 0 or 1 it writes `NN_check.md` (first line `pass` or `fail: <why>`, then every attempt's score and the best attempt's line-by-line result) and, with `--output`, copies the best attempt to the stage output.

## Converting agains into checks

| The again | The check | Layer |
|---|---|---|
| too long | under 200 words (`wc -w` ≤ 200) | script |
| a test fails | `pnpm test --filter api` exits 0; the failing test was written before attempt 1 | script |
| used words we never use | no match for `grep -niwf references/banned-words.txt` | script |
| claimed a feature we did not ship | every feature named appears in `runs/<id>/02_release-notes.md` | rubric |
| missed the point | the first sentence names what changed for the reader | rubric |
| wrong tone | reads like `examples/good-1.md` and `examples/good-2.md` on the two points named in the contract | rubric |
| "make it more professional" | not a check until it is named; until then it is remainder for the human check | — |

A failing test written before the work is the strongest evaluator available: it holds attempt nine to the same bar as attempt one and cannot be talked round.

## The reviewer brief

A rubric check runs in a fresh sub-agent that receives exactly: the attempt file, the check list (ids and pass conditions), and the lookup inputs the checks name. It does not receive earlier attempts, the producer's reasoning, or the conversation. It returns the attempt check file in the format above and nothing else. A check it cannot decide from what it was given is reported `fail <id>: cannot decide from inputs`, which is a sign the check needs rewriting.

## Where the human check goes

- **After every attempt** is the wrong place: the loop runs at the speed of a person's inbox, and each comment is a fresh opinion, so the target moves.
- **Nowhere** is the wrong place: the checks pass, the output leaves, and no check could hold what it costs if it is wrong.
- **Once, after everything countable and before the first irreversible step** is the right place. Whoever carries the consequences of the irreversible step owns the human check.

The question is written into the contract in advance: ship it as is, or name the single change it needs. An open-ended request for feedback restarts the polishing. In code work the irreversible step is usually the merge or the deploy; a required CI check or a hook is the strongest way to hold it (layered-context reference → Human checks and enforcing stops).

## Research shape

When there is no fixed target (what options exist, what competitors charge, where a bug could come from), the loop diverges and its ending is **saturation**:
- Each pass writes `runs/<id>/NN_pass-K.md` with a `## New this pass` section listing only what earlier passes did not find.
- Stop when `New this pass` comes back empty **twice in a row** (one empty pass can be a weak pass).
- Research gets a budget too (default 5 passes), and stopping on budget says so in `NN_check.md`: `fail: budget spent before saturation`.
- `loop_decide.py` handles refinement only; apply the saturation rule by reading the last two pass files.

Research that feeds a refinement (gather the facts, then polish the draft) is two stages, each with its own ending.

## Blocked is not failing

An attempt that cannot run (permission denied, missing credential, tool absent) is not a failed check, and neither is a rubric line that a **decision-gates** question routed to a person. Mark the attempt **blocked**: write its check file with first line `blocked: <why>` (no check lines needed). `loop_decide.py` then stops with exit 4 and the blocker goes to a person; budget attempts are kept for output that ran and fell short. Once the person answers, re-evaluate that same attempt against the full list (overwriting its check file) and run `loop_decide.py` again. Likewise, an attempt identical to the previous one is a marginal stop, whatever the budget says.

## ICM's own Audit and Checkpoint blocks

ICM's published conventions offer an optional Audit list (a check name plus its pass condition, run before the stage writes its output, revising on a fail) and an optional Checkpoint block (after which step, what the agent presents, what the human decides). Neither gives a number of revisions or says what each revision is judged against. This skill supplies that missing ending: the budget, the marginal rule, the fixed target and best-not-last. The Check section in `templates/check-section.md` holds all of it in one place, so a stage contract does not need the separate blocks.
