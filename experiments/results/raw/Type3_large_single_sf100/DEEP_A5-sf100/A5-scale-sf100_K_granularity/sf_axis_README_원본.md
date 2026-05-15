# 06/SF_axis — K granularity × SF axis (SF=1/10/100 추가 측정)

5/14 22:00 추가 측정 (박세은 8:50 발견 + 사용자 옵션 B 결정). DEEP single dataset 의 3 SF axis (A5-scale-sf{1,10,100}) × K=10/30 × 4 anchor × CaseA/CaseB = 48 file.

## 측정 scope

- **cells**: A5-scale-sf1 (DEEP sf=1, 1M rows), A5-scale-sf10 (sf=10, 10M), A5-scale-sf100 (sf=100, 100M)
- **K values**: K=10 + K=30 추가 (K=20 = paper exact base 활용, raw/10_전체측정_백업/CaseA_단독대체_495 + CaseB_결합_496)
- **methods**: 4 anchor (sparse_rp / chao_weighted / hilbert_real / hyperloglog)
- **modes**: CaseA (단독 대체) + CaseB (결합 ensemble)
- **query**: Q3 / Q5 / Q20 (paper Fig.14 query set)

## 디렉토리

| Dir | K 값 | file 수 |
|---|---|---:|
| `K10/` | 10 | 24 (3 cells × 4 method × 2 mode) |
| `K30/` | 30 | 24 |
| (K=20 base) | 20 (paper exact) | raw/10_전체측정_백업/CaseA_단독대체_495 + CaseB_결합_496 |

## 파일명 규칙

`{cell}_{mode}_{method}.json`

예시:
- `K10/A5-scale-sf1_CaseB_sparse_rp.json`
- `K30/A5-scale-sf100_CaseA_chao_weighted.json`

## B1 baseline (paper Bernoulli) reference

| Cell | B1 trim10 mean | path |
|---|---:|---|
| A5-scale-sf1 | 1.6182 | raw/10_전체측정_백업/B1_baseline_9cell/A5-scale-sf1_B1.json |
| A5-scale-sf10 | 1.5407 | raw/10_전체측정_백업/B1_baseline_9cell/A5-scale-sf10_B1.json |
| A5-scale-sf100 | 1.6346 | raw/10_전체측정_백업/B1_baseline_9cell/A5-scale-sf100_B1.json |

## 측정 method

- server: capstone2026@165.132.140.240
- script: `/mnt/hdd0/home/capstone2026/cache/rq3/run_km_sf_axis.sh` (5/14 신규 작성, scp 전송)
- N_STRATA patch: `_measure_common.py` line 59 sed (10 또는 30) → 측정 → 복원
- measurement code: `cache/rq3/measure_paper_exact.py --rq 3 --phase B --cell {cell} --mode {mode} --method {method} --output {OUT_DIR}`
- output dir (server): `cache/rq3/paper_exact_km{K}_sf_axis/`
- 측정 시간: K=10 12:12 → 12:31 (19분), K=30 12:45 → 13:02 (17분)

## 측정 결과 분석

★ `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md` (3-way K granularity SF axis 종합 분석 + 박세은 8:50 답변 영역)

## 핵심 finding (3 줄)

1. **sparse_rp = K=10 매우 sensitive (모든 SF 에서 +50~+90% 악화)**, K=20/K=30 strong (−7~−12%)
2. **chao_weighted = K=20 sweet spot 모든 SF 일관** (sf=1 −14.11%, sf=100 −12.20%)
3. **hilbert_real / hyperloglog = K-robust + K=30 slight edge** (gap 1-2.4%)

→ 회의 PDF v2 §2.5 "SF=1 영역 K=20 best 미측정" wording 정정: SF=1+10+100 axis 모두 측정 완료, method-dependent K best 패턴 일관.

---

작성: 2026-05-14 22:10 KST · K=10+K=30 회수 + 3-way 분석 + 박세은 carry-over 가능 form
