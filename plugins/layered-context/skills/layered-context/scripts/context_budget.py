#!/usr/bin/env python3
"""Report context files that break their size budget, and stage loads that break the step budget.
Exit 1 if anything is over budget (or, with --provenance, if a belief line lacks provenance).

Copy to scripts/ in a repo and run from anywhere:
    python -I scripts/context_budget.py [ROOT] [--provenance] [--json]
ROOT defaults to the folder that holds scripts/. Standard library only.

Budgets (tokens are estimated as characters / 4; override any of them in ROOT/.context-budget.json,
e.g. {"AGENTS.md": {"lines": 80}, "step_tokens": 10000}):
  AGENTS.md                  60 lines,   800 tokens   (entry file: routes only)
  CLAUDE.md, GEMINI.md        3 lines                  (one-line pointer to AGENTS.md)
  any CONTEXT.md             80 lines,   800 tokens   (router or stage contract)
  references/**/*.md        200 lines,  2000 tokens   (factory files)
  a stage's step load                   8000 tokens   (AGENTS.md + its CONTEXT.md + every
                                                       backticked path under its Inputs heading)
Skipped: dot-folders, node_modules/, _archive/, _templates/, runs/, raw/.

--provenance also checks belief files (references/decisions.md, references/app-state.md): every
top-level bullet must end with a provenance note containing "since" and a date (YYYY-MM-DD), and
no bullet may start with "Update:" (stacked corrections - rewrite the original line instead).
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
BELIEF_FILES = ("references/decisions.md", "references/app-state.md")
TICK = re.compile(r"`([^`\s]+)`")
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


def resolve(path, contract, root):
    path = path.split("#", 1)[0]
    for base in (contract.parent, root):
        p = (base / path).resolve()
        if p.is_file():
            return [p]
        if p.is_dir():
            return [f for f in p.rglob("*.md")]
    return []


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parent.parent
    cfg = json.loads(json.dumps(DEFAULTS))
    override = root / ".context-budget.json"
    if override.is_file():
        for k, v in json.loads(override.read_text()).items():
            cfg[k] = {**cfg.get(k, {}), **v} if isinstance(v, dict) else v

    rows, problems = [], []
    agents = root / "AGENTS.md"
    agents_tokens = tokens(agents.read_text(encoding="utf-8", errors="replace")) if agents.is_file() else 0

    for p, rel in walk(root):
        kind, b = budget_for(rel, cfg)
        if not kind:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        n_lines, n_tok = len(text.splitlines()), tokens(text)
        over = [f"{n_lines} lines > {b['lines']}" for _ in [0] if "lines" in b and n_lines > b["lines"]]
        over += [f"~{n_tok} tokens > {b['tokens']}" for _ in [0] if "tokens" in b and n_tok > b["tokens"]]
        rows.append((rel.as_posix(), kind, n_lines, n_tok, "; ".join(over) or "ok"))
        if over:
            problems.append(f"{rel}: {'; '.join(over)}")

        if kind == "CONTEXT.md" and "stages" in rel.parts:
            load, missing = agents_tokens + n_tok, []
            for ref in inputs_of(text):
                files = resolve(ref, p, root)
                if not files:
                    missing.append(ref)
                load += sum(tokens(f.read_text(encoding="utf-8", errors="replace")) for f in files)
            status = "ok" if load <= cfg["step_tokens"] else f"step load ~{load} tokens > {cfg['step_tokens']}"
            rows.append((rel.parent.as_posix() + " (step load)", "step", None, load, status))
            if status != "ok":
                problems.append(f"{rel.parent}: {status} - split the stage, tighten Inputs, or point at a section")

    if "--provenance" in argv:
        for bf in BELIEF_FILES:
            p = root / bf
            if not p.is_file():
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if not re.match(r"^[-*] ", line):
                    continue
                body = line[2:].strip()
                if body.lower().startswith("update:"):
                    problems.append(f"{bf}:{i}: stacked 'Update:' line - rewrite the original belief in place")
                elif "since" not in body.lower() or not DATE.search(body):
                    problems.append(f"{bf}:{i}: belief without provenance (since YYYY-MM-DD, by <who>, ref <PR|commit>)")

    if "--json" in argv:
        print(json.dumps({"rows": rows, "problems": problems}, indent=1))
    else:
        w = max([len(r[0]) for r in rows] + [10])
        for path, kind, n_lines, n_tok, status in rows:
            print(f"{path:<{w}}  {kind:<10}  {'' if n_lines is None else n_lines:>5}  ~{n_tok:>6}  {status}")
        print(f"\n{len(problems)} problem(s)" + (":" if problems else ""))
        for pr in problems:
            print("  " + pr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
