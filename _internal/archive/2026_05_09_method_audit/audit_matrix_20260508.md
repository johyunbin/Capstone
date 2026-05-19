# 측정 매트릭스 Completeness Audit — 5/8 21:48 KST

서버 산출물 read-only 검증. 측정 추가 launch 없음.

## 1. Single 10 cell 매트릭스

기대값: 5 sel × 5 seed × 100 q = 2500 row (RQ1/RQ3/Adaptive). RQ1 km20 는 km20+bern 2 mode 결합으로 5000 row. RQ2 5mode 는 5 mode × 2500 = 12500 row.

| Cell | RQ1 km20 | K-sweep (10/50/100/200) | RQ2 5-mode | RQ3 11 method | Adaptive |
|------|---------|------------------------|-----------|--------------|---------|
| DEEP_sf1 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| DEEP_sf10 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| SIFT_sf1 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| SIFT_sf10 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| SSN_sf1 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| SSN_sf10 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| WIKI_sf1 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| WIKI_sf10 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| YFCC_sf1 | OK 5000 | OK all 2500 | OK 12500 | OK all 2500 | OK 2500 |
| YFCC_sf10 | OK 5000 | **MISS k10/50/100/200** | OK 12500 | OK all 2500 | OK 2500 |

**Single completeness: 49/50 (98%)**. 단일 결손 = YFCC_sf10 K-sweep 1 cell × 4 K. (K-aware sweep narrative 의 일반화 완전성에 영향.)

## 2. Multi 3 cell 매트릭스

| Cell | 4kang (10000) | RQ2 5mode (12500) | RQ2 4way (12500) | Wave1 halton/hammersley/reservoir (2500×3) | Paradigm 11종 | Adaptive |
|------|--------------|-------------------|------------------|-------------------------------------------|--------------|---------|
| partsupp_deep_sift_10 | OK 10000 | OK 12500 | OK 12500 | OK / OK / OK | **0% (running)** | **CSV partial 1/3 done** |
| partsupp_deep_wiki_10 | OK 10000 | OK 12500 | OK 12500 | OK / OK / OK | **0% (running)** | **0% (running)** |
| multi_join_deep_wiki | **MISS** | OK 12500 | N/A (alt rq2_multi_join_deep_wiki=10000) | OK / OK / OK | **0% (running)** | **0% (running)** |

**Multi 완료된 측정: 4kang 2/3 (multi_join_deep_wiki 결손) + RQ2 3/3 + Wave1 3/3.** Paradigm/Adaptive 백그라운드 진행 중 (PID 4100548 adaptive, 4100549 paradigm — 12:34 launch, 18시간 누적 CPU). adaptive 1/3 cell complete (12:42), paradigm 출력 0개. ETA paradigm ~10h, adaptive ~5h → 5/9 새벽 도착.

## 3. 누락 측정 5종 + 추가 가능성

| # | 측정 | 현 상태 | 추가 launch 부담 | 우선순위 |
|---|------|--------|----------------|---------|
| A | YFCC_sf10 K-sweep (k=10/50/100/200) | 4 cell missing | ~2h | **HIGH** — narrative 완전성 |
| B | multi_join_deep_wiki 4kang | 1 cell missing | ~3h | **MEDIUM** — multi narrative 일관성 |
| C | Sample size sensitivity (385 vs 100 vs 1000) | 8M/SIFT 만 부분존재 (rq2_size_sensitivity_*) | ~5h × 10 cell | LOW — limitation 명시 |
| D | Selectivity 0.001/0.005 extreme low | 부재 | ~4h × 10 cell | LOW — boundary 영역 |
| E | SF100 (80M) | 부재 (vanilla_sf100/ exists) | ~60-80h | DEFER — 5/27 무리 |
| F | Multi SF1 setup | 부재 | ~수시간 setup + 측정 | LOW — multi 자체 sweet spot 25× shrunk |
| G | Ensemble (4강 × Adaptive) single | 부재 | ~10h | LOW — 자문 회신 후 |

## 4. 권장 결론

**5/27 발표 전 추가 launch 가치 있는 것 (priority 순):**

1. **A (YFCC sf10 K-sweep, ~2h)** — RQ1 K-sweep narrative 가 "DEEP/SIFT/SSN/WIKI/YFCC × SF1/SF10 = 10 cell 전체 cross-validation" 으로 진술되려면 필수. 현재 9/10 으로는 "YFCC sf10 제외" 라는 footnote 가 Q&A 표적.
2. **B (multi_join_deep_wiki 4kang, ~3h)** — 4kang multi 일반화 문장을 3 cell 모두 갖춰서 "단일 sweet spot 17.13% → multi 0.67% (25× shrinkage)" 의 완전한 paired Δ% 가능. 현재 join cell 만 결손 → narrative 약화.

**limitation 명시 충분 (추가 launch 불필요):**
- C/D (sample size, extreme sel): RQ2/RQ3 의 σ-allocation < 1% 격차 결론을 흔들지 않음. limitation 1줄.
- E (SF100): 채림 자문 회신 + 시간 부담 → future work.
- F/G: Multi sweet spot 25× shrunk 결론으로 충분 + ensemble 은 자문 합의 후.

**총 권장 추가 launch: 2종 × ~5h = 5/9 자정 전 도착 가능.** 측정 추가 launch 권한은 사용자 결정.
