# 엔진 적용 검증 — latency 측정 데이터

> 속도는벡터 캡스톤 · 엔진 적용 검증 실험(`measure_latency_realengine.py`)의 측정 raw + 통계 집계.
> 실험 전체 설명·재현 절차는 **`submission/_drafts/속도는벡터_엔진적용검증_실험정리_20260522_173533.md`** 참조.
>
> 한 줄 요약: Exqutor-패치 PostgreSQL(55435)에 카디널리티 추정값을 4 조건(baseline/B1/oracle/CaseB)으로 주입해 측정한 end-to-end latency + 실행 계획. sf=10 · DEEP/SIFT/SSN/YFCC.

---

## 1. 디렉토리 구조

| 디렉토리 | 내용 | 상태 |
|---|---|---|
| `phase2/` | DEEP sf=10 sel=0.001 — 12 cell (정본 핵심) | 정본 |
| `phase3/` | DEEP sf=10 sel=0.01·0.1 carry-over — 8 cell | 정본 |
| `phase4_extension/` | SIFT·SSN·YFCC sf=10 — 36 cell + 추정치 parquet + figures | 정본 |
| `poc_6_4_extended/` | 3 평면(phase2+3+4) 통합 통계 집계 — `summary.md` + CSV 9종 | **정본 수치** |
| `phase4_extension_*_backup/` | 측정 방식 변형(2stage·seq·4par) 백업 — 분석 미사용 | 보조 |
| `phase4_prescan/` · `prescan/` · `prescan_sanity/` | 본 측정 전 사전 점검(측정 시간·주입 발동 확인) | 보조 |
| `poc_6_4/` · `poc_6_4_extended_2stage_backup/` | 이전 시점 집계 | 보조 |

DEEP sf=10 정본 평면 = `phase2` + `phase3` = 20 cell. 확장 평면 = `phase4_extension` = 측정 36 cell(SIFT/SSN/YFCC 각 12). 단 **SSN·YFCC q12는 주입 미발동(`injection_fired=false`)으로 분석(paired)에선 제외** → 분석 대상 = SIFT 12 + SSN 9 + YFCC 9 = 30 cell (메인 문서 §3.4). WIKI sf=10은 statement_timeout으로 미측정(관측된 예외).

---

## 2. latency 측정 JSON

### 2.1 명명 규칙

```
latency_tpc_h_<query>_<dataset>_sf<sf>_sel<sel>_qid<qid>.json
예: latency_tpc_h_q3_SIFT_sf10_sel0.1_qid0.json
```

파일 하나 = cell 하나 = 16 variant × (1 warmup + 15 timed) rep 측정 결과.

### 2.2 JSON 스키마

```jsonc
{
  "family": "tpc_h",
  "query": "q3",                   // TPC-H 쿼리 (q3/q9/q10/q12)
  "dataset": "SIFT", "sf": 10, "sel": 0.1, "query_id": 0,
  "D": 0.86,                       // 벡터 술어 거리 임계값
  "true_card": 800000.0,           // 참 카디널리티
  "vec_table": "partsupp_sift_10", // 측정 대상 벡터 테이블
  "n_warmup": 1, "n_timed": 15,
  "statement_timeout": "180s",
  "variants": [                    // 16개 — baseline·B1·oracle + CaseB 13 method
    {
      "condition": "CaseB",        // baseline / B1 / oracle / CaseB
      "method": "chao_weighted",   // CaseB만 method명, 그 외 null
      "injected_card": 815000.0,   // 주입한 카디널리티 (baseline은 null)
      "q_error": 1.019,            // max(injected/true, true/injected)
      "exec_ms": [1500.2, ...],    // timed rep별 end-to-end 실행시간(ms)
      "n_timeout": 0,              // statement_timeout 도달 횟수(검열)
      "exec_ms_trimmed": 1498.7,   // 양끝 1개 제거 평균
      "exec_ms_median": 1499.1,
      "exec_ms_iqr": [1490.0, 1510.0],
      "plan_json": { ... },        // pass-2 실행 계획 (auto_explain JSON)
      "plan_duration_ms": 1502.3,
      "injection_fired": true,     // Exqutor 주입 발동 검증 플래그
      "injected_card_seen": 815000.0  // Exqutor 로그에서 읽은 카디널리티
    }
    // ...
  ],
  "kst": "2026-05-22 14:08:03"
}
```

핵심 컬럼: `exec_ms`(실행 시간 분포)·`plan_json`(실행 계획)·`injection_fired`(주입 발동 여부 — false면 그 variant는 짝지은 비교에서 제외).

---

## 3. `poc_6_4_extended/` — 통계 집계 (정본 수치)

`stats_poc_6_4_extended.py`가 3 평면 raw를 통합 분석한 산출. **본 연구 sf=10 결과 수치의 정본.**

| 파일 | 내용 |
|---|---|
| `summary.md` | 전체 요약 — sanity 체크 + 표 8개 |
| `plane_comparison.csv` | 평면(phase2/3/4)별 정답 계획 회복률·효과크기 |
| `dataset_comparison.csv` | 데이터셋(DEEP/SIFT/SSN/YFCC)별 회복률·\|g\| |
| `sf_scaling.csv` | sf별 condition 효과 |
| `plan_level_effect_size.csv` | 계획 회복 여부별 효과크기 분층 |
| `cluster_bootstrap.csv` | cell 단위 cluster paired bootstrap 95% CI |
| `variance_decomp.csv` · `_model1.csv` · `_no_baseline.csv` | 변동 분해 (3 모델) |

★ `variance_decomp_no_baseline.csv`의 `C(cond_str)` 행 `pct_ss ≈ 0.00%`·`p_typ3 = 0.945` = "어느 추정을 주입하든 실행 시간 동등"의 핵심 근거.
★ `variance_decomp_model1.csv`의 `p_typ3` 열은 36-cell 포화모델 statsmodels 엣지케이스로 degenerate(uniform 0.927) — **인용 금지** (보고서는 model3 사용).

---

## 4. 분석 파이프라인

```
측정 raw JSON  ─(analyze_latency.py)→  phase4_extension/figures/paired_stats.csv
                                              │
              phase2·phase3 figures/paired_stats.csv (carry)
                                              │
                                       (stats_poc_6_4_extended.py)
                                              ↓
                              poc_6_4_extended/  (summary.md + CSV 9종)
```

- `analyze_latency.py --input phase4_extension` — cell별 paired Wilcoxon·Holm·Hedges' g 산출 → `figures/paired_stats.csv`.
- `stats_poc_6_4_extended.py` — phase2+3(carry) + phase4_extension paired_stats 통합 → 평면·데이터셋·sf 비교 + 변동 분해.

스크립트 위치: `_internal/scripts/`.

---

작성: 2026-05-22 · 속도는벡터.
