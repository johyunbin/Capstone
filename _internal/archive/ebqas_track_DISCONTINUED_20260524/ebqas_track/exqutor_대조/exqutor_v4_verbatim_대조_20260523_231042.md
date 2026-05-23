# Exqutor v4 verbatim 대조 + 외부 bibliography clean source map (Codex (f) concern 정정)

> 작성: 2026-05-23 23:10 KST. 출발 = 직전 v2 대조 보고서(`exqutor_v2_verbatim_대조_20260523_222815.md` §5·§6·§7) + Codex 적대 검증 결과 정제(`../codex_검증/codex_검증_20260523_225122.md` §2.6 (f) concern · 0.88 confidence). 본 보고서는 (1) arXiv:2512.09695**v4** HTML을 외부 fetch해 §V-B Adaptive Sampling verbatim·hyperparam 7개·식 (2)~(6)을 v2 PDF 대조와 cross-check하고, (2) EB-QAS 정본 anchor §22 외부 인용 9건의 hygiene를 clean source map(utm 제거·venue·year·pages·DOI/arXiv id·신규 entry)으로 정정한다.

## 0. 결론 한 줄

**v4 vs v2: §V-B Adaptive Sampling의 hyperparam 7개와 식 (2)~(6)이 verbatim 동일 — 버전 차가 EB-QAS 정본 anchor 본문 인용에 영향 X**. v2 PDF 직접 검증(222815)에서 확인된 모든 §V-B 항목이 v4 HTML에서도 동일하게 인용 가능. 정본 anchor §22 외부 인용 9건의 hygiene(utm suffix·reference entry 누락·제목 잘림) 정정 완료 — 본 보고서 §3·§4에 clean source map 명시.

## 1. v4 fetch 결과

| 항목 | 값 |
|---|---|
| arXiv 식별 | **arXiv:2512.09695v4 [cs.DB]** |
| 제출 날짜 (v4) | **2026-03-29** |
| Title | Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries |
| Author (v4) | Hyunjoon Kim · Chaerim Lim · Hyeonjun An · Rathijit Sen · Kwanghyun Park (v2와 동일 author line) |
| Fetch source | https://arxiv.org/html/2512.09695v4 (WebFetch, 2026-05-23 23:10 KST) |
| Fetch tool | Claude WebFetch (HTML rendering) |

## 2. §V-B Adaptive Sampling — v4 verbatim 대조

### 2.1 Hyperparam 7개 — v4 vs v2 동일

```text
v4 (HTML, 2026-03-29 fetch):
- Momentum coefficient: m = 0.9
- Initial learning rate: η₀ = 0.1
- Weighting factor: α = 50
- Target Q-error threshold: β = 1.5
- Learning rate decay factor: γ = 0.99
- Update frequency: every 50 queries
- Initial fixed sample size: N = 385 (z=1.96, P̂=0.5, e=0.05)
```

```text
v2 (PDF, 2025-12-11 직접 추출 — 222815 §4 carry):
- m = 0.9, η₀ = 0.1, α = 50, β = 1.5, γ = 0.99, period = 50, N = 385 (z=1.96, P̂=0.5, e=0.05)
```

→ **v2/v4 hyperparam 7개 verbatim 동일**.

### 2.2 식 (2)~(6) — v4 vs v2 동일

| 식 | v4 verbatim | v2 verbatim (222815 §3 carry) | 일치 |
|---|---|---|---|
| (2) Q-error | `Q-error = max(Card_esti/Card_true, Card_true/Card_esti)` | `Q-error = max(Card_esti / Card_true, Card_true / Card_esti)` | ✓ |
| (3) δ | `δ = α·(Q-error − β) − (100 − α)·sampling_ratio` | `δ = α · (Q-error − β) − (100 − α) · sampling_ratio` | ✓ |
| (4) V_t | `V_t = m·V_{t−1} + η_t·δ` | `V_t = m · V_{t-1} + η_t · δ` | ✓ |
| (5) sample size | `sampling_size_{t+1} = sampling_size_t + V_t` | `sampling_size_{t+1} = sampling_size_t + V_t` | ✓ |
| (6) η decay | `η_{t+1} = γ·η_t` | `η_{t+1} = γ · η_t (where 0 < γ < 1)` | ✓ |

→ **식 (2)~(6) verbatim 동일**.

### 2.3 dataset-specific equilibrium description — v4 보강 가능성 확인

v4 HTML에서 추가 인용:

> "Exqutor converges to a dataset-specific equilibrium that reflects the selectivity patterns and estimation difficulty of each workload" — sample size가 DEEP/SimSearchNet++에서 감소, SIFT에서 증가.

