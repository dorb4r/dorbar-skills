# 04_footage: every row has real footage

One job: match each script row to a real clip, or produce the shoot plan for what's missing.

## Inputs
- Working: `{run}/03_script.md`
- Reference: `../../references/shooting.md`
- Reference: `../../references/shoot-card.md`
- Project: `{project}/references/brand.md` (footage catalog location, consent rules, banned material)

Do NOT load: music, editing references; past runs.

## Tools
- From the skill root: `uv run --project tools python tools/reel_breakdown.py <clip> <out>` (contact sheet + facts).

## Process
1. Search the project's footage catalog for each row; look at frames before claiming a match
   (contact sheet per clip). Note path, in-point, duration, faces, consent.
2. Copy the picked clips into `{run}/raw/` (originals stay untouched).
3. Rows with no real footage → `{run}/04_shoot-card.md` from `shoot-card.md`, with the script's
   lines and questions on top. **Never fill a gap with unrelated footage.**
4. After a shoot: sort the new files (the project's sorting step), then repeat 1–2.

## Outputs
- `{run}/04_footage.md` (row → file, in-point, why it fits), `{run}/raw/`, `{run}/04_shoot-card.md` if needed

## Check
Writes `{run}/04_check.md`: `pass` when every row has a viewed clip; else `fail: <rows missing>`.
A fail with a shoot card is a **hold**: the run waits for the shoot, then this stage reruns. Never go to 05 on a fail.
Human check: the owner (and filmer) run the shoot when the card exists.
