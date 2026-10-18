from pathlib import Path
import json
from PIL import Image, ImageOps
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'.work/assets.json').read_text('utf-8'))
dest=root/'assets/images'
dest.mkdir(parents=True,exist_ok=True)
for key,entry in data.items():
    for i,image in enumerate(entry['images'],1):
        with Image.open(root/'.work/originals'/image['file']) as opened:
            pic=ImageOps.exif_transpose(opened).convert('RGB')
            pic.thumbnail((1600,1600),Image.Resampling.LANCZOS)
            name=f'{key}-{i}.webp'
            pic.save(dest/name,'WEBP',quality=88,method=6)
            image.update(path=f'/assets/images/{name}',width=pic.width,height=pic.height)
(root/'data/assets.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Prepared {sum(len(v["images"]) for v in data.values())} local images.')
