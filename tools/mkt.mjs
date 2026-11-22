#!/usr/bin/env node
// mkt — marketplace toolkit for the dorbar-skills marketplace.
//
// Subcommands:
//   mkt new <name> [--bundle] [--skill <skill>] [--desc "..."]   scaffold a plugin
//   mkt sync                                                     regenerate marketplace.json from plugin manifests
//   mkt status                                                   show versions and whether each is tagged
//   mkt lint-title [<title>]                                     check a PR title is <type>(<scope>)!: <summary>
//   mkt version [--title "..."] [--base <ref>] [--check]         set plugin + marketplace versions from the PR title and changed files
//   mkt tag [--push]                                             tag every untagged current version (CI runs it on main)
//   mkt validate                                                 validate manifests + run `claude plugin validate`
//   mkt install-hooks                                            install the commit-msg hook (conventional-commit lint)
//   mkt vendor [--diff] | vendor update [--to <sha>]             check/update vendored files (vendor.json); --diff prints forks vs upstream
//
// Design: each plugin's `.claude-plugin/plugin.json` is the source of truth.
// marketplace.json's plugins[] is generated; never hand-edit plugin entries.

import { readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync, cpSync, statSync, renameSync, rmSync, chmodSync } from "node:fs";
import { join, dirname, basename, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const PLUGINS_DIR = join(ROOT, "plugins");
const TEMPLATES_DIR = join(ROOT, "templates");
const MARKETPLACE_PATH = join(ROOT, ".claude-plugin", "marketplace.json");
const ROOT_CHANGELOG = join(ROOT, "CHANGELOG.md");

// ---------- tiny utils ----------
const c = { dim: s => `\x1b[2m${s}\x1b[0m`, grn: s => `\x1b[32m${s}\x1b[0m`, yel: s => `\x1b[33m${s}\x1b[0m`, red: s => `\x1b[31m${s}\x1b[0m`, bold: s => `\x1b[1m${s}\x1b[0m` };
function die(msg) { console.error(c.red("error: ") + msg); process.exit(1); }
function readJSON(p) { return JSON.parse(readFileSync(p, "utf8")); }
function writeJSON(p, obj) { writeFileSync(p, JSON.stringify(obj, null, 2) + "\n"); }
function git(args, opts = {}) {
  // stdio captures stderr so git's diagnostics (e.g. "bad revision HEAD" on an
  // empty repo) don't leak to our output; failures surface via the thrown error.
  try { return execFileSync("git", args, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], ...opts }).trim(); }
  catch (e) { if (opts.allowFail) return ""; throw e; }
}
function hasGit() { return existsSync(join(ROOT, ".git")); }

// ---------- semver ----------
function parseVer(v) {
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec(String(v || "0.0.0"));
  if (!m) return null;
  return { major: +m[1], minor: +m[2], patch: +m[3] };
}
function bumpVer(v, level) {
  const p = parseVer(v) || { major: 0, minor: 0, patch: 0 };
  if (level === "major") return `${p.major + 1}.0.0`;
  if (level === "minor") return `${p.major}.${p.minor + 1}.0`;
  return `${p.major}.${p.minor}.${p.patch + 1}`;
}
const LEVEL_RANK = { patch: 1, minor: 2, major: 3 };
function maxLevel(a, b) { if (!a) return b; if (!b) return a; return LEVEL_RANK[a] >= LEVEL_RANK[b] ? a : b; }
function cmpVerDesc(a, b) {
  const pa = parseVer(a), pb = parseVer(b);
  return (pb.major - pa.major) || (pb.minor - pa.minor) || (pb.patch - pa.patch);
}

