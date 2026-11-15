---
name: session-handoff
description: >-
  Handoff notes for pausing and resuming agent work across sessions, machines, people or
  sub-agents, without re-pasting the conversation. Two branches: save (write or refresh a
  compact PROGRESS.md at a stopping point) and resume (read the note, verify it against
  git, tests and files, then continue). Use when asked to save progress, hand off, pause
  work, continue tomorrow, brief a sub-agent, when context is running out, or to resume /
  pick up where we left off in a new session.
  Triggers: save progress, handoff, hand off, pause work, resume, pick up where we left off,
  continue tomorrow, context running out, new session, progress note, PROGRESS.md.
---

# Session Handoff

A **progress note** carries a task across a break: a new session, another machine, a colleague, a sub-agent. It holds the useful facts (results, evidence, decisions, dead ends, the next step), not the transcript. The note is a **belief**, not a record: it was true when written, and resume checks it against reality before acting on it.

After Jake Van Clief's Clief Notes lesson on saving state; status-on-disk from icm-architect (MIT).

## Where the note lives
- **Layered repo** (has `AGENTS.md` and `runs/`): `runs/<task-id>/PROGRESS.md`, beside the task's other product.
- **Otherwise:** `PROGRESS.md` at the repo root, or the worktree root when the work is in a worktree. Tell the user which you used.
- One note per task. Never read `_archive/`.
- Durable decisions belong in `references/decisions.md` (the factory), not the note. See Graduate below.

## Choose the branch
- **Save**: you are stopping, switching, handing to someone, dispatching a sub-agent, or context is running low.
- **Resume**: a session starts on a task that has a note, or someone says "pick up where we left off".

## Save
1. **Gather reality**, don't recall it. Run `git status`, `git log -1 --oneline`, `git branch --show-current` and the task's test command; list running processes and ports you started. These fill the Workspace block.
2. **Rewrite the note** from [`PROGRESS.template.md`](PROGRESS.template.md) (first save: copy it). Rewrite every field to the current truth; replace stale lines where they stand and delete finished or moot ones. The note stays the same size as the work grows, it does not accumulate.
   - **Checked** records how each claim was verified (command and outcome). A completed item with no check is "In progress".
   - **Decisions** carry the choice, the reason, what would change it, and `(since YYYY-MM-DD, by <who>)`.
   - **Don't redo** keeps every dead end with its evidence, so the next session does not rediscover it.
   - **Next** is one concrete first action that can be verified in a single step.
3. **Graduate** any decision that will outlive this task into `references/decisions.md` as a belief line (format below), then cut it from the note or leave a one-line pointer.
4. **Fit the budget:** under ~60 lines / ~800 tokens. Over budget means transcript leaked in; cut narration, keep facts.

**Done when:** every Workspace field matches a command you ran this save; Next is a single verifiable action; no line describes something that is no longer true; the note is within budget; a reader with only the repo and the note could start without asking you anything.

## Resume
1. **Read** `AGENTS.md`, the task spec the note names, then the note. Nothing else yet.
2. **Verify before trusting.** Run `git status`, `git log -1`, check the branch, and run the note's test command. Open the files named under Completed and Checked. Check that listed processes or ports are actually up.
3. **Sort every claim** into two lists: **confirmed** (you saw it in git, a test run or a file this session) and **claimed** (only the note says so). Report both to the user, with each discrepancy.
4. **Reality wins.** When the note disagrees with what you observed, correct the note in place now, with today's date and your name on the changed lines. When two context files disagree with each other (note vs `references/decisions.md`, note vs spec), say so and stop. Do not choose.
5. **Continue** from Next, unless verification showed it is already done or blocked; then propose the replacement Next and confirm it.

**Done when:** each Completed/Checked claim is marked confirmed or claimed; the note matches observed reality; the user has seen the discrepancies; you are executing (or have proposed) one Next action.

## Handing off
- **To a sub-agent:** the note is its brief. Save first, then dispatch with the note path plus the scope of its slice; it reads only `AGENTS.md`, the spec and the note. It saves back to the same note (or reports to you and you save), never a second note.
- **To another person or machine:** commit or push the work and the note together; uncommitted state stays on the old machine. List anything that cannot travel (local env values, running processes) under Workspace › Env.

## Decision belief lines
In `references/decisions.md`, one bullet per decision, stating the current truth:

```
- Sessions are stored in Redis, not Postgres (since 2026-11-02, by platform-team, ref #41)
```

When it changes, replace the line in place with new since/by/ref. Never stack an "update:" line beneath the old one.

## Lifecycle
The note is per-task product (Layer 4). When the task ships, graduate surviving decisions, then move `runs/<task-id>/` to `_archive/` (root-level `PROGRESS.md`: delete it after graduating). A shipped task with a live note misleads the next session.
