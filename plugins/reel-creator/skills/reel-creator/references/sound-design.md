# sound-design.md: the layer that makes cuts feel alive

Used by 06_edit (the sound pass). Flat edits usually have one sound layer: the music. Editors treat
sound as half the edit: a hit where the picture changes, a riser into the payoff, silence before it [S].

## Rules [S unless marked]
- **Hit on the exact cut frame.** At 30 fps a frame is 33 ms; 50 ms early already reads as sloppy. Use it on the payoff, a punch-in, a title landing.
- **Whoosh straddles the move**: start ~50 ms before the camera move or transition, peak mid-move, end when the new shot is settled (~0.4–0.5 s for a 0.5 s move).
- **Riser → hit**: a ~1.5 s riser that stops dead on the payoff cut, where the hit starts. Don't stack a riser on a song that already builds there.
- **Sparingly**: sound only section changes, punch-ins and the payoff; space effects ≥ 4 s. The same whoosh ten times becomes invisible.
- **Levels**: effects ≥ 6 dB under voice. Whooshes −18 to −24 dB, hits −12 to −18 dB. If you consciously notice a whoosh, it's too loud.
- **Diegetic sound is the best SFX** [O]: the needle buzz from the clip, a glove snap, the piercing clamp click, a camera shutter on a finished-photo cut. Record your own in the studio once and keep them in the project's sound folder.
- **Room tone** under any gap; a cut to digital silence sounds broken (except the deliberate pre-drop silence).

## The sound pass (in this order)
1. Payoff: hit on the cut, silence 0.3–0.6 s before it, riser into it only if the music doesn't build.
2. Section changes and punch-ins: one hit or whoosh each, if the motion has a direction.
3. Diegetic moments: bring the clip's own sound up (`Shot.volume` 0.6–1.0) for 0.5–1.5 s.
4. Speech: duck the music (volume keyframes, or split the music piece around the line).
5. Listen once on a phone speaker and once on headphones.

## In the spec (`capcut.md`)
`Audio(file, at=<cut time>, volume=0.3, track="sfx")` per effect, with `at` taken from the beat grid.
Snap SFX to cut times, not to guesses. CapCut's built-in SFX library can't be written from code:
use local files, or add library sounds by hand (only items marked for commercial use in ads).

## Sources of effects (check each item's licence before use)
Pixabay SFX (commercial use, no attribution) · Fiftysounds · Freesound **CC0 only** · Sonniss GDC
bundles · CapCut library items marked "Commercial use". Avoid BBC RemArc (non-commercial).
Detail and links: `toolbox.md`.