v2 PDF에도 동일 표현(line 770 부근)이 존재 (Capstone CLAUDE.md 정본 표기 "dataset-specific equilibrium"와 일관). v4에서 boost된 부분은 없음.

### 2.4 momentum smoothing — v4 명시

v4 HTML 추가:

> "Momentum smooths fluctuations in adjustment, preventing instability, while the learning rate scheduler gradually reduces update magnitude to ensure convergence."

v2 PDF (222815 §3 carry)와 의미 동일. 표현만 다소 압축됨.

## 3. EB-QAS 정본 anchor §22 외부 인용 — clean source map (★ bibliography hygiene 정정)

직전 정본 anchor §22 인용 [1]~[9] 9건 + 정본 anchor 본문 §12.2·§12.3·§12.5에서 인용되지만 §22 reference list에 entry가 없는 3건(Fauce·Flow-Loss·Efron)을 모두 clean URL·venue·year·pages·DOI/arXiv id로 정리한다.

### 3.1 외부 인용 12 entry — clean source map

| # | 인용 | clean source | Codex 검증 |
|---|---|---|---|
| [1] | Exqutor | **arXiv:2512.09695** — v4 latest (2026-03-29), v2 local PDF base (2025-12-11). URL: https://arxiv.org/abs/2512.09695. Author: Hyunjoon Kim · Chaerim Lim · Hyeonjun An · Rathijit Sen · Kwanghyun Park. EB-QAS 정본 anchor §V-B 인용은 v4·v2 동일(본 §2 검증). | ✓ |
| [2] | Capstone GitHub | https://github.com/johyunbin/Capstone (self-ref, clean 유지) | ✓ |
| [3] | REPORT_paper_exact_v13.md (raw GitHub) | https://raw.githubusercontent.com/johyunbin/Capstone/main/experiments/results/raw/REPORT_%EB%B6%84%EC%84%9D/REPORT_paper_exact_v13.md (self-ref, clean 유지) | ✓ |
| [4] | poc_6_4_extended/summary.md (raw GitHub) | https://raw.githubusercontent.com/johyunbin/Capstone/main/_internal/cache/rq3/latency/poc_6_4_extended/summary.md (self-ref, clean 유지) | ✓ |
| [5] | Bayes Rules! Ch.3 (Beta-Binomial) | https://www.bayesrulesbook.com/chapter-3.html — Alicia A. Johnson · Miles Q. Ott · Mine Dogucu, "Bayes Rules! An Introduction to Applied Bayesian Modeling", CRC Press 2022. clean (utm 없음) | ✓ |
| [6] | Kuchibhotla 2021 (confidence sequence) | https://proceedings.mlr.press/v139/kuchibhotla21a.html — Arun K. Kuchibhotla · Qinqing Zheng, "Near-Optimal Confidence Sequences for Bounded Random Variables", ICML 2021, PMLR v139. PDF: https://proceedings.mlr.press/v139/kuchibhotla21a/kuchibhotla21a.pdf. clean | ✓ |
| [7] | BayesCard | **arXiv:2012.14743** — Ziniu Wu · Amir Shaikhha · Rong Zhu · Kai Zeng · Yuxing Han · Jingren Zhou, "BayesCard: Revitilizing Bayesian Frameworks for Cardinality Estimation", 2020. URL: https://arxiv.org/abs/2012.14743. **★ utm_source=chatgpt.com suffix 제거** | ✓ 정정 |
| [8] | CardEst PVLDB Comprehensive Evaluation | https://vldb.org/pvldb/vol15/p752-zhu.pdf — Rong Zhu · Ziniu Wu · Chengliang Chai · Andreas Kipf · Bolin Ding · Jingren Zhou · Hong Chen · Cuiping Li, "Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation", PVLDB vol15 no.4 pp.752-765 (2022). **★ utm_source=chatgpt.com suffix 제거 + 제목 잘림 정정** | ✓ 정정 |
| [9] | Capstone results README (raw GitHub) | https://raw.githubusercontent.com/johyunbin/Capstone/main/experiments/results/README.md (self-ref, clean 유지) | ✓ |
| ★ [10] | Fauce (정본 anchor §12.3 인용) | https://vldb.org/pvldb/vol14/p1950-liu.pdf — Jie Liu · Wenqian Dong · Qingqing Zhou · Dong Li, "Fauce: Fast and Accurate Deep Ensembles with Uncertainty for Cardinality Estimation", PVLDB vol14 no.11 pp.1950-1963 (2021). **★ 신규 entry (정본 anchor §22 reference list 누락)** | ✓ 정정 |
| ★ [11] | Flow-Loss (정본 anchor §12.5 인용) | https://par.nsf.gov/biblio/10347336 — Parimarjan Negi · Ryan Marcus · Andreas Kipf · Hongzi Mao · Nesime Tatbul · Tim Kraska · Mohammad Alizadeh, "Flow-Loss: Learning Cardinality Estimates That Matter", PVLDB vol14 no.11 pp.2019-2032 (2021). **★ 신규 entry (정본 anchor §22 reference list 누락)** | ✓ 정정 |
| ★ [12] | Efron empirical Bayes overview (정본 anchor §12.2 인용) | https://efron.ckirby.su.domains/papers/2021EB-concepts-methods.pdf — Bradley Efron, "Empirical Bayes: Concepts and Methods", Stanford Statistics Tech Report (2021). **★ 신규 entry (정본 anchor §22 reference list 누락)** | ✓ 정정 |