// ---------- plugins ----------
function listPlugins() {
  if (!existsSync(PLUGINS_DIR)) return [];
  return readdirSync(PLUGINS_DIR)
    .filter(name => {
      const dir = join(PLUGINS_DIR, name);
      return statSync(dir).isDirectory() && existsSync(join(dir, ".claude-plugin", "plugin.json"));
    })
    .map(name => {
      const dir = join(PLUGINS_DIR, name);
      const manifestPath = join(dir, ".claude-plugin", "plugin.json");
      return { name, dir, manifestPath, manifest: readJSON(manifestPath) };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

// Release tags are <plugin>-v<version> (e.g. layered-context-v0.1.0): one "@"-free ref that works in
// git URLs (uvx/pipx "git+https://...@<ref>") and in GitHub Actions `uses: ...@<ref>`.
const tagFor = (name, version) => `${name}-v${version}`;

function pyprojectsIn(dir) {
  const out = [];
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith(".") || ["node_modules", "build"].includes(e.name)) continue;
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...pyprojectsIn(p));
    else if (e.name === "pyproject.toml") out.push(p);
  }
  return out;
}
const PY_VERSION = /^version\s*=\s*"([^"]*)"/m;
function setPyprojectVersion(file, version) {
  writeFileSync(file, readFileSync(file, "utf8").replace(PY_VERSION, `version = "${version}"`));
}

// ---------- marketplace sync ----------
function syncMarketplace({ quiet } = {}) {
  const mkt = readJSON(MARKETPLACE_PATH);
  const plugins = listPlugins().map(({ name, manifest }) => {
    // Explicit path from the marketplace root. Claude Code resolves a "./"-prefixed
    // source against the marketplace root (NOT metadata.pluginRoot), so spell it out.
    const entry = { name, source: `./plugins/${name}` };
    if (manifest.description) entry.description = manifest.description;
    if (manifest.version) entry.version = manifest.version;
    if (manifest.author) entry.author = manifest.author;
    if (manifest.keywords && manifest.keywords.length) entry.keywords = manifest.keywords;
    if (manifest.category) entry.category = manifest.category;
    if (manifest.homepage) entry.homepage = manifest.homepage;
    if (manifest.license) entry.license = manifest.license;
    return entry;
  });
  mkt.plugins = plugins;
  writeJSON(MARKETPLACE_PATH, mkt);
  if (!quiet) console.log(c.grn("synced ") + `marketplace.json — ${plugins.length} plugin(s)`);
  return mkt;
}

// ---------- changelog ----------
function prependChangelog(file, version, lines, fallbackTitle) {
  const date = new Date().toISOString().slice(0, 10);
  const block = `## [${version}] - ${date}\n\n${(lines.length ? lines : [`- ${fallbackTitle}`]).join("\n")}\n`;
  if (!existsSync(file)) {
    writeFileSync(file, `# Changelog\n\n${block}`);
    return;
  }
  const cur = readFileSync(file, "utf8");
  const idx = cur.indexOf("\n## ");
  if (idx === -1) {
    // no prior release section; insert after the first header paragraph
    const headerEnd = cur.indexOf("\n\n");
    const head = headerEnd === -1 ? cur + "\n" : cur.slice(0, headerEnd + 2);
    writeFileSync(file, head + block + "\n" + (headerEnd === -1 ? "" : cur.slice(headerEnd + 2)));
  } else {
    writeFileSync(file, cur.slice(0, idx + 1) + block + "\n" + cur.slice(idx + 1));
  }
}

// ---------- commands ----------
function cmdNew(args) {
  const flags = parseFlags(args);
  const name = flags._[0];
  if (!name) die("usage: mkt new <name> [--bundle] [--skill <skill>] [--desc \"...\"]");
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) die("plugin name must be kebab-case (a-z, 0-9, -)");
  const dest = join(PLUGINS_DIR, name);
  if (existsSync(dest)) die(`plugin already exists: ${dest}`);
  const tplName = flags.bundle ? "bundle-plugin" : "skill-plugin";
  const tpl = join(TEMPLATES_DIR, tplName);
  const skill = flags.skill || (flags.bundle ? "first-skill" : name);
  const desc = flags.desc || "TODO: one-line description ending with when to use it.";

  cpSync(tpl, dest, { recursive: true });
  // rename the placeholder skill dir
  const skillsDir = join(dest, "skills");
  const placeholder = join(skillsDir, "__SKILL__");
  if (existsSync(placeholder)) renameSync(placeholder, join(skillsDir, skill));
  // fill placeholders in manifest + skill + changelog
  replaceInFile(join(dest, ".claude-plugin", "plugin.json"), { __NAME__: name, __DESCRIPTION__: desc });
  replaceInFile(join(skillsDir, skill, "SKILL.md"), { __SKILL__: skill, __DESCRIPTION__: desc });

  syncMarketplace({ quiet: true });
  console.log(c.grn("created ") + `plugins/${name}/  (${flags.bundle ? "bundle" : "standalone"}, skill: ${skill})`);
  console.log(c.dim("  edit:  ") + `plugins/${name}/skills/${skill}/SKILL.md`);
  console.log(c.dim("  next:  ") + `git add -A && git commit -m "feat(${name}): add ${skill} skill"`);
}

