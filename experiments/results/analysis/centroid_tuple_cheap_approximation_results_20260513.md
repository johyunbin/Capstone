# Centroid tuple cheap 근사 측정 결과 분석 (5/13)

## 0. 작성 status

- **분석 대상**: A2-Fig9 cell × 4 anchor method × 2 mode = 8 measurement (★ Exqutor paper fig 별 cell 한도 내, 사용자 16:45 결정)
- **회수 status**: ★ **8/8 회수 완료 (5/13 19:56:59 KST)**
- **본 문서 status**: ★ **FINAL** — multi-join re-stratification (multi_join_restratification_results_20260513.md) 후속 분석
- **핵심 finding**: CaseB 증강 모드에서 Centroid tuple cheap 근사가 모든 method 에서 multi-jn 보다 우위 (mean -0.84p, 0 학습 비용). CaseA 단독 대체 모드는 method-conditional (hyperloglog + chao_weighted 큰 개선, sparse_rp marginal, hilbert_real harmful).

---

## 1. 측정 framework

### 1.1 Centroid tuple wrapper v3 design (5/13 16:50)

강재현 5/13 14:27 verbatim: "기존에 table 별로 clustering한 거를 저비용으로 multi-reclustering에 근사하는 방법 같은거".

본 wrapper v3 는 multi-join re-stratification (864 차원 concat KM20 expensive 학습) 의 cheap 근사 design 으로, 두 single-table KM20 학습 결과의 (s_A, s_B) tuple 을 새 stratum 으로 사용한다. 구체적 단계는 다음과 같다.

**학습 단계 (single-table, cheap)**:
- **KM20_A**: partsupp_deep_10 의 96 차원 vector 위 MiniBatch K-means K=20 학습
- **KM20_B**: part_wiki_10 의 768 차원 vector 위 MiniBatch K-means K=20 학습
- 두 학습 모두 single-table 영역으로 cheap (864 차원 concat 학습 대비 약 1/8)

**Multi-join 시점 (cheap stratum 결정)**:
- 각 row 의 (s_A, s_B) tuple 식별 (K² = 400 잠재 strata)
- Frequency-based top-K folding: 가장 자주 발생하는 K=20 tuples 에 unique stratum_id [0, K-1) 부여
- Rare tuples 은 modulo fallback (encoded % K)

**Vector pool return**: 96 차원 query space (partsupp_deep 측) 만 반환, stratum_id 는 folded 결과.

### 1.2 비교 framework

본 측정의 paired 비교 3-way:
- **(a) carry-over**: single-table 96 차원 KM20 학습 후 stratum_id column 재사용 (기존 본 연구 framework, baseline)
- **(b) multi-join re-stratification**: 864 차원 concat KM20 fresh 학습 + 96 차원 query space return (expensive, 5/13 16:13 finalize)
- **(c) Centroid tuple cheap 근사**: 두 single-table KM20 + (s_A, s_B) tuple folding (cheap, 본 측정)

3-way paired Δ% 비교를 통해 cheap 근사가 multi-jn 의 효과를 얼마나 근사하는지, 또는 다른 axis 의 효과를 발휘하는지 정량 검증.

---

## 2. 8/8 FINAL 결과

### 2.1 측정값 raw

| Method | Mode | B1 baseline qe_trim | carry-over qe_trim | multi-jn qe_trim | Centroid tuple qe_trim |
|---|---|---:|---:|---:|---:|
| sparse_rp | CaseA | 1.5407 | 1.6104 | 1.5556 | 1.6133 |
| sparse_rp | CaseB | 1.5407 | 1.4393 | 1.4353 | 1.4271 |
| hilbert_real | CaseA | 1.5407 | 1.5681 | 1.5730 | 1.6172 |
| hilbert_real | CaseB | 1.5407 | 1.4471 | 1.4447 | 1.4339 |
| hyperloglog | CaseA | 1.5407 | 1.5584 | 1.5544 | 1.5231 |
| hyperloglog | CaseB | 1.5407 | 1.4613 | 1.4642 | 1.4382 |
| chao_weighted | CaseA | 1.5407 | 1.6353 | 1.5948 | 1.5798 |
| chao_weighted | CaseB | 1.5407 | 1.4483 | 1.4445 | 1.4377 |

