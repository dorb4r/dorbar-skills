#!/usr/bin/env node
// mkt - marketplace toolkit for the dorbar-skills marketplace.
//
// Subcommands:
//   mkt new <name> [--bundle] [--skill <skill>] [--desc "..."]   scaffold a plugin
//   mkt sync                                                     regenerate marketplace.json from plugin manifests
//   mkt status                                                   show versions + pending conventional-commit bumps
//   mkt release [--dry-run] [--plugin <name>] [--no-git]         auto-bump from Conventional Commits, sync, tag
//   mkt bump <plugin> <patch|minor|major>                       manual single-plugin bump
//   mkt validate                                                 validate manifests + run `claude plugin validate`
//   mkt install-hooks                                            install the commit-msg hook (conventional-commit lint)
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
const PACKAGE_PATH = join(ROOT, "package.json");
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

// ---------- conventional commits ----------
// Returns { level, lines } where level is patch|minor|major|null and lines are changelog bullets.
function classifyCommits(commits) {
  let level = null;
  const lines = [];
  for (const { subject, body } of commits) {
    const m = /^(\w+)(\([^)]*\))?(!)?:\s*(.+)$/.exec(subject);
    const breaking = (m && m[3] === "!") || /BREAKING[ -]CHANGE/.test(body);
    let l = null, type = m ? m[1].toLowerCase() : null;
    if (breaking) l = "major";
    else if (type === "feat") l = "minor";
    else if (type === "fix" || type === "perf" || type === "refactor" || type === "revert") l = "patch";
    // docs/chore/style/test/ci/build => no release contribution
    level = maxLevel(level, l);
    if (l || breaking) lines.push(`- ${subject}`);
  }
  return { level, lines };
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

function lastTagFor(name) {
  if (!hasGit()) return null;
  const tags = git(["tag", "--list", `${name}@*`], { allowFail: true }).split("\n").filter(Boolean)
    .map(t => t.slice(name.length + 1))
    .filter(v => parseVer(v))
    .sort(cmpVerDesc);
  return tags.length ? `${name}@${tags[0]}` : null;
}

