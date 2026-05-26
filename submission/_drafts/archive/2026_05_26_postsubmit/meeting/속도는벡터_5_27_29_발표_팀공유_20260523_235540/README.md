# 속도는벡터 5/27·29 최종 발표 + 5/28 포스터·영상 + 6/11 보고서 팀 공유 패키지

> 작성: 2026-05-23 23:55 KST · 발신: 조현빈 · 수신: 박세은(팀장)·강재현·이동욱
> 본 폴더 = 5/26 23:59 LearnUs deck 마감·5/28 12:00 포스터·영상 마감·5/27·29 최종 발표·6/11 최종 보고서 작업 일괄 정리.

---

## 0. 한 줄 — 이번 패키지가 담은 것

5/23 audit (89% 인과 정정 — 앙상블 평균 효과·latency 무개선) → 박세은 팀장 OK → v14 사전 등록 통제 측정 (1.373 / 9 셀) 완료 → 재프레이밍 신본 deck (claude.ai/design 22 장 transformation 진행 중) + 포스터 prompt + 영상 storyboard + 보고서 §4.2.1 신본 + Codex·Gemini 교차검증 결과까지 본 세션 (5/23 23:14 → close) 일괄 정리.

---

## 1. 핵심 산출물 (본 폴더 + 원본 path)

### 1.1 발표 deck (5/26 23:59 LearnUs 마감 · ★★★ critical path)

| 항목 | 상태 | 위치 |
|---|---|---|
| ★ deck 신본 pptx (22장 transformation 결과) | Phase 3 진행 중 (claude.ai/design "최종발표" 디렉토리) | export 후 `속도는벡터_최종발표_슬라이드_<TS>.pptx` |
| prompt v3 (transformation 지시 — 복붙 sources) | ✅ | `submission/_drafts/속도는벡터_발표deck_재프레이밍_prompt_20260523_110051.md` |
| redline (OLD → NEW 매핑) | ✅ | `submission/_drafts/속도는벡터_발표deck_재프레이밍_redline_20260523_110051.md` |
| storyline NEW (22 장 8 단계) | ✅ | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_20260523_110051.md` |

### 1.2 포스터 (5/28 12:00 마감)

| 항목 | 상태 | 위치 |
|---|---|---|
| 포스터 prompt (900 × 1200 mm 세로 PDF) | ✅ | `submission/_drafts/속도는벡터_포스터_prompt_20260523_235540.md` |
| 포스터 PDF | Phase 4 진행 예정 (claude.ai/design "포스터" 디렉토리) | export 후 `속도는벡터_포스터_<TS>.pdf` |
| QR placeholder | 영상 업로드 후 갱신 | Phase 5 후 |

### 1.3 소개영상 (5/28 12:00 마감)

| 항목 | 상태 | 위치 |
|---|---|---|
| 영상 storyboard (8 슬라이드 300 초) | ✅ | `submission/_drafts/속도는벡터_소개영상_storyboard_20260523_235540.md` |
| 영상 prompt (Veo 3.1 / Clipchamp 등 도구용) | ✅ (storyboard 안 §영상 prompt) | 동일 |
| YouTube 업로드 절차 | ✅ (storyboard 안 §YouTube 업로드 절차) | 동일 |
| 영상 MP4 | 사용자 제작 예정 | 사용자 진행 |
| YouTube URL | 사용자 업로드 후 | placeholder |
| QR 코드 | URL 회수 후 generate | placeholder |

### 1.4 보고서 (6/11 마감)

| 항목 | 상태 | 위치 |
|---|---|---|
| 보고서 신본 (15p compact · §4.2.1 v14 통합) | ✅ | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md` |
| 보고서 PDF | (carry · 재 export 필요 시) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.pdf` (직전 carry) |
| ⚠️ Patch 필요 (Phase 6 carry) | §2.2 Exqutor 식 인용 · §2.3 Cochran 1977 §5.5 → §5.6 | Gemini 발견 (`_internal/state/교차검증_20260523_234500.md`) |

### 1.5 박광현 교수님 사전 보고 (박세은 팀장 검토 후 배포)

| 항목 | 상태 | 위치 |
|---|---|---|
| 사전 보고 신본 (1쪽, 3,061 자, 4 sub-section) | ✅ | `submission/_drafts/속도는벡터_박광현미팅_사전보고_20260524_000000.md` |
| 박세은 팀장 검토 | 사용자 진행 | — |
| 박광현 교수님 배포 | 박세은 → 박광현 (5/24~5/26 사이) | — |

### 1.6 audit·교차검증 결과 (참고 — 발표·보고서 인용 시 carry)

| 항목 | 위치 |
|---|---|
| 정합성 audit (Phase 1) | `_internal/state/메인트랙_정합성audit_20260523_233124.md` |
| Codex·Gemini 교차검증 (Phase 2) | `_internal/state/교차검증_20260523_234500.md` |
| 평결 정본 (A1-A5) | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` |
| 재프레이밍 제안서 | `submission/_drafts/속도는벡터_제출물_재프레이밍_제안_20260523_031402.md` |
| ICDE verbatim 발췌 | `_internal/state/ICDE_verbatim_발췌_20260523.md` |

---

## 2. 팀 합의·배포 절차 (사용자 진행)

### 2.1 카톡 합의 (강재현·이동욱)

1. 박세은 팀장이 강재현·이동욱에게 본 패키지·재프레이밍 제안서·박세은 사전 보고 신본 공유
2. 카톡 또는 미팅으로 NEW 서사 (89% 앙상블 평균·latency 무개선·controlled verification) 합의
3. 합의 후 박세은 → 박광현 사전 보고 배포

