"""Measure a music track's beat grid, bars, phrases and climax (no librosa; it hangs here).

    uv run --project <tools> python beatgrid.py <track.mp4|wav> [--until 40]

Prints: exact BPM + beat phase (comb search over the whole song), then one row per beat with kick
strength, onset flux and loudness, marking bar (4-beat) starts. Read it to find the build and the
climax = the phrase downbeat where kick + loudness jump. Then in the spec:
    MUSIC start = CLIMAX_IN_SONG - REVEAL_TIME   (choose REVEAL_TIME on the reel's beat grid)
With that in-point every song beat lands on a multiple of the beat period on the timeline,
so cuts at those multiples are on the beat.
"""
import subprocess, sys, tempfile, numpy as np, soundfile as sf
from pathlib import Path

src = Path(sys.argv[1]); until = float(sys.argv[sys.argv.index("--until") + 1]) if "--until" in sys.argv else 40
wav = Path(tempfile.mkdtemp()) / "t.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "22050", str(wav)], check=True)
y, sr = sf.read(wav); hop, n = 64, 1024
fr = np.lib.stride_tricks.sliding_window_view(y, n)[::hop] * np.hanning(n)
S = np.abs(np.fft.rfft(fr, axis=1)); f = np.fft.rfftfreq(n, 1 / sr)
fps = sr / hop; t = np.arange(len(S)) / fps + n / 2 / sr
L = np.log1p(10 * S)
flux = np.r_[0, np.maximum(0, np.diff(L, axis=0)).sum(1)]
kick = np.r_[0, np.maximum(0, np.diff(L[:, (f > 40) & (f < 160)], axis=0)).sum(1)]
end = min(t[-1] - 1, 150)
def score(bpm, ph):
    bt = np.arange(ph, end, 60 / bpm); bt = bt[bt > 2]
    return flux[np.clip(np.round((bt - n / 2 / sr) * fps).astype(int), 0, len(flux) - 1)].mean()
best = max(((score(b, p), b, p) for b in np.arange(70, 180, 0.25) for p in np.arange(0, 60 / b, 0.01)))
_, bpm, _ = best   # refine
best = max(((score(b, p), b, p) for b in np.arange(bpm - 0.3, bpm + 0.3, 0.01) for p in np.arange(0, 60 / b, 0.005)))
_, bpm, ph = best; P = 60 / bpm
print(f"BPM {bpm:.2f}  beat {P:.4f}s  phase {ph:.3f}s  (beats at {ph:.3f} + {P:.4f}k)")
def at(a, arr): i = (t > a - 0.03) & (t < a + 0.05); return arr[i].max() if i.any() else 0
def rms(a, b): s = y[int(a * sr):int(b * sr)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9)
k = 0
while ph + k * P < until:
    b = ph + k * P
    print(f"beat {k:3d} {b:7.2f}s kick {at(b, kick):5.1f} flux {at(b, flux):6.1f} rms {rms(b, b + P):5.1f}{'  |bar' if k % 4 == 0 else ''}")
    k += 1
