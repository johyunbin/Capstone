# 속도는벡터 — 5/8 회의 PPT outline (W4 sprint)

> **목적**: 5/8 19:00 비대면 회의용 PPT 슬라이드 outline. W4 sprint (5/7 단일 측정일) 결과 종합 + 자문 메일 초안 합의.
> **추후 변환**: 본 markdown → PowerPoint (.pptx) 또는 Keynote.
> **핵심 narrative**: motivation → 매트릭스 → RQ1 → RQ2 → RQ3 (25 method tier elimination, 4강 winner) → multi-relation → YFCC 분포 검증 → limitation → future work (sf100 plan) → 자문 메일 초안.
> **일관성**: master_v6_draft.md 와 동일한 contribution / limitation 사용. [TBD measured] placeholder 그대로 유지.

---

## Slide 1 — 표지

**제목**: 속도는벡터 — W4 Sprint 결과 종합 (5/8 회의 자료)

**핵심 message**:
- 캡스톤 디자인 2026-1, 연세대 (박세은·강재현·조현빈·이동욱)
- Exqutor 본 논문 ECQO 보완 — 단일 테이블 비인덱스 + 분포 인지 sampling

**시각**:
- [그림: 팀 로고 / 학교 로고]
- 발표일자: 2026-05-08 (W4 sprint final)

**Speaker note**:
- 본 자료는 5/7 단일 측정일 W4 sprint 결과 종합 + 5/27 최종 발표 narrative 의 위치 정렬용.
- sf100 (80M) 은 회의 후 자문 합의 후 진행.

---

## Slide 2 — Motivation: Exqutor + 본 연구 위치

**제목**: 본 연구의 위치 — Exqutor 가 미해결한 영역

**핵심 message**:
- Exqutor (BDAI-Research, arXiv:2512.09695v2) = ECQO (HNSW range query + multi-table) + Adaptive Sampling (단일 테이블 비인덱스)
- 본 연구 = Adaptive Sampling 의 *전 단계* sample 분배 전략 (proportional vs Neyman vs distribution-aware) 의 가치 정량

**시각**:
- [그림: Exqutor 매트릭스 4분면 (인덱스 ✓/✗ × multi-table ✓/✗) + 본 연구 영역 highlight]
- [표: Exqutor 본 논문 매트릭스 vs 본 연구 매트릭스 비교]

**Speaker note**:
- Exqutor 본 논문에서 단일 테이블 비인덱스 영역 (Adaptive Sampling) 은 momentum 기반 sample size 조정 1.2~3.2× speedup 만 보고. 분포 인지 sampling 의 가치는 비교 없음.
- 본 연구는 이 영역의 분포 인지 stratification (KM20 oracle) 가치 정량 + production-ready 대안 (4강 method) 도출.

---

## Slide 3 — W4 Sprint 매트릭스 — 15 cell

**제목**: W4 Sprint 측정 매트릭스 — 12 단일 + 3 multi = 15 cell

**핵심 message**:
- 5 dataset (DEEP/SIFT/SSN++/YFCC/WIKI) × sf1 (800K) + sf10 (8M) = 10 단일 cell
- YFCC_DL (build_yfcc 자체 추출, 분포 정합성 비교용) × sf1/sf10 = 2 cell
- Multi-vector (deep_sift_10, deep_wiki_10) + Multi-table join (deep_10 ⨝ part_wiki_10) = 3 cell

**시각**:
- [표: 매트릭스 표 (5 dataset × sf1/sf10 + YFCC_DL ×2 + multi ×3)]

  | Dataset | dim | sf1 (800K) | sf10 (8M) |
  |---------|----:|:---------:|:---------:|
  | DEEP    | 96  | [TBD] | [TBD] |
  | SIFT    | 128 | [TBD] | [TBD] |
  | SSN++   | 256 | [TBD] | [TBD] |
  | WIKI    | 768 | [TBD] | [TBD] |
  | YFCC    | 192 | [TBD] | [TBD] |
  | YFCC_DL | 192 | [TBD] | [TBD] (분포 정합성 비교) |

  Multi: partsupp_deep_sift_10, partsupp_deep_wiki_10, partsupp_deep_10 ⨝ part_wiki_10

