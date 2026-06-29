---
name: obsidian-knowledge
description: Manage project knowledge in an Obsidian vault — capture durable facts, decisions, and status, and keep planning legible for both humans and agents. Use when saving/organizing project notes, maintaining a knowledge base / second brain / project wiki, recording decisions or status, or keeping plans current. Triggers: obsidian, vault, knowledge base, second brain, project notes, project wiki, MOC, "save/document this", "update the plan".
---

# Obsidian Knowledge

Maintain ONE Obsidian vault as the durable, shared source of truth for a project — optimized so humans skim it fast and agents parse it reliably.

## When to use
- Saving or updating project knowledge, decisions, status, or research.
- Setting up or maintaining a project vault.
- Producing planning that both humans and agents consume.

## When NOT to use
- Code-level docs that belong in the repo README.
- Conversation-only facts with no future value.

## Vault model (conventions)
- **One concept per note.** Short, skimmable; the title IS the concept.
- **`Home` note = Map of Content (MOC).** Links every note + a one-line current-status banner at the top.
- **Link liberally** with `[[wikilinks]]` and `[[note#heading]]`. Links to not-yet-written notes are fine — they mark what to write next.
- **Status markers everywhere:** `✅ done` · `🔜 open` · `⚠️ risk` · `❓ needs input`.
- **Diagrams = Mermaid** fenced blocks (see Rendering).
- **Planning = goal → cadence.** A top note states the single goal/metric; decompose into a `Weekly Cadence` note + dated `Weekly Notes/<ISO-week>.md` generated from a `Templates/` note. Max 3 goals per week, each with an owner + status.
- **Version with git.** Commit after meaningful changes. Gitignore per-machine Obsidian state (`.obsidian/workspace*.json`, cache).

## Saving knowledge (rules)
1. **Find the right existing note and update it — do not duplicate.** Create a new note only for a genuinely new concept.
2. **Keep `Home`/MOC current** — add the link and refresh the status banner.
3. **Resolve, don't pile up.** When a decision is made, move it from "open" to "resolved" with the answer (keep a short log; don't silently delete).
4. **Be concise and structured.** Tables for comparisons, bullets over prose, bold the takeaway. Write for a skimmer.
5. **Stamp sources/dates** on facts that can change.
6. **Commit** with a clear message.

## Presenting planning (humans + agents)
- Lead with the goal / north-star metric and current status.
- Show the decomposition (goal → quarter → week) and where things stand.
- Every action carries an owner + a status marker. No walls of text.

## Rendering (Obsidian Mermaid gotchas)
- **Never start a node label with `N. `** (e.g. `["1. Step"]`) — parsed as an ordered list and fails. Drop the number or move it to the end.
- **One edge per line.** Avoid `A & B & C --> D` chains; older bundled renderers choke on `&`.
- **`gantt` is fragile with non-Latin text:** use plain `name :YYYY-MM-DD, Nd`; strip quotes, `+`, and parentheses.
- Inside a quoted label, avoid a raw ASCII `"` (it terminates the string early).
- Labels in any language/RTL are fine; keep them short.

## Portability
- **No hardcoded paths.** Detect the vault root (the folder containing `.obsidian/`); if unknown, ask once, then remember.
- **Domain-agnostic.** Works for any project; assume nothing beyond Home + concept notes + a weekly cadence.
- **Self-contained.** Needs only a filesystem and git — no external services.
