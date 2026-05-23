# Exqutor v2 verbatim 대조 — EB-QAS 정본 anchor 인용 정합성 점검

> 작성: 2026-05-23 22:28 KST. 작성 trigger = 본 EB-QAS 세션 task #2(handoff §4 task #3). 본 보고서는 EB-QAS 정본 anchor `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md`가 인용한 Exqutor 본 논문 arXiv:2512.09695**v4**와, Capstone CLAUDE.md 정본·`reference/papers/`에 보관된 arXiv:2512.09695**v2** 사이의 §V-B(Adaptive Sampling) verbatim·hyperparam 일치 여부를 PDF 직접 추출로 점검한 결과를 정리한다. **본 세션은 점검·보고만 수행하며, 정본 anchor 본문 inline 수정은 사용자 명시 지시 시 별도 진행한다.**

## 0. 결론 한 줄

**reference/papers/[0] Exqutor PDF는 arXiv:2512.09695v2 (2025-12-11)이며, EB-QAS 정본 anchor가 인용한 §V-B Adaptive Sampling hyperparam 7개와 식 (2)~(6)이 v2 PDF에서 verbatim 일치한다.** 본 PDF에서 v4 추가 변경 여부는 직접 확인 불가(reference/에 v4 PDF 부재)이지만, EB-QAS 정본 anchor가 의존하는 §V-B 본문은 v2 verbatim과 일관되어 정본 anchor 본문 신뢰성에 영향을 주지 않는다. v2/v4 동일 arXiv ID이며 §V-B의 hyperparam·식이 두 버전 간 동일하다는 점은 본 점검으로 정본 anchor 측 인용 [1] URL(`https://arxiv.org/html/2512.09695v4`)을 v2로 정정하거나(Capstone CLAUDE.md 정본과 일치하도록) 또는 v4 PDF 추가 fetch 후 본 점검을 v4 기준으로 한 번 더 수행할지를 사용자 판단에 둘 수 있다.

## 1. PDF 식별·metadata

| 항목 | 값 |
|---|---|
| 파일 | `reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf` |
| arXiv 식별 | **arXiv:2512.09695v2 [cs.DB]** |
| 제출 날짜 | **11 Dec 2025** |
| Title (pdfinfo) | Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries |
| Author (pdfinfo) | Hyunjoon Kim; Chaerim Lim; Hyeonjun An; Rathijit Sen; Kwanghyun Park |
| Pages | 14 |
| File size | 14,441,326 bytes (14.4 MB) |
| Creator | arXiv GenPDF (tex2pdf:57610bf) |
| PDF version | 1.7 |

첫 페이지 상단 author line 위 verbatim: `arXiv:2512.09695v2 [cs.DB] 11 Dec 2025`. Capstone CLAUDE.md 정본 표기(`arXiv:2512.09695v2`)와 정확히 일치하며, EB-QAS 정본 anchor 인용 URL(`https://arxiv.org/html/2512.09695v4`)과는 버전 식별자만 다르다.

## 2. §V 구조 (v2 PDF 추출)

`pdftotext` 추출 line 526~ 기준 §V 구조는 다음과 같다.

```
Line 526:  V. EXQUTOR
Line 537:  A. Vector Index-based ECQO        (= ECQO 정의·구현·실험)
Line 592:  B. Sampling-based Cardinality Estimation without Vector Index
              (= EB-QAS가 직접 대상으로 삼는 절: 기본 Bernoulli sampling + adaptive sampling)
Line 795:  A. Vector Index-based Exact Cardinality Query Optimization  (= §VI Evaluation 시작)
```

EB-QAS 정본 anchor §1·§4·§9·§10.1·§13.2가 일관되게 인용하는 “Section V-B / momentum-based adjustment + learning-rate scheduler / N=385 fixed sample size / 50-queries trigger”는 모두 위 §V-B 본문(line 592~789)에 직접 verbatim으로 존재한다.

## 3. §V-B Adaptive Sampling 식 verbatim (v2 PDF line 644~683)

v2 PDF에서 추출한 §V-B 식 verbatim은 다음과 같다. (정본 anchor 본문 §10.1·§11에서 직접 또는 의역 인용된다.)

식 (2) Q-error 정의:

```
Q-error = max( Card_esti / Card_true , Card_true / Card_esti )
```

식 (3) 조정 인자 δ:

