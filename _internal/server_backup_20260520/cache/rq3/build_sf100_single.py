#!/usr/bin/env python3
"""
SF=100 single-cell artifact builder for DEEP / SIFT / FB(=SSN).

Goal
----
Phase D (Exqutor Fig 4-6 strict match) — produce per-cell NPY + parquet
artifacts for the 3 SF=100 single tables so the existing measurement scripts
(``run_adaptive_sampling.py`` / ``run_ensemble_4kang_adaptive.py`` /
``measure_multi_paradigm.py``) can run unchanged.

This script is a **thin sequential wrapper** around the existing
``cache/prepare_cell.py`` (which already supports SF=100 in its CELLS dict
and handles PG fetch → NPY → KMeans K=20 strata → σ → query pool generation).
We add only what's missing for autonomous overnight operation:

1. **Memory-safety gate** — only proceed when free RAM > 100 GB and swap
   < 80% (server has 25+ live measurement procs at peak).
2. **Sequential cell ordering** (DEEP → SIFT → FB) — avoid concurrent fetches
   that would spike memory by 150 GB+.
3. **Resume support** — skip cells whose NPY + strata + query_pool already
   exist (idempotent re-run).
4. **build_meta.json** — single artifact summarising what was built / when /
   row counts / file sizes (downstream analyze scripts can sanity-check).

Cells (3)
---------
    DEEP_sf100   partsupp_deep_100  (96-d,  80M rows,  30.7 GB vectors)
    SIFT_sf100   partsupp_sift_100  (128-d, 80M rows,  41.0 GB vectors)
    SSN_sf100    partsupp_fb_100    (256-d, 80M rows,  82.0 GB vectors)

External label "FB" maps to internal dataset key "SSN" (per CELLS dict in
``cache/prepare_cell.py`` and ``cache/rq3/run_adaptive_sampling.py``).

Output layout (under ``/mnt/hdd0/home/capstone2026/cache/rq1/``)
---------------------------------------------------------------
For each cell ``<dataset>_sf100`` (dataset ∈ {DEEP, SIFT, SSN}):
    partsupp_<table>_vectors.npy           (N, dim)   float32   — raw embeddings
    partsupp_<table>_pks.npy               (N,)       int64     — ps_partkey (single PK)
                                           or (N, 2) int64     — composite PK if cfg has tuple
    partsupp_<table>_strata.npy            (N,)       int16     — KMeans K=20 cluster id
    query_pool_<dataset>_sf100.parquet     query_id, embedding, q_pk
    query_selectivity_<dataset>_sf100.parquet
                                           query_id, selectivity, D_target,
                                           true_cardinality, actual_sel
                                           (5 selectivities × 100 queries = 500 rows)

Disk budget
-----------
    DEEP   ≈  31 GB  vectors  +  0.64 GB pks  +  0.16 GB strata  +  ~50 MB qp
    SIFT   ≈  41 GB  vectors  +  0.64 GB pks  +  0.16 GB strata  +  ~50 MB qp
    FB(SSN)≈  82 GB  vectors  +  0.64 GB pks  +  0.16 GB strata  +  ~50 MB qp
    TOTAL  ≈ 156 GB                     (server has 1.6 TB free)

Time budget (single-thread, sequential)
---------------------------------------
    DEEP   ≈ 30 min  (fetch 25 + KMeans 5)
    SIFT   ≈ 40 min  (fetch 35 + KMeans 5)
    FB     ≈ 70 min  (fetch 60 + KMeans 10)
    TOTAL  ≈ 2.3 h

Then per-cell measurement (run_ensemble_4kang_adaptive × 11 methods) runs in
parallel via ``launch_sf100_safe.sh`` once builds complete.

CLI
---
    # default — build all 3 cells sequentially with memory gating
    python3 _internal/scripts/build_sf100_single.py

    # skip memory gating (force run — only if you've checked free -h yourself)
    python3 _internal/scripts/build_sf100_single.py --no-mem-gate

    # specific cells only
    python3 _internal/scripts/build_sf100_single.py --datasets DEEP

    # plan only — print commands and resource estimate, no execution
    python3 _internal/scripts/build_sf100_single.py --dry-run

    # background launch (server)
    nohup python3 _internal/scripts/build_sf100_single.py \\
        > /mnt/hdd0/home/capstone2026/logs/build_sf100_$(date +%Y%m%d_%H%M).log 2>&1 &

References
----------
- cache/prepare_cell.py        — actual PG fetch + KMeans + querypool builder
- cache/rq3/run_adaptive_sampling.py
                               — single-cell measurement, expects the above outputs
- cache/rq3/run_ensemble_4kang_adaptive.py
                               — 11-method ensemble runner, same artifact layout
- _internal/scripts/build_FB_single_ensemble.py
                               — analogous launcher for SF=1, SF=10 (template)
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
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
SERVER_PREP = SERVER_HOME / "cache" / "prepare_cell.py"
SERVER_NPY = SERVER_HOME / "cache" / "rq1"
SERVER_LOG = SERVER_HOME / "logs"

LOCAL_NPY = Path("/Users/hyunbin/Capstone/experiments/results/cache/rq1")
LOCAL_LOG = Path("/Users/hyunbin/Capstone/_internal/logs")

PREP_SCRIPT = SERVER_PREP if SERVER_PREP.exists() else None
NPY_DIR = SERVER_NPY if SERVER_NPY.exists() else LOCAL_NPY
LOG_DIR = SERVER_LOG if SERVER_HOME.exists() else LOCAL_LOG


# ---------------------------------------------------------------------------
# Cell registry (mirrors cache/prepare_cell.py CELLS, restricted to SF=100 set)
# ---------------------------------------------------------------------------

#: 3 cells × SF=100. external_label is the user-facing tag (FB instead of SSN
#: per the 5/9-5/10 plan); internal dataset key matches prepare_cell.py CELLS.
CELLS_SF100: dict[str, dict] = {
    "DEEP": {
        "internal": "DEEP",   "external": "DEEP",
        "table": "partsupp_deep_100",
        "dim": 96,
        "approx_vec_gb": 31.0,
        "approx_minutes": 30,
    },
    "SIFT": {
        "internal": "SIFT",   "external": "SIFT",
        "table": "partsupp_sift_100",
        "dim": 128,
        "approx_vec_gb": 41.0,
        "approx_minutes": 40,
    },
    # External label "FB" — internal dataset key remains "SSN" (table = partsupp_fb_100).
    "FB": {
        "internal": "SSN",    "external": "FB",
        "table": "partsupp_fb_100",
        "dim": 256,
        "approx_vec_gb": 82.0,
        "approx_minutes": 70,
    },
}

#: Sequential build order — smallest first to fail fast on PG/disk issues.
DEFAULT_ORDER: tuple[str, ...] = ("DEEP", "SIFT", "FB")

#: Memory safety thresholds — server has 1 TB RAM + 128 GB swap.
MIN_FREE_GB = 100         # require this much free RAM
MAX_SWAP_PCT = 80         # do not start if swap > 80% used


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def out_paths(table: str, name: str) -> dict[str, Path]:
    """Files produced by prepare_cell.py for a given (table, name=DATASET_sfSF)."""
    return {
        "vectors": NPY_DIR / f"{table}_vectors.npy",
        "pks":     NPY_DIR / f"{table}_pks.npy",
        "strata":  NPY_DIR / f"{table}_strata.npy",
        "qp":      NPY_DIR / f"query_pool_{name}.parquet",
        "qsel":    NPY_DIR / f"query_selectivity_{name}.parquet",
    }


def cell_outputs_present(cfg: dict, name: str) -> tuple[bool, dict[str, bool]]:
    """Return (all_present, per_file_present_dict)."""
    paths = out_paths(cfg["table"], name)
    presence = {k: p.exists() for k, p in paths.items()}
    return all(presence.values()), presence


def file_size_human(path: Path) -> str:
    if not path.exists():
        return "missing"
    n = path.stat().st_size
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


# ---------------------------------------------------------------------------
# Memory safety gate
# ---------------------------------------------------------------------------

def parse_meminfo() -> dict[str, int]:
    """Read /proc/meminfo → KB ints. Linux-only; on macOS dry-run skip."""
    out: dict[str, int] = {}
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return out
    for line in meminfo.read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].endswith(":"):
            try:
                out[parts[0][:-1]] = int(parts[1])  # KB
            except ValueError:
                pass
    return out


def memory_status() -> dict[str, float]:
    """Return free GB + swap-used pct + raw KB. Empty dict if /proc/meminfo absent."""
    mi = parse_meminfo()
    if not mi:
        return {}
    free_gb = (mi.get("MemAvailable", mi.get("MemFree", 0))) / 1024 / 1024
    total_swap = mi.get("SwapTotal", 0)
    free_swap = mi.get("SwapFree", 0)
    swap_used_pct = 0.0 if total_swap == 0 else (1 - free_swap / total_swap) * 100
    return {
        "free_gb": round(free_gb, 1),
        "swap_used_pct": round(swap_used_pct, 1),
        "mem_total_gb": round(mi.get("MemTotal", 0) / 1024 / 1024, 1),
        "swap_total_gb": round(total_swap / 1024 / 1024, 1),
    }


def check_memory_safe(min_free_gb: float = MIN_FREE_GB,
                      max_swap_pct: float = MAX_SWAP_PCT) -> tuple[bool, str]:
    """Return (safe, message)."""
    st = memory_status()
    if not st:
        return True, "(no /proc/meminfo — assumed safe; macOS dry-run)"
    msg = (f"free={st['free_gb']:.1f}GB / {st['mem_total_gb']:.1f}GB total, "
           f"swap_used={st['swap_used_pct']:.1f}% / {st['swap_total_gb']:.1f}GB total")
    if st["free_gb"] < min_free_gb:
        return False, f"NOT SAFE — {msg} (need free > {min_free_gb}GB)"
    if st["swap_used_pct"] > max_swap_pct:
        return False, f"NOT SAFE — {msg} (need swap < {max_swap_pct}%)"
    return True, f"SAFE — {msg}"


# ---------------------------------------------------------------------------
# Disk safety check
# ---------------------------------------------------------------------------

def check_disk_safe(npy_dir: Path, need_gb: float) -> tuple[bool, str]:
    if not npy_dir.exists():
        return True, f"(npy_dir absent: {npy_dir})"
    usage = shutil.disk_usage(npy_dir)
    free_gb = usage.free / 1e9
    msg = f"free={free_gb:.0f}GB on {npy_dir}"
    if free_gb < need_gb * 1.2:  # 20% safety margin
        return False, f"NOT SAFE — {msg} (need >= {need_gb * 1.2:.0f}GB with 20% margin)"
    return True, f"SAFE — {msg}"


# ---------------------------------------------------------------------------
# prepare_cell.py invocation
# ---------------------------------------------------------------------------

def build_cmd(internal_dataset: str, *, port: int = 55435) -> list[str]:
    """Compose the prepare_cell.py invocation for one cell."""
    if PREP_SCRIPT is None:
        # Local dry-run only.
        prep = Path("/mnt/hdd0/home/capstone2026/cache/prepare_cell.py")
    else:
        prep = PREP_SCRIPT
    return [
        "python3", "-u", str(prep),
        "--dataset", internal_dataset,
        "--sf", "100",
        "--port", str(port),
        # Default: NPY-only mode (skip PG UPDATE — already noted in prepare_cell.py
        # that --pg-update is slow with HNSW; downstream measurement uses NPY strata).
    ]


def run_one(name: str, cfg: dict, *, port: int = 55435,
            log_dir: Path = LOG_DIR, dry: bool = False,
            force: bool = False) -> dict:
    """Run prepare_cell.py for one cell. Skips on existing outputs unless force."""
    log_dir.mkdir(parents=True, exist_ok=True)
    pretty_name = f"{cfg['external']}_sf100"
    internal_name = f"{cfg['internal']}_sf100"  # query_pool/qsel use internal name
    all_ok, presence = cell_outputs_present(cfg, internal_name)

    if (not force) and all_ok:
        sizes = {k: file_size_human(p) for k, p in out_paths(cfg["table"], internal_name).items()}
        print(f"[{kst()}] SKIP {pretty_name} — all outputs already present")
        for k, sz in sizes.items():
            print(f"[{kst()}]     {k}: {sz}")
        return {"name": pretty_name, "internal": internal_name,
                "status": "skipped", "presence": presence, "sizes": sizes}

    cmd = build_cmd(cfg["internal"], port=port)
    log_path = log_dir / (
        f"build_sf100_{pretty_name}_"
        f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M')}.log"
    )
    pretty_cmd = " ".join(shlex.quote(c) for c in cmd)
    print(f"\n[{kst()}] >>> BUILD {pretty_name} (table={cfg['table']}, dim={cfg['dim']})")
    print(f"[{kst()}]     log: {log_path}")
    print(f"[{kst()}]     cmd: {pretty_cmd}")
    print(f"[{kst()}]     est: ~{cfg['approx_minutes']} min, ~{cfg['approx_vec_gb']:.0f} GB vectors")
    if dry:
        return {"name": pretty_name, "internal": internal_name, "status": "dry",
                "cmd": cmd, "log_path": str(log_path)}

    if PREP_SCRIPT is None or not PREP_SCRIPT.exists():
        raise RuntimeError(
            f"prepare_cell.py not found at {SERVER_PREP}; this script must run on "
            "the server (165.132.140.240). Use --dry-run locally."
        )

    t0 = time.time()
    with open(log_path, "wb") as logf:
        proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
    elapsed = time.time() - t0
    status = "ok" if proc.returncode == 0 else "fail"
    print(f"[{kst()}]     end status={status} rc={proc.returncode} "
          f"elapsed={elapsed:.1f}s ({elapsed / 60:.1f} min)")

    # Post-build presence check + sizes
    all_ok2, presence2 = cell_outputs_present(cfg, internal_name)
    sizes = {k: file_size_human(p) for k, p in out_paths(cfg["table"], internal_name).items()}
    return {
        "name": pretty_name, "internal": internal_name,
        "status": status, "rc": proc.returncode, "elapsed_s": round(elapsed, 1),
        "log_path": str(log_path),
        "all_outputs_present": all_ok2, "presence": presence2, "sizes": sizes,
    }


# ---------------------------------------------------------------------------
# Resource estimate
# ---------------------------------------------------------------------------

def print_plan(datasets: list[str]) -> None:
    print(f"\n[{kst()}] === SF=100 build plan ===")
    print(f"  {'cell':<10} {'table':<22} {'dim':>4} {'~GB':>6} {'~min':>5}  status")
    total_gb = 0.0
    total_min = 0
    n_skip = 0
    for ds in datasets:
        cfg = CELLS_SF100[ds]
        internal_name = f"{cfg['internal']}_sf100"
        all_ok, _ = cell_outputs_present(cfg, internal_name)
        tag = "exists" if all_ok else "TODO"
        if all_ok:
            n_skip += 1
        total_gb += cfg["approx_vec_gb"]
        total_min += cfg["approx_minutes"]
        print(f"  {cfg['external']+'_sf100':<10} {cfg['table']:<22} "
              f"{cfg['dim']:>4} {cfg['approx_vec_gb']:>6.0f} "
              f"{cfg['approx_minutes']:>5}  [{tag}]")
    print(f"  {'-'*68}")
    print(f"  TOTAL {len(datasets)} cells, ~{total_gb:.0f} GB vectors, "
          f"~{total_min} min sequential ({total_min/60:.1f} h)")
    if n_skip:
        print(f"  ({n_skip} cell(s) already complete — will SKIP unless --force)")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--datasets", nargs="+", choices=list(CELLS_SF100.keys()),
                    default=list(DEFAULT_ORDER),
                    help=f"Cells to build (default: {' '.join(DEFAULT_ORDER)}).")
    ap.add_argument("--port", type=int, default=55435,
                    help="PG port (default 55435; do NOT use 55432/55433 — chaerim).")
    ap.add_argument("--no-mem-gate", action="store_true",
                    help="Skip memory safety check (only if you've verified free -h yourself).")
    ap.add_argument("--min-free-gb", type=float, default=MIN_FREE_GB,
                    help=f"Min free RAM (GB) to start (default {MIN_FREE_GB}).")
    ap.add_argument("--max-swap-pct", type=float, default=MAX_SWAP_PCT,
                    help=f"Max swap-used %% to start (default {MAX_SWAP_PCT}).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Plan + per-cell command, no execution.")
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if all outputs exist.")
    args = ap.parse_args()

    print(f"[{kst()}] === build_sf100_single ===")
    print(f"[{kst()}] PREP_SCRIPT: {PREP_SCRIPT}")
    print(f"[{kst()}] NPY_DIR:     {NPY_DIR}")
    print(f"[{kst()}] LOG_DIR:     {LOG_DIR}")
    print(f"[{kst()}] datasets={args.datasets}  port={args.port}  force={args.force}")

    print_plan(args.datasets)

    # Disk gate (always — fail loud)
    need_gb = sum(CELLS_SF100[d]["approx_vec_gb"] for d in args.datasets)
    disk_ok, disk_msg = check_disk_safe(NPY_DIR, need_gb)
    print(f"[{kst()}] disk: {disk_msg}")
    if not disk_ok and not args.dry_run:
        raise SystemExit("ABORT: insufficient disk")

    # Memory gate (skipped on dry-run or when explicitly disabled)
    if not args.dry_run and not args.no_mem_gate:
        mem_ok, mem_msg = check_memory_safe(args.min_free_gb, args.max_swap_pct)
        print(f"[{kst()}] memory: {mem_msg}")
        if not mem_ok:
            raise SystemExit(
                "ABORT: memory not safe — wait for sf=10 measurements to drain, "
                "or pass --no-mem-gate (only if you've checked yourself)."
            )

    if args.dry_run:
        print(f"[{kst()}] === dry-run ===")
        for ds in args.datasets:
            run_one(ds, CELLS_SF100[ds], port=args.port, dry=True, force=args.force)
        print(f"\n[{kst()}] dry-run OK — total {len(args.datasets)} cell(s) planned")
        return

    if not NPY_DIR.exists():
        raise SystemExit(f"NPY_DIR not found: {NPY_DIR} (run on server)")

    t_total = time.time()
    summary: list[dict] = []
    for ds in args.datasets:
        # Re-check memory before each cell (process queue may have grown).
        if not args.no_mem_gate:
            mem_ok, mem_msg = check_memory_safe(args.min_free_gb, args.max_swap_pct)
            if not mem_ok:
                print(f"[{kst()}] STOPPING — memory drained between cells: {mem_msg}")
                summary.append({"name": f"{ds}_sf100", "status": "aborted_low_mem",
                                "mem": mem_msg})
                break
            print(f"[{kst()}] memory OK before {ds}: {mem_msg}")

        res = run_one(ds, CELLS_SF100[ds], port=args.port, force=args.force)
        summary.append(res)

        # Stop sequence on first failure — don't waste GB on subsequent fetches.
        if res["status"] == "fail":
            print(f"[{kst()}] STOPPING — {ds} build failed; tail of log:")
            log_path = res.get("log_path")
            if log_path and Path(log_path).exists():
                tail = subprocess.run(["tail", "-n", "30", log_path],
                                      capture_output=True, text=True)
                print(tail.stdout)
            break

    print(f"\n[{kst()}] === summary ===")
    for s in summary:
        print(f"  {s['name']:<12}  status={s.get('status','?'):<14}")
        for k, sz in (s.get("sizes") or {}).items():
            print(f"      {k:<8} {sz}")

    n_ok = sum(1 for s in summary if s.get("status") == "ok")
    n_skip = sum(1 for s in summary if s.get("status") == "skipped")
    n_fail = sum(1 for s in summary if s.get("status") not in ("ok", "skipped"))
    elapsed = time.time() - t_total
    print(f"[{kst()}] ok={n_ok} skipped={n_skip} fail={n_fail}  "
          f"total elapsed={elapsed:.0f}s ({elapsed/3600:.2f} h)")

    # build_meta.json — single source of truth for downstream sanity checks.
    meta_path = NPY_DIR / "build_sf100_meta.json"
    try:
        existing = {}
        if meta_path.exists():
            try:
                existing = json.loads(meta_path.read_text())
            except json.JSONDecodeError:
                existing = {}
        history = existing.get("history", [])
        history.append({
            "kst": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S"),
            "datasets_requested": args.datasets,
            "summary": summary,
        })
        meta = {
            "kst": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S"),
            "cells_sf100": {
                ds: {
                    **CELLS_SF100[ds],
                    "files": {
                        k: {
                            "path": str(p),
                            "size_human": file_size_human(p),
                            "exists": p.exists(),
                        }
                        for k, p in out_paths(CELLS_SF100[ds]["table"],
                                              f"{CELLS_SF100[ds]['internal']}_sf100").items()
                    },
                }
                for ds in args.datasets
            },
            "history": history,
        }
        meta_path.write_text(json.dumps(meta, indent=2, default=str))
        print(f"[{kst()}] meta -> {meta_path}")
    except OSError as exc:
        print(f"[{kst()}] WARN: could not write meta ({exc})")

    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
