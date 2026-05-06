# 카톡 RQ3 메시지 템플릿 — 7 method × (시작 §3.1 + 완료 §3.2)

> 본 파일은 RQ3 7개 method 의 카톡 보고 메시지를 미리 채워둔 템플릿.
> §3.1 (시작) 은 측정 직전 그대로 복사, §3.2 (완료) 는 narrative 채운 뒤 발송.
> placeholder = `_internal/RQ3_narrative_template.md` 와 동일 약속.

---

## 발송 우선순위 (다음 세션 진행 순서)

★ **2026-05-06 18:1x 갱신** — 다른 병렬 세션의 `measure_offline.py` 통합 wrapper 반영.
Offline 6 mode (bernoulli/random20/km20/MiniBatch/RandProj/Hilbert) 는 한 번에 측정 가능.

| # | Method | 코드 위치 | 시작 §3.1 | 완료 §3.2 |
|---|---|---|---|---|
| 0 | RANDOM20 + KM20 + 3 offline methods (통합 wrapper) | `experiments/code/rq3/measure_offline.py` (~30분, 6 mode 동시) | [§§OFFLINE-1] | [§§OFFLINE-2] |
| 1 | A. LSH | `experiments/code/rq3/run_lsh.py` (~1h) | [§§A-1] | [§§A-2] |
| 2 | B. KDE-pilot | `experiments/code/rq3/kde/kde_pilot.py` ✅ self-contained | [§§B-1] | [§§B-2] |
| 3 | G. Distance-Shell | `experiments/code/rq3/online_weight/distance_shell.py` ✅ self-contained | [§§G-1] | [§§G-2] |
| 4 | H. Importance Sampling | `experiments/code/rq3/online_weight/importance_sampling.py` ✅ self-contained | [§§H-1] | [§§H-2] |

> **개별 method 카톡** (F/C/E §§F-1/C-1/E-1) 은 측정이 한 wrapper 에 묶이므로 사실상 [§§OFFLINE-2] 안에서 method 별 결과만 분리 보고. 개별 §§F/C/E 메시지는 reference 로만 보관.

---

## §§OFFLINE-1 — Offline 6-mode 통합 측정 시작

```
[RQ3 Phase 1 시작 — Offline 6 mode 통합] {HH:MM}

실험명: measure_offline.py (bernoulli + random20 + km20 + F. MiniBatch + C. Random Projection + E. Hilbert)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~30분 (DEEP+SIFT, KM cluster cache 후 numpy in-memory)

[기획 의도]
- 6 mode 한 번에 측정 → recovery_rate 분모 (random20) + 분자 (km20) + 3 offline method 동시 확보.
- 박세은 비판 ("사전 학습 비용") 에 대한 핵심 답 — F. MiniBatch (1% 학습) 가 oracle 의 80%+ 회수면 production 솔루션.

[측정 목표 + 가설]
- H3-F (MiniBatch): recovery 0.75~0.95
- H3-C (RandProj): recovery 0.10~0.40 (단순 하한)
- H3-E (Hilbert): recovery 0.20~0.60 (PCA + curve)

[기대치]
- KM20 oracle ≈ Δ% -8~-12% (RQ2 'equal' 와 동등)
- RANDOM20 ≈ Δ% +0~+3% (BERN 과 비슷)

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정, 6 mode 통합

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§OFFLINE-2 — Offline 6-mode 완료

```
[RQ3 Phase 1 완료 — Offline 6 mode] {HH:MM} (소요 ~30분)

산출: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_offline.parquet (60,000 rows)

═══ method 별 4단계 narrative (3개) ═══

[F. MiniBatch K-means]
(a) KM20 oracle 의 학습 비용 단축 → production 후보
(b) recovery 0.75~0.95
(c) DEEP/SIFT 평균 0.85
(d) DEEP {recovery_F_DEEP} / SIFT {recovery_F_SIFT}, p_BH {p_BH_F} → {verdict_F}

[C. Random Projection]
(a) 학습 X 의 단순 하한 (JL random matrix → argmax bucket)
(b) recovery 0.10~0.40
(c) DEEP/SIFT 평균 0.20~0.30
(d) DEEP {recovery_C_DEEP} / SIFT {recovery_C_SIFT}, p_BH {p_BH_C} → {verdict_C}

