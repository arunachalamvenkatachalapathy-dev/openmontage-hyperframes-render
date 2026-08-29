"""
render_direct.py — Build a 9:16 composition for Hyperframes rendering.
Matches the "storytime" YouTube Shorts style:
- Static title at the top
- Ken Burns animated image in the center (cropped to landscape/square)
- Dynamic word-by-word captions at the bottom
"""
import os
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
W, H = 1080, 1920  # 9:16 vertical
total = 24         # seconds

BG_BLACK = "#000000"
TITLE_TEXT = "How to Build AI Agents for Free"

# Timing for the word-by-word captions
# We will approximate the word timings for each clip
clips = [
    {
        "id": "c1", "start": 0, "end": 5,
        "img": "images/scene1.jpg",
        "words": [
            ("Tired", 0.0, 0.5), ("of", 0.5, 0.8), ("API", 0.8, 1.4), ("fees?", 1.4, 2.0),
            ("AI", 2.2, 2.6), ("video", 2.6, 3.2), ("agents", 3.2, 3.8), ("cost", 3.8, 4.2), ("a", 4.2, 4.4), ("fortune.", 4.4, 5.0)
        ]
    },
    {
        "id": "c2", "start": 5, "end": 11,
        "img": "images/scene2.jpg",
        "words": [
            ("Meet", 5.0, 5.5), ("LocalAI.", 5.5, 6.5),
            ("Run", 6.8, 7.2), ("LLMs", 7.2, 8.0), ("&", 8.0, 8.2), ("Voice", 8.2, 8.8), ("on", 8.8, 9.2), ("CPU.", 9.2, 10.0),
            ("Zero", 10.2, 10.6), ("cost.", 10.6, 11.0)
        ]
    },
    {
        "id": "c3", "start": 11, "end": 17,
        "img": "images/scene3.jpg",
        "words": [
            ("Enter", 11.0, 11.6), ("Hyperframes.", 11.6, 13.0),
            ("HTML", 13.2, 14.0), ("→", 14.0, 14.4), ("Video", 14.4, 15.0), ("in", 15.0, 15.4), ("seconds.", 15.4, 16.5)
        ]
    },
    {
        "id": "c4", "start": 17, "end": 24,
        "img": "images/scene4.jpg",
        "words": [
            ("Build", 17.0, 17.5), ("AI", 17.5, 17.9), ("agents", 17.9, 18.5), ("for", 18.5, 18.8), ("free.", 18.8, 19.5),
            ("No", 19.8, 20.2), ("GPUs.", 20.2, 21.0),
            ("No", 21.2, 21.6), ("API", 21.6, 22.0), ("keys.", 22.0, 22.5),
            ("Just", 22.8, 23.2), ("results.", 23.2, 24.0)
        ]
    },
]

audio_segs = [
    {"src": "audio/s1.wav", "start": 0},
    {"src": "audio/s2.wav", "start": 5},
    {"src": "audio/s3.wav", "start": 11},
    {"src": "audio/s4.wav", "start": 17},
]

def build_clip_html(c):
    """Build a single scene div with the image."""
    # Image container in the center (landscape aspect ratio)
    return f"""
  <div id="{c['id']}" class="clip" style="
    position:absolute; top:25%; left:0; width:100%; height:50%;
    opacity:0; overflow:hidden;
  ">
    <!-- Image with Ken Burns -->
    <img id="img_{c['id']}" src="{c['img']}" style="
      position:absolute; top:0; left:0; width:100%; height:100%;
      object-fit:cover; transform:scale(1.0);
    ">
  </div>"""

def build_captions_html():
    """Build the dynamic captions container."""
    html_parts = []
    html_parts.append('<div id="captions-container" style="position:absolute; bottom:15%; left:10%; right:10%; text-align:center;">')
    for c in clips:
        html_parts.append(f'<div id="captions_{c["id"]}" style="display:none; font-family:\'Arial\',sans-serif; font-weight:bold; font-size:60px; line-height:1.3; color:#888888;">')
        for i, (word, start, end) in enumerate(c["words"]):
            html_parts.append(f'<span id="word_{c["id"]}_{i}">{word}</span> ')
        html_parts.append('</div>')
    html_parts.append('</div>')
    return "\n".join(html_parts)

def build_gsap_timeline():
    """Build the GSAP animation timeline."""
    lines = []
    
    lines.append("  const tl = gsap.timeline({paused:true});")
    lines.append("")

    for c in clips:
        s, e = c["start"], c["end"]
        dur = e - s

        # Fade in scene
        lines.append(f'  tl.set("#{c["id"]}", {{opacity:1}}, {s});')
        lines.append(f'  tl.set("#captions_{c["id"]}", {{display:"block"}}, {s});')

        # Ken Burns zoom (slight zoom in)
        lines.append(f'  tl.fromTo("#img_{c["id"]}", {{scale:1.0, x:0}}, {{scale:1.1, x:-20, duration:{dur}, ease:"none"}}, {s});')

        # Captions highlight
        for i, (word, w_start, w_end) in enumerate(c["words"]):
            lines.append(f'  tl.set("#word_{c["id"]}_{i}", {{color:"#FFFFFF"}}, {w_start});')

        # Fade out at the end (except last scene)
        if e < total:
            lines.append(f'  tl.set("#{c["id"]}", {{opacity:0}}, {e});')
            lines.append(f'  tl.set("#captions_{c["id"]}", {{display:"none"}}, {e});')

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
captions_html = build_captions_html()
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
      font-family:'Arial',sans-serif;
    }}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body data-composition-id="root" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
  <!-- Persistent Top Title -->
  <div style="position:absolute; top:8%; left:5%; right:5%; text-align:center; color:#FFFFFF; font-size:64px; font-weight:bold; line-height:1.2;">
    {TITLE_TEXT}
  </div>

  <!-- Scenes -->
  {clips_html}

  <!-- Dynamic Captions -->
  {captions_html}

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
