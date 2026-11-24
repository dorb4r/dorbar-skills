"""Install a pyCapCut draft as a CapCut desktop (macOS 9.x) project.

pyCapCut writes the Windows layout (draft_content.json, schema 6.7). CapCut for Mac keeps
draft_info.json + .bak + template-2.tmp in the project root and in Timelines/<id>/, and lists
projects in root_meta_info.json. This script:
  1. copies the folder skeleton of an existing Mac project (the "shell"; its media and
     timeline are not kept),
  2. fills every key pyCapCut leaves out from same-type objects in the shell, so the JSON
     matches what this CapCut version writes,
  3. writes the JSON to all six files and registers the project in root_meta_info.json.

Run it only while CapCut is on its home page (no project open). Never quit CapCut.

usage: capcut_mac.py <pycapcut draft_content.json> "<new project name>" --shell "<project>" [--replace]
Backups of every injected project go to $REEL_BACKUP_DIR (default ~/Movies/reel-work/capcut-backups).
"""
import argparse, copy, json, os, shutil, sys, time, uuid
from pathlib import Path

ROOT = Path.home() / "Movies/CapCut/User Data/Projects/com.lveditor.draft"
KEEP = {"draft_settings", "draft_virtual_store.json", "key_value.json", "draft_agency_config.json",
        "draft_biz_config.json", "performance_opt_info.json", "timeline_layout.json",
        "attachment_editing.json", "attachment_pc_common.json", "draft.extra", "draft_meta_info.json"}


def new_id():
    return str(uuid.uuid4()).upper()


def fill(obj, template):
    """Add keys the template has and obj lacks (recursively for dicts). Never overwrite."""
    if not isinstance(obj, dict) or not isinstance(template, dict):
        return obj
    for k, v in template.items():
        if k not in obj:
            obj[k] = copy.deepcopy(v)
        elif isinstance(obj[k], dict) and isinstance(v, dict):
            fill(obj[k], v)
    return obj


def first_segment(d, kind):
    for t in d["tracks"]:
        if t["type"] == kind and t["segments"]:
            return t["segments"][0]
    return None


def upgrade(pcc, shell):
    out = copy.deepcopy(pcc)
    for k in ("version", "new_version", "platform", "last_modified_platform"):
        if k in shell:
            out[k] = copy.deepcopy(shell[k])
    fill(out, {k: v for k, v in shell.items() if k not in ("tracks", "materials")})
    for kind, lst in shell["materials"].items():
        if kind not in out["materials"]:
            out["materials"][kind] = []
        if isinstance(lst, list) and lst:
            for m in out["materials"][kind]:
                fill(m, lst[0])
    for tr in out["tracks"]:
        tmpl = first_segment(shell, tr["type"])
        tmpl_tr = next((t for t in shell["tracks"] if t["type"] == tr["type"]), None)
        if tmpl_tr:
            fill(tr, {k: v for k, v in tmpl_tr.items() if k != "segments"})
        for seg in tr["segments"]:
            if tmpl:
                fill(seg, {k: v for k, v in tmpl.items()
                           if k not in ("material_id", "extra_material_refs", "common_keyframes")})
    out["id"] = new_id()
    return out


