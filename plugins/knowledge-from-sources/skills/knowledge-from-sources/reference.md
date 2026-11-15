# knowledge-from-sources: reference

Detail behind the steps in [SKILL.md](SKILL.md). Each section is reached from one step; read the one you are on. Adapted in part from icm-architect's "Knowledge bundle from sources" (MIT, (c) 2026 Jake Van Clief).

## Contents

1. Size it and name the roles (step 0)
2. Collecting, by kind of source (step 2)
3. The notes (steps 3-5)
4. Reading and planning (step 4)
5. Extraction moves (step 5)
6. What the checks enforce, and what they cannot (step 6)
7. Route: sources to a skill (step 7)
8. Route: lecture, script, article, doc set (step 7)
9. Route: gap review (step 7)
10. Walk test (step 8)
11. Failure modes

## 1. Size it and name the roles

| Corpus | Build |
|---|---|
| one short source, one artifact | an outline in chat; no bundle |
| a short corpus whose wording must stay the speaker's | a light bundle: `raw/`, `sources/`, `concepts/`, `plan.md`; `claims/` only when a claim leans on an outside fact |
| long sources (tens of thousands of words), a whole channel or course, or several artifacts sharing ideas | the full tree |

**Speaker**: whoever's words are in the sources. **Author**: who builds the artifact and answers for it. When they differ, "in their words" means the speaker's, and every Open list splits in two: what only the speaker can supply, what only the author can decide. Ask who answers each check.

