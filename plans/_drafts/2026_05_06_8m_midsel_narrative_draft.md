# DEEP 8M mid-sel 보강 narrative draft

> 메인 세션이 8M × s={0.10, 0.30} × {system, bernoulli, stratified} 측정 push 한 후
> 회의 outline (`plans/5_8_19시_회의_outline.md`) §2.4 와 §2.5 사이 또는 §2.4 직후에
> 통합 가능한 narrative draft.
>
> 작성: 조현빈 (병렬 세션) · 2026-05-06 17:55 KST · 측정 마무리 직후 trigger 용

---

## 통합 위치 제안

회의 outline 의 다음 두 위치 중 택일 (메인 세션 판단):

1. **§2.5 RQ1 8M Cross-Dataset 외적 타당성 (추가 섹션)** — §2.4 다음에 새 섹션
2. **§2.1 RQ1 H1 정량 입증 (보강)** — 기존 SIFT 표 다음에 8M cross-dataset 단락 추가

권장: **1번 (별도 §2.5)** — 외적 타당성 narrative 가 H1 정량 입증과 차별화되어 명확.

---

## 단락 1 — 측정 개요

5/6 W1 sprint 의 마지막 보강 측정으로 DEEP 8M × s∈{0.10, 0.30} × {system, bernoulli, stratified}
× 5 seed × 100 query = 3,000 rows 를 측정하였다. 기존 8M 측정 (4/16, phase7) 은
s∈{0.50, 0.05, 0.01} 만 다루었고, mid-sel 구간 (s=0.10, 0.30) 은 결측이었다. 이 보강
측정으로 1M / SIFT 1.5M 과 동일한 5-sel 격자가 8M 에도 완성되며, RQ1 의 H1
(skew → 부정확) 패턴이 데이터 규모 8 배 차이에서도 재현되는지가 외적 타당성 차원에서
직접 검증된다.

기존 측정과의 차이:
- 4/16 phase7: BERN/STRAT 두 mode × 3 sel — RANDOM20 측정 포함되어 Two-Level 분해 가능.
- 5/6 mid-sel: SYSTEM/BERN/STRAT 세 mode × 2 sel — **RANDOM20 미측정**, 따라서
  mid-sel (0.10, 0.30) 의 Two-Level 분해는 본 보강에서는 불가. KM20 only gradient
  의 단조성으로 외적 타당성 평가.

## 단락 2 — KM20 단조성 (외적 타당성 핵심)

(★ 측정 결과 들어오면 자동 갱신 — `update_8m_midsel.py --update` 로 정리.md
"### DEEP 8M 결과 (외적 타당성)" 표 갱신)

기대치: DEEP 1M 의 KM20 gradient (50% +1.64% → 30% +2.62% → 10% +4.19% → 5% +1.85% → 1% +8.93%)
와 같은 "sel 좁아질수록 KM20 효과 증가 (단, 10%→5% 비단조성 존재)" 패턴이 8M 에서도
재현되면 H1 의 외적 타당성 강화. 만약 8M mid-sel 에서 더 강한 단조성이 검출되면
4/16 phase7 의 1% noise 영역과 결합한 보다 robust 한 narrative 가능.

## 단락 3 — Two-Level Decomposition 의 부분 갱신

기존 DEEP 8M Two-Level 표:

| selectivity | Level 1 (비례 배분) | Level 2 (공간 인식) | Total (KM20) |
|-------------|--------------------|--------------------|-------------|
| 50% | +1.10% | +0.66% | +1.76% |
| 5% | +0.20% | +0.35% | +0.55% |
| 1% | +11.06% | -11.77% | -0.71% |

5/6 보강에서는 mid-sel (0.10, 0.30) 의 **Level 1 (RAND20) 측정이 부재** 하므로
Total (KM20) 만 갱신되며 Level 1/Level 2 분해 자리는 "(RAND20 미측정)"
표시. 이는 학술적 한계이며, 본 측정의 우선순위가 RQ3 (7-way distribution-agnostic)
로 이동했기 때문이다. RAND20 mid-sel 측정은 "future work — RQ3 와 병행 가능 시 추가"
로 명시.

