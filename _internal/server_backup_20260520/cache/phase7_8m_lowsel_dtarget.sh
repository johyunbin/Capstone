#!/bin/bash
# 8M low-sel D_target — hook off, sel∈{0.01, 0.05} 측정, hook on
# 2026-05-07 W2 sprint — DEEP 8M sel 5단계 확장
set -e

PGVEC_DIR="/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector"
PG_BIN="/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin"
DATA_DIR="/mnt/hdd0/home/capstone2026/exqutor_sf10"
CACHE="/mnt/hdd0/home/capstone2026/cache/rq1"
LOG="/mnt/hdd0/home/capstone2026/log"

ts() { date '+%H:%M:%S'; }

echo "[$(ts)] === 8M low-sel D_target 측정 시작 ==="

echo "[$(ts)] 1/7 vector.c 백업"
cp "$PGVEC_DIR/src/vector.c" "$PGVEC_DIR/src/vector.c.bak.lowsel_$(date +%Y%m%d_%H%M%S)"

echo "[$(ts)] 2/7 hook 비활성화 (>= 1 → > 2)"
sed -i 's/if (table_count >= 1)/if (table_count > 2)/' "$PGVEC_DIR/src/vector.c"
grep 'table_count >' "$PGVEC_DIR/src/vector.c" | head -3

echo "[$(ts)] 3/7 pgvector 재빌드"
cd "$PGVEC_DIR"
make PG_CONFIG="$PG_BIN/pg_config" -j4 > /dev/null 2>&1
make PG_CONFIG="$PG_BIN/pg_config" install > /dev/null 2>&1
echo "  빌드 완료: $(md5sum $PG_BIN/../lib/postgresql/vector.so | cut -d' ' -f1)"

echo "[$(ts)] 4/7 PG 55436 재시작"
$PG_BIN/pg_ctl restart -D "$DATA_DIR" -l "$LOG/postgres_55436.log" -w -t 30

echo "[$(ts)] 5/7 low-sel D_target 측정 (sel=0.01, 0.05 × 100 queries)"
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

results = {0.01: [], 0.05: []}
t0 = time.time()
with conn.cursor() as cur:
    for sel_target in [0.01, 0.05]:
        print(f'[{kst()}] === sel_target = {sel_target} ===')
        ts0 = time.time()
        for qid in range(100):
            emb = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)
            cur.execute('SELECT setseed(0.42)')
            cur.execute(f"""
            SELECT percentile_cont({sel_target}) WITHIN GROUP (
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
            results[sel_target].append({
                'query_id': qid,
                'D_target_8m': d_8m,
                'true_card_8m': true_card,
                'actual_sel_8m': actual_sel,
            })
            if (qid + 1) % 20 == 0:
                print(f'[{kst()}] sel={sel_target} q{qid+1}/100 ({time.time()-ts0:.0f}s) sel_act={actual_sel:.4f}')
        sels = [r['actual_sel_8m'] for r in results[sel_target]]
        print(f'[{kst()}] sel_target={sel_target}: actual_sel mean={np.mean(sels):.4f} std={np.std(sels):.4f}')

conn.close()

out = f'{CACHE}/phase7_8m_dtarget_lowsel.json'
with open(out, 'w') as f:
    json.dump({
        'total_8m': total,
        'n_queries': 100,
        'sel_targets': [0.01, 0.05],
        'results': {str(k): v for k, v in results.items()},
        'elapsed_s': round(time.time()-t0, 1),
    }, f, indent=2)
print(f'[{kst()}] saved {out}')
PYEOF

echo "[$(ts)] 6/7 hook 복원 (> 2 → >= 1)"
sed -i 's/if (table_count > 2)/if (table_count >= 1)/' "$PGVEC_DIR/src/vector.c"
cd "$PGVEC_DIR"
make PG_CONFIG="$PG_BIN/pg_config" -j4 > /dev/null 2>&1
make PG_CONFIG="$PG_BIN/pg_config" install > /dev/null 2>&1
echo "  복원 완료: $(md5sum $PG_BIN/../lib/postgresql/vector.so | cut -d' ' -f1)"

echo "[$(ts)] 7/7 PG 55436 최종 재시작"
$PG_BIN/pg_ctl restart -D "$DATA_DIR" -l "$LOG/postgres_55436.log" -w -t 30

echo "[$(ts)] === D_target 측정 완료 ==="
