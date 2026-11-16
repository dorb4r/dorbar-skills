# Decision: <name of the gate, e.g. "triage incoming planning docs">

<One sentence: which step this replaces, and what happens after it.>

## Input
`<exact path or glob, e.g. inbox/*.md, or runs/<id>/02_plan.md>`

## Thresholds
- act_at: 0.8
- ask_below: 0.5
- `other` always goes to a person.

## Questions

### kind (pick one)
What kind of document is this?
- plan
- build-log
- question
- other

### receiver (yes/no)
Does it name who receives its output?
- yes
- no

### readiness (rating 0-3)
How ready is the work it describes?
- 0: nothing formed yet
- 1: an idea with a goal
- 2: a plan someone could start from
- 3: already built

## Actions
Applied by the runner, never by the model.
- kind = plan → route to `stages/01_plan/`
- kind = build-log → file under `logs/`
- kind = question → route to the owner's queue
- receiver = no → add "name the receiver" to the item's todo
- readiness ≥ 2 and kind = plan → mark ready for `02_build`
- Combination rules (if any): <e.g. "of the drafts rated clear = yes, pick the highest curiosity; tie → shortest">

## Answers
- In a stage: `runs/<id>/NN_decision.md`; the stage Check is `runs/<id>/NN_check.md`.
- For filed items: `<input>.decision.md`, next to the input.

## Tests
`decision.tests.md`, beside this file. Replay every case before changing anything above.

## Run
`<the runner's command, e.g. python -I scripts/decide.py stages/03_triage/decision.md runs/<id>/02_plan.md>`
