# Vetting report: <name>

| Field | Value |
|---|---|
| URL (as given) | <url> |
| Upstream confirmed | <url, and how: official site link / org / package metadata> |
| Commit vetted | <40-char sha> (from <branch or tag>) |
| Published artifact | <pkg@version + tarball URL, or n/a> |
| Date | <YYYY-MM-DD> |
| Intended use | <what it will do, where it runs, data and credentials it can reach> |
| Tier | <Glance / Standard / Deep>, because <reason> |
| Reviewer(s) | <agent + human> |

## Verdict
**<adopt / adopt with conditions / skip / undecided: needs <check>>**

Conditions:
- <pin to <sha>; remove hook X; scope token Y; ...>

Recheck when: <triggers>

## Five questions
| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Genuine and needed | confirmed / concern / unknown | <file:line, URL or command> |
| 2 | Maintained | | |
| 3 | Covered | | |
| 4 | Delivered | | |
| 5 | Licensed | | |

## What it runs, reads and sends
| Surface | Trigger | Runs | Reads | Sends to | Agent-facing text | Verdict |
|---|---|---|---|---|---|---|
| <hooks/hooks.json SessionStart> | <every session> | <script path> | <paths, env> | <host or none> | <injected text, quoted> | benign: <why> / finding <id> / unknown |

## Findings
| ID | Severity | Where | What | Evidence | Mitigation |
|---|---|---|---|---|---|
| F1 | severe / warning / caution | <file:line> | <one line> | <excerpt in code block or command output> | <condition, or none> |

## Checks run
- <command or lookup, with its result; scan output in `scan.md`>

## Unknowns
- <check the tier requires that could not be completed, and why; the next check that would settle it>

---
<url> @ <sha7> · <date> · <verdict> · unknowns: <n>
