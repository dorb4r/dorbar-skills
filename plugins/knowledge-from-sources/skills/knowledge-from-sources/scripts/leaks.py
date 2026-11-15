#!/usr/bin/env python3
"""Find runs of source text copied into an artifact: any stretch of N or more words that appears
word for word in a raw source. Exit 1 if there are any.

    python -I _tools/leaks.py [PATH ...] [--words 12] [--raw RAW]

PATH is a file or folder to scan (default: output/ beside the folder that holds _tools/); .md, .txt,
.html and .py files are read. RAW defaults to raw/ there. Text is compared lowercased, with
punctuation dropped, so a tidied copy still counts. Cited short quotes the rights allow pass if
they are under --words; a longer passage is the case this catches: someone else's text about to
leave the bundle. Run it before anything in output/ is published. Standard library only.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

READ = {".md", ".txt", ".html", ".py"}


def words(text):
    text = re.sub(r"^---.*?\n---", "", text, flags=re.S)  # provenance and frontmatter
    text = re.sub(r"\[\d+(?::\d+)+\]", " ", text)  # timestamps
    return re.sub(r"[^a-z0-9]+", " ", text.lower().replace("'", "").replace("’", "")).split()


def main():
    args, n, raw = sys.argv[1:], 12, None
    if "--words" in args:
        i = args.index("--words")
        n = int(args[i + 1])
        del args[i:i + 2]
    if "--raw" in args:
        i = args.index("--raw")
        raw = Path(args[i + 1])
        del args[i:i + 2]
    root = Path(__file__).resolve().parent.parent
    raw = raw or root / "raw"
    targets = [Path(a) for a in args] or [root / "output"]

    grams = {}
    for p in sorted(raw.glob("*")):
        if p.is_file() and p.suffix.lower() in {".md", ".txt"} and not p.name.startswith(("_", ".")) \
                and p.name.lower() != "context.md":
            w = words(p.read_text(encoding="utf-8-sig", errors="replace"))
            for i in range(len(w) - n + 1):
                grams.setdefault(" ".join(w[i:i + n]), p.stem)
    if not grams:
        sys.exit(f"no sources found in {raw}")

    files = []
    for t in targets:
        files += [t] if t.is_file() else sorted(f for f in t.rglob("*") if f.is_file() and f.suffix.lower() in READ)
    hits = 0
    for f in files:
        w = words(f.read_text(encoding="utf-8-sig", errors="replace"))
        i = 0
        while i <= len(w) - n:
            key = grams.get(" ".join(w[i:i + n]))
            if not key:
                i += 1
                continue
            j = i + n
            while j < len(w) and " ".join(w[j - n + 1:j + 1]) in grams:
                j += 1
            hits += 1
            print(f"{f.as_posix()}: {j - i} words from {key}: {' '.join(w[i:i + 14])}...")
            i = j
    print(f"{len(files)} files scanned against {raw.as_posix()}, {hits} run(s) of {n}+ words copied")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