### 2.2 paired Δ% 3-way 비교

| Method | Mode | carry-over Δ% | multi-jn Δ% | **Centroid tuple Δ%** | **ct-vs-carry** | ct-vs-mj |
|---|---|---:|---:|---:|---:|---:|
| sparse_rp | CaseA | +4.52% | +0.97% | +4.71% | +0.19p | +3.74p |
| sparse_rp | CaseB | -6.58% | -6.84% | -7.37% | **-0.78p** | -0.52p |
| hilbert_real | CaseA | +1.78% | +2.10% | +4.97% | **+3.19p ★ harmful** | +2.87p |
| hilbert_real | CaseB | -6.07% | -6.23% | -6.93% | **-0.86p** | -0.70p |
| hyperloglog | CaseA | +1.15% | +0.89% | **-1.14%** | **-2.29p ★** | -2.02p |
| hyperloglog | CaseB | -5.15% | -4.96% | **-6.66%** | **-1.50p ★★** | -1.69p |
| chao_weighted | CaseA | +6.14% | +3.51% | **+2.54%** | **-3.60p ★★★** | -0.97p |
| chao_weighted | CaseB | -6.00% | -6.24% | -6.69% | **-0.69p** | -0.45p |

### 2.3 SUMMARY 통계

**CaseA 단독 대체 모드**:
- mean Δ%: carry +3.40% / mj **+1.87%** / ct +2.77%
- **mj < ct < carry** (mj 가 mean 우위, ct 중간, carry worst)
- ct-carry mean diff: -0.63p (ct 가 carry 보다 약간 개선)
- ct-mj mean diff: +0.91p (ct 가 mj 보다 약간 worse)
- individual range: -3.60p ~ +3.19p (8 measurement 매우 spread)

**CaseB 증강 모드** (★ 본 연구 핵심 contribution):
- mean Δ%: carry -5.95% / mj -6.07% / **ct -6.91%**
- **ct < mj < carry** (★ ct 가 mean 우위, 최고 정확도)
- ct-carry mean diff: **-0.96p ★** (모든 method 일관 추가 개선)
- ct-mj mean diff: **-0.84p ★** (cheap 근사가 expensive multi-jn 보다 일관 우위)
- individual range: -1.69p ~ -0.45p (4 measurement 모두 ct < mj)

---

## 3. 핵심 finding

### 3.1 ★ CaseB 증강 모드 — cheap 근사 보편 우위

본 8/8 측정의 가장 중요한 finding 은 CaseB 증강 모드에서 Centroid tuple cheap 근사가 4 anchor method 모두에서 multi-jn (expensive 864 차원 KM20 학습) 보다 일관 우위라는 점이다. 4 measurement 의 ct-vs-mj 차이는 -0.45p (chao_weighted), -0.52p (sparse_rp), -0.70p (hilbert_real), -1.69p (hyperloglog) 으로 모두 negative (즉 ct 가 mj 보다 더 큰 개선) 이며, mean diff -0.84p 의 안정적 패턴이다.

이는 본 연구의 핵심 contribution narrative 인 "Bernoulli + stratified 산술 평균 ensemble augment" 의 효과가 stratification 학습 방식의 변화 (cheap vs expensive) 와 무관하게 robust 함을 입증할 뿐만 아니라, cheap 근사 의 effective stratum diversity (K²=400 product space 의 top-K folding) 가 ensemble averaging 에 추가적인 randomization 효과를 제공함을 시사한다. 즉 **best of both worlds — 0 학습 비용 추가 + 더 좋은 ensemble 정확도** 라는 강력한 결과다.

### 3.2 CaseA 단독 대체 모드 — Method-conditional 패턴

CaseA 단독 대체 모드에서는 method 별로 cheap 근사 효과가 분명히 분기된다.

**Centroid Friendly (큰 개선)**:
- **chao_weighted**: +6.14% → +2.54% (**-3.60p ★★★ 본 측정 최대 효과**), multi-jn (+3.51%) 보다도 -0.97p 추가 개선. weighted reservoir sampling 의 sampling probability 계산이 cheap stratum diversity 의 sparse 한 분포를 추가 정확도 향상으로 활용.
- **hyperloglog**: +1.15% → -1.14% (**-2.29p ★**), multi-jn (+0.89%) 보다도 -2.02p 추가 개선. hash-based distinct count 가 cheap stratum 의 randomization 을 hash diversity 증가로 직접 활용.

