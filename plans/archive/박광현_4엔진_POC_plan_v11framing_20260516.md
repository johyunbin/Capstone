# 박광현 input 4 — 4 엔진 통합 POC plan (v11 framing base)

작성: 2026-05-16 KST
base: `_internal/records/kakaotalk/20260515_박광현미팅.md` (input 4: 엔진 통합 가능성) + narrative v5 (4 type + dynamic method selection axis) + prompt v11 framing (sample selection cross-engine 일반화)
position: 5/27 발표 후 → 6/11 보고서 future work + post-narrative direction

---

## § 1. 영역 + 목적

박광현 5/15 input 4 ("다이나믹 방식 실제 엔진에 넣어서 활용") 영역 직접 대응. 본 연구 1352 file 측정 portfolio 영역 PostgreSQL pgvector single engine 한정 evidence 만 확보 — sample selection 영역 method 우위가 다른 vector engine 영역 일반화 가능 여부 미검증. 4 엔진 cross-engine consistency 확인이 본 연구 paired Δ% 결과 영역 generalization scope 영역 결정.

목적 3 영역:
1. 사용 16 method (Pareto Top 5 + paradigm anchor) 영역 4 엔진 별 paired Δ% 일관성 정량 검증
2. cross-engine ranking 일관성 (Pareto Top 5 method 가 4 엔진 모두 best 5 진입 여부) 검증
3. engine-specific best method 발견 시 → 4 type × engine matrix 영역 selection axis 확장

---

## § 2. 4 엔진 architecture

| 엔진 | type | index | range query 지원 | rationale |
|---|---|---|---|---|
| **PostgreSQL pgvector** | row-store + extension | HNSW / IVFFlat | ✓ (현재 기본) | 본 연구 1352 file base, paper §V-B Bernoulli 구현 reference |
| **DuckDB** | col-store OLAP | HNSW (USEARCH ext) | ✓ ECQO 영역 paper §V-A anchor | Exqutor paper main result 영역 ECQO 검증 엔진, OLAP 영역 sample selection 통합 가능성 |
| **Faiss** | in-memory library | IVF + HNSW + PQ | ✗ (top-k only, range = post-filter) | production reference (Meta), in-memory 환경 영역 sample selection latency baseline |
| **Qdrant** | production vector DB | HNSW + payload filter | ✓ (filter + score threshold) | filter-first 영역 production-grade engine, real-world 영역 selectivity-aware planning case |

4 엔진 영역 차이 axis 3 영역:
- **storage layout**: row (pgvector) / column (DuckDB) / in-memory (Faiss) / segment-based (Qdrant)
- **range query mechanism**: native SQL range (pgvector/DuckDB) / post-filter (Faiss) / payload filter (Qdrant)
- **planner integration**: SQL planner 영역 hint (pgvector/DuckDB) / API call 영역 manual (Faiss/Qdrant)

---

## § 3. RQ4 cross-engine 일반화 hypothesis

**RQ4**: 본 연구 paired Δ% 결과 (CaseB < CaseA 92.5%, 4 type × dynamic method selection axis) 가 PostgreSQL pgvector 외 3 엔진 (DuckDB / Faiss / Qdrant) 영역 일관 재현되는가?

3 sub-hypothesis:
- **H4.1 (paired Δ% sign)**: CaseB < CaseA 영역 sign 영역 4 엔진 모두 retain (rate ≥ 80%)
- **H4.2 (Pareto Top 5 ranking)**: sparse_rp / chao_weighted / hilbert_real / pca1d / neuram 영역 Top 5 ranking 영역 4 엔진 별 retain (Spearman ρ ≥ 0.7)
- **H4.3 (4 type best method)**: type 별 best method (sparse_rp small / hilbert_real large multi 등) 영역 4 엔진 별 일관성 retain

H4.1 ≥ 80% 일관 → cross-engine 일반화 ✓ (본 연구 결과 broadly applicable). H4.2 retain → method ranking universal. H4.3 retain → 4 type axis 영역 cross-engine 안정.

---

