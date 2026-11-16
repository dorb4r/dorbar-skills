# Context Hygiene: reference

Recipes and formats the `context-hygiene` procedure points at. Read the section a step names; nothing here needs reading top to bottom.

Contents: Belief lines · Keep test · Duplicate hunt · Stale signals · Proposal format · Fresh-session prompt · Planted-fact tests · Review line · Fold-in rule · The archive

## Belief lines

`references/decisions.md` and `references/app-state.md` hold one bullet per current belief. Each bullet states what is true now, then its provenance:

```
- Sessions are stored in Redis, not Postgres; TTL 24h. (since 2026-09-02, by platform-team, ref #142)
- Payments go through the v2 provider API only. (since 2026-10-11, by api-team, ref 3f9c2ab) recheck: when v1 sunset is confirmed
```

- **since** a date (`YYYY-MM-DD`), **by** a person or team, **ref** a PR number or commit. A line with no date cannot be doubted, so it cannot be corrected.
- **recheck:** only on a line expected to change, naming the date or event that should trigger a re-look.
- A changed belief **replaces** its line where it stands, with new provenance. The line never gains an `Update:` child or a sibling saying "ignore the line above".
- Group bullets under headings named for **when they are needed** (`## Auth`, `## Data`, `## Deploy`), not by when they were learned. Order within a group by the cost of getting it wrong.
- A belief only some tasks need moves to its own drawer file in `references/`, with one pointer line in the group saying when to open it.

Before/after, same facts:

```
before
- Use Postgres for sessions.
- Update: moved sessions to Redis.
- Update: Redis TTL is now 24h (was 1h).
after
- Sessions are stored in Redis, not Postgres; TTL 24h. (since 2026-09-02, by platform-team, ref #142)
```

## Keep test

For each candidate line in an always-loaded file, ask in order and stop at the first no:

1. Would an agent in a fresh session need to be told this again for its work to be right? No: it was disposable; drop it.
2. Is it the decision itself, or the story of reaching it? Keep the decision; the story is in the PR.
3. Is it durable, and does the line carry its provenance (since when, by whom)? Add the provenance, or drop it.
4. Is it worth a seat on every load? If you hesitate, move it to a drawer file behind a pointer.

## Duplicate hunt

Pull candidate keys from each base file, then find every file that holds each key:

