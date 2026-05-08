# _drafts — 팀과 공유할 작업본

이 폴더는 **현재 작업 중인 공유 문서** 를 둔다. 마감 후 정식 파일은 `submission/제출완료/` 로 이동하고, 작업 중간 버전은 `archive/` 로 보낸다.

> **마지막 갱신**: 2026-05-08 14:55 KST — 5/8 19:00 회의 직전 정리 (master_v6 PDX 보강 + 19개 파일 archive 이동)

---

## 📌 현재 상태 (2026-05-08, W4 sprint 종료 직전)

**5/8 19:00 회의 자료 12종 active.** RQ1+RQ2+RQ3 단일 100% 측정 finalize 완료, multi 측정 진행 중. 자문 메일 발송은 회의 후 ~5/15.

### 5/8 회의 핵심 산출물 (12 파일)

| 자료 | 용도 | 비고 |
|---|---|---|
| `팀원_이해용_종합_20260508.{md,pdf}` | 회의 직전 카톡 공유용 종합 자료 (912KB PDF, 36KB md) | 14:50 finalize |
| `속도는벡터_자문메일초안_W4_20260508.{md,pdf}` v6 | 자문 발송용 (채림 석사 + 지도교수) | 14:48, PDX 의제 4 포함 |
| `속도는벡터_5월27일발표_plan_20260508.{md,pdf}` | 5/27 최종발표 plan (slide outline, 31KB md) | 14:49 |
| `속도는벡터_5월8일회의_v1.pptx` (525KB) | 회의 PPT (양식 99% — Apple SD Gothic Neo) | 14:36 |
| `속도는벡터_5월8일회의_v1.pdf` (1.42MB) | PPT PDF 변환본 | 5/7 20:57 |
| `속도는벡터_5월8일회의_v1.html` (56KB) | PPT HTML 미리보기 | 5/7 20:55 |
| `속도는벡터_5월8일회의_v1_image.pptx` (1.41MB) | image 백업 PPT (PDF 폰트 손상 시 fallback) | 5/7 21:58 |
| `속도는벡터_5월8일회의_PPT_outline.md` | 회의 PPT outline (19KB) | 5/7 20:13 |

### Source dir

| 디렉토리 | 용도 |
|---|---|
| `academic_deck_5월8일회의/` | 5/8 회의 deck source HTML (개별 슬라이드 6종) |
| `academic_deck_v3_source/` | 5/27 academic v3 deck source |
| `발표prototype/` | RQ_interactive_prototype.html (5/7 prototype) |

---

## 📊 분석 자료 (별도 dir)

회의 narrative 의 root 데이터:

- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` — 466 lines skeleton (PDX 8 ref)
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` — 871 lines filled (5/8 14:55 PDX 보강)
- `experiments/results/10cell_narrative_종합_20260508.{md,pdf}` — 10 cell × 4강 method 종합
- `_internal/handoff_v9_session_20260508_AM.{md,pdf}` — 인계 v9

---

## 📂 archive/ 구조

```
archive/
├── W4_5월6일~7일_pre회의/  ⭐ 5/8 14:55 신규 — 5/6~5/7 작업본 19종 (5/8 회의 자료에 superseded)
│   ├── 속도는벡터_자문메일초안_W4_20260507.md            v5 → v6 (5/8) 으로 superseded
│   ├── 속도는벡터_자문메일초안_v3_supplement_20260507.md   merged into W4_0508
│   ├── 속도는벡터_자문메일초안_채림석사_20260506.md
│   ├── 속도는벡터_자문메일초안_지도교수_20260506.md
│   ├── 속도는벡터_채림자문_20260507.{md,pdf,_skeleton.md,_메일본문.md}  4 파일
│   ├── 속도는벡터_5월27일발표_slide_outline_20260506.md      → plan_0508 으로 superseded
│   ├── 속도는벡터_5월27일발표_slide_outline_v2_supplement_20260507.md
│   ├── 속도는벡터_5월27일발표_v3_academic.pdf              5/7 v3 → plan_0508 latest
│   ├── 속도는벡터_5월8일회의_v2_supplement_20260507.md
│   ├── 속도는벡터_5월8일회의_1page_summary_20260506.md
│   ├── 속도는벡터_5월8일회의_RQ진행정리_v1.pdf            → 5월8일회의_v1.pdf 으로 superseded
│   ├── 속도는벡터_RQ3_1차결과정리_20260506.{md,pdf}        2 파일
│   ├── 속도는벡터_실험진행공유_20260506.{md,pdf}           2 파일
│   └── 속도는벡터_연구지도확인서_20260505.md
│
├── 자문이메일/         4/15 자문이메일 v1·v2 (md+pdf+docx)
├── 중간발표/           4/17~4/27 발표 자료 빌드 이력
│   └── templates/      디자인 변형 5종 백업 (academic·bold·editorial·gemini·glass)
├── 중간보고서/         v0~v3 반복 빌드 이력 (이동욱 v1, 조현빈 v2 등)
├── 팀원온보딩/         4/17·4/27·4/28 세 버전
└── 프로젝트설명서/     발표 스크립트, 예상질문, 사용설명서
```

---

## 🛠 빌드 명령 (5/8 회의 후 자료 갱신 시 재사용)

```bash
# 마크다운 → PDF (Chrome CDP, 한글 OK)
python3 _internal/scripts/md2pdf.py "submission/_drafts/<파일>.md"

# 마크다운 → DOCX
python3 _internal/scripts/md2docx.py "submission/_drafts/<파일>.md"

# PPT 빌드 (academic deck source dir 기반)
cd submission/_drafts/academic_deck_5월8일회의 && open *.html  # 미리보기
# pptx 변환은 _internal/scripts/build_native_pptx_5_8.py 참조

# pptx → PDF (Keynote AppleScript)
./_internal/scripts/midterm_pptx/convert_pdf.sh <pptx 절대경로>
```

---

## 🔗 관련 문서

- 정식 제출본: `submission/제출완료/`
- 회의록: `_internal/records/kakaotalk/`
- 핵심 plan: `plans/RQ재정립_20260505_2122.md`
- 실험 raw 데이터: `experiments/results/`
- 핵심 narrative: `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md`
