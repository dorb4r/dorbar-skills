#!/usr/bin/env python3
"""Report context files that break their size budget, and stage loads that break the step budget.
Exit 1 if anything is over budget (or, with --provenance, if a belief line lacks provenance).

Shared, not copied: repos run it through the context-guards action or context_guards.py (see
the layered-context skill, reference.md -> Wiring the guards). Direct use:
    python3 -I context_budget.py [ROOT] [--provenance] [--json]
ROOT defaults to the current directory. Standard library only.

Budgets (tokens are estimated as characters / 4; override any of them in ROOT/.context-budget.json,
e.g. {"AGENTS.md": {"lines": 80}, "step_tokens": 10000}):
  AGENTS.md                  60 lines,   800 tokens   (entry file: routes only)
  CLAUDE.md, GEMINI.md        3 lines                  (one-line pointer to AGENTS.md)
  any CONTEXT.md             80 lines,   800 tokens   (router or stage contract)
  references/**/*.md        200 lines,  2000 tokens   (factory files)
  a contract's step load                8000 tokens   (AGENTS.md, or CLAUDE.md when there is no
                                                       AGENTS.md, + the CONTEXT.md + every backticked
                                                       path under its Inputs heading)
Skipped: dot-folders, node_modules/, _archive/, _templates/, runs/, raw/.

The step load is computed for every CONTEXT.md that has an Inputs heading (stage contracts and area
contracts such as backend/CONTEXT.md alike). Inputs format, shared with links.py: a heading whose
text starts with "Inputs", then a bulleted list of backticked paths; a path may end in #section
(stripped before resolving, the whole file counts); a bullet starting with "Do NOT load" is skipped.
A backticked token counts as a path only when it looks like one: no spaces or template marks, and
a file extension or a first folder that exists (so `go test`, `origin/main` and a lone `/` are
skipped). A path that resolves outside ROOT, or that does not exist (outside runs/), is a problem.

--provenance also checks belief files: references/decisions.md, references/decisions/**/*.md,
references/app-state.md and references/app-state/**/*.md (CONTEXT.md and README.md excluded;
override with "belief_globs" in .context-budget.json). Every top-level bullet must end with a
provenance note containing "since" and a date (YYYY-MM-DD), and no bullet may start with "Update:"
(stacked corrections - rewrite the original line instead). It fails when no belief file matches,
so a rename can't turn the check into a silent pass.
"""
import json
import re
import sys
from pathlib import Path

SKIP = {"node_modules", "_archive", "_templates", "runs", "raw"}
DEFAULTS = {
    "AGENTS.md": {"lines": 60, "tokens": 800},
    "pointer": {"lines": 3},
    "CONTEXT.md": {"lines": 80, "tokens": 800},
    "reference": {"lines": 200, "tokens": 2000},
    "step_tokens": 8000,
}
BELIEF_GLOBS = ["references/decisions.md", "references/decisions/**/*.md",
                "references/app-state.md", "references/app-state/**/*.md"]
NOT_BELIEFS = {"CONTEXT.md", "README.md"}
TICK = re.compile(r"`([^`]+)`")  # pairs backticks left to right; non-paths are filtered later
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def tokens(text):
    return len(text) // 4


def walk(root):
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part.startswith(".") or part in SKIP for part in rel.parts[:-1]):
            continue
        yield p, rel


def budget_for(rel, cfg):
    name = rel.name
    if rel.as_posix() == "AGENTS.md":
        return "AGENTS.md", cfg["AGENTS.md"]
    if rel.as_posix() in ("CLAUDE.md", "GEMINI.md"):
        return "pointer", cfg["pointer"]
    if name == "CONTEXT.md":
        return "CONTEXT.md", cfg["CONTEXT.md"]
    if rel.parts[0] == "references":
        return "reference", cfg["reference"]
    return None, None


def inputs_of(contract_text):
    """Backticked paths in list items under an '## Inputs' heading."""
    out, inside = [], False
    for line in contract_text.splitlines():
        if line.startswith("#"):
            inside = line.lstrip("#").strip().lower().startswith("inputs")
            continue
        if inside and line.lstrip().startswith(("-", "*")) and not line.lower().lstrip("-* ").startswith("do not load"):
            out += TICK.findall(line)
    return out


def has_inputs(contract_text):
    return any(line.startswith("#") and line.lstrip("#").strip().lower().startswith("inputs")
               for line in contract_text.splitlines())


