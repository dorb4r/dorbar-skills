# Cut: <task-id>

<!-- NN is the hosting stage's number (01 when the run has no stages/); every fan-out file shares it. -->

Fan-out reason: <independent pieces | exceeds one worker's attention | would overwrite each other>
Why parallel here (ICM default is one lane): <one line>

## Branches
| Branch | Deliverable | Write path |
|---|---|---|
| <name> | <one deliverable> | <only this branch writes here> |

## Pair tests
<!-- One row per pair (N·(N-1)/2). "none" for a test that finds nothing; a blank cell is an unrun test. -->
| Pair | Question test | Shared-fact test | Order-flip test | Arrow → treatment |
|---|---|---|---|---|
| A × B | | | | |

## Edges
<!-- One line each: who gives what to whom, in what state, in what form. -->
- `NN_facts.md` (approved) → every branch, read-only
- `NN_branches/<name>/brief.md` → <name> worker
- <name> worker → `NN_branches/<name>/return.md` + <write path>
- every `return.md` → the merge step (`NN_merge.md`)
