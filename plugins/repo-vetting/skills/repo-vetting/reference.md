# Repo vetting: reference

Contents: Depth tiers · Safe clone · Five questions · Claude Code asset checklist · General code checklist · Severity · Verdict rules · Recheck.

## Depth tiers

Pick the tier from the intended use, not from the repo's size or popularity. When in doubt, go one tier up.

| Tier | When | Adds |
|---|---|---|
| **Glance** | Reading for ideas, copying a pattern by hand, running only in a throwaway sandbox with no credentials | Steps 1-4; read the README and every file you will copy |
| **Standard** | Anything that executes in your normal environment: a Claude Code plugin, skill with scripts, hook, MCP server, CLI, library you import. **Default for Claude Code assets.** | Every execution surface read in full; dependency list with lockfile status; every runtime fetch (`npx`, `uvx`, `curl`, `pip install` inside a script) traced to a pinned version or flagged |
| **Deep** | Touches client or production data, holds secrets beyond your own, rolls out to a team or org, or auto-updates | Standard, plus: transitive dependencies of what runs; vulnerability lookup (OSV, GitHub Advisory Database) with applicability check; release provenance (signed tags, published artifact compared with the source); CI workflow review; a second human reviewer signs the verdict |

A sandboxed trial run (executing the code with network monitoring) is a separate, human-run step after this report, never part of it.

## Safe clone

```
VET="<scratchpad>/vet-<name>"            # new, empty, outside any repo
mkdir "$VET"
GIT_LFS_SKIP_SMUDGE=1 git clone --no-recurse-submodules \
  -c core.symlinks=false -c core.hooksPath=/dev/null \
  <url> "$VET/src"
git -C "$VET/src" rev-parse HEAD          # record this
git -C "$VET/src" checkout --detach <sha> # when vetting a specific commit or tag
```
- `core.symlinks=false` checks symlinks out as small text files holding their target, so no later read follows them out of the clone. The scanner reports them.
- Full history is wanted for maintainer signals. `--depth` truncates history; `--filter=blob:none` keeps history but fetches file contents lazily (it is not shallow).
- Submodules are separate repos: list them from `.gitmodules` and vet each one as its own target if the asset needs it.
- **Published packages can differ from the repo.** For a library installed from a registry, vet the artifact you will actually install: get its tarball URL from the registry metadata (`npm view <pkg>@<ver> dist.tarball`, or the PyPI JSON API `https://pypi.org/pypi/<pkg>/<ver>/json`), download with `curl` into its own empty directory and extract with `tar`. Avoid `pip download` of an sdist (it runs the build backend) and any `install`.
- Marketplace repos: each plugin entry whose `source` points at another repo or URL is a separate target. An install that tracks a branch picks up every future commit; note whether the entry pins a `ref` or `sha`.

## Five questions

| # | Question | Evidence to gather | Read it carefully |
|---|---|---|---|
| 1 | Genuine and needed | Owner and repo name vs the project's own site/docs links; fork status (`gh api repos/<o>/<r>` → `fork`, `parent`); package name vs repo; what it does that you lack, and whether 30 lines of your own would do | Typosquats and lookalike orgs; a fork that is ahead of upstream by unexplained commits |
| 2 | Maintained | `git log --since=1.year --format='%an' \| sort \| uniq -c`; last commit and release dates; open vs closed issues and response times; who can merge | One-person projects are common and fine for small assets; note bus factor. Quiet can mean finished or abandoned: look at open bug reports |
| 3 | Covered | Test folder and CI that runs it; `SECURITY.md` or org-level policy (a repo-only check can miss it: mark unknown, not absent); Dependabot/Renovate config; lockfiles committed | A test folder that CI never runs is not coverage |
| 4 | Delivered | Tags and releases; `git tag -v` / `git log --show-signature` (needs keys, else unknown); release artifacts vs source; what the install command actually fetches and from where | A Claude Code plugin installs from the repo at whatever ref the marketplace names; an MCP config with `npx -y pkg` (no version) runs whatever is latest at launch |
| 5 | Licensed | `LICENSE` file, package metadata licence, per-file headers, vendored code with its own licence | No licence means no permission to reuse. Copyleft obligations matter for redistribution, not private use |

Popularity (stars, downloads) is one weak signal. A scorecard or rating is a heuristic: read the evidence behind it, and report it only if you ran it.

## Claude Code asset checklist

Read each surface in full. For every one, answer: **when does it run, what does it run, what can it read, where can it send, what does it tell the agent.**

**Plugin manifest and marketplace**
- `.claude-plugin/plugin.json`: inline `hooks`, `mcpServers`, `commands`/`agents` paths pointing outside the plugin.
- `.claude-plugin/marketplace.json`: each plugin `source` (other repos are other targets), pinned `ref`/`sha` or a floating branch.

**Hooks** (`hooks/hooks.json`, `hooks` in plugin.json, `.claude/settings*.json`)
- Event: `SessionStart` runs on every session in every project the plugin is enabled for; `UserPromptSubmit` sees every prompt you type; `PreToolUse`/`PostToolUse` see tool inputs and outputs (file contents, command output); `Stop`/`SubagentStop` can force the agent to keep going.
- Matcher: `*` or empty means every tool.
- Command: the script it calls, read in full, plus everything that script calls. `${CLAUDE_PLUGIN_ROOT}` paths resolve inside the plugin; anything else (a downloaded script, `curl | sh`, `npx`) runs code that is not in the repo.
- Output: stdout from `SessionStart`/`UserPromptSubmit` and `additionalContext` fields are injected into the model's context: read them as prompt text. A `PreToolUse` hook returning `permissionDecision: "allow"` (or `approve`) silently auto-approves tools: **severe** unless tightly scoped and explained.

