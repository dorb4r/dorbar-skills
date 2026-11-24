# study-a-reel.md: turning a reference reel into a reusable lesson

Used when the owner sends a reel to learn from. The lesson is the **mechanism**, never the content:
we don't copy anyone's idea, footage, music or words.

## Steps
1. **Permission**: downloading is a file download. Ask the owner once per batch (source, count, size, folder). Download only for private analysis into a folder outside any repo:
   `uvx yt-dlp -o "%(id)s.%(ext)s" --write-info-json <url>` (strip tracking parameters from the URL).
2. **Measure**: `uv run --project tools python tools/reel_breakdown.py <id>.mp4 <out>/<id>` →
   `shots.jpg`, `audio.png`, `facts.md`. Look at both images; the numbers alone mislead (a single
   take reads as "1 shot" but may be a full performance).
3. **Watch for**: what frame 1 shows · who is on screen and whether they speak · the premise text ·
   the turn · the peak and where it sits in the music · cut rate and whether cuts sit on beats ·
   the visual system (anchor, swap, flip) · sound beyond the music · how it ends · the post caption
   (it often holds the ask) · likes and comments vs the account's usual (from the info json).
4. **Write** `examples/<id>.md` with the template below (≤ 60 lines). No frames or media in the repo.
5. **Fold in**: a general mechanism → a row in `references/formats.md` and a line in
   `examples/README.md` (a PR in the skills repo). A lesson only for this project ("we need a filmer
   for this") → a belief line in `{project}/references/decisions.md`.

## Example template
```
# <id>: <format name> (<account>, <likes> likes)
Link: <url without tracking>   Studied: <YYYY-MM-DD>   Owner's note: <why they sent it>
## Facts
length · shots · median shot · BPM / pulse · cuts on beat · speech yes/no
## Beat by beat
| t | picture | text / speech | sound |
## Mechanism
2–4 lines: why it works (emotion, sender, turn, peak).
## Steal this
1–3 transferable moves, each with what our footage would need.
## Not for us
anything that clashes with the project's brand rules.
```
