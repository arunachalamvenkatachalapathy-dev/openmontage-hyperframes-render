"""
Direct Hyperframes renderer — bypasses the npm-registry runtime check
by calling the hyperframes binary directly via node.
"""
import subprocess
import json
import os
from pathlib import Path

WORKSPACE = Path("projects/local-agents/hf-workspace")
OUTPUT    = Path("projects/local-agents/renders/final.mp4")
AUDIO_DIR = Path("projects/local-agents/assets/audio")

# ── 1. Build the index.html composition ──────────────────────────────────────
WORKSPACE.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Copy audio files into workspace
import shutil
(WORKSPACE / "audio").mkdir(exist_ok=True)
for wav in AUDIO_DIR.glob("*.wav"):
    shutil.copy(wav, WORKSPACE / "audio" / wav.name)

# Duration map (seconds)
clips = [
    {"id": "c1", "start": 0,  "end": 5,  "text": "TIRED OF API FEES?",   "sub": "AI video agents are expensive."},
    {"id": "c2", "start": 5,  "end": 11, "text": "Meet LocalAI",          "sub": "Run LLMs & Voice locally on CPU. Zero cost."},
    {"id": "c3", "start": 11, "end": 17, "text": "ENTER HYPERFRAMES",     "sub": "HTML → video in seconds, not minutes."},
    {"id": "c4", "start": 17, "end": 22, "text": "BUILD FOR FREE.",        "sub": "No API keys. No cloud GPUs. Just results."},
]

audio_segs = [
    {"src": "audio/s1.wav", "start": 0},
    {"src": "audio/s2.wav", "start": 5},
    {"src": "audio/s3.wav", "start": 11},
    {"src": "audio/s4.wav", "start": 17},
]

total = 22  # seconds
W, H  = 1080, 1920  # 9:16 shorts

def clip_html(c):
    bg  = "#0a0a0a"
    acc = "#00ff88"
    return f"""
  <div id="{c['id']}" class="clip" style="
    position:absolute; top:0; left:0; width:100%; height:100%;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    background:{bg}; opacity:0;
    padding: 80px 60px; box-sizing:border-box; text-align:center;
  ">
    <div class="label" style="
      font-family:'Space Grotesk',sans-serif; font-weight:700;
      font-size:108px; line-height:1.05; color:#fff; letter-spacing:-2px;
    ">{c['text']}</div>
    <div class="sub" style="
      font-family:'Space Grotesk',sans-serif; font-weight:400;
      font-size:44px; color:{acc}; margin-top:32px; line-height:1.3;
    ">{c['sub']}</div>
    <div class="bar" style="
      width:120px; height:6px; background:{acc}; border-radius:3px; margin-top:48px;
    "></div>
  </div>"""

clips_html = "\n".join(clip_html(c) for c in clips)

audio_html = "\n".join(
    f'  <audio id="aud{i}" src="{a["src"]}" preload="auto"></audio>'
    for i, a in enumerate(audio_segs)
)

# GSAP timeline: each clip fades in at its start time and fades out at its end
tween_lines = []
for c in clips:
    s, e = c["start"], c["end"]
    tween_lines.append(f'  tl.to("#{c["id"]}", {{opacity:1, duration:0.4, ease:"power2.out"}}, {s});')
    tween_lines.append(f'  tl.to("#{c["id"]} .label", {{y:0, opacity:1, duration:0.5, ease:"power3.out"}}, {s+0.1});')
    if e < total:
        tween_lines.append(f'  tl.to("#{c["id"]}", {{opacity:0, duration:0.3}}, {e-0.3});')

# Audio playback via JS
audio_js = "\n".join(
    f'  gsap.delayedCall({a["start"]}, () => document.getElementById("aud{i}").play());'
    for i, a in enumerate(audio_segs)
)

gsap_init = "\n".join(
    f'  gsap.set("#{c["id"]} .label", {{y:50, opacity:0}});'
    for c in clips
)

html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ width:{W}px; height:{H}px; overflow:hidden; background:#0a0a0a; }}
  </style>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body data-composition-id="root" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{clips_html}
{audio_html}
<script>
  {gsap_init}
  const tl = gsap.timeline({{paused:true}});
{chr(10).join(tween_lines)}
  window.__timelines = window.__timelines || {{}};
  window.__timelines["root"] = tl;
  {audio_js}
</script>
</body>
</html>
"""

index_path = WORKSPACE / "index.html"
index_path.write_text(html, encoding="utf-8")
print(f"[OK] index.html written -> {index_path}")

# ── 2. Run: npx hyperframes render index.html --output final.mp4 ────────────
output_abs = str(OUTPUT.resolve())
cmd = ["npx", "--yes", "hyperframes", "render", str(index_path.resolve()), "--output", output_abs]
print(f"[RUN] {' '.join(cmd)}")
# Shell=True on Windows if npx is a cmd file, but on Ubuntu it's a bash script
result = subprocess.run(cmd, capture_output=False, text=True, shell=(os.name == 'nt'))

if result.returncode == 0 and OUTPUT.exists():
    size = OUTPUT.stat().st_size
    print(f"\n[OK] Done! Video saved -> {output_abs}  ({size:,} bytes)")
else:
    print(f"\n[FAIL] Render failed (exit {result.returncode})")
