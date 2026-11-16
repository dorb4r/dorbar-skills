#!/usr/bin/env python3
"""Run the layered-context guards on a repo: links.py (every link and Inputs path resolves) and
context_budget.py --provenance (file budgets, step loads, belief-line provenance).
Exit 1 if either fails, 2 on bad usage.

One shared copy, used from three places (never copy these scripts into a product repo):
  CI      uses: dorb4r/dorbar-skills/.github/actions/context-guards@<commit sha>
  local   uvx --from "git+https://github.com/dorb4r/dorbar-skills@<commit sha>#subdirectory=plugins/layered-context/skills/layered-context/scripts" context-guards
  agent   python3 -I <layered-context skill dir>/scripts/context_guards.py <repo root>

    context_guards.py [ROOT] [--skip FOLDER ...] [--no-provenance] [--summary FILE]
ROOT defaults to the current directory. A repo's own limits live in ROOT/.context-budget.json.
--summary appends a Markdown report to FILE (CI passes $GITHUB_STEP_SUMMARY).
Standard library only.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if any(a in ("-h", "--help") for a in args):
        print(__doc__)
        return 0
    skip, summary, provenance, rest = [], None, True, []
    while args:
        a = args.pop(0)
        if a == "--skip" and args:
            skip += ["--skip", args.pop(0)]
        elif a == "--summary" and args:
            summary = args.pop(0)
        elif a == "--no-provenance":
            provenance = False
        elif a.startswith("--"):
            print(f"unknown option {a}\n{__doc__}", file=sys.stderr)
            return 2
        else:
            rest.append(a)
    if len(rest) > 1:
        print(__doc__, file=sys.stderr)
        return 2
    root = str(Path(rest[0] if rest else ".").resolve())

    checks = [
        ("links.py", [root, *skip]),
        ("context_budget.py", [root] + (["--provenance"] if provenance else [])),
    ]
    failed = []
    for script, script_args in checks:
        run = subprocess.run([sys.executable, "-I", str(HERE / script), *script_args],
                             capture_output=True, text=True)
        out = (run.stdout + run.stderr).rstrip()
        status = "ok" if run.returncode == 0 else f"failed (exit {run.returncode})"
        print(f"== {script}: {status}\n{out}\n")
        if run.returncode:
            failed.append(script)
        if summary:
            with open(summary, "a", encoding="utf-8") as f:
                f.write(f"### {script}: {status}\n```\n{out}\n```\n")
    print("context guards: " + ("all passed" if not failed else "failed: " + ", ".join(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
