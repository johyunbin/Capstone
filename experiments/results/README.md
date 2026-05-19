# experiments/results/ — 측정 데이터 사전 (외부 공개용)

> **속도는벡터** (연세대 캡스톤) — Exqutor 논문 §V-B Adaptive Sampling 재현 + 분포 인지
> stratification ensemble 의 정량적 가치 검증. 본 폴더는 그 **모든 측정 결과**를 외부인
> (지도교수 · 멘토 · 발표 청중) 이 별도 설명 없이 읽을 수 있도록 정리한 것이다.
>
> 재정리 일자 2026-05-17 · 총 측정 1932 file (raw 691 + server 1241) → 본 트랙 1474 + archive 360 + 중복 사본 54 제외

---

## 1. 변인 (variable) 정의

이 실험은 "단일 테이블에서 인덱스 없이 벡터 쿼리의 카디널리티를 추정할 때, 무작위
표본(Bernoulli) 대신 분포를 인지한 층화(stratified) 표본을 결합하면 추정이 얼마나
정확해지는가" 를 측정한다. 각 측정 file 은 다음 변인의 한 조합이다.

| 변인 | 값 | 의미 |
|---|---|---|
| **dataset** | DEEP(96d) · SIFT(128d) · SSN(256d) · YFCC(192d) · WIKI · DEEP+WIKI · DEEP+SIFT · DEEP+YFCC | 임베딩 데이터셋. 괄호는 벡터 차원 |
| **sf** (scale factor) | 1 · 10 · 100 | 테이블 크기 배율 (sf=100 ≈ 본 논문 기본 규모) |
| **sel** (selectivity) | 0.001 · 0.01 · 0.10 | 쿼리 필터 선택도. 본실험 기본 = 0.01 |
| **mode** | B1 · CaseA · CaseB | 측정 방식 (아래 상세) |
| **single / multi** | single · multi(concat) | 단일 벡터 컬럼 vs 다중 벡터 결합(concatenation) |
| **K** | 10 · 20 · 30 | 층화 클러스터 개수 (KMeans K). 기본 = 20 |
| **method** | 16종 (4절) | 결합에 쓰는 분포 인지 추정기 |

### mode 3종 (가장 중요)

- **B1** — paper §V-B 의 Bernoulli Adaptive Sampling 그대로. 모멘텀 기반 동적 표본
  (Eq 1~6, N=385). **본 연구의 baseline.**
- **CaseB** — `est_final = (est_B1 + est_method) / 2` 산술 평균. paper Bernoulli 추정값과
  우리 method 의 KM20 stratified 추정값을 결합. **본 연구의 핵심 측정.**
- **CaseA** — paper Bernoulli 를 우리 method 로 *단독 대체*. negative control
  (결합이 아닌 대체는 효과 없음을 보이는 대조군). → `archive/미사용method_측정/` 에 보존.

> CaseB 가 B1 보다 q-error 가 낮으면 "결합이 추정을 개선했다" 는 뜻이다.

---

## 2. cell 코드 → 의미명 매핑표

원본 측정 file 은 `A1-DEEP`, `A2-Fig9` 같은 **cell 코드**로 식별되었다 (paper figure 와
1:1 대응). 본 정리에서는 이를 사람이 읽을 수 있는 `{데이터셋}_{sf}` 의미명으로 바꿨다.

