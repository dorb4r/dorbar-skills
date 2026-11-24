# Router: reel-creator

| If | Go to | Stop at |
|---|---|---|
| a new reel is requested | `stages/01_brief/CONTEXT.md` | the owner confirms the brief |
| the brief is confirmed | `stages/02_ideas/CONTEXT.md` | the owner picks an idea |
| an idea is picked | `stages/03_script/CONTEXT.md` | the owner approves the script |
| the script is approved | `stages/04_footage/CONTEXT.md` | every row has a clip (pass), or the shoot card is sent and the run waits |
| footage is complete | `stages/05_music/CONTEXT.md` | the owner approves the track |
| the music map exists | `stages/06_edit/CONTEXT.md` | the build opens in CapCut |
| a build is ready | `stages/07_review/CONTEXT.md` | the owner approves the cut |
| a reel was posted ≥ 7 days ago | `stages/08_learn/CONTEXT.md` | lessons confirmed |
| the owner sends a reel to learn from | `references/study-a-reel.md` | the example note is written |
| "give me reel ideas" (no reel yet) | `stages/02_ideas/CONTEXT.md` with a short brief | the pitch |
| asked for status | list `{project}/runs/`; per run, its highest `NN_*` file and `NN_check.md` | report what exists; no runs = nothing in progress |
| a project has no `AGENTS.md` | copy `templates/project/` into it, fill `brand.md` with the owner | the owner confirms `brand.md` |

## Pipeline
| Stage | Command | Makes | Human check |
|---|---|---|---|
| 01_brief | — | `01_brief.md` | owner confirms |
| 02_ideas | — | `02_ideas.md` | owner picks |
| 03_script | — | `03_script.md` | owner (+ speaker) approves |
| 04_footage | `tools/reel_breakdown.py` for contact sheets | `04_footage.md`, `raw/`, shoot card | filmer shoots if needed |
| 05_music | `tools/beatgrid.py` | `05_music.md` | owner approves the track |
| 06_edit | `tools/build_reel.py` | `06_spec.py`, CapCut project | — |
| 07_review | reviewer sub-agent, `tools/reel_breakdown.py` | `07_review.md`, `07_owner.md` | owner approves the cut |
| 08_learn | — | `08_results.md`, project `decisions.md` | owner confirms lessons |

Skipping a stage is the owner's call, said out loud, and written at the top of the run's next file.

## Maintenance
Rerun the walk test when a stage or reference changes. Lessons that apply beyond one project become
a one-rule edit to a reference here (PR in the skills repo), never a copy in the project.
