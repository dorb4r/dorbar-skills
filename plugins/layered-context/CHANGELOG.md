# Changelog

All notable changes to this plugin are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/), versions follow [SemVer](https://semver.org/).
Entries are written by `mkt version` from each PR's title.

## [0.1.1] - 2026-11-21

- fix(layered-context): guards skip backticked non-paths in Inputs (`go test`, `origin/main`, a lone `/`) instead of resolving `/` and walking the disk
- fix(layered-context): an input that resolves outside the repo or does not exist is reported as a problem, not crashed on or silently dropped

## [0.1.0] - Unreleased

- Initial scaffold.
