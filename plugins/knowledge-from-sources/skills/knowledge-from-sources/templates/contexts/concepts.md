# concepts - one idea per note, in the speaker's words

One job: state each idea once, back it with cited verbatim lines, and say where it stops.

## Inputs
- Working (this run): the stubs in this folder; the cited passages in `../raw/`
- Reference (every run): `../_meta/schema.md`
- Reference (every run): `../_templates/concept.md`
- Reference (every run): `../plan.md`

Do NOT load: `../output/`; raw files no stub in this batch cites.

## Process
1. Fill stubs in batches of about five. The unmarked paragraph says only what the quoted lines say; your reading goes under Note.
2. Where sources disagree, say so under "Where it stops" and add it to the plan's Open list.
3. After every batch run `python -I _tools/quotes.py --show-cuts` and `python -I _tools/links.py`; fix the note, never the raw source.
4. Run `python -I _tools/index.py concepts`.

## Outputs
- `<slug>.md` per idea, `_index.md` (generated)

## Check
`quotes.py` and `links.py` pass with every warning read, no stub is left in `_index.md`, and a reviewer reading three notes says each sounds like the speaker and says what they meant.
