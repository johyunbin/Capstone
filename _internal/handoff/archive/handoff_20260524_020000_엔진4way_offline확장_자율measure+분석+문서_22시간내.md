# handoff 20260524 02:00 — 엔진 4-way + Offline CaseC 1,508 cell 확장 · 자율 측정 + 분석 + 3-multi-model 검증 + 문서 (22 시간 내)

> 직전 handoff (`handoff_20260524_000200_본세션완주_deck재프레이밍+포스터+영상+교차검증+팀공유.md`) → 본 문서. 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 사용자 전권 위임 + 5/24 23:59 KST (~22 시간) 안 마무리 — (1) **엔진 탑재 4-way 측정** (B1·CaseA·CaseB·CaseC) pgvector × scale factor 전체 × cell 전체 × selectivity 전체 전수 + (2) **Offline CaseC 1,508 cell 확장** (v14 9 cell → 25 cell portfolio 또는 더) + (3) **데이터 취합 + storyline·deck·보고서 patch + md + pdf** + (4) **3-multi-model (Claude·Codex·Gemini) 교차 검증**. 메인 세션 자율 진행, 사용자 자러 감.

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (carry)**: `_internal/handoff/active/handoff_20260524_000200_본세션완주_deck재프레이밍+포스터+영상+교차검증+팀공유.md` — 본 세션 (5/23 23:14 → 5/24 02:00) 의 일부 작업 (deck v2 신본 prompt 작성·복붙·AI 작업·PPTX export·포스터/영상 brief·룰·메모리) carry
- **★ deck v2 신본 PPTX**: `submission/_drafts/속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx` (1.13 MB · 15 slide · raster burned-in) — 본 세션 5/24 01:40 export 완료
- **★ storyline NEW v2**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md` (15 슬라이드 · 10분 · ICDE arc)
- **★ v14 CaseC 9 cell q-error 정본**: `_internal/cache/rq3/v14_summary.md` (mean qe_trim 1.3729 · 9/9 셀 우위)
- **★ v13 1,508 cell 정본**: `_internal/cache/rq3/v13_summary.md` + `aggregated_v13_full.parquet` (4,524 row = 1508×3 mode)
- **★ phase2 engine latency 정본**: `_internal/cache/rq3/latency/phase2*.log` + `poc_6_4/summary.md` (12 cell B1·CaseB·oracle · 56 cell paired Δ% +0.13%)
- **★ measure_latency_realengine.py**: `_internal/scripts/measure_latency_realengine.py` (현재 baseline·B1·CaseB-by-method·oracle variants 만 — CaseA·CaseC 추가 patch 필요)
- **★ measure_paper_exact.py**: `_internal/scripts/measure_paper_exact.py` (line 1195 `measure_case_c` 함수 — dual-Bernoulli ensemble, v14 9 cell launch 시 검증됨. 1,508 cell 또는 25 cell 확장 가능)
- **★ 포스터 prompt + 시각 자산 brief (Nano Banana Pro)**: `submission/_drafts/속도는벡터_포스터_prompt_20260523_235540.md` + `..._Nano_Banana_Pro_brief_20260524_010021.md`
- **★ 영상 storyboard + Veo 3.1 brief**: `submission/_drafts/속도는벡터_소개영상_storyboard_20260523_235540.md` (v2 신본 15장 매핑 patch 완료) + `..._Veo_3_1_brief_20260524_010021.md`
- **★ 평결 정본 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`
- **★ 재프레이밍 제안서 (carry)**: `submission/_drafts/속도는벡터_제출물_재프레이밍_제안_20260523_031402.md`
- **★ 보고서 신본 (carry)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md` (Gemini ❌ §2.2 Exqutor 식 · §2.3 Cochran §5.5/§11.10 patch 필요)

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor (arXiv:2512.09695v2) §V-B 적응적 표본 추출의 표본 선택 단계 한 곳 — 무작위 Bernoulli → 분포 인지 stratification — 개입의 효과 controlled verification. 3-way matched (B1·CaseA·CaseB 1,508 cell) + 4-way 확장 (CaseC dual-Bernoulli pre-registered, 5/23 9 셀 · 1.373 mean qe_trim).

5/23 audit 평결: 89.1% Q-error 우위 = 분포 인지 효과 X · 앙상블 평균 효과 ✅. CaseC = (B1+B1)/2 dual-Bernoulli 통제군. NEW 서사 = "통제 실험으로 89% 우위 진짜 메커니즘 = 평균 효과 규명한 음성·방법론적 결과".

박광현 5/22 #1·#3(reject)·#4 처리 완료. 박성원 멘토 3차 자문 회신 = 5/24 (일) 예정.

## 2. 본 세션이 한 일 (2026-05-24 00:00 → 02:00 KST · 2 시간)

| 항목 | 상태 | 내용 |
|---|---|---|
| storyline NEW v2 (15장 · 10분 · ICDE arc) 신본 작성 | ✅ | `속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md`. v22 22장 → v2 15장 압축 + narrative arc 6 단계 |
| deck v2 신본 prompt 작성 (claude.ai/design 용) | ✅ | `속도는벡터_발표deck_재프레이밍_prompt_v2신본15장_20260524_002513.md` (28.5 KB · 코드블록 17.7 KB / 196 줄) |
| claude.ai/design 자동화 (Chrome MCP macmini) | ✅ | macmini Chrome 진입 → input 박스에 17.7KB clipboard paste → Send. AI 가 v21·v22 무시하고 15장 신본 완전 새로 생성 |
| PPTX export 완료 | ✅ | `속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx` (1.13 MB · 15 slide · raster burned-in) — 슬라이드 11 4갈래 도식 + "세 화살표 동일 굵기" + "동등" 메시지 검증 완벽 ✓ |
| 포스터 Nano Banana Pro 5 자산 brief | ✅ | `속도는벡터_포스터_시각자산_Nano_Banana_Pro_brief_20260524_010021.md` |
| 영상 Veo 3.1 hero/transition/close brief | ✅ | `속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md` |
| 영상 storyboard 슬라이드 매핑 patch (v22 22장 → v2 신본 15장) | ✅ | `속도는벡터_소개영상_storyboard_20260523_235540.md` 10 Edit |
| 전역 룰 강화 (`~/.claude/rules/multi-model.md`) | ✅ | Gemini Ultra 강점 + Claude×Gemini 협업 + Chrome MCP macmini 무조건 |
| Claude 전역 메모리 2 신규 | ✅ | `feedback_chrome_browser_choice.md` + `feedback_gemini_ultra_advantages.md` |
| Capstone 메모리 1 신규 + MEMORY.md 갱신 | ✅ | `feedback_design_x_gemini_collab.md` |
| Capstone CLAUDE.md Multi-Model 라우팅 | ✅ | "Multi-Model Workflow (Gemini Ultra 적극 활용)" + "Chrome MCP — macmini 무조건" |
| Phase A 점검 (v13·v14·phase2·서버 자원) | ✅ | v13 1,508 cell × 3 mode 완료 · CaseC 1,508 cell 미측정 · phase2 12 cell × 3-way 완료 · CaseA·CaseC latency 미측정 · 서버 available 765GB · CPU load 8% · disk 1.4TB |

## 3. ★ 핵심 수치·결과 정본 (carry · 본 세션 점검 후 확정)

| 지표 | 값 | 출처 |
|---|---|---|
| v13 3-way matched 측정 | 1,508 cell × 3 mode (4,524 row) | `v13_summary.md` |
| B1 mean qe_trim | 1.4582 | v13 |
| CaseA mean qe_trim | 1.6359 | v13 |
| CaseB mean qe_trim | 1.4019 | v13 |
| 결합 (CaseB) better% vs B1 | 89.1% (1,344/1,508) | v13 |
| 결합 vs 베이스라인 중앙값 Δ% | −4.38% | v13 |
| 단독 대체 (CaseA) better% | 35.2% / 평균 Δ% +12.90% | v13 |
| 사후 분석 평균 비교군 (CaseB′) | 1.459 (1,226 measurement) | audit §1.2 |
| ★ v14 사전 등록 통제 측정 (CaseC, 9 셀) mean qe_trim | **1.3729** | v14_summary.md |
| CaseC vs CaseB Δ% (9/9 셀 우위) | −4.38% ~ −8.99% | v14_summary.md |
| CaseC vs B1 Δ% (9/9 셀 우위) | −12.04% ~ −15.29% | v14_summary.md |
| **phase2 engine latency 12 cell (B1·CaseB·oracle)** | paired Δ% B1↔CaseB +0.13% | poc_6_4/summary.md |
| 4.43× ≈ 4.46× ≈ 4.54× (B1·CaseB·oracle 가속) | phase2 12 cell | audit §4 |
| paired Δ% +0.13% · 노이즈 17% 이하 · 빠름 349 / 느림 379 | latency 56 cell | audit §4 |

## 4. ★ 다음 세션 task — 자율 측정 + 분석 + 문서 + 검증 (22 시간 내, 사용자 자러 감)

### Phase 1: 측정 코드 patch (~45 분)

1. **`measure_latency_realengine.py` patch** — line 340-343 variants 정의에 **CaseA · CaseC 추가**:
   ```python
   variants = [("baseline", None, None), ("B1", None, est_b1),
               ("oracle", None, true_card)]
   # CaseA: method 단독 (16 method 평균 inject — method-agnostic mean variant)
   if est_caseA_mean is not None:
       variants.append(("CaseA", "mean", est_caseA_mean))
   # CaseB: method-by-method (carry)
   for m, est in caseb_by_method.items():
       variants.append(("CaseB", m, est))
   # CaseC: dual-Bernoulli ensemble (method-agnostic)
   if est_caseC is not None:
       variants.append(("CaseC", None, est_caseC))
   ```
2. **`gen_latency_estimates.py` patch** — cell 별 est_caseA_mean·est_caseC 추가 산출 (B1 estimator 와 동일 cell 의 v13 측정에서 method 평균 + dual-Bernoulli 평균 계산)
3. **`measure_offline_casec_portfolio.py` 신규 작성** — `measure_case_c(cell)` 함수를 1,508 cell 또는 25 cell 표포 portfolio 에 batch 적용. v14 launch 와 동일 함수, cell list 만 확장.

### Phase 2: smoke test (~15 분)

1. patch 후 1 cell smoke (engine latency 4-way) — `measure_latency_realengine.py --cell <test_cell> --variants B1,CaseA,CaseB,CaseC,baseline,oracle --n_warmup 2 --n_timed 3`
2. patch 후 1 cell smoke (offline CaseC) — `measure_offline_casec_portfolio.py --cell <test_cell> --trials 2 --n_queries 100`
3. 결과 sanity check — variant 산출 + injection_fired + q_error 값

### Phase 3: 측정 launch (3 병렬, free RAM ≥ 256GB 유지)

**Priority 1 — Engine latency 4-way × phase2 12 cell (~2 시간)**
- 4 query (Q3·Q9·Q10·Q12) × 3 qid × sel 0.001 = 12 cell × 4-way variants
- n_warmup=5, n_timed=15 (phase2 기본)
- 3 병렬 (sf 별 또는 query 별 분할)
- 출력: `_internal/cache/rq3/latency/phase2_4way_<TS>/`

**Priority 2 — Engine latency 확장 sf·sel (~3-5 시간, 시간 가능 시)**
- sf {1, 10, 100} × sel {0.001, 0.01, 0.1} × Q{Q3, Q9, Q10, Q12} = 36 cell (또는 시간 안에 가능한 만큼)
- 4-way variants
- 출력: `_internal/cache/rq3/latency/phase4_4way_<TS>/`

**Priority 3 — Offline CaseC 25 cell portfolio (~35 분 3 병렬)**
- v13 25 cell × CaseC dual-Bernoulli (method-agnostic) — cell-level 1,508 cell 외삽
- trials=10, n_queries=1000 (v14 동일)
- 출력: `_internal/cache/rq3/paper_exact_v15_25cell_<TS>/`

**Priority 4 — Offline CaseC 1,508 cell 전수 (시간 남으면)**
- 1,508 cell 전수 측정 — 25 cell × 16 method × K{10,20,30} × sel{0.001,0.01,0.1} × sf{1,10,100} 의 부분 평면
- ~6-10 시간 (3 병렬). 시간 부족 시 sampling

**자원 모니터링**:
- `_internal/state/resource_watchdog.service` (carry) 또는 신규 — free RAM ≥ 256GB, our RSS ≤ 512GB, 5초 주기
- launch 전 systemd timer 가동
- 위반 시 자동 stop + log

### Phase 4: 데이터 취합·분석 (~3 시간)

1. **Engine latency 4-way aggregate** — phase2_4way + phase4_4way → parquet + summary.md
2. **Offline CaseC portfolio aggregate** — v15_25cell + (가능 시) v15_1508cell → parquet + summary.md
3. **3-multi-model 교차 검증**:
   - **Codex** xhigh — measure_latency_realengine.py CaseA·CaseC patch + aggregate 통계 코드 + paired Δ% 계산 적대 재검증
   - **Gemini** Deep Think (Ultra 한도) — 측정 결과 narrative · 보고서 추가 § 검증 · figure 시각 검증
   - **메인** — 데이터 정합 + 환각 회피

### Phase 5: 문서 작업 (~2-3 시간)

1. **storyline NEW v2 patch** — 슬라이드 12 (paired Δ%) 에 CaseC paired Δ% 추가 한 줄. 슬라이드 11 부 hero "4.43× ≈ 4.46× ≈ 4.54×" 에 CaseC 가속 한 줄 보강
2. **보고서 §4.x 신규 § 추가** — "4-way engine latency 완전 매칭 결과 (CaseA·CaseC 추가)" + figure 1-2개
3. **보고서 §2.2 Exqutor 식·§2.3 Cochran §5.5/§11.10 patch** — Gemini ❌ 2건 정정
4. **md + pdf export** — `_internal/scripts/md2pdf.py` 사용 (한글 Apple SD Gothic Neo)

### Phase 6: 산출물 정리 + handoff close (~30 분)

1. 미커밋 정리 (사용자 자고 있으니 commit 자율 진행 OK · push 는 carry)
2. handoff close + 다음 세션 prompt (마감 일정 변경 시)

### 사용자 진행 사항 (메인 세션 X)

- 박세은 → 강재현·이동욱 카톡 합의 (재프레이밍·deck·포스터·영상·보고서)
- 박세은 → 박광현 교수님 사전 보고 배포 (5/24~5/26)
- 영상 MP4 제작·YouTube 업로드·QR 생성
- LearnUs 제출 (deck 5/26·포스터·영상 5/28·보고서·상호평가 6/11)
- (선택) Gemini 웹앱에서 Nano Banana Pro 5 자산 생성 + Veo 3.1 3 clip 생성

## 5. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260524_020000_엔진4way_offline확장_자율measure+분석+문서_22시간내.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260524_020000.md` | 동반 (작성 중) |
| ★ deck v2 신본 PPTX (Phase 5 export) | `submission/_drafts/속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx` | committed 예정 (1.13 MB) |
| ★ v2 신본 prompt | `submission/_drafts/속도는벡터_발표deck_재프레이밍_prompt_v2신본15장_20260524_002513.md` | committed 예정 |
| ★ 포스터 Nano Banana Pro brief | `submission/_drafts/속도는벡터_포스터_시각자산_Nano_Banana_Pro_brief_20260524_010021.md` | committed 예정 |
| ★ 영상 Veo 3.1 brief | `submission/_drafts/속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md` | committed 예정 |
| ★ 영상 storyboard (v2 매핑 patch) | `submission/_drafts/속도는벡터_소개영상_storyboard_20260523_235540.md` | committed 예정 |
| ★ measure 4-way patch (다음 세션 작성) | `_internal/scripts/measure_latency_realengine.py` | patch 예정 |
| ★ offline CaseC portfolio (다음 세션 작성) | `_internal/scripts/measure_offline_casec_portfolio.py` | 신규 |
| ★ 4-way latency 결과 (다음 세션) | `_internal/cache/rq3/latency/phase2_4way_<TS>/` | 측정 후 |
| ★ Offline CaseC 25 cell 결과 (다음 세션) | `_internal/cache/rq3/paper_exact_v15_25cell_<TS>/` | 측정 후 |
| ★ 보고서 §4.x 4-way 추가 (다음 세션) | `submission/_drafts/속도는벡터_6_11_최종보고서_<TS>.md/.pdf` | 갱신 후 |
| 직전 000200 handoff | `_internal/handoff/active/handoff_20260524_000200_본세션완주_deck재프레이밍+포스터+영상+교차검증+팀공유.md` | archive 이동 예정 |
| 직전 000200 복붙 | `_internal/handoff/active/새세션_복붙_프롬프트_20260524_000200.md` | archive 이동 예정 |

