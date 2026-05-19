#!/usr/bin/env python3
"""reorganize_chain_results_5_16.py

서버 sync 결과 (`_internal/cache/rq3/server_sync/`) →
production 영역 (`experiments/results/raw/Type{1..4b}/{cell}_RQ3_CaseB/`) reorganize.

5/15 chain 결과 cell 명 → Type 영역 mapping:

| 서버 cell                        | Type      | local target                                              |
|----------------------------------|-----------|-----------------------------------------------------------|
| A5-scale-sf1-SIFT                | Type1     | Type1_small_single_sf1/A5-scale-sf1-SIFT_RQ3_CaseB/      |
| A5-scale-sf1-SSN                 | Type1     | Type1_small_single_sf1/A5-scale-sf1-SSN_RQ3_CaseB/       |
| A6-WIKI-sf1                      | Type1     | Type1_small_single_sf1/A6-WIKI-sf1_RQ3_CaseB/            |
| A7-YFCC-sf1                      | Type1     | Type1_small_single_sf1/A7-YFCC-sf1_RQ3_CaseB/            |
| A5-scale-sf10-SIFT               | Type2     | Type2_medium_single_sf10/A5-scale-sf10-SIFT_RQ3_CaseB/   |
| A5-scale-sf10-SSN                | Type2     | Type2_medium_single_sf10/A5-scale-sf10-SSN_RQ3_CaseB/    |
| A6-WIKI-sf10                     | Type2     | Type2_medium_single_sf10/A6-WIKI-sf10_RQ3_CaseB/         |
| A1-SIFT_K10 / K30                | Type3     | Type3_large_single_sf100/SIFT_A1_K{10,30}_RQ3_CaseB/     |
| A1-SSN_K10 / K30                 | Type3     | Type3_large_single_sf100/SSN_A1_K{10,30}_RQ3_CaseB/      |
| A8-DEEP+SIFT-sf10                | Type4a    | Type4a_large_multi_288d/A8-DEEP+SIFT-sf10_RQ3_CaseB/     |
| (multi 864d 케이스 향후 추가)     | Type4b    | Type4b_large_multi_864d/...                               |

사용법:
  python3 reorganize_chain_results_5_16.py --dry-run
  python3 reorganize_chain_results_5_16.py
  python3 reorganize_chain_results_5_16.py --stage v6_caseB --dry-run

note: 기존 raw/Type{N}/{cell}_RQ3_CaseB/ 안에 동일 method json 있으면 overwrite.
사용자 확인 필요 시 --dry-run 으로 plan 먼저 출력.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

LOCAL_SYNC = Path("/Users/hyunbin/Capstone/_internal/cache/rq3/server_sync")
LOCAL_RAW = Path("/Users/hyunbin/Capstone/experiments/results/raw")

# stage → 5 stage 디렉토리 (sync script 와 동일)
STAGES = ["v6_caseB", "v7_extras", "v6v7_fix", "v10_full16", "v9_sel_sweep"]

# cell 명 → (Type 디렉토리, target subdir 이름)
CELL_MAP: dict[str, tuple[str, str]] = {
    # Type1 (sf1)
    "A5-scale-sf1-SIFT":   ("Type1_small_single_sf1", "A5-scale-sf1-SIFT_RQ3_CaseB"),
    "A5-scale-sf1-SSN":    ("Type1_small_single_sf1", "A5-scale-sf1-SSN_RQ3_CaseB"),
    "A6-WIKI-sf1":         ("Type1_small_single_sf1", "A6-WIKI-sf1_RQ3_CaseB"),
    "A7-YFCC-sf1":         ("Type1_small_single_sf1", "A7-YFCC-sf1_RQ3_CaseB"),
    # Type2 (sf10)
    "A5-scale-sf10-SIFT":  ("Type2_medium_single_sf10", "A5-scale-sf10-SIFT_RQ3_CaseB"),
    "A5-scale-sf10-SSN":   ("Type2_medium_single_sf10", "A5-scale-sf10-SSN_RQ3_CaseB"),
    "A6-WIKI-sf10":        ("Type2_medium_single_sf10", "A6-WIKI-sf10_RQ3_CaseB"),
    # Type3 (sf100, K granularity)
    "A1-SIFT_K10":         ("Type3_large_single_sf100", "SIFT_A1_K10_RQ3_CaseB"),
    "A1-SIFT_K30":         ("Type3_large_single_sf100", "SIFT_A1_K30_RQ3_CaseB"),
    "A1-SSN_K10":          ("Type3_large_single_sf100", "SSN_A1_K10_RQ3_CaseB"),
    "A1-SSN_K30":          ("Type3_large_single_sf100", "SSN_A1_K30_RQ3_CaseB"),
    # Type4a (multi 288d)
    "A8-DEEP+SIFT-sf10":   ("Type4a_large_multi_288d", "A8-DEEP+SIFT-sf10_RQ3_CaseB"),
    # Type4b — 향후 multi 864d 케이스 추가 시 여기 등록
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="실제 복사 없이 plan 출력")
    p.add_argument("--stage", choices=STAGES, help="특정 stage 만 처리")
    return p.parse_args()


def discover_cells(stage: str) -> list[Path]:
    """stage 디렉토리 안 cell 디렉토리 list (logs / COMPLETE.flag 제외)."""
    stage_dir = LOCAL_SYNC / stage
    if not stage_dir.exists():
        return []
    return sorted(
        d for d in stage_dir.iterdir()
        if d.is_dir() and d.name not in {"logs", "__pycache__"}
    )


def reorganize_cell(cell_dir: Path, dry_run: bool) -> tuple[int, int]:
    """cell 디렉토리 안 json file 들을 production 영역으로 copy.

    Returns (copied, skipped) count.
    """
    cell_name = cell_dir.name
    if cell_name not in CELL_MAP:
        print(f"  [WARN] unmapped cell: {cell_name} → 스킵 (CELL_MAP 추가 필요)")
        return 0, 0

    type_dir_name, target_subdir = CELL_MAP[cell_name]
    target_dir = LOCAL_RAW / type_dir_name / target_subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    for src in sorted(cell_dir.glob("*.json")):
        dst = target_dir / src.name
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            # size 동일 → 이미 sync 됨
            skipped += 1
            continue
        action = "COPY" if not dst.exists() else "OVERWRITE"
        print(f"  [{action}] {src.name} → {target_dir.relative_to(LOCAL_RAW.parent)}/")
        if not dry_run:
            shutil.copy2(src, dst)
        copied += 1
    return copied, skipped


def main() -> int:
    args = parse_args()

    if not LOCAL_SYNC.exists():
        print(f"[ERR] sync 영역 없음: {LOCAL_SYNC}", file=sys.stderr)
        print("먼저 ./_internal/scripts/sync_chain_results_5_16.sh 실행.", file=sys.stderr)
        return 1

    stages = [args.stage] if args.stage else STAGES
    print(f"[INFO] reorganize_chain_results_5_16.py")
    print(f"[INFO] mode={'DRY-RUN' if args.dry_run else 'EXECUTE'}")
    print(f"[INFO] stages={stages}")
    print()

    total_copied = 0
    total_skipped = 0

    for stage in stages:
        cells = discover_cells(stage)
        if not cells:
            print(f"===> [{stage}] (no cells, skip)")
            continue
        print(f"===> [{stage}] {len(cells)} cells")
        for cell_dir in cells:
            print(f"  cell: {cell_dir.name}")
            c, s = reorganize_cell(cell_dir, args.dry_run)
            total_copied += c
            total_skipped += s
        print()

    print(f"[SUMMARY] copied={total_copied}, skipped(=already)={total_skipped}")
    if args.dry_run:
        print("[INFO] dry-run — 파일 변경 없음. 실측은 --dry-run 빼고 재실행.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