| cell 코드 | 의미명 | paper 대응 | 비고 |
|---|---|---|---|
| A1-DEEP | `DEEP_sf100` | Fig 5/6/12 | DEEP 96d, sel=0.01 기준 |
| A1-SIFT | `SIFT_sf100` | Fig 5/6/12 | SIFT 128d |
| A1-SSN | `SSN_sf100` | Fig 5/6/12 | SimSearchNet++ 256d |
| A2-Fig7 | `YFCC_sf10` | Fig 7 | YFCC 192d |
| A2-Fig9 | `DEEP+WIKI_sf10` | Fig 9 | cross-table (다중 테이블 조인) |
| A4-sel | `DEEP_sf100_Fig13sel` | Fig 13 | **단일 sel cell — sel sweep 아님.** sel=0.001 한 점만 측정 |
| A5-scale-sf1 | `DEEP_sf1` | Fig 14 | scale axis |
| A5-scale-sf10 | `DEEP_sf10` | Fig 14 | scale axis |
| A5-scale-sf100 | `DEEP_sf100_scaleaxis` | Fig 14 | scale axis (A1-DEEP 과 별개 측정 run) |
| A5-scale-sf{1,10}-SIFT | `SIFT_sf{1,10}` | — | SIFT scale 확장 |
| A5-scale-sf{1,10}-SSN | `SSN_sf{1,10}` | — | SSN scale 확장 |
| A6-WIKI-sf{1,10} | `WIKI_sf{1,10}` | — | WIKI single |
| A7-YFCC-sf1 | `YFCC_sf1` | — | YFCC scale 확장 |
| A8-DEEP+SIFT-sf10 | `DEEP+SIFT_sf10` | — | 다중 벡터 (비-concat) |
| A9-DEEP+SIFT-concat-sf{1,10,100} | `DEEP+SIFT_concat_sf{...}` | — | 다중 벡터 concatenation |
| A10-DEEP+WIKI-concat-sf{1,10} | `DEEP+WIKI_concat_sf{...}` | — | 다중 벡터 concatenation |
| A11-DEEP+YFCC-concat-sf{1,10} | `DEEP+YFCC_concat_sf{...}` | — | 다중 벡터 concatenation |
| A2-Fig8 | (scope 외) | Fig 8 | paper §V-A multi-vector. 본 연구 §V-B 범위 외 |
| A3-TPCDS | (scope 외) | Fig 10/11 | paper §V-A ECQO. 본 연구 §V-B 범위 외 |

> **충돌 주의**: A1-DEEP · A4-sel · A5-scale-sf100 은 모두 "DEEP, sf=100" 이지만
> *서로 다른 측정 cell* (각각 Fig 5/6/12 · Fig 13 · Fig 14) 이다. 의미명에
> `_Fig13sel` · `_scaleaxis` suffix 를 붙여 구분했다.

---

## 3. 디렉토리 트리

```
experiments/results/
├── README.md                     ← 이 파일 (데이터 사전)
│
├── 01_baseline_paper재현/        paper §V-B Bernoulli (B1) cell별 baseline
├── 02_single_vector_본실험/      ★ CaseB 16-method, single 벡터, sel=0.01 (본 연구 핵심)
├── 03_selectivity_sweep/         sel 0.001 / 0.10 민감도 (16-method)
├── 04_multi_vector_concat/       다중 벡터 concatenation (224d/864d/288d, 16-method)
├── 05_K_granularity/             클러스터 수 K=10/20/30 민감도
├── 06_부가측정/                  alpha sweep · cheap approximation · multi-join 재학습
│
├── _summary/                     RQ1·RQ2 집계 CSV (분석 산출물)
├── analysis/                     정량 분석 보고서 (.md)
├── archive/                      구버전·범위 외·초기 sprint 측정
│   ├── 미사용method_측정/         16종 외 40 method + CaseA — 본 분석 제외, 보존
│   ├── scope외_측정/              DEEP+CC3M(Fig8) · TPCDS(Fig10/11) — 본 연구 범위 외
│   └── (W1~W4 초기 sprint · REPORT v11 등)
└── raw/                          ★ 원본 측정 (절대 미변경, 본 트랙은 이것의 복사본)
```

### 각 폴더 설명

