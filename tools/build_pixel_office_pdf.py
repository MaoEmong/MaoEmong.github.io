from pathlib import Path
from urllib.request import urlopen
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/pixel-office-portfolio.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
SHOTS = ROOT / '.work/pixel-office-screenshots'
REPO = 'https://github.com/MaoEmong/pixel-office'
RELEASE = REPO + '/releases/tag/v0.1.2'
VERIFY = REPO + '/blob/main/docs/release/0.1.2/VERIFICATION.md'
GALLERY = REPO + '/blob/main/docs/screenshots/README.md'
SHOTS.mkdir(parents=True, exist_ok=True)
for name in ['01-hero.jpg','03-conversation.jpg','08-stage-history.jpg','14-question-to-lead.jpg','15-command-approval.jpg']:
    target = SHOTS / name
    if not target.exists():
        url = 'https://raw.githubusercontent.com/MaoEmong/pixel-office/main/docs/screenshots/' + name
        with urlopen(url, timeout=30) as response:
            target.write_bytes(response.read())

pdfmetrics.registerFont(TTFont('Korean', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('Korean-Bold', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Korean', normal='Korean', bold='Korean-Bold')
W,H = A4
M = 38
CW = W - 2*M
INK = HexColor('#172238')
MUTED = HexColor('#5C6577')
ACCENT = HexColor('#6554CA')
PALE = HexColor('#F2F0FD')
LIGHT = HexColor('#F4F6FA')
LINE = HexColor('#DEE3EE')
GREEN = HexColor('#16866B')
c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('픽셀 오피스 | 김해준 개발 포트폴리오')
c.setAuthor('김해준 (Haejoon Kim) / MaoEmong')
c.setSubject('AI 작업 관리 Windows 앱: 기능, 구조, 문제 해결, 검증과 배포')

def text(x,top,value,size=10,font='Korean',color=INK):
    c.setFont(font,size); c.setFillColor(color)
    c.drawString(x,H-top-size,value)

def para(x,top,width,value,size=10.2,leading=16,color=INK,bold=False):
    style=ParagraphStyle('p',fontName='Korean-Bold' if bold else 'Korean',fontSize=size,leading=leading,textColor=color,wordWrap='LTR',spaceAfter=0)
    p=Paragraph(value,style)
    _,height=p.wrap(width,1000)
    if top+height>H-58: raise ValueError(f'Text overflow: {value[:45]} -> {top+height}')
    p.drawOn(c,x,H-top-height)
    return height

def box(x,top,width,height,fill=LIGHT,stroke=None,radius=9):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x,H-top-height,width,height,radius,stroke=bool(stroke),fill=1)

def rule(top):
    c.setStrokeColor(LINE); c.setLineWidth(.6);c.line(M,H-top,W-M,H-top)

def label(x,top,value,color=ACCENT): text(x,top,value,8.1,'Helvetica-Bold',color)

def link(x,top,title,url,size=9.2):
    text(x,top,title,size,'Korean',ACCENT)
    width=pdfmetrics.stringWidth(title,'Korean',size)
    c.linkURL(url,(x,H-top-size-3,x+width,H-top+3),relative=0,thickness=0)

def header(page,category,title,summary):
    label(M,27,'PIXEL OFFICE / PORTFOLIO')
    text(W-M-104,26,category,8.2,'Korean',MUTED)
    rule(49)
    title_size=min(22,22*CW/pdfmetrics.stringWidth(title,'Korean-Bold',22))
    text(M,68,title,title_size,'Korean-Bold')
    para(M,108,CW,summary,10.2,16,MUTED)

def footer(page):
    rule(H-43)
    text(M,H-32,'김해준 · MaoEmong',7.5,'Korean',MUTED)
    url='github.com/MaoEmong/pixel-office'
    text(M+125,H-31,url,7.4,'Helvetica',MUTED)
    c.linkURL(REPO,(M+125,18,M+125+pdfmetrics.stringWidth(url,'Helvetica',7.4),35),relative=0,thickness=0)
    text(W-M-30,H-32,f'{page:02d} / 06',7.5,'Helvetica',MUTED)

def screenshot(name,top,width=CW,x=M):
    height=width*1032/1920
    box(x-1,top-1,width+2,height+2,white,LINE,3)
    c.drawImage(str(SHOTS/name),x,H-top-height,width,height,mask='auto')
    c.linkURL(REPO+'/blob/main/docs/screenshots/'+name,(x,H-top-height,x+width,H-top),relative=0,thickness=0)
    return top+height

def small_card(x,top,width,height,title,body):
    box(x,top,width,height)
    text(x+14,top+12,title,11,'Korean-Bold')
    ph=para(x+14,top+36,width-28,body,9.2,14.2,MUTED)
    assert ph+48<=height, (title,ph,height)

def end(page): footer(page);c.showPage()

# 01 / Cover
label(M,31,'PROJECT PORTFOLIO / 2026.10')
text(M,67,'PIXEL OFFICE',39,'Helvetica-Bold')
text(M,118,'픽셀 오피스 · AI 팀의 작업을 관리하는 앱',17.6,'Korean-Bold')
para(M,157,CW,'여러 AI가 무엇을 하고, 누구를 기다리며, 왜 멈췄는지 확인합니다.<br/>부장과의 대화부터 팀 구성·회의·실행·결과 검토를 하나의 화면으로 연결했습니다.',10.5,17,MUTED)
for x,w,t in [(M,77,'Windows x64'),(M+86,119,'Flutter + Node.js'),(M+214,89,'v0.1.2 시험판')]:
    box(x,204,w,24,PALE,radius=5);text(x+10,210,t,8.5,'Korean',ACCENT)
screenshot('01-hero.jpg',247)
text(M,535,'실제 Windows 앱 화면. 대화·작업·사용량은 기능 설명을 위한 예시 데이터입니다.',8.1,'Korean',MUTED)
gap=10; tile=(CW-2*gap)/3
small_card(M,574,tile,79,'01  작업 흐름 통합','대화·회의·계획·단계 기록을<br/>한곳에서 확인')
small_card(M+tile+gap,574,tile,79,'02  실패와 복구','대기 대상·오류 원인을 알리고<br/>기존 요청을 보존')
small_card(M+2*(tile+gap),574,tile,79,'03  Windows 배포','실행 구성품을 함께 묶어<br/>0.1.2 시험판 공개')
box(M,678,CW,63,PALE)
text(M+15,689,'GitHub · 앱 소개 / 스크린샷 / 다운로드',9,'Korean-Bold',ACCENT)
link(M+15,712,REPO,REPO,10.2)
text(M,760,'김해준 (Haejoon Kim)  |  개인 주도 · AI 협업 개발',9.2,'Korean',MUTED)
end(1)

# 02 / Product flow
header(2,'제품과 사용 흐름','목표를 말하고, 중간 결과를 확인한다','터미널을 번갈아 보는 부담을 줄이고, 사용자가 작업 방향과 필요한 승인을 판단하도록 구성했습니다.')
steps=[('01','목표 정리'),('02','팀 구성·회의'),('03','배정·실행'),('04','검토·단계 기록')]
step_w=(CW-27)/4
for i,(number,title) in enumerate(steps):
    x=M+i*(step_w+9);box(x,158,step_w,51,PALE)
    label(x+11,166,number);text(x+11,184,title,9.1,'Korean-Bold')
text(M,232,'부장과의 대화',12,'Korean-Bold')
screenshot('03-conversation.jpg',257,width=435,x=M+(CW-435)/2)
text(M,501,'요청·답변을 구분하고 답변 완료 상태를 표시합니다. 이미지 첨부와 붙여넣기도 지원합니다.',8.9,'Korean',MUTED)
rule(533)
screenshot('08-stage-history.jpg',557,width=255)
text(M+276,553,'단계가 끝나면 기록을 남긴다',11.3,'Korean-Bold')
para(M+276,582,CW-276,'완료한 일, 확인한 결과와 다음 작업을 단계별로 저장합니다.<br/><br/>부장이 완료 기준을 검토해 다음 단계로 진행하고, 사용자는 중간 결과를 다시 읽을 수 있습니다.',10,16)
box(M,716,CW,47,PALE)
para(M+13,727,CW-26,'사용자가 판단할 실행 승인과 로그인 절차는 유지합니다. 단계 진행 자동화가 권한 확인을 대신하지 않습니다.',9.4,14.5)
end(2)

# 03 / Architecture
header(3,'구조와 설계','화면과 실제 AI 실행을 분리했다','각 멤버를 실제 Claude Code·Codex 세션에 연결합니다. 화면과 실행 관리를 분리하고 요청과 결과를 주고받습니다.')
layers=[
 ('Flutter · Dart','사무실 화면 / 대화·회의 / 질문·승인 / 실제 터미널',LIGHT),
 ('Node.js · TypeScript','조직·작업 흐름 / 입력 전달·접수 확인 / 상태 저장·복구',PALE),
 ('Claude Code · Codex CLI','멤버별 실제 실행 세션 / 별도 설치·로그인 필요',LIGHT),
]
for i,(title,body,fill) in enumerate(layers):
    top=160+i*100
    box(M,top,CW,69,fill)
    text(M+17,top+12,title,13,'Korean-Bold')
    text(M+17,top+39,body,10,'Korean',MUTED)
    if i<2:
        mid=M+CW/2;c.setStrokeColor(ACCENT);c.setLineWidth(1.1)
        c.line(mid,H-top-73,mid,H-top-94)
        c.line(mid-3,H-top-89,mid,H-top-94);c.line(mid+3,H-top-89,mid,H-top-94)
        note='WebSocket · 요청과 실시간 상태 변경' if i==0 else '가상 터미널 · 명령 전달 / hooks·MCP · 결과 수신'
        text(M+17,top+78,note,8,'Korean',MUTED)
small_card(M,461,(CW-12)/2,101,'저장과 복구','SQLite에 조직·작업·대기 상태를 저장합니다. 프로젝트별 세션 기록과 함께 재시작 후 이어갈 대상을 판단합니다.')
small_card(M+(CW+12)/2,461,(CW-12)/2,101,'실제 상태와 화면 연결','요청 식별자와 저장된 처리 상태를 기준으로 질문·보고·승인 표시를 갱신합니다. 캐릭터 이동에도 직속 상사 정보를 사용합니다.')
text(M,591,'지시는 아래로, 질문과 보고는 위로',12,'Korean-Bold')
roles=[('사용자','목표·방향·필요한 승인'),('부장','계획·검토·단계 진행'),('팀장','업무 배분·팀원 응답'),('팀원','배정 업무·결과 보고')]
rw=(CW-27)/4
for i,(title,body) in enumerate(roles):
    x=M+i*(rw+9);box(x,622,rw,69,PALE if i==0 else LIGHT)
    text(x+11,634,title,10.5,'Korean-Bold')
    para(x+11,657,rw-22,body,8.2,12,MUTED)
para(M,715,CW,'팀원이 늘어나거나 질문·막힌 업무가 있으면 팀장은 직접 구현보다 위임과 답변을 우선하도록 조정했습니다. 사용자는 부장을 중심으로 진행 상황을 확인합니다.',10,16)
end(3)

# 04 / Reliability: delivery and restart
header(4,'문제 해결 01','메시지를 보냈는데, 계속 기다리던 문제','사용 중 발생한 무한 대기를 입력 접수 확인과 재시작 복구라는 두 지점에서 추적했습니다.')
small_card(M,153,(CW-12)/2,130,'원인','터미널이 문장·줄바꿈을 바꾸면 접수를 놓칠 수 있었습니다. 이전 입력의 늦은 완료 신호가 새 입력의 접수로 잘못 처리될 가능성도 있었습니다.')
small_card(M+(CW+12)/2,153,(CW-12)/2,130,'개선','입력별 고유한 접수 표식을 사용합니다. 질문과 답변은 전달 완료까지 저장하고, 재시작 후 미전달 요청을 복구합니다. 무제한 Enter 재전송은 하지 않습니다.')
text(M,311,'누구의 답변을 기다리는지도 구분',12,'Korean-Bold')
screenshot('14-question-to-lead.jpg',338)
text(M,627,'팀원 → 팀장에게 보낸 질문. 사용자 답변이 필요한 요청과 명확하게 구분합니다.',8.7,'Korean',MUTED)
box(M,665,CW,99,PALE)
text(M+14,678,'재발 방지를 위해 확인한 상황',11,'Korean-Bold',ACCENT)
para(M+14,704,CW-28,'질문 전달·답변 저장 중 재시작, 오래된 접수 신호, 여러 입력의 순서, 답변 도구 누락을 검사했습니다. 접수가 확인되지 않으면 내용을 보존하고 팝업으로 알립니다.',10,16)
end(4)

# 05 / Reliability: UI and decisions
header(5,'문제 해결 02','화면의 대기와 실제 처리 결과를 맞춘다','자동 승인 뒤에도 카드가 남거나, 열린 대화창이 과거 상태를 보여 주면 사용자는 같은 요청을 다시 처리하게 됩니다.')
small_card(M,156,(CW-12)/2,135,'승인 카드가 남던 상황','승인 종료 후 실제 대기 목록을 연결된 화면에 다시 전달하도록 보완했습니다. 이미 답한 요청을 늦게 다시 눌러도 기존 결정을 유지하고 명령을 재실행하지 않습니다.')
small_card(M+(CW+12)/2,156,(CW-12)/2,135,'대화창이 갱신되지 않던 상황','늦게 도착한 과거 조회가 최신 알림을 덮지 못하게 했습니다. 이전 대화를 읽는 위치는 유지하고, 새 답변이 오면 이동할 수 있도록 안내합니다.')
text(M,319,'사용자 판단이 필요한 요청만 명확하게 표시',12,'Korean-Bold')
screenshot('15-command-approval.jpg',346)
text(M,635,'요청한 멤버와 실행 명령을 확인한 뒤 허가·거부합니다. 사진은 승인 상태의 소개 예시입니다.',8.4,'Korean',MUTED)
box(M,670,CW,95,PALE)
text(M+14,682,'확인 방법',11,'Korean-Bold',ACCENT)
para(M+14,708,CW-28,'여러 연결 화면의 승인 목록, 늦게 도착한 반대 결정, 창을 열어 둔 연속 대화, 과거 조회의 지연 도착을 검사했습니다. 정상 안내와 실제 오류 팝업도 구분했습니다.',10,16)
end(5)

# 06 / Evidence and responsibility
header(6,'검증·배포와 역할','검증 결과와 남은 과제를 기록한다','Windows 0.1.2 시험판을 공개했습니다. 아래는 2026-10-22 개발·배포 기록을 기준으로 정리한 자동 검사와 배포본 확인 결과입니다.')
row_data=[
 ('앱 자동 검사','896개 통과','1개 건너뜀 · 0.1.2 공개 검증 기록'),
 ('내부 프로그램 자동 검사','1,347개 통과','15개 건너뜀 · 0.1.2 공개 검증 기록'),
 ('압축 해제본 실행·복구','10개 통과','실제 터미널·이미지 처리·재시작 등'),
 ('배포 파일 대조','1,940개 일치','원본·복원·디버깅 파일 제외 검사'),
]
for i,(title,value,note) in enumerate(row_data):
    top=166+i*51
    if i%2==0:box(M,top,CW,48,LIGHT,radius=4)
    text(M+12,top+12,title,10,'Korean-Bold')
    text(M+232,top+10,value,12,'Korean-Bold',ACCENT)
    text(M+232,top+29,note,8,'Korean',MUTED)
para(M,384,CW,'0.1.2에는 웹 미리보기와 한글 입력 보완이 포함됩니다. 자동 검사에는 모의 AI 응답이 포함됩니다. 통과 수는 실제 AI 작업 전체의 성공 횟수를 뜻하지 않습니다. 배포본 실행 검사는 같은 PC에서 사용자 데이터와 실행 경로를 분리해 수행했습니다.',9.2,14.5,MUTED)
small_card(M,450,(CW-12)/2,113,'직접 주도한 부분','제품 목표·기능 우선순위 결정, 실제 사용 중 문제 제보와 동작 기준 제시, 결과 검토와 공개·배포 방향을 정했습니다.')
small_card(M+(CW+12)/2,450,(CW-12)/2,113,'AI가 지원한 부분','Claude Code·Codex로 원인 분석, 코드 구현, 테스트 작성·실행과 문서 정리를 진행했습니다. 프로젝트 결정과 구현 작업의 역할을 구분해 기록했습니다.')
para(M,585,CW,'남은 과제: 개발 도구가 없는 다른 Windows PC에서의 실행, 실제 계정 조합별 장시간 작업과 로그인 만료 복구 확인. 코드 서명을 하지 않은 시험판이며 정식 안정판으로 안내하지 않습니다.',9.8,15.8)
rule(653)
qr=QrCodeWidget(REPO);b=qr.getBounds();qw=b[2]-b[0];qh=b[3]-b[1]
d=Drawing(83,83,transform=[83/qw,0,0,83/qh,0,0]);d.add(qr)
renderPDF.draw(d,c,M,H-680-83)
text(M+102,674,'공개 GitHub 저장소',11,'Korean-Bold')
link(M+102,698,REPO,REPO,9.2)
link(M+102,722,'Windows 시험판 다운로드',RELEASE,9.1)
link(M+102,743,'검증 기록과 확인 범위',VERIFY,9.1)
text(M,776,'공개 저장소는 소개·사용 안내·배포용입니다. 앱 원본 개발 코드는 비공개입니다.',8.1,'Korean',MUTED)
end(6)
c.save()

reader=PdfReader(OUT)
assert len(reader.pages)==6
all_text='\n'.join(p.extract_text() or '' for p in reader.pages)
for expected in ['픽셀 오피스','김해준','1,347','896','1,940',REPO]:
    assert expected in all_text, expected
links=[]
for page in reader.pages:
    for annot in page.get('/Annots',[]):
        a=annot.get_object().get('/A',{})
        if a.get('/URI'): links.append(str(a['/URI']))
assert REPO in links and RELEASE in links and VERIFY in links
assert not any('pixel-office-dev' in l or 'source-archive' in l for l in links)
assert '\ufffd' not in all_text
print(json.dumps({'file':str(OUT),'pages':len(reader.pages),'bytes':OUT.stat().st_size,'clickable_links':len(links),'github':REPO,'text_check':'passed'},ensure_ascii=False))
