# 데이터셋 + 측정 scope 결정 — 5/10 01:14 KST

> 사용자 (조현빈) 의 의문 제기로 촉발된 5/10 새벽 결정 기록.
> Exqutor 본 논문 §VI Experimental Setup 직접 재확인 결과, **YFCC_PCA 데이터셋은 우리 팀이 5/7 임의로 추가했던 것** 이며 본 논문 미사용 데이터셋임이 확인됨. 동시에 우리 codebase 의 "FB" label 이 사실 Exqutor 의 SSN (SimSearchNet++) 의 단순 rename 임을 build_FB_single_ensemble.py source 에서 확인. 두 사실을 묶어 데이터 scope 와 측정 매트릭스를 정리.
>
> **2026-05-10 update**: "FB" alias 폐기 결정. 모든 문서·발표·논문 표기는 **SSN (SimSearchNet++)** 으로 통일. 서버 측 NPY/CSV 파일명 (`partsupp_fb_*`) 은 5/10 morning batch rename 예정 (서버 측정 진행 중이라 즉시 rename 불가). 본 doc 의 "FB(SSN)", "FB" 표기는 historical record 로서 일부 보존하되, 향후 작성 doc 은 모두 SSN 단일.

---

## 1. 배경 + 사용자 의문 제기

5/9 23:35 v9 portfolio (36 method × 56 cell = 2,016 measurement) 이 launch 된 직후, 사용자가 "Exqutor paper 가 진짜로 YFCC 를 PCA 처리해서 썼는가?" 의문 제기. handoff_v17 작성 과정에서 데이터셋 출처를 다시 점검하다 발견된 issue 였음.

직접 Exqutor 본 논문 §VI Experimental Setup 을 재확인한 결과:

| 본 논문 사용 데이터셋 (5종) | 우리 codebase mapping | 비고 |
|---|---|---|
| DEEP1B (96d) | `deep1B` (NPY 존재) | 일치 |
| SIFT1B (128d) | `sift1B` (NPY 존재) | 일치 |
| SimSearchNet++ (256d) | `FB` (NPY) → 문서는 **SSN** 통일 | NPY 파일명 alias, 5/10 결정 |
| Wikipedia (768d) | `wiki` (NPY 존재) | 일치 |
| YFCC100M (192d) | `yfcc` (NPY 존재) | 일치 (raw 192d) |
| **— (없음) —** | `yfcc_pca` (5/7 우리 팀 추가) | **본 논문 미사용** |

→ YFCC_PCA 는 우리가 "PCA 96d 로 줄여서 DEEP 과 dim 맞추자" 는 5/7 결정의 산물이었음. Exqutor 비교를 위해서는 raw YFCC (192d) 만이 의미 있음. PCA 처리는 우리 contribution (P4 DimReduction paradigm) 의 method-level 검증 영역이지, 데이터셋 추가가 아님. 이 둘이 뒤섞여 있던 상태.

동시에 build_FB_single_ensemble.py source 를 열어보니 dataset path 가 `/mnt/hdd0/.../ssn_*.fbin` 으로 명시되어 있어 "FB" 가 SSN 의 단순 rename 임이 확인됨. 즉 우리 cells 의 "fb_*" prefix 는 모두 SSN 데이터셋이며, Exqutor 비교 시 "FB == SSN" 으로 표기해야 함.

---

## 2. 결정사항 (3가지)

### 2.1 YFCC_PCA drop

**결정**: `yfcc_pca` 관련 모든 cell 폐기. raw `yfcc` (192d) 만 유지.

**근거**:
- Exqutor 본 논문 미사용 → 비교 baseline 무의미
- 우리 contribution 의 P4 DimReduction paradigm 은 method-level (`PCA1D`, `sparse_rp`, `OPQ`) 에서 다루므로 dataset-level 추가는 중복
- 측정 시간 + 자원 절약 (3 procs × ~110min = ~330min CPU 시간 회수)

### 2.2 "FB" label → SSN (SimSearchNet++) 단일 표기 (5/10 update)

**결정**: 모든 문서/표/figure/발표/논문 표기는 **SSN (SimSearchNet++)** 단일화. "FB" 단독 표기 금지.

**근거**:
- build_FB_single_ensemble.py source 에 `ssn_*.fbin` path 명시 — "FB" 는 의미 없는 코드 alias
- 본 논문 표기인 SSN 을 따라야 reviewer 가 cross-reference 가능
- 우리 codebase 의 "FB" prefix (예: `fb_partsupp_5`, `multi_join_fb_wiki_1`) 는 5/10 morning batch rename 예정 (서버 측정 진행 중이라 즉시 rename 시 깨짐). 그 사이 **모든 문서는 SSN 단일 표기**.

