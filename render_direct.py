"""
render_direct.py — Build a 9:16 dark-neon kinetic typography composition
for Hyperframes rendering. Matches YouTube Shorts tech explainer style.
"""
import os
import json
import shutil
from pathlib import Path

WORKSPACE = Path("projects/local-agents/hf-workspace")
OUTPUT    = Path("projects/local-agents/renders/final.mp4")
AUDIO_DIR = Path("projects/local-agents/assets/audio")
IMAGE_DIR = Path("projects/local-agents/assets/images")

WORKSPACE.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Copy assets into workspace
(WORKSPACE / "audio").mkdir(exist_ok=True)
for wav in AUDIO_DIR.glob("*.wav"):
    shutil.copy(wav, WORKSPACE / "audio" / wav.name)

(WORKSPACE / "images").mkdir(exist_ok=True)
for img in IMAGE_DIR.glob("*.jpg"):
    shutil.copy(img, WORKSPACE / "images" / img.name)

# ── Composition config ──────────────────────────────────────────────
W, H = 1080, 1920  # 9:16 vertical (YouTube Shorts)
total = 24          # seconds

# Neon palette
NEON_CYAN   = "#00ffcc"
NEON_PURPLE = "#a855f7"
NEON_PINK   = "#ff3366"
NEON_GREEN  = "#00ff88"
BG_BLACK    = "#000000"

# Scene definitions
clips = [
    {
        "id": "c1", "start": 0, "end": 5,
        "img": "images/scene1.jpg",
        "title": "TIRED OF",
        "highlight": "API FEES?",
        "sub": "AI video agents cost a fortune.",
        "accent": NEON_CYAN,
    },
    {
        "id": "c2", "start": 5, "end": 11,
        "img": "images/scene2.jpg",
        "title": "MEET",
        "highlight": "LOCAL AI",
        "sub": "Run LLMs & Voice on CPU. Zero cost.",
        "accent": NEON_GREEN,
    },
    {
        "id": "c3", "start": 11, "end": 17,
        "img": "images/scene3.jpg",
        "title": "ENTER",
        "highlight": "HYPERFRAMES",
        "sub": "HTML → Video in seconds.",
        "accent": NEON_PURPLE,
    },
    {
        "id": "c4", "start": 17, "end": 24,
        "img": "images/scene4.jpg",
        "title": "BUILD",
        "highlight": "FOR FREE.",
        "sub": "No GPUs. No API keys. Just results.",
        "accent": NEON_PINK,
    },
]

audio_segs = [
    {"src": "audio/s1.wav", "start": 0},
    {"src": "audio/s2.wav", "start": 5},
    {"src": "audio/s3.wav", "start": 11},
    {"src": "audio/s4.wav", "start": 17},
]


def build_clip_html(c):
    """Build a single scene div with background image, overlay, and text."""
    return f"""
  <div id="{c['id']}" class="clip" style="
    position:absolute; top:0; left:0; width:100%; height:100%;
    opacity:0; overflow:hidden;
  ">
    <!-- Background image with Ken Burns -->
    <img id="img_{c['id']}" src="{c['img']}" style="
      position:absolute; top:0; left:0; width:100%; height:100%;
      object-fit:cover; transform:scale(1.05); filter:brightness(0.6);
    ">
    <!-- Dark gradient overlay -->
    <div style="
      position:absolute; top:0; left:0; width:100%; height:100%;
      background: linear-gradient(
        180deg,
        rgba(0,0,0,0.3) 0%,
        rgba(0,0,0,0.7) 50%,
        rgba(0,0,0,0.95) 100%
      );
    "></div>
    <!-- Glitch flash overlay -->
    <div id="glitch_{c['id']}" style="
      position:absolute; top:0; left:0; width:100%; height:100%;
      background: {c['accent']}; opacity:0; mix-blend-mode:overlay;
    "></div>
    <!-- Text content -->
    <div style="
      position:absolute; bottom:280px; left:60px; right:60px;
      z-index:10;
    ">
      <div id="title_{c['id']}" class="title-text" style="
        font-family:'Space Grotesk',sans-serif; font-weight:400;
        font-size:64px; line-height:1.1; color:rgba(255,255,255,0.7);
        letter-spacing:4px; text-transform:uppercase;
        opacity:0; transform:translateY(40px);
      ">{c['title']}</div>
      <div id="highlight_{c['id']}" class="highlight-text" style="
        font-family:'Space Grotesk',sans-serif; font-weight:700;
        font-size:96px; line-height:1.05; color:#fff;
        letter-spacing:-1px;
        text-shadow: 0 0 30px {c['accent']}, 0 0 60px {c['accent']}40;
        opacity:0; transform:translateY(60px);
        margin-top:8px;
      ">{c['highlight']}</div>
      <div id="sub_{c['id']}" style="
        font-family:'Space Grotesk',sans-serif; font-weight:400;
        font-size:36px; color:{c['accent']}; margin-top:24px;
        opacity:0; transform:translateY(30px);
        letter-spacing:1px;
      ">{c['sub']}</div>
      <div id="bar_{c['id']}" style="
        width:0px; height:4px; background:{c['accent']};
        border-radius:2px; margin-top:32px;
        box-shadow: 0 0 12px {c['accent']};
      "></div>
    </div>
  </div>"""