| 폴더 | file 수 | 내용 |
|---|---:|---|
| `01_baseline_paper재현/` | 17 | cell 별 B1 (Bernoulli Adaptive Sampling). paper Fig 12 재현 anchor |
| `02_single_vector_본실험/` | 278 | **본 연구 핵심.** 단일 벡터 sel=0.01 에서 16 method × CaseB. q-error 비교의 main 측정 |
| `03_selectivity_sweep/` | 680 | sel 을 0.001 / 0.10 으로 바꿔 본 16-method 측정. 선택도 민감도 |
| `04_multi_vector_concat/` | 357 | 두 데이터셋 벡터를 이어붙인(concat) 다중 벡터 측정. 다중 테이블 일반화 |
| `05_K_granularity/` | 150 | 층화 클러스터 수 K 를 10/20/30 으로 바꾼 측정 |
| `06_부가측정/` | 36 | 결합 비율 α sweep(0.3~0.6) + 저비용 근사 4후보 + 다중 조인 재학습 |
| `_summary/` | 15 | RQ1(bernoulli vs km20) · RQ2(5-way allocation) 집계 CSV |
| `archive/미사용method_측정/` | 354 | 16종에 들지 않는 40 method 측정 + CaseA(단독 대체) 전량. **본 분석에는 쓰지 않으나 보존** |
| `archive/scope외_측정/` | 7 | A2-Fig8(DEEP+CC3M) 6 + TPCDS CSV 1. 본 논문 §V-A 영역이라 본 연구 §V-B 범위 밖 |

> 트랙 01~06 안에서 같은 cell 이 두 측정 캠페인에 모두 있으면
> `run-paper-exact/` (5월 paper-exact portfolio) 와 `run-v6-v10/` (확장 측정 v6~v10) 으로
> 하위 분리했다. 같은 cell 의 독립 재측정이라 평균 내지 말고 캠페인별로 본다.

---

## 4. 16 method 목록 + paradigm 분류

본 분석은 정합성을 통과한 **16 method** 만 사용한다 (paper N=385 budget 준수 +
측정 커버 완료). paradigm 은 추정 원리별 분류다.

| paradigm | method | 추정 원리 |
|---|---|---|
| **P1 Cluster** | `minibatch_partial`, `gmm` | 클러스터링 기반 층화 |
| **P2 Spatial** | `hilbert_real`, `skilling_hilbert`, `zorder_morton`, `faiss_ivf` | 공간 채움 곡선 · 공간 인덱스 |
| **P3 Streaming** | `chao_weighted` | 가중 스트리밍 표본 (Chao 1982) |
| **P4 DimReduction** | `sparse_rp`, `pca1d`, `rsvd`, `ica_fastica` | 차원 축소 후 층화 |
| **P5 QMC/Hashing** | `cum_sqrtf`, `lavallee_hidiroglou` | 최소분산 층화 (Dalenius-Hodges, Lavallée-Hidiroglou) |
| **P6 Quantization** | `rabitq_strat`, `mhist2` | 벡터 양자화 · 히스토그램 |
| **P9 InfoTheoretic** | `hyperloglog` | 카디널리티 스케치 (Flajolet 2007) |

> 16종 외 40 method (halton, sobol, dbscan, lsh, reservoir 등) 는 정합성 위반·중복·
> 측정 미커버 사유로 `archive/미사용method_측정/` 에 보존만 한다. 사유는
> `_internal/METHOD_REGISTRY.md` 참조.

---

## 5. 파일명 읽는 법

본 트랙의 측정 file 은 일관된 이름 규칙을 따른다.

```
{데이터셋}_{sf}_{mode}_{method}.json
```

| 예시 파일명 | 해석 |
|---|---|
| `SIFT_sf100_CaseB_gmm.json` | SIFT 데이터셋, sf=100, CaseB(결합), gmm method |
| `DEEP_sf1_B1.json` | DEEP, sf=1, B1 baseline (method 없음) |
| `DEEP+WIKI_concat_sf10_CaseB_sparse_rp.json` | DEEP+WIKI concat, sf=10, CaseB, sparse_rp |
| `SIFT_sf100_K30_CaseB_rsvd.json` | SIFT sf=100, K=30, CaseB, rsvd |
| `DEEP+WIKI_sf10_alpha0.5_CaseB_pca1d.json` | α=0.5 결합 비율 sweep |

