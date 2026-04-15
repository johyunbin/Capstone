#!/bin/bash
# Phase 7 D_target 재계산 — hook 임시 원복 + 재빌드 + 측정 + 복원
# 서버에서 직접 실행: bash phase7_dtarget_recalc_full.sh
set -e

PGVEC_DIR="/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector"
PG_BIN="/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin"
DATA_DIR_55436="/mnt/hdd0/home/capstone2026/exqutor_sf10"
CACHE="/mnt/hdd0/home/capstone2026/cache/rq1"
LOG="/mnt/hdd0/home/capstone2026/log"

echo "[$(date '+%H:%M:%S')] === Phase 7 D_target 재계산 시작 ==="

# 1. 현재 vector.c 백업
echo "[$(date '+%H:%M:%S')] 1/7 vector.c 백업"
cp "$PGVEC_DIR/src/vector.c" "$PGVEC_DIR/src/vector.c.bak.dtarget_$(date +%Y%m%d_%H%M%S)"

# 2. hook 비활성화 (table_count >= 1 → table_count > 2)
echo "[$(date '+%H:%M:%S')] 2/7 hook 비활성화 (>= 1 → > 2)"
sed -i 's/if (table_count >= 1)/if (table_count > 2)/' "$PGVEC_DIR/src/vector.c"
grep "table_count" "$PGVEC_DIR/src/vector.c" | head -3

# 3. 재빌드
echo "[$(date '+%H:%M:%S')] 3/7 pgvector 재빌드"
cd "$PGVEC_DIR"
make PG_CONFIG="$PG_BIN/../lib/../bin/pg_config" -j4 > /dev/null 2>&1
make PG_CONFIG="$PG_BIN/../lib/../bin/pg_config" install > /dev/null 2>&1
echo "  빌드 완료: $(md5sum $PG_BIN/../lib/postgresql/vector.so | cut -d' ' -f1)"

# 4. PG 55436 재시작
echo "[$(date '+%H:%M:%S')] 4/7 PG 55436 재시작"
$PG_BIN/pg_ctl restart -D "$DATA_DIR_55436" -l "$LOG/postgres_55436.log" -w -t 30

# 5. D_target 측정
echo "[$(date '+%H:%M:%S')] 5/7 D_target 측정 (100 queries)"
python3 << 'PYEOF'
import json, time, numpy as np, psycopg, pyarrow.parquet as pq
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'
def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')
def emb_to_pgvec(emb):
    return '[' + ','.join(f'{float(x):.7f}' for x in emb) + ']'

qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
conn = psycopg.connect(host='/tmp', port=55436, user='wns41559', dbname='wns41559', autocommit=True)

with conn.cursor() as cur:
    cur.execute('SELECT count(*) FROM partsupp_deep_10_phase7_8m_subset')
    total = cur.fetchone()[0]
    print(f'[{kst()}] 8M rows: {total} (hook disabled)')

results = []
t0 = time.time()
with conn.cursor() as cur:
    for qid in range(100):
        emb = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        cur.execute(f'SELECT setseed(0.42)')
        cur.execute(f"""
        SELECT percentile_cont(0.5) WITHIN GROUP (
            ORDER BY (ps_embedding <-> '{vec_str}'::vector)
        ) FROM (
            SELECT ps_embedding FROM partsupp_deep_10_phase7_8m_subset
            TABLESAMPLE BERNOULLI(1)
        ) sub
        """)
        d_8m = float(cur.fetchone()[0])

        cur.execute(f"""
        SELECT count(*) FROM partsupp_deep_10_phase7_8m_subset
        WHERE (ps_embedding <-> '{vec_str}'::vector) < {d_8m}
        """)
        true_card = int(cur.fetchone()[0])
        actual_sel = true_card / total

        results.append({
            'query_id': qid,
            'D_target_8m': d_8m,
            'true_card_8m': true_card,
            'actual_sel_8m': actual_sel,
        })

        if (qid + 1) % 10 == 0:
            print(f'[{kst()}] q{qid+1}/100 ({time.time()-t0:.0f}s) sel={actual_sel:.4f} D={d_8m:.4f}')

conn.close()

sels = [r['actual_sel_8m'] for r in results]
print(f'\n[{kst()}] actual_sel: mean={np.mean(sels):.4f} std={np.std(sels):.4f}')

out = f'{CACHE}/phase7_8m_dtarget_recalc_clean.json'
with open(out, 'w') as f:
    json.dump({'total_8m': total, 'n_queries': 100, 'results': results,
               'elapsed_s': round(time.time()-t0, 1)}, f, indent=2)
print(f'[{kst()}] saved {out}')
PYEOF

# 6. hook 복원 (table_count > 2 → table_count >= 1)
echo "[$(date '+%H:%M:%S')] 6/7 hook 복원 (> 2 → >= 1)"
sed -i 's/if (table_count > 2)/if (table_count >= 1)/' "$PGVEC_DIR/src/vector.c"
cd "$PGVEC_DIR"
make PG_CONFIG="$PG_BIN/../lib/../bin/pg_config" -j4 > /dev/null 2>&1
make PG_CONFIG="$PG_BIN/../lib/../bin/pg_config" install > /dev/null 2>&1
echo "  복원 완료: $(md5sum $PG_BIN/../lib/postgresql/vector.so | cut -d' ' -f1)"

# 7. PG 55436 재시작
echo "[$(date '+%H:%M:%S')] 7/7 PG 55436 최종 재시작"
$PG_BIN/pg_ctl restart -D "$DATA_DIR_55436" -l "$LOG/postgres_55436.log" -w -t 30

echo "[$(date '+%H:%M:%S')] === 완료 ==="
