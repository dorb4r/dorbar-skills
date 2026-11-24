# 07_review: score it cold, then the owner

One job: a fresh reviewer scores the build; the owner watches it; notes go back into the spec.

## Inputs
- Working: `{run}/03_script.md`
- Working: `{run}/05_music.md`
- Working: `{run}/06_edit.md`
- Reference: `../../references/review.md`
- Project: `{project}/references/brand.md` (forbidden material, consent)

Do NOT load: the writer's notes from 02; past runs.

## Process
1. Spawn a reviewer sub-agent with only these inputs and the measured facts (`review.md` → Measure).
2. It writes `{run}/07_review.md`: rubric scores with time codes, failed checks, top 3 fixes.
3. Fix what's objective (timing, safe zones, gaps) with a rebuild at 06, then show the owner.
4. The owner's notes → `{run}/07_owner.md` → back to 06. Loop until the owner approves.
5. Export and publishing only on the owner's explicit request.

## Outputs
- `{run}/07_review.md`, `{run}/07_owner.md`

## Check
First line of `07_review.md` is `pass` (rubric ≥ 11/14, no zero on 1–3) before the owner sees it.
Human check: the owner approves the cut in CapCut.