def inject(draft_content, target, shell_name):
    """Write a pyCapCut draft into a project CapCut itself created (File > Create project).
    CapCut ignores project folders it didn't create, so this is the reliable path."""
    dest = ROOT / target
    if (dest / ".locked").exists():
        sys.exit(f"'{target}' is open in CapCut; go Back to home page first")
    shell = json.loads((ROOT / shell_name / "draft_info.json").read_text())
    own = json.loads((dest / "draft_info.json").read_text())
    d = upgrade(json.loads(Path(draft_content).read_text()), shell)
    d["id"] = own.get("id", d["id"])
    text = json.dumps(d, ensure_ascii=False)
    main_id = json.loads((dest / "Timelines/project.json").read_text())["main_timeline_id"]
    backup_root = Path(os.environ.get("REEL_BACKUP_DIR", Path.home() / "Movies/reel-work/capcut-backups"))
    backup = backup_root / f"{target}-{int(time.time())}"
    shutil.copytree(dest, backup, ignore=shutil.ignore_patterns("Resources"))
    for folder in (dest, dest / "Timelines" / main_id):
        for fname in ("draft_info.json", "draft_info.json.bak", "template-2.tmp"):
            (folder / fname).write_text(text)
    print(f"wrote {d['duration']/1e6:.1f} s into '{target}' (backup {backup})")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "inject":
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd"); ap.add_argument("draft_content"); ap.add_argument("target")
        ap.add_argument("--shell", required=True)
        a = ap.parse_args()
        return inject(a.draft_content, a.target, a.shell)
    ap = argparse.ArgumentParser()
    ap.add_argument("draft_content")
    ap.add_argument("name")
    ap.add_argument("--shell", required=True)
    ap.add_argument("--replace", action="store_true")
    a = ap.parse_args()

    shell_dir = ROOT / a.shell
    dest = ROOT / a.name
    if dest.exists():
        if not a.replace:
            sys.exit(f"{dest} exists (use --replace)")
        shutil.rmtree(dest)
    dest.mkdir()
    for p in shell_dir.iterdir():
        if p.name in KEEP:
            (shutil.copytree if p.is_dir() else shutil.copy2)(p, dest / p.name)

    shell = json.loads((shell_dir / "draft_info.json").read_text())
    d = upgrade(json.loads(Path(a.draft_content).read_text()), shell)
    text = json.dumps(d, ensure_ascii=False)

    draft_id = new_id()
    tl_id = new_id()
    now_us = int(time.time() * 1e6)
    tl_dir = dest / "Timelines" / tl_id
    tl_dir.mkdir(parents=True)
    project = json.loads((shell_dir / "Timelines/project.json").read_text())
    project.update(id=new_id(), main_timeline_id=tl_id, create_time=now_us, update_time=now_us)
    project["timelines"] = [{"create_time": now_us, "id": tl_id, "is_marked_delete": False,
                             "name": "Timeline 01", "update_time": now_us}]
    (dest / "Timelines/project.json").write_text(json.dumps(project))
    for folder in (dest, tl_dir):
        for fname in ("draft_info.json", "draft_info.json.bak", "template-2.tmp"):
            (folder / fname).write_text(text)

    meta_p = dest / "draft_meta_info.json"
    meta = json.loads(meta_p.read_text())
    meta.update(draft_id=draft_id, draft_name=a.name, draft_fold_path=str(dest),
                draft_root_path=str(ROOT), tm_draft_create=now_us, tm_draft_modified=now_us,
                tm_duration=d["duration"])
    meta_p.write_text(json.dumps(meta, ensure_ascii=False))

    root_p = ROOT / "root_meta_info.json"
    root = json.loads(root_p.read_text())
    shutil.copy2(root_p, root_p.with_suffix(".json.before-" + str(int(time.time()))))
    entry = copy.deepcopy(next(e for e in root["all_draft_store"] if e["draft_name"] == a.shell))
    entry.update(draft_id=draft_id, draft_name=a.name, draft_fold_path=str(dest),
                 draft_json_file=str(dest / "draft_info.json"),
                 draft_cover=str(dest / "draft_cover.jpg"), tm_draft_create=now_us,
                 tm_draft_modified=now_us, tm_duration=d["duration"],
                 draft_timeline_materials_size=0)
    root["all_draft_store"] = [e for e in root["all_draft_store"] if e["draft_name"] != a.name]
    root["all_draft_store"].insert(0, entry)
    root["draft_ids"] = root.get("draft_ids", 0) + 1
    root_p.write_text(json.dumps(root, ensure_ascii=False))
    print(f"installed '{a.name}' ({d['duration']/1e6:.1f} s, {len(d['tracks'])} tracks) at {dest}")


if __name__ == "__main__":
    main()
