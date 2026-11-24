# music.md: choose the song, map it, cut it to the edit

Used by 05_music. "The best music with the best moments" = map the song first, then put the best
moment on the strongest musical moment, and cut the song to the story, not the story to the song.

## Choosing
- Mood first, genre second, tempo last. Name the target emotion from the brief and match it [S].
- Mismatch test: play the track over the payoff shot alone. If the music says something the work doesn't, reject it.
- Avoid corporate-upbeat, ukulele-and-claps, generic EDM builds under calm work [O].
- Speech-led formats (skits, mini-docs) often need **no music** or a low bed: the voice is the soundtrack.
- Licensing: the platform's library or a licensed source (`toolbox.md`). Organic posts may use the app's library; ads need commercial-use tracks.

## Mapping (always measured, never by ear)
1. `uv run --project tools python tools/beatgrid.py <track> --until 60` → exact BPM, beat phase, kick/loudness per beat, bar starts.
2. Mark: intro, build, **climax** (the phrase downbeat where kick + loudness jump; not the riser before it), outro. Phrases are 4 or 8 bars.
3. Write the map into the run (`05_music.md`): times in the song, and where each lands on the timeline.
4. A timecode someone hears ("the drop at 05:20") is ~0.2 s late (reaction time): snap it to the measured downbeat and say so.

## Placing it
- Music in-point = climax_in_song − payoff_time_on_timeline. Then every beat lands on a multiple of the beat period on the timeline; put cuts on those multiples.
- The payoff lands on the climax; the hook on the most interesting 2 s of the song (rarely bar 1).
- Grid by section: setup on bar lines, build on every 2nd beat tightening to every beat, climax: cut then hold.
- A cut 1–2 frames *before* the beat feels on time; never > 2 frames after [S].
- Don't cut on every beat: a visual system (anchor wide, blank/art swap, flip) earns fast cutting; plain footage doesn't.

## Cutting the song to the edit
- Rebuild the song from sections with `Audio(track="music")` pieces: short intro → build → climax on the payoff → a tail that ends on a beat or loops into bar 1 [O].
- Join sections on phrase starts, 20–50 ms crossfades. End on a phrase end or a stinger, never mid-bar; fade 0.5–1.5 s only if no clean ending exists [S].
- **Silence before the drop**: 0.3–0.6 s of no music right before the payoff makes it hit [S].

## Voice and natural sound with music
- Duck music 8–12 dB under speech; manual volume keyframes beat auto-ducking for short reels [S].
- The craft's own sound (needle buzz, a laugh, the shutter) at moments, 0.5–1.5 s, music dipped 6–10 dB [O].
- J-cut: the next shot's sound starts 0.2–0.5 s before its picture. L-cut: a laugh carries over the next shot [S]. Keep offsets ≤ 0.4 s.
- Never let shop chatter, the radio or other clients' voices leak in: mute raw audio by default, un-mute chosen moments.
- A person never talks under music unless it is meant as their voice-over.

## Check before 06_edit
`05_music.md` lists: track + licence, BPM, climax time in the song, in-point, the section plan, and where each script beat lands on the beat grid.
