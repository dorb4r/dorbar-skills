# Audit: <job> — what to automate, and what to build

Run: `runs/<YYYY-MM-DD>-audit-<job-slug>/` · Owner: <role> · Audited: <YYYY-MM-DD>

## 1. Outcome
- For: <who receives the result>
- Their next action: <decide / send / fix what>
- Information comes from: <systems, files, people, today>
- What breaks, and who feels it: <failure> → <who>

## 2. Baseline brief
- Current work: <who does it, how often, where time is lost>
- Baseline: <time per accepted result, corrections included>
- Target: <what improves, by how much, over what trial period>
- Quality: <what must stay true for a result to count>
- Owner: <who reviews results and maintains the workflow>
- Challenged by: <role who does the work> on <date>

## 3. Worth building?
- Worth: <revenue up / cost down / risk down: number or range>
- Already done by an app in use: <yes/no/partly> — evidence: <link or test>
- Likely built in by the next model or platform release: <yes/no/unknown> — evidence: <…>
- Cheaper option: <template / spreadsheet / manual / person / none> — why it does or doesn't fit

## 4. Steps

| # | Step | Input → output | Label | Why this label | Mechanism | Check: missing case / wrong case | Impact (why) | Risk (why, conditions a-d) | Verdict | Reviewer + enforcement (HYBRID) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | code / rule / model / person | | | | | | AUTOMATE / HYBRID / MANUAL | |

## 5. Challenges
- Model steps that could be a rule or code: <…>
- Judgment handed to a model without a review point: <…>
- Steps that survive a model swap: <…>
- Agent loops, and why a fixed sequence can't do it: <…>
- 60/30/10 sanity check (code+rule vs model vs person): <counts and a sentence>

## 6. Verdict and hand-off
- Overall: <AUTOMATE / HYBRID / MANUAL>
- Build: <nothing / a script / a skill / a pipeline> — because <reason>
- Next skill: <layered-context (Pipeline) / corrections-to-skill / skill-creator / none>
- First version: <smallest slice that proves the outcome>
- Trial measure: <time per accepted result, correction rate> — review on <date>
- Belief line for `references/decisions.md`: `- <job>: <verdict>, <key gate> (since <date>, by <role>, ref <run path>)`