상위 디렉토리 경로가 추가 변인을 담는다:
`03_selectivity_sweep/SIFT_sf100/sel0.001/CaseB/...` → sel=0.001.
`05_K_granularity/DEEP_sf100/K10/run-v6-v10/...` → K=10, v6-v10 측정 캠페인.

### JSON 내부 구조

```json
{
  "cell": "A1-SIFT", "dataset": "SIFT", "sf": 100,
  "mode": "CaseB", "method": "gmm", "selectivity": 0.01,
  "n_queries": 1000, "trials": 10,
  "avg_q_error_trimmed": 1.743,      ← 핵심 지표: 절사평균 q-error (낮을수록 정확)
  "final_size_mean": 597.4, "final_size_std": 127.4,
  "trial_results": [ ... 10 trial 상세 ... ],
  "kst": "17:37:22"
}
```

핵심 지표는 `avg_q_error_trimmed` — 추정 카디널리티와 실제값의 비율 오차를 10 trial
절사평균한 값. **1.0 에 가까울수록 정확**. CaseB 가 B1 보다 작으면 결합이 효과 있다는 뜻.

---

## 6. 재현 정보

- **측정 서버**: `165.132.140.240` (capstone2026), 작업 디렉토리
  `/mnt/hdd0/home/capstone2026`
- **측정 스크립트**: `_internal/scripts/measure_paper_exact.py`
- **paper §V-B Adaptive Sampling hyperparameter** (Exqutor Eq 1~6, 전 측정 공통):

  | 파라미터 | 값 | 의미 |
  |---|---|---|
  | N_init | 385 | 초기 표본 크기 (paper Eq 1) |
  | m | 0.9 | 모멘텀 계수 |
  | eta_0 | 0.1 | 초기 학습률 |
  | alpha | 50 | 적응 게인 |
  | beta | 1.5 | 적응 지수 |
  | gamma | 0.99 | 감쇠 계수 |
  | update_period | 50 | 갱신 주기 |

- **CaseB 결합식**: `est_final = (est_B1 + est_method) / 2.0` (단순 산술 평균).
  표본 budget 은 두 추정기가 공유 (paper Eq 1 의 N=385).
- **DB / 라이브러리**: PostgreSQL + pgvector, DuckDB / Python, NumPy, FAISS
- **분석 산출물**: `raw/REPORT_분석/REPORT_paper_exact_v13.md` (전체 측정 종합 REPORT),
  `analysis/` (정량 분석 보고서)

---

## 부록: 원본 → 정리 트랙 매핑

| 원본 소스 | 정리 후 위치 |
|---|---|
| `raw/Type*/...paper_main/CaseB/` (16 method) | `02_single_vector_본실험/.../run-paper-exact/` |
| `raw/Type*/...paper_main/CaseB/` (40 method) | `archive/미사용method_측정/02_single_vector_본실험/` |
| `raw/_shared_B1/` | `01_baseline_paper재현/.../run-paper-exact/` |
| `raw/.../K_granularity/K=*/` | `05_K_granularity/.../run-paper-exact/` |
| `raw/.../alpha_sweep/alpha_0.X/` | `06_부가측정/alpha_sweep/` |
| `raw/.../cheap_approximation/` | `06_부가측정/cheap_approximation/` |
| `server_sync/v9_sel_sweep_0530/` | `03_selectivity_sweep/` |
| `server_sync/concat_track_0537/` | `04_multi_vector_concat/` |
| `server_sync/{v6,v6v7,v7,v8,v10,g2}/` | `02_single_vector_본실험` 또는 `05_K_granularity` (`run-v6-v10/`) |
| `raw/.../RQ3_CaseB/`, `RQ1_baseline/` | paper_main 과 byte-identical 인 54건 제외 (5/15 reorg 사본). A2-Fig9 독립 측정 4건만 `02_.../run-rq3-detail/` 보존 |

> `raw/` 원본은 **절대 변경하지 않았다** — 본 트랙은 전부 복사본이다.
> 재정리는 `_internal/scripts/reorg_results_E7.py` 가 수행 (dry-run + 복사 모드).