## § 4. 영역 method (4 step)

### Step 1. 4 엔진 wrapper interface (sample selection abstract API)

공통 abstract 영역:

```python
class SampleSelector(ABC):
    @abstractmethod
    def fit(self, X: np.ndarray, K: int) -> None: ...
    @abstractmethod
    def select_indices(self, n_samples: int) -> np.ndarray: ...

class EngineAdapter(ABC):
    @abstractmethod
    def setup_table(self, X: np.ndarray, ids: np.ndarray) -> None: ...
    @abstractmethod
    def range_query(self, q: np.ndarray, radius: float) -> int: ...  # cardinality
    @abstractmethod
    def estimate_with_sampling(self, q: np.ndarray, radius: float,
                               selector: SampleSelector, n_samples: int) -> int: ...
```

엔진 별 4 adapter 영역: `PgvectorAdapter` / `DuckDBAdapter` / `FaissAdapter` / `QdrantAdapter`.

### Step 2. 사용 16 sample selection method 영역 4 엔진 별 implementation

본 연구 사용 16 method 영역 그대로 4 엔진 적용. method 영역 fit + select_indices 영역 abstract API 영역 구현 — 엔진 영역 무관 reusable. 엔진 별 difference 영역 sample 영역 query mechanism 만 (range query API).

implementation 영역 핵심 challenge 3 영역:
- **Faiss**: native range query 영역 X → top-k 영역 over-fetch 후 post-filter (radius < score threshold)
- **Qdrant**: payload filter 영역 stratified sampling 영역 manual partition 필요
- **DuckDB**: USEARCH HNSW ext 영역 range query API 영역 verbose ANN scan 영역 wrap

### Step 3. paired Δ% 4 엔진 cross-engine consistency 검증

각 엔진 별 본 연구 동일 protocol (B1 baseline + CaseA mode + CaseB ensemble) 영역 측정:
- cells: 4 type × 1-2 dataset = 약 5-7 cells
- methods: Pareto Top 5 + paradigm anchor 4 = 9 methods
- modes: B1 + CaseA + CaseB = 3 modes
- trials: 10 trial × seed
- 측정량: 7 cells × 9 method × 3 mode × 10 trial × 4 engine = **약 7560 file**

cross-engine consistency metric:
- **paired Δ% sign retention**: 4 엔진 별 CaseB < CaseA rate
- **Δ% magnitude correlation**: 엔진 쌍 별 Pearson r (pgvector vs DuckDB / pgvector vs Faiss / pgvector vs Qdrant)

### Step 4. Pareto Top 5 영역 4 엔진 별 best method ranking 일관성

각 엔진 별 method × cell mean Δ% rank → Spearman ρ (pgvector base 대비):
- ρ ≥ 0.9: 강력 일관 → 본 연구 ranking universal
- 0.7 ≤ ρ < 0.9: 중간 일관 → 본 연구 ranking 영역 broadly applicable
- ρ < 0.7: weak → engine-specific best method 분화 → 4 type × engine matrix 영역 selection axis 확장 필요

추가 deliverable: 4 엔진 별 best method matrix table (Type 1-4 × engine 4 = 16 cell).

---

## § 5. ETA + timeline (5/29 ~ 6/7 sprint)

총 10일 sprint 영역 4 phase 영역.

| Phase | 기간 | 영역 |
|---|---|---|
| Phase 1 | 5/29 ~ 5/31 (3d) | wrapper interface 영역 abstract API 설계 + 4 engine adapter 영역 PostgreSQL pgvector 영역 reference implementation |
| Phase 2 | 6/1 ~ 6/3 (3d) | DuckDB + Faiss + Qdrant adapter 영역 구현 + sample selection 16 method 영역 4 engine 영역 cross-validate (single dataset DEEP sf=10) |
| Phase 3 | 6/4 ~ 6/6 (3d) | 4 type × 9 method × 3 mode × 10 trial × 4 engine 영역 measurement (서버 약 30-50h) |
| Phase 4 | 6/7 (1d) | analysis + cross-engine consistency table + ranking matrix + 6/11 보고서 future work § 통합 |

