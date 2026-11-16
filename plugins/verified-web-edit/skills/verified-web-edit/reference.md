# Verified web edit: reference

Contents: Browser tools · Irreversible actions · Editor pitfalls · Compare against intent · Views and limits · Restore.

## Browser tools

The loop needs five capabilities. Map them to whatever tool is connected; load that tool's own skill for its setup, permissions and dialogs.

| Need | Claude in Chrome (`mcp__claude-in-chrome__*`) | Playwright-style MCP | Any tool |
|---|---|---|---|
| Fresh load by URL | `tabs_create_mcp` + `navigate` | `browser_navigate` | open a new tab at the URL |
| Read page text | `get_page_text` | `browser_snapshot` | page-as-text read |
| Read structure (links, media, controls) | `read_page`, `find` | `browser_snapshot` | accessibility tree or DOM read |
| Act | `computer` (click, type), `form_input` | `browser_click`, `browser_type` | click and type |
| Evidence | `computer` screenshot, `read_network_requests` (did the save request succeed) | `browser_take_screenshot`, `browser_network_requests` | screenshot |

- Read-only scripting (listing every `href`, counting `<video>`/`<iframe>` elements) is a fast audit; it never changes the page.
- Work in a new tab you opened; leave the user's existing tabs alone.
- File uploads: support differs by tool and host. If the tool cannot attach the file, the user uploads it by hand and you inspect the saved result. The presence of a local file is not evidence of an upload.

## Irreversible actions

Confirm each with the user before acting, unless the log records a pre-approval naming that action and those pages.

- Publish, unpublish, schedule, or change draft/published state.
- Delete anything: page, block, media, attachment, comment, version.
- Notify: "notify members", "email subscribers", "post to feed", "send update" checkboxes and buttons. Leave them unchecked unless the change calls for them.
- Change a URL slug, page ID, redirect or canonical (breaks inbound links).
- Change access, visibility, pricing, enrolment, or permissions.
- Replace media (a new upload usually discards the old file and its stats).
- Bulk actions and "apply to all".
- Anything behind a dialog that says it cannot be undone.

## Editor pitfalls

- **Separate controls, separate data.** Body text, the media player, attachments and discussion are often stored apart. A "remove" or "clear" next to the body can delete the video, not the text.
- **Rich-text editors** (contenteditable) may ignore programmatic value setting; type through the editor or paste, then confirm the editor registered the change (save button enabled, "unsaved changes" shown).
- **Formatting loss.** Retyping a paragraph can drop links, bold, or line breaks. Replace the smallest span that holds the change.
- **Auto-linking.** Editors turn bare filenames and domains (`CLAUDE.md`, `example.com`) into links. Format them as code when the platform supports it, and check the saved result.
- **Markdown is not always Markdown.** Pasted `**bold**` may stay literal. Check the rendered page.
- **Autosave vs explicit save.** Know which one the platform uses; with autosave, wait for its saved indicator before leaving.
- **Caching.** A reopen can serve a cached copy. Load in a new tab; if the page shows a version or updated time, compare it.
- **Version history.** If the platform keeps revisions, note where in the audit: it is the cheapest restore path.

## Compare against intent

For each page, after the fresh reopen:

1. **Changed text**: the rendered text equals the approved replacement (normalise whitespace only), in the right place, with the surrounding paragraph intact.
2. **Links**: the set of link destinations equals the audit's, except links the change meant to alter. A changed tracking parameter is noted separately from a changed destination. Follow each changed link once.
3. **Media and resources**: same count and identity (title, ID or source URL) as the audit; players load.
4. **Discussion and attribution**: still present.
5. **State**: draft/published state, visibility and URL unchanged unless approved.
6. **Nothing extra**: no stray characters, duplicated blocks, or empty paragraphs where the edit happened.

Each check is `pass`, `fail: <what differs>`, or `unknown: <why not inspectable>`. A page row is `pass` only when every check passed.

## Views and limits

What one view proves is limited. State the gap in the summary, or close it when it matters for the page's readers:
- An editor or admin view does not prove what a member, customer or logged-out visitor sees (access rules, paywalls, drip schedules). Use the platform's "view as" or preview-as-member, or ask the user to check from a member account.
- A resource listed on the admin page does not prove a member can download it.
- Desktop does not prove mobile layout; resize the window or use the tool's viewport control when layout is in scope.
- A save confirmation, a scheduled job, or a saved checklist is not evidence that the page changed.

## Restore

The saved original from the audit is the restore source. Restoring is a change: propose it (current = the bad saved state, replacement = the original), get approval, apply, reopen and compare, and log it as its own row. Prefer the platform's version history when it exists, since it restores formatting and media references a text copy cannot.
