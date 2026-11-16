#!/usr/bin/env python3
"""loop_decide.py - apply a bounded refinement loop's stop rule (bounded-loop skill).

Reads every runs/<id>/NN_attempt-K_check.md, judges them all against the ORIGINAL check list
(the ids reported by attempt 1), and decides: again, done, or stop. When the loop ends it writes
runs/<id>/NN_check.md (first line `pass` or `fail: <why>`) and, with --output, copies the BEST
attempt (most checks passed; ties go to the earlier attempt) to the stage's output path.

Attempt check-file lines (any order, one per check; other lines are ignored):
    pass <check-id>
    fail <check-id>: <the line or place it failed on>
A leading "- " is allowed. The file's first line is the attempt's own overall verdict and is
otherwise ignored, with one exception: a first line `blocked: <why>` means the attempt could not
be judged or needs a person (a missing credential, a tool absent, a decision-gates question routed
to a person). Any blocked attempt ends the loop at once: NN_check.md gets first line
`fail: blocked at attempt K: <why>`, nothing is copied to --output, and the exit code is 4.
A blocked file needs no check lines. Once the blocker is answered, re-evaluate that attempt
(overwrite its check file with the full results) and run this script again.

Exit codes: 0 loop ended, best attempt passes every check
            1 loop ended (budget or marginal), best attempt still fails; the run stops
            3 run another attempt (the carry is printed)
            4 an attempt is blocked; the run stops and the blocker goes to a person
            2 usage or format error

Usage: python -I loop_decide.py runs/<id> <NN> [--budget 3] [--output runs/<id>/NN_<name>.md]
Standard library only.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

CHECK_LINE = re.compile(r"^\s*(?:[-*]\s+)?(pass|fail)\s+([A-Za-z0-9_.-]+)\s*:?\s*(.*)$")


def die(msg):
    print(f"loop_decide: {msg}", file=sys.stderr)
    sys.exit(2)


def read_results(path):
    results = {}
    for raw in path.read_text(encoding="utf-8").splitlines()[1:]:
        m = CHECK_LINE.match(raw)
        if not m:
            continue
        verdict, cid, why = m.groups()
        if cid in results:
            die(f"{path.name}: check '{cid}' reported twice")
        results[cid] = (verdict == "pass", why.strip())
    if not results:
        die(f"{path.name}: no 'pass <id>' / 'fail <id>: <why>' lines")
    return results


def main():
    ap = argparse.ArgumentParser(description="Apply a bounded loop's stop rule.")
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("stage", help="stage number, e.g. 03")
    ap.add_argument("--budget", type=int, default=3)
    ap.add_argument("--output", type=Path, help="copy the best attempt here when the loop ends")
    a = ap.parse_args()
    if a.budget < 1:
        die("--budget must be at least 1")

    pat = re.compile(rf"^{re.escape(a.stage)}_attempt-(\d+)_check\.md$")
    found = {}
    for p in a.run_dir.glob(f"{a.stage}_attempt-*_check.md"):
        m = pat.match(p.name)
        if m:
            found[int(m.group(1))] = p
    if not found:
        die(f"no {a.stage}_attempt-K_check.md files in {a.run_dir}")
    ks = sorted(found)
    if ks != list(range(1, len(ks) + 1)):
        die(f"attempt numbers must run 1..K without gaps, found {ks}")

    for k in ks:
        lines = found[k].read_text(encoding="utf-8").splitlines()
        head = lines[0].strip() if lines else ""
        if head.lower().startswith("blocked:"):
            why = head.split(":", 1)[1].strip() or "no reason given"
            first = f"fail: blocked at attempt {k}: {why}"
            (a.run_dir / f"{a.stage}_check.md").write_text(
                f"{first}\n\n# {a.stage} check: bounded-loop verdict\n\n"
                f"Attempt {k} is blocked, not failed: a person answers the blocker before any retry.\n",
                encoding="utf-8")
            print(first)
            sys.exit(4)

    results = {k: read_results(found[k]) for k in ks}
    original = list(results[1])
    for k in ks[1:]:
        missing = [c for c in original if c not in results[k]]
        extra = [c for c in results[k] if c not in original]
        if missing or extra:
            die(f"attempt {k} was not judged against the original checks "
                f"(missing: {missing or '-'}; extra: {extra or '-'}). Re-evaluate it against the full list.")

    def score(k):
        return sum(ok for ok, _ in results[k].values())

    def fails(k):
        return [(c, results[k][c][1]) for c in original if not results[k][c][0]]

    best = max(ks, key=lambda k: (score(k), -k))
    last = ks[-1]
    n = len(original)

    if score(best) == n:
        reason = None
    elif len(ks) >= a.budget:
        reason = f"budget spent ({len(ks)} attempts)"
    elif len(ks) >= 2 and not any(not results[last - 1][c][0] and results[last][c][0] for c in original):
        reason = f"marginal (attempt {last} turned no check from fail to pass)"
    else:
        print(f"again: write attempt {last + 1}, starting from attempt {best} "
              f"({a.stage}_attempt-{best}.md, {score(best)}/{n} pass). Change only what these lines name:")
        for c, why in fails(best):
            print(f"  fail {c}: {why}")
        sys.exit(3)

    if reason is None:
        first = "pass"
    else:
        first = f"fail: {reason}; best attempt {best} fails " + ", ".join(c for c, _ in fails(best))
    lines = [first, "", f"# {a.stage} check: bounded-loop verdict", "",
             f"Best attempt: {best} (`{a.stage}_attempt-{best}.md`), {score(best)}/{n} checks pass.", ""]
    for k in ks:
        f = [c for c, _ in fails(k)]
        lines.append(f"- attempt {k}: {score(k)}/{n}" + (f"; fails {', '.join(f)}" if f else ""))
    lines += ["", f"## Attempt {best}, every check", ""]
    for c in original:
        ok, why = results[best][c]
        lines.append(f"- pass {c}" if ok else f"- fail {c}: {why}")
    (a.run_dir / f"{a.stage}_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if a.output:
        src = a.run_dir / f"{a.stage}_attempt-{best}.md"
        if not src.exists():
            die(f"{src} not found; cannot copy the best attempt to {a.output}")
        shutil.copyfile(src, a.output)
    print(first)
    sys.exit(0 if reason is None else 1)


if __name__ == "__main__":
    main()
