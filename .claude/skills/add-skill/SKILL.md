---
name: add-skill
description: Add, import, or file a skill/plugin into the dorbar-skills marketplace the correct way. Use when working in the dorbar-skills repo and asked to add a new skill, import a skill exported from elsewhere, create a plugin, or register something in the marketplace. Triggers: add skill, file skill, import skill, new plugin, register skill, scaffold plugin, marketplace.
---

# Add a skill to dorbar-skills

This repo is a Claude Code plugin marketplace. Skills live *inside plugins*; the marketplace
catalogs **plugins**, and versioning is per-plugin. Follow this exact workflow — don't improvise.

## Golden rules
- **`plugins/<name>/.claude-plugin/plugin.json` is the source of truth.** `marketplace.json`'s
  `plugins[]` is GENERATED — never hand-edit it. Run `./bin/mkt sync` to regenerate.
- **Imported skills are copied verbatim.** Don't rewrite an exported `SKILL.md`; only its home changes.
- **The PR title sets the version.** Merges are squash-only with the PR title as the commit on
  `main`, so the title is the semantic commit: see *PR title format* below. Commits inside the PR
  also follow it (the `commit-msg` hook checks them), but only the title decides the bump.

## Decide the shape
- **Standalone** (default): one skill = one plugin with its own version. `./bin/mkt new <name>`
- **Bundle**: several related skills sharing one version. `./bin/mkt new <name> --bundle`

## Steps
1. **Scaffold:** `./bin/mkt new <name> --desc "What it does. Use when ..."`
   (kebab-case name; this also auto-syncs the catalog.)
2. **Add the skill content:**
   - New skill → edit `plugins/<name>/skills/<name>/SKILL.md`.
   - Imported skill → copy the source `SKILL.md` **verbatim** over the generated one
     (`cp <src>/SKILL.md plugins/<name>/skills/<name>/SKILL.md`), plus any `scripts/`/`references/`
     it needs. Do **not** copy staging files like `HANDOFF.md`.
3. **Frontmatter check:** `SKILL.md` must have a `description` that states **when** to use it
   (trigger phrases). That text is how Claude decides to invoke the skill.
4. **Metadata:** set `keywords` (and optionally `category`) in `plugin.json` for discovery.
5. **Sync + validate:** `./bin/mkt sync && ./bin/mkt validate` — must pass `claude plugin validate`.
6. **Branch + commit:** `git switch -c feat/<name>`, then
   `git add -A && git commit -m "feat(<name>): add <skill>"`.
7. **Version from the PR title:** pick the title now, then run
   `./bin/mkt version --title "<the PR title>"` and commit what it writes
   (`chore(<name>): version`). It sets every changed plugin's version, its pyproject and CHANGELOG,
   and the marketplace version; rerun it whenever the title or the changed plugins change (it is
   idempotent and drops sections it wrote for a superseded version).
8. **Push + PR:** `git push -u origin HEAD && gh pr create --title "<the same title>"`. The
   `plugin versions` check runs `mkt lint-title` and `mkt version --check`; if you edit the title on
   GitHub, rerun step 7 with the new title and push.
9. **After merge** the `release` workflow tags each new version `<plugin>-v<version>` (and
   `marketplace-v<version>`). Nothing to do by hand; `./bin/mkt status` shows any untagged version.

## PR title format
`<type>(<scope>)!: <summary>`: lowercase type, scope = the plugin name (comma-separate several, or
omit it for repo-only changes), `!` only for a breaking change, summary in the imperative.

| Title | Bump for each plugin the PR changes |
| ----- | ----------------------------------- |
| `feat(<plugin>)!: ...` | major |
| `feat(<plugin>): ...` | minor |
| `fix:` `perf:` `refactor:` `revert:` | patch |
| `docs:` `style:` `test:` `build:` `ci:` `chore:` | patch if a plugin's files changed, else none |

Every plugin whose files the PR changes (CHANGELOG.md aside) moves one level from its version on
`main`; the marketplace version moves by the same level when any plugin does. A version bump is what
makes `claude plugin update` see a change, so no plugin change ships without one.

## Don't
- Don't put `skills/`, `agents/`, or `hooks/` inside `.claude-plugin/` — only `plugin.json` goes there.
- Don't hand-edit `marketplace.json` plugin entries (use `mkt sync`).
- Don't use a `./<name>` source — sync emits `./plugins/<name>` (resolved from the marketplace root).
- Don't write non-conventional commit messages — the hook will reject them.

## Verify it installs (from another project)
```
/plugin marketplace update dorbar-skills
/plugin install <name>@dorbar-skills
```