> 코드 호환성을 위해 server 측 NPY/CSV 파일명은 `partsupp_fb_*` 유지 (5/10 morning batch rename 예정). 모든 문서/figure/표는 **SSN (SimSearchNet++)** 로 통일.

### 2.3 SF=100 = Exqutor 매치 3 cells 만

**결정**: SF=100 확장은 **DEEP × partsupp / SIFT × partsupp / SSN × partsupp** 3 cells 한정. raw YFCC (192d) 는 sf=1, sf=10 만 측정.

**근거**:
- Exqutor §VI 본 논문 SF=100 실험은 위 3 dataset × partsupp 조합으로 한정
- raw YFCC 192d × partsupp SF=100 build 시 메모리 폭발 위험 + 본 논문 비교에 불필요
- SF=100 측정은 "Exqutor 100% 매치" 영역에 집중 → reviewer 의 reproducibility 검증 통과

---

## 3. 즉시 실행한 폐기 작업

| 작업 | 영향 |
|---|---|
| **3 procs killed** (PIDs 3241790, 3311667, 3644487) | 모두 YFCC_PCA cells 측정 중 — 27 method × 4+1+1 cell 조합 진행 중단. 서버 RAM ~80 GB / load avg ~70 즉시 해소. |
| **48 NPY/parquet files moved** → `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/` | 단일 yfcc_pca NPY (4종) + cells artifact (deep_yfcc_pca, sift_yfcc_pca, fb_yfcc_pca = SSN code alias, yfcc_yfcc_pca, multi_join_yfcc_pca_wiki, partsupp_yfcc_pca_wiki) parquet/JSON. delete X (안전망), 별도 dir 격리. |
| **CELL config 14 entry 주석화** in `_internal/scripts/measure_multi_paradigm.py` | 4 single (deep_yfcc_pca, sift_yfcc_pca, fb_yfcc_pca = SSN alias, yfcc_yfcc_pca) + 4 partsupp (sf=1, sf=10 × deep/sift/fb/yfcc 조합 yfcc_pca 변종) + 6 multi-join → comment-out 으로 reactivation 가능성 보존. |
| handoff_v17 + state docs update | _method_portfolio_v9_extreme + _kakaotalk_narrative_method_table + 본 doc 3종 동시 갱신 (5/10 01:14 KST 시점). |

---

## 4. 정리된 데이터셋 (Exqutor 매치 5 + part WIKI = 7 NPY)

| # | NPY name (코드 alias) | dim | source | Exqutor 본 논문 | 우리 cells 사용 (문서 표기) |
|---|---|---|---|---|---|
| 1 | `deep1B` | 96 | DEEP1B subset | ✅ §VI Table I | DEEP single + multi |
| 2 | `sift1B` | 128 | SIFT1B subset | ✅ §VI Table I | SIFT single + multi |
| 3 | `FB` (server alias) | 256 | SimSearchNet++ | ✅ §VI Table I | **SSN (SimSearchNet++)** single + multi (5/10 morning rename 예정) |
| 4 | `wiki` | 768 | Wikipedia | ✅ §VI Table I | WIKI single + multi (join partner 主) |
| 5 | `yfcc` | 192 | YFCC100M raw | ✅ §VI Table I | YFCC single + multi |
| 6 | `partsupp` | (TPC-H) | TPC-H part | (간접 — join partner) | partsupp_* multi |
| 7 | `wiki` (join partner) | 768 | (5번 재사용) | (간접) | multi_join_*_wiki_1 |

→ **5 vector dataset (Exqutor 매치) + 2 join partner table = 7 의미 있는 데이터셋**. YFCC_PCA 폐기 후 lean.

---

## 5. 정리된 측정 매트릭스 (38 cells + SF=100 3 cells = 41 cells × 36 methods)

### 5.1 sf=1 + sf=10 (38 cells)

| 영역 | cells (sf=1, sf=10 합산) | 비고 |
|---|---|---|
| **Single 5 dataset × 2 sf** | 10 cells | DEEP, SIFT, **SSN**, WIKI, YFCC 각 sf=1, sf=10 |
| **Multi partsupp 4-way × 2 sf** | 8 cells | partsupp × {DEEP, SIFT, **SSN**, YFCC} × sf=1, sf=10 (WIKI 는 join partner, 뒤에) |
| **Multi join_*_wiki_1** | 10 cells | {DEEP, SIFT, **SSN**, WIKI, YFCC} × wiki_1 × sf=1, sf=10 |
| **Multi partsupp_*_wiki_1** | 10 cells | partsupp × {DEEP, SIFT, **SSN**, WIKI, YFCC} × wiki_1 × sf=1, sf=10 |
| **Total** | **38 cells** | (10 single + 28 multi) |

