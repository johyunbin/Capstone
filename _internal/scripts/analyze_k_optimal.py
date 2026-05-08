#!/usr/bin/env python3
"""
RQ1 K-sweep 분석 — K_optimal 도출 + heatmap.

서버 cache (/mnt/hdd0/home/capstone2026/cache/rq1/) 의 rq1_*_km_k_*.parquet
+ rq1_*_km20.parquet 파일을 읽어, dataset × sf × K × mode × sel 로 그룹화 한다.

K 값은 parquet filename / mode 컬럼에서 추출:
    rq1_DEEP_sf1_km_k_10.parquet → K=10  (mode='km10')
    rq1_DEEP_sf1_km_k_20.parquet → K=20  (mode='km20')
    rq1_DEEP_sf1_km20.parquet    → K=20  (호환)

각 (dataset × sf) 별 K_optimal:
  · sel ∈ {0.01, 0.05, 0.10, 0.30, 0.50} 마다 km{K} 의 median q_error 를 계산
  · 그 5 개 sel 의 median q_error 를 평균 → K 별 mean(median qerror)
  · argmin K 가 K_optimal

산출:
    experiments/results/rq1_motivation/k_optimal_per_dataset.csv
        — dataset, sf, K_optimal, K_q_error_table (per-K JSON)
    experiments/figures/rq1_k_sweep_heatmap.png  (optional)
        — heatmap (Apple SD Gothic Neo, 12×6")

Usage:
    # 기본 (로컬 caches 디렉토리에서)
    python3 _internal/scripts/analyze_k_optimal.py

    # rsync 후 실행 (server → local)
    python3 _internal/scripts/analyze_k_optimal.py --rsync-first

    # heatmap 생성
    python3 _internal/scripts/analyze_k_optimal.py --plot-heatmap
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 경로 — 로컬 cache 가 비어있으면 rsync 로 server → local 동기화
# ---------------------------------------------------------------------------

LOCAL_CACHE = Path("/Users/hyunbin/Capstone/_internal/cache/rq1")
SERVER_CACHE = "capstone:/mnt/hdd0/home/capstone2026/cache/rq1/"
RESULTS_DIR = Path("/Users/hyunbin/Capstone/experiments/results/rq1_motivation")
FIG_DIR = Path("/Users/hyunbin/Capstone/experiments/figures")

# 매칭 패턴: rq1_{DS}_sf{X}_km_k_{K}.parquet  또는  rq1_{DS}_sf{X}_km20.parquet
PAT_KSWEEP = re.compile(r"rq1_(?P<ds>[A-Za-z0-9]+)_sf(?P<sf>\d+)_km_k_(?P<K>\d+)\.parquet$")
PAT_KM20 = re.compile(r"rq1_(?P<ds>[A-Za-z0-9]+)_sf(?P<sf>\d+)_km20\.parquet$")


def _rsync_from_server(local: Path) -> None:
    local.mkdir(parents=True, exist_ok=True)
    cmd = [
        "rsync", "-avz", "--include=rq1_*_km*.parquet",
        "--include=*/", "--exclude=*",
        SERVER_CACHE, str(local) + "/",
    ]
    print(f"[rsync] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# 1. parquet 디스커버리 + 로딩
# ---------------------------------------------------------------------------

def discover_parquets(cache_dir: Path) -> list[dict]:
    """cache_dir 안에서 매칭되는 모든 parquet 의 (path, ds, sf, K) tuple 수집."""
    found: list[dict] = []
    for p in sorted(cache_dir.glob("rq1_*_km*.parquet")):
        name = p.name
        m_sweep = PAT_KSWEEP.match(name)
        m_20 = PAT_KM20.match(name)
        if m_sweep:
            found.append({
                "path": p, "dataset": m_sweep.group("ds").upper(),
                "sf": int(m_sweep.group("sf")), "K": int(m_sweep.group("K")),
                "source": "k_sweep",
            })
        elif m_20:
            found.append({
                "path": p, "dataset": m_20.group("ds").upper(),
                "sf": int(m_20.group("sf")), "K": 20,
                "source": "km20_default",
            })
    return found


def load_all(parquet_meta: list[dict]) -> pd.DataFrame:
    """모든 parquet 을 합친 long-form dataframe.

    필요 컬럼: dataset, sf, K, mode, selectivity, seed, query_id, q_error
    """
    dfs: list[pd.DataFrame] = []
    for entry in parquet_meta:
        df = pd.read_parquet(entry["path"])
        df["sf"] = entry["sf"]
        df["K"] = entry["K"]
        if "dataset" not in df.columns:
            df["dataset"] = entry["dataset"]
        else:
            df["dataset"] = df["dataset"].fillna(entry["dataset"])
            df["dataset"] = df["dataset"].astype(str).str.upper()
        dfs.append(df)
        print(f"  loaded {entry['path'].name}: {len(df):,} rows "
              f"(ds={entry['dataset']}, sf={entry['sf']}, K={entry['K']})")
    if not dfs:
        raise RuntimeError("no parquet files matched")
    return pd.concat(dfs, axis=0, ignore_index=True)


# ---------------------------------------------------------------------------
# 2. group + summarize
# ---------------------------------------------------------------------------

def compute_k_optimal(df: pd.DataFrame) -> pd.DataFrame:
    """(dataset, sf) 별로 K_optimal 도출.

    절차:
      · km{K} mode 행만 필터 (bernoulli baseline 제외)
      · group by (dataset, sf, K, sel) → median q_error 계산
      · 같은 (dataset, sf, K) 에서 sel 평균 → K 별 점수
      · argmin K = K_optimal
    """
    # km{K} 만 선별 (mode 가 bernoulli 인 baseline 제거)
    mask_km = df["mode"].astype(str).str.startswith("km")
    df_km = df[mask_km].copy()
    if df_km.empty:
        raise RuntimeError("no km{K} rows found")

    # mode 컬럼에서 K 재추출 (parquet 이 km10 / km100 같이 일관된 mode 라벨인지 확인)
    def _extract_K(mode_str: str) -> int | None:
        m = re.match(r"km(\d+)", str(mode_str))
        return int(m.group(1)) if m else None
    df_km["K_from_mode"] = df_km["mode"].apply(_extract_K)
    # K (filename 기반) 와 K_from_mode 가 다르면 경고 + filename 우선
    mismatch = df_km[df_km["K_from_mode"].notna() & (df_km["K_from_mode"] != df_km["K"])]
    if not mismatch.empty:
        print(f"[warn] {len(mismatch)} rows have K(file) ≠ K(mode) — using filename K")

    # group by (dataset, sf, K, sel) → median q_error
    grp = df_km.groupby(
        ["dataset", "sf", "K", "selectivity"], as_index=False,
    )["q_error"].median().rename(columns={"q_error": "median_qe"})

    # sel 별 median 을 평균 → K 별 점수 (smaller = better)
    score = grp.groupby(["dataset", "sf", "K"], as_index=False)["median_qe"].mean()
    score = score.rename(columns={"median_qe": "mean_median_qe"})

    # K_optimal = argmin K of mean_median_qe per (dataset, sf)
    out_rows: list[dict] = []
    for (ds, sf), g in score.groupby(["dataset", "sf"]):
        g = g.sort_values("K").reset_index(drop=True)
        idx_best = int(g["mean_median_qe"].idxmin())
        K_opt = int(g.loc[idx_best, "K"])
        # K_q_error_table = {K: mean_median_qe}
        k_table = {int(row["K"]): float(round(row["mean_median_qe"], 6))
                   for _, row in g.iterrows()}
        out_rows.append({
            "dataset": ds, "sf": sf, "K_optimal": K_opt,
            "K_q_error_table": json.dumps(k_table),
            "best_score": float(round(g.loc[idx_best, "mean_median_qe"], 6)),
            "K_values": json.dumps(sorted(k_table.keys())),
        })
    out_df = pd.DataFrame(out_rows).sort_values(["dataset", "sf"]).reset_index(drop=True)

    return out_df, grp, score


# ---------------------------------------------------------------------------
# 3. heatmap (선택)
# ---------------------------------------------------------------------------

def plot_heatmap(score: pd.DataFrame, out_png: Path) -> None:
    """heatmap: rows = (dataset, sf), cols = K, color = mean_median_qe.

    Apple SD Gothic Neo 폰트, 12×6 inches.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
    except ImportError:
        print("[warn] matplotlib unavailable — skip heatmap")
        return

    # 폰트 설정 — Apple SD Gothic Neo (mac 기본)
    candidates = [
        "Apple SD Gothic Neo", "AppleSDGothicNeo-Regular",
        "AppleGothic", "Helvetica",
    ]
    fonts_avail = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in fonts_avail:
            plt.rcParams["font.family"] = c
            print(f"[font] using {c}")
            break

    # pivot to (row=dataset_sf, col=K)
    score = score.copy()
    score["row"] = score["dataset"].astype(str) + "_sf" + score["sf"].astype(str)
    pivot = score.pivot(index="row", columns="K", values="mean_median_qe")
    pivot = pivot.sort_index()
    Ks = sorted(pivot.columns)
    pivot = pivot[Ks]

    fig, ax = plt.subplots(figsize=(12, 6))
    data = pivot.values
    im = ax.imshow(data, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(Ks)))
    ax.set_xticklabels([f"K={k}" for k in Ks])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(list(pivot.index))
    ax.set_xlabel("K (number of strata)")
    ax.set_ylabel("dataset × sf")
    ax.set_title("RQ1 K-sweep: mean median q_error per (dataset, sf, K)")

    # annotate cells
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color="white" if val > np.nanmedian(data) else "black",
                        fontsize=8)

    fig.colorbar(im, ax=ax, label="mean median q_error")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] saved {out_png}")