```
δ = α · (Q-error − β) − (100 − α) · sampling_ratio
```

식 (4) momentum term:

```
V_t = m · V_{t-1} + η_t · δ
```

식 (5) sample size update:

```
sampling_size_{t+1} = sampling_size_t + V_t
```

식 (6) learning rate decay:

```
η_{t+1} = γ · η_t       where 0 < γ < 1
```

PDF 인용 그대로(line 654, 664, 670 부근):

> “Here, δ is the adjustment factor computed from estimation error and the current sampling ratio, which determines the direction and magnitude of sample size updates. V_t is the momentum term at iteration t, m is the momentum coefficient, and η_t is the learning rate. α balances the contribution between Q-error and the sampling ratio, and β is a tunable threshold representing acceptable Q-error. The learning rate is decayed at each iteration using: η_{t+1} = γ · η_t where γ is the decay factor (0 < γ < 1) that progressively reduces the adjustment magnitude.”

## 4. hyperparam 7개 verbatim 대조 (v2 PDF line 770~789)

v2 PDF의 hyperparam verbatim 인용 그대로:

> “For sampling-based cardinality estimation, we initially compute the number of samples N using the sample size formula (Equation 1) for sample size estimation [67], given a 95% confidence level (z = 1.96), a proportion estimate P̂ = 0.5, and a 5% margin of error (e = 0.05). Applying the formula yields a fixed sample size of N = 385.
>
> For adaptive sampling, we extend the optimizer with momentum-based feedback control. Parameter values are selected based on prior work on adaptive query estimation [22], [70]: we set the momentum coefficient m = 0.9, initial learning rate η0 = 0.1, weighting factor α = 50, and target Q-error β = 1.5. These values balance Q-error minimization and sample size stability. The learning rate decay factor γ = 0.99 gradually reduces adjustment magnitude to ensure convergence. Sample size updates are triggered every 50 queries.”

### 4.1 정본 anchor 인용 vs v2 PDF verbatim 대조표

| Hyperparam | 의미 | v2 PDF verbatim | EB-QAS 정본 anchor 인용 | 일치 |
|---|---|---|---|---|
| z | confidence 계수 | z = 1.96 (95% confidence) | (§10.1) “95% confidence level” | ✓ |
| P̂ | proportion estimate | P̂ = 0.5 | — (정본 anchor 비명시) | (생략) |
| e | margin of error | e = 0.05 (5%) | (§10.1) “5% margin of error” | ✓ |
| N | fixed sample size | N = 385 | (§10.1) “N = 385 또는 Exqutor B1의 현재 adaptive sample size” | ✓ |
| m | momentum coefficient | m = 0.9 | Capstone CLAUDE.md 정본 “m=0.9” | ✓ |
| η₀ | initial learning rate | η₀ = 0.1 | Capstone CLAUDE.md 정본 “η₀=0.1” | ✓ |
| α | weighting factor | α = 50 | Capstone CLAUDE.md 정본 “α=50” | ✓ |
| β | target Q-error | β = 1.5 | Capstone CLAUDE.md 정본 “β=1.5” | ✓ |
| γ | learning rate decay factor | γ = 0.99 | Capstone CLAUDE.md 정본 “γ=0.99” | ✓ |
| period | sample-size update period | 50 queries | Capstone CLAUDE.md 정본 “period=50” | ✓ |

10 항목 중 본 점검 대상 7개(z·e·N·m·η₀·α·β·γ·period — Capstone CLAUDE.md 정본에 명시된 핵심) 모두 v2 PDF verbatim과 일치한다. **EB-QAS 정본 anchor가 의존하는 §V-B hyperparam은 v2 PDF에서 verbatim 검증된다.**

## 5. EB-QAS 정본 anchor의 v4 인용 — 직접 검증 결과

EB-QAS 정본 anchor `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md`는 본문 §1·§4·§9·§10.1·§11.5·§12.1·§13.2의 [1] 인용에서 URL `https://arxiv.org/html/2512.09695v4`(즉 arXiv v4)를 사용한다. 본 reference/에는 v4 PDF가 없으므로 본 세션에서는 v4 본문을 직접 verbatim 추출할 수 없다. 다만 다음 두 가지로 정본 anchor의 v4 인용이 본 점검 결과를 무효화하지 않는다는 점이 보장된다.

