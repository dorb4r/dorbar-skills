# {Subject} - the plan: what gets built, from which ideas

One job: decide the artifact and the ideas it needs, before any concept is filled.

## Inputs
- Working (this run): every file in `raw/`, read whole; `sources/`
- Reference (every run): `_meta/schema.md`
- Reference (every run): `_templates/plan.md`

Do NOT load: `_archive/`; other bundles.

## Process
1. Read every source whole. List each distinct idea once, clustered by how the artifact will ask for it, not by where it appeared.
2. Write a stub for every planned concept and claim (frontmatter `status: stub`, a one-line description, the title as first heading).
3. Fill each source note's Parts table, linking the stubs.
4. Copy `_templates/plan.md` to `plan.md`: audience, one idea, spine, Open. Several artifacts: `plans/<slug>.md` each, plus `plans/map.md`.
5. Run `python -I _tools/index.py sources concepts claims` and `python -I _tools/links.py`.

## Outputs
- `plan.md`, stubs in `concepts/` and `claims/`, Parts tables in `sources/`

## Check
The author reads the cluster list (`concepts/_index.md`) and `plan.md` and approves, adds, merges or drops before any stub is filled.
