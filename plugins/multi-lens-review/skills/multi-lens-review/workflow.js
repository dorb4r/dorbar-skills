export const meta = {
  name: 'multi-lens-review',
  description: 'Specialist reviewers in parallel (functionality, language, testing, data, security, performance), then a master reviewer verifies, dedupes and ranks into one report',
  whenToUse: 'Thorough review of a PR or branch. Pass args: repoPath, target, diffCmd (+ optional testCmd, stack, scopeDoc, lenses, extraLenses, notes).',
  phases: [
    { title: 'Review', detail: 'one read-only reviewer per lens, in parallel' },
    { title: 'Consolidate', detail: 'master reviewer verifies each finding against the code and writes one report' },
  ],
}

// ---- Inputs -----------------------------------------------------------------
const A = args || {}
for (const k of ['repoPath', 'target', 'diffCmd']) {
  if (!A[k]) throw new Error(`multi-lens-review: args.${k} is required`)
}
const testRule = A.testCmd
  ? `If you run tests, use exactly \`${A.testCmd}\` from ${A.repoPath}. Never run tests any other way.`
  : 'Do not run tests unless the repo\'s CLAUDE.md documents how; then use exactly that command.'

const COMMON = `You are one reviewer in a multi-lens code review of: ${A.target}.
The change is checked out at ${A.repoPath}. Work ONLY from that directory.
See the change with: cd ${A.repoPath} && ${A.diffCmd} --stat   and   ${A.diffCmd} -- <path>
${A.stack ? `Stack: ${A.stack}.` : 'Detect the stack from the repo (manifest files, file types in the diff).'}
Scope: ${A.scopeDoc ? `the current task plan is ${A.scopeDoc}; work it assigns to a later milestone is NOT a finding unless this change blocks it.` : 'look for a task plan under runs/ (layered context) or the PR description; out-of-scope work is not a finding.'}
Rules:
- READ-ONLY. Do not edit files, commit, push, or comment on the PR.
- ${testRule}
- Never point anything at a production database or a live vendor account. Never print secrets (.env, keys).
- Report only concrete issues inside the change's scope. Each finding needs file + line, the problem, a concrete failure scenario, and a suggested fix. No style nits unless they hide a bug.
- Few real findings beat many speculative ones. An empty list is fine.
${A.notes ? `Notes from the caller: ${A.notes}` : ''}`

const ALL_LENSES = [
  {
    key: 'functionality',
    title: 'Functionality (product fit)',
    prompt: `LENS: functionality / product fit. You have no product knowledge of your own: load it from the repo's layered context, in this order, reading only what the change touches:
1. CLAUDE.md (identity, non-negotiable rules)
2. CONTEXT.md (router: which areas does the diff touch?)
3. <area>/CONTEXT.md for each touched area (its contract)
4. references/ (product definition, domain/state machines, decisions, standards, app-state)
5. runs/<task>/ (the current plan: what this change is supposed to deliver)
If the repo has no layered context, use README, docs/, ADRs and the PR description, and say in your summary that product context was thin.
Then check the change against it: requirements missing or contradicted, states/transitions/rules/flows the product needs that the code cannot represent, documented risks the design ignores, and docs that now disagree with the code.`,
  },
  {
    key: 'language',
    title: 'Language expert',
    prompt: `LENS: expert in the repo's language(s) and frameworks${A.stack ? ` (${A.stack})` : ''}. Check idiomatic and correct use: error handling and wrapping, context/cancellation, resource lifetimes and leaks (connections, files, bodies), concurrency, the exported API of touched packages and module boundaries per the repo's area contracts, HTTP client behaviour (timeouts, non-2xx and non-JSON bodies), build tooling (Makefile/scripts/env loading), dependency hygiene.`,
  },
  {
    key: 'testing',
    title: 'Testing expert',
    prompt: `LENS: test quality. For each test in the change ask: could it pass while the code is wrong? Check that tests assert WHICH error/constraint fired (not just "an error"), that "valid input is accepted" cases exist next to "invalid is rejected", that state machines are covered exhaustively where the plan requires it, edge values, isolation and cleanup (shared databases, leftovers, parallel runs), and flakiness. Verify the harness's isolation instead of trusting it. You may run the tests.`,
  },
  {
    key: 'data',
    title: 'Data model expert',
    prompt: `LENS: data model and persistence. Check schema/migrations and how code writes to them: tenancy/ownership boundaries (can a row point into another tenant?), missing or wrong constraints, nullability and override semantics, invariants the docs state but the database doesn't enforce, indexes against the queries the plan says are coming, migration up/down correctness, money (integer minor units + currency) and time (timestamptz/UTC) types, seed or backfill semantics (does re-running overwrite user data?).`,
  },
  {
    key: 'security',
    title: 'Security expert',
    prompt: `LENS: security. Secrets handling (storage, references, env loading, logs), injection (SQL including hand-built literals, URL/path, shell), authentication/authorization implied by the design (who can perform each action?), PII handling, cross-tenant leakage, dangerous defaults in tooling (destructive commands without guards, prod credentials reachable from dev commands), committed data that should not be in the repo.`,
  },
  {
    key: 'performance',
    title: 'Performance expert',
    prompt: `LENS: performance and runtime behaviour on the deploy target named in the repo's context. Connection handling and pooling (serverless + pooled databases, advisory locks), cold starts, HTTP client reuse and timeouts, N+1 and unbounded work, index coverage for expected queries, anything that grows per request with tenants or users. Only report issues with real impact at the product's expected scale, or a clear path to it.`,
  },
]