## 단락 4 — SYSTEM-block 효과 (RQ1 H1 보강)

phase7 measure.py 가 같이 산출한 system vs bernoulli 비교는 RQ1 의 H1 narrative
에 추가 가치를 제공한다. 1M / SIFT 의 RQ1 SYS-BERN 격차 (실험 #1 결과) 는
**모든 sel 에서 SIFT(skew) > DEEP(normal)**:

| sel | SIFT(skew) Δ% | DEEP 1M Δ% | (SIFT − DEEP_1M) | DEEP 8M Δ% (★ 측정) |
|---|---|---|---|---|
| 0.50 | +14.36% | +12.59% | +1.77%p | (★ 측정) |
| 0.30 | +14.85% | +14.05% | +0.80%p | (★ 측정) |
| 0.10 | +16.68% | +14.76% | +1.92%p | (★ 측정) |
| 0.05 | +17.32% | +12.61% | +4.71%p | (★ 결측) |
| 0.01 | +10.27% | +4.66% | +5.61%p | (★ 결측) |

8M mid-sel (0.10, 0.30) 의 SYS-BERN 격차가 DEEP 1M 의 같은 sel 격차와 비슷한
크기 (+14% 안팎) 로 나오면 → DEEP 패밀리의 H1 패턴이 데이터 규모에 robust 함을 입증.
SIFT > DEEP 의 cross-dataset 격차도 8M 에 대해 동일 부호로 재현되면 H1 narrative
가 한층 강화된다.

## 단락 5 — 회의 발표 핵심 메시지

(a) **외적 타당성 (RQ1+RQ2)**: DEEP 8M 의 mid-sel KM20 효과가 1M 패턴과 일관되면
"우리의 결론은 데이터 규모 8 배 차이에서도 robust" 라는 결정적 narrative 확보.

(b) **연구 설계의 견고성**: SYSTEM-block 효과의 cross-dataset 비교가 8M 에서도
DEEP < SIFT 부호 일관이면 H1 의 외적 타당성 입증.

(c) **Limitation 명시**: RAND20 mid-sel 부재로 8M mid-sel 의 Two-Level 분해 불가
— RQ3 우선순위 이동의 trade-off 명시. 학술적 정직성으로 가산점.

(d) **다음 단계 (W2)**: RQ3 측정에 본 측정 인프라 (Python 시뮬레이션, fresh conn
per cluster) 그대로 활용 — 측정 효율 W1 sprint 에서 검증됨 (실험 #4 의 51초/40K rows).

---

## 인용 그림 (병렬 세션이 자동 생성 중)

`generate_8m_figures.py --update` 실행 후 산출:

- `fig6_8m_midsel_gradient.png` — 8M 5sel × KM20 gradient (1M/SIFT overlay)
- `fig7_two_level_decomposition_full.png` — 1M/SIFT/8M Level 1/2/Total (8M mid-sel
  은 hatched)
- `fig8_rq1_cross_dataset_8m_extended.png` — RQ1 H1 SYS-BERN gradient (8M sys20 추가)

---

## Trigger 명령 (메인 세션 측정 push 직후)

```bash
# 1. 분석 함수 재실행 → 정리.md in-place 갱신
python3 experiments/code/local_analysis/update_8m_midsel.py --update

# 2. figures 자동 생성
python3 experiments/code/local_analysis/generate_8m_figures.py --update

# 3. (선택) 본 draft 의 단락 1~5 를 회의 outline §2.4 직후로 통합
#    수동 — 메인 세션이 narrative 톤 검토 후 외부 outline.md 에 paste

# 4. git add + commit + push
git add experiments/results/RQ1_RQ2\ 실험\ 결과\ 정리.md \
        experiments/figures/rq1_rq2_w1_sprint/fig{6,7,8}*.png
git commit -m "RQ3 P8: 8M mid-sel 보강 분석 + figures + 정리.md 갱신"
git push origin main
```

---

**작성**: 조현빈 · 2026-05-06 17:55 KST · 5/8 회의 발표 자료 보강용