```
# commands, paths, versions, ports, env vars, numbers with units
grep -rhoE '`[^`]+`|[A-Z_]{4,}|v?[0-9]+\.[0-9]+(\.[0-9]+)?|[0-9]+ ?(ms|s|MB|GB|%|req/s)' \
  AGENTS.md CONTEXT.md references stages --include='*.md' | sort | uniq -c | sort -rn | head -60

# for each key that matters, where does it live?
grep -rnF -- '<key>' . --include='*.md' --exclude-dir=_archive --exclude-dir=runs --exclude-dir=node_modules
```

Also grep names of things (services, tables, feature names, owners), because a renamed thing often survives under its old name in a second file. Pick the home by job: a standard goes in `standards.md`, a current-state fact in `app-state.md`, a choice-with-a-reason in `decisions.md`, a term in `domain.md`. Every other copy becomes a relative link to that home.

## Stale signals

| Signal | How to spot it | Usual fix |
|---|---|---|
| Stacked update | bullet starting `Update:`, "was X", "ignore the earlier" | rewrite the original line, remove the rest |
| No provenance | `context_budget.py --provenance` fails | add since/by/ref from `git log -S '<phrase>'`, or drop |
| Recheck overdue | `recheck:` date passed or its trigger happened | verify against code, rewrite with new since |
| Conflict | two lines, same subject, different answers | code decides; if code cannot, ask the human |
| Code contradicts | grep the symbol / read the config / run the command | rewrite to match the code |
| Shipped plan in factory | a plan or spec in `references/` whose work is merged | move to `_archive/` or its `runs/<id>/` |
| Dead route | router names a folder or file that is gone or empty | remove the route |
| Unrouted file | nothing in any router or contract points at it | route it, or archive it |
| Model default | an instruction the current model follows without being told; sweep for these after every model or harness upgrade | remove after a fresh-session check without it |
| Diary line | "tried", "we discussed", "for now", undated "this week" | rewrite as a rule with provenance, or drop |
| Routing file with content | `AGENTS.md` or a `CONTEXT.md` explaining instead of pointing | move content to a shelf, leave a pointer |

Useful git lookups: `git log -S '<phrase>' --oneline -- <file>` finds when a line entered; `git log --merges --since=<last review> --oneline | wc -l` counts merged features since the last review.

A line marked stale is fine to keep while you check it. A line that states a wrong fact with confidence is the one that hurts.

## Proposal format

`04_proposal.md`:

```
# Context hygiene proposal (YYYY-MM-DD)

Budget: before <N> tokens always-loaded / after <M> (projected)

| # | File:line | Action | New text or new path | Evidence | Referrers updated |
|---|-----------|--------|----------------------|----------|-------------------|
| 1 | references/decisions.md:14-16 | rewrite in place | "- Sessions ... (since ..., by ..., ref #142)" | src/session/store.ts:8 | - |
| 2 | references/plan-billing-v2.md | move to _archive/ | _archive/plan-billing-v2.md | merged in #188 | CONTEXT.md:22 |
| 3 | runs/2026-08-03-spike/ | delete (generated) | - | no referrers, spike abandoned | - |

Open conflicts (human decides):
- decisions.md:9 vs app-state.md:31: rate limit 100 vs 200 req/s; code reads it from env, value unknown.
```

Actions allowed: rewrite in place, replace with pointer, move to `_archive/`, delete a generated run. Each row cites evidence. Each move lists every referrer found and how it is updated. On macOS and Windows, check the destination name case-insensitively before moving, since a rename can silently overwrite a file differing only in case.

## Fresh-session prompt

Spawn a general-purpose sub-agent with no conversation context and this prompt (fill the two tasks):

```
You are new to the repository at <ROOT>. Start by reading AGENTS.md and follow only the pointers
you find. Answer briefly:
1. What is this repo and what does it do?
2. What work is in progress right now?
3. What is next?
4. Where would you go, file by file, to do this task: <a recent, common task>?
5. Where would you go for this one: <a rare task, e.g. rotate a secret, add a locale>?
6. Did any two files tell you different things? Quote both.
Then list every file you opened, in order, with one line on why.
```

Score it: each answer right or wrong against the code and the human; files opened that the task did not need; hops from `AGENTS.md` to the right contract (two or fewer). Question 6 checks the disagreement rule in `AGENTS.md` actually fires.

## Planted-fact tests

The fresh-session prompt proves the map routes. These prove the beliefs are actually used. Each runs in its own fresh sub-agent with no conversation context.

**Recall** (on the real tree). Pick three belief lines, favouring ones deep in a long file. Before giving any task, ask: "What do you know about <subject of the line>? Say which file told you." Pass: it states the line's content and cites its file. A line that is routed but not recalled is stored, not remembered: move it under a heading named for when it is needed, or into a drawer file with a pointer, then retest.

**Correct** and **remove** run in a scratch copy so the real tree is untouched. Build the scratch copy from the working tree, so uncommitted approved edits are in it: `scratch=$(mktemp -d) && rsync -a --exclude .git ./ "$scratch/"` from the repo root. Run the test there, then delete it (`rm -rf "$scratch"`).

- **Correct:** change one belief line there to a new, plausible value (a TTL, a send day, a provider). Ask a question whose answer depends on it. Pass: the answer uses the new value. Fail: it repeats the old value, so another copy or a stale source still holds it; find it (duplicate hunt) and fix the real tree.
- **Remove:** delete one belief line there. Ask the same kind of question. Pass: it says the context does not state this (and where it looked). Fail: it invents an answer; make "if a fact is not in the context, say so" explicit in `AGENTS.md` rules and retest.

Delete the scratch copy afterwards. Record each test's question, the planted change, the answer, and pass/fail in `05_fresh_session.md`.

## Review line

One line in the root `CONTEXT.md`, under a `## Maintenance` heading:

```
- Next context review: 2026-12-15 or after 5 merged features, whichever first. Run the context-hygiene skill. (last: runs/2026-11-15-context-hygiene/)
```

Suggested cadence: monthly for an active repo, quarterly for a quiet one; the feature trigger catches bursts. Shorten the interval if a review needed more than a handful of rewrites; lengthen it if two reviews in a row found nothing.

## Fold-in rule

Paste into the delivery (ship) stage contract, under Process, so beliefs are corrected when they change instead of piling up for the review:

```
- Fold in: for every belief this change alters, rewrite its line in place in
  `references/decisions.md` or `references/app-state.md` with new provenance
  (since <today>, by <who>, ref <PR#>). Remove the lines it supersedes. Move this run's
  plan out of `references/` if it was ever placed there. Add no "Update:" lines.
```

And under its `## Check`: `context_budget.py --provenance` exits 0.

## The archive

- `_archive/` holds retired context: shipped plans, old specs, removed folders, optional `decisions-history.md`. Its route line in `AGENTS.md` reads, in effect, "retired; never read". Scripts skip it.
- Move into it only after the referrer check, and keep the relative path shape (`references/plan-x.md` becomes `_archive/references/plan-x.md`) so it is easy to restore.
- `decisions-history.md` is append-only: the removed line, its old provenance, and the ref that superseded it. Git already keeps this; the file is a convenience for humans, never an input.
- Generated `runs/` folders that nobody will reopen are deleted, not archived; their final outputs already live in the code or in git history.
