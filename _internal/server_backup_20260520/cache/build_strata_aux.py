#!/usr/bin/env python3
"""Build separate strata_aux table from NPY (bypass slow UPDATE on partsupp_*).
Usage: python3 build_strata_aux.py <table>
  e.g.  python3 build_strata_aux.py partsupp_deep_10
"""
import sys, time
import numpy as np
import psycopg

table = sys.argv[1]
NPY_DIR = "/mnt/hdd0/home/capstone2026/cache/rq1"
pks = np.load(f"{NPY_DIR}/{table}_pks.npy")
strata = np.load(f"{NPY_DIR}/{table}_strata.npy")
print(f"[strata_aux] {table}: {len(pks):,} rows, {strata.max()+1} strata")

aux = f"{table}_strata_aux"
with psycopg.connect(host="/tmp", port=55435, dbname="wns41559", user="wns41559", autocommit=True) as c:
    cu = c.cursor()
    cu.execute(f"DROP TABLE IF EXISTS {aux}")
    cu.execute(f"CREATE TABLE {aux} (ps_partkey BIGINT, ps_suppkey BIGINT, stratum_id SMALLINT)")
    t0 = time.time()
    with cu.copy(f"COPY {aux} (ps_partkey, ps_suppkey, stratum_id) FROM STDIN") as copy:
        for i in range(len(pks)):
            copy.write_row((int(pks[i,0]), int(pks[i,1]), int(strata[i])))
    cu.execute(f"CREATE INDEX ON {aux} (stratum_id)")
    cu.execute(f"CREATE INDEX ON {aux} (ps_partkey, ps_suppkey)")
    print(f"[strata_aux] {aux}: COPY+INDEX done in {time.time()-t0:.1f}s")
