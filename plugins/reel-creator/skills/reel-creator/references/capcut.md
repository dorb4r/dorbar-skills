# capcut.md: building the edit into CapCut desktop (macOS) from a spec

Used by 06_edit. The edit lives in a CapCut project the owner can open and fix by hand. Every build
is code (`tools/build_reel.py`); the screen is driven only to close and reopen projects.

## The build
1. In CapCut: **Create project**, rename it (top title) to `<reel> v<N>`, then CapCut menu → **Back to home page**. CapCut ignores project folders it didn't create. The folder name may stay the old auto name until the home page refreshes: check `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`.
2. Write `06_spec.py` in the run (format: the docstring of `tools/build_reel.py`): `SHOTS`, `CAPTIONS`, `MUSIC` or `AUDIO` sections, SFX `Audio(track="sfx")`, `STYLE_FROM` (the project's approved caption style).
3. **Before rebuilding a project the owner may have edited**, diff its `draft_info.json` against the last spec and carry their changes into the spec. Never overwrite hand edits silently.
4. from the skill root: `uv run --project tools python tools/build_reel.py {run}/06_spec.py "<project folder name>"` (the folder under `com.lveditor.draft/`). It refuses if the project is open (`.locked`). It backs up the project first (`$REEL_BACKUP_DIR`).
5. Reopen the project from the home page. Play it once with sound.

**Never quit CapCut** (the owner reviews there). Close a project only with menu → Back to home page.

## What the spec can write (pyCapCut 0.0.4, pinned) [S: library source]
Shots with in-points, fill/fit + blur background, zoom/punch-in, reframe x/y, push-in keyframes, constant speed (a ramp = stepped speeds over consecutive shots), clip volume, dissolves · captions with the approved style and one **emphasis** word in an accent colour · music in one piece or rebuilt from sections · SFX and voice-over on their own tracks with fades.
The library also supports (not yet wired into the builder): volume keyframes (ducking), transitions (1,137; 152 free), scene effects (shake, flash, grain), filters, static masks, blend modes (Screen), clip and text in/out/loop animations. Add one to the builder when a script needs it, test once, then document it here.

## What only a person can do in CapCut (the hand-finish list)
- **Speed curves** (Speed → Curve → Custom, Smooth slow-mo) where the spec steps speeds.
- Freeze frames, reverse, animated mask wipes, eased keyframes.
- Colour: one adjustment layer over everything (HSL, curves), light grain.
- Play every animated RTL caption once: per-letter animations can run left-to-right.
- CapCut library sounds and effects (Pro assets watermark or block export on a free plan).
The build prints this list; the run's `06_edit.md` records which items apply to this reel.

## Known traps
- iPhone HLG clips need HDR mode 4 (the builder sets it); SDR mode 1.
- CapCut rounds in-points to frames (30 fps): ±1 frame is fine.
- Captions copy the first text of `STYLE_FROM`: keep that project unchanged.
- `AudioMaterial` rejects files with a video track: extract audio for J/L cuts, or use the clip's own volume.
- CapCut updates can change the draft format: if a build stops opening, check the CapCut version against pyCapCut first.

## Export (only when the owner asks)
Export → 1080p, bitrate Higher, H.264, mp4, 30 fps. Drafts are reviewed inside CapCut, not exported.
