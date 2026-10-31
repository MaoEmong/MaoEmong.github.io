# 김해준 개발 포트폴리오

웹·백엔드와 AI 서비스 중심으로 선정한 10개 프로젝트의 상세 기술 사례와 PDF를 제공하는 정적 GitHub Pages 사이트입니다.

- 사이트: https://maoemong.github.io/
- 대표: EMS, 이커머스, Support Desk, 이음, 픽셀 오피스, Video Translator
- 추가: Synapse, 여기 한국, LangGraph RAG, 하루 기록
- 목록: `index.html`
- 독립 상세: `projects/<id>/index.html`
- 다운로드 PDF: `output/pdf/<id>-portfolio.pdf`

## 상세 소개의 구성

문제와 사용 맥락, 주요 기능과 사용자 흐름, 아키텍처, 프로젝트별 설계 사례 3개, 본인 역할과 AI 지원 범위, 검증 근거와 한계, 공개 출처를 담았습니다. 웹과 PDF는 같은 원문을 읽습니다. 원본 저장소의 과거 검사 기록을 이번 사이트의 재실행 결과로 표시하지 않습니다.

2026-11-01 갱신: 선정 목록을 22개에서 10개로 정리하고 상세 설명과 PDF를 확장했습니다. 픽셀 오피스는 Windows 0.2.5 공개 문서·화면·다운로드에 맞췄습니다. 기존 비선정 프로젝트 URL과 PDF는 보관하되 메인·사이트맵에서 제외했습니다.

## 로컬 미리보기

저장소 루트에서 실행합니다.

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

http://127.0.0.1:8080/ 에서 확인합니다. 루트 기준 경로를 사용하므로 HTML을 직접 더블클릭하는 대신 웹 서버를 사용하세요.

## 원문과 생성기

- `data/projects.mjs`: 프로젝트 기본 정보·선정 순서·분류. 과거 목록은 보관용입니다.
- `data/details/business.json`: EMS·이커머스·Support Desk의 상세 원문과 출처.
- `data/details/products.json`: 픽셀 오피스·이음·Video Translator의 상세 원문과 출처.
- `data/details/supporting.json`: Synapse·여기 한국·LangGraph RAG·하루 기록의 상세 원문과 출처.
- `data/assets.json`: 이미지 파일·원본 주소·캡션.
- `tools/build.mjs`: 목록·상세·보관 페이지·사이트맵과 PDF용 공통 JSON 생성.
- `tools/build_pdfs.py`: 같은 상세 원문을 자동 페이지 나눔으로 PDF 조판.

Node.js 22 이상과 Python 3.10 이상, `reportlab`, `Pillow`, `pypdf`가 필요합니다. PDF 검사에는 `pdfplumber`와 Poppler의 `pdftoppm`을 사용합니다. 한글 TrueType 글꼴은 macOS 사용자의 `~/Library/Fonts/malgun.ttf`·`malgunbd.ttf`, Windows 맑은 고딕, Linux NanumGothic 순으로 지원합니다. 다른 위치는 `PORTFOLIO_FONT`, `PORTFOLIO_FONT_BOLD`에 지정합니다. 글꼴 파일은 저장소에 포함하지 않습니다.

```sh
node tools/build.mjs
python3 tools/build_pdfs.py
node tools/build.mjs
node --test tools/test-content.mjs
node tools/check.mjs
python3 tools/test-pdfs.py
python3 tools/review_pdfs.py
```

PDF 생성 후 웹 생성기를 다시 실행하면 페이지 수와 파일 크기를 반영합니다. 일부만 갱신하려면 `python3 tools/build_pdfs.py --only commerce`처럼 ID를 지정합니다. 그 외 PDF는 보존하며 선택한 10개 항목의 manifest를 갱신합니다. 별도의 과거 픽셀 오피스 PDF 생성기는 현재 갱신에 사용하지 않습니다.

`tools/check_browser.cjs`는 Playwright가 설치된 환경에서 쓸 수 있는 브라우저 회귀 검사입니다. `PREVIEW_URL`로 서버 주소를 지정합니다. 기본 검사와 별도로 실제 브라우저에서 모바일·데스크톱 표시, 목차·이미지 확대·검색과 PDF 링크를 확인하세요.

## 공개 범위와 구성품

공개 GitHub 자료만 소개에 사용합니다. 비공개 원본 코드·계정·대화와 로컬 검사 중간 자료는 게시하지 않습니다. PDF와 `.work/` 중간 자료를 구분하며 `.work/`·`tmp/`는 Git에서 제외합니다. 프로젝트 화면의 출처와 합성·Mock 여부는 이미지 목록 및 각 소개에 기록합니다.

텍스트 크기 계산에 MIT 라이선스의 Pretext 1.0.0을 사용합니다. 실행 파일과 사용 조건은 `assets/vendor/pretext/`에 포함했습니다. 기존 GoatCounter 방문 집계도 유지합니다. 통계는 https://maoemong.goatcounter.com/ 에서 확인하며 직접 PDF 열기와 차단된 방문은 집계되지 않을 수 있습니다.
