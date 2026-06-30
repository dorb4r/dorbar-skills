<!-- main is protected: every change lands via a reviewed PR. -->

## What & why

<!-- One or two lines. What does this add/change, and why? -->

## Type

- [ ] New skill / plugin (`feat`)
- [ ] Fix to an existing skill/plugin (`fix`)
- [ ] Tooling / docs / chore

## Checklist

- [ ] Commit messages follow Conventional Commits (`feat(<plugin>): …`, `fix(<plugin>): …`)
- [ ] `./bin/mkt validate` passes
- [ ] `marketplace.json` was generated via `./bin/mkt sync` (not hand-edited)
- [ ] Imported `SKILL.md` copied verbatim; no staging files (e.g. `HANDOFF.md`) included
- [ ] `SKILL.md` frontmatter has a `description` with clear "use when" triggers
