# handoff 20260523 22:51 — EB-QAS 별도 트랙 인프라·spec·v2 대조·Codex 적대 검증 결과 회수까지 완료, 활성화 전 정정 plan 5건 carry

> 본 handoff = EB-QAS 별도 트랙 두 번째 세션의 최종 인계 anchor (22:20~22:51 KST · 31분). 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 세션은 직전 정본화 commit `d6d1b5a7` 위에서 (1) 별도 트랙 인프라 `_internal/state/ebqas_track/` 신설 + README + 4 하위 디렉토리 (2) Exqutor v2 PDF 직접 추출로 §V-B hyperparam 7개와 식 (2)~(6) verbatim 일치 확인 (3) 실험 A 4-way matched spec + 실험 B~E outline + 구현 의사코드 정제 3 문서 작성 (4) Codex 적대 검증 디스패치 spec 작성 + xhigh background 실행(8분, 320,939 tokens) + **결과 회수·한국어 학술 산문 정제 완료**까지 완료. **★ Codex 종합 verdict = concern · (b) 안전장치 fail 발견 — mismatch reset이 B1으로 수렴하지 않음(κ ~ 19로 수렴)이 알고리즘 동작의 반례. 활성화 전 정정 plan 5건 carry**. 메인 트랙 v14 aggregate paused 유지(사용자 22:12 결정), 본 세션 손대지 않음. **다음 EB-QAS 세션 = (a) 의사코드 §4.2 mismatch reset 재설계 (b) 정본 anchor §10.4 inline 정정 (c) CaseB comparator + paired effect size 사전 고정 (d) group key·label 분리 (e) Exqutor v4 fetch + 외부 bibliography clean (f) 활성화 결정·다음 carry**.

## 0. 정본·진입점