[E. Hilbert Curve]
(a) PCA 2D + curve + quantile = 학습 X + 일부 cluster 구조 반영, contribution 후보
(b) recovery 0.20~0.60
(c) DEEP 0.30~0.50, SIFT 0.40~0.60 (skew 우위 가설)
(d) DEEP {recovery_E_DEEP} / SIFT {recovery_E_SIFT}, p_BH {p_BH_E} → {verdict_E}

═══ 의의 + 다음 ═══
- {3 method 의 ranking 한 줄 / production 후보 명시 / RQ1 narrative 강화 여부}
- 다음 Phase 2 — A. LSH (run_lsh.py, ~1h)

자동 git commit + push 완료
```

---

---

## §§F-1 — F. MiniBatch K-means (시작)

```
[실험 #8 (P2: F) 시작] {HH:MM}

실험명: F. MiniBatch K-means
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~1h

[기획 의도]
- KM20 oracle 의 학습 비용 (~30~60s) 을 ~5초로 단축 (1% sample MiniBatchKMeans).
- recovery 0.85+ 면 production 솔루션 명확.

[측정 목표 + 가설]
- H3-F: recovery_rate 0.75~0.95
- 정량: cluster 균질성 max/min ratio < 3, p_BH ≪ 0.05 (vs RANDOM20)

[기대치]
- recovery_rate 85% 평균

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- 학습 sample = 1% (~10K rows from PG)

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§F-2 — F. MiniBatch K-means (완료)

```
[실험 #8 (P2: F) 완료] {HH:MM} (소요 ~Nh)

실험명: F. MiniBatch K-means
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_minibatch.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — KM20 oracle 의 학습 비용 단축 + recovery 보존이 production 핵심.
(b) 가설 — H3-F: recovery_rate 0.75~0.95.
(c) 예상 결과 — DEEP/SIFT recovery 0.85, p_BH ≪ 0.05.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (mean q_error {method_q_SIFT}, p_BH {p_BH_SIFT})
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의 한 줄: production 솔루션 후보 / oracle 대용 가능 등}
- 다음 실험 #5 (C. Random Projection) 진행

자동 git commit + push 완료
```

---

## §§C-1 — C. Random Projection (시작)

```
[실험 #5 (P2: C) 시작] {HH:MM}

실험명: C. Random Projection (Johnson-Lindenstrauss)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~2h

[기획 의도]
- 학습 X 의 가장 단순 baseline (random matrix → argmax bucket).
- recovery 의 하한 후보 — 다른 method 의 reference.

[측정 목표 + 가설]
- H3-C: recovery_rate 0.10~0.40
- 정량: 0 < recovery < 0.40, p_BH ≤ 0.05 (RANDOM20 보다 약간 우수)

[기대치]
- recovery_rate 20~30% 평균

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- argmax bucket (K=20) 결정론 seed=42

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§C-2 — C. Random Projection (완료)

```
[실험 #5 (P2: C) 완료] {HH:MM} (소요 ~Nh)

실험명: C. Random Projection
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_random_projection.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — 학습 X 의 단순 하한 baseline. cluster 구조 보존 한계 정량화.
(b) 가설 — H3-C: recovery_rate 0.10~0.40.
(c) 예상 결과 — DEEP/SIFT recovery 0.20~0.30, RANDOM20 보다 약간 우수.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (mean q_error {method_q_SIFT}, p_BH {p_BH_SIFT})
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의: 다른 method 의 reference 역할 확립 / argmax bucket 의 한계 입증 등}
- 다음 실험 #7 (E. Hilbert Curve) 진행

자동 git commit + push 완료
```

---

## §§E-1 — E. Hilbert Curve (시작)

```
[실험 #7 (P3: E) 시작] {HH:MM}

실험명: E. Hilbert Curve (PCA 2D + space-filling curve)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~4h

[기획 의도]
- PCA 2D + Hilbert curve + quantile 분할 → "결정론 + 균질 cluster + 일부 cluster 구조 반영"
- 본 연구 contribution 후보 — Hilbert > MiniBatch 면 학습 비용 0 으로 oracle 근접

[측정 목표 + 가설]
- H3-E: recovery_rate 0.20~0.60
- SIFT (skew) > DEEP (normal) 가능 (PCA 가 skew 방향 잡음)

[기대치]
- DEEP recovery 30~50%, SIFT recovery 40~60%

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- PCA fit 5% sample, p=10 (Hilbert grid 1024×1024)

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§E-2 — E. Hilbert Curve (완료)

```
[실험 #7 (P3: E) 완료] {HH:MM} (소요 ~Nh)

실험명: E. Hilbert Curve
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_hilbert.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — PCA + space-filling curve 로 학습 비용 0 + cluster 구조 반영.
(b) 가설 — H3-E: recovery 0.20~0.60. SIFT > DEEP 가능.
(c) 예상 결과 — DEEP 0.30~0.50, SIFT 0.40~0.60.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (mean q_error {method_q_SIFT}, p_BH {p_BH_SIFT})
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의: 본 연구 contribution 강화 / PCA 가 skew 잡는 효과 / 학습 비용 0 의 가치 등}
- 다음 실험 #6 (A. LSH) 진행

자동 git commit + push 완료
```

---

## §§A-1 — A. LSH (시작)

```
[실험 #6 (P4: A) 시작] {HH:MM}

실험명: A. LSH (Random Hyperplane Cosine)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~4h

[기획 의도]
- 5 hyperplanes → 32 raw bucket → mod 20 → K=20 strata.
- locality-sensitive — 가까운 vector 같은 bucket 확률 높음 (Charikar 2002).
- 학습 X (random projection 1회), 결정론 seed=0.

[측정 목표 + 가설]
- H3-A: recovery_rate 0.30~0.60
- LSH > Random Projection (locality-sensitive 효과)

[기대치]
- recovery_rate 40~50% 평균

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- 5 hyperplanes × mod 20

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§A-2 — A. LSH (완료)

```
[실험 #6 (P4: A) 완료] {HH:MM} (소요 ~Nh)

실험명: A. LSH
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_lsh.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — locality-sensitive hashing 으로 학습 X + 가까운 vector 같은 bucket.
(b) 가설 — H3-A: recovery 0.30~0.60. LSH > RandProj.
(c) 예상 결과 — DEEP/SIFT recovery 0.40~0.50.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (mean q_error {method_q_SIFT}, p_BH {p_BH_SIFT})
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의: locality-sensitive 의 가치 / mod 20 bucket 균질성 한계 등}
- 다음 실험 #10 (B. KDE-pilot) 진행 [코드 완료 ✅]

자동 git commit + push 완료
```

---

## §§B-1 — B. KDE-pilot (시작)

```
[실험 #10 (P5: B) 시작] {HH:MM}

실험명: B. KDE-pilot Online (Silverman + Gaussian KDE + Neyman)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~6h

[기획 의도]
- KM20 strata 위 query 마다 pilot 5×20=100 → σ_i online 추정 (Silverman + KDE).
- RQ2 의 정적 σ_i 보다 query-adaptive 가 얼마나 이득인지 정량.
- Online paradigm 의 이론 상한 후보.

[측정 목표 + 가설]
- H3-B: recovery_rate 0.50~0.80
- 좁은 sel (s=0.01) 에서 RQ2 Neyman 대비 +5~15%p 이득

[기대치]
- recovery_rate 65% 평균

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- pilot 5/cluster (총 100), main 285 Neyman

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§B-2 — B. KDE-pilot (완료)

```
[실험 #10 (P5: B) 완료] {HH:MM} (소요 ~Nh)

실험명: B. KDE-pilot Online
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_kde_pilot.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — query-adaptive σ 추정으로 RQ2 정적 Neyman 의 한계 돌파 시도.
(b) 가설 — H3-B: recovery 0.50~0.80. 좁은 sel 에서 우위 큼.
(c) 예상 결과 — DEEP/SIFT recovery 0.65 평균.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (mean q_error {method_q_SIFT}, p_BH {p_BH_SIFT})
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의: Online query-adaptive 의 이론 상한 입증 / RQ2 Neyman 대비 이득 등}
- 다음 실험 #9 (G. Distance-Shell) 진행 [코드 완료 ✅]

자동 git commit + push 완료
```

---

## §§G-1 — G. Distance-Shell (시작)

```
[실험 #9 (P6: G) 시작] {HH:MM}

실험명: G. Distance-Shell Online (5-shell quantile + Neyman)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~4h

[기획 의도]
- 사전 분할·학습 모두 X. query 마다 pilot 50개 → distance quantile 5등분 → Neyman.
- "가장 단순한 query-adaptive" — KDE-pilot 의 KDE 평활화 ablation 역할.

[측정 목표 + 가설]
- H3-G: recovery_rate 0.25~0.50
- KDE-pilot 의 ~2/3 수준이면 KDE 평활화의 의의 입증

[기대치]
- recovery_rate 35% 평균

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- pilot 50, main 335, 5 shells

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§G-2 — G. Distance-Shell (완료)

```
[실험 #9 (P6: G) 완료] {HH:MM} (소요 ~Nh)

실험명: G. Distance-Shell
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_distance_shell.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — KDE 평활화 의의 ablation. 사전 분할·학습 0 의 단순 baseline.
(b) 가설 — H3-G: recovery 0.25~0.50. KDE-pilot 의 ~2/3.
(c) 예상 결과 — DEEP/SIFT recovery 0.30~0.40.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (mean q_error {method_q_SIFT}, p_BH {p_BH_SIFT})
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의: KDE 평활화 효과 정량 / quantile-equal 가정의 한계 등}
- 다음 실험 #11 (H. Importance Sampling) 진행 [코드 완료 ✅]

자동 git commit + push 완료
```

---

## §§H-1 — H. Importance Sampling (시작)

```
[실험 #11 (P7: H) 시작] {HH:MM}

실험명: H. Importance Sampling (비분할 + 가중치, 2x2 factorial)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~6h

[기획 의도]
- 분할 X — 모든 row 에 importance weight + uniform sample + IPW HT.
- 2x2 factorial: (가중치 hard/soft) × (대역폭 sample/pilot) — 평활화·pilot 효과 분리.
- "분할의 가치" 가설 검증 — 비분할 method 가 분할 method 못하면 분할 의의 정량화.

[측정 목표 + 가설]
- H3-H: recovery_rate 0.30~0.70 (mode 별 0.30~0.60+)
- (soft + pilot) 이 KDE-pilot 의 ~80% 수준이면 분할 의의 입증

[기대치]
- 4 mode 평균 recovery_rate 50% 평균, best mode 60%+

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정
- 4 mode (hard/soft × sample/pilot)

진행 후 결과 다시 공유드리겠습니다 🙏
```

## §§H-2 — H. Importance Sampling (완료)

```
[실험 #11 (P7: H) 완료] {HH:MM} (소요 ~Nh)

실험명: H. Importance Sampling 2x2
산출 위치: experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_importance_sampling.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — "분할의 가치" 가설 검증 + 평활화·pilot 효과 분리 (2x2 factorial).
(b) 가설 — H3-H: best mode recovery 0.60+ (KDE-pilot 의 ~80%).
(c) 예상 결과 — (soft+pilot) best, (hard+sample) worst.
(d) 실제 결과
   - DEEP recovery {recovery_DEEP} (best mode, mean q_error {method_q_DEEP}, p_BH {p_BH_DEEP})
   - SIFT recovery {recovery_SIFT} (best mode)
   - {verdict} — {expected_band}. {narrative_extra}

═══ 의의 + 다음 ═══
- {의의: 분할 method 의 우위 정량 / 평활화 vs pilot 의 상대 중요도 등}
- ★ 7-way 모두 완료 → 통합 분석 (rq3_combine.py + rq3_figures.py) 단계로

자동 git commit + push 완료
```

---

## ⭐ 7-way 종합 보고 (모든 method 완료 후 발송)

```
[RQ3 7-way 종합 완료] {HH:MM}

모든 method 측정·분석 완료. 산출:
- experiments/results/rq3_agnostic/{YYYY_MM_DD}/rq3_combined.parquet
- rq3_summary.csv, rq3_pairwise.csv, rq3_ranking.csv
- experiments/figures/rq3_distribution_agnostic/ (fig6/7/8/9)

═══ Recovery Rate Ranking ═══
1. {top1_method}: recovery {top1_recovery}
2. {top2_method}: recovery {top2_recovery}
3. {top3_method}: recovery {top3_recovery}
... (7-way ranking)

═══ Paradigm 별 결론 ═══
- Offline 4 → {offline_winner} 가 production 솔루션 후보
- Online 2 → {online_winner} 이 query-adaptive 의 가치 입증
- Weight 1 → {weight_finding}

═══ Cost-Recovery Pareto frontier ═══
- 좌상단 (low cost + high recovery): {pareto_methods}
- KM20 oracle 의 80%+ recovery 달성한 method: {oracle_class}

═══ RQ1 narrative 강화 여부 ═══
{rq1_finding_oneline}

다음: 5/8 19:00 비대면 회의 자료 정리 + 발표 자료 초안 (5/21).
```

---

**작성 규칙**
- 시각 (HH:MM) 은 KST 기준 (`python3 -c "from datetime ..."` 한 줄로 확인)
- placeholder 채울 때 `_internal/RQ3_narrative_template.md` 와 동일 값 사용
- 발송 직전 1회 read-through 권장 (오타·placeholder 누락 방지)
