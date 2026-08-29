import json
from tools.video.video_compose import VideoCompose

with open('projects/local-agents/artifacts/edit_decisions.json') as f:
    ed = json.load(f)
with open('projects/local-agents/artifacts/asset_manifest.json') as f:
    am = json.load(f)

vc = VideoCompose()
try:
    result = vc.execute({
        'operation': 'render',
        'output_path': 'projects/local-agents/renders/final.mp4',
        'edit_decisions': ed,
        'asset_manifest': am
    })
    
    # Dump to file to avoid cp1252 console encoding errors with remotion's arrows
    with open('projects/local-agents/artifacts/render_result.json', 'w', encoding='utf-8') as out_f:
        out_f.write(str(result))
    
except Exception as e:
    import traceback
    with open('projects/local-agents/artifacts/render_error.txt', 'w', encoding='utf-8') as err_f:
        traceback.print_exc(file=err_f)
