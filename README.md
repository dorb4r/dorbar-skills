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
└── .github/workflows/release.yml   # auto-release on push to main
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
./bin/mkt status                                                   # versions + pending bumps
./bin/mkt sync                                                      # rebuild marketplace.json
./bin/mkt release [--dry-run] [--plugin <name>] [--no-git]         # auto-bump + tag
./bin/mkt bump <plugin> <patch|minor|major>                        # manual bump
./bin/mkt validate                                                 # check manifests + claude plugin validate
./bin/mkt check-bump [--base <ref>]                                # fail if a plugin changed without a version bump
./bin/mkt install-hooks                                            # commit-msg conventional-commit lint
```

(Or via npm: `npm run new -- <name>`, `npm run release`, etc.)

## Versioning

Two independent version axes, both SemVer:

- **Per-plugin** — `version` in each `plugins/<name>/.claude-plugin/plugin.json`. This is the cache
  key Claude Code uses to decide whether an installed plugin has an update.
- **Marketplace** — top-level `version` in `marketplace.json`. Bumped automatically to the highest
  level of any plugin changed in a release.

Bumps are derived from **[Conventional Commits](https://www.conventionalcommits.org/)** since each
plugin's last release tag, scoped by which files the commit touched:

| Commit type             | Bump  |
| ----------------------- | ----- |
| `fix:` `perf:` `refactor:` `revert:` | patch |
| `feat:`                 | minor |
| `feat!:` / `BREAKING CHANGE` | major |
| `docs:` `chore:` `style:` `test:` `ci:` `build:` | none |

`mkt release` applies the bumps, prepends each plugin's `CHANGELOG.md`, syncs `marketplace.json`,
bumps the marketplace version, commits, and tags (`<plugin>-v<version>`, `marketplace-v<version>`).
The GitHub Actions workflow runs this automatically on every push to `main` once a `RELEASE_TOKEN`
secret exists (see `release.yml`); until then, tag by hand after merging.

**Every PR that changes a plugin's files bumps that plugin's version** (`./bin/mkt bump <plugin>
<level>`, which also updates its CHANGELOG, pyproject and `marketplace.json`). `claude plugin update`
compares versions only, so an unbumped change never reaches installed copies. The `plugin versions`
workflow runs `mkt check-bump` on every PR and fails when a changed plugin (CHANGELOG.md aside) kept
its base version or reuses a tagged one. `mkt release` tags a version bumped this way as is, without
bumping it again.

> First `mkt release` establishes baseline tags at the current versions without bumping. After that,
> commits drive the bumps. Run `mkt install-hooks` once to enforce the commit format locally.

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
