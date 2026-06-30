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
- **Commits must follow Conventional Commits** (a `commit-msg` hook enforces it) — that's what drives
  auto-versioning. New skill = `feat(<plugin>): ...`; bug fix = `fix(<plugin>): ...`.

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
6. **Commit + push:**
   `git add -A && git commit -m "feat(<name>): add <skill>" && git push`
7. **Version (optional now, required for clean updates):** `./bin/mkt release` bumps versions from
   commit history, updates CHANGELOGs, and tags. First release per plugin just sets the baseline tag.

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
