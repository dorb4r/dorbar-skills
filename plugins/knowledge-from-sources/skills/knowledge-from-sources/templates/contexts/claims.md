# claims - outside facts, checked before they are said

One job: for every number or general fact a concept leans on, record how it was checked and the safe line.

## Inputs
- Working (this run): `../concepts/` (the lines that lean on outside facts)
- Reference (every run): `../_meta/schema.md`
- Reference (every run): `../_templates/claim.md`

Do NOT load: `../raw/` beyond the cited passage.

## Process
1. One block per claim: the speaker's quote, cited; what it leans on; how and when it was checked; a status word; the safe version.
2. With search: verify against a primary source. A search summary is a lead, not a source. Without search: write what would settle it and where to look.
3. Unverified stays "not checked", dated, and out of the plan's best lines.
4. Run `python -I _tools/quotes.py` and `python -I _tools/index.py claims`.

## Outputs
- `<slug>.md` per group of claims, `_index.md` (generated)

## Check
Every claim block has a status word and a safe version, and `quotes.py` passes.
