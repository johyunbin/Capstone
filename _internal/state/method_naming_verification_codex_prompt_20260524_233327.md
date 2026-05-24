# Codex (xhigh) 적대 검증 prompt — 16 method 명칭·알고리즘·paradigm 정합성

> 작성: 2026-05-24 23:33 KST · target: GPT-5.5 xhigh effort
> 검증 결과 critical: 5/27 발표·6/11 보고서·채림님 자료 학술 정직성

## 0. 임무

당신은 **method 명칭·실제 알고리즘 코드·reference·paradigm 분류 의 정합성을 0 환각 0 오차로 적대 검증하는 평가자**다. 본 연구 16 method 중 명칭과 실제 구현이 어긋난 항목을 모두 발견하고 정정 권고를 한다. 학술 사기 (fraud) 위험·misleading naming·simplification 미명시 등을 priority 분류한다.

## 1. Context

연세대 캡스톤 "속도는벡터" 의 1,508 cell RQ3 측정에 사용한 16 method 의 명칭 정직성을 검증한다. METHOD_REGISTRY.md 의 audit (5/10) carry, 두 method 의 issue 가 이미 발견됨:
- `hilbert_real` (이전 `hilbert`) — METHOD_REGISTRY 권고: PCA 2D + lex sort alias → rename `pca2d_lex`. 다만 **현재 구현 (method_hilbert_real.py)** = PCA 2D + Wikipedia xy2d Hilbert curve — 진짜 Hilbert curve 알고리즘이지만 high-D 환원 X
- `sparse_rp` — Achlioptas 2003 표명 → 실제 Li-Hastie-Church 2006 (reference only 정정)

추가 검증 필요 — Claude 자체 audit 결과 11 method 의 명칭·알고리즘·reference 부분 불일치 발견:

## 2. 16 method 정본 carry

### Group A — 명칭·알고리즘 완전 일치 (5)
1. **chao_weighted** (M1): u^(1/w) priority sampling + quantile bin. Ref: Chao 1982 JRSS 69:653.
2. **cum_sqrtf** (M3): PCA 1D + histogram + cum-√f boundary. Ref: Dalenius-Hodges 1959 JASA 54:88.
3. **idistance** (M5): KMeans + d-from-centroid scalar + quantile. Ref: Jagadish 2005 TODS 30:364.
4. **ica_fastica** (M8): FastICA(n=1) + quantile. Ref: Hyvärinen 1999 IEEE NN 10:626.
5. **rsvd**: TruncatedSVD(n=2) + 2D quantile. Ref: Halko-Martinsson-Tropp 2011 SIAM Review.

### Group B — 부분 불일치 (11 의심 항목, code 직접 read 후 정정 권고)

| # | 명칭 | 실제 구현 (verbatim code 요약) | 표명 reference | 의심 |
|:--:|---|---|---|---|
| 6 | **hilbert_real** | PCA 2D 환원 후 Wikipedia xy2d Hilbert curve algorithm + quantile bin | Faloutsos 1989 SIGMOD | "real" 표명 misleading — high-D Hilbert X (PCA 2D 환원) |
| 7 | **skilling_hilbert** (M7) | PCA(4) 환원 후 Skilling Hilbert (4-axis × 8-bit) | Skilling AIP 2004 707:381 | "true high-D" 표명 — 실제 PCA(4) 환원 simplification |
| 8 | **zorder_morton** (M6) | PCA(2) + Morton bit-interleave + quantile | Morton IBM 1966 | PCA 환원 명시 X (Morton 자체는 정확) |
| 9 | **lpm1_proper** (M2) | KMeans + BallTree subsample 50K + Grafström pivot **approximation** | Grafström 2012 Biometrics 68:514 | "proper" 표명 — 실제 approximation |
| 10 | **lavallee_hidiroglou** (M4) | PCA 1D + take-all + cum-√f (**Neyman σ_h 적용 X**) | Lavallée-Hidiroglou 1988 Survey Method 14:33 | Neyman allocation 적용 X — partial |
| 11 | **kmeans_neyman** (M9) | KMeans cluster id만 return (σ_h 계산하지만 boundary 적용 X) | Cochran 1977 §5 + Neyman 1934 JRSS | "neyman" 명칭 — 실제 cluster id only |
| 12 | **rabitq_strat** (M10) | center + QR orthonormalize + sign bits (**1-bit code 부분만**) | Gao-Lin VLDB 2024 17:3252 | full RaBitQ X — 1-bit code partition only |
| 13 | **idistance_neyman** (M11) | iDistance + σ_h Neyman approximation re-bin | Jagadish 2005 + Neyman 1934 | Neyman approximation 명시 |
| 14 | **mhist2** | PCA(2) + 2D **equi-depth** grid (k×k bin) | Poosala-Ioannidis 1997 VLDB | MHIST-2 의 MaxDiff 가 아닌 equi-depth (simplification) |
| 15 | **kde_parzen** | **PCA 1D** 환원 + 1D KDE Silverman bandwidth + density quantile | Parzen 1962 Annals | high-D KDE 회피 위해 PCA 1D 환원 — 명시 필요 |
| 16 | **hyperloglog** | int8 quantize + md5 hash + leading p bits (**HLL cardinality estimator 부분 X, hash partitioning only**) | Flajolet-Fusy-Gandouet-Meunier 2007 AofA | HLL 의 핵심 (cardinality estimator) 적용 X — naming misleading |
| (carry) | **wavelet_hist** | PCA 1D + Haar wavelet on density profile + boundary | Matias-Vitter-Wang 1998 SIGMOD | partial Matias 구현 (density profile 만) |
| (carry) | **dbscan** | subset DBSCAN + centroid + nearest 할당 | Ester-Kriegel-Sander-Xu 1996 KDD | subset training simplification |