### 5.1 EBQAS 트랙 (5/24 02:00 점검 시 archive 이동 확인 — 메인 트랙 commit 시 분리)

| 항목 | 경로 | 상태 |
|---|---|---|
| EBQAS DISCONTINUED archive | `_internal/archive/ebqas_track_DISCONTINUED_20260524/` | untracked (별도 commit) |
| EBQAS handoff archive (6 file) | `_internal/handoff/archive/handoff_2026052[34]_*EBQAS*.md` | untracked |
| EBQAS 복붙 archive (6 file) | `_internal/handoff/archive/새세션_복붙_프롬프트_*EBQAS.md` | untracked |
| EBQAS 측정 raw | `experiments/results/raw/EBQAS_24cell_001021/` + `EBQAS_smoke_001021/` | untracked |
| EBQAS submission archive | `submission/_drafts/archive/_ebqas_discontinued_20260524/` | untracked |
| EBQAS 제안서 (deleted) | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | deleted (D) |

## 6. 환경·검증

- **자가검증 (Phase A 점검)**: v13 1,508 cell × 3 mode 확인 ✓ · v14 CaseC 9 cell 확인 ✓ · phase2 12 cell × 3-way 확인 ✓ · 서버 자원 ✓
- **자가검증 (deck v2 신본 PPTX)**: 슬라이드 11 (3-7× hero + 4갈래 도식 + 세 화살표 동일 굵기 + "동등" 메시지) 시각 검증 완벽 ✓
- **자가검증 (Chrome MCP)**: macmini Chrome (deviceId `644dba75-3349-4c8d-ba29-1507743d45a5`) 연결 ✓ · clipboard 17.7KB paste + 자동 Send ✓ · AI v21/v22 무시 + 15장 신본 새 생성 ✓
- **시간**: 2026-05-24 00:00 → 02:00 KST (2 시간) + 다음 세션 ~22 시간 (5/24 23:59 KST 까지)
- **서버 자원**: available 765GB · CPU load 8% (~10 core 사용) · disk 1.4TB · 4× RTX 6000 Ada 49GB · uptime 11 days
- **256GB free RAM 유지** = 우리 작업 ≤ 510GB · 3 병렬 측정 시 ~300GB 안전
- **미커밋**: 본 세션 종료 시 메인 트랙 commit 진행 (사용자 자고 있어도 commit OK · push X)

