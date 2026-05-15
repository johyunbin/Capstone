# narrative v5 outline — 박세은 5/15 20:49 정리 + 박광현 5/15 미팅 input 종합

작성: 2026-05-15 20:55 KST · v4 commit ad8bc43 base + 박세은 5/15 20:49 정리본 + 박광현 5/15 미팅 input

박세은 정리 3 axis:
1. **분포 안다/모른다 binary 구분 폐기** — 우리 method (클러스터링 등) 자체가 분포 파악 도구
2. **데이터셋 진입 시 빠르게 분포 catch + 대응** — 우리 RQ3 method 들 활용
3. **분포 분류 2-3 type + 분류별 적합 method 매핑** — 데이터셋 특성별 분류 기준 정의

박세은 + 박광현 input 종합 매핑:
| input | v5 axis |
|---|---|
| 박세은 1 binary 폐기 + 박광현 2 결과 기반 재설정 | §0 main theme + §1 출발점 |
| 박세은 2 빠른 catch + 박광현 3 분포 catch speed | §2 분포 catch speed (fit_time) |
| 박세은 3 분류 + 박광현 1 분포별 sampling | §3 데이터셋 특성별 3 type + 분류별 적합 method |
| 박광현 6 plan robustness | §5 plan robustness across variability |

박광현 4 (엔진 통합) + 5 (adversarial) = narrative 전체 제거 (측정 evidence X, 사용자 5/15 16:45 지시 align).

---

## v5 본문 8 section + 부록 §A

### §0 main theme
"Measurement-driven Distribution-aware Cardinality Estimation for VAQ" (v3/v4 유지)