const wanted = A.lenses && A.lenses.length ? A.lenses : ALL_LENSES.map(l => l.key)
const unknown = wanted.filter(k => !ALL_LENSES.some(l => l.key === k))
if (unknown.length) log(`Ignoring unknown lenses: ${unknown.join(', ')}`)
const LENSES = ALL_LENSES.filter(l => wanted.includes(l.key)).concat(A.extraLenses || [])
const skipped = ALL_LENSES.filter(l => !wanted.includes(l.key)).map(l => l.title)
if (skipped.length) log(`Lenses not run: ${skipped.join(', ')}`)

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          file: { type: 'string' },
          line: { type: 'integer' },
          title: { type: 'string' },
          problem: { type: 'string' },
          failure_scenario: { type: 'string' },
          suggested_fix: { type: 'string' },
        },
        required: ['severity', 'file', 'title', 'problem', 'failure_scenario', 'suggested_fix'],
      },
    },
    summary: { type: 'string' },
  },
  required: ['findings', 'summary'],
}

// ---- Review: lenses in parallel ------------------------------------------------
phase('Review')
const reviews = await parallel(LENSES.map(l => () =>
  agent(`${COMMON}\n\n${l.prompt}`, { label: `review:${l.key}`, phase: 'Review', schema: FINDINGS })
    .then(r => r && { lens: l.title, ...r })))

const done = reviews.filter(Boolean)
const missing = LENSES.filter((l, i) => !reviews[i]).map(l => l.title)
if (missing.length) log(`Reviewers that returned nothing: ${missing.join(', ')}`)
log(`${done.reduce((n, r) => n + r.findings.length, 0)} raw findings from ${done.length} reviewers`)

// ---- Consolidate: one skeptical master reviewer --------------------------------
phase('Consolidate')
const report = await agent(`You are the MASTER REVIEWER for: ${A.target}.
The change is checked out at ${A.repoPath} (diff: ${A.diffCmd}). READ-ONLY: no edits, commits, pushes or PR comments. ${testRule}

Specialist reviewers (${done.map(r => r.lens).join(', ')}) produced the raw findings below.
1. VERIFY every finding against the actual code: open the file and line, run a test if needed. Be skeptical. Drop anything wrong, speculative, out of scope (${A.scopeDoc || "the repo's current task plan"}), or already handled.
2. MERGE duplicates across lenses into one item and note which lenses raised it.
3. RE-RATE severity: blocker = must fix before merge (bug, data-integrity or tenancy hole, security hole, contradiction with the product definition); major = fix in this PR (cheap now, expensive later); minor = fine as a written follow-up.
4. Mark findings that are really PRODUCT DECISIONS for the owner (not bugs) as "needs a decision", with the options.
5. Write ONE report in GitHub-flavoured markdown for the repo owner (plain and concrete; not everyone is an expert in every area):
   - one-line verdict: merge / merge after fixes / needs rework
   - what you ran to verify (e.g. the test command and its result)
   - a table of confirmed findings: #, severity, lens(es), file:line, one-line issue
   - per finding: problem, failure scenario, fix (short)
   - "Needs a decision": the product calls, each with options and a recommendation
   - "Dropped": each rejected finding with a one-line reason
   - one line per lens summarising what it found
Return only the markdown report.

Reviewers that returned nothing: ${missing.length ? missing.join(', ') : 'none'}.

RAW FINDINGS (JSON):
${JSON.stringify(done, null, 1)}`, { label: 'master-review', phase: 'Consolidate' })

return report
