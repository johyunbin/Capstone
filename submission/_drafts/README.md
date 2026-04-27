# _drafts — 팀과 공유할 최신 작업본

이 폴더에는 4 월 28 일 마감 작업의 **최신 공유본** 을 모은다. 같은 문서의 이전 버전은 `archive/` 안에 별도로 보관하므로, 외부 팀원이 처음 들어와도 폴더 직속의 파일만 보면 된다.

> **마지막 갱신**: 2026-04-27 19:04 (4 라운드 보강 + 사용자 수정본 v2 + 발표 스크립트 PDF 추가)

---

## 📌 팀과 공유할 최신본 (정식 파일명, LearnUs 업로드 대상)

| 우선순위 | 파일 | 무엇 |
|---|---|---|
| ⭐ **1** | `속도는벡터_중간보고서.pdf` / `.docx` | **4/28 마감 중간보고서**. 학교 양식 5 장 구조, **18 페이지**, 표 5 + 그림 8 + 페이지 번호 + 폰트 임베딩 완료. 사용자 양식 직접 손봤음 (캡션 두 줄, 표 width 조정 등) — 양식 보존. |
| ⭐ **2** | `속도는벡터_중간발표.pdf` / `.pptx` | **중간발표 자료**, **17 페이지**, Academic Light 디자인. pptx 가 발표 본본이며 pdf 가 LearnUs 제출용. 슬라이드 3·7·8·9·10 글머리표 line spacing 1.40 + slide 10 헤더/본문 박스 좌표 정정. |
| ⭐ **3** | `속도는벡터_중간발표_스크립트.pdf` / `.md` | **발표자(강재현) 본인용 스크립트**, **9 페이지**, 10 분 분량 (총 620 초, 600 초로 단축 가능). 시간 표 + Q&A 분담 가이드 + 발음 주의어 포함. LearnUs 업로드 대상 X (팀 내부용). |
| ⭐ **4** | `팀원 온보딩_20260427.md` / `.pdf` | 팀원 진입용 자료 — §0 (3 분 요약) + 핵심 숫자 5 개 + 4/21 자문 회신 + 4/29~4/30 발표 일정. **25 페이지**. |

---

## 📂 파일 트리

```
_drafts/
├── README.md                                   ← 이 파일 (갱신 4/27 19:04)
│
├── 속도는벡터_중간보고서.pdf                    ⭐ LearnUs 업로드 (18p, 1.34 MB)
├── 속도는벡터_중간보고서.docx                   ⭐ 양식 원본 (사용자 직접 보강)
│
├── 속도는벡터_중간발표.pdf                      ⭐ LearnUs 업로드 (17p, 1.22 MB)
├── 속도는벡터_중간발표.pptx                     ⭐ 발표 본본 (사용자 직접 보강)
│
├── 속도는벡터_중간발표_스크립트.pdf              발표자 본인용 (9p, 0.59 MB)
├── 속도는벡터_중간발표_스크립트.md               원본 마크다운
│
├── 팀원 온보딩_20260427.pdf                    팀원 진입용 (25p, 1.22 MB)
├── 팀원 온보딩_20260427.md                     원본 마크다운
│
└── archive/                                    이전 버전 모음
    ├── midterm_v1_drafts/                       9 디자인 변형 백업 (4/27 16:00)
    ├── midterm_pre_final_20260427_1715/         정식 v1 → v2 전환 백업
    └── midterm_pre_final2_20260427_1740/        정식 v2 → v3+ 전환 백업
```

---

## 📑 중간보고서 v3 의 페이지 구조 (18 페이지)

