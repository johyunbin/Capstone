# Ultra-Review — plans/ + reference/ (2026-05-08 22:30 KST)

> **에이전트**: U3 (Capstone background agent)
> **범위**: `plans/` cleanup + `reference/` inventory
> **방침**: plans/ 의 stale design 안만 archive/ 로 이동, reference/ 는 보존 + 점검만 수행
> **commit hash**: `e6a12b5`

---

## 1. plans/ inventory + cleanup

### Active (5/8 22:30 finalize)

| 문서 | 날짜 | 위치 | 상태 |
|------|------|------|------|
| `RQ재정립_20260505_2122.md` | 5/5 | plans/ | ★ 최신 v6 — RQ1/RQ2/RQ3 재정립 |
| `최종보고서_outline_v2_20260508.md` | 5/8 21:45 | plans/ | ★ 최신 v2 — 6/11 outline (516 lines) |
| `5_8_19시_회의_outline.{md,pdf}` | 5/6 | plans/ | 오늘 회의 outline (회의 종료, 회의록으로 이관 예정) |
| `README.md` | 5/8 갱신 | plans/ | 최신 상태 반영 |
| `_drafts/2026_05_06_8m_midsel_narrative_draft.md` | 5/6 | plans/_drafts/ | 8M mid-sel 보강 narrative draft |
| `_drafts/2026_05_08_회의록_template.md` | 5/6 | plans/_drafts/ | 회의 직후 채울 template |
| `_drafts/2026_05_12_W2_분담표_template.md` | 5/6 | plans/_drafts/ | W2 sprint 분담 template |

### Archived (이번 cleanup, plans/archive/2026_05_08_supersed/)

| 문서 | 원본 | 사유 |
|------|------|------|
| `최종보고서_outline_v1_20260507.md` | 5/7 12:25 | outline v2 (5/8 21:45) 로 superseded |
| `RQ3설계안_20260416_213500.md` | 4/16 | RQ재정립 v6 (5/5) 로 superseded |
| `RQ3설계안_20260416_213500.pdf` | 4/16 | (md 와 같이 이동) |
| `연구재설계안_20260415_131400.md` | 4/15 | RQ재정립 v6 (5/5) 로 superseded |

### archive/ 루트 (기존 보존)

5개 문서 — 4/3 v3 연구설계안 / 4/15 v4 수정안 / 연구제안서 + 수행계획서 (LearnUs 제출분 사본) / 프레이밍 두-단계 draft. 변경 없음.

---

## 2. reference/ inventory (보존 + 점검)

### 개수 점검

| 디렉토리 | 파일 수 | 자료 수 | 상태 |
|----------|--------|--------|------|
| `papers/` | 69 PDF | 69 논문 | 번호 [0]~[81] (13 결번 — 13개 summary 가 논문 PDF 없는 web/blog/repo 자료) |
| `summaries/` | 164 (md+pdf 페어) | 82 총정리 | 번호 [0]~[81] 완전 cover |
| `analysis/` | 24 (md+pdf 페어) | 12 시리즈 | (01)~(12) 연속 numbering |

### papers/ vs summaries/ 갭

papers/ 에 PDF 없는 13개 summary: `[12] Qdrant`, `[13] pgvector`, `[21] DNA Sequence`, `[28] Chroma`, `[31] DuckDB-VSS`, `[35] K-NN`, `[37] Generalized K-NN`, `[46] Annoy`, `[50] Exact Cardinality (bounded)`, `[61] Misinformation`, `[64] Wikipedia`, `[75] Vector DB Benchmark`, `[80] Selectivity Cost (Joins)`. 모두 web/blog/GitHub/repository 출처 자료로 PDF 부재가 자연스러움. **갭 없음**.

### naming 일관성 점검

- **papers/**: `[N] Title; Subtitle.pdf` 패턴, `;` 는 콜론 대체 (filesystem). Title Case 준수, 약어 대문자 유지 (HNSW, GPU, LSH). **위반 0건**.
- **summaries/**: `[N] Title Subtitle 총정리.{md,pdf}` 패턴, 콜론·세미콜론 미사용. Title Case + 약어 대문자 (`ACORN`, `K-Nearest Neighbor`, `pgvector`) 준수. **위반 0건**.
- **analysis/**: `(NN) 제목.{md,pdf}` 패턴. (01)~(12) 연속, 한글 제목 자연어 띄어쓰기 정합. **위반 0건**.

### 미세 불일치 (정정 불필요)

`papers/[76] Acorn; Performant ...pdf` (PDF 원제 따라 'Acorn') vs `summaries/[76] ACORN Hybrid ...md` (acronym 우선 'ACORN'). **CLAUDE.md 규칙은 acronym 대문자 = summaries 측이 맞음**. PDF 측은 원파일명 보존 원칙으로 그대로 둠. 양쪽 모두 내부 일관성 유지하므로 **rename 보류**.

### 핵심 자료 보존 확인

- `[0] Exqutor` (papers + summaries 양쪽 존재) ✅
- `[71] PDX` (SIGMOD 2025, RQ3 학술 confirmation) ✅
- `(01)~(12) analysis` 시리즈 (Exqutor 상세분석 + 레퍼런스 6/24/81 분석 + 미팅준비 심층분석) ✅
- 모두 보존, 이동 없음.

---

## 3. 산출 요약

- **이동**: plans/ stale 4 파일 → `plans/archive/2026_05_08_supersed/`
- **재명명**: 0건 (papers/summaries/analysis 모두 일관성 양호)
- **README 갱신**: `plans/README.md` 최신 상태 반영 (active 7건 + archive 매트릭스 2단)
- **commit**: 다음 step 에서 ultra-review 메시지로 finalize

reference/ 175 파일 (papers 69 + summaries 164 + analysis 24 + README 등) 완전 보존. 보고서 drafting 과정에서 활용도 손상 없음.
