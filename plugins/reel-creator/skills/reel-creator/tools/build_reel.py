"""Build a reel spec into a CapCut desktop project (macOS).

    uv run --project tools python tools/build_reel.py <spec.py> "<CapCut project folder name>"

The folder name is the project's folder under ~/Movies/CapCut/User Data/Projects/com.lveditor.draft/
(normally the name shown in CapCut; a freshly renamed project may keep its old folder name).

The target project must already exist and be closed: create it in CapCut (Create project, rename it),
then CapCut menu > Back to home page. CapCut ignores project folders it didn't create itself.

A spec is a Python file defining:
    RAW        = Path of the clip folder (relative paths in SHOTS resolve against it)
    SHOTS      = [Shot(...), ...] laid end to end from 0 s on the main video track
    CAPTIONS   = [Cap(text, start, end, y=0.62, emphasis="word", color=(1, .8, 0)), ...]
    MUSIC      = Music(file, start, fade_in, fade_out, volume) or None   (one piece, whole reel)
    AUDIO      = [Audio(file, at, src, dur, volume, fade_in, fade_out, track="sfx"), ...]
                 extra audio: music sections (cut the song to the edit, leave a silence gap
                 before the drop), SFX hits/whooshes/risers, a recorded voice-over.
    STYLE_FROM = name of a CapCut project whose first caption is the approved caption look
                 (required when CAPTIONS is not empty; set it in the project's references).
    SHELL      = optional: a CapCut project used as the JSON template (default STYLE_FROM).

Captions copy STYLE_FROM's look (font, size, stroke). `emphasis` recolours one word (kinetic emphasis).
iPhone HLG clips get CapCut's HDR mode 4 (as CapCut sets it after "Adapt"); SDR clips mode 1.
Prints the hand-finish list at the end: what pyCapCut can't write (see references/capcut.md).
"""
import copy, importlib.util, json, subprocess, sys
from dataclasses import dataclass
from pathlib import Path

import pycapcut as cc
from pycapcut import trange, SEC
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import capcut_mac

W, H = 1080, 1920


@dataclass
class Shot:
    file: str
    dur: float                 # seconds on the timeline
    src: float = 0.0           # in-point in the clip (video only)
    push: float = 0.0          # slow push-in: end scale = start scale * (1 + push)
    fit: bool = False          # keep the whole frame, blurred background behind it
    zoom: float = 1.0          # extra scale on top of fill (1.15 = punch-in)
    x: float = 0.0             # reframe: CapCut transform x/y (-1..1, half-canvas units)
    y: float = 0.0
    volume: float = 0.0        # clip's own sound (needle buzz, a laugh): 0..1
    speed: float = 1.0         # constant speed; a ramp = consecutive shots with stepped speeds
    dissolve: float = 0.0      # cross-dissolve into the NEXT shot (seconds)
    note: str = ""             # the story beat this shot serves


@dataclass
class Cap:
    text: str
    start: float
    end: float
    y: float = 0.62
    x: float = 0.0
    emphasis: str = ""         # a word inside text to recolour
    color: tuple = (1.0, 0.8, 0.0)


@dataclass
class Music:
    file: str
    start: float = 0.0
    fade_in: float = 0.0
    fade_out: float = 1.5
    volume: float = 1.0


@dataclass
class Audio:
    file: str
    at: float                  # timeline position (s)
    src: float = 0.0           # in-point in the file (s)
    dur: float = 0.0           # 0 = to the end of the file (or the reel)
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    track: str = "sfx"         # "music" for song sections, "sfx", "vo"


def media_size(path: Path):
    if path.suffix.lower() in (".jpg", ".jpeg", ".png"):
        return Image.open(path).size, "image", ""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,color_transfer:stream_side_data=rotation",
                          "-of", "json", str(path)], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    w, h = s["width"], s["height"]
    rot = max([abs(int(sd.get("rotation", 0))) for sd in s.get("side_data_list", [])] or [0])
    if rot in (90, 270):
        w, h = h, w
    return (w, h), "video", s.get("color_transfer", "")


def audio_len(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True).stdout.strip())


def fill_scale(w, h):
    fit = min(W / w, H / h)
    return max(W / w, H / h) / fit


def load_spec(p):
    spec = importlib.util.spec_from_file_location("spec", p)
    mod = importlib.util.module_from_spec(spec)
    mod.Shot, mod.Cap, mod.Music, mod.Audio = Shot, Cap, Music, Audio
    sys.modules["spec"] = mod
    spec.loader.exec_module(mod)
    return mod


