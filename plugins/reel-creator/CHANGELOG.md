# Changelog

All notable changes to this plugin are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/), versions follow [SemVer](https://semver.org/).
Entries are written by `mkt version` from each PR's title.

## [0.1.0] - Unreleased

- Staged reel pipeline as a layered workspace: 8 stage contracts (brief → ideas → script → footage/shoot card → music map → CapCut build → cold review → learn), a router, and project/run templates.
- Craft references distilled from research (story, formats, hooks, script, shooting, shoot card, music, sound design, editing, CapCut, review, toolbox, study-a-reel).
- 10 studied reference reels in `examples/`.
- Tools: `build_reel.py` (adds SFX/music-section/VO audio tracks, constant speed, caption emphasis word; requires STYLE_FROM), `capcut_mac.py` (project-neutral; `$REEL_BACKUP_DIR`), `beatgrid.py`, `reel_breakdown.py` (shots, cut-vs-beat offsets, audio hits).