function replaceInFile(file, map) {
  let s = readFileSync(file, "utf8");
  for (const [k, v] of Object.entries(map)) s = s.split(k).join(v);
  writeFileSync(file, s);
}

// ---------- semantic PR titles ----------
// Merges are squash-only with the PR title as the commit title, so the PR title alone decides the
// bump: <type>(<scope>)!: <summary>. The scope is the plugin name (comma-separate several, or omit it).
const TITLE = /^(feat|fix|perf|refactor|revert|docs|style|test|build|ci|chore)(\(([a-z0-9-]+(?:,[a-z0-9-]+)*)\))?(!)?: \S.*$/;
const TYPE_LEVEL = { feat: "minor", fix: "patch", perf: "patch", refactor: "patch", revert: "patch" };
const TITLE_HELP = `PR title must be <type>(<scope>)!: <summary>, e.g.
    fix(layered-context): skip non-path Inputs tokens      -> patch
    feat(agent-workflows): add a bounded-loop skill        -> minor
    feat(layered-context)!: rename the Inputs heading      -> major (! = breaking)
  types: feat fix perf refactor revert docs style test build ci chore; scope = plugin name(s), optional`;

function parseTitle(title) {
  const m = TITLE.exec(String(title || "").trim());
  if (!m) return null;
  return { type: m[1], scopes: m[3] ? m[3].split(",") : [], breaking: !!m[4], level: m[4] ? "major" : TYPE_LEVEL[m[1]] || null };
}