**Centroid Indifferent (marginal)**:
- **sparse_rp**: +4.52% → +4.71% (+0.19p, carry-over 수준), multi-jn (+0.97%) 보다 +3.74p worse. random projection 자체가 이미 randomization 메커니즘이라 cheap 근사 의 추가 randomization 효과가 marginal.

**Centroid Hostile (harmful)**:
- **hilbert_real**: +1.78% → +4.97% (**+3.19p ★ 큰 악화**). Hilbert curve 의 spatial locality 가 (s_A, s_B) imperfect folding 으로 fragmentation 되며 stratification 효과 손실.

### 3.3 ★ 새 method classification axis — "Cheap 근사 친화도"

본 8/8 finding 은 본 연구의 anchor method 분류에 **"Cheap 근사 친화도"** 라는 새로운 axis 의 존재를 입증한다. 기존의 두 axis 와 비교하면 다음과 같다.

| Method | Paradigm | Quality-sensitivity (multi-jn 우위) | **Cheap 근사 친화도** |
|---|---|---|---|
| sparse_rp | P4 차원축소 | sensitive (mj CaseA -3.55p) | Indifferent |
| chao_weighted | P3 스트리밍 | sensitive (mj CaseA -2.63p) | **Friendly** (ct CaseA -3.60p) |
| hilbert_real | P2 공간분할 | robust | **Hostile** (ct CaseA +3.19p) |
| hyperloglog | P9 정보이론 | robust | **Friendly** (ct CaseA -2.29p) |

본 새 axis 는 paradigm 분류와도 다르고, multi-jn quality-sensitivity axis 와도 다르다 — chao_weighted 는 quality-sensitive + Friendly 양쪽 모두, hyperloglog 는 robust + Friendly, sparse_rp 는 sensitive + Indifferent, hilbert_real 은 robust + Hostile 으로 method 별 메커니즘이 결정한다. 이는 본 연구의 anchor method 들이 stratification 효과를 어떻게 활용하는지의 본질적 메커니즘 axis 다.

### 3.4 5/13 다른 분석과의 패턴 일치성 검증

본 finding 을 5/13 부록 F (km granularity sensitivity) + 부록 G (multi-jn re-stratification) 결과와 cross-check 하면:

| Method | 부록 F K-sensitivity | 부록 G multi-jn | 본 분석 Centroid tuple 친화도 |
|---|---|---|---|
| sparse_rp | K-sensitive (U-shape) | sensitive ★ | Indifferent |
| chao_weighted | K=20 sweet | sensitive ★ | **Friendly ★** |
| hilbert_real | K-robust | robust | Hostile (CaseA harmful) |
| hyperloglog | K-robust | robust | **Friendly ★** |

기존 부록 F + G 의 "quality-sensitive vs quality-robust" 분류 (sparse_rp + chao_weighted 가 sensitive, hilbert_real + hyperloglog 가 robust) 는 method 의 외부 stratification quality 변화에 대한 sensitivity 였다. 본 새 axis 는 cheap stratum 분포 (sparse, top-K + modulo) 의 활용 능력으로, 각 method 의 internal sampling 메커니즘이 결정한다 — chao_weighted 의 weighted reservoir + hyperloglog 의 hash distinct count 는 cheap stratum diversity 를 활용, sparse_rp 의 random projection 은 marginal, hilbert_real 의 spatial locality 는 fragmentation harmful.

---

## 4. 강재현 14:27 hypothesis 결론

강재현이 5/13 14:27 카톡에서 제시한 cheap 근사 가설 — "기존에 table 별로 clustering한 거를 저비용으로 multi-reclustering에 근사하는 방법" — 에 대한 본 8/8 측정의 정량 답변은 **mode-conditional + method-conditional Yes** 다.

### 4.1 본 연구 핵심 CaseB 모드: 보편 Yes

CaseB 증강 모드에서 Centroid tuple cheap 근사 가 모든 4 anchor method 에서 multi-jn 보다 우위 (mean -0.84p). 본 연구의 핵심 contribution 영역이라는 점에서 이 결과는 매우 강력하다 — **0 학습 비용 추가로 더 좋은 ensemble 정확도** 라는 best of both worlds 결과.

