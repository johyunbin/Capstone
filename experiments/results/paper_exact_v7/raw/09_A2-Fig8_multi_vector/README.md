# 09 — A2-Fig8 Multi-Vector (paper Fig 8 영역)

본 디렉토리는 paper Fig 8 multi-vector 시나리오 추가 측정 (5/14 11:00 80 회 측정 추가).

## paper Fig 8 의미

paper §VI experimental setup 의 multi-vector 시나리오:
- 한 쿼리에 여러 벡터 (multi-vector embedding) 사용
- 예: 이미지 + 텍스트 dual-encoder, 또는 한 이미지의 여러 region embedding
- single-vector 보다 더 복잡한 분포 → stratification 의 강화 효과

## 측정 file (8 file)

```
09_A2-Fig8_multi_vector/
├── A2-Fig8_CaseA_sparse_rp.json
├── A2-Fig8_CaseA_chao_weighted.json
├── A2-Fig8_CaseA_hilbert_real.json
├── A2-Fig8_CaseA_hyperloglog.json
├── A2-Fig8_CaseB_sparse_rp.json
├── A2-Fig8_CaseB_chao_weighted.json
├── A2-Fig8_CaseB_hilbert_real.json
└── A2-Fig8_CaseB_hyperloglog.json
```

A2-Fig8 = paper Fig 8 multi-vector cell, 4 method × 2 mode = 8 file.

## 핵심 finding (본 narrative §10)

- 본 portfolio 의 paper Fig 8 영역 추가 측정 (5/14 11:00 80 회 측정 추가 작업의 결과)
- single-vector (Fig 5/6, Fig 7, Fig 9) 와 동일 패턴 — 우리 method 의 통계 우위 유지
- multi-vector 분포 복잡도 증가에도 우리 ensemble 의 robust 성 검증

## 출처

`_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` §10 (A2-Fig8 측정 80 회수 추가)
`10_full_portfolio_CaseA_CaseB_B1/REPORT_분석/REPORT_paper_exact_v11.md` §10