핵심 reframing (박세은 정리 #1 반영):
- paper §V-B 의 "분포 모름 → Bernoulli random" framing 폐기
- 우리 method (클러스터링 등) 자체가 분포 파악 도구
- binary "분포 안다/모른다" 구분 의미 없음
- 새 axis = **데이터셋 진입 → 빠른 분포 catch → 데이터셋 특성별 적합 sampling 매칭**

### §1 출발점 + 측정 portfolio
- paper §V-B 가 "분포 모름" 가정으로 Bernoulli 만 — 분포 파악 불가능
- 본 연구의 axis: 우리 method 자체가 분포 파악. **데이터셋 진입 시 어떻게 빨리 파악하고 적합한 sampling 매칭하는가**
- 측정 portfolio: 9 cell × 56 method × 2 mode × 10 trial = 1352 file
- 8 paradigm rollup + 40 method 폐기

### §2 분포 catch speed (★ 박세은 정리 #2 + 박광현 input 3)
- 5/15 fit_time 직접 측정 90 file (Pareto Top 5 × 9 cell × 2 mode)
- sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× range**
- cache_time mean ≈ 10s (vector dim 의존, method 무관)
- reservoir O(1) 메모리
- 결론: catch 속도가 11.9× 차이 — 데이터셋 진입 시 method 선택 직접 axis

### §3 데이터셋 특성별 분류 4 type + 적합 method (★ 박세은 정리 #3 + 박광현 input 1)

**분류 기준 = 데이터 크기 (scale) × 테이블 구조 + dimension**:

| Type | 정의 | 1352 file cell | 적합 method (CaseB best) | fit_time |
|---|---|---|---|---:|
| **Type 1** | small single (sf=1, 0.1M rows, 저차원) | A5-scale-sf1 = 1 cell | **chao_weighted K=20 −14.11%** (★ 최강) / sparse_rp K=20 −11.70% | 3.67s ~ 9.40s |
| **Type 2** | medium single (sf=10, 1M rows, 저차원) | A5-scale-sf10 = 1 cell | (sweet spot 약함, chao_weighted K=20 −6.00%) | 3.67s ~ 9.40s |
| **Type 3** | large single (sf=100, 10M rows, 저-중차원 96~256d) | A1-DEEP / A1-SIFT / A1-SSN / A4-sel / A5-scale-sf100 = 5 cells | chao_weighted / sparse_rp (K=20 sweet) / neuram | 3.67s ~ 19.97s |
| **Type 4** | large multi-table (sf=100, 10M rows, 중-고차원 288d/864d) | A2-Fig7 (DEEP+YFCC 288d) + A2-Fig9 (DEEP+WIKI 864d) = 2 cells | hilbert_real K=30 (Type 4a 288d) / **Centroid tuple −7.37%** (Type 4b 864d, 학습 비용 0) | 43.50s |

4 type 별 적합 method 매핑 + **dynamic method selection** = 본 §3 의 핵심 finding. 데이터셋 진입 시 Type 판별 → Type 별 권장 method 적용.

핵심 finding (sf axis): **sf=10 영역 분포 인지 효과 약화 (paper §VI-B "shifting workloads" align)** — 데이터 크기 sweet spot 가 있다는 evidence.

추가 evidence: K granularity SF axis (A5-scale × K=10/30 × 4 anchor × 2 mode = 48 file) 에서 method-dependent K best 패턴 (sparse_rp/chao_weighted K=20 sweet vs hilbert_real/hyperloglog K=30 slight edge) — Type 1/3 의 K 권장 patterns.

### §4 정확도 evidence — paired 92.5%
- paired CaseB < CaseA = 92.5% (455/492, p<1e-45)
- Cliff's δ large = 63%, Hedges' g large = 56%
- 단독 best minibatch_partial −10.17% / 결합 best Centroid tuple −7.37%
- α sweep evidence: α=0.5 산술 평균 best
- method base (4 component 통합)

### §5 plan robustness across environment variability (★ 박광현 input 6)
- 9 측정 환경 variability 영역 결합 모드 안정성 92.5%
- 단독 negative control = large worsening 37.1%
- Neyman selectivity-dependent paradox (sel=0.01 vs sel=0.10) — 환경 variability 영역 plan 변동 evidence

### §6 Pareto frontier
- 정확도 + 자원 동시 best 영역 동일 method 군 (Pareto Top 5)
- §2 fit_time + §4 paired accuracy 통합

### §7 권장 설계 — Dynamic method selection by dataset Type
**Type 판별 후 동적 method 선택 (박세은 #3 + 박광현 input 1 직접 반영)**:
- Type 1 (small single sf=1): **chao_weighted K=20** (−14.11% 최강)
- Type 2 (medium single sf=10): chao_weighted K=20 (sweet spot 약함 −6.00%, 데이터 크기 sweet spot 검토 필요)
- Type 3 (large single sf=100 저-중차원): chao_weighted / sparse_rp K=20
- Type 4a (large multi-table 288d): hilbert_real K=30
- Type 4b (large multi-table 864d): **Centroid tuple** (학습 비용 추가 0, −7.37%)

**Dynamic method selection flow**:
1. 데이터셋 진입 → scale (rows) 파악 + structure (single/multi) + dimension 파악
2. Type 판별 (4 type 中 결정)
3. Type 별 권장 method 적용

**axis 별 권장 (v4 carry-over, Type 별 권장에 보조)**:
- 단독 대체 우선 (정확도 best)
- 결합 보조 (plan robustness)
- 자원 우선 (reservoir O(1))

### §8 결론
- 핵심 finding 5:
  1. 분포 catch speed 11.9× (fit_time evidence)
  2. 데이터셋 3 type 별 적합 method 매핑 (Type 1 chao_weighted / Type 2 hilbert_real / Type 3 Centroid tuple)
  3. 정확도 paired 92.5%
  4. plan robustness across 9 환경 + selectivity paradox
  5. Pareto frontier (정확도 + 자원 동시 best)
- paper §V-B Eq 1-6 + hyperparam 7종 verbatim 100% 정합

### 부록 §A 정정 룰 7 (v3/v4 유지)

---

## v4 → v5 변경 매트릭스

| v4 section | v5 변경 |
|---|---|
| §0 main theme | reframing — paper §V-B "분포 모름" binary 폐기 (박세은 #1) |
| §1 문제 + portfolio | 박세은 정리 "우리 method 자체가 분포 파악 도구" wording 추가 |
| §2 분포 catch speed | 유지 (fit_time 11.9×) |
| §3 분포 유형별 method 적합성 | **본격 재구성** — 데이터셋 특성별 3 type + Type 별 적합 method 매핑 (박세은 #3) |
| §4 정확도 evidence | 유지 |
| §5 plan robustness | 유지 |
| §6 Pareto frontier | 유지 |
| §7 권장 설계 | **Type 별 권장 추가** (박세은 #3) + axis 별 권장 carry-over |
| §8 결론 | finding 4 → finding 5 (Type 별 매핑 추가) |
| 부록 §A | 유지 |

---

다음 단계: 사용자 outline 확인 → §0-§8 본문 + 부록 §A 작성 → commit + push
