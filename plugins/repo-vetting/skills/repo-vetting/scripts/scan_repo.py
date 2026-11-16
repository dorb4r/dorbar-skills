#!/usr/bin/env python3
"""Read-only inventory and pattern scan of a cloned repository, for repo-vetting.

Usage: python -I scan_repo.py <clone-dir> [--max-bytes N]

Never imports, executes or follows anything inside <clone-dir>: it walks files without
following symlinks, reads bytes, and prints a Markdown report to stdout.
The output is evidence for a human or agent to triage, never a verdict: a pattern
list that finds nothing proves only that the list missed it.
Exit 0 when the scan completed, 2 on usage error.
"""
import json
import os
import re
import sys
from collections import defaultdict
from urllib.parse import urlparse

SKIP_DIRS = {".git"}
TEXT_EXCERPT = 160
MAX_ROWS_PER_CATEGORY = 150

SURFACES = [
    ("plugin manifest", re.compile(r"(^|/)\.claude-plugin/(plugin|marketplace)\.json$")),
    ("hooks config", re.compile(r"(^|/)hooks\.json$")),
    ("claude settings", re.compile(r"(^|/)\.claude/settings(\.local)?\.json$")),
    ("mcp config", re.compile(r"(^|/)(\.mcp|mcp|claude_desktop_config)\.json$")),
    ("agent-facing markdown", re.compile(
        r"(^|/)(SKILL\.md|CLAUDE\.md|AGENTS\.md|GEMINI\.md|\.cursorrules)$|(^|/)(commands|agents)/[^/]+\.md$")),
    ("install-time code", re.compile(
        r"(^|/)(package\.json|setup\.py|setup\.cfg|pyproject\.toml|build\.rs|Makefile|binding\.gyp|"
        r"Dockerfile|install\.(sh|ps1|py))$")),
    ("auto-run on open", re.compile(
        r"(^|/)(\.vscode/tasks\.json|\.envrc|\.pre-commit-config\.yaml)$|(^|/)(\.devcontainer|\.husky|\.githooks)/")),
    ("ci workflow", re.compile(r"(^|/)\.github/workflows/[^/]+\.ya?ml$")),
    ("submodules", re.compile(r"(^|/)\.gitmodules$")),
]

PATTERNS = {
    "agent-directed text": [
        r"ignore\s+(all\s+|any\s+)?(previous|prior|above|earlier|system)\s+(instructions|prompts?|messages|rules)",
        r"disregard\s+(the\s+|all\s+|any\s+)?(previous|prior|above|system)",
        r"(do\s+not|don'?t|never)\s+(tell|inform|mention|show|reveal|notify)\b[^.\n]{0,40}\b(user|human|owner)",
        r"without\s+(asking|confirmation|confirming|telling|prompting|permission)",
        r"\b(silently|secretly|covertly)\b",
        r"\byou\s+are\s+now\b|\bnew\s+instructions\b|\bsystem\s+prompt\b",
        r"\b(fetch|curl|visit|open|read|download)\b[^.\n]{0,60}\b(and|then)\s+(follow|execute|obey|run)\b",
        r"\b(auto-?approve|always\s+approve|approve\s+all)\b",
    ],
    "permission / config override": [
        r"bypassPermissions|dangerously-skip-permissions|permissionDecision|enableAllProjectMcpServers",
        r"apiKeyHelper|ANTHROPIC_BASE_URL|Bash\(\*\)|allowed-tools",
    ],
    "network": [
        r"\b(curl|wget|Invoke-WebRequest|iwr|ncat|netcat)\b",
        r"\bfetch\s*\(|\baxios\b|\brequests\.(get|post|put|patch)|\burllib\b|\bhttp\.client\b|\bhttpx\b|"
        r"\bsocket\.|XMLHttpRequest|new\s+WebSocket",
        r"https?://\d{1,3}(\.\d{1,3}){3}",
        r"discord(app)?\.com/api/webhooks|api\.telegram\.org|pastebin|ngrok|requestbin|webhook\.site|transfer\.sh",
    ],
    "credentials / private paths": [
        r"\.ssh/|id_rsa|id_ed25519|\.aws/|\.netrc|\.config/gh|\.claude/(settings|\.credentials|credentials)",
        r"find-generic-password|security\s+dump-keychain|Login\s+Data|Cookies\.binarycookies",
        r"\bprintenv\b|os\.environ\.copy\(\)|dict\(os\.environ\)|JSON\.stringify\(process\.env\)|"
        r"Object\.(keys|entries)\(process\.env\)",
        r"\b[A-Z0-9_]*(TOKEN|API_KEY|SECRET|PASSWORD)[A-Z0-9_]*\b",
    ],
    "exec / obfuscation": [
        r"\beval\s*\(|\bexec\s*\(|new\s+Function\s*\(|child_process|os\.system\s*\(|shell\s*=\s*True",
        r"base64\s+(-d|--decode)|b64decode|\batob\s*\(|fromCharCode",
        r"\|\s*(ba|z|da)?sh\b|\|\s*python3?\b|\|\s*node\b",
        r"\bnpx\s+(-y|--yes)\b|\buvx\b|\bpipx\s+run\b",
    ],
    "persistence": [
        r"\.(bash|zsh)rc\b|\.bash_profile|\.zprofile|\bcrontab\b|\blaunchctl\b|LaunchAgents|\bsystemctl\b",
        r"git\s+config\s+--global|core\.hooksPath",
    ],
}
COMPILED = {k: [re.compile(p, re.IGNORECASE if k == "agent-directed text" else 0) for p in v]
            for k, v in PATTERNS.items()}