- [그림: chain_unified.py 파이프라인 architecture (CELLS dict → 25 method dispatch)]

**Speaker note**:
- 모든 적재본 `partsupp_<DS>_<sf>` 일관 패턴.
- 25 method = 16 base + 9 NEW9 (NEW8 + spectral) per cell.
- sf100 (80M) 은 회의 후 자문 합의 후 별도 측정.

---

## Slide 4 — RQ1: Selectivity Gradient 단조성 (5×2 cell)

**제목**: RQ1 — BERN sampling 의 selectivity gradient 단조성

**핵심 message**:
- BERN sampling 의 부정확성은 selectivity 작을수록 단조 증가 (per-seed Spearman ρ)
- 5 dataset × sf1/sf10 = 10 cell 부호 일관성 입증

**시각**:
- [그림: per-seed Spearman ρ + bootstrap 95% CI (5 dataset × sf1/sf10 forest plot)]
- [표: 단조성 결과]

  | Dataset | sf1 ρ | sf10 ρ | 부호 일관 |
  |---------|------:|------:|:---------:|
  | DEEP    | [TBD] | [TBD] | [TBD] |
  | SIFT    | [TBD] | [TBD] | [TBD] |
  | SSN++   | [TBD] | [TBD] | [TBD] |
  | WIKI    | [TBD] | [TBD] | [TBD] |
  | YFCC    | [TBD] | [TBD] | [TBD] |

**Speaker note**:
- 측정 환경: numpy estimator (Phase 7 simulation, 빠른 반복).
- 5/5 dataset 부호 일관 시 → "BERN 부정확성 단조성" 5 dataset 일반화 입증.
- 부호 일관성 4/5 면 honest 별도 보고.

---

## Slide 5 — RQ2: KM20 oracle + Anti-Neyman + K-aware

**제목**: RQ2 — KM20 oracle stratification 의 가치 + σ_i 신호 약함

**핵심 message**:
- KM20 oracle 은 sample size 100/385/1000/3000 모두에서 BERN 보다 우수 ([TBD] 10 cell 일관)
- σ_i Neyman 신호 약함, Anti-Neyman 은 좁은 sel 에서 systematic hurt (paired Wilcoxon)
- K-aware: K_optimal per dataset (저차원 K=20 / 고차원 더 큰 K)

**시각**:
- [그림: KM20 vs BERN paired difference (sample size × dataset heatmap)]
- [표: Anti-Neyman hurt cell (s=0.01 부호)]

  | Dataset | sf10 s=0.01 Anti-Neyman effect |
  |---------|------:|
  | DEEP    | +5.21% (W2 확정) |
  | SIFT    | +9.49% (W2 확정) |
  | SSN++   | [TBD] |
  | WIKI    | [TBD] |
  | YFCC    | [TBD] |

- [그림: K-sweep K∈{10,20,50,100,200} K_optimal per dataset]

**Speaker note**:
- W2 확정 (DEEP/SIFT) + W4 확장 (SSN++/WIKI/YFCC).
- σ_i 신호 약함 honest 입증 — Anti-Neyman vs Proportional Wilcoxon p>0.5, Cohen's d<0.1.
- K=20 default 의 generalization 정도 입증.

---

## Slide 6 — RQ3: 25 method tier 1-4 elimination

**제목**: RQ3 — 25 method tier elimination → 4-6 winner

**핵심 message**:
- 25 method = 16 base + 9 NEW9 (DBSCAN/OPTICS/Agglomerative/Hierarchical KMeans/Faiss IVF/PCA-KMeans/KMeans++/Coresets + Spectral)
- Tier 1 (통계 robust ≥5/10 cell) → Tier 2 (production cost ≤ KM20) → Tier 3 (sf1↔sf10 부호 일관) → Tier 4 (5 dataset robust)
- 최종 winner 4-6 method

