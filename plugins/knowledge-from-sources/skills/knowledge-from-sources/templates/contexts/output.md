# output - artifacts built from the bundle, and reviews of existing ones

One job: build the artifact the plan describes, or compare an existing artifact against the bundle.

## Inputs
- Working (this run): `../plan.md` and only the concepts and claims it names
- Working (gap review): the existing artifact, copied to `review/`
- Reference (every run): `../_meta/schema.md` (Rights)
- Reference (every run): `../_templates/gap-review.md`

Do NOT load: `../raw/`; concepts the plan does not name; `../_archive/`.

## Process
1. Build: follow the plan's spine. Write instructions and explanations in your own words; quote only short lines, cited, where the rights allow. End with the attribution line from `_meta/schema.md`.
2. Gap review: copy `_templates/gap-review.md` to `gap-review-<artifact>.md`; sort every concept in the plan into missing, conflicting or fine, each with the concept link and the artifact location.
3. Set the plan's `status:` to `built` or `reviewed`.

## Outputs
- the artifact (for a skill: `<skill-name>/SKILL.md` and its files), `gap-review-<artifact>.md`

## Check
`python -I _tools/quotes.py` and `python -I _tools/links.py` pass over `output/`, and the author reads the artifact (or the gap review) against the plan and signs off.
