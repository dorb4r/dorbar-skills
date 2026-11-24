"""Break a reference reel down into measurable facts: shots, cut timing vs the music grid, audio hits.

    uv run --project <tools> python <tools>/reel_breakdown.py <reel.mp4> <out_dir> [--scene 0.25]

Writes to <out_dir>:
    shots.jpg    one frame per shot (mid-shot; long shots get 3), labelled "#n t=start d=dur"
    audio.png    loudness envelope + onset flux, cut lines (red), beat ticks (grey), downbeats (blue)
    facts.md     per-shot table: start, duration, offset to the nearest beat (ms), onset at the cut
                 (a hit/whoosh/SFX or a music accent), voice-band share (speech hint), plus the BPM,
                 cut rate and how many cuts land within 60 ms of a beat.
Facts only; the judgement (why it works) is written by whoever reads these files.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

src, out = Path(sys.argv[1]), Path(sys.argv[2])
thr = float(sys.argv[sys.argv.index("--scene") + 1]) if "--scene" in sys.argv else 0.25
out.mkdir(parents=True, exist_ok=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                           capture_output=True, text=True).stdout.strip())

# --- shots -------------------------------------------------------------------------------------
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-filter:v", f"select='gt(scene,{thr})',showinfo",
                      "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
cuts = [c for c in cuts if 0.1 < c < dur - 0.1]
merged = []
for c in cuts:                       # drop flicker cuts closer than 0.12 s
    if not merged or c - merged[-1] > 0.12:
        merged.append(c)
bounds = [0.0] + merged + [dur]
shots = [(bounds[i], bounds[i + 1] - bounds[i]) for i in range(len(bounds) - 1)]

# --- audio -------------------------------------------------------------------------------------
wav = Path(tempfile.mkdtemp()) / "a.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "22050", str(wav)], check=True)
y, sr = sf.read(wav)
hop, n = 256, 2048
fr = np.lib.stride_tricks.sliding_window_view(y, n)[::hop] * np.hanning(n)
S = np.abs(np.fft.rfft(fr, axis=1)); f = np.fft.rfftfreq(n, 1 / sr)
fps = sr / hop; t = np.arange(len(S)) / fps + n / 2 / sr
L = np.log1p(10 * S)
flux = np.r_[0, np.maximum(0, np.diff(L, axis=0)).sum(1)]
rms = np.sqrt((fr ** 2).mean(1)); db = 20 * np.log10(rms + 1e-6)
voice = S[:, (f > 300) & (f < 3400)].sum(1) / (S.sum(1) + 1e-9)
fz = (flux - np.median(flux)) / (np.percentile(flux, 95) - np.median(flux) + 1e-9)

def score(bpm, ph):
    bt = np.arange(ph, t[-1], 60 / bpm)
    return flux[np.clip(np.round((bt - n / 2 / sr) * fps).astype(int), 0, len(flux) - 1)].mean()
cands = [(score(b, p), b, p) for b in np.arange(70, 180, 0.5) for p in np.arange(0, 60 / b, 0.01)]
base = np.mean([c[0] for c in cands]); sc, bpm, ph = max(cands)
pulse = sc / base                     # >1.3 = clear beat; ~1 = no steady beat (speech/ambient)
beats = np.arange(ph, dur, 60 / bpm)
# downbeat phase: the beat offset (0..3) whose beats carry the most flux
acc = [flux[np.clip(np.round((beats[k::4] - n / 2 / sr) * fps).astype(int), 0, len(flux) - 1)].mean() for k in range(4)]
down = beats[int(np.argmax(acc))::4]

def at(arr, x, w=0.05):
    i0, i1 = np.searchsorted(t, x - w), np.searchsorted(t, x + w)
    return arr[i0:max(i1, i0 + 1)].max()

rows, on_beat = [], 0
for i, (s, d) in enumerate(shots):
    off = (s - beats[np.argmin(np.abs(beats - s))]) * 1000 if i else 0
    hit = at(fz, s) if i else 0
    on_beat += i > 0 and abs(off) <= 60
    seg = (t >= s) & (t < s + d)
    rows.append((i + 1, s, d, off, hit, float(np.median(voice[seg])) if seg.any() else 0, float(np.median(db[seg])) if seg.any() else -99))

# --- facts.md ----------------------------------------------------------------------------------
info = src.with_suffix(".info.json")
meta = json.loads(info.read_text()) if info.exists() else {}
lines = [f"# {src.stem}: measured facts", "",
         f"- account: {meta.get('uploader', '?')} | likes {meta.get('like_count')} | comments {meta.get('comment_count')}",
         f"- caption: {(meta.get('description') or '').splitlines()[0][:200] if meta.get('description') else ''}",
         f"- length {dur:.1f} s | {len(shots)} shots | mean shot {dur / len(shots):.2f} s | median {np.median([d for _, d in shots]):.2f} s",
         f"- music: {bpm:.1f} BPM, pulse strength {pulse:.2f} (>1.3 clear beat, ~1.0 none) | beat = {60 / bpm:.3f} s",
         f"- cuts within 60 ms of a beat: {on_beat}/{max(len(shots) - 1, 0)}",
         f"- loudest second: {t[np.argmax(np.convolve(db, np.ones(int(fps)) / fps, 'same'))]:.1f} s", "",
         "| # | start | dur | beat off (ms) | onset at cut (z) | voice share | level dB |", "|---|---|---|---|---|---|---|"]
lines += [f"| {r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:+.0f} | {r[4]:.1f} | {r[5]:.2f} | {r[6]:.0f} |" for r in rows]
lines += ["", "onset z > 1.5 at a cut = an audible hit/whoosh/accent on the cut. voice share > ~0.55 with no clear beat = likely speech."]
(out / "facts.md").write_text("\n".join(lines) + "\n")

# --- shots.jpg ---------------------------------------------------------------------------------
font = ImageFont.load_default(size=22)
tiles = []
for i, (s, d) in enumerate(shots):
    k_n = 1 if d < 2.5 else min(12, max(3, int(d / 1.5)))
    times = [s + d / 2] if k_n == 1 else [s + d * (j + 0.5) / k_n for j in range(k_n)]
    for k, x in enumerate(times):
        p = out / f"_f{i}_{k}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{x:.3f}", "-i", str(src), "-frames:v", "1",
                        "-vf", "scale=216:384", str(p)], check=True)
        im = Image.open(p).convert("RGB"); p.unlink()
        dr = ImageDraw.Draw(im); lab = f"#{i + 1} {s:.1f}s" + (f" d{d:.1f}" if k == 0 else f" +{x - s:.1f}")
        dr.rectangle([0, 0, 216, 28], fill=(0, 0, 0)); dr.text((4, 3), lab, fill=(255, 255, 0), font=font)
        tiles.append(im)
cols = 8; rws = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 216, rws * 384), (20, 20, 20))
for j, im in enumerate(tiles):
    sheet.paste(im, ((j % cols) * 216, (j // cols) * 384))
sheet.save(out / "shots.jpg", quality=80)

# --- audio.png ---------------------------------------------------------------------------------
W, H = 1600, 300; img = Image.new("RGB", (W, H), (15, 15, 15)); dr = ImageDraw.Draw(img)
X = lambda s: int(s / dur * (W - 1))
for b in beats: dr.line([X(b), 0, X(b), H], fill=(55, 55, 55))
for b in down: dr.line([X(b), 0, X(b), H], fill=(40, 70, 140))
lv = np.interp(np.linspace(0, dur, W), t, db); lv = (lv - lv.min()) / (np.ptp(lv) + 1e-9)
fl = np.interp(np.linspace(0, dur, W), t, np.clip(fz, 0, 4) / 4)
for x in range(W):
    dr.line([x, H, x, H - int(lv[x] * 140)], fill=(90, 160, 90))
    dr.line([x, 150, x, 150 - int(fl[x] * 140)], fill=(220, 180, 60))
for s, _ in shots[1:]: dr.line([X(s), 0, X(s), H], fill=(230, 50, 50), width=2)
for sec in range(int(dur) + 1): dr.text((X(sec) + 2, H - 14), str(sec), fill=(200, 200, 200))
img.save(out / "audio.png")
print((out / "facts.md").read_text())