def build_gsap_timeline():
    """Build the GSAP animation timeline."""
    lines = []
    # Initial state
    for c in clips:
        lines.append(f'  gsap.set("#{c["id"]}", {{opacity:0}});')
        lines.append(f'  gsap.set("#title_{c["id"]}", {{opacity:0, y:40}});')
        lines.append(f'  gsap.set("#highlight_{c["id"]}", {{opacity:0, y:60}});')
        lines.append(f'  gsap.set("#sub_{c["id"]}", {{opacity:0, y:30}});')
        lines.append(f'  gsap.set("#bar_{c["id"]}", {{width:0}});')

    lines.append("")
    lines.append("  const tl = gsap.timeline({paused:true});")
    lines.append("")

    for c in clips:
        s, e = c["start"], c["end"]
        dur = e - s

        # Glitch flash on entry
        lines.append(f'  // Scene: {c["id"]} ({s}s-{e}s)')
        lines.append(f'  tl.to("#glitch_{c["id"]}", {{opacity:0.8, duration:0.05}}, {s});')
        lines.append(f'  tl.to("#glitch_{c["id"]}", {{opacity:0, duration:0.15}}, {s+0.05});')

        # Fade in scene
        lines.append(f'  tl.to("#{c["id"]}", {{opacity:1, duration:0.3, ease:"power2.out"}}, {s});')

        # Ken Burns zoom
        lines.append(f'  tl.to("#img_{c["id"]}", {{scale:1.2, duration:{dur}, ease:"none"}}, {s});')

        # Title slam up
        lines.append(f'  tl.to("#title_{c["id"]}", {{opacity:1, y:0, duration:0.4, ease:"power3.out"}}, {s+0.15});')

        # Highlight slam up (delayed, heavier)
        lines.append(f'  tl.to("#highlight_{c["id"]}", {{opacity:1, y:0, duration:0.5, ease:"power3.out"}}, {s+0.3});')

        # Subtitle fade in
        lines.append(f'  tl.to("#sub_{c["id"]}", {{opacity:1, y:0, duration:0.4, ease:"power2.out"}}, {s+0.6});')

        # Accent bar wipe
        lines.append(f'  tl.to("#bar_{c["id"]}", {{width:120, duration:0.6, ease:"power2.out"}}, {s+0.8});')

        # Fade out (except last scene)
        if e < total:
            lines.append(f'  tl.to("#{c["id"]}", {{opacity:0, duration:0.2, ease:"power2.in"}}, {e-0.2});')

        lines.append("")

    return "\n".join(lines)


def build_audio_html():
    return "\n".join(
        f'  <audio id="aud{i}" src="{a["src"]}" preload="auto"></audio>'
        for i, a in enumerate(audio_segs)
    )


def build_audio_js():
    return "\n".join(
        f'  gsap.delayedCall({a["start"]}, () => document.getElementById("aud{i}").play());'
        for i, a in enumerate(audio_segs)
    )


# ── Assemble HTML ───────────────────────────────────────────────────
clips_html = "\n".join(build_clip_html(c) for c in clips)
audio_html = build_audio_html()
gsap_timeline = build_gsap_timeline()
audio_js = build_audio_js()

html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
      width:{W}px; height:{H}px; overflow:hidden;
      background:{BG_BLACK};
      font-family:'Space Grotesk',sans-serif;
    }}
    /* Subtle scanline overlay */
    body::after {{
      content:'';
      position:fixed; top:0; left:0; width:100%; height:100%;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
      );
      pointer-events:none;
      z-index:999;
    }}
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body data-composition-id="root" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{clips_html}
{audio_html}
<script>
{gsap_timeline}
  window.__timelines = window.__timelines || {{}};
  window.__timelines["root"] = tl;
  {audio_js}
</script>
</body>
</html>
"""

index_path = WORKSPACE / "index.html"
index_path.write_text(html, encoding="utf-8")
print(f"[OK] Composition written -> {index_path}")
print(f"     Dimensions: {W}x{H} (9:16 vertical)")
print(f"     Duration: {total}s")
print(f"     Scenes: {len(clips)}")