INLINE_SHELL_MD = re.compile(r"!`[^`]+`")
HTML_COMMENT = re.compile(r"<!--")
URL_RE = re.compile(r"https?://[^\s\"'<>)`\]]+")
HIDDEN = re.compile("[​-‏⁠-⁤‪-‮⁦-⁩﻿]")
LIFECYCLE = {"preinstall", "install", "postinstall", "prepare", "prepublish", "preprepare", "postprepare"}
SHA_PIN = re.compile(r"@[0-9a-f]{40}\b")


def excerpt(line):
    line = line.strip().replace("`", "'")
    line = HIDDEN.sub(lambda m: "<U+%04X>" % ord(m.group()), line)
    line = "".join(c if c.isprintable() else "?" for c in line)
    return line[:TEXT_EXCERPT] + ("..." if len(line) > TEXT_EXCERPT else "")


def is_binary(head):
    return b"\x00" in head


def load_json(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def hooks_rows(rel, hooks):
    rows = []
    if isinstance(hooks, str):
        return ["`%s`: hooks loaded from path `%s` (read that file)" % (rel, hooks)]
    if not isinstance(hooks, dict):
        return rows
    for event, groups in hooks.items():
        for g in groups if isinstance(groups, list) else []:
            matcher = g.get("matcher", "") if isinstance(g, dict) else ""
            for h in (g.get("hooks", []) if isinstance(g, dict) else []):
                if isinstance(h, dict):
                    rows.append("`%s`: **%s** matcher=`%s` %s=`%s`" % (
                        rel, event, matcher or "*", h.get("type", "?"),
                        excerpt(str(h.get("command") or h.get("prompt") or h.get("url") or ""))))
    return rows


def mcp_rows(rel, servers):
    if isinstance(servers, str):
        return ["`%s`: MCP servers loaded from path `%s` (read that file)" % (rel, servers)]
    rows = []
    for name, s in (servers or {}).items() if isinstance(servers, dict) else []:
        if not isinstance(s, dict):
            continue
        target = s.get("url") or " ".join([str(s.get("command", ""))] + [str(a) for a in s.get("args", [])])
        rows.append("`%s`: server **%s** type=`%s` -> `%s`; env keys=%s; header keys=%s" % (
            rel, name, s.get("type", "stdio"), excerpt(target),
            sorted((s.get("env") or {}).keys()), sorted((s.get("headers") or {}).keys())))
    return rows


def json_details(rel, data, details):
    if not isinstance(data, dict):
        return
    base = os.path.basename(rel)
    if "hooks" in data:
        details["hooks"] += hooks_rows(rel, data["hooks"])
    if "mcpServers" in data:
        details["mcp servers"] += mcp_rows(rel, data["mcpServers"])
    if base == "package.json" and isinstance(data.get("scripts"), dict):
        for k, v in data["scripts"].items():
            if k in LIFECYCLE:
                details["install-time scripts"].append("`%s`: **%s** = `%s`" % (rel, k, excerpt(str(v))))
    if base.startswith("settings"):
        perms = data.get("permissions") or {}
        for key in ("allow", "defaultMode", "additionalDirectories"):
            if key in perms:
                details["settings"].append("`%s`: permissions.%s = `%s`" % (rel, key, excerpt(json.dumps(perms[key]))))
        for key in ("apiKeyHelper", "statusLine", "enableAllProjectMcpServers", "env"):
            if key in data:
                details["settings"].append("`%s`: %s = `%s`" % (rel, key, excerpt(json.dumps(data[key]))))
    if base == "marketplace.json":
        for p in data.get("plugins", []) or []:
            if isinstance(p, dict):
                details["marketplace sources"].append("`%s`: plugin **%s** source=`%s`" % (
                    rel, p.get("name", "?"), excerpt(json.dumps(p.get("source")))))


def scan(root, max_bytes):
    surfaces = defaultdict(list)
    hits = defaultdict(list)
    details = defaultdict(list)
    domains = defaultdict(set)
    symlinks, binaries, executables, large, unreadable = [], [], [], [], []
    files = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for d in list(dirnames):
            p = os.path.join(dirpath, d)
            if os.path.islink(p):
                symlinks.append("`%s` -> `%s`" % (os.path.relpath(p, root), os.readlink(p)))
                dirnames.remove(d)
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if os.path.islink(path):
                symlinks.append("`%s` -> `%s`" % (rel, os.readlink(path)))
                continue
            files += 1
            for label, rx in SURFACES:
                if rx.search(rel):
                    surfaces[label].append(rel)
            try:
                st = os.stat(path, follow_symlinks=False)
                if st.st_mode & 0o111:
                    executables.append(rel)
                if st.st_size > max_bytes:
                    large.append("%s (%d bytes, not scanned)" % (rel, st.st_size))
                    continue
                with open(path, "rb") as fh:
                    raw = fh.read()
            except OSError as e:
                unreadable.append("%s (%s)" % (rel, e.__class__.__name__))
                continue
            if is_binary(raw[:8192]):
                binaries.append(rel)
                continue
            text = raw.decode("utf-8", errors="replace")
            if fn.endswith(".json"):
                json_details(rel, load_json(text), details)
            is_md = fn.lower().endswith((".md", ".mdx", ".markdown"))
            for n, line in enumerate(text.splitlines(), 1):
                loc = "%s:%d" % (rel, n)
                if len(line) > 1000:
                    hits["long line (>1000 chars)"].append((loc, line[:80]))
                if HIDDEN.search(line):
                    hits["hidden unicode"].append((loc, line))
                if is_md and HTML_COMMENT.search(line):
                    hits["html comment in markdown"].append((loc, line))
                if is_md and INLINE_SHELL_MD.search(line):
                    hits["inline shell in markdown (!`cmd`)"].append((loc, line))
                if rel.startswith(".github/workflows/"):
                    if "pull_request_target" in line:
                        hits["ci: pull_request_target"].append((loc, line))
                    if re.search(r"^\s*-?\s*uses:\s*[^./][^@\s]*@", line) and not SHA_PIN.search(line):
                        hits["ci: action not pinned to full SHA"].append((loc, line))
                for cat, rxs in COMPILED.items():
                    if any(r.search(line) for r in rxs):
                        hits[cat].append((loc, line))
                for u in URL_RE.findall(line):
                    host = urlparse(u).hostname
                    if host:
                        domains[host].add(rel)
    return dict(files=files, surfaces=surfaces, hits=hits, details=details, domains=domains,
                symlinks=symlinks, binaries=binaries, executables=executables, large=large,
                unreadable=unreadable)


def section(title, rows):
    print("\n## %s (%d)" % (title, len(rows)))
    if not rows:
        print("- none found (not proof of absence)")
    for r in rows[:MAX_ROWS_PER_CATEGORY]:
        print("- " + r)
    if len(rows) > MAX_ROWS_PER_CATEGORY:
        print("- ... %d more; narrow with grep" % (len(rows) - MAX_ROWS_PER_CATEGORY))


def main(argv):
    args = argv[1:]
    max_bytes = 2_000_000
    if "--max-bytes" in args:
        i = args.index("--max-bytes")
        max_bytes = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1 or not os.path.isdir(args[0]):
        sys.stderr.write(__doc__)
        return 2
    root = os.path.abspath(args[0])
    r = scan(root, max_bytes)
    print("# Scan: %s" % root)
    print("\nFiles scanned: %d. Evidence for triage, not a verdict: every surface below gets read "
          "by hand, every hit gets `benign: <why>` or a finding." % r["files"])
    print("\n# Execution surfaces")
    for label, _ in SURFACES:
        section(label, ["`%s`" % p for p in r["surfaces"].get(label, [])])
    for key in ("hooks", "mcp servers", "install-time scripts", "settings", "marketplace sources"):
        section("detail: " + key, r["details"].get(key, []))
    section("symlinks (directories not followed)", r["symlinks"])
    section("binary files", ["`%s`" % b for b in r["binaries"]])
    section("executable-bit files", ["`%s`" % e for e in r["executables"]])
    section("skipped: too large", r["large"])
    section("unreadable", r["unreadable"])
    print("\n# Pattern hits")
    cats = list(PATTERNS) + ["hidden unicode", "html comment in markdown", "inline shell in markdown (!`cmd`)",
                             "long line (>1000 chars)", "ci: pull_request_target", "ci: action not pinned to full SHA"]
    for cat in cats:
        section(cat, ["`%s` `%s`" % (loc, excerpt(line)) for loc, line in r["hits"].get(cat, [])])
    print("\n# Domains referenced")
    rows = ["`%s` in %s" % (d, ", ".join("`%s`" % f for f in sorted(fs)[:5]) + (" +%d" % (len(fs) - 5) if len(fs) > 5 else ""))
            for d, fs in sorted(r["domains"].items())]
    section("domains", rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
