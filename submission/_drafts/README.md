# _drafts — 팀과 공유할 작업본

이 폴더는 **현재 작업 중인 공유 문서** 를 둔다. 마감 후 정식 파일은 `submission/제출완료/` 로 이동하고, 작업 중간 버전은 `archive/` 로 보낸다.

> **마지막 갱신**: 2026-05-08 17:55 KST — 5/8 19:00 회의 직전 정리 (3 파일 통합 narrative + 5/8 v1 PPT archive 이동)

---

## 📌 현재 상태 (2026-05-08, W4 sprint 종료 직전)

**5/8 19:00 회의 자료 finalize.** RQ1+RQ2+RQ3 단일 100% 측정 + multi-vector 4강 일반화 완료, multi-table join (STAGE 3) 측정 진행 중. 자문 메일 발송은 회의 후 ~5/15.

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

## 📋 회의 의제 자료

| 자료 | 용도 | 비고 |
|---|---|---|
| `속도는벡터_자문메일초안_W4_20260508.{md,pdf}` | 자문 발송용 (채림 석사 + 지도교수님) | v6, PDX 의제 4 포함 + multi 4강 일반화 update |
| `속도는벡터_5월27일발표_plan_20260508.{md,pdf}` | 5/27 최종발표 plan (slide outline) | §S13 multi 25.4× shrinkage 반영 |

---

## 🎨 5/27 발표 deck (academic v3, W4 finalize)

| 자료 | 용도 |
|---|---|
| `academic_deck_v3_source/academic-deck/` | 5/27 발표 deck source (index.html, Slides.jsx, deck-stage.js) — Claude Design archive 적용 (5/8 17:40) |
| `academic_deck_v3_W4_finalize.zip` (49 KB) | source 압축 — 카톡 첨부 가능 form |

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
├── 5_8_회의_v1_PPT/        ← 5/8 v1 PPT 관련 (Claude Design deck 으로 대체됨, 5/8 17:55 이동)
│   ├── 속도는벡터_5월8일회의_v1.pptx (525 KB, 양식 99%)
│   ├── 속도는벡터_5월8일회의_v1.{html,pdf}
│   ├── 속도는벡터_5월8일회의_v1_image.pptx (image backup)
│   ├── 속도는벡터_5월8일회의_PPT_outline.md (5/7 outline)
│   └── academic_deck_5월8일회의/ (5/7 prototype HTML)
├── 발표prototype/          ← RQ_interactive_prototype.html (5/7)
└── (이전 19 archive 파일들, 5/6~7 work-in-progress)
```

---

## 🔄 파일 버저닝 규칙

- **현재 작업본** = 본 폴더 (`_drafts/`)
- **이전 버전** = `archive/` (회의 후 정리 시 이동)
- **마감 후 정식** = `submission/제출완료/` (LearnUs 또는 멘토 발송 완료 자료)

---

## 📅 다음 작업 (5/8 회의 후)

1. handoff_v11 update (회의 4 의제 결정 사항 반영)
2. 자문 메일 발송 결정 (Option A: 회의 직후 / Option B: 5/9~10 v7 후)
3. master_v6 v7 작성 (회의 narrative 합의 결과)
4. STAGE 3 multi-table join 결과 도착 시 master_v6 §multi-2 + Slides.jsx S13 추가 반영
5. 5/27 plan v2 (자문 회신 ~5/15+ 후)
