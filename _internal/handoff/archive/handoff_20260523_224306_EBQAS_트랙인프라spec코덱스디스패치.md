# handoff 20260523 22:43 — EB-QAS 별도 트랙 인프라·실험 spec·Exqutor v2 대조·Codex 적대 검증 디스패치 완료, 다음 세션 결과 회수

> 본 handoff = EB-QAS 별도 트랙 두 번째 세션 인계 anchor. 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 2026-05-23 22:20~22:43 KST 본 EB-QAS 세션이 직전 정본화 commit `d6d1b5a7` 위에서 (1) 별도 트랙 인프라 `_internal/state/ebqas_track/` 신설 + README + 4 하위 디렉토리 (2) Exqutor v2 PDF 직접 추출로 §V-B hyperparam 7개와 식 (2)~(6) verbatim 일치 확인 (3) 실험 A 4-way matched spec + 실험 B~E outline + 구현 의사코드 정제 3 문서 작성 (4) Codex 적대 검증 디스패치 spec 작성 + background 실행 시작(xhigh, ~15-40분 견적)까지 완료. 메인 트랙 v14 aggregate paused 유지(사용자 22:12 결정), 본 세션 손대지 않음. **다음 EB-QAS 세션 = (a) Codex 검증 결과(`/tmp/codex_ebqas_224306.log`) 회수·정제 (b) 결과 기반 정본 anchor·신규 spec 정정 (c) v4 PDF arXiv fetch 추가 검증(선택) (d) 활성화 시점·팀 공유 결정(사용자 판단) (e) 다음 carry handoff/복붙**.

## 0. 정본·진입점

