from pathlib import Path
import json, subprocess, os, shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]
PDFS=ROOT/'output/pdf'
TEMP=ROOT/'tmp/pdfs';TEMP.mkdir(parents=True,exist_ok=True)
manifest=json.loads((PDFS/'manifest.json').read_text('utf-8'))
POPPLER=os.environ.get('PDFTOPPM') or shutil.which('pdftoppm')
if not POPPLER:
    raise RuntimeError('pdftoppm을 설치하거나 PDFTOPPM에 실행 파일 경로를 지정하세요.')
def render(item):
    slug,data=item;file=PDFS/data['file']
    with pdfplumber.open(file) as doc:
        for i,page in enumerate(doc.pages,1):
            assert page.extract_text().strip(),(slug,i,'empty page')
            outside=[ch['text'] for ch in page.chars if ch['x0']<-.5 or ch['x1']>page.width+.5 or ch['top']<-.5 or ch['bottom']>page.height+.5]
            assert not outside,(slug,i,outside[:5])
    subprocess.run([str(POPPLER),'-scale-to','800','-png',str(file),str(TEMP/slug)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    return slug
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,manifest.items()))
files=[]
for slug,data in manifest.items():files.extend((slug,i,TEMP/f'{slug}-{i}.png') for i in range(1,data['pages']+1))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for start in range(0,len(files),6):
    group=files[start:start+6]
    sheet=Image.new('RGB',(1740,1710),'#dce2d8');draw=ImageDraw.Draw(sheet)
    for k,(slug,num,file) in enumerate(group):
        with Image.open(file) as page:
            page.thumbnail((550,800))
            x=15+(k%3)*580;y=30+(k//3)*850
            sheet.paste(page,(x,y));draw.text((x,y-23),f'{slug} / {num}',font=font,fill='#203225')
    sheet.save(TEMP/f'contact-{start//6+1:02d}.jpg',quality=92)
print(json.dumps({'pdfs':len(manifest),'pages':sum(d['pages'] for d in manifest.values()),'rendered':len(files),'contactSheets':(len(files)+5)//6,'outsidePageText':0}))