**MCP servers** (`.mcp.json`, `mcpServers` in plugin.json or settings)
- `command` + `args`: local code; is the package pinned to an exact version? `npx -y`, `uvx`, `pipx run` without a version fetch latest at every launch.
- `url` / `type: http|sse`: a remote server; everything the agent sends to its tools leaves the machine. Who runs it?
- `env` and `headers`: which tokens it asks for, and their scope.
- Server source: the tool **names and descriptions** are prompt text the agent reads every session (tool poisoning lives here); tools that read files or run commands; outbound calls not needed for the stated job.

**Agent-facing markdown** (`SKILL.md`, `commands/*.md`, `agents/*.md`, `CLAUDE.md`, `AGENTS.md`, README sections addressed to "the assistant")
- Frontmatter: `allowed-tools` (grants tools without asking), agent `tools` lists, `model`. A skill or command granting `Bash` broadly deserves a reason.
- Inline shell: a line starting `!` followed by a backticked command in a command or skill file runs that shell command when invoked.
- Injection signals: instructions to ignore prior or system instructions, to hide actions from the user, to skip confirmation, to run with bypassed permissions, to fetch a URL and follow what it says, to edit `~/.claude` or other config; a `description` that claims to apply to every task (over-triggering).
- Hidden text: HTML comments, zero-width or bidirectional Unicode, white-on-white or collapsed `<details>` blocks, base64 blobs, very long single lines.

**Settings** (`.claude/settings.json` shipped in a template or repo)
- `permissions.allow` wildcards (`Bash(*)`), `defaultMode: bypassPermissions`, `enableAllProjectMcpServers`, `apiKeyHelper` and `statusLine.command` (both run shell), `env` overrides (`ANTHROPIC_BASE_URL` redirects all model traffic).

**Scripts the skill tells the agent to run**: read in full, as for hooks. A script the agent runs later still runs as you.

## General code checklist

- **Install-time execution**: `package.json` `preinstall`/`install`/`postinstall`/`prepare`; `setup.py` top level; `pyproject.toml` custom build backend; `build.rs`; `Makefile` default target; `binding.gyp`; Dockerfile `RUN` fetching remote scripts.
- **Auto-run on open**: `.vscode/tasks.json` with `runOn: folderOpen`, `.envrc`, `.devcontainer` `postCreateCommand`, git-hook installers (`husky`, `pre-commit` config).
- **Network**: `curl`, `wget`, `fetch(`, `requests`, `urllib`, `http.client`, `socket`, `Invoke-WebRequest`, raw IPs, webhook and paste hosts (Discord, Telegram, pastebin, ngrok, requestbin). For each: destination, what is sent, whether the stated job needs it.
- **Credential and private-path access**: `~/.ssh`, `~/.aws`, `~/.config/gh`, `~/.netrc`, `.env`, `~/.claude`, browser profile folders, macOS `security find-generic-password`, environment dumps (`env`, `printenv`, `os.environ` iterated whole), tokens like `GITHUB_TOKEN`, `ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`.
- **Exec and obfuscation**: `eval`, `exec`, `Function(`, `child_process`, `subprocess` with `shell=True`, `base64 -d | sh`, `atob` then eval, minified or packed files in a source repo, committed binaries.
- **Persistence**: writes to shell rc files, `crontab`, `launchctl`/LaunchAgents, systemd units, `~/.claude/settings.json`, global git config or hooks.
- **CI** (maintainer practice, Deep tier): `pull_request_target` with checkout of PR code, third-party actions not pinned to a full commit SHA, secrets exposed to forks.

## Severity

- **Severe**: credential or private-path read combined with any network send; obfuscated or downloaded code executed; silent permission auto-approval; persistence outside the asset's own folder; agent-facing text instructing concealment, bypass or following remote instructions.
- **Warning**: runtime fetch of an unpinned package or script; broad tool grants without reason; network calls the stated job does not need; hooks on every event with a wildcard matcher; no licence.
- **Caution**: single maintainer, no tests in CI, no security policy found, no lockfile, unsigned releases.

Verify before escalating: the code path is reachable, the version you vetted is affected, and a vulnerability match is the same ecosystem and package. A branch-protection rule or org policy you cannot see is **unknown**, not absent.

## Verdict rules

- Any unaccepted **severe** finding → `skip`. The owner may accept a severe finding only in writing, in the report, with the condition that contains it.
- Any **unknown** on a check the tier requires → at most `adopt with conditions`, where a condition resolves it, or `undecided: needs <check>`.
- Warnings → `adopt with conditions` naming each mitigation (pin `<sha>` or exact version, remove or narrow a hook, scope a token, disable an MCP server, run in a sandbox).
- `adopt` only when every required check is `confirmed` or triaged benign.
- Always pin: the report's commit is the one adopted. A later commit is unvetted.

For a pattern you will copy rather than install, close with the five-line note: problem · reference URL@commit · pattern (file or interaction) · reuse conditions (licence) · decision (adopt, adapt or skip, and the smallest check).

## Recheck

Recheck when: the pin moves (any update or reinstall), a new release you want, a new advisory naming it, the intended use widens (new data, new team, production), or the asset gains a new hook, MCP server or permission. A recheck diffs from the vetted commit (`git diff <old-sha>..<new-sha>`) and repeats steps 4-6 on the changed surfaces.
