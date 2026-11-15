#!/usr/bin/env python3
"""Check a system map's cards against the code they cite. Exit 1 if any card needs attention.

    python -I map_check.py [MAP] [--since REF]

MAP defaults to ./map. Run inside the mapped git repo. Standard library only.

A card is any .md under MAP/objects/ or MAP/processes/ except _index.md and CONTEXT.md.
Citations are backticked `path:line` or `path:start-end` (repo-root paths) in the body, plus
the `entity:` / `entry:` frontmatter path. For each card it reports:
  - status verified without a `verified: YYYY-MM-DD <sha>` line, or with no citations
  - a cited path that does not exist, or a cited line past the end of the file
  - a verified commit git does not know
  - re-verify: a cited path changed since the card's verified commit (or since --since REF,
    e.g. --since origin/main in a PR), committed or not
  - a card over 150 lines (split it)
"""
import re
import subprocess
import sys
from pathlib import Path

CITE = re.compile(r"`([^`\s:]+):(\d+)(?:-(\d+))?`")
VERIFIED = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+([0-9a-f]{7,40})\b")
NOT_CARDS = {"_index.md", "context.md"}
MAX_LINES = 150


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def front(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            meta = {}
            for line in text[3:end].splitlines():
                if ":" in line and not line.startswith(" "):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = re.split(r"\s+#", v.strip(), maxsplit=1)[0].strip()
            return meta, text[end + 4:]
    return {}, text


def main():
    args = sys.argv[1:]
    since = None
    if "--since" in args:
        i = args.index("--since")
        since = args[i + 1]
        del args[i:i + 2]
    mapdir = Path(args[0] if args else "map").resolve()
    top = git(mapdir, "rev-parse", "--show-toplevel")
    if top is None:
        sys.exit(f"{mapdir} is not inside a git repo")
    repo = Path(top.strip())
    changed_cache = {}

    def changed(ref):
        if ref not in changed_cache:
            out = git(repo, "diff", "--name-only", ref)  # ref vs working tree: includes uncommitted
            changed_cache[ref] = None if out is None else set(out.split())
        return changed_cache[ref]

    cards = sorted(f for shelf in ("objects", "processes") for f in (mapdir / shelf).rglob("*.md")
                   if f.name.lower() not in NOT_CARDS)
    problems = 0
    for card in cards:
        rel = card.relative_to(repo).as_posix()
        text = card.read_text(encoding="utf-8-sig", errors="replace")
        meta, body = front(text)
        status = meta.get("status", "")
        cites = [(m.group(1), int(m.group(3) or m.group(2))) for m in CITE.finditer(body)]
        paths = {p for p, _ in cites}
        for key in ("entity", "entry"):
            if meta.get(key) and "{" not in meta[key]:
                paths.add(meta[key].split(":")[0])
        notes = []
        if text.count("\n") > MAX_LINES:
            notes.append(f"{text.count(chr(10))} lines, over {MAX_LINES}: split it")
        v = VERIFIED.match(meta.get("verified", ""))
        if status == "verified" and not v:
            notes.append("status verified without `verified: YYYY-MM-DD <sha>`")
        if status == "verified" and not cites:
            notes.append("status verified with no `path:line` citations")
        for p, line in cites:
            f = repo / p
            if not f.is_file():
                notes.append(f"cites missing path `{p}`")
            elif line > len(f.read_text(encoding="utf-8", errors="replace").splitlines()):
                notes.append(f"cites `{p}:{line}` past end of file")
        ref = since or (v.group(2) if v else None)
        if ref and status != "stub":
            diff = changed(ref)
            if diff is None:
                notes.append(f"git does not know `{ref}`")
            else:
                for p in sorted(paths & diff):
                    notes.append(f"re-verify: `{p}` changed since {ref}")
        for n in dict.fromkeys(notes):
            print(f"{rel}: {n}")
        problems += bool(notes)
    print(f"{len(cards)} cards checked, {problems} need attention")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
