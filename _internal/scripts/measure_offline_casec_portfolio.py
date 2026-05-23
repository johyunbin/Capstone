#!/usr/bin/env python3
"""오프라인 CaseC dual-Bernoulli 측정 portfolio — v14 9 cell 외 추가 cell 확장.

v14 (5/23 launch) = 9 cell CaseC (A1-DEEP/SIFT/SSN, A2-Fig7/Fig9, A4-sel,
A5-scale-sf1/10/100). 본 script 는 build_cell_specs() 의 18 cell type 전체 + sel
ablation 변형 으로 portfolio 를 확장한다 (v15).

cell list:
  · v14 carry (9 cell) — 정합성 재확인 (같은 mean qe_trim 기대)
  · 신규 type (9 cell) — A2-Fig8 (DEEP+WIKI multi), A6-WIKI-sf1/10,
    A5-scale-sf1/10-SIFT, A5-scale-sf1/10-SSN, A7-YFCC-sf1, A8-DEEP+SIFT-sf10
  · 선택: sel ablation (A4-sel 0.01/0.10, A1-DEEP/SIFT/SSN 0.001/0.10) — flag

★ ECQO cell (A3-TPCDS) 은 제외 — CaseC dual-Bernoulli 와 무관 (HNSW range 정확).
★ 각 cell launch = `python3 measure_paper_exact.py --rq 3 --phase E --cell <sub>
   --mode CaseC --output <outdir>` subprocess. v14_launch_20260523.sh 와 동일 패턴.
   sel ablation 변형 cell 은 별도 spec 추가가 measure_paper_exact.py 에 필요해 본
   wrapper 는 portfolio cell 만 sequential/parallel 으로 launch.

서버 실행:
    python3 measure_offline_casec_portfolio.py \\
        --output /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v15_25cell_<TS> \\
        --parallel 3 --trials 10 --n-queries 1000

병렬 launch:
  · CaseC 한 cell = 약 4 분 (v14 launch 38분 / 9 cell ≈ 4.3 min/cell).
  · 3 병렬: 18 cell × 4 min / 3 ≈ 24 분 wall. 단 fetch_all_vectors 메모리 부하 (~10GB) ×
    3 cell 동시 = ~30GB. v14_launch 는 sequential 만 함 — 본 wrapper 가 첫 병렬 시도.
  · 자원 모니터: launch 전 free RAM ≥ 256GB 확인 + 위반 시 새 cell launch 중단.

로컬 dry-run:
    python3 measure_offline_casec_portfolio.py --dry-run
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

SERVER = Path("/mnt/hdd0/home/capstone2026").is_dir()
SERVER_SCRIPT = Path("/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py")
LOCAL_SCRIPT = Path(__file__).resolve().parent / "measure_paper_exact.py"

# v14 carry — 정합성 재확인용 9 cell
V14_CELLS = (
    "A1-DEEP", "A1-SIFT", "A1-SSN",
    "A2-Fig7", "A2-Fig9",
    "A4-sel",
    "A5-scale-sf1", "A5-scale-sf10", "A5-scale-sf100",
)

# 신규 9 cell — build_cell_specs() 추가 type (A3-TPCDS ECQO 는 제외)
NEW_CELLS = (
    "A2-Fig8",                  # DEEP+WIKI sf10 multi
    "A6-WIKI-sf10",             # 고차원 single
    "A5-scale-sf1-SIFT",        # small SIFT
    "A5-scale-sf1-SSN",         # small SSN
    "A5-scale-sf10-SIFT",       # medium SIFT
    "A5-scale-sf10-SSN",        # medium SSN
    "A6-WIKI-sf1",              # small 고차원 single
    "A7-YFCC-sf1",              # small 중차원 single
    "A8-DEEP+SIFT-sf10",        # multi 중차원
)

# 기본 portfolio = v14 carry + 신규 = 18 cell
DEFAULT_PORTFOLIO = V14_CELLS + NEW_CELLS

# whitelist — measure_paper_exact.py build_cell_specs() 의 모든 sub names (A3-TPCDS 제외 = ECQO mode, CaseC 부적합)
# Codex BLOCKER D 적용 (5/24) — invalid cell sub name 거부, measure_paper_exact 가 미발견 시 rc=0 으로 끝나는 silent failure 방어
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
})


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")


def script_path() -> Path:
    """서버 우선, 없으면 로컬 _internal/scripts/ (dry-run 용)."""
    if SERVER and SERVER_SCRIPT.exists():
        return SERVER_SCRIPT
    return LOCAL_SCRIPT


def launch_one(cell: str, output_dir: Path, trials: int, n_queries: int,
               log_dir: Path) -> tuple[str, int, float, str]:
    """한 cell launch (subprocess). (cell, rc, elapsed_s, log_path) 반환."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{cell}.log"
    cmd = [
        sys.executable, "-u", str(script_path()),
        "--rq", "3", "--phase", "E",
        "--cell", cell,
        "--mode", "CaseC",
        "--n-queries", str(n_queries),
        "--trials", str(trials),
        "--output", str(output_dir),
    ]
    t0 = time.time()
    with open(log_path, "w") as fp:
        fp.write(f"[{kst()}] cell={cell} cmd={' '.join(cmd)}\n")
        fp.flush()
        proc = subprocess.run(cmd, stdout=fp, stderr=subprocess.STDOUT,
                              cwd=str(script_path().parent))
    elapsed = time.time() - t0
    return cell, proc.returncode, elapsed, str(log_path)


