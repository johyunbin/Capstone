import sys
sys.path.insert(0, "cache/rq3")
sys.path.insert(0, "_internal/scripts")
import numpy as np
v = np.random.RandomState(0).randn(2000, 16).astype(np.float32)
from run_ensemble_4kang_adaptive import fit_assign_base
KEY = "fit_assign_elapsed_s"
for m in ["minibatch", "gmm", "faiss_ivf", "reservoir", "pca1d", "lsh", "sobol"]:
    try:
        sids, diag = fit_assign_base(m, v, learn_frac=0.1, learn_seed=42)
        t = diag[KEY]
        print(f"OK {m:10s} sids={sids.shape} unique={len(set(sids))} t={t}s")
    except Exception as e:
        msg = str(e)[:140]
        tn = type(e).__name__
        print(f"FAIL {m:10s} {tn}: {msg}")
