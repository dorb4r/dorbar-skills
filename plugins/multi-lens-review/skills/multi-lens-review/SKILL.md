---
name: multi-lens-review
description: >-
  Thorough code review of a pull request or branch by several specialist reviewers working in
  parallel, each through one lens (functionality/product fit, language expert, testing, data
  model, security, performance, simplicity, code architecture, frontend and design system), followed by a master reviewer that verifies every finding
  against the code, merges duplicates, re-rates severity and returns ONE ranked report. The
  functionality reviewer takes its product context from the target repo itself (layered context:
  CLAUDE.md, CONTEXT.md, references/, runs/), so the skill works on any system. Use when asked
  for a thorough, deep, multi-perspective, multi-agent or "send several reviewers" code review of
  a PR, branch or diff. Triggers: multi-lens review, review this PR thoroughly, several
  reviewers, specialist reviewers, review agents, master reviewer, deep code review, is this
  code necessary, simplify, too much code, duplication, separation of concerns.
---

# Multi-lens review

Review a change through several independent specialist lenses at once, then have a **master
reviewer** check every finding against the code and write a single report. You (the caller)
never hold the reviewers' raw output; you get back one verified, ranked report and relay it.

Why this shape:
- **Different lenses find different bugs.** A product reviewer catches "the schema can't
  represent what we agreed"; a data reviewer catches a missing constraint; a test reviewer
  catches tests that pass while the code is wrong. One generalist misses most of these.
- **Reviewers are confidently wrong sometimes.** The master reviewer is a skeptic: it opens each
  file and line, may run tests, drops what doesn't hold, and says why.
- **One report, not six.** Routing and dedup happen outside your context.

## The lenses

| Lens | Looks for | Context it loads |
|---|---|---|
| **Functionality** | Does the change implement what the product needs? Gaps and contradictions between the docs and the code; states, rules or flows the product needs that the code cannot represent. | **The target repo's own layered context** (see below). Nothing system-specific lives in this skill. |
| **Language expert** | Idiomatic, correct use of the repo's language and frameworks: error handling, resource lifetimes, API design of the touched packages, build tooling. | The language and frameworks detected from the repo (manifest files, file types in the diff). |
| **Testing** | Could the tests pass while the code is wrong? Missing cases and edges, tests asserting the wrong thing, isolation and cleanup, flakiness. | The tests in the diff plus the code they cover. May run the repo's test command. |
| **Data model** | Schema and persistence: constraints, tenancy or ownership boundaries, nullability, indexes against the queries that will run, migrations up and down, money and time types. | Migrations, models and the queries in the diff. |
| **Security** | Secrets handling, injection (SQL, URL, path, shell), authn/authz implied by the design, PII, cross-tenant leaks, dangerous tooling defaults. | The whole diff, plus config and tooling. |
| **Performance** | Real runtime cost at the product's expected scale: connections and pooling, N+1, unbounded work, missing indexes, cold starts. | The diff plus the deploy target named in the repo's context. |
| **Simplicity** | "Is this necessary? Can it be simpler?" Code nothing needs yet, speculative abstractions, defensive checks for impossible cases, pass-through wrappers, duplication (in the change, or of something the repo or a library already does). Says what to delete and how many lines it saves. | Every added line, plus the existing code it may duplicate. |
| **Code architecture** | Strict separation of concerns: one responsibility per module, one thing per function at one level of abstraction, dependency direction (domain never imports adapters), no vendor types across a port, code in the right place. | The repo's intended structure (`CONTEXT.md`, area contracts, standards), then the diff. |
| **Frontend & design system** | Enforces the repo's design system: UI built only from its component library, tokens instead of raw values, new visuals added to the library with a story, intent kept (not just lint). Plus accessibility, i18n/RTL, responsive layout, loading/empty/error states and React state/effect bugs. Uses the `ui-ux-pro-max` skill as its UX standard when installed. Reports nothing for changes without UI. | The design system (library README, tokens, stories, lint configs), the frontend area contract, then the UI parts of the diff. |

Simplicity and architecture pull in opposite directions (delete and merge vs. split). The
master reviewer settles each conflict: keep a separation only when the repo's docs require it or
it untangles a real mix of concerns; otherwise less code wins.

Drop a lens that has nothing to look at (no schema in the diff → skip **Data model**). Add one
when the change needs it (accessibility, i18n, API compatibility), using the same contract.