# ---------------------------------------------------------------------------
# 4. main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default=str(LOCAL_CACHE),
                    help="local cache directory holding rq1_*.parquet")
    ap.add_argument("--rsync-first", action="store_true",
                    help="rsync from server before reading")
    ap.add_argument("--out-csv", default=str(RESULTS_DIR / "k_optimal_per_dataset.csv"))
    ap.add_argument("--plot-heatmap", action="store_true")
    ap.add_argument("--heatmap-out", default=str(FIG_DIR / "rq1_k_sweep_heatmap.png"))
    args = ap.parse_args()

    cache_dir = Path(args.cache_dir)
    if args.rsync_first:
        _rsync_from_server(cache_dir)
    if not cache_dir.exists():
        raise SystemExit(f"cache dir not found: {cache_dir} (use --rsync-first?)")

    print(f"=== analyze_k_optimal: scanning {cache_dir} ===")
    parquet_meta = discover_parquets(cache_dir)
    if not parquet_meta:
        raise SystemExit(
            f"no rq1_*_km*.parquet under {cache_dir} — "
            f"run with --rsync-first or copy files manually"
        )
    print(f"  found {len(parquet_meta)} parquet files")
    by_ds = {}
    for entry in parquet_meta:
        by_ds.setdefault((entry["dataset"], entry["sf"]), []).append(entry["K"])
    for (ds, sf), Ks in sorted(by_ds.items()):
        print(f"    {ds} sf={sf}: K ∈ {sorted(set(Ks))}")

    df = load_all(parquet_meta)
    print(f"  total rows loaded: {len(df):,}")

    out_df, sel_grp, score = compute_k_optimal(df)
    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_csv, index=False)
    print(f"\n=== K_optimal per (dataset, sf) ===")
    print(out_df.to_string(index=False))
    print(f"\nsaved {out_csv}")

    if args.plot_heatmap:
        plot_heatmap(score, Path(args.heatmap_out))


if __name__ == "__main__":
    main()