### 3.2 hygiene 정정 4건 요약

| Hygiene 결함 | 직전 정본 anchor §22 표기 | 본 보고서 정정 |
|---|---|---|
| utm_source suffix (BayesCard) | `https://arxiv.org/abs/2012.14743?utm_source=chatgpt.com` | `https://arxiv.org/abs/2012.14743` |
| utm_source suffix (CardEst) | `https://vldb.org/pvldb/vol15/p752-zhu.pdf?utm_source=chatgpt.com` | `https://vldb.org/pvldb/vol15/p752-zhu.pdf` |
| 제목 잘림 (CardEst) | "Cardinality Estimation in DBMS: A Comprehensive ..." | "Cardinality Estimation in DBMS: A Comprehensive Benchmark Evaluation" |
| reference entry 누락 (Fauce·Flow-Loss·Efron) | 본문 §12.2·§12.3·§12.5 인용만, §22 list X | [10]·[11]·[12] 신규 entry 추가 (본 §3.1) |

본 정정은 사용자 명시 지시 시 정본 anchor §22 inline 반영. 본 세션은 source map만 작성.

## 4. 외부 claim source map (★ Codex (f) 권고 3)

정본 anchor 본문에서 외부 reference를 인용한 claim 한 줄씩 다음과 같이 source map.

| 정본 anchor 위치 | claim | 인용 source |
|---|---|---|
| §1·§4·§9·§10.1·§11.5·§13.2 | Exqutor B1 = Section V-B Bernoulli Adaptive Sampling, momentum/LR scheduler, N=385 fixed sample size, 50-queries trigger | [1] Exqutor §V-B (v4·v2 동일, 본 §2 verbatim 검증) |
| §5.5·§7·§8·§17.3 | Beta-Binomial conjugate posterior `Beta(α+s, β+n−s)`·posterior mean weighted average | [5] Bayes Rules! Ch.3 |
| §11.2 | EB posterior mean이 shrinkage estimator라는 사실 | [5] Bayes Rules! Ch.3 + [12] Efron 2021 EB overview |
| §11.5 | optional stopping 문제 보강 — confidence sequence | [6] Kuchibhotla 2021 PMLR v139 |
| §12.1 | Exqutor와의 직접 연결 (sample-size momentum vs prior accumulation) | [1] Exqutor §V-B |
| §12.2 | empirical Bayes에서 N개 group이 있을 때 group별 prior를 history로 누적 | [12] Efron 2021 EB overview Tech Report (Stanford) |
| §12.3 | Bayesian Network로 cardinality estimation (BayesCard) | [7] BayesCard arXiv:2012.14743 §3 |
| §12.3 | Fauce는 deep ensembles 기반 cardinality estimation with uncertainty | [10] Fauce PVLDB vol14 p1950 (신규 entry) |
| §12.4 | CardEst PVLDB Comprehensive Evaluation — uncertainty-aware cardinality estimation | [8] CardEst PVLDB vol15 p752 Table 3 (제목·utm 정정) |
| §12.5 | Q-error만으로는 plan downstream 효과를 다 포착 못 함 — plan-aware loss | [11] Flow-Loss NSF par/biblio 10347336 (신규 entry) |

본 source map은 측정·발표·보고서 단계에서 외부 reference 정합성 cross-check base.

## 5. 정본 anchor §22 inline 정정 권고 (사용자 결정 영역)

본 보고서 §3.1·§4 source map은 정본 anchor §22의 [1]~[9] 9 entry를 12 entry로 확장하고 hygiene를 정정한다. 권고 단계:

1. **권고 A (필수)**: [7] BayesCard·[8] CardEst URL에서 `?utm_source=chatgpt.com` suffix 제거 + [8] CardEst 제목 "A Comprehensive Benchmark Evaluation"으로 정정.
2. **권고 B (강력 권고)**: [10] Fauce·[11] Flow-Loss·[12] Efron 신규 entry 3건을 §22 reference list에 추가. 본문 §12.2·§12.3·§12.5의 인용이 reference list에 매핑되도록.
3. **권고 C (선택)**: [1] Exqutor URL을 `arxiv.org/abs/2512.09695`로 일반화 (특정 버전 식별자 없는 abstract 페이지) — v4 latest와 v2 local PDF 양쪽 모두 본 anchor에 mapping 가능. 본문 §1·§4·§9·§10.1 등 텍스트는 그대로.

