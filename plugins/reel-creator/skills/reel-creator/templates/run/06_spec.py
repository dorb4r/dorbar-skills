# 06_spec: {reel slug}. Format: tools/build_reel.py docstring. Every time comes from 05_music.md.
from pathlib import Path
HERE = Path(__file__).parent
RAW = HERE / "raw"
STYLE_FROM = "{approved caption style project, from brand.md}"
BEAT = 0.5          # seconds per beat (05_music.md)
SHOTS = [
    # Shot("clip.MOV", dur, src=in_point, volume=0.0, zoom=1.0, speed=1.0, note="script row #"),
]
CAPTIONS = [
    # Cap("text", start, end, emphasis="word"),
]
AUDIO = [
    # Audio(str(HERE / "audio/track.mp3"), at=0.0, src=in_point, dur=..., track="music"),
    # Audio("/path/hit.wav", at=payoff_time, volume=0.3, track="sfx"),
]
