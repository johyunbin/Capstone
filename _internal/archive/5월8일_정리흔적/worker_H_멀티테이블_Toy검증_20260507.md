# Worker H — 멀티 테이블 Toy 검증 (본 연구 마무리 단계)

> **임무**: 단일 테이블에서 발견한 효과적인 RQ3 방식 (Hilbert / MiniBatch partial / HDBSCAN / Hybrid) 을 멀티 테이블 join 환경에 적용. 5/5 회의 옵션 (B) Toy 검증. 본 연구의 Exqutor 마무리 단계.
> **세션 진입**: 본 핸드오프 첫 read → 5/5 회의록 + RQ재정립안 read → 멀티 테이블 데이터 준비 → 측정 → 분석 → commit.
> **manager 세션**: 2026-05-07 12:05 KST, Opus 4.7 1M.
> **시간 제약**: W2~W3 sprint (~1주), 5/22 미팅 또는 5/27 발표에 결과 포함.

---

## 1. 입력 자료

| 자료 | 위치 |
|---|---|
| 5/5 회의록 (옵션 B 결정 — Toy 검증 추가) | `_internal/records/kakaotalk/20260505_RQ재정립_회의.md` |
| RQ 재정립 plan (Limitation 4 — 단일→멀티 future work) | `plans/RQ재정립_20260505_2122.md` |
| Exqutor 본 논문 (multi-relation join 방법) | `reference/papers/Exqutor.pdf` 또는 arXiv:2512.09695v2 |
| 단일 테이블 RQ3 4강 결과 | `experiments/results/RQ1_RQ2_RQ3_종합_master.md` |
| 단일 테이블 측정 인프라 | `/mnt/hdd0/home/capstone2026/cache/rq3/run_*.py` |

## 2. 5/5 회의 합의 (재확인)

박세은 5/5 20:17:
> "Exqutor 와 연관 지으려면 멀티테이블 환경에서 검증을 통해 단일 → 멀티 개선이 이루어지는지 검증 절차가 필요하지 않은가?"

→ 옵션:
- (A) **연구 positioning 재정의** — Exqutor 단일 영역에 새 솔루션, 멀티는 future work ✓ **5/5 채택**
- (B) **Toy 검증 추가** — 1~2일 정성 분석

→ **5/7 사용자 결정 (본 worker)**: (B) 옵션도 추가 진행 — 본 연구 마무리 단계.

## 3. 작업 단계

### Step 1 (1h) — 멀티 테이블 데이터 준비

**옵션 A (TPC-H benchmark 활용)**:
- TPC-H scale factor 1 (~1GB) 또는 SF=10 (~10GB)
- partsupp ⋈ part / lineitem ⋈ orders / customer ⋈ orders ⋈ lineitem 같은 join
- pgvector + TPC-H 데이터 + embedding column 추가 (예: part 의 description embedding)

**옵션 B (현재 단일 테이블 데이터 → 인공 join)**:
- partsupp_deep_10_subset_1m + customer_sift_10_phase7_noidx_subset 같은 두 테이블
- join key 추가 (예: partkey ↔ custkey 1:1 매핑) → 인공 multi-table 환경
- 빠른 toy 측정 가능

**권장**: 옵션 B (Toy 검증, 1~2일 분량). TPC-H 정식 도입은 별도 future work.

```bash
ssh capstone "
PSQL=/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin/psql
\$PSQL -h /tmp -p 55436 -U wns41559 -d wns41559 -c '
-- 인공 join 테이블 (toy 검증용)
CREATE TABLE IF NOT EXISTS toy_multi_join AS
SELECT p.ps_partkey, p.ps_embedding AS deep_emb,
       c.c_embedding AS sift_emb,
       p.stratum_id AS deep_stratum, c.stratum_id AS sift_stratum
FROM partsupp_deep_10_subset_1m p
JOIN customer_sift_10_phase7_noidx_subset c
  ON p.ps_partkey % 1000000 = c.c_custkey % 1000000;
'
"
```

(또는 더 간단: 두 테이블 분리 측정 후 join cardinality 곱셈으로 multi-table 추정)

### Step 2 (2h) — Exqutor multi-relation 측정 인프라 분석

```bash
# Exqutor 본 논문의 multi-relation join cardinality 추정 방식 확인
# - vector range join 의 stratum_id 활용 방식
# - 단일 테이블 stratum_id 가 join 후에도 의미 유지하는지

ls /mnt/hdd0/home/capstone2026/Exqutor/Code 2>/dev/null  # 본 논문 코드
find /mnt/hdd0/home/capstone2026/Exqutor -name '*.py' -path '*multi*' 2>/dev/null
find /mnt/hdd0/home/capstone2026/Exqutor -name '*.py' -path '*join*' 2>/dev/null
```

### Step 3 (3h) — 단일 테이블 RQ3 4강 method를 multi-table에 적용