**시각**:
- [그림: Tier elimination flow (25 → 12 → 8 → 4-6 → 4 winner)]
- [표: tier 통과 method]

  | Tier | 통과 method (예상) |
  |------|-------------------|
  | Tier 1 | KM20, MiniBatch, MiniBatch_partial, Hilbert, Z-order, Hybrid, HDBSCAN, KDtree, PCA1D, BIRCH, Faiss IVF, Hierarchical KMeans (~10-12) |
  | Tier 2 | MiniBatch_partial, Hilbert, Z-order, Hybrid, HDBSCAN, KDtree, PCA1D, BIRCH (~6-8) |
  | Tier 3 | MiniBatch_partial, Hilbert, Hybrid, HDBSCAN (~4) |
  | **Tier 4** | **MiniBatch_partial, Hilbert, Hybrid, HDBSCAN** (4 final winner 가설) |

**Speaker note**:
- Tier 1 criteria: |CI_lower| > 0 AND CI_upper < 0 in ≥5/10 cell.
- Tier 2 criteria: 학습시간 < 5분 + memory < 10 GB + deterministic.
- Tier 3 criteria: sf1↔sf10 부호 일관성 ≥ 80%.
- Tier 4 criteria: 5 dataset 모두 improve sign.
- W3 시사된 4강 (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 의 5 dataset 일반화 검증이 W4 핵심.

---

## Slide 7 — 4강 method 5 cell 일관성 heatmap

**제목**: 4강 method (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 의 5 dataset × sf1/sf10 일관성

**핵심 message**:
- 4강 method 가 5 dataset × sf1/sf10 = 10 cell 모두에서 improve direction 인지 정량 검증
- paired bootstrap CI 0 제외 cell 수 [TBD measured]

**시각**:
- [그림: 4강 method × 10 cell heatmap (효과 크기 색)]

  ```
  ┌─────────────────┬────────┬────────┬────────┬────────┬────────┐
  │                 │ DEEP   │ SIFT   │ SSN++  │ WIKI   │ YFCC   │
  ├─────────────────┼────────┼────────┼────────┼────────┼────────┤
  │ Hilbert sf1     │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ Hilbert sf10    │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ MiniBatch_p sf1 │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ MiniBatch_p sf10│ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ Hybrid sf1      │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ Hybrid sf10     │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ HDBSCAN sf1     │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  │ HDBSCAN sf10    │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │ [TBD]  │
  └─────────────────┴────────┴────────┴────────┴────────┴────────┘
  ```

- [표: 4강 method 의 production 특성]

  | Method | 학습 시간 | Deterministic | Online OK | 차원 robust |
  |--------|----------:|:-------------:|:---------:|:-----------:|
  | Hilbert | learning-free | ✓ | ✓ | ✓ |
  | MiniBatch_partial | < 1 min | ✓ (seed) | ✓ | ✓ |
  | Hybrid | ~2 min | ✓ | partial | ✓ |
  | HDBSCAN | ~5 min | ✓ | ✗ | partial |

**Speaker note**:
- Hilbert: learning-free + 결정론 + competitive recovery (W3 5/5 dataset CI 0 제외).
- MiniBatch_partial: production-ready OLTP, ARI 1.000 vs batch.
- Hybrid: KMeans + Hilbert 결합.
- HDBSCAN: density-based skew 가치 (SIFT mid-sel −4.82~−8.55%).

---

## Slide 8 — K-aware (K_optimal per dataset × scale)

**제목**: K-aware baseline — K_optimal per dataset

**핵심 message**:
- K∈{10, 20, 50, 100, 200} sweep 으로 dataset 별 K_optimal 도출
- K=20 default 의 generalization 정도 정량

**시각**:
- [그림: K_optimal heatmap (5 dataset × sf1/sf10)]
- [표: K_optimal per dataset]

  | Dataset | dim | sf1 K_optimal | sf10 K_optimal | K=20 격차 |
  |---------|----:|--------------:|---------------:|----------:|
  | DEEP    | 96  | [TBD] | [TBD] | [TBD] |
  | SIFT    | 128 | [TBD] | [TBD] | [TBD] |
  | SSN++   | 256 | [TBD] | [TBD] | [TBD] |
  | WIKI    | 768 | [TBD] | [TBD] | [TBD] |
  | YFCC    | 192 | [TBD] | [TBD] | [TBD] |
  | YFCC_DL | 192 | [TBD] | [TBD] | [TBD] |

**Speaker note**:
- 저차원 (DEEP/SIFT/YFCC) → K=20 부근.
- 고차원 (SSN++/WIKI) → K=50 또는 K=100 가능.
- K=20 default 의 robustness 정량 입증.

---

## Slide 9 — Multi-vector ablation

**제목**: Multi-vector — partsupp_deep_sift_10, partsupp_deep_wiki_10

**핵심 message**:
- 한 행 두 임베딩 (DEEP+SIFT, DEEP+WIKI) 환경에서 4강 method 일반화 검증
- Exqutor 본 논문의 multi-vector query 영역과 직접 매칭

**시각**:
- [그림: multi-vector cell 의 4강 method recovery rate]
- [표: multi-vector 결과]

  | Cell | KM20 | Hilbert | MiniBatch_p | Hybrid | HDBSCAN |
  |------|-----:|--------:|------------:|-------:|--------:|
  | partsupp_deep_sift_10 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
  | partsupp_deep_wiki_10 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

**Speaker note**:
- DEEP (96d) + SIFT (128d) = 224d concat 또는 separate column.
- DEEP (96d) + WIKI (768d) = 864d 격차 dim 시나리오.
- 4강 method 의 multi-vector 일관성이 핵심.

---

## Slide 10 — Multi-table natural join

**제목**: Multi-table natural join — partsupp_deep_10 ⨝ part_wiki_10

**핵심 message**:
- TPC-H natural join 두 dataset 매칭 → Exqutor 본 논문 multi-table query 영역 직접 매칭
- 단일 → multi-table generalization 의 *필요조건* 만 입증

**시각**:
- [그림: join 시나리오 — partsupp (deep 96d) ⨝ part (wiki 768d)]
- [표: join cell 의 4강 method 결과]

  | Cell | KM20 | Hilbert | MiniBatch_p | Hybrid | HDBSCAN |
  |------|-----:|--------:|------------:|-------:|--------:|
  | partsupp_deep_10 ⨝ part_wiki_10 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

**Speaker note**:
- TPC-H natural join: partsupp 와 part 의 자연 외래키 (ps_partkey = p_partkey).
- 두 dataset 의 다른 dim (96 vs 768) 환경에서 4강 method 일반화 검증.
- 단일 정확성이 multi 의 *필요조건* — multi 정확성의 *충분조건* 까지 일반화는 future work.

---

## Slide 11 — YFCC 분포 정합성 검증 (build_yfcc 비교)

**제목**: YFCC vs YFCC_DL — PCA basis 일치 검증

**핵심 message**:
- 채림 적재본 (partsupp_yfcc_*) vs 본 연구 자체 추출 (build_yfcc.py → partsupp_yfcc_dl_*)
- PCA basis 일치 + distribution shape 일관성 정량 (KS test / energy distance / PCA correlation)

**시각**:
- [그림: PCA component-wise correlation (192 components)]
- [그림: distribution histogram comparison]
- [표: 분포 정합성 metric]

  | Metric | sf1 | sf10 |
  |--------|----:|-----:|
  | PCA correlation (192 comp avg) | [TBD] | [TBD] |
  | KS test p-value | [TBD] | [TBD] |
  | Energy distance | [TBD] | [TBD] |
  | 4강 method recovery 일치도 | [TBD] | [TBD] |

**Speaker note**:
- 채림 석사 적재본은 1280d CLIP embedding → PCA 192d, 본 연구도 동일 PCA target dim.
- PCA fit 은 다른 sample 으로 학습됨 → component-wise correlation 으로 basis 일치 검증.
- 일치하지 않을 시 honest 별도 보고 + 차후 분석.

---

## Slide 12 — Honest limitations (6-8종)

**제목**: Honest limitations — W4 sprint 단일 측정일 기준

**핵심 message**:
- 본 연구의 한계 6-8종 정직 reporting

**시각**:
- [표: limitation 6-8종 + 대응]

  | # | Limitation | 대응 / future work |
  |---|------------|--------|
  | 1 | 단일 → multi-table generalization | W4 partsupp_deep_sift / partsupp_deep_10⨝part_wiki_10 부분 입증 |
  | 2 | NPY-only mode 의 RQ2 dependency | partsupp_<DS>_<sf> NPY 추출본 의존, 적재본 부재 시 RQ2 skip |
  | 3 | YFCC PCA basis 검증 caveat | YFCC vs YFCC_DL 분포 정합성 정량 별도 보고 |
  | 4 | σ_i 신호 약함 | Anti-Neyman vs Proportional Wilcoxon p>0.5, d<0.1 |
  | 5 | IS NaN sel=0.01 발산 | 분할 X + weight only invalid → negative control narrative |
  | 6 | K-sweep upper bound K=200 | K>200 영역 미측정, 차후 extend |
  | 7 | sf100 (80M) deferred | 5/8 회의 후 자문 합의 후 5/27 발표 직전 측정 |
  | 8 | Effect size dataset 별 격차 | DEEP small / SIFT large / WIKI/YFCC/SSN++ [TBD] 별도 보고 |

**Speaker note**:
- 모든 한계는 future work 으로 link.
- σ_i 신호 약함 + IS NaN 은 negative control narrative 으로 활용.

---

## Slide 13 — Future work + sf100 plan

**제목**: Future work — sf100 plan + Exqutor multi-table 영역 + Distribution shift

**핵심 message**:
- sf100 (80M) 은 5/8 회의 후 자문 합의 후 진행 (W4 의 future scope)
- Exqutor multi-table 영역 일반화, vector.c integration, K>200 sweep, distribution shift detection

**시각**:
- [표: future work + 일정]

  | Future work | ETA | 대응 |
  |-------------|-----|------|
  | sf100 (80M) 5 dataset 측정 | ~5/22 | 5/8 자문 회신 후 launch |
  | Exqutor multi-table 영역 일반화 | 차후 학기 | 본 연구 multi-relation 부분 입증 |
  | vector.c C-level integration | 차후 학기 | Phase 6 SQL D 영역 |
  | K>200 K-sweep | 차후 | WIKI/SSN++ 고차원 영역 |
  | Distribution shift detection | 차후 | online detection mechanism |
  | DuckDB native fixed-rate baselines | 차후 | Exqutor pgvector 33% / VBASE 50% / DuckDB 100% 직접 통합 |

- [그림: 5/8 회의 → 자문 회신 → sf100 측정 → 5/27 발표 timeline]

**Speaker note**:
- sf100 measurement estimated time: 5 dataset × ~2-4 hour = ~10-20 hour overnight chain.
- 자문 회신 후 chain_unified.py extension 으로 launch.

---

## Slide 14 — 5/27 발표 narrative 흐름

**제목**: 5/27 최종 발표 narrative — W4 결과 + sf100

**핵심 message**:
- 5/27 발표 = W4 (12 단일 + 3 multi) + sf100 (5 cell) = 20 cell narrative

**시각**:
- [그림: 5/27 발표 슬라이드 구조 (12 슬라이드)]

  ```
  Slide 1 — 표지 (속도는벡터)
  Slide 2 — Motivation (Exqutor + 본 연구 위치)
  Slide 3 — W4 매트릭스 + sf100 (15 + 5 = 20 cell)
  Slide 4 — RQ1 (5 dataset × 2~3 scale selectivity gradient)
  Slide 5 — RQ2 (KM20 + K-aware + Anti-Neyman)
  Slide 6 — RQ3 25 method tier elimination → 4-6 winner
  Slide 7 — 4강 method 일관성 heatmap
  Slide 8 — Multi-vector + Multi-table direct comparison
  Slide 9 — YFCC 분포 정합성 (build_yfcc 비교)
  Slide 10 — Honest limitation
  Slide 11 — Future work
  Slide 12 — Q&A
  ```

**Speaker note**:
- 5/8 회의에서 narrative 흐름 합의.
- sf100 결과 추가 시 cross-scale validation 완성.

---

## Slide 15 — 자문 메일 초안 (채림 + 지도교수)

**제목**: 자문 메일 초안 — 채림 석사 + 지도교수

**핵심 message**:
- 채림 석사: YFCC 분포 정합성 + multi-table 영역 일반화 자문
- 지도교수: sf100 (80M) plan + W4 narrative 검토

**시각**:
- [표: 자문 메일 핵심 질문]

  | 대상 | 핵심 질문 |
  |------|----------|
  | 채림 석사 | (1) YFCC PCA fit 의 sample 의존성 + distribution shape 검증 방법 (2) multi-table natural join 영역의 sampling rate dependency |
  | 지도교수 | (1) sf100 (80M) 5 dataset 측정의 시간 자원 합의 (2) W4 narrative (4강 method + 25 method tier elimination) 의 발표 정합성 |

- [표: 자문 발송 일정]

  | 일정 | 행동 |
  |------|------|
  | 5/8 19:00~20:30 | 회의에서 자문 메일 초안 합의 |
  | 5/9 ~ 5/12 | 자문 메일 발송 (채림 + 지도교수) |
  | ~5/15 | 자문 회신 ETA |
  | 5/15 이후 | sf100 측정 launch |
  | 5/22 | 교수님 미팅 (자문 결과 + sf100 진행 상황) |
  | 5/27 | 최종 발표 |

**Speaker note**:
- 자문 메일 초안 v3 (`속도는벡터_자문메일초안_v3_supplement_20260507.md`) 참조.
- 회의에서 메일 본문 + 첨부 자료 합의.

---

## (Appendix) 측정 운영 + 자료 location

**활성 tmux 세션 (5/7 22:00 시점)**:
- chain_DEEP_sf1, chain_DEEP_sf10, chain_SIFT_sf1, chain_SIFT_sf10
- chain_SSN_sf1, chain_SSN_sf10, chain_WIKI_sf1, chain_WIKI_sf10
- chain_YFCC_sf1, chain_YFCC_sf10, chain_YFCC_DL_sf1, chain_YFCC_DL_sf10
- multi_vec, multi_join

**자동화 인프라**:
- `_internal/scripts/prepare_cell.py` — CELLS dict dispatch
- `_internal/scripts/chain_unified.py` — 25 method dispatcher
- `_internal/scripts/build_wiki.py`, `build_yfcc.py` — raw → partsupp 추출
- `_internal/scripts/measure_multi_vector.py`, `measure_multi_table_join.py` — multi 측정 runner

**산출 path**:
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` — W4 narrative master
- `experiments/results/rq3_agnostic/rq3_<cell>_<method>.parquet` — 12 단일 + 3 multi × 25 method ~375 parquet
- `experiments/results/rq2_aware/k_sweep_<cell>.parquet` — K-sweep 12 cell × 5 K
- `experiments/results/cross_source/yfcc_vs_yfcc_dl_distribution.csv` — YFCC 분포 정합성
- `experiments/figures/W4_matrix/`, `k_sweep/`, `method_tier/`, `multi_relation/`, `cross_source/`

---

**최초 작성**: 조현빈 · 2026-05-07 22:00 KST
**작성 모델**: Claude Opus 4.7 1M, 통합 manager session
**선행 doc**: `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` (W4 narrative master) + `_internal/handoff_v6_session_20260507_1822.md` (5/7 18:22 인계)
**측정 완료 후 갱신**: 5/8 새벽 (sf1+sf10 측정 완료) → [TBD measured] 정량 채움 → 5/8 19:00 회의 직전 final.
