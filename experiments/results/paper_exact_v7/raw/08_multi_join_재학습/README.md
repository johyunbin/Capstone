# 08 — Multi-Join 재학습 (Multi-Table)

본 디렉토리는 multi-join cross-table 시나리오에서 KM20 stratification 재학습 필요성 raw 측정.

## 의미

paper §V-B 는 단일 table 시나리오. 우리는 다음 시나리오:
1. 단일 table 에서 KM20 학습 → stratum sigma 산출 → estimator 작동
2. multi-join (예: DEEP × WIKI cross) 시 stratum sigma 가 다르므로 **재학습 필수**
3. 재학습 하지 않으면 stratum 불일치 → 추정 변동성 증가

## 측정 file (8 file)

```
08_multi_join_재학습/
├── A2-Fig9_CaseA_sparse_rp.json     ← multi-join 재학습 후
├── A2-Fig9_CaseA_chao_weighted.json
├── A2-Fig9_CaseA_hilbert_real.json
├── A2-Fig9_CaseA_hyperloglog.json
├── A2-Fig9_CaseB_sparse_rp.json
├── A2-Fig9_CaseB_chao_weighted.json
├── A2-Fig9_CaseB_hilbert_real.json
└── A2-Fig9_CaseB_hyperloglog.json
```

A2-Fig9 = DEEP+WIKI cross join (multi-table scenario), 4 method × 2 mode = 8 file.

## 핵심 finding (본 narrative §9 multi-join)

- multi-join 재학습 시 stratum sigma 변화 → 추정 변동성 30% 감소
- 재학습 안 한 baseline 대비 정확도 약 5% 우위
- → multi-table production scenario 에서 재학습 필수

## file 명 규칙

`A2-Fig9_{mode}_{method}.json`

## 출처

`_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` §10
`10_full_portfolio_CaseA_CaseB_B1/REPORT_분석/REPORT_paper_exact_v11.md` §9
