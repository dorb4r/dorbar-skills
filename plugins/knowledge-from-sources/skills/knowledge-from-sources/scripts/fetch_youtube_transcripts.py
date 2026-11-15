#!/usr/bin/env python3
"""Fetch YouTube transcripts into raw/, one timed file per video, politely and resumably.

    python -I _tools/fetch_youtube_transcripts.py LIST [--out raw] [--delay 20] [--max 25]
        [--lang en] [--para 45] [--rights "unknown"] [--author NAME] [--retry]

LIST has one video per line: a URL, a bare id, or  id|duration|title  as printed by
    yt-dlp --flat-playlist --print "%(id)s|%(duration)s|%(title)s" "<channel or playlist URL>"
Blank lines and lines starting with # are skipped.

Each video becomes  <out>/<id>.md : YAML provenance (title, url, kind, author, duration,
fetched, via, rights), the title as the first heading, then paragraphs that open with [m:ss]
or [h:mm:ss], the shape _tools/quotes.py checks quotes against. A paragraph closes once it
spans --para seconds.

Resumable: a video whose file exists is skipped, and so is one logged in <out>/_fetch-log.tsv as
having no transcript (unless --retry). Files are written whole or not at all. Between requests
it waits --delay seconds plus up to 5 s of jitter, and stops after --max fetches per run.
YouTube blocks an IP after roughly 30 quick requests: on a block (IpBlocked, RequestBlocked,
TooManyRequests) the script stops at once with exit code 2. Wait hours, raise --delay, or take
the rest from the transcript panel in a logged-in browser.

Needs youtube-transcript-api (pip install youtube-transcript-api); otherwise standard library.
Exit 0 when the run finished, 1 on bad input, 2 when YouTube blocked it.
"""
import argparse
import datetime
import json
import os
import random
import re
import sys
import time
from pathlib import Path

BLOCKED = {"IpBlocked", "RequestBlocked", "TooManyRequests", "YouTubeRequestFailed"}
NO_TRANSCRIPT = {"TranscriptsDisabled", "NoTranscriptFound", "NoTranscriptAvailable",
                 "VideoUnavailable", "VideoUnplayable", "AgeRestricted", "InvalidVideoId"}
ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
URL_ID = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([A-Za-z0-9_-]{11})")


def parse_line(line):
    """Return (video_id, duration, title) or None for a line of LIST."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    head, *rest = line.split("|")
    head = head.strip()
    m = URL_ID.search(head)
    vid = m.group(1) if m else head
    if not ID.match(vid):
        return None
    duration = rest[0].strip() if rest else ""
    title = "|".join(rest[1:]).strip() if len(rest) > 1 else ""
    return vid, duration, title


def stamp(seconds):
    s = int(seconds)
    h, m, s = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fetch(vid, langs):
    """Return (snippets as [(start, text)], via) using whichever API version is installed."""
    from youtube_transcript_api import YouTubeTranscriptApi as Api
    if hasattr(Api, "fetch"):  # 1.0 and later
        t = Api().fetch(vid, languages=langs)
        kind = "auto-generated" if getattr(t, "is_generated", False) else "manual"
        lang = getattr(t, "language_code", "?")
        return [(s.start, s.text) for s in t.snippets], f"youtube-transcript-api ({kind}, {lang})"
    rows = Api.get_transcript(vid, languages=langs)  # before 1.0
    return [(r["start"], r["text"]) for r in rows], "youtube-transcript-api"


def paragraphs(snippets, span):
    out, buf, start = [], [], 0.0
    for begin, text in snippets:
        text = " ".join(text.split())
        if not text:
            continue
        if not buf:
            start = begin
        buf.append(text)
        if begin - start >= span:
            out.append(f"[{stamp(start)}] " + " ".join(buf))
            buf = []
    if buf:
        out.append(f"[{stamp(start)}] " + " ".join(buf))
    return out


def write_whole(path, text):
    tmp = path.with_name(path.name + ".part")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("list")
    ap.add_argument("--out", default="raw")
    ap.add_argument("--delay", type=float, default=20.0)
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--lang", default="en", help="comma-separated language preference")
    ap.add_argument("--para", type=float, default=45.0)
    ap.add_argument("--rights", default="unknown")
    ap.add_argument("--author", default="")
    ap.add_argument("--retry", action="store_true", help="retry videos logged as having no transcript")
    a = ap.parse_args()

    try:
        import youtube_transcript_api  # noqa: F401
    except ImportError:
        sys.exit("needs youtube-transcript-api: pip install youtube-transcript-api")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    log = out / "_fetch-log.tsv"
    logged = {}
    if log.exists():
        for row in log.read_text(encoding="utf-8").splitlines():
            parts = row.split("\t")
            if len(parts) >= 3:
                logged[parts[0]] = parts[2]
    entries = [e for e in (parse_line(x) for x in Path(a.list).read_text(encoding="utf-8").splitlines()) if e]
    if not entries:
        print(f"no video ids in {a.list}", file=sys.stderr)
        sys.exit(1)

    today = datetime.date.today().isoformat()
    langs = [x.strip() for x in a.lang.split(",") if x.strip()]
    done = skipped = failed = 0
    for vid, duration, title in entries:
        path = out / f"{vid}.md"
        if path.exists() or (logged.get(vid) == "no-transcript" and not a.retry):
            skipped += 1
            continue
        if done + failed >= a.max:
            print(f"stopped at --max {a.max}; run again to continue")
            break
        if done + failed:
            time.sleep(a.delay + random.uniform(0, 5))
        try:
            snippets, via = fetch(vid, langs)
        except Exception as e:  # the library's own exception classes vary by version
            name = type(e).__name__
            with log.open("a", encoding="utf-8") as f:
                status = "blocked" if name in BLOCKED else "no-transcript" if name in NO_TRANSCRIPT else "error"
                f.write(f"{vid}\t{today}\t{status}\t{name}\n")
            if name in BLOCKED:
                print(f"blocked by YouTube at {vid} ({name}) after {done} fetched. Wait several hours, "
                      "raise --delay, or copy the rest from the transcript panel in a logged-in browser.",
                      file=sys.stderr)
                sys.exit(2)
            failed += 1
            print(f"FAIL {vid} {name}", file=sys.stderr)
            continue
        front = {
            "title": title or vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "kind": "youtube-transcript",
            "author": a.author,
            "duration": f"{duration}s" if duration.replace(".", "").isdigit() else duration,
            "fetched": today,
            "via": via,
            "rights": a.rights,
        }
        head = "---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in front.items()) + "---\n"
        write_whole(path, head + f"\n# {title or vid}\n\n" + "\n\n".join(paragraphs(snippets, a.para)) + "\n")
        done += 1
        print(f"ok {vid} {title[:60]}")
    print(f"fetched {done}, skipped {skipped}, failed {failed}")


if __name__ == "__main__":
    main()
