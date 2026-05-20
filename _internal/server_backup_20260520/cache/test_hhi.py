import numpy as np, pyarrow.parquet as pq, psycopg

CACHE = "/mnt/hdd0/home/capstone2026/cache/rq1"
qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()
qs = pq.read_table(f"{CACHE}/query_selectivity.parquet").to_pandas()

row = qs[(qs["selectivity"]==0.010) & (qs["query_id"]==0)].iloc[0]
D = float(row["D_target"])
emb = np.asarray(qp.iloc[0]["embedding"], dtype=np.float32)
vec_str = "[" + ",".join("%.7f" % float(x) for x in emb) + "]"

conn = psycopg.connect(host="/tmp", port=55436, user="wns41559", dbname="wns41559", autocommit=True)
cur = conn.cursor()
cur.execute("SET vector.update_sample_size = off")
cur.execute("SET vector.sample_size = 1")

sql = f"SELECT stratum_id, count(*) FROM partsupp_deep_10_subset_1m WHERE (ps_embedding <-> '{vec_str}'::vector) < {D} GROUP BY stratum_id ORDER BY stratum_id"
cur.execute(sql)
rows = cur.fetchall()
print(f"Result: {len(rows)} strata")
total = sum(r[1] for r in rows)
print(f"Total matches: {total} (expected ~10000)")
for r in rows[:5]:
    print(f"  stratum {r[0]}: {r[1]} rows")
conn.close()
