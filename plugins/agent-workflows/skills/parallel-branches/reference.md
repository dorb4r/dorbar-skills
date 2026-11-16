# Parallel branches: reference

Contents: Worked example · Pair table · Edge lines · Merge stage · Rulings · Edge cases.

## Worked example
Job: ship a new `export` endpoint with three deliverables: the handler code, the public API docs page, and the release-notes entry.

**First cut, by phase** ("design", "build", "document"): each phase waits on the one before. That is a sequence; it belongs in layered-context stages, not here.

**Second cut, by deliverable:** `handler`, `docs`, `release-notes`. Run the tests:

| Pair | Question test | Shared-fact test | Order-flip test | Arrow → treatment |
|---|---|---|---|---|
| handler × docs | docs asks "what are the query params and error codes?" → lives in handler | both state the route, params, limits | yes: docs would copy whatever handler chose | share: route, params, error codes, rate limit on the facts sheet |
| handler × release-notes | notes asks "is it behind a flag?" → lives in handler | both state the flag name | yes | share: flag name and default on the sheet |
| docs × release-notes | notes asks "what do we call the feature?" | both name the feature | no | share: the feature's public name on the sheet |

Every arrow became a sheet line. The sheet (route, params, error codes, rate limit, flag, public name) is approved first; then the three branches run beside each other.

## Pair table
One row per pair, in `NN_cut.md`. Columns: pair · question test (the question, and where its answer lives) · shared-fact test (the fact) · order-flip test (yes/no, and what would change) · arrow → treatment (sequence / share / merge, and the artifact or step it becomes). Write "none" for a test that finds nothing; a blank cell is an unrun test.

Treatment guide:
- **Share** when the answer is a fact that can be decided before work starts (a name, a number, an interface signature).
- **Sequence** when the answer only exists after real work (a schema that must be designed, a measurement that must be taken): that work becomes its own upstream stage, and its output joins the sheet.
- **Merge** when two branches would trade more than two or three questions: they are one branch.

## Edge lines
Before writing briefs, write one line per edge in `NN_cut.md`: who gives what to whom, in what state, in what form.

```
NN_facts.md (approved) → every branch, read-only
NN_branches/handler/brief.md → handler worker
handler worker → NN_branches/handler/return.md + src/export/ (its write path)
every return.md → NN_merge.md (the merge step)
```

What crosses is an **artifact**, never history: no chat transcript, no "background" thread, no sibling's draft. A long history beside a short sheet carries the rejected options too, and the history is longer, so it wins attention. Status rides with the artifact (`draft` / `approved by <who>` / `superseded`) so no branch treats a maybe as a fact.

## Merge stage
The merge is a step with its own contract. When the run uses `stages/`, keep it beside the hosting stage's contract as `stages/NN_<name>/merge.md` and list it in that stage's `CONTEXT.md` (`NN` is the hosting stage's number, as for every fan-out file):

```
# NN merge — rule on every difference between branch returns

One job: turn N branch returns into one result by explicit rulings.

## Inputs
- Working: `runs/<id>/NN_branches/*/brief.md`, `runs/<id>/NN_branches/*/return.md`
- Working: `runs/<id>/NN_facts.md`, `runs/<id>/NN_merge.md` (cross-read list, written before dispatch)
Do NOT load: the chat that produced the branches, past runs/, _archive/.

## Process
1. Any return missing → stop and say which.
2. Read each return alone against its brief; note contract failures per branch.
3. Read side by side against the cross-read list; append every difference to NN_merge.md. Fix nothing yet.
4. Rule each difference (pick one + why / one owner / send up). Fact contradictions always go up.
5. Apply the rulings to produce the merged result.

## Outputs
- `runs/<id>/NN_merge.md` (differences + rulings), the merged deliverable(s)

## Check
A reviewer sub-agent that produced no branch confirms: every difference has a ruling, every ruling is applied,
no fact appears that is not on the sheet. Writes `runs/<id>/NN_check.md`, first line `pass` or `fail: <why>`.
Then the owner reads the merged result before anything irreversible.
```

When the run has no `stages/`, the same contract runs inline from `NN_merge.md`.

## Rulings
Every difference gets exactly one, with the ruler's name:
- **Pick one**: "Lead with the time saved, as the docs draft does; the release-notes draft led with the format list, which the reader can find in the docs. (owner)"
- **One owner**: "Both docs and notes explain the rate limit. Docs owns it; notes links to it. (owner)"
- **Send up**: "Docs says 1,000 rows per page, handler enforces 500. Fact contradiction → sheet line fixed to 500, docs reruns. (owner)"

A difference with no ruling is an open item; `NN_check.md` fails on it.

**Independent agreement.** When two or more branches reached the same point without seeing each other, record it as corroborated in `NN_merge.md`. It weighs more than any single branch's claim, because it cannot be an echo. The reverse does not hold: a point only one branch raised is not wrong for being alone.

## Edge cases
- **Rerun scope.** When the sheet changes, rerun every branch whose brief or return touches the changed line (grep the returns for it); leave the rest.
- **A branch returns code.** Its write path is its own directory or worktree. The merge stage integrates the code; branches never edit each other's files.
- **The facts-I-lacked list is long.** Step 2 missed arrows. Add them to the pair table before the rerun, so the next run of this job starts with a better cut.
- **The same job recurs.** Keep `NN_cut.md` and the sheet template under `_templates/` so the next run starts from the proven cut.
