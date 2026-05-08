# _drafts — 팀과 공유할 작업본

이 폴더는 **현재 작업 중인 공유 문서** 를 둔다. 마감 후 정식 파일은 `submission/제출완료/` 로 이동하고, 작업 중간 버전은 `archive/` 로 보낸다.

> **마지막 갱신**: 2026-05-08 22:30 KST — 회의 종료 후 cleanup 정리. v3/v4 active 만 _drafts/ 잔존, 이전 버전은 `archive/2026_05_08_drafts_cleanup/` 으로 이동.

---

## 📌 현재 상태 (2026-05-08, W4 sprint 종료)

**5/8 19:00 회의 자료 finalize.** RQ1+RQ2+RQ3 단일 100% 측정 + multi-vector 4강 일반화 + multi-table-join 4강 (STAGE 3, 5/8 17:50) 모두 완료. shrinkage chain 17.13 → 0.67 → 0.68% 25.2× 확정. 자문 메일 발송은 회의 후 ~5/15.

5/8 회의 발표 본체는 **Claude Design 16-slide academic deck** (사용자 카톡 link 직접 공유). 본 _drafts 는 그 보조 문서들.

---

## 🎯 회의 보조 자료 — 3 파일 통합 narrative

목적별 3 파일로 통합 (구체적 / 핵심 요약 / 초보자용):

| 우선 | 파일 | 용도 | 사이즈 |
|:-:|---|---|---:|
| ⭐⭐⭐ | **`팀원_요약_20260508.{md,pdf}`** | 1장 핵심 요약 (5 결과 + 4 의제 + timeline) | ~2 KB md / ~420 KB PDF |
| ⭐⭐ | **`팀원_슬라이드가이드_20260508.{md,pdf}`** | **초심자용** — slide 따라가는 풀어쓰기 + 비유 + 학술 용어 사전 | ~25 KB md / ~830 KB PDF |
| ⭐ | **`팀원_이해용_종합_20260508.{md,pdf}`** | 학술 narrative 상세 (회의 본격 토론용) | ~38 KB md / 975 KB PDF |

**카톡 공유 권장 조합**:
- (필수) Claude Design 16-slide deck **link** + `팀원_요약_20260508.pdf`
- (옵션) `팀원_슬라이드가이드_20260508.pdf` (slide 보면서 함께 읽기)

---

## 📋 회의 후 active 자료 (W2 자문 발송 / 지도확인서)

| 자료 | 용도 | 비고 |
|---|---|---|
| `속도는벡터_연구지도확인서_20260508_v3.{md,pdf}` | 연구 지도 확인서 (5/22 미팅 + 6/11 보고서 reference) | v3, narrative 축소 → method 선정 단계까지만 |
| `속도는벡터_자문메일_박성원멘토_20260508_v4.md` | 자문 발송용 (박성원 멘토, 5/15~5/20 발송 예정) | v4, W4 sprint 결과 반영 |

> 5/27 발표 outline 은 별도 plan 문서 대신 본 deck (`속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}`) 자체로 대체. 이전 outline plan PDF 는 archive/ 로 이동.

---

## 🎨 5/27 발표 deck (academic v3, W4 finalize)

| 자료 | 용도 | 사이즈 |
|---|---|---:|
| ⭐ **`속도는벡터 — Academic v3 · Final 5_27.pdf`** | **발표 본체 PDF** (Claude Design export, 5/8 17:58) | **936 KB, 16 pages** |
| `속도는벡터 — Academic v3 · Final 5_27.pptx` | 발표 본체 PPTX (Claude Design export) | 1.05 MB |
| `academic_deck_v3_source/academic-deck/` | source HTML (index.html, Slides.jsx, deck-stage.js) — Claude Design archive 적용 (5/8 17:40) | — |
| `academic_deck_v3_W4_finalize.zip` (49 KB) | source 압축 — 카톡 첨부 가능 form | 49 KB |

