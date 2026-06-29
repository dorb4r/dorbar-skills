# Authoring skills & plugins

## Add a new skill (standalone plugin)

```sh
./bin/mkt new pdf-tools --desc "Extract and transform PDF content."
# edit the generated skill:
#   plugins/pdf-tools/skills/pdf-tools/SKILL.md
git add -A && git commit -m "feat(pdf-tools): add pdf-tools skill"
```

The `feat:` commit means the first `mkt release` (after baseline) will treat it as a minor bump.

## Add a bundle (several related skills in one versioned plugin)

```sh
./bin/mkt new dev-kit --bundle --skill lint-fix --desc "Everyday dev helpers."
# add more skills as sibling directories:
mkdir -p plugins/dev-kit/skills/commit-helper
$EDITOR plugins/dev-kit/skills/commit-helper/SKILL.md
```

All skills in a bundle share the bundle's single version.

## Migrate an existing skill into the marketplace

1. Scaffold a home: `./bin/mkt new <name>` (or `--bundle`).
2. Drop your existing `SKILL.md` (and any scripts/reference files) into
   `plugins/<name>/skills/<skill>/`.
3. Make sure the `SKILL.md` frontmatter has a `description` that states **when** to use it —
   that text is how Claude decides to invoke it.
4. `./bin/mkt sync && ./bin/mkt validate`
5. Commit with a Conventional Commit: `git commit -m "feat(<name>): import <skill>"`.

## What can live in a plugin

| Directory / file        | Purpose                                              |
| ----------------------- | ---------------------------------------------------- |
| `skills/<name>/SKILL.md`| Model-invoked skills (the main thing here)           |
| `agents/*.md`           | Custom sub-agents                                    |
| `hooks/hooks.json`      | Event hooks (PreToolUse, PostToolUse, …)             |
| `.mcp.json`             | MCP server definitions                               |
| `.lsp.json`             | Language-server definitions                          |
| `commands/*.md`         | Flat-file commands (legacy; prefer `skills/`)        |
| `bin/`                  | Executables added to PATH while the plugin is active |

> **Never** put `skills/`, `agents/`, or `hooks/` inside `.claude-plugin/` — only `plugin.json` goes there.
> All component directories live at the plugin root.

## SKILL.md frontmatter

```yaml
---
name: pdf-tools                  # optional; defaults to the directory name
description: >-                  # REQUIRED — include "Use when …" trigger text
  Extract and transform PDF content. Use when the user works with PDF files,
  needs text/table extraction, or wants to split/merge PDFs.
# allowed-tools: Read, Bash      # optional tool restriction
# disable-model-invocation: true # optional: only callable explicitly as /plugin:skill
---
```

## Release workflow

```sh
./bin/mkt status            # preview pending bumps
./bin/mkt release --dry-run # see what would change
./bin/mkt release           # apply, commit, tag
git push --follow-tags      # (or let the GitHub Action do it on push to main)
```