### 2.2 박광현 교수님 사전 보고 (박세은 → 박광현)

1. 박세은 팀장이 사전 보고 신본 (`속도는벡터_박광현미팅_사전보고_20260524_000000.md`) 검토
2. 검토 OK 시 박광현 교수님께 메일 또는 미팅으로 배포 (5/24~5/26 사이)
3. 교수님 의견 도착 시 산출물 추가 패치

### 2.3 박성원 멘토 5/24 회신 반영

1. 5/24 (일) 박성원 멘토 3차 자문 회신 예정 — `submission/_drafts/속도는벡터_3차자문요청_20260520_202200.pdf` 베이스
2. 회신 도착 시 storyline·redline·prompt·보고서 §4.2.1 추가 패치

### 2.4 5/26 23:59 LearnUs deck 제출 (★ critical path)

1. deck 신본 pptx final (Phase 3 export 완료 후 검증 통과본)
2. 박세은 팀장이 LearnUs 업로드
3. 마감 시각 23:59 (러너스 자동 마감) — 미리 제출

### 2.5 5/28 12:00 포스터·영상 제출

1. 포스터 PDF final (Phase 4 후) + 영상 YouTube URL (Phase 5 후)
2. 박세은 팀장이 LearnUs 업로드
3. 마감 시각 12:00 정오 (포스터 업체 프린트 일정)

### 2.6 6/11 23:59 보고서·상호평가 제출

1. 보고서 신본 (`_20260523_215000.md`) + ⚠️ Gemini 발견 2건 patch 후 final
2. PDF 재 export (md2pdf compact)
3. 상호평가 (5/26·6/9·6/11 3차) 동시 제출

---

## 3. 핵심 수치 정본 (carry · 5 anchor 정합 확인됨)

| 지표 | 값 | 출처 |
|---|---|---|
| v13 3-way matched 측정 | 1,508 cell × 3 mode | `_internal/cache/rq3/v13_summary.md` |
| 결합 (CaseB) better% | 89.1% (1,344/1,508) | v13 정본 |
| 결합 vs 베이스라인 중앙값 Δ% | −4.38% | v13 정본 |
| 단독 대체 (CaseA) better% | 35.2% / 평균 Δ% +12.90% | v13 정본 |
| 사후 분석 평균 비교군 (CaseB′) | 1.459 (1,226 measurement) | audit §1.2 |
| **★ v14 사전 등록 통제 측정 (9 셀) mean qe_trim** | **1.3729** | v14_summary.md |
| **CaseC vs CaseB (16M 평균) Δ%** | **−6.74% (9/9 셀 우위)** | v14_summary.md |
| **CaseC vs B1 (16M 평균) Δ%** | **−13.31% (9/9 셀 우위)** | v14_summary.md |
| hyperloglog (무작위 해시) | 단독 +2.57% / 평균 −4.58% | audit §1.3 |
| latency 가속 (베이스라인·결합·정답) | 4.43× ≈ 4.46× ≈ 4.54× | audit §4 |
| paired Δ% +0.13% / 노이즈 17% 이하 | 빠름 349 · 느림 379 | audit §4 |

---

## 4. NEW 서사 (carry · 모든 산출물 일관)

본 연구 = Exqutor (arXiv:2512.09695v2) §V-B 적응적 표본 추출의 표본 선택 단계 한 곳 — 무작위 Bernoulli → 분포 인지 stratification — 개입의 효과 controlled verification.

5/23 audit 결과: 89.1% Q-error 우위 = 분포 인지 효과 X · 독립 추정량 평균 효과 ✅. latency 56 cell 무개선 · 구조적 한계 (베이스라인이 이미 정답 plan 회복).

NEW 결론: "통제 실험으로 89% 우위의 진짜 메커니즘 = 평균 효과 임을 규명한 음성·방법론적 결과. 5/23 v14 사전 등록 통제 측정 (9 셀, 1.373) 으로 두 층 evidence 입증 — 사후 분석 (1.459) + 사전 등록 (1.373) 모두 결합 방식보다 정확."

---

## 5. 발표물 룰 (5 산출물 동결)

- **코드명 (B1·CaseA·CaseB·CaseB′·CaseC·oracle·baseline) 노출 금지** — 한국어 라벨 (베이스라인 방식·단독 대체 방식·결합 방식·평균 비교군·사전 등록 통제 측정·기본 엔진·정답)
- **"영역" 필러 / 수식 / 영문 메타 라벨 / ★ 별표 노출 금지**
- **design system 동결**: navy 앵커 · 악센트 4색 · Apple SD Gothic Neo · 흰 배경 · navy → cyan 그라데이션

---

## 6. ⚠️ 잔여 task (Phase 6 carry)

1. **deck 신본 pptx export 완료 후 검증** — Phase 3 진행 중 (claude.ai/design 22 장 transformation)
2. **포스터 PDF 제작** — Phase 4 (claude.ai/design "포스터" 디렉토리, 포스터 prompt 복붙)
3. **영상 MP4 제작·YouTube 업로드** — Phase 5 (storyboard·prompt 따라 사용자 진행)
4. **보고서 §2.2 Exqutor 식·§2.3 Cochran §5.5 patch** — Gemini ❌ 2건 (6/11 마감 전)
5. **카톡 합의 + 박광현 사전 보고 배포** — 사용자 진행
6. **박성원 5/24 회신 반영** — 회신 도착 시 추가 패치

---

작성: 2026-05-23 23:55 KST · 5/27·29 최종 발표·5/28 12:00 포스터·6/11 보고서 일괄 패키지 · 발신 조현빈 → 박세은·강재현·이동욱
