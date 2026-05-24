#!/usr/bin/env python3
"""
Single-cell ensemble (Adaptive × 11 method) launcher for FB × SF{1, 10}.

Goal
----
Phase C of the 5/9 plan calls for two new single-cell ensemble runs that the
existing X6/X7 ensemble launches missed:

    rq3_FB_sf1_ensemble_<method>.parquet      (11 files)
    rq3_FB_sf10_ensemble_<method>.parquet     (11 files)

The "FB" cell maps to the existing ``partsupp_fb_<sf>`` tables (256-d image
embeddings) which the rest of the codebase tags as ``SSN`` in
``run_ensemble_4kang_adaptive.py`` (cf. CELLS dict in run_adaptive_sampling.py).
This script only renames outputs from ``SSN`` to ``FB`` so that downstream
analysis (analyze_ensemble.py, single_multi_consistency_*) can address the cell
under both names if needed.

Pattern
-------
Mirrors ``experiments/code/rq3/launch_ensemble_4kang_adaptive.sh`` exactly:

    for sf in (1, 10):
        for method in (hdbscan, minibatch, gmm, hilbert, faiss_ivf,
                       minibatch_partial, reservoir, sparse_rp, pca1d, lsh, sobol):
            python3 run_ensemble_4kang_adaptive.py \\
                --dataset SSN --sf <sf> --base-method <method> \\
                --out-prefix rq3_FB_sf<sf>_ensemble_<method>

Ensemble = base-method stratification + Adaptive Sampling dynamic budget
(Exqutor §V-B Algorithm 1, momentum=0.9, η₀=0.1, α=50, β=1.5, γ=0.99,
period=50, init_N=385, [min,max]=[50,5000]).

Output
------
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_FB_sf<sf>_ensemble_<method>.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_FB_sf<sf>_ensemble_<method>_meta.json

Schema (matches existing rq3_SSN_sf*_ensemble_*.parquet — verified):
    dataset, mode='ensemble_<method>', base_method, selectivity, seed, query_id,
    D_target, true_card, est, q_error, sample_size_used, total_sample_size

CLI
---
    # default — sequential 11 method × 2 sf = 22 runs
    python3 _internal/scripts/build_FB_single_ensemble.py

    # subset
    python3 _internal/scripts/build_FB_single_ensemble.py --sf 10 --methods pca1d sobol

    # plan only — no compute, no DB
    python3 _internal/scripts/build_FB_single_ensemble.py --dry-run

    # background launch (server)
    nohup python3 _internal/scripts/build_FB_single_ensemble.py \\
        > /mnt/hdd0/home/capstone2026/logs/build_FB_single_ensemble_$(date +%Y%m%d_%H%M).log 2>&1 &

References
----------
- experiments/code/rq3/run_ensemble_4kang_adaptive.py  — single ensemble script
- experiments/code/rq3/launch_ensemble_4kang_adaptive.sh — original 4-method launcher
- _internal/scripts/measure_multi_ensemble.py — multi-cell counterpart (reuses
  AdaptiveState + proportional_alloc_dynamic; same hyperparameters as here).
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Paths — server-first, local fallback (dry-run only)
# ---------------------------------------------------------------------------

SERVER_HOME = Path("/mnt/hdd0/home/capstone2026")
SERVER_RQ3_CODE = SERVER_HOME / "cache" / "rq3"
SERVER_OUT_DIR = SERVER_HOME / "cache" / "rq1"
SERVER_LOG_DIR = SERVER_HOME / "logs"

LOCAL_RQ3_CODE = Path("/Users/hyunbin/Capstone/experiments/code/rq3")
LOCAL_OUT_DIR = Path("/Users/hyunbin/Capstone/experiments/results/cache/rq1")
LOCAL_LOG_DIR = Path("/Users/hyunbin/Capstone/_internal/logs")

RQ3_CODE = SERVER_RQ3_CODE if SERVER_RQ3_CODE.exists() else LOCAL_RQ3_CODE
OUT_DIR = SERVER_OUT_DIR if SERVER_OUT_DIR.exists() else LOCAL_OUT_DIR
LOG_DIR = SERVER_LOG_DIR if SERVER_HOME.exists() else LOCAL_LOG_DIR


# ---------------------------------------------------------------------------
# Constants — keep in lock-step with run_ensemble_4kang_adaptive.py
# ---------------------------------------------------------------------------

#: Underlying dataset key in ``CELLS`` (run_adaptive_sampling.py line 91-93).
#: ``SSN`` -> ``partsupp_fb_<sf>`` (256-d FB embeddings). This is the canonical
#: internal name; we re-label outputs to ``FB`` per the 5/9 plan.
INTERNAL_DATASET = "SSN"
EXTERNAL_DATASET = "FB"

SFS: tuple[int, ...] = (1, 10)

#: 11 methods of the 5-paradigm framework (5/8 20:48 user confirm).
#:   P1 Cluster: hdbscan, minibatch, gmm
#:   P2 Spatial: hilbert, faiss_ivf
#:   P3 Streaming: minibatch_partial, reservoir
#:   P4 DimReduction: sparse_rp, pca1d
#:   P5 Quasi-random: lsh, sobol
#: Method names match run_ensemble_4kang_adaptive's --base-method choices when
#: that script is extended to 11 methods (existing rq3_SSN_sf10_ensemble_pca1d.parquet
#: confirms the extension is already deployed on the server).
METHODS_11: tuple[str, ...] = (
    "hdbscan", "minibatch", "gmm",
    "hilbert", "faiss_ivf",
    "minibatch_partial", "reservoir",
    "sparse_rp", "pca1d",
    "lsh", "sobol",
)

PARADIGM_OF: dict[str, str] = {
    "hdbscan": "P1_Cluster", "minibatch": "P1_Cluster", "gmm": "P1_Cluster",
    "hilbert": "P2_Spatial", "faiss_ivf": "P2_Spatial",
    "minibatch_partial": "P3_Streaming", "reservoir": "P3_Streaming",
    "sparse_rp": "P4_DimReduction", "pca1d": "P4_DimReduction",
    "lsh": "P5_Quasi-random", "sobol": "P5_Quasi-random",
}

#: AdaptiveState hyperparameters (Exqutor §VI - production defaults).
ADAPTIVE_HP: dict = {
    "momentum": 0.9, "lr0": 0.1, "alpha": 50.0, "beta": 1.5, "gamma": 0.99,
    "update_period": 50, "min_size": 50, "max_size": 5000,
}

#: Estimated per-run elapsed time in minutes (from existing 4-kang launcher
#: comments + cell-row scaling). Used for resource estimate / logging only.
ELAPSED_MIN_PER_RUN: dict[tuple[int, str], float] = {
    # SF1 baseline ≈ 18 min (HDBSCAN), 9-13 for cheaper methods.
    (1, "hdbscan"):           18,
    (1, "minibatch"):         12,
    (1, "gmm"):               16,
    (1, "hilbert"):           12,
    (1, "faiss_ivf"):         11,
    (1, "minibatch_partial"): 11,
    (1, "reservoir"):          9,
    (1, "sparse_rp"):         11,
    (1, "pca1d"):             10,
    (1, "lsh"):               10,
    (1, "sobol"):             11,
    # SF10 ≈ 6× longer (ratio observed from 4-kang launcher results).
    (10, "hdbscan"):          120,
    (10, "minibatch"):         85,
    (10, "gmm"):              110,
    (10, "hilbert"):           85,
    (10, "faiss_ivf"):         80,
    (10, "minibatch_partial"): 80,
    (10, "reservoir"):         70,
    (10, "sparse_rp"):         80,
    (10, "pca1d"):             75,
    (10, "lsh"):               75,
    (10, "sobol"):             80,
}


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Run plan helpers
# ---------------------------------------------------------------------------

def out_prefix(sf: int, method: str) -> str:
    """Output prefix following the 5/9 plan: ``rq3_FB_sf<sf>_ensemble_<method>``."""
    return f"rq3_{EXTERNAL_DATASET}_sf{sf}_ensemble_{method}"


def out_paths(sf: int, method: str) -> tuple[Path, Path]:
    p = out_prefix(sf, method)
    return OUT_DIR / f"{p}.parquet", OUT_DIR / f"{p}_meta.json"


def build_cmd(sf: int, method: str, *, n_queries: int = 100,
              extra_args: Optional[list[str]] = None) -> list[str]:
    """Build the python invocation for a single (sf × method) ensemble run."""
    cmd = [
        "python3", "-u", str(RQ3_CODE / "run_ensemble_4kang_adaptive.py"),
        "--dataset", INTERNAL_DATASET,            # SSN cell config in CELLS dict
        "--sf", str(sf),
        "--base-method", method,
        "--selectivity", "0.01", "0.05", "0.10", "0.30", "0.50",
        "--seed-start", "0", "--num-seeds", "5",
        "--num-queries", str(n_queries),
        "--out-dir", str(OUT_DIR),
        "--out-prefix", out_prefix(sf, method),  # rq3_FB_sf<sf>_ensemble_<method>
        # AdaptiveState defaults already match ADAPTIVE_HP, but pin them
        # explicitly so the meta.json is unambiguous.
        "--momentum", str(ADAPTIVE_HP["momentum"]),
        "--lr0", str(ADAPTIVE_HP["lr0"]),
        "--alpha", str(ADAPTIVE_HP["alpha"]),
        "--beta", str(ADAPTIVE_HP["beta"]),
        "--gamma", str(ADAPTIVE_HP["gamma"]),
        "--update-period", str(ADAPTIVE_HP["update_period"]),
        "--min-size", str(ADAPTIVE_HP["min_size"]),
        "--max-size", str(ADAPTIVE_HP["max_size"]),
    ]
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def expected_outputs_present(sf: int, method: str) -> bool:
    pq, meta = out_paths(sf, method)
    return pq.exists() and meta.exists()


def estimate_minutes(sfs: list[int], methods: list[str]) -> float:
    return sum(
        ELAPSED_MIN_PER_RUN.get((sf, m), 60.0)
        for sf in sfs for m in methods
    )


# ---------------------------------------------------------------------------
# Resource estimate / dry-run report
# ---------------------------------------------------------------------------

def print_resource_table(sfs: list[int], methods: list[str]) -> None:
    print(f"\n[{kst()}] === resource estimate ===")
    print(f"  {'sf':<3} {'method':<22} {'paradigm':<18} {'~min':>6}  output")
    total = 0.0
    for sf in sfs:
        for m in methods:
            est_min = ELAPSED_MIN_PER_RUN.get((sf, m), 60.0)
            total += est_min
            pq, _ = out_paths(sf, m)
            tag = "exists" if pq.exists() else "TODO"
            print(f"  {sf:<3} {m:<22} {PARADIGM_OF[m]:<18} {est_min:>6.0f}  "
                  f"[{tag:>6}] {pq.name}")
    n = len(sfs) * len(methods)
    print(f"  {'-' * 80}")
    print(f"  TOTAL {n} runs, ~{total:.0f} min sequential = ~{total / 60:.1f} h")
    print(f"  memory: dominated by partsupp_fb_<sf> vector fetch "
          f"(SF1 ≈ 0.8GB, SF10 ≈ 8GB; rest under 2GB)")
    print()


# ---------------------------------------------------------------------------
# Sequential run dispatcher
# ---------------------------------------------------------------------------

def run_one(sf: int, method: str, *, n_queries: int = 100,
            log_dir: Path = LOG_DIR, dry: bool = False,
            force: bool = False) -> dict:
    """Execute a single ensemble run (or print plan when dry=True)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    pq, meta_path = out_paths(sf, method)
    if (not force) and expected_outputs_present(sf, method):
        print(f"[{kst()}] SKIP sf={sf} method={method} — outputs already present")
        return {"sf": sf, "method": method, "status": "skipped",
                "out_parquet": str(pq), "out_meta": str(meta_path)}

    cmd = build_cmd(sf, method, n_queries=n_queries)
    log_path = log_dir / (
        f"build_FB_ensemble_sf{sf}_{method}_"
        f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M')}.log"
    )
    pretty = " ".join(shlex.quote(c) for c in cmd)
    print(f"\n[{kst()}] >>> sf={sf} method={method} ({PARADIGM_OF[method]})")
    print(f"[{kst()}]     log: {log_path}")
    print(f"[{kst()}]     cmd: {pretty}")
    if dry:
        return {"sf": sf, "method": method, "status": "dry",
                "cmd": cmd, "log_path": str(log_path),
                "out_parquet": str(pq), "out_meta": str(meta_path)}

    if not (RQ3_CODE / "run_ensemble_4kang_adaptive.py").exists():
        raise RuntimeError(
            f"run_ensemble_4kang_adaptive.py not found at {RQ3_CODE}; "
            "run on server (165.132.140.240) or pass --dry-run locally"
        )

    t0 = time.time()
    with open(log_path, "wb") as logf:
        proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
    elapsed = time.time() - t0
    status = "ok" if proc.returncode == 0 else "fail"
    print(f"[{kst()}]     end status={status} rc={proc.returncode} "
          f"elapsed={elapsed:.1f}s ({elapsed / 60:.1f}min)")
    return {
        "sf": sf, "method": method, "status": status,
        "rc": proc.returncode, "elapsed_s": round(elapsed, 1),
        "log_path": str(log_path),
        "out_parquet": str(pq), "out_meta": str(meta_path),
    }


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--sf", type=int, choices=list(SFS), nargs="+", default=list(SFS),
                    help="Scale factors to run (default 1 10).")
    ap.add_argument("--methods", nargs="+", choices=list(METHODS_11),
                    default=list(METHODS_11),
                    help="Base methods (default = all 11 paradigm methods).")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--dry-run", action="store_true",
                    help="Print plan + per-run command, no execution.")
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if outputs already exist.")
    args = ap.parse_args()

    print(f"[{kst()}] === build_FB_single_ensemble ===")
    print(f"[{kst()}] RQ3_CODE: {RQ3_CODE}")
    print(f"[{kst()}] OUT_DIR:  {OUT_DIR}")
    print(f"[{kst()}] LOG_DIR:  {LOG_DIR}")
    print(f"[{kst()}] sf={args.sf}  methods={args.methods}")
    print(f"[{kst()}] n_queries={args.n_queries}  force={args.force}")

    print_resource_table(args.sf, args.methods)

    if args.dry_run:
        print(f"[{kst()}] === dry-run ===")
        for sf in args.sf:
            for method in args.methods:
                run_one(sf, method, n_queries=args.n_queries,
                        dry=True, force=args.force)
        print(f"\n[{kst()}] dry-run OK — total "
              f"{len(args.sf) * len(args.methods)} runs planned")
        return

    if not OUT_DIR.exists():
        raise SystemExit(f"OUT_DIR not found: {OUT_DIR} (run on server)")

    t_total = time.time()
    summary: list[dict] = []
    for sf in args.sf:
        for method in args.methods:
            res = run_one(sf, method, n_queries=args.n_queries, force=args.force)
            summary.append(res)

    print(f"\n[{kst()}] === summary ===")
    for s in summary:
        print(f"  sf={s['sf']}  {s['method']:<22}  status={s['status']:<8}  "
              f"out={s.get('out_parquet', '?')}")
    n_ok = sum(1 for s in summary if s["status"] == "ok")
    n_skip = sum(1 for s in summary if s["status"] == "skipped")
    n_fail = sum(1 for s in summary if s["status"] == "fail")
    print(f"[{kst()}] ok={n_ok} skipped={n_skip} fail={n_fail} "
          f"total={time.time() - t_total:.0f}s "
          f"({(time.time() - t_total) / 3600:.2f}h)")

    # Persist a top-level summary alongside the parquet artifacts.
    summary_path = OUT_DIR / (
        f"build_FB_single_ensemble_summary_"
        f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M')}.json"
    )
    try:
        with open(summary_path, "w") as f:
            json.dump({
                "kst": kst(),
                "sf": args.sf, "methods": args.methods,
                "n_queries": args.n_queries,
                "adaptive_hp": ADAPTIVE_HP,
                "internal_dataset": INTERNAL_DATASET,
                "external_dataset": EXTERNAL_DATASET,
                "summary": summary,
            }, f, indent=2, default=str)
        print(f"[{kst()}] summary -> {summary_path}")
    except OSError as exc:
        print(f"[{kst()}] WARN: could not write summary ({exc})")

    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
