# 02_single_vector_본실험 — ★ 본 연구 핵심 측정

단일 벡터 컬럼, 선택도 sel=0.01 에서 **16 method 의 CaseB(결합) 측정**. 본 연구의
"분포 인지 stratification 을 Bernoulli 와 결합하면 추정이 정확해지는가" 라는 핵심
질문에 답하는 main 측정이다.

- file 278개 (cell × 16 method × CaseB, 일부 cell 은 B1 동반)
- 구조: `{데이터셋}_{sf}/{측정캠페인}/{mode}/{파일}.json`
- 측정 캠페인 하위 분리:
  - `run-paper-exact/` — 5월 paper-exact portfolio (DEEP·SIFT·SSN·YFCC·DEEP+WIKI 의 A1/A2 cell)
  - `run-v6-v10/` — 확장 측정 v6~v10 (WIKI·YFCC sf1·DEEP+SIFT·SIFT/SSN scale)
  - `run-rq3-detail/` — A2-Fig9 의 독립 재측정 4건 (paper_main 과 별개 run, byte 다름)

분석 시 `B1` (= `01_baseline_paper재현/`) 와 `CaseB` 의 `avg_q_error_trimmed` 를
같은 cell 에서 비교한다. CaseB < B1 이면 결합이 추정을 개선한 것이다.

> 16 method 외 method 와 CaseA(단독 대체) 는 `_archive_미사용method/02_single_vector_본실험/`
> 에 별도 보존 (본 분석 비사용).