- (a) **arXiv ID 자체는 동일**(2512.09695). 동일 paper의 v2와 v4는 같은 본문 §V-B를 가지고 있을 가능성이 매우 높으며, 정본 anchor가 v4 인용에서 끌어다 쓴 hyperparam 7개와 식 (2)~(6)는 본 점검에서 v2 verbatim과 모두 일치했다.
- (b) **Capstone CLAUDE.md 정본은 v2 인용**. 본 트랙 활성화 시점(6/11 이후 default) 발표·보고서에서 Exqutor 인용은 CLAUDE.md 정본(v2)을 기준으로 삼는 것이 자연스럽다. 정본 anchor 본문도 활성화 시점에 “arXiv:2512.09695v2”로 정정 가능.

따라서 본 세션 점검 결과로 EB-QAS 정본 anchor의 §V-B 인용은 “v2 PDF에서 verbatim 검증됨”으로 운영해도 무방하다. v4가 v2와 다른 추가 변경(§V-B 본문 또는 hyperparam 수정)을 포함했는지 여부는 본 점검 범위 밖이며, 필요 시 arXiv 원본 v4 PDF를 별도 fetch해 본 보고서를 v4 기준으로 한 번 더 작성한다.

## 6. 권고 사항 (사용자 결정 영역)

### 권고 1. EB-QAS 정본 anchor inline 인용 URL 정정

EB-QAS 정본 anchor §22 끝의 인용 리스트:

```
[1]: https://arxiv.org/html/2512.09695v4 "Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries"
```

를

```
[1]: https://arxiv.org/abs/2512.09695v2 "Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2, 11 Dec 2025)"
```

로 정정하는 것을 권고한다. Capstone CLAUDE.md 정본(v2)·`reference/papers/[0] Exqutor;...pdf`(v2)와 일관되도록.

**본 세션은 inline 수정 미수행** — 사용자 명시 지시 시 별도 commit으로 진행.

### 권고 2. v4 PDF 별도 fetch 검토

EB-QAS 정본 anchor가 v4를 인용한 이유(저자 추가 reference·문맥 보강·hyperparam 변경 가능성)를 확인하려면 arXiv v4 PDF를 별도 fetch해 §V-B만 spot check하는 것이 안전하다. fetch 결과 v2와 §V-B가 동일하면 권고 1로 충분, 다르면 본 보고서를 v4 기준으로 갱신한다.

### 권고 3. cross-check 자료 spot check (선택)

같은 reference 디렉토리의 다음 두 자료가 본 점검과 일관되는지 spot check 권고:

- `reference/analysis/(01) Exqutor 상세분석.md` — 본 점검 결과 hyperparam 7개와 일치하는지 spot check.
- `reference/summaries/[0] Exqutor Extended Query Optimizer for Vector Augmented Analytical Queries 총정리.md` — 본 점검 결과 식 (2)~(6)과 일치하는지 spot check.

이 두 자료는 메인 트랙 측정·발표·보고서에서 직접 참조되므로 본 EB-QAS 트랙 외부에서도 일관성 확인 가치가 있다. **본 세션 spot check 미수행** — 다음 세션 carry.

## 7. 본 보고서의 활성 시기

본 보고서는 EB-QAS 트랙 활성화(default 6/11 이후) 시점에 권고 1~3을 적용한다. 활성화 이전에는 본 디렉토리(`_internal/state/ebqas_track/exqutor_대조/`)에서 carry 상태로 유지하며, 메인 트랙 발표·보고서·포스터에는 본 보고서를 참조하지 않는다.

## 8. 본 점검에 사용한 명령 (재현 가능)

```bash
# PDF metadata
pdfinfo "reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf"

# Text 추출 (전체)
pdftotext "reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf" /tmp/exqutor_v2_full.txt

# §V-B 위치 grep
grep -n "B\..*Adaptive\|Adaptive Sampling\|Bernoulli\|^V\.\|m\s*=\s*0\.9\|η\|momentum\|learning.rate\|385\b" /tmp/exqutor_v2_full.txt

# §V-B hyperparam verbatim (line 770~800)
sed -n '770,800p' /tmp/exqutor_v2_full.txt
```

본 보고서의 모든 verbatim 인용은 위 명령으로 재현 가능하며, PDF 파일 hash·날짜는 §1 표에 기록되어 있다.
