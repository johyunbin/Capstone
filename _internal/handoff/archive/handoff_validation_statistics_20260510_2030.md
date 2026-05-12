# Handoff — 통계/paired Δ%/narrative 정합성 검증 세션 (5/10 20:30 KST)

> 별도 세션 (메인 측정 세션과 분리). 메인 세션은 Phase B/C measurement 진행 중 — **읽기 전용 검증** 권장.
> 사용자: 조현빈 (Capstone, 5/10 외출 후 복귀, 전권 위임)

---

## 0. TL;DR — 검증 목표

**메인 세션이 paper exact (avg_qe 1.69 일치) 검증 + Phase B/C 측정 진행 중**. 본 세션은 **측정 결과 통계 + narrative 정합성 검증** 전담.

검증 4 layer:
1. **paired Δ% 계산 정확성** (CaseA vs B1, CaseB vs B1)
2. **Wilcoxon + BH-FDR 통계 검증** (multiple testing correction)
3. **5단계 narrative consistency** (RQ1/RQ2 ↔ paper sel 영역에서 narrative 성립)
4. **cherry-picking 회피 검증** (REPORT.md selective bias)

**메인 세션 변경 X — 읽기 전용**.

---

## 1. 메인 세션 진행 상태 (5/10 20:30 시점)

### 1.1 완료 ✅
- **Phase A B1**: 9/9 cells (avg_qe 1.541~1.708, paper Fig 12 reports 1.69 매우 근접)
- **Phase B CaseA Tier 1 Legacy**: 99/99 (11 methods × 9 cells)
- **Phase C CaseB Tier 1 Legacy**: 99/99
- **RQ1 paper exact**: DEEP/SIFT × Bernoulli/KM20 (5% 격차 narrative 검증)
- **RQ2 paper exact**: DEEP/SIFT × Bernoulli/Equal/Prop (9% 격차 narrative 검증)

### 1.2 진행 중 🔄
- **Phase B extra**: 8 NEW methods × 9 cells = 72 (pq/kdtree/halton/hammersley/coreset/birch/agglomerative/dense_rp)
- **Phase B extra2**: 20 NEW methods × 9 cells = 180 (Tier S+/A/B: opq/kdpp/banditucb1/neuram/thompson_sampling/mfmc/epsilon_net/ams_count_sketch/neurocard_lite/adaptive_bucket_probing/ccsketch/factor_join/lp_bound/cca1d/cocluster_nystrom/tucker/vinecopula/hkbu_repsample/lhs/lpm2)
- **Phase C extra**: 28 NEW methods × 9 cells = 252 (CaseB ensemble, Phase B 와 병렬 dispatch)
- **23 active procs** on server (CPU ~25 cores 사용, 자원 충분)

### 1.3 미완료 ⏳
- **A2-Fig8** (DEEP+WIKI partsupp 4-way multi-vector): partsupp_deep_wiki_10 stratum_id 컬럼 부재 + multi-vector AND predicate measurement loop 별도 implementation
- **A3-TPCDS** (Fig 10 ECQO mode): Exqutor patched PG의 ECQO trigger가 vector cast SQL과 충돌 → PG crash 반복 (autocommit + exqutor_qerror 테이블 생성 후도 fail)

### 1.4 핵심 결과 (Tier 1 Legacy 198 measurements)
| Method | B1 | CaseA Δ% | CaseB Δ% | 평가 |
|---|---|---|---|---|
| **minibatch_partial** | 2.090 | **-7.41%** | -2.11% | CaseA best single replace |
| **sparse_rp ★4** (paradigm anchor) | 2.090 | -0.98% | **-7.11%** | CaseB significant |
| minibatch | 2.090 | -2.40% | **-7.17%** | CaseB best |
| hilbert | 2.090 | -2.15% | -5.21% | CaseB |
| pca1d | 2.090 | -2.34% | -4.75% | CaseB |
| reservoir | 2.090 | -1.85% | -4.68% | CaseB |
| faiss_ivf / gmm | 2.090 | +5%/+15% | +1%/+5% | underperform |
| **lsh / random_projection / sobol** | 2.090 | **outliers** (YFCC 192d) | +35%/+1964%/+11% | YFCC 분포 부적합 |

**전체 narrative**:
- ✅ #2 paper 정확 재현 (paper Fig 12 1.69 -6.3%~+1.1% 일치)
- ⚠️ #3 CaseA 단독 대체: minibatch_partial -7.41% 만 강한 outperform, 다른 methods 약함
- ✅ #4 CaseB 증강 (B1 + method ensemble): 6 methods 모두 -2~-7% outperform
- ✅ #5 최종 비교: CaseB > CaseA > B1

---

## 2. 검증 task spec

### 2.1 Layer 1 — paired Δ% 계산 검증

