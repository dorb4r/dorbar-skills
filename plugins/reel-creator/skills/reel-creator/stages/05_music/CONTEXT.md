# 05_music: map the song onto the story

One job: choose the track and map the script beats onto its measured beat grid.

## Inputs
- Working: `{run}/03_script.md`
- Working: `{run}/04_footage.md`
- Reference: `../../references/music.md`
- Project: `{project}/references/brand.md` (music brief, licences)

Do NOT load: editing or CapCut references; past runs.

## Process
1. Speech-led format? Decide music yes/no first (`music.md`).
2. Propose 2–3 tracks matched to the emotion, with licence; the owner may supply one.
3. From the skill root: `uv run --project tools python tools/beatgrid.py <track> --until 60`; find the climax downbeat.
4. Write the map: BPM, climax time, in-point (climax − payoff time), sections to keep or cut, the
   pre-drop silence, and each script row's start snapped to the grid.

## Outputs
- `{run}/05_music.md`, the track in `{run}/audio/`

## Check
Human check: the owner approves the track (listens to the climax over the payoff shot).