**4강 method**: Hilbert / MiniBatch partial / HDBSCAN / Hybrid

각 method 의 multi-table 확장:
- **Hilbert (curve)**: 두 테이블 각자 Hilbert curve fit → join 후 stratum_id 조합 (D × S 격자)
- **MiniBatch partial_fit**: 각 테이블 K=20 cluster, join 후 cluster pair (20 × 20 = 400 strata)
- **HDBSCAN**: density 기반, join 후 hierarchical 처리
- **Hybrid**: KMeans + Hilbert 조합

vs **baseline** (단일 테이블 BERN 의 multi-table 확장):
- BERN_multi: 두 테이블 각자 random sample → join 결과 cardinality 추정

**측정 변수**:
- 데이터: toy_multi_join (1M × 1.5M ≈ 1M join, 1:1 mapping)
- selectivity: 5 sel (0.01 / 0.05 / 0.10 / 0.30 / 0.50)
- seed: 5개
- query: 100개 (multi-relation join cardinality 추정)
- 비교: BERN_multi vs 4강 method × 2 (단일 stratum 사용 vs join stratum 조합)

### Step 4 (2h) — 측정 결과 분석

핵심 질문: **단일 테이블에서 효과 있던 4강 method가 multi-table 환경에서도 BERN 대비 개선되는가?**

기대 결과:
- ✓ Hilbert / MiniBatch partial 가 multi-table 에서도 BERN 우위
- ⚠️ Effect size 는 단일보다 작을 수 있음 (join 후 분산 증폭)
- ✓ "단일 정확성 → multi 일반화의 *충분조건*" 정량 입증

### Step 5 (1h) — narrative 작성

`experiments/results/rq3_agnostic/multi_table_toy_validation.md`:
- 단일 vs multi 4강 method × 5 sel × 2 dataset 결과
- 단일에서 발견한 효과의 multi-table 일반화 가능성 정량
- 5/27 발표 / 6/11 보고서 narrative 입력

### Step 6 (30분) — commit + push

```bash
git add experiments/code/multi_table/ \
        experiments/results/rq3_agnostic/multi_table_toy_validation.md \
        experiments/results/rq3_agnostic/multi_table_*.parquet
git commit -m "멀티 테이블 Toy 검증 — 단일 테이블 RQ3 4강 method의 multi-table 일반화 입증 (본 연구 마무리)"
git push
```

## 4. 산출 spec

| 산출 | 위치 | 형식 |
|---|---|---|
| Multi-table 측정 인프라 | `experiments/code/multi_table/run_*.py` | Python |
| Multi-table 4강 측정 결과 | `experiments/results/rq3_agnostic/multi_table_*.parquet` | parquet |
| Multi-table Toy 검증 narrative | `experiments/results/rq3_agnostic/multi_table_toy_validation.md` | markdown |
| 5/27 발표 보강 (옵션) | `submission/_drafts/속도는벡터_5월27일발표_slide_outline_*.md` | Slide 추가 |

## 5. 의존성

- **Worker F + G (8M 보강)**: 의존성 없음, 병렬 가능
- **5/22 교수님 미팅**: 본 결과를 미팅 안건으로 (지도교수 자문 — multi 일반화)
- **5/27 발표**: 본 결과를 Slide 12 (Future Work) → "★ Toy 검증 결과로 일부 입증" 으로 격상

## 6. 예상 시간

총 **8-12h** (1~2일 분량, 5/5 회의 옵션 B 명시). W2~W3 sprint.
- 데이터 준비: 1h
- 인프라 분석: 2h
- 측정 코드 작성 + dispatch: 3h
- 분석: 2h
- narrative 작성: 1h
- commit: 30분

## 7. 본 worker가 만들지 말 것

- TPC-H 정식 도입 (Toy 검증 → 정식은 future work)
- 본 연구 contribution 7종 변경 (master.md 보존)
- multi-table을 main contribution으로 격상 (단일이 main, multi는 입증 단계)

---

## 부록 A — 5/5 회의 옵션 (A) vs (B) 충돌 해소

5/5 회의에서 (A) "positioning 재정의" 채택. 그러나 5/7 사용자 결정으로 (B) "Toy 검증 추가" 도 진행:

- (A) 보존: 본 연구 main scope = 단일 테이블 정확성
- (B) 추가: Toy 검증으로 multi-table 일반화 가능성 *입증*
- Limitation 4 갱신: "단일 → 멀티 일반화는 Toy 검증으로 일부 입증, 정식 multi-table benchmarking 은 future work"

자문 메일 (지도교수) 의 자문 사항 (바) Future work positioning 에 본 결과 반영 예정.

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:05 KST
**기반**: 5/5 회의록 옵션 (B) + 5/7 사용자 결정 (본 연구 마무리 단계)