def build(spec, workdir: Path):
    folder = cc.DraftFolder(str(workdir))
    script = folder.create_draft("build", W, H, allow_replace=True)
    script.add_track(cc.TrackType.video).add_track(cc.TrackType.text)
    dissolve = cc.TransitionType.__members__["叠化"]
    hdr, t = {}, 0.0
    for shot in spec.SHOTS:
        path = (spec.RAW / shot.file) if not Path(shot.file).is_absolute() else Path(shot.file)
        assert path.exists(), path
        (w, h), kind, transfer = media_size(path)
        base = (1.0 if shot.fit else fill_scale(w, h)) * shot.zoom
        tr = trange(f"{t}s", f"{shot.dur}s")
        kw = dict(volume=shot.volume, clip_settings=cc.ClipSettings(scale_x=base, scale_y=base,
                                                                    transform_x=shot.x, transform_y=shot.y))
        if kind == "video":
            kw["source_timerange"] = trange(f"{shot.src}s", f"{shot.dur * shot.speed}s")
            if shot.speed != 1.0:
                kw["speed"] = shot.speed
        seg = cc.VideoSegment(str(path), tr, **kw)
        if shot.push:
            seg.add_keyframe(cc.KeyframeProperty.uniform_scale, 0, base)
            seg.add_keyframe(cc.KeyframeProperty.uniform_scale, int(shot.dur * SEC), base * (1 + shot.push))
        if shot.fit:
            seg.add_background_filling("blur", 0.375)
        if shot.dissolve:
            seg.add_transition(dissolve, duration=f"{shot.dissolve}s")
        script.add_segment(seg)
        hdr[str(path)] = 4 if transfer == "arib-std-b67" else 1
        t += shot.dur
    total = t

    for c in spec.CAPTIONS:
        script.add_segment(cc.TextSegment(c.text, trange(f"{c.start}s", f"{c.end - c.start}s"),
                                          clip_settings=cc.ClipSettings(transform_x=c.x, transform_y=c.y)))
    tracks = set()

    def add_audio(path, at, src, dur, volume, fade_in, fade_out, track):
        if track not in tracks:
            script.add_track(cc.TrackType.audio, track)
            tracks.add(track)
        a = cc.AudioSegment(str(path), trange(f"{at}s", f"{dur}s"),
                            source_timerange=trange(f"{src}s", f"{dur}s"), volume=volume)
        if fade_in or fade_out:
            a.add_fade(f"{fade_in}s", f"{fade_out}s")
        script.add_segment(a, track)

    if getattr(spec, "MUSIC", None):
        m = spec.MUSIC
        add_audio(m.file, 0.0, m.start, total, m.volume, m.fade_in, m.fade_out, "music")
    for a in getattr(spec, "AUDIO", []):
        p = Path(a.file)
        assert p.exists(), p
        dur = a.dur or (audio_len(p) - a.src)
        add_audio(p, a.at, a.src, round(min(dur, total - a.at), 3), a.volume, a.fade_in, a.fade_out, a.track)
    script.save()
    return workdir / "build" / "draft_content.json", hdr, total


def utf16(s):
    return len(s.encode("utf-16-le")) // 2


def restyle(draft_path: Path, hdr: dict, style_from, caps):
    d = json.loads(draft_path.read_text())
    if d["materials"]["texts"]:
        shell = json.loads((capcut_mac.ROOT / style_from / "draft_info.json").read_text())
        tmpl = shell["materials"]["texts"][0]
        tcontent = json.loads(tmpl["content"])
        by_text = {c.text: c for c in caps}
        for i, m in enumerate(d["materials"]["texts"]):
            text = json.loads(m["content"])["text"]
            new = copy.deepcopy(tmpl)
            new["id"] = m["id"]
            c = copy.deepcopy(tcontent)
            c["text"] = text
            style = c["styles"][0]
            cap = by_text.get(text)
            k = text.find(cap.emphasis) if cap and cap.emphasis else -1
            if k < 0:
                style["range"] = [0, utf16(text)]
                c["styles"] = [style]
            else:                                    # split into before / emphasis / after ranges
                a, b = utf16(text[:k]), utf16(text[:k + len(cap.emphasis)])
                hot = copy.deepcopy(style)
                hot["fill"]["content"]["solid"]["color"] = list(cap.color)
                parts = [(0, a, style), (a, b, hot), (b, utf16(text), style)]
                c["styles"] = [dict(copy.deepcopy(s), range=[x, y]) for x, y, s in parts if y > x]
            new["content"] = json.dumps(c, ensure_ascii=False)
            d["materials"]["texts"][i] = new
    vids = {v["id"]: v for v in d["materials"]["videos"]}
    for tr in d["tracks"]:
        if tr["type"] == "video":
            for s in tr["segments"]:
                mode = hdr.get(vids[s["material_id"]]["path"], 1)
                s["hdr_settings"] = {"mode": mode, "intensity": 1.0, "nits": 1000}
    draft_path.write_text(json.dumps(d, ensure_ascii=False))


HAND_FINISH = """Hand-finish in CapCut (pyCapCut can't write these; see references/capcut.md):
  - speed CURVES (Speed > Curve > Custom, Smooth slow-mo) where the spec steps speeds
  - freeze frames, reverse, animated mask wipes, eased keyframes
  - colour: one adjustment layer (HSL/curves), light grain
  - play every animated Hebrew/RTL caption once (per-letter animations can run left-to-right)"""


def main():
    spec_path, target = sys.argv[1], sys.argv[2]
    spec = load_spec(spec_path)
    style_from = getattr(spec, "STYLE_FROM", None)
    if spec.CAPTIONS and not style_from:
        sys.exit("STYLE_FROM is required when the spec has captions (the approved-style CapCut project)")
    shell = getattr(spec, "SHELL", None) or style_from
    if not shell:
        sys.exit("set SHELL (or STYLE_FROM): an existing CapCut project used as the JSON template")
    work = Path(spec_path).parent / "_build"
    work.mkdir(exist_ok=True)
    draft, hdr, total = build(spec, work)
    restyle(draft, hdr, style_from, spec.CAPTIONS)
    capcut_mac.inject(str(draft), target, shell)
    extra = len(getattr(spec, "AUDIO", []))
    print(f"{len(spec.SHOTS)} shots, {len(spec.CAPTIONS)} captions, {extra} extra audio, {total:.1f} s")
    print(HAND_FINISH)
    print("Next: open the project in CapCut, play it once with sound, then stage 07_review.")


if __name__ == "__main__":
    main()
