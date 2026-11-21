"""Regression tests for the shared context guards (links.py, context_budget.py).

    python3 -m unittest discover -s tests/context-guards

Each case builds a small repo in a temp dir and runs the scripts as CI does, with a timeout,
so a guard that walks outside the repo fails the test instead of hanging it.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "plugins/layered-context/skills/layered-context/scripts"
DECISIONS = "# Decisions\n\n- Postgres only (since 2026-09-02, by team, ref #1)\n"


def run(script, root, *args):
    r = subprocess.run([sys.executable, "-I", str(SCRIPTS / script), str(root), *args],
                       capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout + r.stderr


class Guards(unittest.TestCase):
    def repo(self, inputs):
        tmp = Path(tempfile.mkdtemp())
        root = tmp / "repo"
        (root / "references").mkdir(parents=True)
        (root / "stages/01_plan").mkdir(parents=True)
        (root / "AGENTS.md").write_text("# Repo\n\nRead `CONTEXT.md`.\n")
        (root / "CONTEXT.md").write_text("# Router\n\n- plan: `stages/01_plan/CONTEXT.md`\n")
        (root / "references/decisions.md").write_text(DECISIONS)
        (root / "references/standards.md").write_text("# Standards\n\n" + "x" * 4000 + "\n")
        (tmp / "outside.md").write_text("# not part of the repo\n")
        (root / "stages/01_plan/CONTEXT.md").write_text(
            "# 01_plan\n\n## Inputs\n" + "".join(f"- {i}\n" for i in inputs))
        return root

    def step_load(self, root):
        code, out = run("context_budget.py", root, "--json")
        rows = json.loads(out)["rows"]
        contract = next(r[3] for r in rows if r[0] == "stages/01_plan/CONTEXT.md")
        return code, out, next(r[3] for r in rows if r[1] == "step") - contract  # what the Inputs add

    def test_commands_and_git_refs_are_not_inputs(self):
        tokens = ["Run `go test`/`npx jest`", "`/`", "Compare with `origin/main`", "`git diff origin/main`"]
        root = self.repo(tokens + ["`references/standards.md`"])
        code, out, load = self.step_load(root)
        self.assertEqual(code, 0, out)
        _, _, only_standards = self.step_load(self.repo(["`references/standards.md`"]))
        self.assertEqual(load, only_standards, "a non-path token was counted in the step load")
        code, out = run("links.py", root)
        self.assertEqual(code, 0, out)

    def test_lone_slash_does_not_walk_the_disk(self):
        root = self.repo(["`/`", "`./`", "Run `go test`/`npx jest`"])
        code, out = run("context_guards.py", root)  # the timeout fails this test if it hangs
        self.assertEqual(code, 0, out)

    def test_missing_input_is_reported_not_crashed(self):
        root = self.repo(["`references/missing.md`", "`references/gone/`"])
        code, out = run("context_budget.py", root)
        self.assertEqual(code, 1, out)
        self.assertIn("`references/missing.md` not found", out)
        self.assertIn("`references/gone/` not found", out)
        self.assertNotIn("Traceback", out)
        code, out = run("links.py", root)
        self.assertEqual(code, 1, out)
        self.assertIn("input `references/missing.md`", out)
        self.assertNotIn("Traceback", out)

    def test_paths_outside_the_repo_are_rejected(self):
        root = self.repo(["`../../../outside.md`", "`/etc/hosts`"])
        code, out = run("context_budget.py", root)
        self.assertEqual(code, 1, out)
        self.assertIn("`../../../outside.md` not found", out)
        self.assertIn("`/etc/hosts` not found", out)
        code, out = run("links.py", root)
        self.assertEqual(code, 1, out)
        self.assertIn("input `../../../outside.md`", out)

    def test_sections_and_pending_run_outputs_still_resolve(self):
        root = self.repo(["`references/decisions.md#Data layer`", "`runs/<task-id>/00_brief.md`",
                          "`stages/`", "Do NOT load: `_archive/`"])
        self.assertEqual(run("context_guards.py", root)[0], 0)


if __name__ == "__main__":
    unittest.main()
