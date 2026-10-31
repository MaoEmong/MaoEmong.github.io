"""Generate readable project PDFs from the same detailed content as the website."""
from pathlib import Path
import argparse
import json
import os
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, Image, Table, TableStyle, HRFlowable
from pypdf import PdfReader
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / '.work/projects.json').read_text('utf-8'))
OUT = ROOT / 'output/pdf'
OUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only', nargs='+', help='Regenerate only these selected project IDs')
args = parser.parse_args()
if args.only and not set(args.only).issubset({p['id'] for p in DATA}):
    parser.error('Unknown project ID')

def find_font(env, candidates):
    names = [os.environ.get(env), *candidates]
    for name in names:
        if name and Path(name).is_file():
            return name
    raise RuntimeError(f'Set {env} to a Korean TrueType font file')

regular = find_font('PORTFOLIO_FONT', [Path.home()/'Library/Fonts/malgun.ttf', 'C:/Windows/Fonts/malgun.ttf', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'])
bold = find_font('PORTFOLIO_FONT_BOLD', [Path.home()/'Library/Fonts/malgunbd.ttf', 'C:/Windows/Fonts/malgunbd.ttf', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf', regular])
pdfmetrics.registerFont(TTFont('KR', regular))
pdfmetrics.registerFont(TTFont('KR-Bold', bold))
pdfmetrics.registerFontFamily('KR', normal='KR', bold='KR-Bold', italic='KR', boldItalic='KR-Bold')
W,H = A4
M = 46
CW = W-2*M
INK = colors.HexColor('#202c27')
MUTED = colors.HexColor('#58665d')
ACC = colors.HexColor('#285943')
PALE = colors.HexColor('#edf2e8')
LINE = colors.HexColor('#dce4d6')
STYLE = {
    'body': ParagraphStyle('body', fontName='KR', fontSize=10, leading=17.5, textColor=INK, spaceAfter=10, wordWrap='CJK', allowWidows=0, allowOrphans=0),
    'muted': ParagraphStyle('muted', fontName='KR', fontSize=9, leading=15.5, textColor=MUTED, spaceAfter=9, wordWrap='CJK'),
    'small': ParagraphStyle('small', fontName='KR', fontSize=8, leading=13, textColor=MUTED, spaceAfter=8, wordWrap='CJK'),
    'link': ParagraphStyle('link', fontName='KR', fontSize=8.5, leading=14, textColor=ACC, spaceAfter=10, wordWrap='CJK'),
    'title': ParagraphStyle('title', fontName='KR-Bold', fontSize=28, leading=38, textColor=INK, spaceAfter=14, wordWrap='CJK'),
    'lead': ParagraphStyle('lead', fontName='KR', fontSize=13, leading=22, textColor=INK, spaceAfter=16, wordWrap='CJK'),
    'h1': ParagraphStyle('h1', fontName='KR-Bold', fontSize=20, leading=29, textColor=INK, spaceBefore=6, spaceAfter=20, keepWithNext=True, wordWrap='CJK'),
    'h2': ParagraphStyle('h2', fontName='KR-Bold', fontSize=13, leading=21, textColor=INK, spaceBefore=14, spaceAfter=9, keepWithNext=True, wordWrap='CJK'),
    'label': ParagraphStyle('label', fontName='KR-Bold', fontSize=8, leading=13, textColor=ACC, spaceBefore=6, spaceAfter=7, keepWithNext=True, wordWrap='CJK'),
}
STYLE['validation-body'] = ParagraphStyle('validation-body', parent=STYLE['body'], leading=16, spaceAfter=7)
STYLE['validation-scope'] = ParagraphStyle('validation-scope', parent=STYLE['muted'], leading=14, spaceAfter=6)
STYLE['validation-heading'] = ParagraphStyle('validation-heading', parent=STYLE['h2'], leading=19, spaceBefore=10, spaceAfter=7)

def P(text, style='body'):
    return Paragraph(escape(str(text)).replace('\n','<br/>'), STYLE[style])

def L(label, url):
    return Paragraph(f'<link href="{escape(url, {chr(34): "&quot;"})}" color="#285943">{escape(label)}</link>', STYLE['link'])

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self.states = []
    def showPage(self):
        self.states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        total = len(self.states)
        for state in self.states:
            self.__dict__.update(state)
            self.draw_page_number(total)
            super().showPage()
        super().save()
    def draw_page_number(self, total):
        p = self.project
        self.setStrokeColor(LINE)
        self.setLineWidth(.6)
        self.line(M, H-33, W-M, H-33)
        self.setFillColor(MUTED)
        self.setFont('KR', 7)
        self.drawString(M, H-24, '김해준 / PORTFOLIO')
        self.drawRightString(W-M, H-24, p['title'])
        self.line(M, 36, W-M, 36)
        self.drawString(M, 24, '자료 업데이트 '+p['sourceUpdated'])
        self.setFont('Helvetica', 7)
        url = f'https://maoemong.github.io/projects/{p["id"]}/'
        self.drawCentredString(W/2, 24, 'maoemong.github.io/projects/'+p['id']+'/')
        self.drawRightString(W-M, 24, f'{self._pageNumber:02d} / {total:02d}')

def make(p):
    d = p['detail']
    file = OUT / f'{p["id"]}-portfolio.pdf'
    doc = SimpleDocTemplate(str(file), pagesize=A4, leftMargin=M, rightMargin=M, topMargin=53, bottomMargin=51,
        title=f'{p["title"]} | 김해준 포트폴리오', author='김해준 (Haejoon Kim) / MaoEmong')
    story = []
    def section(no, label, title, new_page=True):
        if new_page:
            story.append(PageBreak())
        else:
            story.append(Spacer(1, 22))
        story.extend([P(no+' / '+label,'label'),P(title,'h1')])
    def paragraphs(items):
        story.extend(P(t) for t in items)
    def bullet(items):
        for item in items:
            story.append(P('• '+item))
    story.extend([Spacer(1,12),P('SELECTED WORKS / '+p['category'],'label'),Spacer(1,10),P(p['title'],'title'),P(p['tagline'],'lead'),P(p['summary']),L(p['github'],p['github']),L('웹 상세 소개 보기',f'https://maoemong.github.io/projects/{p["id"]}/'),P(' · '.join(p['stack']),'muted')])
    facts = [[P(f['label'],'label'),P(f['value'],'muted')] for f in d['facts']]
    table = Table(facts, colWidths=[90,CW-90], hAlign='LEFT')
    table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,-1),PALE),('LEFTPADDING',(0,0),(-1,-1),11),('RIGHTPADDING',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.extend([Spacer(1,13),table,Spacer(1,23),P('01 / CONTEXT','label'),P('어떤 문제에서 시작했나요?','h1')])
    paragraphs(d['problem'])
    section('02','PRODUCT FLOW','기능과 사용자 흐름')
    for title, body in p['features']:
        story.extend([P(title,'h2'),P(body)])
    story.append(P('한 번의 사용을 따라가 보면','h2'))
    for i,step in enumerate(d['journey'],1):
        story.extend([P(f'{i:02d}  '+step['title'],'h2'),P(step['body'])])
    section('03','ARCHITECTURE','구조와 책임을 나눈 방식',new_page=False)
    for i,item in enumerate(d['architecture'],1):
        story.extend([P(f'{i:02d}  '+item['title'],'h2'),P(item['body'])])
    engineering_start = len(story)
    section('04','ENGINEERING CASES','구현하면서 선택한 것',new_page=False)
    for i,case in enumerate(d['engineering'],1):
        case_story = [P(f'CASE {i:02d} / '+case['title'],'h2'),P('마주한 문제','label'),P(case['problem']),P('선택과 구현','label'),P(case['choice']),P('남은 비용과 한계','label'),P(case['tradeoff']),L(case['source']['label'],case['source']['url']),Spacer(1,12)]
        if i == 1:
            case_story = story[engineering_start:] + case_story
            del story[engineering_start:]
        story.append(KeepTogether(case_story))
    contribution_start = len(story)
    section('05','ROLE & CONTRIBUTION','맡은 역할과 기여',new_page=False)
    paragraphs(d['contribution'])
    contribution_story = story[contribution_start:]
    story[contribution_start:] = [KeepTogether(contribution_story)]
    validation_start = len(story)
    story.extend([Spacer(1,15),P('06 / EVIDENCE & LIMITS','label'),P('무엇을 확인했고, 무엇이 남았나요?','h1'),P('프로젝트 검증 당시의 실행 기록과 코드에 구성한 테스트 항목을 정리했습니다. 각 항목에 실행 조건과 추가 확인이 필요한 범위를 함께 적었습니다.','small')])
    for i,item in enumerate(d['validation']):
        validation_story = [P(item['label'],'validation-heading'),P(item['result'],'validation-body'),P(item['scope'],'validation-scope'),L('검증 근거 보기',item['url'])]
        if i == 0:
            validation_story = story[validation_start:] + validation_story
            del story[validation_start:]
        story.append(KeepTogether(validation_story))
    for title,items in [('현재 범위와 남은 과제',d['limitations']),('다음에 보완할 것',d['nextSteps'])]:
        story.append(KeepTogether([P(title,'validation-heading'),*[P('• '+item,'validation-body') for item in items]]))
    images = p['assets']['images']
    if images:
        screens_start = len(story)
        section('07','SCREENS','프로젝트 화면',new_page=False)
        story.append(P(p.get('imageNote','공개 README에 수록된 프로젝트 화면입니다.'),'small'))
        for image in images:
            image_file = ROOT/image['path'].lstrip('/')
            with PILImage.open(image_file) as pic:
                iw,ih = pic.size
            scale = min(CW/iw, 155/ih)
            figure = Image(str(image_file),width=iw*scale,height=ih*scale)
            figure.hAlign = 'CENTER'
            story.extend([figure,Spacer(1,6),P(image['alt'],'small'),Spacer(1,14)])
        screens = story[screens_start:]
        story[screens_start:] = [KeepTogether(screens)]
    sources_start = len(story)
    section('08' if images else '07','SOURCE MATERIAL','코드와 개발 기록',new_page=False)
    story.append(P('아래 공개 자료에서 구현 범위와 설계 판단을 확인할 수 있습니다. 링크를 누르면 원문으로 이동합니다.'))
    for i,source in enumerate(d['sources'],1):
        story.extend([P(f'{i:02d}  '+source['label'],'h2'),L(source['url'],source['url'])])
    sources = story[sources_start:]
    story[sources_start:] = [KeepTogether(sources)]
    doc.build(story,canvasmaker=lambda *a,**kw:NumberedCanvas(*a,project=p,**kw))
    return file

manifest = {}
for p in DATA:
    file = OUT / f'{p["id"]}-portfolio.pdf'
    if not args.only or p['id'] in args.only:
        make(p)
    if not file.exists():
        raise FileNotFoundError(file)
    reader = PdfReader(file)
    manifest[p['id']] = {'file':file.name,'pages':len(reader.pages),'bytes':file.stat().st_size,'github':p['github'],'updated':p['sourceUpdated']}
    print(json.dumps({'id':p['id'],**manifest[p['id']]},ensure_ascii=False))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Completed {len(manifest)} selected project PDFs.')