Frame questions, a few at a time: what will be built and for whom; whose words must survive; what must not be said (names, embargoes, client confidences); what a citation points at (a time, a page); where the bundle will live; what the rights are per source (a license, the owner's permission, or none known).

## 2. Collecting, by kind of source

Every source becomes one text file in `raw/`, named by its key, opening with the header in `_templates/raw-header.md`. Provenance is written at capture time, never reconstructed: `url`, `fetched`, `rights` are required and `raw_index.py` fails without them. Originals that are not text (PDF, video, audio) go in `raw/_files/`; frames in `raw/_frames/<key>/`. Never edit a raw file after capture; fixes go in the source note's "Words to fix".

**A YouTube channel or playlist.**
1. List it: `yt-dlp --flat-playlist --print "%(id)s|%(duration)s|%(title)s" "https://www.youtube.com/@{channel}/videos" > list.txt`. Trim the list to what the plan needs; shorts and trailers rarely carry ideas.
2. Fetch: `python -I _tools/fetch_youtube_transcripts.py list.txt --out raw --author "{author}" --rights "{rights}"`. Defaults: 20 s delay plus jitter, 25 fetches per run, 45 s paragraphs. It skips files that exist and videos logged as having no transcript, so rerunning continues where it stopped.
3. Rate limits: YouTube blocks an IP after roughly 30 quick requests (`IpBlocked` / `RequestBlocked`). The script stops with exit 2 on the first block; continuing only extends the block. Options, in order: wait several hours and rerun with `--delay 60`; or open each remaining video in the owner's logged-in browser, "...more" then "Show transcript", copy the panel, and write it as `[m:ss] text` paragraphs under the same header with `via: "browser transcript panel"`.
4. Auto-generated captions mishear names and terms. Record each in the source note's "Words to fix"; quotes keep the raw wording so they still match.

**A course platform (lessons behind a login).** Use the owner's browser session (Claude in Chrome or the in-app browser); never ask for their password. One lesson per file, key `<course>-<nn>-<slug>`, `kind: course-lesson`, `url` the lesson URL, `via: "browser page text"`. Lesson videos: take the platform's transcript or captions if it shows them, otherwise the YouTube copy if the lesson embeds one; with neither, note it in `_sources.md` as not fetched and ask the owner. Paywalled material is almost never licensed for reuse: set `rights: "unlicensed"` unless the owner says otherwise.

**A PDF or paper.** Keep the original in `raw/_files/`. Text with page markers, so `quotes.py` checks by page:
`pdftotext -layout raw/_files/x.pdf - | python3 -c "import sys; print('\n'.join(f'Page {i}\n{p}' for i, p in enumerate(sys.stdin.read().split('\f'), 1) if p.strip()))" >> raw/x.txt` (write the header first). Scanned PDFs need OCR first.

**A web page or doc.** Save the page text, not the HTML, with `kind: web-page`. Record the license shown on the page (docs are often CC-BY or MIT).

**An interview or recording.** Transcribe with timestamps (`[m:ss]` paragraphs); record the transcription model under `via`. Get the speaker's consent for the recording and its use, and write it under `rights`.

**Frames: only where the visual matters.** Scan transcripts for cues: "as you can see", "look at this", "on screen", "this slide", "this diagram", "let me show you", "click here". For each cue the artifact needs:
`yt-dlp --download-sections "*{start}-{end}" -f "bv*[height<=720]" -o "raw/_files/{key}-%(section_start)s.%(ext)s" "https://youtu.be/{key}"`, then
`ffmpeg -ss {offset} -i raw/_files/{clip} -frames:v 1 -q:v 2 raw/_frames/{key}/{m-ss}.jpg`.
Describe each frame in words in the source note's Visuals table: the description is what notes and artifacts use. Delete the clips once the frames exist.

Then run `python -I _tools/raw_index.py`. It writes `raw/_sources.md` and lists, as "not fetched", anything `_fetch-log.tsv` says failed.

## 3. The notes

Citations follow `_meta/schema.md`, the one home for the format: `"verbatim line" (key position)`.

- **Source** (`source.md`): how to cite it, its rights and attribution, its Parts, its Visuals, the words the transcription gets wrong with their fixes, **Gaps** (where it stops short or holds only one voice), and what stays out. Say what and where; the phrases themselves go in `_meta/keep-out.txt`.
- **Concept** (`concept.md`): the idea stated once, in two or three sentences, saying only what the quoted lines say. **In their words**: verbatim lines, each cited, trimmed to the clean part and never tidied. **Where it stops**: the speaker's own limits and hedges; the loud version of an idea is rarely all of it. **Note**: your reading, marked as a proposal; delete it if you have none. **Related**: other concepts and the plan.
- **Claim** (`claim.md`): one block per outside fact: the speaker's quote with its citation, what it leans on, how and when it was checked, a status word, and the safe line. The speaker's words never share a line with your verdict.
- **Plan** (`plan.md`): who it is for and what they arrive with, the one idea, what they leave able to do, the spine (concepts in order, each with why it is there and whether it gets the full treatment or a line), the speaker's best lines copied from the concepts, the real thing to show, the claims that apply, and **Open**, split between speaker and author. A plan holds a route, not the artifact. Several artifacts: `plans/<slug>.md` each (links become `../concepts/...`), plus `plans/map.md` with the ideas everything rests on, the artifacts in order with status, and the author's decisions; give `plans/` a `CONTEXT.md` adapted from this skill's `templates/contexts/root.md`.

One home per fact. A verifiable fact lives in `claims/`. A gap in a source lives in that source's note. A question only the speaker can answer lives in the plan's Open list. Concepts link to these; they do not repeat them.

## 4. Reading and planning

Read every source whole before writing a note; sampling gives a map of the opening. For a large corpus, fan out: one subagent per batch of sources, each returning a list of ideas with citations; you merge. List each distinct idea once, and cluster by how the artifact will ask for it, not by where it appeared. A course's lesson order is the author's teaching order, not necessarily the artifact's.

Write a stub for every planned note, concepts and claims alike, so links resolve from the first batch. Present the cluster list (`concepts/_index.md`) and `plan.md`. The author adds, merges, drops. Do not create shelves for types you will not use.

## 5. Extraction moves

- **Quotes are word for word, cited, and checked by script.** A quote `quotes.py` cannot find is a typo or an invention; either way it does not ship.
- **The speaker's words and yours never share a line.** Verbatim sits under "In their words". Your reading sits under "Note" and is a proposal.
- **One idea, one note.** The plan and other notes link; they do not copy.
- **Gaps are named, not filled.** Open lists name what only someone can supply. Where sources disagree, say so in the concept's "Where it stops" and ask; do not reconcile them. A later lesson that revises an earlier one is a disagreement with a date: cite both.
- **Private people are described by role, never named** (`_meta/schema.md`, Privacy). Names live only in the raw copies, and later agents read the notes, never the raw copies, so a name cannot travel.
- **Facts are checked before the plan's best lines, not after the artifact.** With search, verify against a primary source; a search summary is a lead. Without search, write what would settle it and where to look.

## 6. What the checks enforce, and what they cannot

`quotes.py` fails on a quote not found near its cited position or on its cited page; a citation with no timestamp or page; an unknown source key; a bullet under "In their words" with no cited quote; a cut that drops a negation or leaves a piece too short to verify; and a keep-out phrase anywhere outside `raw/` and `_meta/`. It warns on a quote found in a neighboring paragraph and on eight or more quoted words with no citation. `links.py` fails on any link or input path that does not resolve. `raw_index.py` fails on a source with no url, fetched date or rights. `leaks.py` fails on any run of 12 or more words copied from a raw source.

A script can prove a quote is in the source. It cannot prove a paraphrase is fair, or that a synonym of a kept-out phrase is absent: that is what the reviewer's three notes are for. Read every `--show-cuts` line: a cut can change a meaning without dropping a negation.

## 7. Route: sources to a skill

The route this skill was born from: a course author's lessons and videos turned into skills an agent runs.

1. In the plan, the artifact is a skill: **Arrives with** is the task an agent is handed; **Leaves able to** is the task done; the spine is the steps and rules, each linked to the concept it comes from.
2. Write the skill in `output/<skill-name>/` following the skill-writing guidance the owner uses (steps with checkable completion criteria, detail disclosed to a reference file). Each step is an instruction in your words, built from a concept's claim, not a quote; the speaker's best lines appear only where their exact wording is the instruction, quoted briefly and cited.
3. The description's triggers come from the plan's **Arrives with** and the words the audience uses, not the speaker's jargon.
4. End the skill with the attribution line from `_meta/schema.md`. Keep a `SOURCES.md` beside it (or a section in its reference) that maps each step to the concepts behind it, by concept title and source URL, not by raw file.
5. Check: `leaks.py output/<skill-name>` passes, `quotes.py` passes, and a cold agent given the skill and the plan's **Arrives with** task can follow it.

## 8. Route: lecture, script, article, doc set

The plan is the route; building the artifact is a pipeline's job. Its first stage reads one plan and the concepts that plan names, never the whole bundle. Open with orientation before the hook. Quote the speaker's best lines where the rights allow; attribute every one. A claim marked "not checked" is said as the speaker's account or not at all.

## 9. Route: gap review

Compare an existing artifact (a skill, doc, course outline) against the bundle.

1. Copy the artifact into `output/review/` (or name its path and version in the review).
2. Copy `_templates/gap-review.md` to `output/gap-review-<artifact>.md`.
3. For every concept in the plan's scope: **Missing** (the bundle has it, the artifact does not), **Conflicting** (the artifact says otherwise: give both, the source side cited), **Fine** (covered and consistent). Then **Not in the sources**: what the artifact asserts that no source supports.
4. Done when every concept in scope sits in exactly one list. The author decides each fix; the review proposes, it does not edit the artifact.

## 10. Walk test

A cold agent, no memory of the sources:

1. Open `AGENTS.md`. Can it say what artifacts exist and where to start?
2. Open `plan.md`. Can it list the spine and the speaker's best lines without opening a raw source?
3. Do `quotes.py`, `links.py` and `raw_index.py` pass, with no stub in any `_index.md`?
4. Open one concept. Does the unmarked paragraph say only what the quoted lines say?
5. Does the plan answer an Open item itself?
6. Does the plan plus the concepts it names stay under about 8,000 tokens?
7. Does `leaks.py` pass over everything meant for others, and does `git check-ignore raw` confirm `raw/` stays out of the repo?

If a step fails, split or move files. Do not add a "how to read this bundle" note.

## 11. Failure modes

- Summarizing a source instead of splitting it into ideas: the bundle becomes a second transcript.
- Quotes tidied "for readability," so they stop matching.
- Provenance written after the fact, or a source with no rights line.
- Hammering YouTube after the first block.
- Frames pulled for every video instead of where the transcript points at the screen.
- The same idea restated per artifact. One home.
- A plan that contains the script, or a skill that is a transcript with headings.
- Only the loud version of an idea: no "Where it stops."
- Smoothing over a disagreement between sources instead of asking.
- Private names, client details or embargoed lines in notes.
- Raw text, or long verbatim passages, in a public repo.
- Trusting the scripts for what they cannot see: whether a paraphrase is fair.
- A hand-edited `_index.md` or `_sources.md`.
