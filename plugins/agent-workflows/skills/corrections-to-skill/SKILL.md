---
name: corrections-to-skill
description: >-
  Corrections-to-skill: turn a job you already do in chat, and keep correcting the same way, into
  a skill built from the evidence of those corrections. Keeps a corrections log (live, or mined
  from past chats), interviews the owner seeded with it, drafts the skill, audits the draft for
  invented rules and one-off examples turned into laws, moves client and project facts out of
  the skill into project context, and tests it in an empty chat on a real new input. Use when
  the same fixes keep being retyped ("too formal again", "don't promise that"), or someone wants
  a skill made from how they actually do a task. Not for a new skill with no correction
  history — use skill-creator. Not for formal evals, benchmarks or description tuning
  (skill-creator), or for deciding whether to automate a job at all (workflow-audit).
---

# Corrections to skill

Every correction you type in chat is a decision the model could not have known: about your voice, about what is actually true, about who you are to the reader. Retyping them each week means the method lives in your head. This skill writes the method down once, from the corrections themselves, so the skill holds what you said and nothing the model invented.

## What this skill owns, and what it hands off
- **Owns:** the corrections log as evidence; the trace from every rule back to a correction; the audit for invented rules and one-example laws; the split of method (skill) from facts (project context); the empty-chat test.
- **Interview mechanics** → **grilling** (step 2 supplies only the branches).
- **Wording** of the SKILL.md → **writing-for-agents**.
- **Eval suites, benchmarks, description optimisation** → **skill-creator**, given the finished, tested skill (step 7). Its intent-capture interview is already answered by steps 1-2: hand it the skill, not the job.
- **Filing** the skill into a marketplace → the repo's **add-skill** skill, when present.
- A job with several stages and files passed between them is a pipeline: run **workflow-audit** first.

## Procedure
Create `runs/<YYYY-MM-DD>-skill-<name>/`. Every step writes its file there.

### 1. Keep the corrections log
Copy [templates/corrections-log.md](templates/corrections-log.md) to `01_corrections.md`. Fill it one of two ways:
- **Live:** do the job in chat on real inputs. Each time you correct the output, log it in your own words.
- **From past chats:** read transcripts of the job already done and pull out every place the owner pushed back, plus each call the model made silently that the owner kept (tone, length, an assumption).

Each entry records what the output did, the correction, its **kind** (voice / fact / relationship / scope / format), its **cost if missed** (high when a wrong output promises, commits or misstates something), the instance it came from, and **method or fact**: would it hold for the next client or project?
**Done when** the log covers at least two separate instances of the job and every entry has all fields. A correction seen in both instances is the strongest evidence; mark it `repeated`.

### 2. Interview, seeded with the log
Run the interview with the **grilling** skill, seeding the design tree with these branches:
- **The one job:** what the skill does, and what it leaves to other skills.
- **When it fires:** the requests that should trigger it, and near-misses that should not.
- **A good output:** one the owner would send unchanged, and what makes it right.
- **Each high-cost or single-instance correction:** a rule for every case, or true only for this client, this week, this input?
- **Silent model calls kept:** which become rules, which stay open.
- **Hard limits:** anything that must never happen (send, promise, delete). These need a permission mode or a hook as well as a rule (layered-context reference → Human checks and enforcing stops); note them.

If grilling is not installed, ask these branches in rounds, each question with a recommended answer. Write the answers to `02_interview.md`.
**Done when** the owner confirms shared understanding and every `high` or single-instance log entry has a ruling.

### 3. Split method from facts
Sort every log entry and interview answer into one home:
- **Method** (how this kind of job is done, for anyone): goes in the skill.
- **Facts** (this client's dates, prices, names, agreements; this project's terms): go in project context: `references/<client-or-project>.md` in a layered-context repo, or the project's knowledge files. The skill says where to look for them, never what they are.

Test each line: *would it still be true for the next client?* No → fact.
**Done when** every entry has exactly one home, recorded in a `home` column of `01_corrections.md`.

### 4. Draft
Write `SKILL.md` in the run folder from [templates/SKILL.draft.md](templates/SKILL.draft.md), wording per **writing-for-agents**. Each method entry becomes a rule or a step in the owner's words; the description states the job, the trigger branches from the interview, and what it is not for. Keep a trace table in `04_trace.md`: every rule → the log entries or interview answers it rests on.
**Done when** every method entry appears in the draft and every rule in the draft has a row in `04_trace.md`.

### 5. Audit the draft
Spawn a reviewer sub-agent with no conversation context. Give it `01_corrections.md`, `02_interview.md`, the draft and the [audit questions](reference.md#draft-audit); it marks each rule `traced`, `invented`, `one-example law`, `fact leak`, or `not your voice`. Bring every non-`traced` rule to the owner: cut it, scope it to its real case, move it to project context, or reword it in their words. Write `05_check.md`, first line `pass` or `fail: <why>`.
**Done when** every rule is `traced`, or the owner explicitly kept it, and `05_check.md` says `pass`.

### 6. Test in an empty chat
Install the draft where a fresh session can find it, open a new session with no history, and give it the **next real input** of the job (one not in the log) with a bare request ("reply to this"). Recipe: [reference.md](reference.md#empty-chat-test).
Pass needs all three: the skill fires and says so; no logged correction is needed again; nothing is stated that the input or project context does not support. On a fail, fix the description if it did not fire, or the rule if a correction came back, and rerun with another fresh input. Write `06_check.md`, first line `pass` or `fail: <why>`, with the input and the output.
**Done when** `06_check.md` says `pass` on an input the skill has never seen.

### 7. Hand off
- Ship it: file the skill with **add-skill** in a marketplace repo, or copy it to the user or project skills folder.
- Keep logging: new corrections from real use go into a fresh log; change one rule at a time and rerun step 6. Corrections that stop appearing mean the skill is holding.
- Need a measured suite (many prompts, variance, a tuned description)? Hand the shipped skill and the run folder to **skill-creator**.

**Done when** the skill is installed where the owner works and the owner knows where new corrections go.

Draws on Jake Van Clief's Clief Notes course (Foundation lessons on chat and skills) and his talk on extracting decisions from dialogue, restated in our own words.
