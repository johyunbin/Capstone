# Worker I — σ table reproducibility 회복 (DEEP 1M / SIFT 1.5M σ 재계산)

> **임무**: RQ2 딥리뷰 보강 §4 발견 — `compute_stratum_sigma.py` 의 unconditional DELETE 로 DEEP 1M / SIFT 1.5M σ wiped (8M σ만 잔존). conditional DELETE 로 수정 후 재실행 → reproducibility 회복.
> **세션 진입**: 본 핸드오프 첫 read → 서버 script 수정 + 재실행 → 검증 → commit.
> **manager 세션**: 2026-05-07 12:15 KST, Opus 4.7 1M.
> **시간**: 40분 (서버 background, narrative 영향 X — 측정 시점에는 σ valid)

---

## 1. 입력 자료

| 자료 | 위치 |
|---|---|
| 기존 script | `/mnt/hdd0/home/capstone2026/cache/compute_stratum_sigma.py` (서버) |
| RQ2 딥리뷰 보강 (issue 명시) | `_internal/RQ2_딥리뷰_DEEPcluster_확인_20260507.md` §4 |
| 현재 σ table 상태 | DEEP 8M (20 strata × 8M rows × sel=0.1) 만 잔존 |

## 2. 작업 단계

### Step 1 (10분) — script conditional DELETE 로 수정

```bash
ssh capstone "
cd /mnt/hdd0/home/capstone2026/cache
cp compute_stratum_sigma.py compute_stratum_sigma_safe.py
# line 74의 unconditional DELETE FROM 제거
sed -i '/cur.execute(\"DELETE FROM vector_stratum_sigma\")/d' compute_stratum_sigma_safe.py
# for loop 안에 conditional DELETE 추가 (각 dataset 처리 직전)
python3 -c \"
content = open('compute_stratum_sigma_safe.py').read()
target = 'for ds in DATASETS:'
replacement = '''for ds in DATASETS:
        # (safe) per-dataset DELETE only
        cur.execute(\\\"DELETE FROM vector_stratum_sigma WHERE table_name = %s\\\", (ds[\\'table\\'],))
        conn.commit()'''
content = content.replace(target, replacement, 1)
open('compute_stratum_sigma_safe.py', 'w').write(content)
print('saved')
\"
"
```

(또는 vim으로 직접 수정)

### Step 2 (25분) — 서버 background 재실행

```bash
ssh capstone "tmux new -d -s sigma_recompute 'cd /mnt/hdd0/home/capstone2026/cache && python3 -u compute_stratum_sigma_safe.py 2>&1 | tee /tmp/sigma_recompute_20260507.log'"
```

DEEP 1M (1M × 100 query × 20 stratum) + SIFT 1.5M (1.5M × 100 query × 20 stratum) ≈ 25-30분.

### Step 3 (5분) — 결과 검증

```bash
ssh capstone "
PSQL=/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin/psql
\$PSQL -h /tmp -p 55436 -U wns41559 -d wns41559 -c '
  SELECT table_name, COUNT(DISTINCT stratum_id) AS strata, SUM(n_i) AS total_n
  FROM vector_stratum_sigma GROUP BY table_name;'
"
```

기대 결과:
- partsupp_deep_10_subset_1m: 20 strata × 1,000,000 ✓
- customer_sift_10_phase7_noidx_subset: 20 strata × 1,500,000 ✓
- partsupp_deep_10_phase7_8m_subset: 20 strata × 8,000,000 ✓ (보존)

### Step 4 (5분) — commit + push

```bash
# 서버 script 변경 사항 검증 후 로컬에 (필요 시) 동기화
# 현재 본 script는 서버 cache에만 있음. git 추적 X.
# 단, 측정 결과 narrative 영향 없음 (측정 시점에는 σ valid).
# commit message 만 제공:

git commit --allow-empty -m "Worker I: σ table reproducibility 회복 — DEEP 1M / SIFT 1.5M σ 재계산 완료 (compute_stratum_sigma_safe.py 서버 적용, 8M σ 보존)"
git push
```

(또는 본 worker는 서버 작업만 진행, commit X 가능 — manager session 통합 시 narrative 갱신)

## 3. 산출 spec

| 산출 | 위치 | 검증 |
|---|---|---|
| DEEP 1M σ | PG `vector_stratum_sigma` | 20 strata, total_n=1M |
| SIFT 1.5M σ | PG `vector_stratum_sigma` | 20 strata, total_n=1.5M |
| DEEP 8M σ | PG `vector_stratum_sigma` | 20 strata, total_n=8M (보존) |

## 4. 의존성

- 독립 (다른 worker 영향 X)
- W2 권고 사항이지만 narrative 변경 X — RQ2 딥리뷰 보강 §4 의 "측정 시점에는 σ valid, 결과 그대로 valid" 보존

## 5. 본 worker가 만들지 말 것

- compute_stratum_sigma.py 원본 변경 (safe variant 만 작성)
- 8M σ 재계산 (이미 valid, wipe risk)
- master.md narrative 변경 (manager 책임)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:15 KST
**기반**: RQ2 딥리뷰 보강 commit 1267b8a §4
