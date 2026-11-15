# Schema - the rules of this bundle

The closed set of note types, how quotes are cited, what the rights allow, and what may never appear. When practice and this file disagree, reconcile the same day.

types: source, concept, claim, plan

Add `ask`, `story` or `reading` to this list only when someone will query them.

## Note types

| `type:` | Lives at | Carries |
|---|---|---|
| source | `sources/<key>.md` | how to cite, rights, parts, visuals, errors and fixes, gaps, what stays out |
| concept | `concepts/<slug>.md` | one idea, the speaker's words, where it stops |
| claim | `claims/<slug>.md` | outside facts to verify, lines to rework |
| plan | `plan.md` (or `plans/<slug>.md` when there are several artifacts) | one artifact's route through the concepts |

Every note's first heading is its title. A planned note that is not written yet is a stub: its frontmatter (`status: stub`, a one-line description) and its title. Links to it resolve from the first batch, and `_index.md` shows it as a stub until it is filled.

## Citations

`"verbatim line" (key position)`. The key is the raw file's name without its extension, or a short name declared in `_meta/sources.txt` as `key = filename`. Position for a transcript is `m:ss` or `h:mm:ss` (or a range, `12:30-13:05`); cite the timestamp that opens the paragraph. Position for a document is a page (`page 2`, `pp 4-5`); a document with `Page 1`, `Page 2` lines is checked by page, and any other document is matched anywhere. Paraphrase takes no quote marks. To keep a name out of a quote, cut it with `...`; never swap a word inside the marks. `_tools/quotes.py` checks every quote.

## Rights

{Fill at the frame step. Per source the `rights:` line in its raw header is the one home; this section holds the rule for the bundle.}

- Where the bundle lives: {private folder or private repo}. `raw/` never enters a public repo; `.gitignore` holds it out.
- Unlicensed or unknown rights: notes may quote (they stay private); anything in `output/` meant for others paraphrases and attributes, and quotes only short lines, cited.
- Licensed: follow the license (attribution form, share-alike, non-commercial).
- Attribution line for outputs: {e.g. "Based on the lessons and videos of {author} ({URL})"}.

## Privacy

The speaker of a published source is named where attribution needs it. Everyone else (students, clients, interviewees, people named in passing) is described by role, never named, with neutral pronouns unless the source states them. Phrases that must never appear go in `_meta/keep-out.txt`, one per line; `_tools/quotes.py` fails on a whole-word hit anywhere outside `raw/` and `_meta/`, so list each form of a word. Keep that file out of anything that is published.

## Naming

Slugs are kebab-case. One idea per file, and the filename is the idea. A source note is named by its key. Each shelf has a `CONTEXT.md` (its contract, with one `## Check`) and an `_index.md` written by `_tools/index.py`. `_archive/` is never read.
