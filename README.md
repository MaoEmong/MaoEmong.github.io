# 김해준 개발 포트폴리오

공개 프로젝트 21개를 목차에서 선택하고, 프로젝트별 설명과 GitHub 저장소·PDF를 확인하는 GitHub Pages 사이트입니다.

- 사이트: https://maoemong.github.io/
- 목록: `index.html`
- 개별 소개: `projects/<프로젝트>/index.html`
- PDF: `output/pdf/<프로젝트>-portfolio.pdf`
- 내용 원본: `data/projects.mjs`
- 사진 목록·출처: `data/assets.json`

EMS, 픽셀 오피스, 이음을 먼저 배치합니다. 원본 앱·서버 저장소의 공개 범위를 변경하지 않으며, 비공개 코드나 계정·작업 기록은 포함하지 않습니다. 설명은 공개 README의 구현 범위와 검사 기록을 기준으로 작성했습니다.

## 로컬에서 보기

저장소 루트에서 정적 웹 서버를 실행합니다. 예를 들어 Python을 사용한다면:

```sh
python -m http.server 8080 --bind 127.0.0.1
```

http://127.0.0.1:8080/ 에서 확인합니다. 직접 HTML 파일을 더블클릭하는 대신 서버를 사용하세요.

## 내용 갱신

`data/projects.mjs`를 수정한 뒤 `node tools/build.mjs`로 목록·소개 페이지를 생성합니다. PDF는 `tools/build_pdfs.py`로 만들고, 파일 정보 표시를 갱신하기 위해 웹 생성기를 다시 실행합니다. PDF 생성에는 Python의 reportlab·Pillow·pypdf와 한글 글꼴이 필요합니다. 기본 글꼴 경로는 Windows의 맑은 고딕입니다.

픽셀 오피스는 이미 검토한 6쪽 PDF를 그대로 유지합니다. PDF 화면 검사는 pdfplumber와 Poppler의 `pdftoppm`을 사용하며, 실행 경로가 등록되어 있지 않다면 `PDFTOPPM`으로 지정할 수 있습니다.

수집·검사 중간 자료와 상세 보완 목록은 로컬 `.work/`에 두며 공개하지 않습니다. 원본 저장소 보완은 사이트·PDF 작성 이후 별도로 진행합니다.

## 외부 구성품

텍스트 크기 계산에 MIT 라이선스의 Pretext 1.0.0을 사용합니다. 실행용 파일과 사용 조건은 `assets/vendor/pretext/`에 포함했습니다. 프로젝트 화면은 각 공개 저장소의 README에서 가져왔으며 출처를 사진 목록에 기록했습니다. 게임 모작은 학습·연습 프로젝트로 구분합니다.
