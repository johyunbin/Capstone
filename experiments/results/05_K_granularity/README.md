# 05_K_granularity — 클러스터 수 K 민감도

층화에 쓰는 **KMeans 클러스터 개수 K 를 10 / 20 / 30** 으로 바꿔 본 측정. 기본 K=20
대비 K 가 결합 추정 정확도에 미치는 영향을 본다.

- file 150개 (cell × K{10,20,30} × method)
- 구조: `{데이터셋}_{sf}/K{10|20|30}/{측정캠페인}/{mode}/{파일}.json`
- 측정 캠페인 하위 분리:
  - `run-paper-exact/` — raw paper-exact K granularity (method 4종: chao_weighted, hilbert_real, hyperloglog, sparse_rp)
  - `run-v6-v10/` — 확장 측정 v6~v10 (16 method, K10/K30)
- 같은 cell·K 라도 두 캠페인은 독립 재측정 — 평균 내지 말고 캠페인별로 본다

> K granularity 효과는 차원 의존성이 약하고 run-level bias 가 있음 (analysis 보고서 참조).