- **★ 본 handoff** — 본 문서 한 장으로 EB-QAS 트랙 인계. self-contained.
- **★ EB-QAS 정본 anchor (carry)**: `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` (사용자 제공 verbatim 22 § + 정본 머리말 5절)
- **★ 본 트랙 진입 README**: `_internal/state/ebqas_track/README.md` (위상·메인 트랙 격리·5/23 평결 호환성 4축·하위 디렉토리 4·메모리 cross-ref·환각 회피 룰·활성화 시기)
- **★ 강재현 카톡 출처 기록 (carry)**: `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md`
- **★ 메모리 별도 트랙 anchor (carry)**: `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md`
- **★ 5/23 감사 평결 정본 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`
- **★ 본 세션 신규 산출물 6건**:
  - 트랙 README 1건
  - Exqutor v2 대조 보고 1건 (`_internal/state/ebqas_track/exqutor_대조/exqutor_v2_verbatim_대조_20260523_222815.md`)
  - 실험 spec 3건 (`_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_222815.md`)
  - Codex 디스패치 spec 1건 (`_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md`)
- **★ Codex background log**: `/tmp/codex_ebqas_224306.log` (다음 세션 회수)
- **메인 트랙 paused handoff (공존)**: `_internal/handoff/active/handoff_20260523_220000_v14CaseC분석완료_4산출물패치.md` — 본 트랙은 정독 X (메인 재개 시 별도 read)
- **EB-QAS 트랙 직전 handoff (carry, archive 대상)**: `_internal/handoff/active/handoff_20260523_221204_EBQAS별도트랙진입_다음세션이어가기.md` — 본 handoff가 후속본, 다음 세션은 본 handoff만 read

## 1. EB-QAS framing (불변 전제, carry)

EB-QAS는 Exqutor 논문(arXiv:2512.09695, Capstone CLAUDE.md 정본 v2 — 정본 anchor 인용은 v4이며 §V-B verbatim은 v2 PDF로 본 세션 검증 완료) §V-B의 distribution-unaware Bernoulli Adaptive Sampling을 **대체**하는 방향이다. 데이터 분포를 미리 안다고 가정하지 않으며, 가용 정보는 (a) 현재 query uniform random sample, (b) 이전 유사 query/predicate의 true cardinality·Q-error, (c) query metadata(table·column·distance metric·threshold bucket·query template·scalar predicate signature)뿐이다. query-group별 Beta prior `(α_g, β_g)`를 누적해 현재 query sample `s/n`과 결합한 posterior mean `(α_g+s)/(α_g+β_g+n)`으로 cardinality를 추정하고, posterior Q-risk `Q_post = max(p̂/L, U/p̂)`가 충분히 작으면 sampling을 조기 종료한다. κ cap·decay·mismatch reset으로 잘못된 prior를 안전하게 처리한다(정본 §5~10).

본 트랙은 5/23 오프라인 실험 정당성 감사 평결과 4축 정확 호환된다. (a) CaseB식 산술평균을 채택하지 않고 Exqutor B1 자체를 대체(89% Q-error 우위 = 평균 효과 평결), (b) 분포 사전 지식 가정 명시적 제거(CaseA portfolio 악화 평결), (c) latency를 objective로 삼지 않고 평가 지표·plan-sensitive subset 한정(56 cell 무개선 평결), (d) method library 미의존(skilling_hilbert 가짜 Hilbert·신호 5종 PCA/ICA 환원 평결).

별도 후속 연구 트랙이다 — 메인 트랙(v14 4-way 측정·5/26 발표 deck·5/27·29 발표·5/28 포스터·6/11 최종 보고서)과 분리되며, 메인 트랙 음성·방법론적 재프레이밍을 회피·우회하지 않는다. 6/11 보고서 이후 또는 향후 후속 연구 트랙 후보다.

## 2. 본 세션이 한 일 (2026-05-23 22:20~22:43 KST · 23분)

| 항목 | 상태 | 내용 |
|---|---|---|
| 시간 확인·git 상태·메모리·정본 anchor 정독 | ✅ | KST 22:20 시작. git status·메모리 2건·정본 anchor 전문(~2160줄)·카톡 출처 기록 정독 |
| Plan 모드 진입·ultraplanning | ✅ | EnterPlanMode 후 plan `~/.claude/plans/abstract-jumping-crab.md` 작성(7 task + 산출물·검증·정책·견적) — ExitPlanMode 22:25 사용자 승인 |
| 탐색 발견 carry | ✅ | 정본 anchor §A.2 “`measure_3way` 구조” 표현 정정 필요 발견 — 실제 코드는 `measure_b1_paper`(361)·`measure_case_a`(986)·`measure_case_b`(1087)·`measure_case_c`(1195) 4분리. 본 발견을 신규 spec §5.1·§5.2에 정정 반영 |
| ★ task #1 인프라 신설 | ✅ | `_internal/state/ebqas_track/` 디렉토리 + 4 하위(`실험_spec`·`codex_검증`·`exqutor_대조`·`handoff`) + 각 `.gitkeep` + README.md(9 §, 트랙 위상·메인 트랙 격리·5/23 평결 4축 호환성·하위 디렉토리·메모리 cross-ref·진입 순서·환각 회피·활성화 시기) |
| ★ task #2 Exqutor v2 PDF 대조 | ✅ | `reference/papers/[0] Exqutor;...pdf` = **arXiv:2512.09695v2 [cs.DB] 11 Dec 2025** 확인. §V-B verbatim 추출 → hyperparam 7개(z·e·N·m·η₀·α·β·γ·period) + 식 (2)~(6) 정본 anchor 인용과 verbatim 일치. 대조 보고서 작성: `exqutor_v2_verbatim_대조_20260523_222815.md` (대조표 row 10 + 권고 3) |
| ★ task #3 실험 spec 정제 | ✅ | 3 문서 작성: `EBQAS_실험A_4way_matched_spec_20260523_222815.md`(18 KB, §0~§9·4-way matched 측정·metric 20·paired 비교·measure_ebqas 신규 함수 spec) + `EBQAS_실험BCDE_outline_20260523_222815.md`(16 KB, 실험 B online protocol·C prior mismatch stress·D latency·E ablation + hyperparam grid 8 축) + `EBQAS_구현_의사코드_20260523_222815.md`(15 KB, §17.1~4 의사코드 한국어 정제 + §18 4 룰) |
| ★ task #4 Codex 디스패치 spec + background 실행 | 🔄 | 디스패치 spec 작성: `codex_디스패치_spec_20260523_223921.md`(검증축 6개·디스패치 명령·결과 회수 정책·실패 대응). codex exec --sandbox read-only --skip-git-repo-check -c model_reasoning_effort=xhigh background 실행 시작 22:43 — `/tmp/codex_ebqas_224306.log`에 출력. 결과는 다음 세션 회수 |
| task #5 활성 시기·공유 시점 | ⏸ | 사용자 판단 보류 — 6/11 이후 default |
| ★ task #6 본 handoff·복붙 작성 | 🔄 | 본 문서 + 동반 복붙 프롬프트(다음 메시지) — 표준 9-§ 패턴 |
| 메인 트랙 paused 유지 | ✅ | handoff_220000·v14 산출물·measure_paper_exact.py·storyline·redline·prompt·보고서_215000·복붙_220000 모두 본 세션 손대지 않음. `git status`로 본 세션 종료 시 확인 |

## 3. ★ 핵심 수치·결과 (정본 carry + 본 세션 신규)

본 세션은 측정 결과를 만들지 않았다 — spec·검증·인프라 단계. 5/23 감사 평결의 v13 수치 정본 + 본 세션 신규 검증 결과를 carry한다.

### 3.1 v13 정본 (carry)

- **v13 3-way matched 측정**: 1508건 paired (B1·CaseA·CaseB 동시 산출) — 정본 `_internal/cache/rq3/v13_summary.md`
- **CaseB vs B1 paired**: better 1344/1508 = **89.1%** · median Δ% **−4.38%** — 진짜 수치이나 인과 귀속(“분포 인지 효과”)은 5/23 감사로 폐기
- **CaseA vs B1 paired**: better 531/1508 = **35.2%** · mean Δ% **+12.90%** (단독 대체 portfolio 악화)
- **고정-N(q<50, 1,226) 통제군**: B1 1.944 / CaseA 1.984 / CaseB **1.477** / CaseB′(Bernoulli+Bernoulli)/2 **1.459** — 평균 효과 입증
- **hyperloglog 무작위 해시**: CaseA 단독 mean Δ% **+2.57%**(악화) → CaseB(평균) median Δ% **−4.58%**(둔갑) — 평균 효과 결정적 증거
- **엔진 적용 검증 latency**: 56 cell paired Δ% 중앙값 **+0.13%**(무개선) · within-cell r=**−0.007**(디커플)
- **v14 CaseC dual-Bernoulli 통제군 (메인 트랙, 본 트랙 unrelated)**: smoke 1 cell `avg_q_error_trimmed=1.467` ≈ CaseB v13 1.477 (Δ% ~0.7%, 평결 추가 보강)

### 3.2 본 세션 신규 검증 결과

- **Exqutor v2 PDF 대조 (★ 본 세션 산출)**:
  - `reference/papers/[0] Exqutor;...pdf` = **arXiv:2512.09695v2 [cs.DB] 11 Dec 2025** (Capstone CLAUDE.md 정본과 동일 버전)
  - §V-B hyperparam 7개(z=1.96·e=0.05·N=385·m=0.9·η₀=0.1·α=50·β=1.5·γ=0.99·period=50) 정본 anchor 인용과 **verbatim 일치**
  - 식 (2)~(6)(Q-error·δ·V_t·sampling size·η decay) 정본 anchor 본문 인용과 verbatim 일치
  - 정본 anchor가 인용한 arXiv v4와 v2 사이 §V-B 본문 차이 직접 검증 불가(reference/에 v4 부재) — 권고: 정본 anchor inline URL을 v2로 정정 또는 v4 PDF 별도 fetch
- **Codex 적대 검증 디스패치 (★ background 실행 중, 다음 세션 회수)**:
  - 검증축 6개 (a) 수학 정확성 (b) 안전장치 충분성 (c) paired 비교 통제 (d) leakage 방지 (e) 5/23 평결 4축 호환성 (f) 외부 인용 verbatim·연도·저자·핵심 claim 정확성
  - 외부 fetch 8 reference: Exqutor·BayesCard·Fauce·Flow-Loss·CardEst PVLDB vol15·Bayes Rules!·Efron·Kuchibhotla 2021
  - 디스패치 명령: `codex exec --sandbox read-only --skip-git-repo-check -c model_reasoning_effort=xhigh < /dev/null > /tmp/codex_ebqas_224306.log 2>&1`
  - 견적 15-40분 (xhigh + 7 input 파일 read + 6 축 검증 + 외부 fetch)

### 3.3 EB-QAS 자체 수치 (carry)

EB-QAS 자체 측정 수치는 본 세션 시점에 **없다** — 측정 전, 검증 가설 단계. 핵심 가설 H1~H5 (정본 §21):

- **H1** 유사 query 반복 workload에서 EB-QAS는 B1보다 적은 sample로 유사~낮은 Q-error
- **H2** low-selectivity zero-hit query에서 prior shrinkage로 p95/p99 Q-error 감소
- **H3** posterior early stopping으로 final sample size·sampling overhead 감소
- **H4** latency 개선은 plan_changed·low-selectivity·high-dimensional subset에 한정
- **H5** κ cap·decay·mismatch reset 없으면 잘못된 group key에서 B1보다 악화 가능

## 4. ★ 다음 세션 task (5/23 22:43 KST 기준)

본 세션 진행 결과 다음 EB-QAS 세션의 task는 직전 세션 4 항목 + 본 세션이 추가로 carry한 항목을 합쳐 다음 6 항목이다.

1. **★★★ Codex 검증 결과 회수·정제** — `/tmp/codex_ebqas_224306.log`에서 출력 read 후 6 검증축(a~f) 결과 정제. 각 축 verdict(pass/concern/fail) + 핵심 finding + 정정 권고 + confidence를 한국어 학술 산문으로 정제해 `_internal/state/ebqas_track/codex_검증/codex_검증_<HHMMSS>.md`로 저장.
2. **★★★ Codex 결과 기반 정본 anchor·신규 spec 정정** — 발견된 concern·fail 항목을 다음 4 문서에 반영:
   - `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` (정본 anchor — 본문 inline 또는 머리말 §환각·정합성 점검 추가)
   - `_internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_<새 타임코드>.md` (덮어쓰기 X, 새 타임코드 파일 생성)
   - `_internal/state/ebqas_track/실험_spec/EBQAS_실험BCDE_outline_<새 타임코드>.md`
   - `_internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_<새 타임코드>.md`
3. **★★ Exqutor v4 arXiv 추가 fetch (선택)** — `https://arxiv.org/abs/2512.09695v4` PDF fetch 후 §V-B verbatim·hyperparam 추출 → `_internal/state/ebqas_track/exqutor_대조/exqutor_v4_verbatim_대조_<HHMMSS>.md`. v2와 차이 0이면 “버전 차 영향 없음”으로 처리.
4. **★★ 정본 anchor inline 인용 URL 정정 (Exqutor v2 권고 1)** — 정본 anchor §22 끝의 인용 [1] URL을 `arxiv.org/abs/2512.09695v2`로 정정. Capstone CLAUDE.md 정본과 일관.
5. **★ EB-QAS 활성 시기·팀 공유 시점 결정 (사용자 판단)** — default 6/11 이후. 6/11 이전 활성화 시 별도 의사결정. 박세은·강재현·박광현·박성원 멘토 공유 시기는 활성화 결정 후. 활성화 결정 시 `measure_ebqas` 구현·smoke 1 cell·우선 24 cell 측정 진입.
6. **★ 다음 carry handoff/복붙 작성** — 본 세션 산출물(Codex 결과 정제·정본 anchor 정정·v4 fetch·활성화 결정) 인계용 2종 세트.
7. **(메인 트랙 paused 유지)** — handoff_220000·v14_summary.md·aggregated_v14.parquet·aggregate_v14.py·storyline·redline·prompt·보고서_215000·measure_paper_exact.py 등 그대로. 재개 시점 사용자 결정.