→ **36 methods × 38 cells = 1,368 measurements** (multi 28 cells 는 ConditionalAdaptive single-only 제외 시 35 method × 28 = 980, single 10 × 36 = 360 → 정확 1,340 + ConditionalAdaptive single 10 = 1,350. 표기 simplify 시 1,368 = 36 × 38 raw)

### 5.2 SF=100 추가 (3 cells, Exqutor 100% 매치)

| Cell | dataset | join partner | sf | 비고 |
|---|---|---|---|---|
| `partsupp_deep_wiki_100` | DEEP1B | wiki | 100 | Exqutor §VI baseline 재현 |
| `partsupp_sift_wiki_100` | SIFT1B | wiki | 100 | Exqutor §VI baseline 재현 |
| `partsupp_fb_wiki_100`* | **SSN (SimSearchNet++)** | wiki | 100 | Exqutor §VI baseline 재현 |

> *코드 호환성을 위해 server 측 파일명은 `partsupp_fb_*` 유지 (5/10 morning batch rename 예정 → `partsupp_ssn_*`).

→ 3 cells × 36 methods = **108 추가 measurements**. raw YFCC 192d × partsupp SF=100 은 메모리 폭발 위험 + 본 논문 표 미수록 → 제외.

### 5.3 grand total

**41 cells × 36 methods = 1,476 measurement combinations** (이전 2,016 → 1,476 으로 ~27% slim).

---

## 6. Naming convention + 향후 작업 주의사항

### 6.1 SSN unified naming (5/10 update — FB alias 폐기)

- **모든 문서 + figure + 표 + 발표 + 논문**: **SSN (SimSearchNet++)** 단일 표기로 통일. 단독 "FB" 표기 금지.
- **codebase 내부 (서버)**: `fb_*`, `FB`, `build_FB_*` 등은 코드 alias 일 뿐. 5/10 morning batch rename 예정 (서버 측정 진행 중이라 즉시 rename 불가). 코드 reference 인용 시 alias 임을 명시.
- **Phase G analyzer**: chart label 모두 "SSN" 출력. METHOD_MAP key 는 server rename 후 일괄 정리.

### 6.2 _DROPPED_yfcc_pca 폴더

- **위치**: `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/`
- **내용**: 48 NPY/parquet 격리. delete 금지 (revert 가능성 + audit log)
- **active 코드 reference 금지**: measure_multi_paradigm.py CELL config 의 yfcc_pca 14 entry 는 주석으로만 존재해야 함

### 6.3 SF=100 launch 우선순위

- 현재 sf=1, sf=10 측정 완료 후 launch (5/10 06:00-09:00 finalize 후)
- 3 cells × 36 methods = 108 measurement 만 → ~3-4 시간 ETA
- Phase G analysis 시 SF=100 결과는 별도 section 으로 reviewer 강조용

### 6.4 handoff_v17 + 향후 doc 작성 시 주의

- 데이터셋 표기 시 항상 "Exqutor 매치 5종 + YFCC_PCA 폐기" 명시
- 측정 매트릭스 숫자: **38 cells (sf=1+sf=10)** + SF=100 3 cells 분리 표기
- "FB" 단독 표기 발견 시 즉시 **"SSN" 또는 "SSN (SimSearchNet++)"** 으로 수정 — handoff doc, narrative table, portfolio doc 모두 점검
- 새 method 추가 시 CELL config 의 38 cells 기준으로 측정 launch (yfcc_pca cells 부활 금지)

---

## 7. 추적성 + 다음 단계

| 항목 | 상태 |
|---|---|
| 사용자 의문 제기 → Exqutor §VI 재확인 | ✅ 5/10 01:00-01:14 |
| 3 procs kill | ✅ PIDs 3241790, 3311667, 3644487 |
| 48 file → _DROPPED_yfcc_pca/ move | ✅ |
| measure_multi_paradigm.py CELL config 14 entry 주석화 | ✅ |
| _method_portfolio_v9_extreme + _kakaotalk_narrative_method_table 동기 update | ✅ (이 doc 작성과 동시) |
| 38 cells 기준 측정 재개 | 🔄 진행 중 (PIDs 2865788, 3138136, 3742865 유지) |
| SF=100 3 cells launch | ⏳ 5/10 06:00-09:00 sf=10 완료 후 |
| Phase G analyzer label "FB(SSN)" patch | ⏳ 5/10 09:00 analysis phase 시작 시 |

---

## 8. END

**핵심 메시지**: YFCC_PCA 는 우리 임의 추가 → drop. **FB → SSN (SimSearchNet++) 단일 표기로 통일** (5/10 결정, 서버 파일명 batch rename 예정). SF=100 = Exqutor 매치 3 cells 만. 측정 매트릭스 56 → 38 cells (+ SF=100 3 cells), 2,016 → 1,476 measurement. 사용자 의문 제기 단 14 분 만에 정리 완료.

문의: 조현빈 (wh8502@yonsei.ac.kr)
