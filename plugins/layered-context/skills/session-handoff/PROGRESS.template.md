<!--
Copy to runs/<task-id>/PROGRESS.md (no runs/ folder: PROGRESS.md at the repo or worktree root).
Rewrite this note in place at every save. It holds current facts, not history. Budget: ~60 lines / ~800 tokens.
Delete these comments and any field that is genuinely empty ("none" is a valid value).
-->
# Progress: <task-id>, <one-line goal>

Updated: <YYYY-MM-DD HH:MM> by <who: person, session or agent>
Spec: <path to the task brief / issue / PRD this work serves>

## Workspace
- Path: <repo or worktree path>
- Branch: <branch>, last commit `<short SHA>` <subject>
- Dirty: <uncommitted files, or "clean">
- Tests: `<exact command>`, <N passing / M failing (names of the failing ones)>
- Running: <process, port, tmux/session id, or "nothing">
- Env: <assumptions the next session must reproduce: env vars by name, services, seed data, versions>

## Completed
- <result>, <where it lives: file, commit, PR, link>

## Checked
- <the check actually run> → <its observed outcome>

## In progress
- <partial work>, <where it stops and what state it is left in>

## Decisions
- <the choice>, because <reason>; revisit if <what would change it> (since <YYYY-MM-DD>, by <who>)

## Don't redo
- <approach tried> failed: <the evidence>. <what that rules out>

## Open questions
- <unknown or blocker>, <who or what can answer it>

## Facts I lacked
<!-- One line per fact this session or sub-agent needed that the note and spec did not hold. Never guess: stop, or leave a visible placeholder. -->
- <fact> → stopped | placeholder: <what stands in>

## Next
<one concrete first action, small enough to verify in one step, e.g. "run `<cmd>` and confirm test X fails on line Y">
