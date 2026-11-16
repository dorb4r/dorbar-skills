# Workflow audit: reference

Consulted from [SKILL.md](SKILL.md). Contents: Labels · Mechanisms · Scoring · Hand-off · Audit check · Trial · Worked example.

## Labels

| Label | Test | Typical mechanism | Smells |
|---|---|---|---|
| **code** | Same input gives the same output; nothing is decided. | export, API call, query, script, an existing app feature | a model asked to copy, sort, total or reformat |
| **rule** | You can write the decision as if/then on fields you already have. | a script branch, a filter, a lookup table | "the model decides" where the rule fits in one sentence |
| **model** | The step reads or writes language (summarise, draft, classify free text, extract from messy documents), or predicts an outcome from past data. | a prompt, a skill; for prediction, a trained or statistical model | a model holding a commitment; a chat model asked to forecast |
| **person** | The output binds someone (price, date, promise, hire), needs taste, or someone must answer for it. | a named reviewer at a gate | a person retyping what code could fetch |

Edge cases:
- **Agent or single call?** A model call inside fixed code (gather the inputs, one call, store the result) is the default. An agent, a model that picks its own tools in a loop, earns its cost only when the next action depends on what it just found and no rule can choose it.
- **Prediction** (who will pay late, which lead converts) is machine learning on your data. Label it **model**, write "prediction" in the reason, and the mechanism is a trained model, a statistical rule or a spreadsheet formula, never a free-text prompt.
- **A step that mixes labels** is two steps. "Draft the reply and promise the date" is model (draft) + person (the date).
- **Data capture** (getting the inputs into a usable shape) is usually the largest share of the work and is code. When the inputs are wrong or missing, fixing capture beats any model downstream.

## Mechanisms

Choose the smallest part that does the step; package or automate only after the simple version works by hand.

| Part | What it is | Its check catches only |
|---|---|---|
| prompt | the instruction for one request: input, result, constraints | what you read |
| skill | reusable instructions (plus files) a tool loads when a request matches | what its steps check |
| connector / MCP | access to another app's data or actions; its permissions define what is reachable | nothing by itself: permissions and review still matter |
| hook | an action the harness runs at an event (before a tool call, before save) | exactly the condition it tests |
| script | code for a calculation, transformation or validation | its rules; a bug repeats every run |
| plugin | a host-specific bundle of the above | per its parts |
| existing app feature | what the tool already does | per the app |
| person | a named role at a gate | what they are shown |

**Present vs verified.** A check that a field exists cannot prove the field is right. For each check, name one missing-value case and one wrong-value case and say which part catches each.

## Scoring

- **Impact** 1-5: value of a successful result. **Risk** 1-5: cost of a wrong one. Write the reason beside each; the numbers are decision aids, not a statistical estimate.
- **Four risk conditions.** Does the output (a) bind the business, (b) reach a customer, (c) feed another system, (d) damage trust if wrong? One condition sets risk to at least 3; two or more set it to at least 4.
- **Verdicts:**
  - **AUTOMATE**: useful, low-consequence, with tested limits, monitoring and a way to recover. Typically risk ≤ 2.
  - **HYBRID**: code or a model prepares; a person reviews consequential output before it is used. Typically risk 3-4, or any step meeting condition (a) or (b).
  - **MANUAL**: a person does it; a model may help with research or preparation. Typically risk 5, or impact too low to repay the build.
- **Enforcing a HYBRID halt.** A review folder or an `approved.md` makes the review visible; it cannot stop anything. The runner must check for approval, block when it is missing, and keep the agent from approving itself. Use the strongest stop that fits (layered-context reference → Human checks and enforcing stops), and **test that a missing approval blocks** before connecting real accounts.

## Hand-off

| Outcome | When | Next |
|---|---|---|
| **nothing** | no worth line; an app in use already does it; a platform release is likely to absorb it soon and the benefit until then is small; every step MANUAL | write the reason and a `recheck:` date or trigger in the belief line |
| **a script** | every step is code or rule | write it, test it against a run done by hand and diff the two, name its command (layered-context, invariant 8) |
| **a skill** | one person, one sitting, model steps plus a person check, nothing carried between runs | **corrections-to-skill** if the job is already done in chat with repeated corrections; otherwise **skill-creator** |
| **a pipeline** | several steps with files passed between them, different checks per step, or other people run it | **layered-context**, Pipeline shape, handed `runs/<id>/01_audit.md` (its Interview mode seeds from it): each audited step becomes a stage or a Process line, the label decides how it runs, the check column becomes the stage Check, each HYBRID step a person Check with its enforcement point |

Inside a pipeline: a step retried until its check passes → **bounded-loop**; a model judgment repeated many times with confidence routing → **decision-gates**; independent deliverables made side by side → **parallel-branches**.

**First version.** Build the smallest slice that proves the outcome (often the code steps plus one model step, with the person doing the rest by hand) and run it before adding the remaining steps. Add a piece only when a real need appears: the inputs keep changing, the steps repeat every time, or someone else must run it.

## Audit check

The reviewer sub-agent gets `01_audit.md` and this list only. `pass` requires every item; otherwise `fail:` naming the first missing one.
1. Outcome and baseline fields each hold a number or `unknown: measure by <how>`.
2. The worth line names revenue, cost or risk, or the verdict is **nothing**.
3. The exists/absorb/cheaper questions each cite evidence.
4. Every step has one label with a reason, one mechanism, and a check naming a missing-value and a wrong-value case.
5. No step mixes labels; no person-labelled decision sits inside a model step.
6. Every step has impact and risk with reasons, and the risk floors are applied.
7. Every HYBRID step names a reviewer and an enforcement point other than a file.
8. The hand-off names one outcome, its reason, the first version, and the trial measure.

## Trial

At the end of the trial period set in the brief, add a section `## Trial result` to `01_audit.md`: time per accepted result and correction rate (corrections per accepted result) against the baseline, plus running cost. Change one instruction or step at a time and keep it only if it improves those numbers on the same kind of input. Re-label steps the evidence moved: a model step behaving identically every run becomes code; a code step that keeps failing on edge cases may need a rule or a person. A step whose verdict changes updates its belief line in place.

## Worked example (fictional)

Job: chase overdue invoices each month. Finance-ops does it; about 3 hours a month; target: under 1 hour with no wrong amounts, over a two-month trial. Worth: cost down and cash in sooner.

| # | Step | Label | Mechanism | Check (missing / wrong) | I | R | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | Export unpaid invoices | code | accounting export or API | export empty / total differs from ledger | 3 | 2 | AUTOMATE |
| 2 | Keep those 30+ days overdue, drop disputed | rule | script | no due date / disputed flag ignored | 3 | 3 (c) | AUTOMATE |
| 3 | Fetch contact and last message | code | connector | no contact / wrong account matched | 3 | 3 (c) | AUTOMATE |
| 4 | Draft the reminder in house tone | model | skill | amount missing / amount differs from export | 4 | 4 (b, d) | HYBRID |
| 5 | Decide escalation or payment plan | person | finance lead | — | 5 | 5 (a, b) | MANUAL |
| 6 | Send | code | mail connector behind a blocking hook | sent without approval / sent to wrong contact | 4 | 4 (b, d) | HYBRID |

Challenges: step 4 stays model (tone varies by history); step 5 is never inside the draft prompt. Hand-off: a pipeline (four stages: collect = steps 1-3 as one script, draft, approve, send), first version = the script plus the draft step, with sending done by hand.
