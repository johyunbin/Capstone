# 통합 manager 세션 인계 v5 — 5/7 17:45 KST (Exqutor full match + K-aware redesign)

> **이전 세션**: 5/7 15:50~17:45 KST, Opus 4.7 1M.
> **인계 목적**: 5/7 오후 사용자 결정사항 — Exqutor 5×3 matrix full match + K-aware baseline 통합 진행 인계.

---

## 1. 사용자 핵심 결정사항 (5/7 16:00~17:30)

1. **Exqutor 5 dataset × 3 scale 완전 대조** — DEEP/SIFT/SSN++/YFCC/WIKI × sf1(800K)/sf10(8M)/sf100(80M) = 15 cell.
2. **TPC-H natural baseline 통일** — 기존 BIGANN raw extract (customer_sift_*_subset, partsupp_deep_*_subset_1m) 등 우리가 만든 인공 데이터는 appendix 로 보존, primary 매트릭스는 partsupp_* (TPC-H natural) 만.
3. **행 수 정확 일치 X** — 0.04% 자연 변동 용인. LIMIT 강제 X.
4. **YFCC sf100 가능 경로 발견** — `https://comp21storage.z5.web.core.windows.net/yfcc100m_images/yfcc100m_vecs.fbin` (505 GB, 98.7M × 1280d float32 CLIP). 다운로드 → PCA 1280→192 → extract 800K/8M/80M. 다운로드 진행 중 (tmux `yfcc_dl`, ETA ~12h).
5. **WIKI 전부 자체 extract** — wiki-all raw 사용, partsupp_wiki_1/10/100 적재 (768d). 행 수 강제 800K/8M/80M.
6. **K-aware baseline 재설계** — K=20 단일 default 부족 (특히 WIKI 768d, SSN++ 256d). K-sweep K=10/20/50/100/200 → K_optimal per dataset 도출.
7. **30 method 비교 narrative** — 기존 22 + 추가 8 (DBSCAN/OPTICS/Agglomerative/Hierarchical KMeans/Faiss IVF/PCA-KMeans/KMeans++/Coresets) → tier 1-4 elimination → 4-6 winner 채택.
8. **VBASE/DuckDB/pgvector fixed-sampling baselines** RQ1 추가.
9. **멀티벡터 + 멀티 테이블 자연 조인 진행** — partsupp_deep_sift_10, partsupp_deep_wiki_10, partsupp_deep_10 ⨝ part_wiki_10 등 (자체 toy_multi_join 은 후순위).
10. **Subset-training pattern** for 80M slow methods (HDBSCAN/spectral/birch).
11. **백그라운드 + 알림 패턴** — tmux + flag + watchdog 패턴.

---

## 2. 현재 진행 상태 (5/7 17:45 KST)

### 활성 tmux 세션 (8개)
```
yfcc_dl                # YFCC 505GB 다운로드, ETA ~12h, 1% 진행 (10GB/505GB)
sf1_DEEP/SIFT/SSN      # sf1 prep + K-sweep + 18 methods, ETA ~3-5min
sf10_DEEP/SIFT/SSN     # sf10 prep + K-sweep + 16 methods, ETA ~20-30min
post_8m                # legacy (W2/W3 잔존, 무시 OK)
```

### 검증 완료 (works end-to-end)
- ✅ NPY-only mode (PG UPDATE 우회) — UPDATE 26분+ → 1분
- ✅ Composite PK 처리 (ps_partkey, ps_suppkey)
- ✅ rq2_alloc_python.py PORT 55435 override
- ✅ chain_unified.py end-to-end (5,000 rows/3.6s 검증)
- ✅ DEEP_sf1 prep + RQ1 km20 측정 검증

### 검증 산출 (이미 PG/NPY/parquet 존재)
- partsupp_deep_1 + NPY (vectors/pks/strata) + querypool parquet × 2
- rq1_DEEP_sf1_km20.parquet (5000 rows)
- rq3_DEEP_sf1_random20.parquet
- partsupp_sift_1, partsupp_fb_1 NPY (sf1 SIFT/SSN++ prep 완료)
- rq1_SIFT_sf1_km20.parquet, rq1_SSN_sf1_km20.parquet