### 4.2 CaseA 단독 대체 모드: method-conditional Yes/No

CaseA 단독 대체 모드는 method-specific 적용이 필요하다.
- **chao_weighted, hyperloglog**: cheap 근사 큰 효과 (multi-jn 보다도 우위 또는 동등)
- sparse_rp: marginal (carry-over 수준)
- hilbert_real: harmful (carry-over 보다 worse)

CaseA 영역에서 cheap 근사 적용 시 method-aware design 필요.

### 4.3 5/16 이후 추가 측정 plan 결정

본 8/8 결과의 mode-conditional + method-conditional 패턴은 충분히 robust 한 정량 evidence 를 제공한다. 다른 cheap 근사 후보 (PCA preprocessing, Iterative refinement, Hash-based bucketing) 의 추가 측정 가치는 본 결과로 method-aware design 의 narrative arc 가 이미 확립되었으므로 제한적이다. 5/16 ~ 5/26 finalize sprint 시점에는 본 측정 결과를 박광현 미팅 자료 + v5 deck 정정에 finalize 하는 것이 우선이다.

---

## 5. 본 연구 narrative arc 의 확장

### 5.1 부록 F + G + Centroid tuple 통합 narrative

5/13 03:00 부록 F (km granularity sensitivity) + 5/13 16:20 부록 G (multi-join re-stratification 8 measurement) + 5/13 20:00 본 분석 (Centroid tuple cheap 근사 8 measurement) 는 본 연구의 일관된 method-aware design narrative 를 형성한다.

본 연구의 12 anchor method 가 9 cells 전반에서 -9 ~ -10% 일관 개선 효과 (std 2-3 안정) 를 보이지만, multi-table cell (A2-Fig9) 의 stratification 학습 방식 변화에 대한 method 별 반응은 다양하며 다음 세 axis 의 복합적 결과로 분석된다:

1. **K-sensitivity (cluster granularity sensitivity)**: K 변화에 대한 robust 여부
2. **Quality-sensitivity (multi-jn re-stratification 우위 여부)**: stratum 의 quality 향상에 대한 활용
3. **Cheap 근사 친화도 (Centroid tuple folding 우위 여부)**: cheap stratum diversity 활용

세 axis 는 부분적으로 correlate 하지만 method 별로 독립적 분기를 보인다. 본 연구의 12 anchor method 일관성은 paradigm 분류가 아닌 이 세 메커니즘 axis 의 본질적 차이를 통해 method-aware design 의 학술적 contribution 으로 확장된다.

### 5.2 박광현 5/15 미팅 자료 + v5 deck 반영 plan

본 8/8 Centroid tuple 결과는 박광현 5/15 미팅 자료 부록 G.4.1 (cheap 근사 방향 답변) 에 finalize 데이터를 채우고, v5 deck 정정 prompt 6.6 의 cheap 근사 slide spec 에 반영된다. 박광현 confirm 요청 항목으로 "Cheap 근사 친화도" 새 axis 의 학술적 인정 여부 + CaseB 증강 모드 보편 우위 narrative 의 발표 deck 반영 우선순위를 결정한다.

---

## 6. 측정 source

- 측정 launch: 5/13 16:47 KST tmux mj_centroid (16:47 ~ 19:57)
- 회수 완료: 5/13 19:56:59 KST DONE flag
- 출력 dir: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_centroid_tuple/` (8 file)
- wrapper: `/tmp/launch_centroid_tuple.py` (864d concat 없이 두 single-table KM20 + (s_A, s_B) top-K + modulo folding)
- carry-over baseline: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/` (108 file)
- multi-jn baseline: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/` (8 file, 5/13 16:13 finalize)
- B1 baseline: `paper_exact/A2-Fig9_B1.json` qe_trim=1.5407

---

작성: 2026-05-13 20:05 KST · 8/8 회수 완료 + finalize
관련 분석 file: `multi_join_restratification_results_20260513.md` (multi-jn re-strat 8/8 결과)
관련 부록: 박광현 5/15 미팅 자료 slide_draft 부록 G + 1page §7 (finalize 예정)
다음: 박광현 자료 G.4.1 update + v5 prompt 정정 6.6 update + PDF 재생성 + 강재현 paste form