- **★ 본 handoff** — 본 문서 한 장으로 EB-QAS 트랙 인계. self-contained.
- **★ EB-QAS 정본 anchor (carry)**: `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` (사용자 제공 verbatim 22 § + 정본 머리말 5절)
- **★ 본 트랙 진입 README**: `_internal/state/ebqas_track/README.md`
- **★ Codex 적대 검증 결과 정제 (★ 본 세션 핵심 산출)**: `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md` — verdict 6 축 / finding·정정 권고 verbatim carry / 활성화 전 정정 plan 5건
- **★ Codex 디스패치 spec**: `_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md`
- **★ Codex 원본 log**: `/tmp/codex_ebqas_224306.log` (4995줄, 320,939 tokens, exit 0)
- **★ Exqutor v2 대조 보고**: `_internal/state/ebqas_track/exqutor_대조/exqutor_v2_verbatim_대조_20260523_222815.md`
- **★ 실험 spec 3건**: `_internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_20260523_222815.md` · `EBQAS_실험BCDE_outline_20260523_222815.md` · `EBQAS_구현_의사코드_20260523_222815.md`
- **강재현 카톡 출처 기록 (carry)**: `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md`
- **메모리 별도 트랙 anchor (carry)**: `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md`
- **5/23 감사 평결 정본 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`
- **메인 트랙 paused handoff (공존)**: `_internal/handoff/active/handoff_20260523_220000_v14CaseC분석완료_4산출물패치.md` — 본 트랙은 정독 X
- **본 세션 직전 EB-QAS handoff (archive 권고 대상)**: `_internal/handoff/active/handoff_20260523_221204_EBQAS별도트랙진입_다음세션이어가기.md` · `_internal/handoff/active/handoff_20260523_224306_EBQAS_트랙인프라spec코덱스디스패치.md` — 본 handoff가 후속본, 다음 세션이 archive 이동 권고

## 1. EB-QAS framing (불변 전제, carry)

EB-QAS는 Exqutor 논문(arXiv:2512.09695, Capstone CLAUDE.md 정본 v2 — 정본 anchor 인용은 v4이며 §V-B verbatim은 v2 PDF로 본 세션 검증 완료, Codex 축 f는 v4 실제 존재 확인) §V-B의 distribution-unaware Bernoulli Adaptive Sampling을 **대체**하는 방향이다. 데이터 분포를 미리 안다고 가정하지 않으며, 가용 정보는 (a) 현재 query uniform random sample, (b) 이전 유사 query/predicate의 true cardinality·Q-error, (c) query metadata뿐이다. query-group별 Beta prior `(α_g, β_g)`를 누적해 현재 query sample `s/n`과 결합한 posterior mean `(α_g+s)/(α_g+β_g+n)`으로 cardinality를 추정하고, posterior Q-risk `Q_post = max(p̂/L, U/p̂)`가 충분히 작으면 sampling을 조기 종료한다. κ cap·decay·mismatch reset으로 잘못된 prior를 처리한다 — **다만 본 세션 Codex 검증 결과 (b) fail로 mismatch reset 식이 B1 수렴 보장 X 발견, 활성화 전 explicit mode switch 재설계 필요**.

본 트랙은 5/23 오프라인 실험 정당성 감사 평결과 4축 정확 호환된다(Codex 축 e pass 0.87). (a) CaseB식 산술평균을 채택하지 않고 Exqutor B1 자체를 대체, (b) 분포 사전 지식 가정 명시적 제거, (c) latency를 objective로 삼지 않고 평가 지표·plan-sensitive subset 한정, (d) method library 미의존. 별도 후속 연구 트랙이며 6/11 보고서 이후 또는 향후 활성화 candidate.

## 2. 본 세션이 한 일 (2026-05-23 22:20~22:51 KST · 31분)

| 항목 | 상태 | 내용 |
|---|---|---|
| 시간 확인·git 상태·메모리·정본 anchor 정독 | ✅ | KST 22:20 시작. 메모리 2건·정본 anchor 전문(~2160줄)·카톡 출처 정독 |
| Plan 모드 진입·ultraplanning | ✅ | `~/.claude/plans/abstract-jumping-crab.md` 작성 → ExitPlanMode 22:25 사용자 승인 |
| 탐색 발견 carry | ✅ | 정본 anchor §A.2 “`measure_3way`” 표현 정정 필요 — 실제 코드 4분리(`measure_b1_paper`·`measure_case_a/b/c`). 실험 A spec §5에 정정 carry |
| ★ task #1 인프라 신설 | ✅ | `_internal/state/ebqas_track/` + 4 하위 + `.gitkeep` + README (9 §) |
| ★ task #2 Exqutor v2 PDF 대조 | ✅ | `reference/papers/[0] Exqutor;...pdf` = **arXiv:2512.09695v2 11 Dec 2025**. §V-B hyperparam 7개(z·e·N·m·η₀·α·β·γ·period) + 식 (2)~(6) 정본 anchor v4 인용과 verbatim 일치. 대조 보고서 작성 |
| ★ task #3 실험 spec 정제 | ✅ | 3 문서: 실험 A spec(18 KB) + 실험 B~E outline(16 KB) + 구현 의사코드(15 KB) |
| ★ task #4 Codex 디스패치 + 결과 회수·정제 | ✅ | 디스패치 spec(14 KB) 작성 → background 실행 22:43 → 22:51 결과 회수(4995줄·320,939 tokens·exit 0) → **결과 정제 보고서 작성**(`codex_검증_20260523_225122.md`, 6 축 verbatim carry + 활성화 전 top 5 정정) |
| task #5 활성 시기·공유 시점 | ⏸ | 사용자 판단 보류 — 6/11 이후 default. **Codex (b) fail 발견 후 6/11 이전 활성화 시 정정 5건 우선** |
| ★ task #6 본 handoff·복붙 작성 | ✅ | 본 문서 + 동반 복붙(다음 메시지) — 직전 224306 handoff는 archive 권고 |
| 메인 트랙 paused 유지 | ✅ | `measure_paper_exact.py`·v14 산출물·storyline·redline·prompt·보고서_215000·handoff_220000·복붙_220000 모두 본 세션 손대지 않음 (`git status` 확인) |

## 3. ★ 핵심 수치·결과 (정본 carry + 본 세션 신규)

### 3.1 v13 정본 (carry)

- v13 3-way matched 1508 paired (B1·CaseA·CaseB 동시 산출)
- CaseB vs B1: better **89.1%** (1344/1508) · median Δ% **−4.38%** — 진짜 / 인과 귀속(“분포 인지”)은 폐기
- CaseA vs B1: better **35.2%** · mean Δ% **+12.90%** (단독 대체 portfolio 악화)
- 고정-N 통제군: B1 1.944 / CaseA 1.984 / CaseB **1.477** / CaseB′ **1.459** — 평균 효과 입증
- hyperloglog 무작위 해시: CaseA +2.57% (악화) / CaseB(평균) −4.58% (둔갑)
- latency 56 cell paired Δ% **+0.13%** (무개선) · within-cell r=**−0.007**
- v14 CaseC dual-Bernoulli 통제군 smoke 1 cell 1.467 ≈ CaseB v13 1.477 (메인 트랙 paused)

### 3.2 본 세션 신규 검증 결과

- **Exqutor v2 PDF 대조 (task #2)**: arXiv:2512.09695v2 [cs.DB] 11 Dec 2025 = Capstone CLAUDE.md 정본 일치. §V-B verbatim·hyperparam 7개·식 (2)~(6) 정본 anchor v4 인용과 일치.
- **★ Codex 적대 검증 (task #4 · xhigh · 320,939 tokens · 결과 정제 본 세션 완료)**: 6 축 verdict — **종합 concern**
  | 축 | verdict | confidence |
  |---|---|---|
  | (a) 수학 정확성 | concern | 0.86 |
  | **(b) 안전장치 충분성** | **fail** | **0.91** |
  | (c) paired 비교 통제 | concern | 0.82 |
  | (d) leakage 방지 | concern | 0.84 |
  | (e) 5/23 평결 4축 호환성 | pass | 0.87 |
  | (f) 외부 인용 정확성 | concern | 0.88 |
  
  - **(b) fail 핵심**: 의사코드 mismatch reset이 `κ *= γ` 직후 `κ ← ρ·κ + w` 적용 → 반복 mismatch에서도 κ가 `w/(1−ρ·γ) = 10/(1−0.475) ≈ 19.0` 근방으로 수렴, B1으로 가지 않음. spec 수준에서도 알고리즘 동작의 반례.
  - **(e) pass**: 5/23 평결 4축 호환성 — CaseB 평균 채택 X, 분포 사전 지식 X, latency objective X, method library 미의존 정본 7건 일관 적용 확인.
  - **활성화 전 top 5 정정**: (1) mismatch fallback explicit mode switch 재설계 (2) leakage-free group key 확정·target sel label 제거 (3) CaseB comparator + paired effect size 사전 고정 (4) 수식 가정·empirical prior update 지위 분리 (5) Exqutor v4 PDF + 외부 bibliography clean source map.
  - **외부 fetch 확인**: Exqutor v4 실재(arxiv.org/html/2512.09695v4), BayesCard·Fauce(PVLDB vol14 p1950 Liu)·Flow-Loss·CardEst(PVLDB vol15 p752 Zhu)·Bayes Rules!·Efron·Kuchibhotla PMLR v139 모든 핵심 claim 정확 — reference hygiene 정정 필요.

### 3.3 EB-QAS 자체 측정 수치 (carry)

EB-QAS 자체 측정은 본 세션 시점 **없다** — 측정 전. 가설 H1~H5(정본 §21)는 측정 결과로만 평가. (b) fail 정정 완료 전 측정 코드 작성·launch 금지.

## 4. ★ 다음 세션 task (5/23 22:51 KST 기준)

Codex 검증 결과의 활성화 전 정정 5건을 다음 세션의 6 task로 확장. 직전 handoff_224306의 task 일부와 통합.

1. **★★★ 의사코드 §4.2 mismatch reset 식 재설계 (Codex (b) fail 해결)** — `_internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_<새 타임코드>.md`로 신규 파일 작성(덮어쓰기 X). explicit mode switch: 반복 mismatch N회 이상 시 `prior_mode=no_history` + `κ=0|2` + `early_stop=False` + B1 cap까지 sampling. mismatch query에서 `w` update skip 또는 `w_mismatch` 별도. `Q_post` numerical floor 로깅용·stop decision용 분리.
2. **★★★ 정본 anchor §10.4 mismatch reset 식 inline 정정** — `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` 본문 inline. 머리말 §환각·정합성 점검에 Codex 검증 결과 cross-ref + (b) fail 처리 carry. 머리말 §정본·정합성 점검 표에 “(b) Codex 안전장치 fail → explicit mode switch 정정 완료” row 추가.
3. **★★ 실험 A spec §1·§5 CaseB comparator 사전 고정 (Codex (c) concern)** — `EBQAS_실험A_4way_matched_spec_<새 타임코드>.md` 신규 파일. CaseB의 method를 strong-13 aggregate 또는 대표 method 또는 v14 CaseC dual-Bernoulli 중 사전 고정. paired effect size를 Cliff's δ → matched rank-biserial / sign-based effect size 교체. 통계축 = Wilcoxon + paired bootstrap CI + matched rank-biserial. output을 query-level row로 저장해 `cell·trial_idx·query_idx` join invariant 테스트 명시.
4. **★★ 실험 B outline §1.2·§1.3 group key·label 분리 (Codex (d) concern)** — `EBQAS_실험BCDE_outline_<새 타임코드>.md` 신규 파일. group key는 query text + threshold D + template + predicate signature만 — `sel=...` label은 benchmark 분석 label로만(runtime group key X) 명시. threshold_bucket은 단순 log-scale D bucket 명시(또는 train-only quantile). prequential evaluation 명시(query t 평가는 t−1까지의 history만 사용). `Q-error`는 true cardinality 이후만 계산 — current query stop/update에 절대 미사용 assert 추가.
5. **★ Exqutor v4 fetch + 외부 bibliography clean source map (Codex (f) concern)** — `https://arxiv.org/html/2512.09695v4` fetch 후 §V-B verbatim·hyperparam 추출 → `exqutor_v4_verbatim_대조_<HHMMSS>.md`. v2와 차이 0이면 “버전 차 영향 없음”으로 처리. 정본 anchor §22 인용 [1]~[10] 8 reference를 clean URL·venue·year·pages·DOI/arXiv id로 정정: BayesCard(arXiv:2012.14743), Fauce(PVLDB vol14 p1950, Liu et al.), Flow-Loss(par.nsf.gov/biblio/10347336), CardEst(PVLDB vol15 p752, Zhu et al.), Bayes Rules!(bayesrulesbook.com/chapter-3), Efron(efron.ckirby.su.domains/papers/2021EB-concepts-methods.pdf), Kuchibhotla(PMLR v139, proceedings.mlr.press/v139/kuchibhotla21a). 외부 claim source map 한 줄씩 작성.
6. **★ 활성 시기·팀 공유 시점 결정 + 다음 carry handoff/복붙** (사용자 판단) — default 6/11 이후. **Codex (b) fail 정정 완료 전 measure_ebqas 측정 코드 작성·launch 금지**. 박세은·강재현·박광현·박성원 멘토 공유 시기는 활성화 결정 후. Codex 검증 결과를 함께 공유 권고. 다음 carry handoff/복붙 작성.
7. **(메인 트랙 paused 유지)** — handoff_220000·v14 산출물·measure_paper_exact.py·storyline·redline·prompt·보고서_215000 그대로. 재개 시점 사용자 결정.

