from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'.work/projects.json').read_text('utf-8'))
OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('KR','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('KR-Bold','C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('KR',normal='KR',bold='KR-Bold')
W,H=A4; M=39; CW=W-2*M
INK=HexColor('#202c27');MUTED=HexColor('#647267');ACC=HexColor('#285943');PALE=HexColor('#edf2e8');LINE=HexColor('#dce4d6')
manifest={}

def make(project):
    file=OUT/f'{project["id"]}-portfolio.pdf'
    images=project['assets']['images'][:2]
    pages=3 if images else 2
    c=canvas.Canvas(str(file),pagesize=A4,pageCompression=1)
    c.setTitle(f'{project["title"]} | 김해준 포트폴리오');c.setAuthor('김해준 (Haejoon Kim) / MaoEmong')
    def text(x,y,t,size=10,font='KR',color=INK):
        if pdfmetrics.stringWidth(t,font,size)>CW+1 and x==M:
            raise ValueError(f'Line overflow: {project["id"]}: {t}')
        c.setFont(font,size);c.setFillColor(color);c.drawString(x,H-y-size,t)
    def para(y,t,width=CW,x=M,size=10.2,leading=17,color=INK,bold=False):
        st=ParagraphStyle('p',fontName='KR-Bold' if bold else 'KR',fontSize=size,leading=leading,textColor=color,wordWrap='LTR')
        p=Paragraph(escape(t).replace('\n','<br/>'),st);_,height=p.wrap(width,1200)
        if y+height>H-59:raise ValueError(f'Paragraph overflow {project["id"]}: {t[:40]}')
        p.drawOn(c,x,H-y-height);return y+height
    def box(x,y,w,h,fill=PALE):
        c.setFillColor(fill);c.roundRect(x,H-y-h,w,h,5,fill=1,stroke=0)
    def line(y):c.setStrokeColor(LINE);c.setLineWidth(.65);c.line(M,H-y,W-M,H-y)
    def link(x,y,label,url,size=9):
        text(x,y,label,size,color=ACC);w=pdfmetrics.stringWidth(label,'KR',size);c.linkURL(url,(x,H-y-size-2,x+w,H-y+3),relative=0,thickness=0)
    def footer(number):
        line(H-43);text(M,H-31,'김해준 · MaoEmong',7.5,color=MUTED)
        link(M+127,H-31,'maoemong.github.io/projects/'+project['id']+'/',f'https://maoemong.github.io/projects/{project["id"]}/',7.1)
        c.setFont('Helvetica',7.5);c.setFillColor(MUTED);c.drawRightString(W-M,22,f'{number:02d} / {pages:02d}')
        c.showPage()
    def eyebrow(title):text(M,31,title,8.2,'KR-Bold',ACC)
    def section(y,title):text(M,y,title,14,'KR-Bold');return y+31
    eyebrow(f'PROJECT PORTFOLIO  /  {project["category"]}')
    size=min(31,31*CW/pdfmetrics.stringWidth(project['title'],'KR-Bold',31))
    text(M,72,project['title'],size,'KR-Bold')
    para(123,project['tagline'],size=13.3,leading=21,color=MUTED)
    text(M,185,'GITHUB REPOSITORY',8.2,'KR-Bold',MUTED)
    link(M,205,project['github'],project['github'],9.2)
    para(238,' · '.join(project['stack']),size=9,leading=15,color=ACC)
    line(278)
    y=section(301,'프로젝트 개요')
    y=para(y,project['summary'],size=12,leading=20)+15
    y=para(y,project['overview'],size=10.1,leading=17,color=MUTED)+29
    y=section(y,'주요 기능')
    for i,(title,body) in enumerate(project['features'],1):
        text(M,y,f'{i:02d}',10,'KR-Bold',ACC)
        text(M+31,y,title,11,'KR-Bold')
        y=para(y+24,body,width=CW-31,x=M+31,size=9.8,leading=16,color=MUTED)+20
    footer(1)
    eyebrow('ENGINEERING  /  ROLE & SCOPE')
    text(M,72,'구현과 소개 범위',26,'KR-Bold')
    fw=(CW-24)/4
    for i,step in enumerate(project['flow']):
        x=M+i*(fw+8);box(x,132,fw,67)
        text(x+11,141,f'{i+1:02d}',8,'KR-Bold',ACC)
        para(163,step,width=fw-22,x=x+11,size=9,leading=13)
    y=section(231,'선택한 구조')
    for title,body in project['decisions']:
        y=para(y,title,size=11.2,bold=True)+7
        y=para(y,body,size=10,leading=17,color=MUTED)+20
    if project.get('role'):
        y=section(y+5,'역할과 기여')
        y=para(y,project['role'],size=10,leading=17,color=MUTED)+24
    y=section(y+5,'확인한 내용과 범위')
    if project.get('verification'): y=para(y,project['verification'],size=9.8,leading=16.5,color=MUTED)+12
    y=para(y,project['scope'],size=9.8,leading=16.5,color=MUTED)
    # Fixed bottom source area stays clear of the body.
    if y>672:raise ValueError(f'Evidence too long for source area: {project["id"]} {y}')
    line(691)
    text(M,709,'정리 기준 · 공개 README / 2026-10-19',8.4,'KR-Bold',MUTED)
    link(M,731,'원본 README에서 구현 내용과 검사 범위 확인',project['assets']['readme'],8.8)
    link(M,754,project['github'],project['github'],8.6)
    footer(2)
    if images:
        eyebrow('SCREENS  /  PUBLIC PROJECT IMAGES')
        text(M,72,'프로젝트 화면',26,'KR-Bold')
        para(116,project.get('imageNote','공개 README에 수록된 프로젝트 화면입니다.'),size=9.2,leading=15,color=MUTED)
        y=160
        for i,image in enumerate(images):
            file_image=ROOT/image['path'].lstrip('/')
            with Image.open(file_image) as pic:
                maxw,maxh=CW,239;factor=min(maxw/pic.width,maxh/pic.height)
                dw,dh=pic.width*factor,pic.height*factor
                box(M,y,CW,maxh)
                c.drawImage(ImageReader(pic),M+(CW-dw)/2,H-y-(maxh+dh)/2,dw,dh,mask='auto')
                c.linkURL(project['assets']['readme'],(M,H-y-maxh,W-M,H-y),relative=0,thickness=0)
            text(M,y+maxh+9,image['alt'],8.2,color=MUTED)
            y+=282
        footer(3)
    c.save()
    return file

for project in DATA:
    # Preserve the six-page Pixel Office portfolio already reviewed by the user.
    previous=OUT/'pixel-office-portfolio.pdf'
    if project['id']=='pixel-office' and previous.exists():
        file=previous
    else:file=make(project)
    reader=PdfReader(file)
    full='\n'.join(page.extract_text() or '' for page in reader.pages)
    assert project['github'] in full,project['id']
    assert '\ufffd' not in full,project['id']
    links=[]
    for page in reader.pages:
        for a in page.get('/Annots',[]):
            obj=a.get_object().get('/A',{})
            if obj.get('/URI'):links.append(str(obj['/URI']))
    assert project['github'] in links,project['id']
    manifest[project['id']]={'file':file.name,'pages':len(reader.pages),'bytes':file.stat().st_size,'github':project['github']}
    print(json.dumps({'id':project['id'],**manifest[project['id']]},ensure_ascii=False))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Completed {len(manifest)} project PDFs.')
