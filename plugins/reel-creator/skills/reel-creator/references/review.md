# review.md: the review before the owner sees it

Used by 07_review. A reviewer sub-agent that did not write the reel scores it cold, then the owner
watches it in CapCut. The reviewer gets the script, the music map and the measured facts, not the
writer's reasoning.

## Measure first
Export a preview only if the owner allows draft exports; otherwise review inside CapCut and measure
the final export. On an export: `uv run --project tools python tools/reel_breakdown.py <file.mp4> <run>/07_facts`
→ `shots.jpg` (a frame per shot), `audio.png` (loudness, onsets, cuts vs beats), `facts.md`
(shot lengths, cut offsets from the beat, hits on cuts, speech share).

## Soul rubric (each 0–2; ship at ≥ 11 of 14, no zero on 1–3)
1. **Sender**: a specific person would send it to a specific friend.
2. **Turn**: there is a "but" (stakes, conflict, a twist), not "and then".
3. **Face or voice**: a person with a voice carries it; the emotion lands on a face.
4. **Specific**: one concrete human detail (an exact line, a real object, a number).
5. **Peak**: one clear peak, placed on the musical climax or a silence → hit.
6. **Ending**: fast, and it means something (a line, a look, a loop), not only a logo.
7. **Ours**: only this artist/studio could post it; the format differs from the last post.

## Craft checks (pass/fail)
- Frame 1 moves or speaks; the promise reads on mute in ≤ 1.5 s.
- A visual change every 1.5–3 s, or a held shot that changes inside.
- Cuts on the beat where the script says so (facts: offsets within ±60 ms) and none of the payoff cuts late.
- Sound: hits on the money moments, no gap to digital silence except the planned pre-drop silence, music ducked under speech, no chatter leaking.
- Text: ≤ 6 words in the hook card; reading time met; inside safe zones; never over the work or a face; RTL renders right.
- Length matches the format; the ending loops or lands.
- Truth: real order, real words, consent for every identifiable person, no forbidden material (the project's `references/brand.md`).

## Output
`07_review.md`: the rubric scores with one line of evidence each (a time code), the failed checks,
and the 3 changes that would raise the score most. First line `pass` or `fail: <why>`.

## Owner check
The owner watches in CapCut with sound, then on mute. Their notes go into the run as `07_owner.md`
and drive the next build. Publishing or scheduling happens only on the owner's explicit OK.