server time 추정: Phase 1-2 dev ~ 30h (사용자 + Claude pair) + Phase 3 measurement ~ 40h server = **70h total**.

5/27 발표 본 연구 narrative 영역 영향 X (POC 영역 post-narrative future work 영역). 6/11 보고서 § future work 영역 POC 결과 통합 — Pilot result (single engine subset) 영역 가능 시 본문 통합, 미완 시 future work 명시.

---

## § 6. risk + mitigation

| risk | impact | mitigation |
|---|---|---|
| **R1**: Faiss native range query 영역 X | medium | top-k over-fetch (k=2N) + post-filter, latency overhead 명시 |
| **R2**: Qdrant payload stratified partition 영역 manual cost 높음 | medium | partition 영역 pre-compute + cache, query time overhead 영역 분리 측정 |
| **R3**: DuckDB USEARCH ext 영역 production-readiness 낮음 | high | DuckDB ext 영역 fallback = USEARCH-direct API + DuckDB SQL 영역 separate measurement |
| **R4**: 4 engine 영역 measurement 영역 server resource 영역 동시 X | medium | engine 별 sequential 측정 + tmux session 분리, 각 engine 영역 독립 verify |
| **R5**: H4.1-H4.3 영역 cross-engine consistency 영역 weak | low (목적 영역 검증 자체 가치) | weak 결과 = engine-specific best method 발견 영역 contribution → 4 type × engine matrix 영역 axis 확장 |
| **R6**: 6/7 deadline 영역 Phase 3 measurement 영역 미완 | high | Phase 3 영역 단축 = single dataset (DEEP sf=10) × 4 engine 영역 pilot 만 → 6/11 보고서 future work 영역 통합, full sweep 영역 post-6/11 |

---

## § 7. 박광현 자문 요청 사항 (3 옵션)

5/22 박광현 weekly review 영역 자문 요청 옵션 3 영역. 사용자 영역 1 옵션 선택 후 진행:

**Option A (보수)**: 본 연구 narrative v5 영역 5/27 발표 + 6/11 보고서 base 영역 유지 + 4 engine POC 영역 6/11 보고서 § future work 영역 plan 만 명시 (실측 X). 안전 + scope contained, narrative 영역 영향 X.

**Option B (균형, 추천)**: 5/29 ~ 6/7 sprint 영역 4 engine pilot (single dataset DEEP sf=10 × 4 engine × Pareto Top 5) 영역 측정 → 6/11 보고서 § future work 영역 pilot result 영역 통합. cross-engine consistency 영역 first evidence 확보, scope manageable.

**Option C (적극)**: 5/29 ~ 6/7 sprint 영역 4 engine full sweep (Step 3 영역 7560 file) → 6/11 보고서 § 5.x 영역 RQ4 영역 본문 통합. cross-engine 일반화 영역 본문-grade evidence, 단 Phase 3 server time 영역 risk 높음 (R6).

자문 영역 핵심 question 3 영역:
1. RQ4 cross-engine 영역 본 연구 narrative scope 영역 통합 시점 (6/11 본문 vs future work)?
2. 4 engine 영역 priority (DuckDB / Faiss / Qdrant 中 1-2 영역 만 우선 시 어느 영역)?
3. cross-engine consistency 영역 weak (H4.1 < 80%) 결과 영역 narrative reframing 영역 (engine-specific best method matrix 영역 contribution) 영역 박광현 의견?

---

## 8. 관련 file

- narrative v5 base: `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v5_*.md`
- 추가 측정 plan v5: `plans/추가측정plan_v5_narrative_20260515_2115.md` § 3 (POC 영역 outline)
- 박광현 input 6 항목: `_internal/records/kakaotalk/20260515_박광현미팅.md`
- prompt v11 framing: 사용자 5/16 영역 `prompt v11`
- 6/11 보고서 outline v5: `plans/6_11_보고서/6_11_보고서_outline_v5_update_20260515_2130.md`
