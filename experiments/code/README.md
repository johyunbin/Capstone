# experiments/code/ — 측정 script (2026-05-19 갱신)

> 본 연구의 활성 측정·분석·문서 빌드 script 는 `_internal/scripts/` 에 있다. 본 디렉토리는 W1~W4 초기 sprint script archive 만 보유한다.

## 활성 script 위치 — `_internal/scripts/`

- `measure_paper_exact.py` — paper §V-B 재현 + 우리 method 측정
- `_measure_common.py` — 공통 측정 library (N_STRATA=20 default)
- `analyze_paper_exact.py` — 측정 결과 분석
- `md2pdf.py` · `md2docx.py` — 문서 빌드 도구 (Chrome CDP · pandoc)
- 완료된 측정 캠페인 launcher 는 `_internal/scripts/archive/`

상세는 `_internal/SERVER_REGISTRY.md` · `_internal/METHOD_REGISTRY.md`.

## archive

```
code/
├── README.md   본 파일
└── archive/2026_04_W1_W4_초기실험_scripts/   W1~W4 sprint script (4/16~5/10)
    ├── rq1/ (27)   RQ1 motivation 측정
    ├── rq2/ (5)    KM20 allocation
    ├── rq3/ (43)   RQ3 22-method runner
    └── local_analysis/ (42)   figure 생성
```

W1~W4 sprint script 는 paper exact / v13 측정으로 superseded. 신규 측정은 `_internal/scripts/measure_paper_exact.py` base 를 사용한다 — archive 안 초기 script 직접 사용은 정합성 보장이 안 되므로 비권장.

---

작성: 2026-05-19 · 디렉토리 총 정리. 이전 README(5/14)는 git history 보존.
