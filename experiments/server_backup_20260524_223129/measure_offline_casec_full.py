#!/usr/bin/env python3
"""오프라인 CaseC dual-Bernoulli 전수 측정 — v13 scope 일치 95 tuple 평면.

v15 portfolio (measure_offline_casec_portfolio.py) 는 cell × default sel/K 만
측정 (18 cell). 본 wrapper 는 (cell, sel, K) 세 축 전수 평면 (~95 tuple) 을
measure_paper_exact.py --mode CaseC --sel <sel> --K <K> subprocess 로 launch
한다. v13 정본 1,508 cell (3-way matched) scope 와 완전 일치.

CSV 형식 (--tuples-csv):
    cell,sel,K
    A1-DEEP,0.001,20
    A1-DEEP,0.010,10
    A1-DEEP,0.010,20
    ...

CSV 생성 (로컬):
    python3 -c "
    import pyarrow.parquet as pq
    df = pq.read_table('_internal/cache/rq3/aggregated_v13_full.parquet').to_pandas()
    tuples = df[['cell','sel','K']].drop_duplicates().sort_values(['cell','sel','K'])
    tuples.to_csv('/tmp/v13_casec_95tuples.csv', index=False)
    "

서버 실행:
    python3 measure_offline_casec_full.py \\
        --tuples-csv /mnt/hdd0/home/capstone2026/cache/rq3/v13_casec_95tuples.csv \\
        --parallel 3 --trials 10 --n-queries 1000 \\
        --output /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v16_full95_<TS>

ETA:
  · sequential = 95 cell × 3-4분/cell ≈ 6 시간
  · parallel 3 (sf-adaptive) = 2-2.5 시간
  · watchdog v6 (free < 256GB → SIGSTOP, 회복 시 SIGCONT) 가 메모리 압박 자동 양보
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

SERVER = Path("/mnt/hdd0/home/capstone2026").is_dir()
SERVER_SCRIPT = Path("/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py")
LOCAL_SCRIPT = Path(__file__).resolve().parent / "measure_paper_exact.py"

# v13 정본 (build_cell_specs + concat 7 cell) 의 25 cell whitelist
KNOWN_CELLS = frozenset({
    "A1-DEEP", "A1-SIFT", "A1-SSN",
    "A2-Fig7", "A2-Fig8", "A2-Fig9",
    "A4-sel",
    "A5-scale-sf1", "A5-scale-sf10", "A5-scale-sf100",
    "A5-scale-sf1-SIFT", "A5-scale-sf1-SSN",
    "A5-scale-sf10-SIFT", "A5-scale-sf10-SSN",
    "A6-WIKI-sf1", "A6-WIKI-sf10",
    "A7-YFCC-sf1",
    "A8-DEEP+SIFT-sf10",
    "A9-DEEP+SIFT-concat-sf1", "A9-DEEP+SIFT-concat-sf10", "A9-DEEP+SIFT-concat-sf100",
    "A10-DEEP+WIKI-concat-sf1", "A10-DEEP+WIKI-concat-sf10",
    "A11-DEEP+YFCC-concat-sf1", "A11-DEEP+YFCC-concat-sf10",
})

# cell name → sf 추출 (cell name 안 'sf{N}' 패턴 없으면 cell-type default)
_CELL_SF_DEFAULT = {
    "A1-DEEP": 100, "A1-SIFT": 100, "A1-SSN": 100,
    "A2-Fig7": 10, "A2-Fig8": 10, "A2-Fig9": 10,
    "A4-sel": 100,
}


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")


def script_path() -> Path:
    if SERVER and SERVER_SCRIPT.exists():
        return SERVER_SCRIPT
    return LOCAL_SCRIPT


def extract_sf(cell: str) -> int:
    """cell name 에서 sf 추출 (sf{N} 패턴 우선, 없으면 default lookup)."""
    m = re.search(r"sf(\d+)", cell)
    if m:
        return int(m.group(1))
    if cell in _CELL_SF_DEFAULT:
        return _CELL_SF_DEFAULT[cell]
    raise ValueError(f"cannot infer sf from cell name: {cell}")


def load_tuples(csv_path: Path) -> list[tuple[str, float, int]]:
    """CSV → [(cell, sel, K), ...]. cell whitelist + sel·K range 검증."""
    if not csv_path.exists():
        raise FileNotFoundError(f"tuples CSV not found: {csv_path}")
    tuples: list[tuple[str, float, int]] = []
    with open(csv_path, newline="") as fp:
        reader = csv.DictReader(fp)
        required = {"cell", "sel", "K"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError(f"CSV header missing one of {required}, got {reader.fieldnames}")
        for row in reader:
            cell = row["cell"].strip()
            sel = float(row["sel"])
            K = int(row["K"])
            if cell not in KNOWN_CELLS:
                raise ValueError(f"unknown cell sub name in CSV: {cell}")
            if sel not in (0.001, 0.01, 0.1):
                raise ValueError(f"sel out of paper range (0.001/0.01/0.1): {sel} for {cell}")
            if K not in (10, 20, 30):
                raise ValueError(f"K out of paper range (10/20/30): {K} for {cell}")
            tuples.append((cell, sel, K))
    if not tuples:
        raise ValueError(f"empty tuples CSV: {csv_path}")
    # duplicate 검증
    if len(tuples) != len(set(tuples)):
        dup = sorted({t for t in tuples if tuples.count(t) > 1})
        raise ValueError(f"duplicate (cell, sel, K) tuples: {dup}")
    return tuples


def launch_one(cell: str, sel: float, K: int, output_dir: Path,
               trials: int, n_queries: int, log_dir: Path
               ) -> tuple[str, float, int, int, float, str]:
    """한 tuple launch. (cell, sel, K, rc, elapsed_s, log_path) 반환."""
    log_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{cell}_sel{sel:g}_K{K}"
    log_path = log_dir / f"{tag}.log"
    cmd = [
        sys.executable, "-u", str(script_path()),
        "--rq", "3", "--phase", "E",
        "--cell", cell,
        "--mode", "CaseC",
        "--sel", str(sel),
        "--K", str(K),
        "--n-queries", str(n_queries),
        "--trials", str(trials),
        "--output", str(output_dir),
    ]
    t0 = time.time()
    with open(log_path, "w") as fp:
        fp.write(f"[{kst()}] {tag} cmd={' '.join(cmd)}\n")
        fp.flush()
        proc = subprocess.run(cmd, stdout=fp, stderr=subprocess.STDOUT,
                              cwd=str(script_path().parent))
    elapsed = time.time() - t0
    return cell, sel, K, proc.returncode, elapsed, str(log_path)


def run_full(tuples: list[tuple[str, float, int]], output_dir: Path,
             trials: int, n_queries: int, parallel: int) -> dict:
    """전수 95 tuple launch (parallel 또는 sequential)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir = output_dir / "launch_logs"

    # sf-adaptive ordering: sf=100 (heavy) 먼저 → sf=10 → sf=1.
    # 단순 무가중치 ProcessPoolExecutor 가 watchdog (256GB) 보호와 함께 안전.
    sorted_tuples = sorted(tuples, key=lambda t: (-extract_sf(t[0]), t[0], t[1], t[2]))

    print(f"[{kst()}] full launch start — {len(sorted_tuples)} tuples, parallel={parallel}")
    print(f"[{kst()}] output_dir={output_dir}")
    print(f"[{kst()}] sf distribution: "
          f"sf=100={sum(1 for t in sorted_tuples if extract_sf(t[0])==100)} | "
          f"sf=10={sum(1 for t in sorted_tuples if extract_sf(t[0])==10)} | "
          f"sf=1={sum(1 for t in sorted_tuples if extract_sf(t[0])==1)}")

    results = []
    t_total = time.time()

    if parallel <= 1:
        for cell, sel, K in sorted_tuples:
            tag = f"{cell}/sel{sel:g}/K{K}"
            print(f"\n[{kst()}] launching {tag} (sequential)…")
            res = launch_one(cell, sel, K, output_dir, trials, n_queries, log_dir)
            results.append(res)
            _, _, _, rc, elapsed, log = res
            status = "OK" if rc == 0 else f"FAIL rc={rc}"
            print(f"[{kst()}] {tag}: {status}, {elapsed:.1f}s")
    else:
        with ProcessPoolExecutor(max_workers=parallel) as ex:
            future_map = {
                ex.submit(launch_one, cell, sel, K, output_dir, trials, n_queries, log_dir):
                    (cell, sel, K)
                for cell, sel, K in sorted_tuples
            }
            done_n = 0
            for fut in as_completed(future_map):
                cell, sel, K = future_map[fut]
                tag = f"{cell}/sel{sel:g}/K{K}"
                try:
                    res = fut.result()
                    results.append(res)
                    _, _, _, rc, elapsed, log = res
                    status = "OK" if rc == 0 else f"FAIL rc={rc}"
                except Exception as e:
                    print(f"[{kst()}] {tag}: EXCEPTION {type(e).__name__}: {e}")
                    results.append((cell, sel, K, -1, 0.0, ""))
                    status = "EXCEPTION"
                done_n += 1
                print(f"[{kst()}] [{done_n:3d}/{len(sorted_tuples)}] {tag}: {status}")

    t_wall = time.time() - t_total
    ok = sum(1 for r in results if r[3] == 0)
    fail = len(results) - ok
    print(f"\n[{kst()}] full launch done — {ok}/{len(sorted_tuples)} OK, {fail} FAIL, "
          f"wall {t_wall:.1f}s ({t_wall / 60:.1f} min / {t_wall / 3600:.2f} h)")

    summary_path = output_dir / "full95_summary.md"
    with open(summary_path, "w") as fp:
        fp.write(f"# CaseC full 95 tuple summary — v16 ({kst()})\n\n")
        fp.write(f"- tuples: {len(sorted_tuples)}, parallel={parallel}, "
                 f"trials={trials}, n_queries={n_queries}\n")
        fp.write(f"- wall time: {t_wall:.1f}s ({t_wall / 60:.1f} min / "
                 f"{t_wall / 3600:.2f} h)\n")
        fp.write(f"- OK / FAIL: {ok} / {fail}\n\n")
        fp.write("| cell | sel | K | rc | elapsed_s |\n|---|--:|--:|--:|--:|\n")
        for r in sorted(results, key=lambda x: (x[0], x[1], x[2])):
            cell, sel, K, rc, elapsed, _ = r
            fp.write(f"| {cell} | {sel:g} | {K} | {rc} | {elapsed:.1f} |\n")
    print(f"[{kst()}] summary: {summary_path}")

    return {
        "tuples_total": len(sorted_tuples),
        "ok": ok,
        "fail": fail,
        "wall_s": t_wall,
        "summary_path": str(summary_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="오프라인 CaseC dual-Bernoulli 전수 95 tuple 측정 launcher")
    ap.add_argument("--tuples-csv", type=Path, required=True,
                    help="CSV: cell,sel,K (헤더 필수). v13 parquet 에서 추출.")
    ap.add_argument("--trials", type=int, default=10,
                    help="trial 수 (paper §VI verbatim, v14·v15 동일)")
    ap.add_argument("--n-queries", type=int, default=1000,
                    help="query 수 per trial (paper Fig 6 verbatim)")
    ap.add_argument("--output", type=Path,
                    default=Path(f"/mnt/hdd0/home/capstone2026/cache/rq3/"
                                  f"paper_exact_v16_full95_"
                                  f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M%S')}"))
    ap.add_argument("--parallel", type=int, default=3,
                    help="병렬 tuple 수 (default 3). watchdog 256GB 가 압박 시 SIGSTOP/CONT 보호.")
    ap.add_argument("--dry-run", action="store_true",
                    help="CSV 검증 + launch cmd 표시만 (subprocess 실행 X)")
    args = ap.parse_args()

    tuples = load_tuples(args.tuples_csv)
    print(f"[{kst()}] loaded {len(tuples)} tuples from {args.tuples_csv}")
    sf_dist = {sf: sum(1 for t in tuples if extract_sf(t[0]) == sf)
               for sf in (1, 10, 100)}
    print(f"[{kst()}] sf distribution: {sf_dist}")

    if args.dry_run:
        print(f"\n=== dry-run: {len(tuples)} tuples ===")
        print(f"script_path: {script_path()}")
        print(f"output_dir: {args.output}")
        for cell, sel, K in tuples[:5]:
            cmd = [sys.executable, "-u", str(script_path()),
                   "--rq", "3", "--phase", "E", "--cell", cell, "--mode", "CaseC",
                   "--sel", str(sel), "--K", str(K),
                   "--n-queries", str(args.n_queries), "--trials", str(args.trials),
                   "--output", str(args.output)]
            print(f"  {cell} sel{sel:g} K{K}: {' '.join(cmd)}")
        if len(tuples) > 5:
            print(f"  … (+{len(tuples) - 5} more)")
        print("\n✓ dry-run 통과")
        return

    if not SERVER:
        print("서버 전용 — 165.132.140.240 capstone2026 에서 실행")
        print("로컬에서는 --dry-run 만 가능")
        return

    summary = run_full(tuples, args.output, args.trials, args.n_queries, args.parallel)
    # ★ Codex D fix (5/24): subprocess fail 을 exit code 0 으로 숨기던 결함.
    #   fail 이 있으면 SystemExit 으로 명시 종료 → 자동화 후속에서 실패 인지.
    if summary["fail"]:
        raise SystemExit(
            f"❌ {summary['fail']}/{summary['tuples_total']} tuples FAIL — "
            f"see {summary['summary_path']}")


if __name__ == "__main__":
    main()
