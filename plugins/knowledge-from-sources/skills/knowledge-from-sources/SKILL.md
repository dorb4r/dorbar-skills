---
name: knowledge-from-sources
description: >-
  Turn a pile of sources (video transcripts, course lessons, interviews, papers, docs) into a
  linked, quote-checked knowledge bundle of source notes, concept notes and claims, then build
  from it: a skill, lecture, script or doc, or a gap review of an existing artifact. Covers
  collecting the sources too: YouTube transcripts with rate limiting, course pages through the
  browser, PDFs, provenance and rights, key video frames. Use when asked to turn transcripts
  into notes, learn from a course, build a research corpus, turn a YouTube channel into a
  knowledge base, extract lessons from videos, build a skill from source material, make a
  knowledge bundle, verify quotes, or turn a literature review into notes.
---

# Knowledge from sources

Turn sources into a **knowledge bundle**: every idea stated once, backed by the speaker's exact words, each quote checked by script against its source, every outside fact checked before it is said. Artifacts are then built from the bundle, never from the raw pile, so they say what the sources say and nothing they do not.

The bundle is an ICM workspace (folder structure as agent architecture): `AGENTS.md` only routes, every working folder has a `CONTEXT.md` contract with exactly one `## Check`, and nothing moves on until that check passes.

Adapted from icm-architect (MIT, (c) 2026 Jake Van Clief): bundle method, note templates and `quotes.py` / `index.py` / `links.py`.

## When to use
- A course, channel, interview set or reading list whose ideas will feed a skill, lecture, script or doc.
- The wording must stay the speaker's, or claims must be traceable to a timestamp or page.
- An existing artifact must be checked against what the sources actually say (gap review).

## When NOT to use
- One short source and one artifact: write an outline in chat.
- General web research toward a report: a research skill fits better.

## The bundle

```
<subject>/                   private: never inside a public repo
├─ AGENTS.md  CLAUDE.md      routing only (CLAUDE.md is the line @AGENTS.md)
├─ CONTEXT.md  plan.md       the plan's contract, and the plan
├─ .gitignore                raw/ and _meta/keep-out.txt
├─ raw/                      untouched sources + provenance; _sources.md, _files/, _frames/
├─ sources/                  one note per raw source: cite, rights, parts, gaps
├─ concepts/                 one idea per note, in the speaker's words
├─ claims/                   outside facts, how each was checked
├─ output/                   the built artifact; gap reviews
├─ _meta/                    schema.md, keep-out.txt, sources.txt (optional key aliases)
├─ _templates/  _tools/      blank notes; scripts
└─ _archive/                 never read
```

`raw/`, `sources/`, `concepts/`, `claims/`, `output/` and the root each get a contract copied from `templates/contexts/`. `_meta/`, `_templates/`, `_tools/` are factory and carry none.

## Steps

Stop after each step: a person reads its output before the next starts. Run commands from the bundle root.

**0. Frame.** Ask what will be built and for whom; who the speaker is and who the author is; the sources (URLs, files, a channel, a course); the rights for each (license, owner permission, none known); what must stay out (names, client details, embargoes); where the bundle will live. Size it with reference §1.
Done when: the owner has confirmed the artifact, the source list, the rights, and a private location.

**1. Scaffold.** In the chosen location copy from this skill: `templates/AGENTS.md`, `templates/CLAUDE.md`, `templates/gitignore` as `.gitignore`, `templates/contexts/root.md` as `CONTEXT.md`, `templates/plan.md`; each `templates/contexts/<folder>.md` as `<folder>/CONTEXT.md`; `templates/schema.md` and `templates/keep-out.txt` to `_meta/` (fill Rights and the keep-out list now); the note templates and `raw-header.md` to `_templates/`; `scripts/*.py` to `_tools/`.
Done when: `python -I _tools/raw_index.py`, `python -I _tools/quotes.py` and `python -I _tools/links.py` all pass on the empty bundle.

**2. Collect.** Follow `raw/CONTEXT.md` and reference §2: YouTube through `fetch_youtube_transcripts.py` (it stops on the first block; never push past it), course pages through the owner's browser session, PDFs as paged text, frames only where a transcript points at the screen. Provenance goes in each file's header as it is captured.
Done when: `raw_index.py` exits 0 and every source on the list has a row in `raw/_sources.md`, fetched or marked not fetched with the reason.

**3. Index.** One source note per raw file (`sources/CONTEXT.md`, reference §3): how to cite, rights and attribution, words to fix, gaps, what stays out. Parts tables wait for step 4.
Done when: every fetched source has a note with its rights line filled, and `links.py` passes.

**4. Plan.** Follow the root `CONTEXT.md` and reference §4: read every source whole, cluster the ideas by how the artifact will ask for them, write a stub for every concept and claim, fill the Parts tables, write `plan.md`.
Done when: the author has approved the cluster list (`concepts/_index.md`) and `plan.md`, and `links.py` passes.

**5. Extract.** Fill concept stubs in batches of about five (`concepts/CONTEXT.md`, reference §5), then claims (`claims/CONTEXT.md`) before the plan's best lines are final. Fix notes, never raw files.
Done when: no stub is left in any `_index.md`, and `quotes.py` and `links.py` pass after the last batch.

**6. Verify.** Run `python -I _tools/quotes.py --show-cuts` and read every cut and warning (reference §6). A reviewer reads three concept notes against their sources.
Done when: zero problems, every warning resolved or accepted in writing, and the reviewer says the three notes sound like the speaker and say what they meant.

**7. Synthesize.** Build what the plan names in `output/` (`output/CONTEXT.md`), reading only the plan and the concepts it names. Pick the route: a **skill** (reference §7), a **lecture, script or doc** (§8), or a **gap review** of an existing artifact: missing, conflicting, fine (§9).
Done when: the artifact or review exists, and the plan's `status:` reads `built` or `reviewed`.

**8. Check.** Run `python -I _tools/leaks.py`, `quotes.py` and `links.py` over the bundle and `output/`, then the walk test (reference §10).
Done when: every script passes, the walk test passes, and the author signs off on the output.

## Rights

- `raw/` is someone else's work. It stays private and out of every repo; `.gitignore` holds it out, and `git check-ignore raw` proves it.
- Unlicensed or unknown rights: what leaves `output/` paraphrases, attributes, and quotes only short cited lines. `leaks.py` fails on 12+ copied words.
- Licensed: follow the license. Owner permission: record who and when under `rights:`.
- Course platforms and paywalled pages are read through the owner's logged-in browser, never with their password.
- Every artifact ends with the attribution line from `_meta/schema.md`.

## Tools

| Script | Job |
|---|---|
| `fetch_youtube_transcripts.py` | transcripts to `raw/`: polite delay, resumable, stops on a block (needs `youtube-transcript-api`) |
| `raw_index.py` | writes `raw/_sources.md` from provenance headers; fails on missing provenance |
| `quotes.py` | every quote matches its source at its position; keep-out phrases stay out (vendored, adapted for `raw/`) |
| `links.py` | every link and contract input resolves (vendored) |
| `index.py` | writes each shelf's `_index.md` (vendored) |
| `leaks.py` | no long runs of source text in `output/` |

All are Python standard library except the fetcher; run with `python -I`.

## Reference

[reference.md](reference.md): sizing and roles, collecting by kind of source, the notes, extraction moves, what the checks catch and miss, the three output routes, the walk test, failure modes. Each step names its section.
