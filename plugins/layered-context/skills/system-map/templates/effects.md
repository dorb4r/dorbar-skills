# Effects: change-impact index

Catalog only: "if you are changing X, open these cards." The waterfalls live on the cards; when this index and a card disagree, fix the card, then this line.

## Inside the tree

| If you change | Open first | Then check |
|---|---|---|
| {noun or path glob, e.g. `src/billing/**`} | [{card}](objects/{cluster}/{card}.md) | [{card}](processes/{card}.md) |

## Pointing in from outside

Consumers that hardcode a path, name, schema or endpoint of this tree. Nothing inside the tree references them, so they break silently. Each row also appears under **Outside the tree** on the card it lands on.

| Consumer | Where it lives | What it depends on | Card |
|---|---|---|---|
| {CI workflow} | `.github/workflows/{file}.yml:{line}` | `{path or command}` | [{card}](objects/{cluster}/{card}.md) |
| {agent hook / setting} | `.claude/{file}:{line}` | `{path}` | |
| {infra config} | `{infra/file}:{line}` | `{env var, port, bucket}` | |
| {other service or repo} | {repo name + path, from the owner} | `{endpoint, table, package}` | |

Searched: {date} at `{short-sha}` with {the commands run}. Owner-supplied rows: {who, date}.