| 페이지 | 섹션 |
|---|---|
| p.1 | 표지 (제목·팀명·팀원 4 명·박광현 교수님·임채림 석사·2026 년 4 월) |
| p.2 | Contents |
| p.3 | 1. 연구 주제 |
| p.4 | 2. 연구의 필요성 |
| p.5 | 3. 연구 내용 — Ⅰ. Exqutor 의 두 보완책과 단일 테이블 사각지대 + 그림 1 (vector.c snippet) |
| p.6 | 3-Ⅰ 세 단계 연구 질문 (이 사각지대를 다음 세 단계의 …) |
| p.7 | 3-Ⅱ. RQ1 — 사각지대의 구조적 한계 확인 (첫째·둘째·셋째 발견) |
| p.8 | 3-Ⅱ 넷째 발견 — query feature 사전 식별 불가 + 그림 2 (Phase 5 heatmap) |
| p.9 | 3-Ⅲ. RQ2 — 두 단계 sanitize + (1) RQ2-1 검증 + 표 1 |
| p.10 | (1) Selectivity 0.050 이상 4 구간 통계 + 그림 3 (Phase 4 scatter 2×2) |
| p.11 | (2) RQ2-2 검증 — Stratified sampling 5-seed + 표 2 |
| p.12 | 그림 4 (boxplot) + 그림 5 (cross-dataset bar) |
| p.13 | 그림 6 (selectivity gradient) |
| p.14 | (3) Two-Level Decomposition + 그림 7 (Two-Level 분해) |
| p.15 | (4) HHI 와 CV + 그림 8 (cluster skew) |
| p.16 | 3-Ⅳ. RQ3 — 분포를 모르는 환경으로의 확장 (설계) + 표 3 |
| p.17 | 4. 현재 진행 상황 |
| p.18 | 5. 일정 및 역할 배분 + 표 4 (학기 전체 일정) + 표 5 (역할 분담) |

---

## ✅ 캡스톤 공식 가이드 6 필수 항목 매칭

| 필수 항목 | 본 보고서 위치 |
|---|---|
| 해결하고자 하는 문제 | 1. 연구 주제 + 2. 연구의 필요성 |
| 기존 연구의 현황 및 한계점 | 2. 연구의 필요성 + 3-Ⅰ |
| 기존 연구와의 차별성 및 제안하는 연구의 중요성 | 3-Ⅰ (사각지대 = 원논문에 명시되지 않은 빈자리) |
| 연구 및 실험 방법 | 3-Ⅱ (RQ1) + 3-Ⅲ (RQ2) + 3-Ⅳ (RQ3) |
| 현재까지의 진행 상황 및 향후 계획 | 4. 현재 진행 상황 + 5. 일정 |
| 팀원별 역할 분담 | 5. 일정 및 역할 배분 (표 5) |

---

## 📤 제출 절차 (4/28 화 23:59 LearnUs)

1. ⭐ 1 + ⭐ 2 (보고서 PDF + 발표 PDF) 두 파일을 대표 팀원이 LearnUs 분반 게시판에 업로드.
2. **PDF 변환 옵션**: "전자 배포" (Electronic Distribution) — LearnUs 화면 검토용, 인쇄 X.
3. 발표는 4/29 (수) 15:00 D508 또는 4/30 (목) 19:00 A428 중 분반 시간 참조.

---

## 🛠 빌드 명령

```bash
# 보고서 재빌드 (단, 사용자가 직접 docx 손본 상태이므로 build 재실행은 양식 손실 위험)
python3 _internal/scripts/_build_docx_v1.py

# 발표 재빌드
cd _internal/scripts/midterm_pptx
python3 build_academic.py /Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표.pptx

# 마크다운 → PDF (Chrome CDP, 한글 OK)
python3 _internal/scripts/md2pdf.py "submission/_drafts/속도는벡터_중간발표_스크립트.md"

# pptx → PDF (Keynote AppleScript)
./_internal/scripts/midterm_pptx/convert_pdf.sh /Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표.pptx

# docx → PDF (Microsoft Word AppleScript)
osascript << 'EOF'
tell application "Microsoft Word"
  activate
  open POSIX file "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간보고서.docx"
  delay 4
  set theDoc to active document
  save as theDoc file name "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간보고서.pdf" file format format PDF
  delay 3
  close theDoc saving no
end tell
EOF
```

---

## 📅 발표 일정

- **4/29 (수) 15:00 ~ 15:50** — 인종 D508
- **4/30 (목) 19:00 ~ 21:00** — 인종 A428
- 팀당 발표 10 분 + 질의응답 5 분 (10 분 초과 시 강제 중단)

---

## 🔗 관련 문서

- 팀 온보딩: `팀원 온보딩_20260427.pdf`
- 발표 스크립트 (10 분 분량): `속도는벡터_중간발표_스크립트.pdf`
- 회의록: `_internal/records/kakaotalk/20260425_중간보고서 작성 피드백 및 회의 제안.md`
- 평가서: `_internal/records/kakaotalk/20260427_중간보고서 docx 평가.md`
- RQ3 7 가지 비교 설계: `plans/RQ3설계안_20260416_213500.md`
- 실험 raw 데이터: `experiments/results/rq1_motivation/` + `experiments/results/rq2_aware/`
