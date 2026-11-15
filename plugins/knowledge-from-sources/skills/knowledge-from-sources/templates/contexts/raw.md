# raw - collect sources untouched, with provenance

One job: hold each source exactly as captured, with where it came from and what the rights allow.

## Inputs
- Working (this run): the source list from the frame step (URLs, files, a channel or course)
- Reference (every run): `_meta/schema.md` (Rights)
- Reference (every run): `_templates/raw-header.md`

Do NOT load: concepts, claims or output; other bundles' raw folders.

## Process
1. One text file per source, named by its key (`<video-id>.md`, `<course>-<nn>-<slug>.md`, `<paper-slug>.txt`), opening with the provenance header from `_templates/raw-header.md`.
2. YouTube: run `python -I _tools/fetch_youtube_transcripts.py list.txt --out raw --author "{author}" --rights "{rights}"`. Exit 2 means blocked: wait, or copy the transcript panel from the logged-in browser into the same shape.
3. Course pages behind a login: read them through the owner's browser session, one lesson per file.
4. PDFs: the text goes here with a `Page N` line before each page; the original goes in `_files/`.
5. Frames only where a transcript says the screen matters: `_frames/<key>/<m-ss>.jpg`.
6. Run `python -I _tools/raw_index.py`.

## Outputs
- `<key>.md` or `<key>.txt` per source, `_sources.md` (generated), `_fetch-log.tsv`, `_files/`, `_frames/`

## Check
`python -I _tools/raw_index.py` exits 0, and every source on the list has a row in `_sources.md`, fetched or marked "not fetched" with the reason.