def run_portfolio(cells, output_dir: Path, trials: int, n_queries: int,
                  parallel: int) -> dict:
    """portfolio cell 들을 parallel 또는 sequential 으로 launch."""
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir = output_dir / "launch_logs"

    print(f"[{kst()}] portfolio launch start — {len(cells)} cells, parallel={parallel}")
    print(f"[{kst()}] output_dir={output_dir}")
    print(f"[{kst()}] cells: {', '.join(cells)}")

    results = []
    t_total = time.time()

    if parallel <= 1:
        # sequential — v14_launch 와 동일 패턴
        for cell in cells:
            print(f"\n[{kst()}] launching {cell} (sequential)…")
            res = launch_one(cell, output_dir, trials, n_queries, log_dir)
            results.append(res)
            cell_, rc, elapsed, log = res
            tag = "OK" if rc == 0 else f"FAIL rc={rc}"
            print(f"[{kst()}] {cell_}: {tag}, {elapsed:.1f}s, log={log}")
    else:
        # parallel — ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=parallel) as ex:
            future_map = {
                ex.submit(launch_one, cell, output_dir, trials, n_queries, log_dir): cell
                for cell in cells
            }
            for fut in as_completed(future_map):
                cell = future_map[fut]
                try:
                    res = fut.result()
                    results.append(res)
                    cell_, rc, elapsed, log = res
                    tag = "OK" if rc == 0 else f"FAIL rc={rc}"
                    print(f"[{kst()}] {cell_}: {tag}, {elapsed:.1f}s, log={log}")
                except Exception as e:
                    print(f"[{kst()}] {cell}: EXCEPTION {type(e).__name__}: {e}")
                    results.append((cell, -1, 0.0, ""))

    t_wall = time.time() - t_total
    ok = sum(1 for (_, rc, _, _) in results if rc == 0)
    fail = len(results) - ok
    print(f"\n[{kst()}] portfolio done — {ok}/{len(cells)} OK, {fail} FAIL, "
          f"wall {t_wall:.1f}s ({t_wall / 60:.1f} min)")

    # summary 작성
    summary_path = output_dir / "portfolio_summary.md"
    with open(summary_path, "w") as fp:
        fp.write(f"# CaseC portfolio summary — v15 ({kst()})\n\n")
        fp.write(f"- cells: {len(cells)}, parallel={parallel}, trials={trials}, "
                 f"n_queries={n_queries}\n")
        fp.write(f"- wall time: {t_wall:.1f}s ({t_wall / 60:.1f} min)\n")
        fp.write(f"- OK / FAIL: {ok} / {fail}\n\n")
        fp.write("| cell | rc | elapsed_s |\n|---|--:|--:|\n")
        for cell_, rc, elapsed, _ in sorted(results):
            fp.write(f"| {cell_} | {rc} | {elapsed:.1f} |\n")
    print(f"[{kst()}] summary: {summary_path}")

    return {
        "cells_total": len(cells),
        "ok": ok,
        "fail": fail,
        "wall_s": t_wall,
        "results": results,
        "summary_path": str(summary_path),
    }


