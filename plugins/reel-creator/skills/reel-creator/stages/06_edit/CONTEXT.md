# 06_edit: build it in CapCut

One job: write the spec from script + footage + music map and build it into a CapCut project.

## Inputs
- Working: `{run}/03_script.md`
- Working: `{run}/04_footage.md`
- Working: `{run}/05_music.md`
- Reference: `../../references/editing.md`
- Reference: `../../references/sound-design.md`
- Reference: `../../references/capcut.md`
- Project: `{project}/references/brand.md` (caption style project, colours, SFX folder)

Do NOT load: story, idea or shooting references; past runs.

## Process
1. Passes in order (`editing.md`): rough cut → music map → sound → motion → text → colour notes.
2. Write `{run}/06_spec.py` from `templates/run/06_spec.py` (format: the `tools/build_reel.py` docstring); every cut time from the grid.
3. Create/close the CapCut project and build (`capcut.md`). If the owner edited a previous version,
   diff and carry their edits into the spec first.
4. Record the hand-finish items that apply in `{run}/06_edit.md`. No SFX folder yet → use the clips'
   own sound, and list the effects to record or license in `06_edit.md`.

## Outputs
- `{run}/06_spec.py`, `{run}/06_edit.md`, the CapCut project `<reel> v<N>`

## Check
`build_reel.py` exits 0 and the project opens and plays. Writes `{run}/06_check.md`.
Human check: none here; the owner reviews at 07.