---

## 3. 코드 인프라 (이번 세션 작성 산출)

### 로컬 (`/Users/hyunbin/Capstone/_internal/scripts/`)
- `prepare_cell.py` (13.7 KB) — 통합 prep 스크립트 (composite PK + NPY-only mode)
- `chain_unified.py` (5.5 KB) — RQ1+RQ2+RQ3 dispatcher (`rq1_km20`, `rq1_km_k_N`, `rq3_at_k_N_method`, `rq3_method` 지원)
- `build_wiki.py` (6 KB) — WIKI raw → partsupp_wiki_{1,10,100} extract + 적재
- `build_yfcc.py` (7 KB) — YFCC 1280d → PCA 192d → partsupp_yfcc_pca_{1,10,100} extract
- `run_cell_full.sh` — bash driver: prep → K-sweep × 5 → RQ3 random20 → RQ2 5mode → 18 methods

### 서버 (`/mnt/hdd0/home/capstone2026/cache/`)
- prepare_cell.py, build_wiki.py, build_yfcc.py, run_cell_full.sh (모두 업로드 완료)
- `rq3/chain_unified.py` (업로드 완료)
- `rq3/_measure_common.py` 패치 — NPY-only fast path 추가 (`{table}_strata.npy` exist 시 PG fetch 우회)

### 매핑 (CELLS dict, prepare_cell.py)
```python
CELLS = {
  ('DEEP', 1):   {'table':'partsupp_deep_1',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':96},
  ('DEEP', 10):  {'table':'partsupp_deep_10',  ...},
  ('DEEP', 100): {'table':'partsupp_deep_100', ...},
  ('SIFT', 1):   {'table':'partsupp_sift_1',   ..., 'dim':128},
  ('SIFT', 10):  ..., ('SIFT', 100): ...,
  ('SSN',  1):   {'table':'partsupp_fb_1',     ..., 'dim':256},
  ('SSN',  10):  ..., ('SSN', 100): ...,
  ('YFCC', 10):  {'table':'partsupp_yfcc_10',  ..., 'dim':192},  # 기존 BigANN release, appendix
  ('WIKI', 10):  {'table':'part_wiki_10',      ..., 'dim':768},  # 기존 TPC-H natural part, appendix
}
# 자체 extract 후 추가 필요: ('WIKI', 1/10/100) → partsupp_wiki_*, ('YFCC', 1/10/100) → partsupp_yfcc_pca_*
```

---

## 4. 다음 세션 즉시 actions

### 알림 받으면
1. **sf1 6 batch 완료** (~3-5min after launch 17:42) → 산출 verify (~22 parquet × 3 cells = 66 parquet)
2. **sf10 6 batch 완료** (~20-30min) → 산출 verify
3. **YFCC 다운로드 완료** (~12h, 5/8 새벽 ETA) → `bash run_cell_full.sh ...` 으로 build_yfcc.py 호출 → PCA fit + extract sf1/sf10/sf100

### 즉시 진행 (백그라운드 batch 와 무관)

#### A. WIKI extract sf1/sf10 (sf100 은 80M 추출, 시간 큼)
```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && \
  tmux new -d -s wiki_sf1 'python3 build_wiki.py --sf 1 2>&1 | tee /tmp/wiki_sf1.log; touch /tmp/wiki_sf1_done.flag' && \
  tmux new -d -s wiki_sf10 'python3 build_wiki.py --sf 10 2>&1 | tee /tmp/wiki_sf10.log; touch /tmp/wiki_sf10_done.flag'"
```
적재 후 prepare_cell.py CELLS dict 에 추가 + run_cell_full.sh 실행.

#### B. sf100 prep + chain (메모리 사용 큼, 직렬 권장)
sf10 batch 완료 후 자동으로 sf100 launch:
```bash
for DS in DEEP SIFT SSN; do
  tmux new -d -s sf100_${DS} "bash run_cell_full.sh ${DS} 100"
done
```