**deck 구성**: 16 slide (Cover / TOC / Problem / Prior+PDX / Approach / RQ1 / RQ2 / RQ3 4강 / Hilbert+Tier1 / MiniBatch / Sweet Spot / Cross-scale / Mechanism+Multi 25.4× / Effect / Limitation / Closing) + 한국어 speaker notes 16개 (12분 분량) + 차트 hand-coded SVG.

**deck 사용**:
- 카톡 공유 = Claude Design link 으로 직접 공유 (사용자 권장)
- 또는 zip 다운로드 후 `index.html` 브라우저 열기
- ⌘P → "PDF로 저장" 시 16 slide 1 페이지씩 print-friendly (deck-stage `@media print`)

---

## 📊 분석 자료 (별도 dir, _drafts 외)

회의 narrative 의 root 데이터:

- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.{md,pdf}` (1.6 MB PDF, 871+ lines) — 분석 본체 (§multi-2 + §10.6 multi 25.4× narrative 반영)
- `experiments/results/10cell_narrative_종합_20260508.{md,pdf}` — 10 cell × 4강 method 종합
- `_internal/handoff_v10_session_20260508_PM.{md,pdf}` — 5/8 16:20 인계
- `_internal/handoff_v11_session_20260508_PostMeeting.md` — 회의 후 update skeleton

---

## 📂 archive/ 구조

```
archive/
├── 2026_05_08_drafts_cleanup/  ← 5/8 22:30 cleanup, v3/v4 로 superseded 된 파일들
│   ├── 속도는벡터_연구지도확인서_20260508_v2.md (v3 로 superseded)
│   ├── 속도는벡터_자문메일초안_W4_20260508_v6.pdf (v4 md 로 superseded)
│   └── 속도는벡터_5월27일발표_plan_20260508.pdf (deck 으로 대체)
├── 5_8_회의_v1_PPT/        ← 5/8 v1 PPT 관련 (Claude Design deck 으로 대체됨, 5/8 17:55 이동)
│   ├── 속도는벡터_5월8일회의_v1.pptx (525 KB, 양식 99%)
│   ├── 속도는벡터_5월8일회의_v1.{html,pdf}
│   ├── 속도는벡터_5월8일회의_v1_image.pptx (image backup)
│   ├── 속도는벡터_5월8일회의_PPT_outline.md (5/7 outline)
│   └── academic_deck_5월8일회의/ (5/7 prototype HTML)
├── W4_5월6일~7일_pre회의/   ← 5/6~7 pre-회의 work-in-progress (19 파일)
├── 발표prototype/          ← RQ_interactive_prototype.html (5/7)
├── 자문이메일/             ← 4/15 발송 archive (v1, v2)
├── 중간발표/               ← 4/30 중간발표 archive (templates + history)
├── 중간보고서/             ← 4/28 중간보고서 archive (history)
├── 팀원온보딩/             ← 4/27 온보딩 archive
└── 프로젝트설명서/         ← 4/28 프로젝트 설명서 archive
```

---

## 🔄 파일 버저닝 규칙

- **현재 작업본** = 본 폴더 (`_drafts/`)
- **이전 버전** = `archive/` (회의 후 정리 시 이동)
- **마감 후 정식** = `submission/제출완료/` (LearnUs 또는 멘토 발송 완료 자료)

---

## 📅 다음 작업 (5/8 회의 종료 후)

1. ✅ 회의 종료 (5/8 19:00~19:30, 비대면 전원) — 결정 3가지: Adaptive Sampling 비교 / 5/27 발표 / SF100 시간 여유 시
2. 5/9~5/15: 자문 메일 v4 발송 (박성원 멘토) + 회신 대기 + Adaptive 비교 측정 launch
3. 5/22 교수님 미팅 — 연구지도확인서 v3 reference
4. 5/27 최종발표 — Academic v3 deck 본체 + 자문 합의 supplementary slide
5. 6/11 최종보고서 (~38p) drafting
