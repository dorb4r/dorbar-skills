# dorbar-skills

A personal [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) —
a shared catalog of skills, agents, hooks, and MCP servers I can install across all my projects.
Private for now; publishable later by pushing to a public git host.

## Layout

```
dorbar-skills/
├── .claude-plugin/
│   └── marketplace.json     # the catalog (name, owner, version, plugins[]) — GENERATED, don't hand-edit plugins[]
├── plugins/                 # one directory per plugin (the source of truth)
│   └── <plugin>/
│       ├── .claude-plugin/plugin.json   # name, version, description, author…
│       ├── skills/<name>/SKILL.md       # one or more skills
│       ├── agents/*.md                  # optional sub-agents
│       ├── hooks/hooks.json             # optional event hooks
│       ├── .mcp.json                    # optional MCP servers
│       └── CHANGELOG.md
├── templates/               # scaffolding templates (skill-plugin, bundle-plugin)
├── tools/mkt.mjs            # the marketplace toolkit (zero-dependency Node)
├── bin/mkt                  # `./bin/mkt …` convenience shim
└── .github/workflows/            # plugin-versions (PR check), release (tags on main)
```

A **plugin** is the unit Claude Code installs and versions. A plugin can be:
- **Standalone** — one skill, its own version. (`mkt new my-skill`)
- **A bundle** — several related skills/agents/hooks sharing one version. (`mkt new dev-kit --bundle`)

Skills are namespaced by plugin: a skill `foo` in plugin `bar` is invoked as `/bar:foo`.

## The `mkt` toolkit

`plugin.json` is the source of truth. `marketplace.json`'s `plugins[]` is **generated** from
the plugin manifests — never edit it by hand; run `mkt sync` (or any command that syncs).

```sh
./bin/mkt new <name> [--bundle] [--skill <skill>] [--desc "..."]   # scaffold a plugin
./bin/mkt status                                                   # versions + whether each is tagged
./bin/mkt sync                                                      # rebuild marketplace.json
./bin/mkt lint-title ["<title>"]                                    # check a PR title is a semantic commit
./bin/mkt version --title "<PR title>" [--base <ref>] [--check]     # set versions from the PR title
./bin/mkt tag [--push]                                             # tag untagged versions (CI does it on main)
./bin/mkt validate                                                 # check manifests + claude plugin validate
./bin/mkt install-hooks                                            # commit-msg conventional-commit lint
```

(Or via npm: `npm run new -- <name>`, `npm run version -- --title "..."`, etc.)

## Versioning

Two independent version axes, both SemVer:

- **Per-plugin** — `version` in each `plugins/<name>/.claude-plugin/plugin.json`. This is the cache
  key Claude Code uses to decide whether an installed plugin has an update.
- **Marketplace** — top-level `version` in `marketplace.json`. Bumped automatically to the highest
  level of any plugin changed in a release.

**The PR title sets the bump.** Merges are squash-only and the PR title becomes the commit on `main`,
so the title must be a [Conventional Commit](https://www.conventionalcommits.org/):
`<type>(<plugin>)!: <summary>`.

| PR title type           | Bump for each plugin the PR changes |
| ----------------------- | ----- |
| `fix:` `perf:` `refactor:` `revert:` | patch |
| `feat:`                 | minor |
| `<type>!:` (breaking)   | major |
| `docs:` `chore:` `style:` `test:` `ci:` `build:` | patch if a plugin's files changed, else none |

`./bin/mkt version --title "<PR title>"` writes the bumps into the PR: each changed plugin's
`plugin.json`, pyproject and `CHANGELOG.md`, and the marketplace version and root `CHANGELOG.md`
(the highest level, applied once). It computes from the versions on `main`, so rerunning it is safe.
`claude plugin update` compares versions only, so no plugin change ships without a bump.

The `plugin versions` workflow runs on every PR (and on title edits): `mkt lint-title`, then
`mkt version --check`, which fails with the exact command to run when the versions don't match the
title and the changed files. After merge, the `release` workflow runs `mkt tag --push`, tagging each
new version `<plugin>-v<version>` and `marketplace-v<version>`.

## Using this marketplace from another project

```sh
# local path (private, no publishing needed):
/plugin marketplace add /Users/dorbar/code/dorbar_skills
# or once pushed to a private/public git host:
/plugin marketplace add <owner>/dorbar-skills

/plugin install <plugin>@dorbar-skills
/plugin marketplace update dorbar-skills    # pull new versions later
```

See [docs/AUTHORING.md](docs/AUTHORING.md) for how to add a new skill or migrate an existing one.
