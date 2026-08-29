import subprocess
import os
cmd = ["npx", "--yes", "hyperframes", "render", "projects/local-agents/hf-workspace", "--output", "projects/local-agents/renders/final.mp4"]
print(f"[RUN] {' '.join(cmd)}")
subprocess.run(cmd, capture_output=False, text=True, shell=(os.name == "nt"))
