#!/usr/bin/env python3
# From icm-architect (MIT, (c) 2026 Jake Van Clief) - https://github.com/RinDig/icm-architect - see LICENSE-icm-architect
# Adapted for layered-context: Inputs headings match by prefix, #section is stripped, a "Do NOT load"
# bullet is skipped, every input outside runs/ must exist, and ROOT defaults to the current directory.
# Inputs tokens: backticks pair left to right, commands and git refs are not paths, and an input
# must resolve inside ROOT.
"""List every relative link and input path that does not resolve. Exit 1 if there are any.

Run through context_guards.py or the context-guards action, or directly:
    python3 -I links.py [ROOT] [--skip FOLDER ...] [--graph FILE]
ROOT defaults to the current directory. Standard library only.

Checks every .md file outside dot-folders, node_modules/, _archive/, _templates/, raw/ and any
folder named with --skip:
  - markdown links [text](path), .md paths in consumes: / produces: frontmatter, and import
    lines such as @AGENTS.md (the one-line pointers CLAUDE.md and GEMINI.md hold).
    Web links, #anchors, {placeholders} and [[wikilinks]] are not checked.
  - backticked paths in list items under an Inputs heading, relative to the file or to ROOT.
    Every input must exist, except one under runs/, which passes if its folder exists, since
    this run's output may not be made yet. A token counts as a path only when it has no spaces or
    template marks and has a file extension or a first folder that exists (`go test`, `origin/main`
    and a lone `/` are skipped); a path that resolves outside ROOT is broken.

Inputs format (the one both this script and context_budget.py parse): a heading whose text starts
with "Inputs", then a bulleted list (- or *) of backticked paths. A path may end in #section
(`references/decisions.md#Database`); the section is stripped before resolving. A bullet that
starts with "Do NOT load" is skipped.
Fenced code blocks are skipped.

--graph FILE also writes the graph it walked, one JSON object per line: first the root (relative
to FILE), then each file (path, type, title, description, tags) and each link between .md files.
icm-architect's viz.py draws it (not included here).
"""
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKIP = {"node_modules", "_archive", "_templates", "raw"}
LINK = re.compile(r"\[[^\]]*\]\((<[^>]+>|[^)\s]+)\)")
TICK = re.compile(r"`([^`]+)`")  # pairs backticks left to right; non-paths are filtered later
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK_KEYS = re.compile(r"^(?:consumes|produces):\s*(.+)$", re.M)
IMPORT = re.compile(r"^@(\S+\.md)\s*$")


def front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def field(front, name):
    m = re.search(rf"^{name}:\s*(.+)$", front, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if v[:1] not in "\"'":
        v = re.split(r"\s+#", v, maxsplit=1)[0]  # drop a YAML comment
    if len(v) > 1 and v[0] == v[-1] == '"':
        try:
            return json.loads(v)  # YAML double quotes allow \u escapes
        except ValueError:
            return v[1:-1]
    return v[1:-1] if len(v) > 1 and v[0] == v[-1] == "'" else v


def lines_outside_fences(body):
    fence = None
    for line in body.splitlines():
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            mark = s[:3]
            fence = None if fence == mark else (fence or mark)
            continue
        if fence is None:
            yield line


def looks_like_path(s, bases):
    """True when a backticked Inputs token names a repo path, not a command, a git ref or a URL.
    Kept in step with looks_like_path in context_budget.py."""
    if not s.strip("/.") or any(c.isspace() for c in s) or any(c in s for c in "{}<>*?|$"):
        return False
    if re.match(r"^[a-z][a-z0-9+.-]*:", s, re.I):  # web link, scheme or drive letter
        return False
    if re.search(r"\.\w{1,5}$", s.rstrip("/")) or s.startswith("/"):
        return True  # has an extension, or is absolute (reported as outside the repo)
    first = s.split("/", 1)[0]
    return "/" in s and any((b / first).exists() for b in bases)


def inside(p, root):
    return p != root and p.is_relative_to(root)


def main():
    args, skip, graph_out = sys.argv[1:], set(SKIP), None
    while "--skip" in args:
        i = args.index("--skip")
        skip.add(args[i + 1])
        del args[i:i + 2]
    if "--graph" in args:
        i = args.index("--graph")
        graph_out = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    root = Path(args[0]).resolve() if args else Path.cwd()

    files = sorted(f for f in root.rglob("*.md")
                   if not any(p.startswith(".") or p in skip for p in f.relative_to(root).parts[:-1]))
    broken, nodes, edges, checked = [], [], [], 0

    def link(f, rel, target):
        nonlocal checked
        if re.match(r"^[a-z]+:", target) or target.startswith("#") or "{" in target:
            return  # web link, anchor, or a template's {placeholder}
        checked += 1
        path = (f.parent / urllib.parse.unquote(target.split("#")[0])).resolve()
        if not path.exists():
            broken.append(f"{rel}: {target}")
        elif path.suffix == ".md" and path != f.resolve():
            try:
                edges.append((rel, Path(os.path.relpath(path, root)).as_posix()))
            except ValueError:  # another drive
                pass

    for f in files:
        rel = f.relative_to(root).as_posix()
        front, body = front_matter(f.read_text(encoding="utf-8-sig", errors="replace"))
        for m in LINK_KEYS.finditer(front):
            for target in re.findall(r"[^\s\[\],\"']+\.md\b", m.group(1)):
                link(f, rel, target)
        title = field(front, "title")
        in_inputs = False
        for line in lines_outside_fences(body):
            h = HEADING.match(line)
            if h:
                in_inputs = h.group(2).strip().lower().startswith("inputs")
                title = title or (h.group(2) if h.group(1) == "#" else "")
                continue
            imp = IMPORT.match(line.strip())
            if imp and not re.match(r"^(~|/|[A-Za-z]:)", imp.group(1)):  # home or absolute paths aren't the tree's
                link(f, rel, imp.group(1))
            for m in LINK.finditer(line):
                link(f, rel, m.group(1)[1:-1] if m.group(1).startswith("<") else m.group(1))
            if (in_inputs and re.match(r"\s*[-*]\s", line)
                    and not line.lower().lstrip("-* ").startswith("do not load")):
                for m in TICK.finditer(line):
                    p = m.group(1).split("#", 1)[0]
                    if not looks_like_path(p, (f.parent, root)):
                        continue
                    strict = not p.startswith("runs/")  # a run's output may not be made yet
                    checked += 1
                    hits = [h for h in ((f.parent / p).resolve(), (root / p).resolve()) if inside(h, root)]
                    if not any(h.exists() or (not strict and h.parent.is_dir()) for h in hits):
                        broken.append(f"{rel}: input `{p}`")
        nodes.append({"node": rel, "type": field(front, "type"), "title": title or f.stem,
                      "description": field(front, "description"), "tags": field(front, "tags")})

    if graph_out:
        try:
            where = Path(os.path.relpath(root, graph_out.parent)).as_posix()
        except ValueError:  # another drive
            where = root.as_posix()
        with graph_out.open("w", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps({"root": where}) + "\n")
            for n in nodes:
                out.write(json.dumps(n, ensure_ascii=False) + "\n")
            for a, b in dict.fromkeys(edges):
                out.write(json.dumps({"edge": [a, b]}, ensure_ascii=False) + "\n")

    for b in broken:
        print(b)
    print(f"{len(files)} files, {checked} links and inputs checked, {len(broken)} broken")
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