## 5. 산출물 경로 (본 세션 신규 + 종전 carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260523_224306_EBQAS_트랙인프라spec코덱스디스패치.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260523_224306_EBQAS.md` | 동반 (본 세션 후속 메시지) |
| ★ 트랙 README | `_internal/state/ebqas_track/README.md` | 신규 |
| ★ Exqutor v2 대조 보고 | `_internal/state/ebqas_track/exqutor_대조/exqutor_v2_verbatim_대조_20260523_222815.md` | 신규 |
| ★ 실험 A spec | `_internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_20260523_222815.md` | 신규 |
| ★ 실험 B~E outline | `_internal/state/ebqas_track/실험_spec/EBQAS_실험BCDE_outline_20260523_222815.md` | 신규 |
| ★ 구현 의사코드 | `_internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_20260523_222815.md` | 신규 |
| ★ Codex 디스패치 spec | `_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md` | 신규 |
| ★ Codex background log | `/tmp/codex_ebqas_224306.log` | background 실행 중, 다음 세션 회수 |
| 정본 anchor (carry) | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | 변경 X |
| 카톡 출처 (carry) | `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md` | 변경 X |
| 5/23 평결 (carry) | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` | 변경 X |
| 메모리 anchor (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` | 변경 X |
| 메모리 평결 cross-ref (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_offline_audit_20260523.md` | 변경 X |
| 메모리 인덱스 (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` | 변경 X |
| 직전 EB-QAS handoff (archive 대상) | `_internal/handoff/active/handoff_20260523_221204_EBQAS별도트랙진입_다음세션이어가기.md` | 다음 세션이 archive로 이동 권고 |

본 세션 신규 6 파일은 사용자 명시 commit 지시 시 별도 EB-QAS 트랙 commit으로 분리(직전 commit `d6d1b5a7` 패턴 유지). 메인 트랙 미커밋·신규는 그대로.

## 6. 메인 트랙 paused 상태 (carry, 사용자 결정 22:12 KST)

본 세션은 메인 트랙을 손대지 않았다 (사용자 결정 21:48 + 22:12 v14 paused 유지). 메인 트랙 미커밋·신규는 그대로:

- handoff: `_internal/handoff/active/handoff_20260523_220000_v14CaseC분석완료_4산출물패치.md` (메인 세션 22:00 작성, paused)
- 복붙: `_internal/handoff/active/새세션_복붙_프롬프트_20260523_220000.md` (메인, paused)
- v14 분석: `_internal/cache/rq3/v14_summary.md` · `_internal/cache/rq3/aggregated_v14.parquet` · `_internal/scripts/aggregate_v14.py`
- 측정 JSON: `_internal/cache/rq3/paper_exact_v14_20260523/` 9건
- 보고서 신본: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md`
- 발표 deck 패치본 (modified): `storyline_NEW_20260523_110051.md`·`재프레이밍_redline_20260523_110051.md`·`재프레이밍_prompt_20260523_110051.md`
- 측정 코드 (modified): `_internal/scripts/measure_paper_exact.py` (local·server divergent, server 신본이 v14 launch에 사용됨)

`active/`에 메인 handoff_220000과 EB-QAS handoff_221204(직전) + 224306(본 handoff) 공존 — 본 복붙 프롬프트는 224306만 명시.

메인 트랙 critical path(5/26 23:59 LearnUs · 5/27·29 발표 · 5/28 12:00 포스터 · 6/11 최종 보고서)는 v14 aggregate 없이도 v13 정본 + 평결 + 박세은 OK 재프레이밍으로 진행 가능 — v14 CaseC 통제군 데이터는 추가 보강 evidence였으며 평결의 결정적 증거(고정-N CaseB′ 1.459 + hyperloglog 무작위 해시 −4.58%)는 이미 v13 자체에서 나왔다.

## 7. ★ 환각 회피 룰 (carry · EB-QAS 트랙)

- **v13 정본 수치 진위·인과 분리**: “89.1% / −4.38% / 1344 / 1508 / 35.2% / 12.90% / 1.477 / 1.459 / 1.944 / 1.984 / hyperloglog −4.58% / 56 cell +0.13% / r=−0.007”은 진짜 측정. 인과 귀속(“분포 인지 효과”)은 5/23 감사로 폐기 → 본 트랙은 그 인과를 다시 주장하지 않는다. CaseB식 산술평균을 채택하지 않고 B1 자체를 대체한다는 점으로 평결과 호환.
- **EB-QAS는 본 시점 검증 가설**. “EB-QAS가 B1보다 낫다”는 단언 금지(측정 전). 핵심 가설 H1~H5(정본 §21)는 측정 결과로만 평가.
- **잘못된 group key·κ 과대·prior drift 위험**은 정본 §C(stress)·§E(ablation)·H5에 명시 — 발표·보고서·논문화 시 함께 보고.
- **Exqutor 본 논문 버전 차이**: 정본 anchor v4 인용 ↔ Capstone CLAUDE.md 정본 v2 ↔ `reference/papers/`도 v2. 본 세션이 v2 PDF로 §V-B verbatim·hyperparam 일치 확인 완료. 다음 세션이 v4 추가 fetch + 정본 anchor 인용 URL 정정 결정.
- **외부 인용 verbatim 정확성**: Codex 디스패치(축 f)에서 BayesCard·Fauce·Flow-Loss·CardEst PVLDB vol15·Bayes Rules!·Efron·Kuchibhotla 2021 verbatim·연도·저자·핵심 claim 정확성 외부 fetch 검증 — 다음 세션 결과 회수 후 정본 anchor 정정.
- **메인 트랙 손대지 않음** (사용자 결정 21:48 + 22:12 v14 paused). EB-QAS 작업이 메인 트랙 발표·포스터·보고서·v14 작업에 영향 X. push는 사용자 명시 지시 시.
- **별도 트랙 위상 유지**: 본 EB-QAS를 메인 트랙 발표·재프레이밍에 끼워 넣지 않는다. 메인 트랙 음성·방법론적 결과의 정직성을 본 EB-QAS의 “전망”으로 흐리지 않는다.
- **본 handoff은 EB-QAS 트랙 only**. 다음 세션이 메인 트랙 재개를 결정하면 handoff_220000을 별도로 read.
- **타임코드 네이밍**: `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않는다 — 모든 EB-QAS 트랙 산출물은 `<문서명>_YYYYMMDD_HHMMSS.ext`. 본 세션 타임코드 = `20260523_222815`(인프라·v2 대조·실험 spec)·`20260523_223921`(Codex 디스패치 spec)·`20260523_224306`(handoff·복붙·Codex 실행 log).
- **본 세션 정본 anchor §A.2 정정 carry**: 정본 anchor가 인용한 “기존 `measure_paper_exact.py:1312 measure_3way` 구조”는 실제 코드에는 단일 함수 X. 실험 A spec §5.1에 “measure_b1_paper(361)·measure_case_a(986)·measure_case_b(1087)·measure_case_c(1195) 4분리 + 신규 measure_ebqas 추가”로 정정 반영. 정본 anchor 본문 inline 수정은 다음 세션이 활성화 결정 시.

## 8. 일정 (carry)

| 일자 | 항목 | EB-QAS 트랙 영향 |
|---|---|---|
| 2026-05-24 (일) | 박성원 멘토 3차 자문 회신 예정 | 메인 트랙 (paused 상태에서 회신 도착 시 사용자 결정) |
| 2026-05-26 (화) 23:59 | LearnUs 발표 deck 마감 ★★ critical path | 메인 트랙 (v13 + 평결 + 재프레이밍으로 v14 aggregate 없이도 진행 가능) |
| 2026-05-27 (수) · 5/29 (금) | 최종 발표 | 메인 트랙 |
| 2026-05-28 (목) 12:00 | 포스터 PDF 마감 (900×1200) | 메인 트랙 |
| 2026-06-11 (목) | 최종 보고서 마감 | 메인 트랙 |
| 6/11 이후 또는 향후 | EB-QAS 별도 트랙 활성화 후속 (사용자 결정) | **본 트랙** default 활성화 시점 |

---

작성: 2026-05-23 22:43 KST. 본 세션(plan 22:25 승인 → 인프라 22:28 → 실험 spec 3건 22:32~22:39 → Exqutor v2 대조 22:32 → Codex 디스패치 spec 22:39 → background 실행 22:43 → 본 handoff 22:43) 인계. → 다음 EB-QAS 세션 = Codex 검증 결과 회수·정제 → 정본 anchor·신규 spec 정정 → (선택) v4 fetch → 활성화 시점 결정 → 다음 carry handoff/복붙.
