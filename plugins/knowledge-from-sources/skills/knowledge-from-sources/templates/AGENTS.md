# {Subject} - knowledge bundle

{One sentence: what sources this bundle holds and what is built from it.}

## Where things live

| Folder | What it holds |
|---|---|
| `raw/` | untouched sources with provenance; [raw/_sources.md](raw/_sources.md) lists them. Never published |
| `sources/` | one note per source: how to cite, rights, parts, gaps |
| `concepts/` | one idea per note, with the speaker's words, cited |
| `claims/` | outside facts the concepts lean on, and how each was checked |
| [plan.md](plan.md) | the artifact being built and its route through the concepts |
| `output/` | the built artifact, and gap reviews of existing ones |
| `_meta/` | [schema](_meta/schema.md): citations, rights, privacy; `keep-out.txt` |
| `_templates/`, `_tools/` | blank notes; scripts the checks run |

`_archive/` is never read.

## Route by task

| If | Go to | Then stop at |
|---|---|---|
| adding sources | [raw/CONTEXT.md](raw/CONTEXT.md) | its check |
| a source has no note yet | [sources/CONTEXT.md](sources/CONTEXT.md) | its check |
| deciding what to build | [CONTEXT.md](CONTEXT.md) (the plan) | the author's approval |
| filling ideas | [concepts/CONTEXT.md](concepts/CONTEXT.md) | its check |
| about to state a number or general fact | [claims/CONTEXT.md](claims/CONTEXT.md) | its check |
| building or reviewing an artifact | [output/CONTEXT.md](output/CONTEXT.md) | its check |
| the exact words | the concept's "In their words" | - |
| status | `status:` lines in `_index.md` files and `plan.md` | report what exists |

## The one rule

Every quote is checked by `python -I _tools/quotes.py` before anything leaves `output/`.