## 5. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260523_225122_EBQAS_Codex검증결과회수_정정plan.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260523_225122_EBQAS.md` | 동반 (본 세션 마지막 메시지) |
| ★ 트랙 README | `_internal/state/ebqas_track/README.md` | 신규 |
| ★ Exqutor v2 대조 보고 | `_internal/state/ebqas_track/exqutor_대조/exqutor_v2_verbatim_대조_20260523_222815.md` | 신규 |
| ★ 실험 A spec | `_internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_20260523_222815.md` | 신규 |
| ★ 실험 B~E outline | `_internal/state/ebqas_track/실험_spec/EBQAS_실험BCDE_outline_20260523_222815.md` | 신규 |
| ★ 구현 의사코드 | `_internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_20260523_222815.md` | 신규 |
| ★ Codex 디스패치 spec | `_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md` | 신규 |
| ★ Codex 검증 결과 정제 | `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md` | 신규 (본 세션 핵심 산출) |
| Codex 원본 log | `/tmp/codex_ebqas_224306.log` | 4995줄 320,939 tokens, carry (별도 보존 권고) |
| 정본 anchor (carry) | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | 변경 X |
| 카톡 출처 (carry) | `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md` | 변경 X |
| 5/23 평결 (carry) | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` | 변경 X |
| 메모리 anchor (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` | 변경 X |
| 메모리 평결 cross-ref (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_offline_audit_20260523.md` | 변경 X |
| 메모리 인덱스 (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` | 변경 X |
| 직전 EB-QAS handoff (archive 권고) | `_internal/handoff/active/handoff_20260523_221204_EBQAS별도트랙진입_다음세션이어가기.md` · `handoff_20260523_224306_EBQAS_트랙인프라spec코덱스디스패치.md` | 다음 세션 archive 이동 권고 |

본 세션 신규 9 파일 모두 untracked — 사용자 명시 commit 지시 시 별도 EB-QAS 트랙 commit (직전 `d6d1b5a7` 패턴). 메인 트랙 미커밋·신규는 그대로.

## 6. 메인 트랙 paused 상태 (carry, 사용자 결정 22:12 KST)

본 세션은 메인 트랙을 손대지 않았다 (사용자 결정 21:48 + 22:12 v14 paused). 메인 트랙 미커밋·신규 그대로:

- handoff: `_internal/handoff/active/handoff_20260523_220000_v14CaseC분석완료_4산출물패치.md`
- 복붙: `_internal/handoff/active/새세션_복붙_프롬프트_20260523_220000.md`
- v14 분석: `_internal/cache/rq3/v14_summary.md` · `_internal/cache/rq3/aggregated_v14.parquet` · `_internal/scripts/aggregate_v14.py`
- 측정 JSON: `_internal/cache/rq3/paper_exact_v14_20260523/` 9건
- 보고서 신본: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md`
- 발표 deck 패치본 (modified): `storyline_NEW_20260523_110051.md` · `재프레이밍_redline_20260523_110051.md` · `재프레이밍_prompt_20260523_110051.md`
- 측정 코드 (modified): `_internal/scripts/measure_paper_exact.py`

`active/`에 메인 handoff_220000 + EB-QAS handoff_221204(직전, archive 권고) + handoff_224306(직전, archive 권고) + 본 handoff(225122) 공존. **본 복붙 프롬프트는 225122만 명시**.

메인 트랙 critical path(5/26 23:59 LearnUs · 5/27·29 발표 · 5/28 12:00 포스터 · 6/11 최종 보고서)는 v14 aggregate 없이도 v13 정본 + 평결 + 박세은 OK 재프레이밍으로 진행 가능.

## 7. ★ 환각 회피 룰 (carry · 본 세션 추가)

- **v13 정본 수치 진위·인과 분리** (carry): “89.1% / −4.38% / 1344 / 1508 / 35.2% / 12.90% / 1.477 / 1.459 / 1.944 / 1.984 / hyperloglog −4.58% / 56 cell +0.13% / r=−0.007”은 진짜 측정. 인과 귀속(“분포 인지 효과”)은 5/23 감사로 폐기.
- **EB-QAS는 본 시점 검증 가설**. “EB-QAS가 B1보다 낫다”는 단언 금지(측정 전). 핵심 가설 H1~H5는 측정 결과로만 평가.
- **★ Codex (b) fail carry 신규**: 의사코드 §4.2 mismatch reset이 B1으로 수렴하지 않는 알고리즘 동작 반례 발견. 활성화 전 explicit mode switch 재설계 필수. 본 항목 정정 완료 전 measure_ebqas 측정 코드 작성·launch 금지.
- **★ Codex (d) concern carry 신규**: `threshold_bucket`을 “dataset별 quantile”로 만들거나 `sel=0.001` 식 라벨을 group key에 넣으면 leakage. 활성화 시 group key·benchmark label 분리.
- **★ Codex (c) concern carry 신규**: CaseB comparator(어느 method의 CaseB인지) 사전 고정 X. paired effect size를 Cliff's δ → matched rank-biserial로 교체. 활성화 시 spec patch.
- **★ Codex (f) concern carry 신규**: 정본 anchor §22 외부 인용 8건 reference hygiene 부족 — Fauce·Flow-Loss·Efron reference entry 없음, BayesCard/CardEst URL `utm_source=chatgpt.com` suffix 제거. 활성화 시 정정.
- **Exqutor 본 논문 버전 차이** (carry · Codex 확인): 정본 anchor v4 인용 ↔ Capstone CLAUDE.md 정본 v2 ↔ `reference/papers/` v2. Codex 검증으로 v4 arXiv 실재 확인(arxiv.org/html/2512.09695v4). 다음 세션이 v4 fetch + 정본 anchor 인용 URL 정정.
- **메인 트랙 손대지 않음** (carry). EB-QAS 작업이 메인 트랙 발표·포스터·보고서·v14 작업에 영향 X.
- **별도 트랙 위상 유지**: 본 EB-QAS를 메인 트랙 발표·재프레이밍에 끼워 넣지 않는다.
- **본 handoff는 EB-QAS 트랙 only**. 다음 세션이 메인 트랙 재개 결정 시 handoff_220000 별도 read.
- **타임코드 네이밍** (carry): `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않는다. 본 세션 타임코드 = `222815`(인프라·v2 대조·spec)·`223921`(Codex 디스패치 spec)·`224306`(Codex 실행 시작·직전 handoff)·`225122`(Codex 결과 정제·본 handoff).
- **정본 anchor §A.2 정정 carry** (직전 세션 발견): “`measure_3way` 구조” 표현 → 실제 `measure_b1_paper`(361)·`measure_case_a`(986)·`measure_case_b`(1087)·`measure_case_c`(1195) 4분리 + 신규 `measure_ebqas` 추가. 실험 A spec §5에 정정 반영, 정본 anchor 본문 inline 수정은 다음 세션 활성화 결정 시.

## 8. 일정 (carry)

| 일자 | 항목 | EB-QAS 트랙 영향 |
|---|---|---|
| 2026-05-24 (일) | 박성원 멘토 3차 자문 회신 예정 | 메인 트랙 (paused 상태에서 회신 도착 시 사용자 결정) |
| 2026-05-26 (화) 23:59 | LearnUs 발표 deck 마감 ★★ critical path | 메인 트랙 (v13 + 평결 + 재프레이밍으로 진행 가능) |
| 2026-05-27 (수) · 5/29 (금) | 최종 발표 | 메인 트랙 |
| 2026-05-28 (목) 12:00 | 포스터 PDF 마감 (900×1200) | 메인 트랙 |
| 2026-06-11 (목) | 최종 보고서 마감 | 메인 트랙 |
| 6/11 이후 또는 향후 | EB-QAS 별도 트랙 활성화 후속 | **본 트랙** default 활성화 시점 |

---

작성: 2026-05-23 22:51 KST. 본 세션(plan 22:25 → 인프라 22:28 → Exqutor v2 22:32 → 실험 spec 3건 22:34~22:39 → Codex 디스패치 spec 22:41 → background 실행 22:43 → 결과 회수 22:51 → 정제 + 본 handoff 22:51) 인계. → 다음 EB-QAS 세션 = 의사코드 mismatch reset 재설계 → 정본 anchor inline 정정 → CaseB comparator 사전 고정 → group key·label 분리 → Exqutor v4 fetch + bibliography clean → 활성화 결정 → 다음 carry handoff/복붙.