#### C. K_optimal 분석 driver
sf1+sf10 K-sweep 결과로 dataset × scale 별 K_optimal 도출.
산출물: `experiments/results/rq1_motivation/k_optimal_per_dataset.csv`
narrative: "K=20 default, K_optimal per dataset" 분리 narrative.

#### D. 멀티벡터 + 멀티 테이블 측정
- partsupp_deep_sift_10 (DEEP+SIFT 한 행 두 임베딩)
- partsupp_deep_wiki_10 (DEEP+WIKI)
- partsupp_deep_10 ⨝ part_wiki_10 (TPC-H natural join + 두 임베딩)

측정 adapter 필요 — `chain_unified.py` 에 multi-vector / join stage 추가.

#### E. 추가 8 method runner
`/mnt/hdd0/home/capstone2026/cache/rq3/run_dbscan.py`, `run_optics.py`, `run_agglomerative.py`, `run_hierarchical_kmeans.py`, `run_faiss_ivf.py`, `run_pca_kmeans.py`, `run_kmeans_pp.py`, `run_coresets.py` 작성 필요.

기존 22 + 8 = 30 method, tier 1-4 elimination narrative.

#### F. RQ1 baseline VBASE/DuckDB/pgvector
fixed-sampling rate (33%, 50%, 100%) 비교 baseline. 별도 runner 필요.

#### G. master.md update
5×3 K-aware matrix narrative + Exqutor full match + 30 method elimination 추가.

---

## 5. 시행착오 학습 (다음 세션 주의)

1. **PG backend 종료** — `pkill -9` 가 아닌 `pg_terminate_backend(pid)` 사용. SIGKILL 시 PG recovery mode 진입.
2. **HNSW 인덱스 + UPDATE** — 80M 테이블에 stratum_id UPDATE 시 HNSW 재인덱싱으로 매우 느림. NPY-only mode 로 PG UPDATE 우회.
3. **multi-line SSH bash escape** — 변수 escape 복잡. .sh 파일을 SCP 후 `tmux new -d -s X 'bash /path/script.sh ARGS'` 패턴이 안전.
4. **Composite PK** — partsupp 테이블은 (ps_partkey, ps_suppkey) 복합키. 단일 PK 가정 시 stratum 중복 덮어쓰기 발생.
5. **rq2_alloc_python.py PORT** — 자체 PORT=55436 (exqutor) 하드코딩. chain_unified 에서 `rq2.PORT = mc.PORT` override 필수. (수정 완료)
6. **sf1 partsupp 행 수 800K vs 800,041** — TPC-H 자연 변동. LIMIT 안 함.

---

## 6. 디스크 / 메모리 예산

- 디스크 1.9 TB free / 13 TB total (85% used)
- YFCC 505 GB 다운로드 + PCA 결과 ~17 GB 후 원본 삭제
- WIKI 80M extract = 246 GB NPY 영구 (디스크 부담 큰 단일 항목)
- sf100 NPY 캐시 합 ~150 GB (DEEP 30 + SIFT 41 + SSN 82) + WIKI 246 = 396 GB
- 다운로드 + 80M NPY peak ~ 900 GB (+ 1.0 TB 잔여)
- 메모리 1 TB RAM, 80M × 768d (WIKI) = 246 GB → 1 cell 로드 가능, multi-cell parallel 시 주의

---

## 7. Read 필수 (다음 세션 진입)

- 본 doc (`_internal/handoff_v5_session_20260507_1745.md`)
- `experiments/results/RQ1_RQ2_RQ3_종합_master.md` (W3 종합)
- `_internal/handoff_v4_session_20260507_1550.md` (이전 세션)
- `submission/_drafts/속도는벡터_5월8일회의_v2_supplement_20260507.md` (5/8 회의 자료)
- `_internal/scripts/prepare_cell.py` + `chain_unified.py` + `run_cell_full.sh` + `build_wiki.py` + `build_yfcc.py`

---

**작성**: Claude Opus 4.7 1M, 통합 manager session, 2026-05-07 17:45 KST
**다음 session 시작 prompt**: 본 doc + master.md read → 알림 처리 + 즉시 actions A~G 순차 진행
