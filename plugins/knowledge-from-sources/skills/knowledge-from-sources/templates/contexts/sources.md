# sources - one note per raw source

One job: say how to cite each source, what rights it carries, what is in it, and where it falls short.

## Inputs
- Working (this run): one file in `../raw/` at a time, whole
- Reference (every run): `../_meta/schema.md`
- Reference (every run): `../_templates/source.md`

Do NOT load: other raw files while writing one source's note.

## Process
1. Copy `_templates/source.md` to `sources/<key>.md`; fill citing, rights, attribution, words to fix, gaps, what stays out. Phrases to keep out go in `_meta/keep-out.txt`.
2. Leave the Parts table until the concept stubs exist (plan step), then fill it.
3. Run `python -I _tools/index.py sources`.

## Outputs
- `<key>.md` per raw source, `_index.md` (generated)

## Check
Every file listed in `raw/_sources.md` as fetched has a note here with its rights line filled, and `python -I _tools/links.py` passes.