본 세션은 권고 단계만 명시 — 정본 anchor §22 inline 정정은 다음 EB-QAS 세션 또는 활성화 결정 시점에 사용자 명시 지시 시 별도 commit.

## 6. v4 vs v2 — Capstone CLAUDE.md 정본 운영 가이드

| 경로 | 기준 버전 | 근거 |
|---|---|---|
| Capstone CLAUDE.md 정본 | **v2** (2025-12-11) | reference/papers/[0] Exqutor PDF가 v2이며, 메인 트랙 측정·발표·보고서가 본 PDF 기준으로 운영됨 |
| EB-QAS 정본 anchor | **v4** (2026-03-29) | 사용자 paste 시점 강재현 발화가 v4를 인용. §V-B verbatim은 v2와 동일하므로 운영상 무영향 |
| 본 EB-QAS 트랙 산출물 | v4 latest를 기본, v2 PDF base로 cross-check | 본 보고서 §2가 cross-check 정합성 확인 |

**핵심**: v2/v4 분리 운영은 본 트랙 활성화 시 발표·보고서에서 "Exqutor §V-B" 인용 시 항상 본 보고서를 cross-ref해 어떤 버전 표기를 사용했는지 source map. 메인 트랙 외부 노출 자료는 v2 PDF 기준 유지.

## 7. 본 보고서의 활성 시기

본 보고서는 EB-QAS 트랙 활성화 시점에 다음 활용:
1. 정본 anchor §22 reference list 정정 — §5 권고 A·B 적용.
2. measure_ebqas 코드 작성 시 외부 reference cross-check base.
3. 발표·보고서·포스터 외부 노출 자료 작성 시 §6 운영 가이드 적용.

활성화 이전에는 carry 상태로 유지(`_internal/state/ebqas_track/exqutor_대조/`). 메인 트랙 발표·보고서·포스터에는 본 보고서 직접 인용 X — 별도 트랙 산출물.

## 8. 본 보고서의 재현 가능성

본 보고서의 §2 verbatim 인용은 다음 명령으로 재현 가능.

```bash
# v4 HTML fetch (Claude WebFetch)
# URL: https://arxiv.org/html/2512.09695v4
# fetch 시점: 2026-05-23 23:10 KST

# v2 PDF 대조 (직전 222815 §3·§4 carry)
pdftotext "reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf" /tmp/exqutor_v2_full.txt
sed -n '770,800p' /tmp/exqutor_v2_full.txt   # hyperparam verbatim
grep -n "δ\|Q-error\|sampling_size\|momentum\|learning rate" /tmp/exqutor_v2_full.txt
```

본 보고서 §3 source map은 §3.1 표 12 entry의 URL을 직접 fetch로 검증 가능 — 본 세션은 v4 외에 추가 fetch 미수행 (source map의 venue·year·pages·author는 Codex 검증 §2.6 (f) external fetch 결과와 cross-ref).

## 9. 본 신규 보고서와 222815 사이 변경 요약

| 위치 | 222815 | 본 신규 (231042) | 정정 근거 |
|---|---|---|---|
| §1 PDF 식별 | v2 PDF 직접 추출 (reference/papers/) | + v4 HTML 외부 fetch (Claude WebFetch) | 직전 §6 권고 2 carry |
| §2 §V-B verbatim 대조 | v2 단독 | v4 vs v2 cross-check — hyperparam 7개·식 (2)~(6) 동일 확인 | Codex §2.6 (f) finding 1 |
| §3 외부 인용 source map | (없음) | 12 entry clean source map — utm 제거·신규 entry 3건·제목 정정 | Codex §2.6 (f) 권고 1 |
| §4 외부 claim source map | (없음) | 정본 anchor 본문 11 claim → reference 한 줄씩 매핑 | Codex §2.6 (f) 권고 3 |
| §5 정본 anchor 정정 권고 | URL 정정 권고 1건 | 권고 A(필수)·B(강력)·C(선택) 3 단계 | 본 patch |
| §6 v2/v4 운영 가이드 | (없음) | Capstone CLAUDE.md 정본(v2) vs EB-QAS 정본 anchor(v4) 분리 운영 가이드 | 본 patch |

222815는 carry로 유지. 본 신규 231042는 활성화 시점 정본 anchor §22 정정·발표·보고서 외부 인용 cross-check base.