function prTitle(flags) {
  if (typeof flags.title === "string") return flags.title;
  if (process.env.PR_TITLE) return process.env.PR_TITLE;
  try {
    return execFileSync("gh", ["pr", "view", "--json", "title", "-q", ".title"], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  } catch { die('no PR for this branch yet - pass the title you will use: --title "fix(<plugin>): ..."'); }
}

function cmdLintTitle(args) {
  const flags = parseFlags(args);
  const title = flags._.length ? flags._.join(" ") : prTitle(flags);
  const t = parseTitle(title);
  if (!t) { console.error(c.red(`✗ "${title}"\n`) + TITLE_HELP); process.exit(1); }
  console.log(c.grn(`✓ ${title}`) + c.dim(` (${t.level || "no release level; plugin changes still ship as patch"})`));
}

// ---------- versions from the PR (mkt version) ----------
function showAt(ref, rel) { return git(["show", `${ref}:${rel}`], { allowFail: true }); }
function jsonAt(ref, rel) { try { return JSON.parse(showAt(ref, rel) || "null"); } catch { return null; } }

// A file the version step itself writes counts as changed only when more than its version moved.
function realChange(rel, mb) {
  if (rel.endsWith("/CHANGELOG.md")) return false;
  const before = showAt(mb, rel);
  if (!before || !existsSync(join(ROOT, rel))) return true;
  const now = readFileSync(join(ROOT, rel), "utf8");
  if (rel.endsWith(".claude-plugin/plugin.json")) {
    const strip = s => { try { const o = JSON.parse(s); delete o.version; return JSON.stringify(o); } catch { return s; } };
    return strip(before) !== strip(now);
  }
  if (rel.endsWith("pyproject.toml")) return before.replace(PY_VERSION, "") !== now.replace(PY_VERSION, "");
  return true;
}

function versionPlan(flags) {
  if (!hasGit()) die("version needs a git repository");
  const title = prTitle(flags);
  const t = parseTitle(title);
  if (!t) die(`"${title}"\n${TITLE_HELP}`);
  const base = typeof flags.base === "string" ? flags.base : "origin/main";
  const mb = git(["merge-base", base, "HEAD"], { allowFail: true });
  if (!mb) die(`no merge base with ${base} (fetch it first: git fetch origin main)`);
  // committed + uncommitted + untracked changes since the merge base
  const changed = [...new Set([
    ...git(["diff", "--name-only", mb]).split("\n"),
    ...git(["ls-files", "--others", "--exclude-standard"]).split("\n"),
  ].filter(Boolean))];
  const level = maxLevel(t.level, "patch"); // a plugin's files are what users install: any change ships
  const plugins = listPlugins().map(p => {
    const rel = relative(ROOT, p.dir) + "/";
    const files = changed.filter(f => f.startsWith(rel) && realChange(f, mb));
    const before = jsonAt(mb, relative(ROOT, p.manifestPath))?.version ?? null;
    if (before === null) return { p, before, expected: p.manifest.version, files, isNew: true, level: null };
    return { p, before, files, expected: files.length ? bumpVer(before, level) : before, level: files.length ? level : null };
  });
  const touched = plugins.filter(x => x.files.length || x.isNew);
  const mktBefore = jsonAt(mb, relative(ROOT, MARKETPLACE_PATH))?.version ?? readJSON(MARKETPLACE_PATH).version;
  const market = { before: mktBefore, expected: touched.length ? bumpVer(mktBefore, level) : mktBefore };
  for (const s of t.scopes) if (listPlugins().some(p => p.name === s) && !touched.some(x => x.p.name === s))
    console.log(c.yel(`! scope "${s}" names a plugin this PR does not change`));
  return { title, t, level, plugins, touched, market };
}

// Drop sections this PR wrote for other versions (above the base); keep an existing section for
// `version` (it may carry hand-written notes) unless `replace`; otherwise write it.
function writeChangelog(file, before, version, lines, { replace = false } = {}) {
  let exists = false;
  if (existsSync(file)) {
    const parts = readFileSync(file, "utf8").split(/(?=^## \[)/m);
    const keep = parts.filter(s => {
      const m = /^## \[([^\]]+)\]/.exec(s);
      if (!m || !parseVer(m[1]) || !before || cmpVerDesc(before, m[1]) <= 0) return true;
      if (m[1] === version && !replace) { exists = true; return true; }
      return false;
    });
    writeFileSync(file, keep.join(""));
  }
  if (!exists && version !== before) prependChangelog(file, version, lines, "Release.");
}

function cmdVersion(args) {
  const flags = parseFlags(args);
  const plan = versionPlan(flags);
  const rows = plan.plugins.filter(x => x.files.length || x.isNew || x.p.manifest.version !== x.before);
  if (flags.check) {
    let ok = true;
    const bad = (msg) => { console.error(c.red("✗ " + msg)); ok = false; };
    for (const x of plan.plugins) {
      if (x.p.manifest.version !== x.expected)
        bad(`${x.p.name}: version ${x.p.manifest.version}, expected ${x.expected}` + (x.files.length ? ` (${x.files.length} file(s) changed, ${x.level})` : " (unchanged in this PR)"));
      for (const py of pyprojectsIn(x.p.dir)) {
        const v = (readFileSync(py, "utf8").match(PY_VERSION) || [])[1];
        if (v !== x.expected) bad(`${relative(ROOT, py)}: version ${v}, expected ${x.expected}`);
      }
      if (x.files.length && !x.isNew && !readFileSync(join(x.p.dir, "CHANGELOG.md"), "utf8").includes(`## [${x.expected}]`))
        bad(`${x.p.name}: CHANGELOG.md has no [${x.expected}] section`);
    }
    const mkt = readJSON(MARKETPLACE_PATH);
    if (mkt.version !== plan.market.expected) bad(`marketplace.json: version ${mkt.version}, expected ${plan.market.expected}`);
    for (const x of plan.plugins) {
      const e = (mkt.plugins || []).find(e => e.name === x.p.name);
      if (!e || e.version !== x.p.manifest.version) bad(`marketplace.json entry for ${x.p.name} is out of sync with plugin.json`);
    }
    if (!ok) { console.error(`  fix: ./bin/mkt version --title "${plan.title}" && commit the result`); process.exit(1); }
    console.log(c.grn(`✓ versions match "${plan.title}"`) + c.dim(` (${plan.touched.length} plugin(s) changed)`));
    return;
  }
  for (const x of plan.plugins) {
    if (x.isNew || x.p.manifest.version === x.expected && !x.files.length) continue;
    x.p.manifest.version = x.expected;
    writeJSON(x.p.manifestPath, x.p.manifest);
    for (const py of pyprojectsIn(x.p.dir)) setPyprojectVersion(py, x.expected);
    const log = join(x.p.dir, "CHANGELOG.md");
    if (x.files.length) writeChangelog(log, x.before, x.expected, [`- ${plan.title}`]);
    else writeChangelog(log, x.before, x.before, []); // reverted: drop this PR's section only
  }
  const mkt = readJSON(MARKETPLACE_PATH);
  mkt.version = plan.market.expected;
  writeJSON(MARKETPLACE_PATH, mkt);
  syncMarketplace({ quiet: true });
  if (plan.touched.length)
    writeChangelog(ROOT_CHANGELOG, plan.market.before, plan.market.expected,
      plan.touched.map(x => `- **${x.p.name}** ${x.expected}${x.isNew ? " (new)" : ` (${x.level})`}`), { replace: true });
  for (const x of rows) console.log(`  ${x.p.name.padEnd(26)} ${x.before ?? "new"} → ${c.grn(x.expected)}`);
  console.log(`  ${"marketplace".padEnd(26)} ${plan.market.before} → ${c.grn(plan.market.expected)}`);
  console.log(c.dim("  commit these files with the PR; CI runs mkt version --check"));
}

// ---------- tags (after merge, on main) ----------
function cmdTag(args) {
  const flags = parseFlags(args);
  if (!hasGit()) die("tag needs a git repository");
  const want = [...listPlugins().map(p => tagFor(p.name, p.manifest.version)), `marketplace-v${readJSON(MARKETPLACE_PATH).version}`];
  const have = new Set(git(["tag", "--list"]).split("\n"));
  const made = want.filter(t => !have.has(t));
  if (!made.length) { console.log(c.dim("every current version is already tagged")); return; }
  for (const t of made) git(["tag", t]);
  if (flags.push) git(["push", "origin", ...made.map(t => `refs/tags/${t}`)]);
  console.log(c.grn("tagged ") + made.join(", ") + (flags.push ? "" : c.dim("  (push with: git push origin --tags)")));
}

function cmdStatus() {
  const have = new Set(hasGit() ? git(["tag", "--list"]).split("\n") : []);
  console.log(c.bold("plugin".padEnd(28)) + c.bold("version".padEnd(12)) + c.bold("tag"));
  for (const p of listPlugins()) {
    const t = tagFor(p.name, p.manifest.version);
    console.log(p.name.padEnd(28) + String(p.manifest.version || "—").padEnd(12) + (have.has(t) ? c.dim(t) : c.yel("untagged")));
  }
}

function cmdValidate() {
  let ok = true;
  const mkt = readJSON(MARKETPLACE_PATH);
  if (!mkt.name || !mkt.owner || !mkt.owner.name) { console.error(c.red("✗ marketplace.json missing name/owner")); ok = false; }
  const listed = new Set((mkt.plugins || []).map(p => p.name));
  const plugins = listPlugins();
  for (const p of plugins) {
    if (!p.manifest.name) { console.error(c.red(`✗ ${p.name}: plugin.json missing name`)); ok = false; }
    if (p.manifest.name !== p.name) { console.error(c.red(`✗ ${p.name}: plugin.json name "${p.manifest.name}" != directory`)); ok = false; }
    if (p.manifest.version && !parseVer(p.manifest.version)) { console.error(c.red(`✗ ${p.name}: invalid version "${p.manifest.version}"`)); ok = false; }
    for (const py of pyprojectsIn(p.dir)) {
      const v = (readFileSync(py, "utf8").match(PY_VERSION) || [])[1];
      if (v !== p.manifest.version) { console.error(c.red(`✗ ${p.name}: ${relative(ROOT, py)} version "${v}" != plugin.json "${p.manifest.version}"`)); ok = false; }
    }
    if (!listed.has(p.name)) { console.error(c.yel(`! ${p.name}: not in marketplace.json (run: mkt sync)`)); }
    const entry = (mkt.plugins || []).find(e => e.name === p.name);
    if (entry && entry.version !== p.manifest.version) { console.error(c.red(`✗ ${p.name}: marketplace.json version "${entry.version}" != plugin.json "${p.manifest.version}" (run: mkt sync)`)); ok = false; }
  }
  // delegate deep validation to claude CLI if present
  try {
    const out = execFileSync("claude", ["plugin", "validate", "."], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    if (out.trim()) console.log(c.dim(out.trim()));
  } catch (e) {
    const msg = (e.stdout || "") + (e.stderr || "");
    if (msg.trim()) { console.error(c.red(msg.trim())); ok = false; }
    else console.log(c.dim("(claude plugin validate unavailable — skipped deep validation)"));
  }
  console.log(ok ? c.grn("✓ validation passed") : c.red("✗ validation failed"));
  process.exit(ok ? 0 : 1);
}

// ---------- vendored third-party files (vendor.json) ----------
const VENDOR_PATH = join(ROOT, "vendor.json");
const OUR_HEADER = /^# (From |Adapted for )/;

async function fetchText(url) {
  const r = await fetch(url, { headers: { "User-Agent": "mkt-vendor" } });
  if (!r.ok) throw new Error(`${r.status} ${url}`);
  return r.text();
}
const rawUrl = (repo, sha, path) => `https://raw.githubusercontent.com/${repo}/${sha}/${path}`;
// our copy minus our attribution header (header lines sit right after the shebang)
function stripHeader(text) {
  const lines = text.split("\n");
  const start = lines[0]?.startsWith("#!") ? 1 : 0;
  return [...lines.slice(0, start), ...lines.slice(start + headerOf(text).length)].join("\n");
}
function withHeader(upstream, headerLines) {
  const lines = upstream.split("\n");
  const at = lines[0]?.startsWith("#!") ? 1 : 0;
  return [...lines.slice(0, at), ...headerLines, ...lines.slice(at)].join("\n");
}
function headerOf(text) {
  const lines = text.split("\n");
  const start = lines[0]?.startsWith("#!") ? 1 : 0;
  const out = [];
  for (let i = start; i < lines.length && OUR_HEADER.test(lines[i]); i++) out.push(lines[i]);
  return out;
}

// unified diff of upstream (pinned) vs our copy, via git (no index needed)
function printDiff(upstream, ours, aLabel, bLabel) {
  const dir = join(ROOT, "node_modules", ".mkt-vendor-diff");
  mkdirSync(dir, { recursive: true });
  const a = "__upstream__", b = "__ours__";
  writeFileSync(join(dir, a), upstream); writeFileSync(join(dir, b), ours);
  try {
    execFileSync("git", ["diff", "--no-index", "--no-color", "--src-prefix=", "--dst-prefix=", a, b], { cwd: dir, encoding: "utf8" });
  } catch (e) {
    console.log((e.stdout || "").split(a).join(aLabel).split(b).join(bLabel).replace(/^index .*\n/m, "").replace(/^/gm, "    "));
  } finally { rmSync(dir, { recursive: true, force: true }); }
}

async function cmdVendor(args) {
  const flags = parseFlags(args);
  const update = flags._[0] === "update";
  const showDiff = !!flags.diff;
  if (flags._[0] && !update) die("usage: mkt vendor [--diff] | mkt vendor update [--to <sha>]");
  const manifest = readJSON(VENDOR_PATH);
  let problems = 0;
  for (const src of manifest.sources) {
    const head = JSON.parse(await fetchText(`https://api.github.com/repos/${src.repo}/commits/HEAD`)).sha;
    const target = update ? (flags.to || head) : src.commit;
    console.log(c.bold(src.name) + c.dim(` ${src.repo}  pinned ${src.commit.slice(0, 7)}  upstream HEAD ${head.slice(0, 7)}`));
    for (const f of src.files) {
      const pinned = await fetchText(rawUrl(src.repo, src.commit, f.path));
      const latest = head === src.commit ? pinned : await fetchText(rawUrl(src.repo, head, f.path)).catch(() => null);
      const moved = latest !== pinned;
      for (const copy of f.copies) {
        const ours = readFileSync(join(ROOT, copy), "utf8");
        const same = stripHeader(ours) === pinned;
        let state = f.fork ? c.yel("fork") : same ? c.grn("matches pin") : c.red("edited locally");
        if (!f.fork && !same) problems++;
        if (moved) state += c.yel(latest === null ? "  (removed upstream at HEAD)" : "  (changed upstream since pin)");
        if (update && !f.fork && target !== src.commit) {
          const next = await fetchText(rawUrl(src.repo, target, f.path));
          writeFileSync(join(ROOT, copy), withHeader(next, headerOf(ours)));
          state = c.grn(`updated to ${target.slice(0, 7)}`);
        }
        console.log(`  ${f.path} -> ${copy}  ${state}`);
        if (showDiff && !same) printDiff(pinned, ours, `${src.repo}@${src.commit.slice(0, 7)}:${f.path}`, copy);
      }
      if (f.fork && moved) console.log(c.dim(`    fork: ${f.fork}; review upstream changes by hand`));
    }
    if (update && target !== src.commit) {
      src.commit = target;
      writeJSON(VENDOR_PATH, manifest);
      console.log(c.dim("  review with: git diff -- plugins vendor.json"));
    }
  }
  if (problems) { console.error(c.red(`✗ ${problems} vendored copy(ies) differ from the pinned upstream; mark as fork or restore`)); process.exit(1); }
}

function cmdInstallHooks() {
  if (!hasGit()) die("not a git repo");
  const hook = join(ROOT, ".git", "hooks", "commit-msg");
  const script = `#!/bin/sh
# conventional-commit lint (installed by: mkt install-hooks)
msg=$(head -1 "$1")
case "$msg" in
  "Merge "*|"Revert "*|fixup!*|squash!*) exit 0 ;;
esac
echo "$msg" | grep -Eq '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\\([a-z0-9-]+(,[a-z0-9-]+)*\\))?!?: .+' && exit 0
echo "✗ commit message must follow Conventional Commits, e.g.:" >&2
echo "    feat(my-skill): add OCR support" >&2
echo "    fix(my-skill): handle empty input" >&2
exit 1
`;
  writeFileSync(hook, script);
  chmodSync(hook, 0o755);
  console.log(c.grn("installed ") + ".git/hooks/commit-msg (conventional-commit lint)");
}

function parseFlags(args) {
  const out = { _: [] };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      if (i + 1 < args.length && !args[i + 1].startsWith("--")) out[key] = args[++i];
      else out[key] = true;
    } else out._.push(a);
  }
  return out;
}

const HELP = `mkt — dorbar-skills marketplace toolkit

  mkt new <name> [--bundle] [--skill <skill>] [--desc "..."]   scaffold a plugin
  mkt sync                                                     regenerate marketplace.json from manifests
  mkt status                                                   show versions and whether each is tagged
  mkt lint-title [<title>]                                     check a PR title: <type>(<scope>)!: <summary>
  mkt version [--title "..."] [--base <ref>] [--check]         versions from the PR title + changed files (--check: CI verify)
  mkt tag [--push]                                             tag every untagged current version (CI, on main)
  mkt validate                                                 validate manifests + claude plugin validate
  mkt install-hooks                                            install commit-msg conventional-commit lint
  mkt vendor [--diff] | vendor update [--to <sha>]             check vendored files against upstream (vendor.json); --diff shows each fork
`;

const [cmd, ...rest] = process.argv.slice(2);
switch (cmd) {
  case "new": cmdNew(rest); break;
  case "sync": syncMarketplace(); break;
  case "status": cmdStatus(); break;
  case "lint-title": cmdLintTitle(rest); break;
  case "version": cmdVersion(rest); break;
  case "tag": cmdTag(rest); break;
  case "validate": cmdValidate(); break;
  case "install-hooks": cmdInstallHooks(); break;
  case "vendor": await cmdVendor(rest); break;
  case undefined: case "help": case "--help": case "-h": console.log(HELP); break;
  default: die(`unknown command: ${cmd}\n\n${HELP}`);
}