## 7. 일정 (carry)

- **5/24 (일) ~ 23:59 KST** ★★ 자율 측정 + 분석 + 문서 + 검증 마감 (사용자 명시 "오늘 안")
- **5/24 (일)** 박성원 멘토 3차 자문 회신 예정 + 산출물 추가 반영
- **5/24~5/26** deck v2 신본 검증 + 포스터 PDF + 영상 제작·YouTube 업로드
- **5/26 (화) 23:59** 발표 슬라이드 LearnUs 마감 ★★ critical path
- **5/27 (수)** · **5/29 (금)** 최종 발표
- **5/28 (목) 12:00** 포스터·영상 LearnUs 마감
- **6/5 (금) 9:00~18:00** 전시회 (제5공학관 1층 로비, 504호 15:00 집결)
- **6/11 (목) 23:59** 최종 보고서·상호평가 결과 마감

## 8. ★ 환각 회피 룰 (carry · 본 세션 추가)

- v13 1,508 cell 정본 · v14 9 cell CaseC 정본 · phase2 12 cell latency 정본 — 모두 진짜 측정. Codex 재현 ✅ (5/23 23:44 KST)
- ★ 89% = 앙상블 평균 효과 (분포 인지 효과 X) — controlled verification
- CaseC = (B1+B1)/2 dual-Bernoulli 통제군 (method-agnostic) — q-error 1.373 측정 완료 / **engine latency 미측정 → 다음 세션 측정**
- 측정 코드 변경 시 smoke 우선 — sanity check 통과 후 launch
- 자원 watchdog (free RAM ≥ 256GB) 위반 시 자동 stop
- 3 병렬 launch 시 RAM 모니터링 주기 5초 (systemd watchdog 또는 monitoring script)
- 비가역 작업 (git push --force · DB DROP · rm -rf) — 사용자 자는 동안 사전 위임 없음 → carry
- git push X (사용자 명시 요청 시만, carry)
- Codex·Gemini 적극 활용 — 통계 코드 + 보고서 narrative + figure 모두 교차 검증
- 코드명 (B1·CaseA·CaseB·CaseB′·CaseC) = 보고서·기술 문서 OK, 발표물 (deck·포스터·영상) 노출 금지
- ⚠️ Engine latency 4-way 측정 결과 = CaseC paired Δ% 가 0 또는 양수 → "음성" carry. CaseC vs B1 paired Δ% 가 의미 있게 음수 (개선) → "★ engine 에서도 CaseC 우위" 새 발견 (storyline patch 필요). 결과에 따라 narrative 유동 적용
- 실험 진행 시 — Codex 적대 재검증 (xhigh, measurement code + 결과 통계) + Gemini Deep Think (보고서 narrative) 호출
- handoff 룰: 종료 시 active 직전 set archive → 신본 timecode 작성

---

작성: 2026-05-24 02:00 KST. 본 세션 (deck v2 신본 PPTX export + 포스터/영상 brief + 룰·메모리 + Phase A 점검) 완료 인계. → 다음 세션 = (a) Phase 1 코드 patch (engine 4-way + offline CaseC) → (b) Phase 2 smoke → (c) Phase 3 launch (3 병렬, ~6-8 시간) → (d) Phase 4 분석 + 3-multi-model 검증 → (e) Phase 5 문서 (storyline·deck·보고서 patch + md + pdf) → (f) Phase 6 handoff close. 사용자 자고 있는 동안 메인 세션 자율 진행.