def _dry_run() -> None:
    print(f"=== dry-run: measure_offline_casec_portfolio ===")
    print(f"\nscript_path: {script_path()}")
    print(f"SERVER: {SERVER}")
    print(f"\nv14 carry cells ({len(V14_CELLS)}):")
    for c in V14_CELLS:
        print(f"  · {c}")
    print(f"\nNEW cells ({len(NEW_CELLS)}):")
    for c in NEW_CELLS:
        print(f"  · {c}")
    print(f"\nDEFAULT_PORTFOLIO total: {len(DEFAULT_PORTFOLIO)} cells")
    print(f"\nExample launch cmd (cell=A1-DEEP):")
    cmd = [
        sys.executable, "-u", str(script_path()),
        "--rq", "3", "--phase", "E",
        "--cell", "A1-DEEP",
        "--mode", "CaseC",
        "--n-queries", "1000",
        "--trials", "10",
        "--output", "/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v15_25cell_<TS>",
    ]
    print(f"  {' '.join(cmd)}")
    print("\n✓ dry-run 통과 — portfolio cell list·subprocess 구조 정상")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="오프라인 CaseC dual-Bernoulli portfolio 측정 wrapper")
    ap.add_argument("--cells", nargs="+", default=list(DEFAULT_PORTFOLIO),
                    help="측정 cell sub names (default: v14 9 + 신규 9 = 18)")
    ap.add_argument("--skip-v14-carry", action="store_true",
                    help="v14 carry 9 cell 건너뛰고 신규 9 cell 만")
    ap.add_argument("--trials", type=int, default=10,
                    help="trial 수 (paper §VI verbatim, v14 동일)")
    ap.add_argument("--n-queries", type=int, default=1000,
                    help="query 수 per trial (paper Fig 6 verbatim, v14 동일)")
    ap.add_argument("--output", type=Path,
                    default=Path(f"/mnt/hdd0/home/capstone2026/cache/rq3/"
                                  f"paper_exact_v15_{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M%S')}"))
    ap.add_argument("--parallel", type=int, default=1,
                    help="병렬 cell 수 (default 1 sequential — v14 와 동일 안전). "
                         "병렬 시 fetch_all_vectors 메모리 부하 (~10GB) × N 주의")
    ap.add_argument("--dry-run", action="store_true",
                    help="cell list + launch cmd 검증 (서버 불필요)")
    args = ap.parse_args()

    # Codex BLOCKER D — cell whitelist validation + duplicate 금지 (server check 이전)
    cells = args.cells
    unknown = [c for c in cells if c not in KNOWN_CELLS]
    if unknown:
        raise SystemExit(f"unknown cell sub names: {unknown}\n"
                         f"valid cells: {sorted(KNOWN_CELLS)}")
    if len(cells) != len(set(cells)):
        dup = [c for c in cells if cells.count(c) > 1]
        raise SystemExit(f"duplicate cell sub names: {sorted(set(dup))}")

    if args.dry_run:
        _dry_run()
        return

    if not SERVER:
        print("서버 전용 — 165.132.140.240 capstone2026 에서 실행")
        print("로컬에서는 --dry-run 만 가능")
        return

    if args.skip_v14_carry:
        cells = [c for c in cells if c not in V14_CELLS]
        print(f"[{kst()}] skip-v14-carry: {len(cells)} cells (신규 만)")

    run_portfolio(cells, args.output, args.trials, args.n_queries, args.parallel)


if __name__ == "__main__":
    main()