**입력 데이터** (server 측):
```
/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/
├── A1-DEEP_B1.json        # B1 baseline (Phase A)
├── A1-SIFT_B1.json
├── A1-SSN_B1.json
├── A2-Fig7_B1.json
├── A2-Fig9_B1.json
├── A4-sel_B1.json
├── A5-scale-sf{1,10,100}_B1.json
├── *_CaseA_*.json         # Phase B (99 + 252 진행 중)
├── *_CaseB_*.json         # Phase C (99 + 252 진행 중)
├── rq1_paper_exact_DEEP_sf100.csv
├── rq1_paper_exact_SIFT_sf100.csv
├── rq2_paper_exact_DEEP_sf100.csv
├── rq2_paper_exact_SIFT_sf100.csv
└── REPORT_paper_exact.md  # 자동 생성 (analyze_paper_exact.py)
```

**JSON schema** (B1/CaseA/CaseB):
```json
{
  "cell": "A1-DEEP", "fig": "Fig 5/6", "dataset": "DEEP", "sf": 100,
  "mode": "B1" | "CaseA" | "CaseB",
  "method": "minibatch_partial",  # CaseA/CaseB only
  "ensemble_strategy": "simple_average",  # CaseB only
  "n_queries": 1000, "trials": 10,
  "avg_q_error_trimmed": 1.353,
  "final_size_mean": 1388, "final_size_std": 1438,
  "trial_results": [
    {"trial": 0, "avg_q_error_finite": 1.512, "n_finite": 985, "n_inf": 15,
     "final_size": 380, "final_eta": 0.082},
    ...
  ]
}
```

**검증 항목**:
1. paired Δ% 공식: `(CaseA - B1) / B1 × 100` per **(cell × method × trial)** 격자
2. trial pairing: B1 trial 0 ↔ CaseA trial 0 (동일 seed `trial_idx * 13 + 7`)
3. inf/nan handling: `avg_q_error_finite` 사용 (inf 제외 후 평균)
4. trim mean: lowest 1 + highest 1 제외 (paper p.7 verbatim, `TRIM=1`)
5. cell × method 순서 일관성 (sort key)

**산출**:
- `_internal/validation/paired_delta_audit.md` — paired Δ% 정확성 + 발견된 incorrect 사례

### 2.2 Layer 2 — Wilcoxon + BH-FDR 통계 검증

**현재 implementation**: `_internal/scripts/analyze_paper_exact.py` § `paired_delta()` + `bh_fdr()`

**검증 항목**:
1. **Wilcoxon signed-rank test**:
   - `scipy.stats.wilcoxon(b1, ca, alternative="two-sided")`
   - paired sample (B1 vs CaseA per trial) — 대응표본 가정 충족?
   - sample size n=10 trials — Wilcoxon 권장 n>=20, n=10은 power 낮음 (정확한 검정 vs 근사)
   - ties handling (Pratt vs Wilcoxon) — default behavior 검증
2. **BH-FDR multiple testing correction**:
   - n_finite p-values 사용
   - monotonic non-decreasing constraint (rank 역순 누적 min)
   - α=0.05 cutoff
3. **multiple comparison framework**:
   - cell × method = 9 × 11 = 99 comparisons (Tier 1)
   - 추가 cell × method = 9 × 28 = 252 (NEW methods, 진행 중)
   - 총 ~351 comparisons → BH-FDR n_finite는 충분

**산출**:
- `_internal/validation/wilcoxon_bh_fdr_audit.md`

### 2.3 Layer 3 — 5단계 narrative consistency 검증

**5단계 narrative** (사용자 명시 5/10 14:03):
1. RQ1/RQ2/RQ3 검증 (기존 결과 paper exact 재확인)
2. Exqutor 100% 정확 재현 (paper Fig 12 1.69 + Fig 6 358-415)
3. CaseA: 우리 method 대체 (sampling step replace)
4. CaseB: 우리 method 증강 (sampling step augment)
5. 최종 비교 B1 vs CaseA vs CaseB

**검증 항목**:
1. **#2 (paper 정확 재현)**: 9 cells avg_qe = paper Fig 12 1.69 ± **명시 tolerance** (현재 -6.3% ~ +1.1%)
   - tolerance 합리성 검증 (paper variance 추정)
2. **#3 (CaseA outperform)**: REPORT.md "minibatch_partial -7.41%" claim의 통계 유의성 (Wilcoxon p_adj < 0.05?)
3. **#4 (CaseB ensemble)**: "6 methods 모두 outperform" claim 일관성
4. **#5 (최종 비교)**: CaseB > CaseA > B1 ordering 통계 유의성
5. **RQ1**: paper sel{0.01, 0.10}에서 random vs KM20 5% 격차 (csv 검증)
6. **RQ2**: paper sel{0.01, 0.10}에서 Prop < Equal < Bernoulli ordering (csv 검증)
7. **YFCC 192d outliers** (lsh/RP/sobol): cell 일부에서 극단값 → narrative 영향 평가

**산출**:
- `_internal/validation/narrative_consistency_audit.md`
- 각 단계별 PASS / WARN / FAIL 판정

### 2.4 Layer 4 — cherry-picking 검증

