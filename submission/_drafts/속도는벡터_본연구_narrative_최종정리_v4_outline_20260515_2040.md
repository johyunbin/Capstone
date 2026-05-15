# narrative v4 outline — 박광현 5/15 input 영역 본문 axis 재구성

작성: 2026-05-15 20:40 KST · v3 commit 4879999 base · 박세은 + 임채림 정리본 도착 전 사용자 임시 진행분

v3 의 한계: main theme 만 변경, 본문 구조 (§4 4 component / §5 paper Eq 1-6 통합 / §6 paired / §7 Pareto / §10 권장) 는 여전히 paper §V-B Extending form 잔재.

v4 의 변경: 박광현 input 4 항목 (1 분포별 sampling / 2 결과 기반 / 3 분포 catch speed / 6 plan robustness) 을 본문 axis 6 개로 재구성. input 4 (엔진 통합) + 5 (adversarial) 은 측정 evidence 없어 narrative 전체 제거.

---

## v4 본문 구조 (8 section + 부록 §A)

### §0 main theme
- "Measurement-driven Distribution-aware Cardinality Estimation for VAQ" (v3 유지)
- paper §V-B base reference 로만 인용 (anchor X)
- 3 axis: measurement-driven / distribution-aware / VAQ

### §1 문제 + 측정 portfolio
- 박광현 input 2 align — paper §V-B 후속 X, 결과 기반 문제
- VAQ cardinality estimation 영역 데이터 분포가 plan 결정에 결정적
- paper Bernoulli 만으로 분포 catch 불가
- 측정 portfolio: 9 cell × 56 method × 2 mode = 1352 file
- 8 paradigm rollup axis

### §2 분포 catch speed (★ 박광현 input 3 align)
- 5/15 fit_time 90 file 직접 측정
- Pareto Top 5: sparse_rp 3.67s ~ hilbert_real 43.50s = 11.9× range
- cache_time mean ≈ 10s (vector dim 의존)
- reservoir 메모리 O(1)
- 결론: 분포를 catch 하는 method 의 speed 가 13× 차이 — 산업 환경 선택 axis

### §3 분포 유형별 method 적합성 (★ 박광현 input 1 align)
- 8 paradigm × 9 측정 환경 rollup
- paradigm 별 CaseB Δ% mean:
  - P10 Density -11.93% / P9 InfoTheoretic -7.60% / P3 Streaming -6.63% / P4 DimReduction -6.03% / P2 Spatial -5.57%
  - P5 QMC +1.47% (paradigm-level only) / P1 Cluster +2.04% / P6 Quantization +8.44%
- 분포 유형별 적합성 patterns: 5 paradigm CaseB 우위 vs 3 paradigm 약화

### §4 정확도 evidence — paired 92.5%
- 1001 file paper exact base + CaseA 단독 대체 + CaseB 결합 ensemble
- paired CaseB < CaseA = 92.5% (455/492, p<1e-45)
- Cliff's δ large = 63.0% / Hedges' g large = 55.7%
- 단독 best: minibatch_partial -10.17% (A2-Fig8)
- 결합 best: Centroid tuple -7.37% (A2-Fig9)
- α sweep evidence: α=0.5 산술 평균 best

### §5 plan robustness across environment variability (★ 박광현 input 6 align)
- 박광현 input 6: "순서 바뀌지 않을 정도 정의 어려움 (테이블 크기, 숫자 등 변수 많음)"
- 본 연구의 plan robustness 정의: 9 측정 환경 (dataset / sf / sel / dimension / multi-table) × 56 method 영역 paired CaseB < CaseA 안정성
- 결합 모드의 환경별 변동성 정량: paired 우위 92.5% × 9 환경 일관
- 단독 대체 (CaseA) negative control: large worsening 37.1% 발현 → 결합 모드 안전망

### §6 Pareto frontier — 정확도 + 자원 동시 best
- §2 fit_time + §4 paired evidence 통합
- Pareto Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert
- 정확도 best (단독 대체 안정 우위 15 method) 과 자원 효율 best (Pareto frontier) 가 동일 method 군
- 메모리 O(K × d) 이하 / reservoir O(1)

### §7 권장 설계 4 단계 (측정 evidence 기반)
- 7.1 단독 대체 우선 (Pareto Top 5 中 선택, 정확도 best -10.17%)
- 7.2 결합 보조 (CaseB 92.5% paired 우위, plan robustness)
- 7.3 자원 우선 (reservoir O(1), sparse_rp 3.67s)
- 7.4 다중 테이블 (Centroid tuple, 학습 비용 추가 0)

### §8 결론
- paper §V-B Adaptive Sampling base 환경 위에서 분포 인지 stratification 의 cardinality estimation 정량 가치를 1352 file 직접 측정으로 검증
- 핵심 finding 4: 분포 catch speed 11.9× / 분포별 method 적합성 / paired 92.5% / plan robustness across environment
- paper Eq 1-6 verbatim 100% 정합 + hyperparam 7종 paper verbatim

### 부록 §A 정정 룰 7
- A-1 paper §V-B algorithm pseudo-code 없음
- A-2 framework axis novelty 한정
- A-3 paper §V-B single-table = 구현 코드 한계
- A-4 paper §V-B sampling = block + row hybrid
- A-5 "분포 안다" L1/L2/L3 multi-layer
- A-6 paper §V-B = "without index" 가정
- A-7 "Anti-Neyman > Neyman" wording 정정 → selectivity-dependent

(v3 의 §8 K granularity + §9 Neyman selectivity-dependent 는 §3 분포 유형별 적합성 + §5 plan robustness 의 evidence sub-section 으로 통합)

---

## v3 → v4 변경 매트릭스

| v3 section | v4 변경 |
|---|---|
| §0 main theme | 유지 |
| §1 1352 file 3 finding | §1 문제 + portfolio 영역 통합 |
| §2 탐색 (8 paradigm 56 method) | §1 portfolio 영역 통합 |
| §3 폐기 40 method | §1 portfolio 영역 sub-section 통합 또는 부록 |
| §4 4 component | **§4 sub-section** 또는 부록 §F |
| §5 paper Eq 1-6 통합 | **§4 sub-section** 또는 부록 §F |
| §6 paired 92.5% | **§4 정확도 evidence** 로 이동 |
| §7 자원 효율 + fittime | **§2 분포 catch speed + §6 Pareto** 로 분리 |
| §8 K granularity | **§3 분포 유형별 적합성** sub-section |
| §9 Neyman selectivity | **§5 plan robustness** sub-section |
| §10 권장 설계 4 | **§7 권장 설계** 로 이동 |
| §11 결론 | **§8 결론** 으로 이동 |
| 부록 §A 정정 룰 7 | 유지 |

---

## 박광현 input 4 항목 → v4 axis 매핑

| input | v4 axis |
|---|---|
| 1. 분포별 sampling 적용 | §3 분포 유형별 method 적합성 |
| 2. 결과 기반 재설정 | §0 main theme + §1 문제 framing |
| 3. 분포 빠른 catch | §2 분포 catch speed (fit_time 11.9×) |
| 6. plan robustness | §5 plan robustness across variability |

input 4 (엔진 통합) + 5 (adversarial) 은 narrative 에서 완전 제거 (측정 evidence X).

---

다음 단계: 사용자 outline 확인 → §0-§8 본문 + 부록 §A 작성 → commit + push