### 외부 file method (4)
- pca1d (Pearson 1901), gmm (Dempster-Laird-Rubin 1977 EM), minibatch_partial (Sculley 2010 WWW), faiss_ivf (Johnson-Douze-Jégou 2017)
- sparse_rp: Li-Hastie-Church 2006 정정 carry (reference only, code 정확)

## 3. 검증 임무

다음 5 task 에 priority 0 (학술 fraud risk) · 1 (major misleading) · 2 (minor simplification) 분류 + evidence + 정정 권고:

### Task A — 명칭 정합성 (16 method 전수)
각 method 의 명칭이 실제 알고리즘과 부합하는가? "real"·"proper"·"neyman"·"hyperloglog" 같은 표명이 실제로 그 알고리즘을 구현했는가?

### Task B — Reference 정합성
표명된 paper 가 본 알고리즘의 정본 출처인가? 또는 다른 paper 가 더 정확한가? simplification·approximation 시 명시 필요?

### Task C — Paradigm 분류 정합
현재 7 paradigm 분류:
- P1 Cluster: gmm·minibatch·minibatch_partial·dbscan·birch·agglomerative·coreset·kmeans_neyman M9 (8)
- P2 Spatial: hilbert_real·skilling_hilbert M7·zorder_morton M6·idistance M5·idistance_neyman M11·faiss_ivf·lpm1_proper M2·epsilon_net (8)
- P3 Streaming: chao_weighted M1 (1)
- P4 DimReduction: sparse_rp·random_projection·pca1d·rsvd·ica_fastica M8 (5)
- P5 QMC: lsh·sobol·halton·hammersley·lhs·cum_sqrtf M3·lavallee_hidiroglou M4 (7)
- P6 Quantization: rabitq_strat M10·mhist2·wavelet_hist (3)
- P9 InfoTheoretic: hyperloglog (1)
- P10 Density: kde_parzen (1)

질문:
1. **PCA 환원 후 다른 알고리즘 적용 method (hilbert_real·skilling_hilbert·zorder_morton·mhist2·rsvd·kde_parzen·wavelet_hist·cum_sqrtf·lavallee_hidiroglou·ica_fastica)** 는 **주된 알고리즘 paradigm** vs **DimReduction P4** 어디로 분류하는 게 맞는가?
2. **kmeans_neyman (M9)** 는 Neyman 미적용 — P1 Cluster + RQ2 Neyman 분류 맞는가, 단순 P1 Cluster 로 reclass?
3. **hyperloglog** 는 cardinality estimator 적용 X — P9 InfoTheoretic 명칭 맞는가, P5 Hashing 또는 새 paradigm?
4. **rabitq_strat** 는 1-bit code partition only — P6 Quantization 맞는가, P5 Hashing?
5. **idistance_neyman, lavallee_hidiroglou** 의 Neyman approximation/미적용 — paradigm 영향?

### Task D — 정정 권고
각 의심 항목에 대해:
- **(a) rename only** (code 변경 X, 명칭만): "real" 제거 → 정확한 명칭
- **(b) reference 정정**: paper 변경 또는 추가 (예: hilbert_real → Faloutsos 1989 + Wikipedia xy2d)
- **(c) docstring 명시**: "simplification·approximation 사용" 명시
- **(d) paradigm 재분류**: 다른 P 로 이동
- **(e) 폐기**: 사용 X 권고

### Task E — 영향 분석 (storyline·보고서·자료 B)
정정 시 다음 자료들에 어떤 영향?
1. storyline v3 (slide 7·8 의 paradigm 분류 + method 아이콘)
2. 보고서 6/11 (§3.6 paradigm 분류 표 + §4.4 method 별 정본 ranking)
3. 채림님 전달용 자료 (method 명칭·reference·paradigm 정확성 critical)
4. METHOD_REGISTRY.md (정본 carry)

## 4. 응답 형식

```
# 검증 결과 (Codex axis — method 명칭 정직성)

## Summary
- 명칭 정합성 점수 (0-100):
- algorithm 정합 점수 (0-100):
- paradigm 분류 정합 점수 (0-100):
- 종합 신뢰도 (0-100):
- pass / conditional pass / fail:
- Priority 0 (fraud risk): N건
- Priority 1 (major misleading): N건
- Priority 2 (minor simplification): N건

## Priority 0 발견 사항
1. [발견]
   - Evidence (code line·verbatim quote):
   - 현재 명칭:
   - 권고 정정:
   - storyline·보고서·자료 영향:

## Priority 1 / Priority 2 동일

## Task A-E 세부 판정

## 정정 항목 final list (rename·reference·docstring·paradigm)

## 종합 권고
```

언어: 한국어 (수치·통계·algorithm 용어는 영문/숫자 그대로).
응답 길이: 자세히 (2000-4000 자), 발견된 모든 명칭·algorithm·paradigm 정합성 issue 명시. 점수는 16 method 전수 평균 기준.