function commitsTouching(dir, sinceTag) {
  if (!hasGit()) return [];
  const range = sinceTag ? `${sinceTag}..HEAD` : "HEAD";
  const SEP = "\x1e", FLD = "\x1f";
  const out = git(["log", `--format=%s${FLD}%b${SEP}`, range, "--", relative(ROOT, dir)], { allowFail: true });
  return out.split(SEP).map(s => s.trim()).filter(Boolean).map(rec => {
    const [subject, body = ""] = rec.split(FLD);
    return { subject: subject.trim(), body: body.trim() };
  });
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
  if (!quiet) console.log(c.grn("synced ") + `marketplace.json - ${plugins.length} plugin(s)`);
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

function cmdStatus() {
  const plugins = listPlugins();
  if (!plugins.length) { console.log(c.dim("no plugins yet - scaffold one with: mkt new <name>")); return; }
  console.log(c.bold("plugin".padEnd(28)) + c.bold("version".padEnd(12)) + c.bold("pending bump"));
  for (const p of plugins) {
    const tag = lastTagFor(p.name);
    const commits = commitsTouching(p.dir, tag);
    const { level } = classifyCommits(commits);
    const note = !hasGit() ? c.dim("(no git)")
      : !tag ? c.yel("unreleased") + c.dim(` (${commits.length} commit(s))`)
      : level ? c.yel(level) + c.dim(` → ${bumpVer(p.manifest.version, level)}`) + c.dim(` (${commits.length} commit(s))`)
      : c.dim("none");
    console.log((p.name).padEnd(28) + String(p.manifest.version || "-").padEnd(12) + note);
  }
}

function cmdBump(args) {
  const [name, level] = args;
  if (!name || !["patch", "minor", "major"].includes(level)) die("usage: mkt bump <plugin> <patch|minor|major>");
  const p = listPlugins().find(x => x.name === name);
  if (!p) die(`no such plugin: ${name}`);
  const from = p.manifest.version || "0.0.0";
  const to = bumpVer(from, level);
  p.manifest.version = to;
  writeJSON(p.manifestPath, p.manifest);
  prependChangelog(join(p.dir, "CHANGELOG.md"), to, [], `Manual ${level} bump.`);
  syncMarketplace();
  console.log(c.grn("bumped ") + `${name} ${from} → ${to}`);
}

function cmdRelease(args) {
  const flags = parseFlags(args);
  if (!hasGit()) die("release needs a git repository (run `git init` and commit first)");
  const only = flags.plugin;
  const plugins = listPlugins().filter(p => !only || p.name === only);
  if (!plugins.length) die(only ? `no such plugin: ${only}` : "no plugins to release");

  const changes = [];
  for (const p of plugins) {
    const tag = lastTagFor(p.name);
    const commits = commitsTouching(p.dir, tag);
    const { level, lines } = classifyCommits(commits);
    if (!tag) {
      // first release: establish baseline at the manifest's current version, no bump.
      changes.push({ p, from: p.manifest.version, to: p.manifest.version, level: "baseline", lines, baseline: true });
      continue;
    }
    if (!level) continue; // nothing release-worthy
    const to = bumpVer(p.manifest.version, level);
    changes.push({ p, from: p.manifest.version, to, level, lines });
  }

  if (!changes.length) { console.log(c.dim("nothing to release.")); return; }

  let marketLevel = null;
  for (const ch of changes) if (!ch.baseline) marketLevel = maxLevel(marketLevel, ch.level);

  const packageManifest = readJSON(PACKAGE_PATH);
  const marketFrom = packageManifest.version || "0.0.0";
  const marketTo = marketLevel ? bumpVer(marketFrom, marketLevel) : marketFrom;

  console.log(c.bold(flags["dry-run"] ? "DRY RUN - planned release:" : "Releasing:"));
  for (const ch of changes) {
    console.log(`  ${ch.p.name.padEnd(26)} ${ch.from} → ${c.grn(ch.to)} ${ch.baseline ? c.dim("(baseline tag)") : c.dim(`(${ch.level})`)}`);
  }
  if (marketLevel) console.log(`  ${"marketplace".padEnd(26)} ${marketFrom} → ${c.grn(marketTo)} ${c.dim(`(${marketLevel})`)}`);

  if (flags["dry-run"]) return;

  // apply
  for (const ch of changes) {
    if (!ch.baseline) {
      ch.p.manifest.version = ch.to;
      writeJSON(ch.p.manifestPath, ch.p.manifest);
      prependChangelog(join(ch.p.dir, "CHANGELOG.md"), ch.to, ch.lines, "Release.");
    }
  }
  if (marketLevel) {
    packageManifest.version = marketTo;
    writeJSON(PACKAGE_PATH, packageManifest);
  }
  syncMarketplace({ quiet: true });
  if (marketLevel) {
    const rootLines = changes.filter(c => !c.baseline).map(ch => `- **${ch.p.name}** ${ch.to} (${ch.level})`);
    prependChangelog(ROOT_CHANGELOG, marketTo, rootLines, "Release.");
  }

  if (flags["no-git"]) { console.log(c.grn("done") + c.dim(" (files written; skipped git commit/tag)")); return; }

  const bumped = changes.filter(c => !c.baseline);
  if (bumped.length || marketLevel) {
    // a baseline-only release writes no files, so there is nothing to commit - just tag.
    git(["add", "-A"]);
    const summary = bumped.map(c => `${c.p.name}@${c.to}`).join(", ");
    git(["commit", "-q", "-m", `chore(release): ${summary || "marketplace"}${marketLevel ? `; marketplace@${marketTo}` : ""}`]);
  }
  for (const ch of changes) git(["tag", `${ch.p.name}@${ch.to}`]);
  if (marketLevel) git(["tag", `marketplace-v${marketTo}`]);
  console.log(c.grn("released ") + `tagged: ${changes.map(c => `${c.p.name}@${c.to}`).join(", ")}${marketLevel ? `, marketplace-v${marketTo}` : ""}`);
  console.log(c.dim("  push with: git push && git push --tags"));
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
    if (!listed.has(p.name)) { console.error(c.yel(`! ${p.name}: not in marketplace.json (run: mkt sync)`)); }
  }
  // delegate deep validation to claude CLI if present
  try {
    const out = execFileSync("claude", ["plugin", "validate", "."], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
    if (out.trim()) console.log(c.dim(out.trim()));
  } catch (e) {
    const msg = (e.stdout || "") + (e.stderr || "");
    if (msg.trim()) { console.error(c.red(msg.trim())); ok = false; }
    else console.log(c.dim("(claude plugin validate unavailable - skipped deep validation)"));
  }
  console.log(ok ? c.grn("✓ validation passed") : c.red("✗ validation failed"));
  process.exit(ok ? 0 : 1);
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
echo "$msg" | grep -Eq '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\\([a-z0-9-]+\\))?!?: .+' && exit 0
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

const HELP = `mkt - dorbar-skills marketplace toolkit

  mkt new <name> [--bundle] [--skill <skill>] [--desc "..."]   scaffold a plugin
  mkt sync                                                     regenerate marketplace.json from manifests
  mkt status                                                   show versions + pending conventional bumps
  mkt release [--dry-run] [--plugin <name>] [--no-git]         auto-bump (Conventional Commits), sync, tag
  mkt bump <plugin> <patch|minor|major>                        manual single-plugin bump
  mkt validate                                                 validate manifests + claude plugin validate
  mkt install-hooks                                            install commit-msg conventional-commit lint
`;

const [cmd, ...rest] = process.argv.slice(2);
switch (cmd) {
  case "new": cmdNew(rest); break;
  case "sync": syncMarketplace(); break;
  case "status": cmdStatus(); break;
  case "release": cmdRelease(rest); break;
  case "bump": cmdBump(rest); break;
  case "validate": cmdValidate(); break;
  case "install-hooks": cmdInstallHooks(); break;
  case undefined: case "help": case "--help": case "-h": console.log(HELP); break;
  default: die(`unknown command: ${cmd}\n\n${HELP}`);
}
