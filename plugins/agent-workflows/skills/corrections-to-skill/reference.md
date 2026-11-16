# Corrections to skill: reference

Consulted from [SKILL.md](SKILL.md). Contents: Reading a correction · Mining past chats · Draft audit · Method or fact · Empty-chat test.

## Reading a correction

A correction is a decision the model lacked. Name what kind it is; the kind decides where the rule lands and how it is worded.

| Kind | It is about | Becomes | Example correction → rule |
|---|---|---|---|
| voice | how the owner sounds | a style rule in the skill | "too stiff" → "Match the sender's length; plain words, no stock openers." |
| fact | what is actually true or booked | a *lookup* rule in the skill + the fact in project context | "the room isn't confirmed" → "State dates, rooms and prices only when the client notes confirm them; otherwise say when we will confirm." |
| relationship | who the owner is to this reader | a rule keyed to a field the skill can read | "sign it with my first name" → "Sign with the name in the sender profile." |
| scope | what the output covers or leaves out | a step, or a "leave to X" line | "don't summarise the attachment" → "Answer the question asked first; mention attachments only if asked." |
| format | shape, length, structure | a template or a format rule | "bullets, not prose" → a template in the skill folder |

**Cost if missed.** A wrong commitment (a date, a price, a promise) costs far more than a stiff sentence. Mark those `high`; they get a ruling in the interview and, if they must never happen, an enforced stop outside the skill.

## Mining past chats

When the job has already been done in chat, the transcripts are the log. For each exchange record, on the owner's side: the goal, every constraint added along the way, every example given ("like this one"). On the model's side: each decision it made and each assumption it ran on, and whether the owner kept or changed it. A kept assumption is a rule nobody wrote down yet; put it to the owner in the interview rather than adopting it silently.

## Draft audit

Questions the reviewer sub-agent applies to every rule in the draft:
1. **Traced?** Which log entry or interview answer says this? None → `invented`.
2. **One-example law?** Does the rule rest on a single instance but read as "always"/"never"/a fixed value? → `one-example law`. The owner either confirms it is general or it is scoped ("when the client asks about dates, …").
3. **Fact leak?** Does it name a client, a date, a price, a person, a product detail that belongs to one project? → `fact leak`: move the fact to project context and leave a lookup instruction.
4. **Voice?** Is it worded the way the owner talks in the log, or in generic assistant prose? → `not your voice`; reword from the owner's own phrases.
5. **Missing?** Any method entry in the log with no rule in the draft is reported as a gap.

Write each verdict beside the rule in `05_check.md`; the first line is `pass` only when every rule is `traced` or owner-kept and there are no gaps.

## Method or fact

- In the skill: how to do this kind of job for anyone; where to find the facts ("read the client's notes file before stating any date").
- In project context: everything about one client or project. In a layered-context repo that is `references/<client>.md`, loaded by the stage that needs it; in a chat app, the project's knowledge files.
- Context true in every session (the owner's name, role) belongs in the user-level instructions, not in the skill.
- Symptom of mixing: the skill gives the next client the last client's date.

## Empty-chat test

The point: an empty desk. Nothing from the drafting session, no pasted guidance, only the skill and the project context it is meant to read.

**Claude Code:**
1. Copy the run folder's `SKILL.md` (and any templates) to `.claude/skills/<name>/` in the project where the job happens, or `~/.claude/skills/<name>/`.
2. From that project, start a new session (`claude`, or `claude -p "<bare request>"` with the input file path) with no `--resume` and no extra prompt.
3. Give the bare request and the new input. Watch for the skill being loaded.

**Chat apps:** upload the skill (in Claude: Customize → Skills), open a new chat in the right project, paste the new input with a bare request.

**Inputs:** use a real instance that is not in the log. If none is at hand yet, ask the owner for the next one rather than reusing a logged instance; a reused input tests memory of the drafting session's examples, not the method.

**Reading the result:**
- Did not fire, or fired on the wrong request → the description lacks the trigger the owner actually uses, or claims one it should not; make one description fix per observed misfire and rerun. Misfires that keep coming back after those fixes → hand the skill to **skill-creator** for its description optimisation.
- Fired, but a logged correction came back → the rule is weak or buried; sharpen or move it up.
- Stated something the input does not support → a fact leaked or a lookup rule is missing.

Record the input, the full output, and the verdict in `06_check.md`.