**REPORT.md "Top 15 wins" / "Bottom 5 outliers" 표** 의 selection bias 검증:
1. 모든 (cell × method) 조합 분포 (histogram of Δ%)
2. Top/Bottom subset 통계 vs 전체 평균
3. **선별적 narrative 위험**: REPORT가 outlier (lsh/RP/sobol)를 강조하면서 우리 method 우위 claim?
   - 실제 narrative는 "outlier 명시 + 다른 cells는 정상" 형식
4. paper-exact 강조 영역에서 우리 결과가 paper보다 좋다는 claim의 정당성

**산출**:
- `_internal/validation/cherrypicking_audit.md`

---

## 3. 본 세션 작업 흐름

### Phase 1: 환경 setup
1. server SSH 접속 검증 (메인 세션 영향 X — read-only)
2. 입력 파일 list:
   ```bash
   ssh capstone2026@165.132.140.240 "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*.json | wc -l"
   ssh capstone2026@165.132.140.240 "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*.csv | wc -l"
   ```
3. server side 분석 script: `/mnt/hdd0/home/capstone2026/cache/rq3/analyze_paper_exact.py` (메인이 작성, 변경 X)

### Phase 2: 검증 코드 작성
**메인 세션 영역 X**:
- 새 분석 scripts: `_internal/validation/audit_*.py` (server 또는 local)
- 결과 md: `_internal/validation/*.md`

**기존 코드 변경 X**:
- ❌ `analyze_paper_exact.py` — 메인이 사용
- ❌ `measure_paper_exact.py` — 메인이 사용
- ❌ `_measure_common.py` — server-side 공통

### Phase 3: 검증 결과 작성
- 4 layer 각각 audit md
- 종합 보고서: `_internal/validation/SUMMARY_validation.md`
- PASS/WARN/FAIL count + recommendation

### Phase 4: handoff back to 메인 세션
- audit 결과를 메인 세션에 전달:
  - PASS: 그대로 narrative 강화
  - WARN: 메인이 재검토 (재측정 또는 narrative 조정)
  - FAIL: 메인이 즉시 fix

---

## 4. 메인 세션 침범 회피 룰

**❌ 절대 금지**:
- `cache/rq3/paper_exact/*.json` 또는 `*.csv` 변경 / 삭제
- `cache/rq3/measure_paper_exact.py` 또는 `analyze_paper_exact.py` 변경
- 메인 세션 tmux 세션 (paper_exact, phase_b_*, phase_c_*, pb_*, pc_*, pce_*, pbe_*, pbe2_*) kill
- 메인 진행 중 procs (`pgrep -af measure_paper`) 영향
- PostgreSQL 인스턴스 (port 55435) 영향
- NPY cache (`cache/rq1/*.npy`) 변경

**✅ 허용**:
- 메인 결과 read-only (json/csv/md)
- 별도 분석 scripts 작성 (`_internal/validation/audit_*.py`)
- 별도 audit md 작성 (`_internal/validation/*.md`)
- server side 별도 디렉토리 사용 (`cache/rq3/audit/`)
- SSH read-only 명령 (psql SELECT, file ls)

---

## 5. 산출 spec

### 5.1 audit 파일 list
```
_internal/validation/
├── audit_paired_delta.py         # Layer 1
├── audit_wilcoxon_bh_fdr.py      # Layer 2
├── audit_narrative_consistency.py # Layer 3
├── audit_cherrypicking.py        # Layer 4
├── paired_delta_audit.md
├── wilcoxon_bh_fdr_audit.md
├── narrative_consistency_audit.md
├── cherrypicking_audit.md
└── SUMMARY_validation.md         # 종합
```

### 5.2 SUMMARY_validation.md 형식
```markdown
# 검증 종합 (5/10 ~)

## Layer 1 — paired Δ% (PASS/WARN/FAIL count)
## Layer 2 — Wilcoxon + BH-FDR
## Layer 3 — 5단계 narrative consistency
## Layer 4 — cherry-picking

## 종합 판정
- PASS: ...
- WARN: ...
- FAIL: ... → 메인에 즉시 통지 권장

## Recommendation
- ...
```

---

## 6. SSH 접속 정보

**채림님 메일**:
- IP: 165.132.140.240
- 계정: capstone2026
- pwd: bdai1234! (SSH key 등록 시 password X)
- port: **55435** (PG 우리 인스턴스)
- 작업 dir: `/mnt/hdd0/home/capstone2026/`
- DB: wns41559 (TPC-H), tpcds (TPC-DS)
- sudo X, GPU 사용 자제 (다른 사용자 작업 中 X 시 활용 OK)
- 다른 인스턴스 포트 (55432/55433) 절대 X

**ed25519 SSH key 등록**: 메인 세션이 5/10 14:30에 ssh-copy-id 등록 완료 — 별도 세션도 즉시 SSH 가능.

---

## 7. END

작성: 2026-05-10 20:30 KST
작성자: 메인 세션 (조현빈 외출 중 + 별도 검증 세션 권장 응답)
다음 step: 별도 세션이 §3 작업 흐름 따라 진행 → audit md 4건 + SUMMARY → handoff back to 메인 세션

**핵심**: 메인 측정 세션과 영향 0 → 검증 끝나면 메인이 결과 반영 (narrative 정정 또는 강화).