### Where the functionality lens gets its context
The skill stays system-agnostic because the **target repo carries its own context**. Point the
functionality reviewer at it, in this order (the `layered-context` skill's layers):

1. `CLAUDE.md`: identity and non-negotiable rules (test command, git rules).
2. `CONTEXT.md`: the router; find the areas the diff touches.
3. `<area>/CONTEXT.md`: the contract of each touched area.
4. `references/`: product definition, domain, decisions, standards, `app-state.md`.
5. `runs/<task>/`: the current task's plan. **This sets the review's scope.** Work the plan
   assigns to a later milestone is not a finding unless this change blocks it.

If the repo has no layered context, use whatever it has (README, docs/, ADRs, the PR
description), and **say in the report** that product context was thin.

## Procedure

### 1. Scope (you, inline: a few tool calls)
- Resolve the target: a PR number (`gh pr view <n>`), a branch, or a commit range. Work out the
  base and head, and the exact diff command, e.g. `git diff origin/main...HEAD`.
- Pick a **local checkout** of the head that the reviewers can read. Prefer an existing
  worktree; otherwise create a read-only worktree. Never review in a checkout someone is
  editing.
- Read the repo's `CLAUDE.md` for the **test command** and rules the reviewers must respect
  (for example "run tests only via `make test`").
- Detect the language and frameworks (`go.mod`, `package.json`, `pyproject.toml`, ...).
- Find the current task's plan in `runs/`, if one exists.

### 2. Run the review
**If the `Workflow` tool is available, use it.** Read the bundled `workflow.js` (in this skill's
base directory) and pass its **full text** as `script`, with `args` from step 1. Don't pass it as
`scriptPath`: the tool refuses paths outside the working directory, and an installed plugin lives
in the plugin cache. To run a subset of lenses, keep the script as is and set `args.lenses`.

```
Workflow({
  script: "<the full contents of workflow.js>",
  args: {
    repoPath: "/abs/path/to/checkout",          // required: read-only checkout of the head
    target: "PR #4 of org/repo (M1 backend)",   // required: one line, for the report
    diffCmd: "git diff origin/main...HEAD",      // required
    testCmd: "cd backend && make test",          // optional: the ONLY way reviewers may run tests
    stack: "Go 1.26, Chi, GORM, Postgres",       // optional: detected in step 1
    scopeDoc: "runs/001-mvp/plan.md",           // optional: what's in or out of scope
    lenses: ["functionality","language","testing","data","security","performance","simplicity","architecture","frontend"], // optional subset
    extraLenses: [{ key: "a11y", title: "Accessibility", prompt: "..." }],           // optional
    notes: "anything reviewers must know (e.g. do not touch DATABASE_URL)"            // optional
  }
})
```

The script runs the lenses in parallel (read-only), then one master reviewer that verifies,
dedupes, re-rates and writes the report. It returns the report as markdown.

**Without the `Workflow` tool:** do the same by hand. Spawn one `Agent` per lens in a single
message (so they run in parallel), each with the shared rules plus its lens prompt from
`workflow.js`, asking for findings as structured JSON. Then spawn **one** master-reviewer
`Agent` with all the raw findings and the consolidation prompt from `workflow.js`. Don't
consolidate in your own context.

### 3. Report back
- Relay the master report: verdict, the ranked table, and the per-finding detail the user needs.
- **Pull out the decisions that belong to the user.** Some findings are product calls ("should
  this expire?", "which side wins?"), not bugs. Ask them as numbered questions, each with your
  recommendation, before fixing.
- Don't start fixing until the user agrees. When fixing: blockers and majors in the same PR;
  minors either fixed if cheap or written down as follow-ups in the repo (the task plan), not
  silently dropped.

## Rules for every reviewer
- **Read-only.** No edits, commits, pushes, or comments on the PR.
- Tests only through the repo's documented command. Never point anything at a production
  database or a live vendor account.
- Never print secrets (`.env`, keys).
- Only findings inside the change's scope. Each one needs **file:line, the problem, a concrete
  failure scenario, and a suggested fix**. No style nits unless they hide a bug.
- Few real findings beat many speculative ones. An empty list is a valid result.

## Severity
- **blocker:** must fix before merge (a bug, data-integrity or tenancy hole, security hole,
  contradiction with the product definition).
- **major:** should be fixed in this PR; cheap now, expensive once later work builds on it.
- **minor:** fine as a written follow-up.

## Lessons from real runs
- The master reviewer's **Dropped** list matters as much as the findings: it shows what was
  checked and rejected (wrong, out of scope, a duplicate), so nobody re-raises it.
- Generated code is usually too much code. Run the **simplicity** lens on every AI-written
  change; its findings are the cheapest fixes with the biggest effect on readability.
- Reviewers miss what tests *don't* exercise. Ask the testing lens to check whether each test
  could pass while the behaviour is broken: assert *which* constraint or error fired, and insert
  a valid row first.
- Verify a test harness's isolation instead of trusting it. A hosted database proxy silently
  dropped a `search_path` connection parameter, so "isolated" tests all shared one schema and
  passed only because of the order they ran in.
