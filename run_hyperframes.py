import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from tools.video.hyperframes_compose import HyperFramesCompose

with open('projects/local-agents/artifacts/edit_decisions.json') as f:
    ed = json.load(f)
with open('projects/local-agents/artifacts/asset_manifest.json') as f:
    am = json.load(f)

vc = HyperFramesCompose()
result = vc.execute({
    'operation': 'render',
    'output_path': 'projects/local-agents/renders/final.mp4',
    'edit_decisions': ed,
    'asset_manifest': am
})
print("Result:")
print(result)