def belief_files(root, globs):
    found = set()
    for g in globs:
        found.update(p for p in root.glob(g) if p.is_file() and p.name not in NOT_BELIEFS)
    return sorted(found)


def looks_like_path(s, bases):
    """True when a backticked Inputs token names a repo path, not a command, a git ref or a URL.
    Kept in step with looks_like_path in links.py."""
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


def resolve(path, contract, root):
    """Files an input loads, or None when it is missing or resolves outside ROOT."""
    for base in (contract.parent, root):
        p = (base / path).resolve()
        if not inside(p, root):
            continue
        try:
            if p.is_file():
                return [p]
            if p.is_dir():
                return [f for f in p.rglob("*.md") if f.is_file() and inside(f.resolve(), root)]
        except OSError:
            return None
    return None


def read(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    root = Path(args[0]).resolve() if args else Path.cwd()
    cfg = json.loads(json.dumps(DEFAULTS))
    override = root / ".context-budget.json"
    if override.is_file():
        for k, v in json.loads(override.read_text()).items():
            cfg[k] = {**cfg.get(k, {}), **v} if isinstance(v, dict) else v

    rows, problems, notes = [], [], []
    base = next((root / n for n in ("AGENTS.md", "CLAUDE.md") if (root / n).is_file()), None)
    base_tokens = tokens(read(base)) if base else 0

    for p, rel in walk(root):
        kind, b = budget_for(rel, cfg)
        if not kind:
            continue
        text = read(p)
        n_lines, n_tok = len(text.splitlines()), tokens(text)
        over = [f"{n_lines} lines > {b['lines']}" for _ in [0] if "lines" in b and n_lines > b["lines"]]
        over += [f"~{n_tok} tokens > {b['tokens']}" for _ in [0] if "tokens" in b and n_tok > b["tokens"]]
        rows.append((rel.as_posix(), kind, n_lines, n_tok, "; ".join(over) or "ok"))
        if over:
            problems.append(f"{rel}: {'; '.join(over)}")

        if kind == "CONTEXT.md" and has_inputs(text):
            load = base_tokens + n_tok
            for ref in inputs_of(text):
                path = ref.split("#", 1)[0]
                if not looks_like_path(path, (p.parent, root)):
                    continue
                files = resolve(path, p, root)
                if files is None:
                    if not path.startswith("runs/"):  # a run's output may not be made yet
                        problems.append(f"{rel}: input `{ref}` not found in the repo")
                    continue
                load += sum(tokens(read(f)) for f in files)
            status = "ok" if load <= cfg["step_tokens"] else f"step load ~{load} tokens > {cfg['step_tokens']}"
            rows.append((rel.parent.as_posix() + " (step load)", "step", None, load, status))
            if status != "ok":
                problems.append(f"{rel.parent}: {status} - split the contract, tighten Inputs, or point at a section")

    if "--provenance" in argv:
        files = belief_files(root, cfg.get("belief_globs", BELIEF_GLOBS))
        checked = 0
        if not files:
            problems.append("no belief files found (looked for " + ", ".join(cfg.get("belief_globs", BELIEF_GLOBS))
                            + ") - set belief_globs in .context-budget.json if they moved")
        for p in files:
            bf = p.relative_to(root).as_posix()
            for i, line in enumerate(read(p).splitlines(), 1):
                if not re.match(r"^[-*] ", line):
                    continue
                checked += 1
                body = line[2:].strip()
                if body.lower().startswith("update:"):
                    problems.append(f"{bf}:{i}: stacked 'Update:' line - rewrite the original belief in place")
                elif "since" not in body.lower() or not DATE.search(body):
                    problems.append(f"{bf}:{i}: belief without provenance (since YYYY-MM-DD, by <who>, ref <PR|commit>)")
        notes.append(f"provenance: {checked} belief line(s) checked in {len(files)} file(s)")

    if "--json" in argv:
        print(json.dumps({"rows": rows, "notes": notes, "problems": problems}, indent=1))
    else:
        w = max([len(r[0]) for r in rows] + [10])
        for path, kind, n_lines, n_tok, status in rows:
            print(f"{path:<{w}}  {kind:<10}  {'' if n_lines is None else n_lines:>5}  ~{n_tok:>6}  {status}")
        for note in notes:
            print(note)
        print(f"\n{len(problems)} problem(s)" + (":" if problems else ""))
        for pr in problems:
            print("  " + pr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
