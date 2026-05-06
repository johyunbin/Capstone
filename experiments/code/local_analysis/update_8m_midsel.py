"""
update_8m_midsel.py — DEEP 8M × s={0.10, 0.30} 측정 결과 회수 + 분석 + 정리.md 갱신

Trigger 시나리오 (사용자 주도):
  1. 메인 세션이 서버에서 8M × s={0.10, 0.30} × KM20/RAND20/BERN 측정 후 parquet/json
     산출물을 본 레포에 push.
  2. 본 스크립트가 새 측정 파일을 자동 탐색하여:
     (a) DEEP 1M (mid-sel 보충 완료) + SIFT 1.5M 패턴과 5sel × 3 dataset gradient 단조성 비교
     (b) Two-Level Decomposition (Level 1 비례 배분 / Level 2 공간 인식) 갱신
     (c) `experiments/results/RQ1_RQ2 실험 결과 정리.md` 의 8M 관련 3 표 갱신
         - "DEEP 8M 결과 (외적 타당성)"
         - "실험 5: KM20 vs RANDOM20 — DEEP 8M"
         - "실험 6: Two-Level Decomposition — DEEP 8M 수치 분해"

본 파일은 *함수만* 정의한다. 실제 trigger 는 측정 파일이 들어온 후 메인 세션이
`python3 experiments/code/local_analysis/update_8m_midsel.py --update` 로 호출.

Usage:
  python3 update_8m_midsel.py --check        # 측정 파일 존재 확인만 (read-only)
  python3 update_8m_midsel.py --update       # 분석 + 정리.md in-place 갱신
  python3 update_8m_midsel.py --dry-run      # 분석 결과 stdout, md 갱신은 skip
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = REPO_ROOT / "experiments" / "results"
SUMMARY_MD = RESULTS_DIR / "RQ1_RQ2 실험 결과 정리.md"

T_CRITICAL_4DOF = 2.776  # t(4, 0.975), 5-seed 95% CI

# 비교 baseline — 정리.md 에 이미 들어가 있는 1M/SIFT 측정값 (mid-sel 포함)
BASELINE = {
    "DEEP_1M": {
        # KM20: 5-seed 평균 개선 % (BERN 대비)
        "km20": {0.50: 1.64, 0.30: 2.62, 0.10: 4.19, 0.05: 1.85, 0.01: 8.93},
        "rand20": {0.50: 2.20, 0.30: 0.26, 0.10: 1.74, 0.05: 0.79, 0.01: -10.67},
    },
    "SIFT_1_5M": {
        "km20": {0.50: 3.07, 0.05: 4.39, 0.01: -0.53},  # mid-sel 미측정
        "rand20": {0.50: 1.01, 0.05: -0.05, 0.01: -12.11},
    },
    "DEEP_8M": {
        # 기존 phase7 측정 (mid-sel 결측)
        "km20": {0.50: 1.76, 0.05: 0.55, 0.01: -0.71},
        "rand20": {0.50: 1.10, 0.05: 0.20, 0.01: 11.06},
    },
}


# ============================================================
# 0. 시간/유틸
# ============================================================


def kst_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now_iso()}] {msg}", flush=True)


def fmt_pct(x: float | None, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
        return "    -"
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.{digits}f}%"


def fmt_ci(lo: float | None, hi: float | None) -> str:
    if lo is None or hi is None or np.isnan(lo) or np.isnan(hi):
        return "[   -,    -]"
    return f"[{lo:+.2f}, {hi:+.2f}]"


# ============================================================
# 1. 측정 파일 탐색 (메인 세션이 push 한 새 8M mid-sel 산출)
# ============================================================


@dataclass
class MeasurementFile:
    """8M mid-sel 측정 파일 1개 (parquet 또는 json)."""

    path: Path
    fmt: str  # "parquet" | "json"
    sel: float  # 0.10 또는 0.30
    mode: str  # "km20" | "rand20" | "bern" | "mixed"


def discover_8m_midsel_files(
    search_dirs: list[Path] | None = None,
) -> list[MeasurementFile]:
    """8M × s={0.10, 0.30} 측정 산출물을 탐색.

    탐색 패턴 (메인 세션이 다음 위치 중 어디든 push 가능):
      - experiments/results/rq1_motivation/{8m_midsel_*, *_8m_s010*, *_8m_s030*}.parquet|json
      - experiments/results/rq2_aware/{8m_midsel_*, *_8m_s010*, *_8m_s030*}.parquet|json
      - experiments/results/rq2_aware/2026_05_06_alloc/{*8m*midsel*, *8m*s010*, *8m*s030*}.*

    파일명에서 selectivity (0.10 / 0.30) 와 mode (km20/rand20/bern) 를 추출.
    파일명 인코딩 안 되어 있으면 parquet 안 의 selectivity 컬럼으로 추론.
    """
    if search_dirs is None:
        # rq1_motivation, rq2_aware 의 직접 자식 + 모든 sub-directory (rglob)
        # measure.py 산출 위치 (예: rq1_motivation/2026_05_06_8m_midsel/) 도 포함.
        search_dirs = [
            RESULTS_DIR / "rq1_motivation",
            RESULTS_DIR / "rq2_aware",
        ]

    found: list[MeasurementFile] = []
    sel_re = re.compile(r"s0?\.?(?P<sel>010|030|0?10|0?30|0_10|0_30)", re.IGNORECASE)
    mode_re = re.compile(r"(km20|rand20|random20|bern(?:oulli)?)", re.IGNORECASE)
    midsel_marker = re.compile(r"(mid[\-_]?sel|midsel|s_?010|s_?030|s0\.10|s0\.30)", re.IGNORECASE)
    eight_m_marker = re.compile(r"8[\-_]?m|phase7_8m|8m_", re.IGNORECASE)

    for d in search_dirs:
        if not d.is_dir():
            continue
        for ext in ("parquet", "json"):
            for p in sorted(d.rglob(f"*.{ext}")):
                name = p.name.lower()
                if not eight_m_marker.search(name):
                    continue
                if not midsel_marker.search(name):
                    continue
                # selectivity 추출
                sel = None
                m = sel_re.search(name)
                if m:
                    raw = m.group("sel").replace("_", "").replace(".", "")
                    if raw in ("010", "10", "010"):
                        sel = 0.10
                    elif raw in ("030", "30", "030"):
                        sel = 0.30
                # mode 추출
                m2 = mode_re.search(name)
                mode = "mixed"
                if m2:
                    g = m2.group(1).lower()
                    if "km" in g:
                        mode = "km20"
                    elif "rand" in g:
                        mode = "rand20"
                    elif "bern" in g:
                        mode = "bern"
                if sel is None:
                    log(
                        f"  ! {p.name} — selectivity 미인식 (parquet 안 selectivity 컬럼 필요)"
                    )
                    sel = float("nan")
                found.append(MeasurementFile(path=p, fmt=ext, sel=sel, mode=mode))
    return found


# ============================================================
# 2. 측정 파일 로드 (parquet 또는 summary json)
# ============================================================


@dataclass
class CellMeasurement:
    """단일 (dataset, sel, mode) 의 5-seed 집계."""

    dataset: str  # "DEEP_8M"
    sel: float  # 0.10 / 0.30
    mode: str  # "km20" | "rand20"
    diff_pct_per_seed: list[float] = field(default_factory=list)  # BERN 대비 %
    p_per_seed: list[float] = field(default_factory=list)
    bern_med_per_seed: list[float] = field(default_factory=list)
    strat_med_per_seed: list[float] = field(default_factory=list)

    @property
    def mean_diff_pct(self) -> float:
        if not self.diff_pct_per_seed:
            return float("nan")
        return float(np.mean(self.diff_pct_per_seed))

    @property
    def std_diff_pct(self) -> float:
        if len(self.diff_pct_per_seed) < 2:
            return float("nan")
        return float(np.std(self.diff_pct_per_seed, ddof=1))

    @property
    def ci_t_based(self) -> tuple[float, float]:
        """t(n-1) 기반 95% CI."""
        n = len(self.diff_pct_per_seed)
        if n < 2:
            return (float("nan"), float("nan"))
        m = self.mean_diff_pct
        se = self.std_diff_pct / np.sqrt(n)
        # n=5 → t(4,0.975)=2.776; 다른 n 은 fallback 으로 1.96
        t = T_CRITICAL_4DOF if n == 5 else 1.96
        return (m - t * se, m + t * se)

    @property
    def n_significant_seeds(self) -> int:
        return sum(1 for p in self.p_per_seed if p < 0.05)


def load_summary_json(path: Path) -> dict[str, CellMeasurement]:
    """기존 random20_low_sel_summary.json / 8m_km20_s0500_5seed.json 형태 처리.

    반환: {f"{mode}_s{sel}": CellMeasurement, ...}
    """
    raw = json.loads(path.read_text())
    out: dict[str, CellMeasurement] = {}
    if "sels" in raw:
        # 형식 A: {"sels": {"s0.01": {"km20": {...}, "rand": {...}}, ...}}
        for sk, modes in raw["sels"].items():
            sel = float(sk.replace("s", ""))
            for mode_key, mode_data in modes.items():
                mode = "km20" if "km" in mode_key.lower() else (
                    "rand20" if "rand" in mode_key.lower() else mode_key
                )
                cell = CellMeasurement(dataset="DEEP_8M", sel=sel, mode=mode)
                for ps in mode_data.get("per_seed", []):
                    cell.diff_pct_per_seed.append(float(ps["diff_pct"]))
                    cell.p_per_seed.append(float(ps.get("p", float("nan"))))
                    cell.bern_med_per_seed.append(float(ps.get("bern_med", float("nan"))))
                    cell.strat_med_per_seed.append(float(ps.get("strat_med", float("nan"))))
                out[f"{mode}_s{sel:.2f}"] = cell
    elif "per_seed" in raw:
        # 형식 B: {"per_seed": [...], "aggregate": {...}} — 단일 (sel, mode) 단위
        # 파일명에서 sel/mode 추론
        name = path.stem.lower()
        sel = 0.10 if "s010" in name or "s0.10" in name else (
            0.30 if "s030" in name or "s0.30" in name else (
                0.50 if "s0500" in name or "s0.50" in name else float("nan")
            )
        )
        mode = "km20" if "km" in name else ("rand20" if "rand" in name else "km20")
        cell = CellMeasurement(dataset="DEEP_8M", sel=sel, mode=mode)
        for ps in raw["per_seed"]:
            cell.diff_pct_per_seed.append(float(ps["diff_pct"]))
            cell.p_per_seed.append(float(ps.get("p", float("nan"))))
            cell.bern_med_per_seed.append(float(ps.get("bern_med", float("nan"))))
            cell.strat_med_per_seed.append(float(ps.get("strat_med", float("nan"))))
        out[f"{mode}_s{sel:.2f}"] = cell
    elif "per_cell_stats" in raw:
        # 형식 C: phase7_8m_midsel_meta.json (measure.py 산출).
        #   {"per_cell_stats": [
        #       {"sel_target": 0.10, "comparison": "system vs bernoulli", ...},
        #       {"sel_target": 0.10, "comparison": "stratified vs bernoulli", ...},
        #       ...
        #   ]}
        # comparison "stratified vs bernoulli" → km20 cell (RAND20 측정 없음)
        # comparison "system vs bernoulli" → RQ1 SYSTEM-block (별도 추적, sys20 mode)
        for stat in raw["per_cell_stats"]:
            sel = float(stat["sel_target"])
            comp = stat.get("comparison", "")
            if "stratified" in comp:
                mode = "km20"
            elif "system" in comp:
                mode = "sys20"  # 별도 — RQ1 narrative 용
            else:
                continue
            cell = CellMeasurement(dataset="DEEP_8M", sel=sel, mode=mode)
            for ps in stat.get("per_seed", []):
                cell.diff_pct_per_seed.append(float(ps["diff_pct"]))
                cell.p_per_seed.append(float(ps.get("p", float("nan"))))
                # phase7 meta 의 키는 med_a (mode_a=stratified), med_b (mode_b=bernoulli)
                cell.bern_med_per_seed.append(float(ps.get("med_b", float("nan"))))
                cell.strat_med_per_seed.append(float(ps.get("med_a", float("nan"))))
            out[f"{mode}_s{sel:.2f}"] = cell
    return out


def load_phase7_midsel_parquet(path: Path) -> dict[str, CellMeasurement]:
    """measure.py 의 단일 parquet (`phase7_8m_midsel.parquet`) 분해.

    Schema: ['query_id', 'true_card', 'plan_rows', 'q_error', 'hook_est',
             'q_error_hook', 'sel_target', 'mode', 'seed', 'actual_sel_med', 'error']
    mode ∈ {'system', 'bernoulli', 'stratified'}
    sel_target ∈ {0.10, 0.30}
    seed ∈ {0.1, 0.2, 0.3, 0.4, 0.5}

    paired Wilcoxon: (mode_a, bernoulli) per (sel, seed) → cell 의 5-seed diff_pct.
    q_error_hook 컬럼 우선 사용 (phase7 의 hook 추정 q-error).
    """
    try:
        import pyarrow.parquet as pq
        from scipy.stats import wilcoxon
    except ImportError as e:
        log(f"  ! 의존성 미설치 — {e}")
        return {}

    df = pq.read_table(path).to_pandas()
    if "mode" not in df.columns or "sel_target" not in df.columns:
        log(f"  ! {path.name}: schema 미일치 (mode/sel_target 컬럼 없음)")
        return {}

    qcol = "q_error_hook" if "q_error_hook" in df.columns else "q_error"
    out: dict[str, CellMeasurement] = {}
    sel_targets = sorted(df["sel_target"].dropna().unique())
    seeds = sorted(df["seed"].dropna().unique()) if "seed" in df.columns else [None]

    for sel in sel_targets:
        sub = df[df["sel_target"] == sel]
        bern = sub[sub["mode"] == "bernoulli"]
        if len(bern) == 0:
            continue
        for mode_a, cell_mode in (("stratified", "km20"), ("system", "sys20")):
            mode_a_df = sub[sub["mode"] == mode_a]
            if len(mode_a_df) == 0:
                continue
            cell = CellMeasurement(dataset="DEEP_8M", sel=float(sel), mode=cell_mode)
            for sd in seeds:
                if sd is None:
                    a = mode_a_df[[ "query_id", qcol]].rename(columns={qcol: "qa"})
                    b = bern[[ "query_id", qcol]].rename(columns={qcol: "qb"})
                else:
                    a = mode_a_df[mode_a_df["seed"] == sd][["query_id", qcol]].rename(
                        columns={qcol: "qa"}
                    )
                    b = bern[bern["seed"] == sd][["query_id", qcol]].rename(
                        columns={qcol: "qb"}
                    )
                pair = a.merge(b, on="query_id").dropna()
                if len(pair) == 0:
                    continue
                ma = float(np.median(pair["qa"]))
                mb = float(np.median(pair["qb"]))
                diff = (mb - ma) / mb * 100.0 if mb > 0 else 0.0
                try:
                    p = float(
                        wilcoxon(
                            pair["qa"].values,
                            pair["qb"].values,
                            alternative="less",
                            zero_method="wilcox",
                        ).pvalue
                    )
                except Exception:
                    p = float("nan")
                cell.diff_pct_per_seed.append(diff)
                cell.p_per_seed.append(p)
                cell.bern_med_per_seed.append(mb)
                cell.strat_med_per_seed.append(ma)
            if cell.diff_pct_per_seed:
                out[f"{cell_mode}_s{float(sel):.2f}"] = cell
    return out


def load_parquet_pair(
    bern_path: Path, strat_path: Path, mode: str, sel_filter: float | None = None
) -> CellMeasurement | None:
    """phase7 형태 (query_id × seed × selectivity → q_error) 의 BERN/STRAT pair 로드.

    파일 schema: ['query_id', 'selectivity', 'D_target', 'true_card', 'plan_rows',
                  'q_error', 'error', 'hook_est', 'q_error_hook'] + (있으면) 'seed'

    seed 컬럼이 없으면 단일 seed 측정으로 가정.
    """
    try:
        import pyarrow.parquet as pq
    except ImportError:
        log("  ! pyarrow 미설치 — parquet 처리 skip")
        return None

    bern = pq.read_table(bern_path).to_pandas()
    strat = pq.read_table(strat_path).to_pandas()

    if sel_filter is not None:
        bern = bern[np.isclose(bern["selectivity"], sel_filter)]
        strat = strat[np.isclose(strat["selectivity"], sel_filter)]

    if len(bern) == 0 or len(strat) == 0:
        return None

    sel_actual = float(bern["selectivity"].median())
    cell = CellMeasurement(dataset="DEEP_8M", sel=sel_actual, mode=mode)

    if "seed" in bern.columns and "seed" in strat.columns:
        seeds = sorted(set(bern["seed"].unique()) & set(strat["seed"].unique()))
        for sd in seeds:
            b_qe = bern[bern["seed"] == sd]["q_error"].values
            s_qe = strat[strat["seed"] == sd]["q_error"].values
            if len(b_qe) == 0 or len(s_qe) == 0:
                continue
            b_med = float(np.median(b_qe))
            s_med = float(np.median(s_qe))
            diff = (b_med - s_med) / b_med * 100.0 if b_med > 0 else 0.0
            try:
                from scipy.stats import wilcoxon

                # paired query_id 매칭 (정렬해서 1:1)
                if len(b_qe) == len(s_qe):
                    _, p = wilcoxon(b_qe, s_qe, alternative="greater")
                else:
                    p = float("nan")
            except Exception:
                p = float("nan")
            cell.diff_pct_per_seed.append(diff)
            cell.p_per_seed.append(float(p))
            cell.bern_med_per_seed.append(b_med)
            cell.strat_med_per_seed.append(s_med)
    else:
        # 단일 seed
        b_med = float(np.median(bern["q_error"]))
        s_med = float(np.median(strat["q_error"]))
        diff = (b_med - s_med) / b_med * 100.0 if b_med > 0 else 0.0
        cell.diff_pct_per_seed.append(diff)
        cell.bern_med_per_seed.append(b_med)
        cell.strat_med_per_seed.append(s_med)

    return cell


def load_all_8m_midsel(files: list[MeasurementFile]) -> dict[str, CellMeasurement]:
    """탐색된 측정 파일 모두 로드 → {cell_key: CellMeasurement} 통합."""
    cells: dict[str, CellMeasurement] = {}
    json_files = [f for f in files if f.fmt == "json"]
    parquet_files = [f for f in files if f.fmt == "parquet"]

    for jf in json_files:
        try:
            partial = load_summary_json(jf.path)
            log(f"  + {jf.path.name}: {len(partial)} cell")
            cells.update(partial)
        except Exception as e:
            log(f"  ! {jf.path.name} 로드 실패: {e}")

    # parquet 처리 — 우선 phase7 단일 parquet 인지 확인 (mode 컬럼 자동 분해)
    handled_paths: set[Path] = set()
    for pf in parquet_files:
        # phase7_8m_midsel.parquet 패턴 (mode + sel_target 컬럼 보유)
        try:
            import pyarrow.parquet as pq

            schema = pq.read_schema(pf.path)
            cols = {f.name for f in schema}
            if "mode" in cols and "sel_target" in cols:
                partial = load_phase7_midsel_parquet(pf.path)
                log(f"  + {pf.path.name} (phase7-style): {len(partial)} cell")
                cells.update(partial)
                handled_paths.add(pf.path)
        except Exception as e:
            log(f"  ! {pf.path.name} schema 확인 실패: {e}")

    # 나머지 parquet — 기존 BERN/STRAT pair 패턴 (selectivity 단일 컬럼)
    by_sel: dict[float, dict[str, list[Path]]] = {}
    for pf in parquet_files:
        if pf.path in handled_paths:
            continue
        sel_key = pf.sel
        by_sel.setdefault(sel_key, {}).setdefault(pf.mode, []).append(pf.path)

    for sel, modes in by_sel.items():
        bern_paths = modes.get("bern", [])
        for stratified_mode in ("km20", "rand20"):
            strat_paths = modes.get(stratified_mode, [])
            if bern_paths and strat_paths:
                cell = load_parquet_pair(
                    bern_paths[0], strat_paths[0], stratified_mode, sel_filter=sel
                )
                if cell is not None:
                    key = f"{stratified_mode}_s{sel:.2f}"
                    log(f"  + parquet pair → {key}: {len(cell.diff_pct_per_seed)} seed")
                    cells[key] = cell
    return cells


# ============================================================
# 3. Gradient 단조성 매트릭스 (5sel × 3 dataset)
# ============================================================


@dataclass
class GradientCell:
    dataset: str
    sel: float
    km20_diff: float
    rand20_diff: float

    @property
    def gap(self) -> float:
        return self.km20_diff - self.rand20_diff


def build_gradient_matrix(
    new_8m: dict[str, CellMeasurement],
) -> dict[str, dict[float, GradientCell]]:
    """5sel × 3 dataset gradient — DEEP 1M / SIFT 1.5M / DEEP 8M.

    DEEP 1M 은 BASELINE 에서 직접, SIFT 1.5M 은 측정 cell 만, DEEP 8M 은 baseline +
    new_8m 의 mid-sel 측정 (있으면 덮어씀).
    """
    matrix: dict[str, dict[float, GradientCell]] = {
        "DEEP_1M": {},
        "SIFT_1_5M": {},
        "DEEP_8M": {},
    }

    # DEEP 1M: 5 sel 모두
    for sel, km in BASELINE["DEEP_1M"]["km20"].items():
        rd = BASELINE["DEEP_1M"]["rand20"].get(sel, float("nan"))
        matrix["DEEP_1M"][sel] = GradientCell("DEEP_1M", sel, km, rd)

    # SIFT 1.5M: baseline 만 (3 sel)
    for sel, km in BASELINE["SIFT_1_5M"]["km20"].items():
        rd = BASELINE["SIFT_1_5M"]["rand20"].get(sel, float("nan"))
        matrix["SIFT_1_5M"][sel] = GradientCell("SIFT_1_5M", sel, km, rd)

    # DEEP 8M: baseline 3 sel + new_8m 의 mid-sel
    for sel, km in BASELINE["DEEP_8M"]["km20"].items():
        rd = BASELINE["DEEP_8M"]["rand20"].get(sel, float("nan"))
        matrix["DEEP_8M"][sel] = GradientCell("DEEP_8M", sel, km, rd)
    for key, cell in new_8m.items():
        sel = cell.sel
        # phase7 measure.py 산출: km20 / sys20 만 있고 rand20 측정 없음.
        # 따라서 mid-sel (s=0.10, 0.30) 의 RAND20 은 NaN 으로 두고,
        # Two-Level Decomposition 의 Level 1 자리는 "(미측정)" 으로 표시.
        if cell.mode == "km20":
            existing = matrix["DEEP_8M"].get(sel)
            rd = existing.rand20_diff if existing else float("nan")
            matrix["DEEP_8M"][sel] = GradientCell(
                "DEEP_8M", sel, cell.mean_diff_pct, rd
            )
        elif cell.mode == "rand20":
            existing = matrix["DEEP_8M"].get(sel)
            km = existing.km20_diff if existing else float("nan")
            matrix["DEEP_8M"][sel] = GradientCell(
                "DEEP_8M", sel, km, cell.mean_diff_pct
            )
        # sys20 (system vs bernoulli) 는 RQ1 narrative 영역 — gradient matrix 에는 X.

    return matrix


def collect_sys20_cells(new_8m: dict[str, CellMeasurement]) -> dict[float, CellMeasurement]:
    """phase7 measure.py 의 'system vs bernoulli' (sys20) cell 만 추출.

    8M 의 SYSTEM-block sampling 효과 — RQ1 cross-dataset narrative 보강용.
    sel → CellMeasurement 매핑. 기존 8M (s=0.50) phase7_8m_bern/strat parquet 측정에는
    SYSTEM mode 가 없으므로 mid-sel (s=0.10, 0.30) 만.
    """
    out: dict[float, CellMeasurement] = {}
    for key, cell in new_8m.items():
        if cell.mode == "sys20":
            out[cell.sel] = cell
    return out


def check_km20_monotonicity(
    matrix: dict[str, dict[float, GradientCell]],
) -> dict[str, dict[str, Any]]:
    """KM20 only gradient 단조성 (RAND20 부재시 fallback).

    KM20 의 BERN 대비 개선 % 가 sel 좁아질수록 커지는가? — 8M mid-sel 구간만 측정된
    경우에 사용. gap 기반 단조성 (check_gradient_monotonicity) 의 대체 metric.
    """
    out: dict[str, dict[str, Any]] = {}
    for ds, cells in matrix.items():
        sels = sorted(cells.keys(), reverse=True)
        kms = [cells[s].km20_diff for s in sels]
        valid = [(s, k) for s, k in zip(sels, kms) if not (np.isnan(s) or np.isnan(k))]
        if len(valid) < 2:
            out[ds] = {"valid_n": len(valid), "monotonic": None}
            continue
        vsels, vkms = zip(*valid)
        diffs = [vkms[i + 1] - vkms[i] for i in range(len(vkms) - 1)]
        n_inc = sum(1 for d in diffs if d > 0)
        n_dec = sum(1 for d in diffs if d < 0)
        out[ds] = {
            "valid_n": len(valid),
            "sels_desc": list(vsels),
            "km20_pcts": list(vkms),
            "diffs": diffs,
            "n_increase": n_inc,
            "n_decrease": n_dec,
            "monotonic_strict": all(d > 0 for d in diffs),
            "monotonic_weak": all(d >= 0 for d in diffs),
        }
    return out


def check_gradient_monotonicity(
    matrix: dict[str, dict[float, GradientCell]],
) -> dict[str, dict[str, Any]]:
    """gradient 단조성 (sel 작을수록 KM-RAND gap 커지는가) 검증.

    DEEP 8M mid-sel (s=0.10, 0.30) 은 RAND20 미측정 → gap 산출 불가 (NaN) →
    valid 에서 자동 제외. 따라서 8M 단조성은 측정된 sel (0.50, 0.05, 0.01) 만
    기준으로 평가됨. mid-sel 보강은 KM20 only gradient 의 단조성으로 별도 평가.
    """
    out: dict[str, dict[str, Any]] = {}
    for ds, cells in matrix.items():
        sels = sorted(cells.keys(), reverse=True)  # 0.5 → 0.01
        gaps = [cells[s].gap for s in sels]
        # NaN 제외 (RAND20 미측정 영역)
        valid = [(s, g) for s, g in zip(sels, gaps) if not (np.isnan(s) or np.isnan(g))]
        if len(valid) < 2:
            out[ds] = {"valid_n": len(valid), "monotonic": None}
            continue
        valid_sels, valid_gaps = zip(*valid)
        diffs = [valid_gaps[i + 1] - valid_gaps[i] for i in range(len(valid_gaps) - 1)]
        n_increase = sum(1 for d in diffs if d > 0)
        n_decrease = sum(1 for d in diffs if d < 0)
        is_strict = all(d > 0 for d in diffs)
        is_weak = all(d >= 0 for d in diffs)
        out[ds] = {
            "valid_n": len(valid),
            "sels_desc": list(valid_sels),
            "gaps": list(valid_gaps),
            "diffs": diffs,
            "n_increase": n_increase,
            "n_decrease": n_decrease,
            "monotonic_strict": is_strict,
            "monotonic_weak": is_weak,
        }
    return out


# ============================================================
# 4. Two-Level Decomposition (Level 1 / Level 2 / Total)
# ============================================================


@dataclass
class DecompositionRow:
    sel: float
    level_1: float  # RAND20 mean diff_pct
    level_2: float  # KM20 - RAND20
    total: float  # KM20 mean diff_pct


def build_decomposition(
    matrix: dict[str, dict[float, GradientCell]], dataset: str
) -> list[DecompositionRow]:
    """Two-Level Decomposition row 산출 — 1 dataset 의 모든 sel."""
    rows: list[DecompositionRow] = []
    cells = matrix.get(dataset, {})
    for sel in sorted(cells.keys(), reverse=True):
        c = cells[sel]
        level_1 = c.rand20_diff
        total = c.km20_diff
        level_2 = total - level_1 if not (np.isnan(total) or np.isnan(level_1)) else float("nan")
        rows.append(DecompositionRow(sel=sel, level_1=level_1, level_2=level_2, total=total))
    return rows


# ============================================================
# 5. 정리.md 갱신 (8M 표 3종)
# ============================================================


def render_8m_extended_validity_table(
    matrix: dict[str, dict[float, GradientCell]],
    new_8m: dict[str, CellMeasurement],
) -> str:
    """실험 4 의 'DEEP 8M 결과 (외적 타당성)' KM20-only 표 렌더링."""
    cells = matrix["DEEP_8M"]
    rows = []
    for sel in sorted(cells.keys(), reverse=True):
        c = cells[sel]
        # 측정 cell 이 있으면 CI / 유의 seed 같이 표기
        meas = new_8m.get(f"km20_s{sel:.2f}")
        if meas is not None and meas.diff_pct_per_seed:
            ci_lo, ci_hi = meas.ci_t_based
            ci_str = fmt_ci(ci_lo, ci_hi)
            sig = f"{meas.n_significant_seeds}/{len(meas.diff_pct_per_seed)}"
        else:
            ci_str = "(기존측정)"
            sig = "-"
        rows.append(
            f"| {sel*100:.0f}% | **{fmt_pct(c.km20_diff)}** | {ci_str} | {sig} |"
        )
    header = (
        "| selectivity | 5-seed 평균 개선 | 95% CI | 유의한 seed |\n"
        "|-------------|-----------------|--------|------------|\n"
    )
    return header + "\n".join(rows)


def render_8m_km_vs_rand_table(
    matrix: dict[str, dict[float, GradientCell]],
) -> str:
    """실험 5 의 'DEEP 8M' KM20 vs RANDOM20 격차 표."""
    cells = matrix["DEEP_8M"]
    rows = []
    for sel in sorted(cells.keys(), reverse=True):
        c = cells[sel]
        rows.append(
            f"| {sel*100:.0f}% | {fmt_pct(c.km20_diff)} | {fmt_pct(c.rand20_diff)} "
            f"| {fmt_pct(c.gap, digits=1).replace('%', '%p')} |"
        )
    header = (
        "| selectivity | KM20 | RANDOM20 | 격차 |\n"
        "|-------------|------|----------|------|\n"
    )
    return header + "\n".join(rows)


def render_8m_two_level_table(
    matrix: dict[str, dict[float, GradientCell]],
) -> str:
    """실험 6 의 'DEEP 8M 수치 분해' Two-Level 표.

    measure.py 산출에는 RANDOM20 mid-sel 측정이 없으므로 mid-sel (0.10, 0.30) 의
    Level 1/Level 2 는 NaN → '(RAND20 미측정)' 표시. 학술적 한계 명시 차원.
    """
    rows_dec = build_decomposition(matrix, "DEEP_8M")
    rows = []
    for r in rows_dec:
        if np.isnan(r.level_1):
            l1 = "(RAND20 미측정)"
            l2 = "(분해 불가)"
        else:
            l1 = fmt_pct(r.level_1)
            l2 = fmt_pct(r.level_2)
        rows.append(
            f"| {r.sel*100:.0f}% | {l1} | {l2} | {fmt_pct(r.total)} |"
        )
    header = (
        "| selectivity | Level 1 (비례 배분) | Level 2 (공간 인식) | Total (KM20) |\n"
        "|-------------|--------------------|--------------------|-------------|\n"
    )
    return header + "\n".join(rows)


def render_sys20_8m_block(
    sys20: dict[float, CellMeasurement],
) -> str:
    """8M 의 SYSTEM-block sampling 효과 (sys20 cell) — RQ1 cross-dataset narrative 보강.

    1M/SIFT 의 RQ1 SYSTEM-BERN 격차 (실험 #1 결과) 와 동일 metric 으로 비교 가능.
    """
    if not sys20:
        return ""
    lines = ["### DEEP 8M × SYSTEM-block 효과 (RQ1 cross-dataset 보강)\n"]
    lines.append(
        "phase7 8M mid-sel 측정에서 같이 산출된 SYSTEM-block sampling 효과 "
        "(BERN 대비 격차) — RQ1 의 cross-dataset 비교 (1M/SIFT/8M) 에 활용.\n"
    )
    lines.append("| sel | DEEP 8M Δ% (SYS−BERN) | 95% CI | 유의 seed |")
    lines.append("|---|---|---|---|")
    for sel in sorted(sys20.keys()):
        c = sys20[sel]
        ci_lo, ci_hi = c.ci_t_based
        ci_str = fmt_ci(ci_lo, ci_hi)
        sig = f"{c.n_significant_seeds}/{len(c.diff_pct_per_seed)}"
        lines.append(f"| {sel*100:.0f}% | **{fmt_pct(c.mean_diff_pct)}** | {ci_str} | {sig} |")
    return "\n".join(lines)


def render_gradient_consistency_block(
    matrix: dict[str, dict[float, GradientCell]],
    monotonicity: dict[str, dict[str, Any]],
) -> str:
    """5sel × 3 dataset gradient 일관성 요약 블록."""
    lines = ["### 5sel × 3 dataset gradient 일관성 (8M mid-sel 보강 후)\n"]
    lines.append(
        "| sel | DEEP 1M (KM gap) | SIFT 1.5M (KM gap) | DEEP 8M (KM gap) |"
    )
    lines.append("|-----|-----------------|--------------------|-------------------|")
    all_sels = sorted(
        set(matrix["DEEP_1M"]) | set(matrix["SIFT_1_5M"]) | set(matrix["DEEP_8M"]),
        reverse=True,
    )
    for sel in all_sels:
        row = [f"{sel*100:.0f}%"]
        for ds in ("DEEP_1M", "SIFT_1_5M", "DEEP_8M"):
            c = matrix[ds].get(sel)
            if c is None:
                row.append("-")
            else:
                row.append(f"{fmt_pct(c.km20_diff)} (gap {fmt_pct(c.gap, 1)})")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("**단조성 판정 (sel 좁아질수록 KM-RAND gap 증가):**")
    for ds, m in monotonicity.items():
        if m.get("monotonic_strict"):
            verdict = "✓ 엄격 단조 증가"
        elif m.get("monotonic_weak"):
            verdict = "○ 약 단조 증가 (등호 허용)"
        elif m.get("n_increase", 0) >= m.get("valid_n", 0) - 2:
            verdict = f"~ 부분 단조 (반례 {m.get('n_decrease', 0)}건)"
        else:
            verdict = f"✗ 비단조 (증 {m.get('n_increase', 0)} / 감 {m.get('n_decrease', 0)})"
        lines.append(f"- **{ds}**: {verdict} (n={m.get('valid_n', 0)})")
    return "\n".join(lines)


def update_summary_md(
    md_path: Path,
    new_8m: dict[str, CellMeasurement],
    matrix: dict[str, dict[float, GradientCell]],
    monotonicity: dict[str, dict[str, Any]],
    dry_run: bool = False,
) -> bool:
    """정리.md 의 8M 관련 표 in-place 갱신.

    교체 대상 섹션:
      (a) "### DEEP 8M 결과 (외적 타당성)" 직후 첫 표
      (b) "### DEEP 8M\n\n| selectivity | KM20 (CI) ..." (실험 5)
      (c) "### DEEP 8M 수치 분해" 직후 첫 표
    또한 "## 보충 실험 상태" 직전에 gradient 일관성 블록 삽입.

    dry_run=True 면 변경 사항 stdout 만 출력.
    """
    if not md_path.exists():
        log(f"  ! 정리.md 없음: {md_path}")
        return False
    text = md_path.read_text()
    original = text

    # (a) 외적 타당성 표 — "### DEEP 8M 결과 (외적 타당성)\n\n" 다음 첫 표 블록
    new_a = render_8m_extended_validity_table(matrix, new_8m)
    text = _replace_table_after_heading(
        text, "### DEEP 8M 결과 (외적 타당성)", new_a
    )

    # (b) 실험 5 의 DEEP 8M 표 — "### DEEP 8M\n\n" (앞에 KM20 vs RANDOM20 컨텍스트)
    #     + 다음 표 (KM20 (CI) | RANDOM20 (CI))
    new_b = render_8m_km_vs_rand_table(matrix)
    # CI 컬럼 형태 유지 위해 Wide 버전으로 재포맷 (기존: KM20 (CI) | RANDOM20 (CI) | 격차)
    text = _replace_8m_km_vs_rand_in_exp5(text, matrix, new_8m)

    # (c) Two-Level Decomposition DEEP 8M 표
    new_c = render_8m_two_level_table(matrix)
    text = _replace_table_after_heading(
        text, "### DEEP 8M 수치 분해", new_c
    )

    # (d) gradient 일관성 블록 — "## 보충 실험 상태" 직전에 삽입 (기존 블록 있으면 교체)
    consistency_block = render_gradient_consistency_block(matrix, monotonicity)
    text = _upsert_consistency_block(text, consistency_block)

    if dry_run:
        log("=== [dry-run] 갱신될 섹션 미리보기 ===")
        log("(a) 외적 타당성 표:\n" + new_a)
        log("(b) KM20 vs RANDOM20 표:\n" + new_b)
        log("(c) Two-Level 표:\n" + new_c)
        log("(d) gradient 일관성 블록:\n" + consistency_block)
        return text != original

    if text != original:
        md_path.write_text(text)
        log(f"  ✓ 정리.md 갱신 완료 ({len(text) - len(original):+d} chars)")
        return True
    log("  ~ 정리.md 변경 없음 (이미 최신)")
    return False


def _replace_table_after_heading(text: str, heading: str, new_table: str) -> str:
    """heading 다음 첫 markdown 표 블록을 new_table 로 교체."""
    idx = text.find(heading)
    if idx < 0:
        return text
    # heading 이후 첫 "| " 로 시작하는 line 부터 빈 줄 전까지가 표
    after = text[idx + len(heading):]
    table_start = after.find("\n|")
    if table_start < 0:
        return text
    table_abs_start = idx + len(heading) + table_start + 1
    # table 끝: 첫 빈 줄 (\n\n)
    table_end_rel = text[table_abs_start:].find("\n\n")
    if table_end_rel < 0:
        table_end_abs = len(text)
    else:
        table_end_abs = table_abs_start + table_end_rel
    return text[:table_abs_start] + new_table + text[table_end_abs:]


def _replace_8m_km_vs_rand_in_exp5(
    text: str,
    matrix: dict[str, dict[float, GradientCell]],
    new_8m: dict[str, CellMeasurement],
) -> str:
    """실험 5 의 'DEEP 8M' 섹션 표를 CI 포함 형식으로 교체.

    기존 표 형식:
      | selectivity | KM20 (CI) | RANDOM20 (CI) | 격차 |
    """
    cells = matrix["DEEP_8M"]
    rows = []
    for sel in sorted(cells.keys(), reverse=True):
        c = cells[sel]
        km_meas = new_8m.get(f"km20_s{sel:.2f}")
        rd_meas = new_8m.get(f"rand20_s{sel:.2f}")
        km_str = fmt_pct(c.km20_diff)
        rd_str = fmt_pct(c.rand20_diff)
        if km_meas is not None and km_meas.diff_pct_per_seed:
            ci_lo, ci_hi = km_meas.ci_t_based
            km_str = f"{fmt_pct(c.km20_diff)} {fmt_ci(ci_lo, ci_hi)}"
        if rd_meas is not None and rd_meas.diff_pct_per_seed:
            ci_lo, ci_hi = rd_meas.ci_t_based
            rd_str = f"{fmt_pct(c.rand20_diff)} {fmt_ci(ci_lo, ci_hi)}"
        gap_str = fmt_pct(c.gap, 1).replace("%", "%p")
        rows.append(f"| {sel*100:.0f}% | {km_str} | {rd_str} | {gap_str} |")
    header = (
        "| selectivity | KM20 (CI) | RANDOM20 (CI) | 격차 |\n"
        "|-------------|-----------|---------------|------|"
    )
    new_table = header + "\n" + "\n".join(rows)
    # 실험 5 → "### DEEP 8M\n\n| selectivity | KM20 (CI)" 패턴
    pattern = re.compile(
        r"(### DEEP 8M\n\n)(\| selectivity \| KM20 \(CI\)[^\n]*\n[^\n]*\n(?:\|[^\n]+\n)+)"
    )
    return pattern.sub(lambda m: m.group(1) + new_table + "\n", text, count=1)


def _upsert_consistency_block(text: str, block: str) -> str:
    """gradient 일관성 블록 — '## 보충 실험 상태' 직전에 upsert.

    이미 '### 5sel × 3 dataset gradient 일관성' 헤더가 있으면 그 블록 교체.
    없으면 '## 보충 실험 상태' 직전 또는 문서 끝에 삽입.
    """
    marker = "### 5sel × 3 dataset gradient 일관성"
    if marker in text:
        # 기존 블록 교체: marker 부터 다음 ## (또는 ###) 까지
        start = text.find(marker)
        rest = text[start:]
        # 다음 H2 또는 H3 (단, 자기 자신 제외)
        m = re.search(r"\n(##[^#])", rest[1:])
        if m:
            end = start + 1 + m.start()
            return text[:start] + block + "\n\n" + text[end:].lstrip("\n")
        return text[:start] + block + "\n"
    # 신규 삽입: '## 보충 실험 상태' 직전, 없으면 문서 끝
    insert_marker = "## 보충 실험 상태"
    if insert_marker in text:
        idx = text.find(insert_marker)
        return text[:idx] + block + "\n\n---\n\n" + text[idx:]
    return text.rstrip() + "\n\n---\n\n" + block + "\n"


# ============================================================
# 6. 종합 리포트 (stdout)
# ============================================================


def print_report(
    files: list[MeasurementFile],
    cells: dict[str, CellMeasurement],
    matrix: dict[str, dict[float, GradientCell]],
    monotonicity: dict[str, dict[str, Any]],
) -> None:
    log("=" * 70)
    log("8M mid-sel 분석 리포트")
    log("=" * 70)

    log(f"\n탐색된 측정 파일: {len(files)}")
    for f in files:
        log(f"  - {f.path.relative_to(REPO_ROOT)} ({f.fmt}, sel={f.sel}, mode={f.mode})")

    log(f"\n로드된 cell: {len(cells)}")
    for k, c in sorted(cells.items()):
        ci_lo, ci_hi = c.ci_t_based
        log(
            f"  {k}: {fmt_pct(c.mean_diff_pct)} {fmt_ci(ci_lo, ci_hi)} "
            f"(n={len(c.diff_pct_per_seed)}, sig={c.n_significant_seeds})"
        )

    log("\n--- Gradient 매트릭스 (5sel × 3 dataset, KM-RAND gap) ---")
    all_sels = sorted(
        set(matrix["DEEP_1M"]) | set(matrix["SIFT_1_5M"]) | set(matrix["DEEP_8M"]),
        reverse=True,
    )
    log(f"  {'sel':>6} | {'DEEP_1M':>20} | {'SIFT_1_5M':>20} | {'DEEP_8M':>20}")
    for sel in all_sels:
        row = [f"{sel*100:>5.0f}%"]
        for ds in ("DEEP_1M", "SIFT_1_5M", "DEEP_8M"):
            c = matrix[ds].get(sel)
            if c is None:
                row.append("-".rjust(20))
            else:
                gap_str = f"gap={fmt_pct(c.gap, 1)}"
                row.append(gap_str.rjust(20))
        log("  " + " | ".join(row))

    log("\n--- 단조성 ---")
    for ds, m in monotonicity.items():
        log(f"  {ds}: {json.dumps({k: v for k, v in m.items() if k != 'gaps'}, default=str)}")

    log("\n--- DEEP 8M Two-Level Decomposition ---")
    rows_dec = build_decomposition(matrix, "DEEP_8M")
    log(f"  {'sel':>6} | {'L1':>10} | {'L2':>10} | {'Total':>10}")
    for r in rows_dec:
        log(
            f"  {r.sel*100:>5.0f}% | {fmt_pct(r.level_1):>10} | "
            f"{fmt_pct(r.level_2):>10} | {fmt_pct(r.total):>10}"
        )


# ============================================================
# 7. 메인 entry point
# ============================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="8M mid-sel 측정 결과 회수 + 분석 + 정리.md 갱신"
    )
    g = parser.add_mutually_exclusive_group(required=False)
    g.add_argument("--check", action="store_true", help="측정 파일 존재 확인만")
    g.add_argument("--update", action="store_true", help="분석 + 정리.md 갱신")
    g.add_argument("--dry-run", action="store_true", help="분석 후 stdout 만, md 갱신 X")
    parser.add_argument(
        "--results-dir",
        default=str(RESULTS_DIR),
        help="experiments/results 경로 override",
    )
    args = parser.parse_args(argv)

    # 기본 동작: --check
    if not (args.check or args.update or args.dry_run):
        args.check = True

    log(f"results_dir={args.results_dir}")
    log("Phase 1 — 8M mid-sel 측정 파일 탐색")
    files = discover_8m_midsel_files()
    if not files:
        log("  ! 8M × s={0.10, 0.30} 측정 파일 미발견.")
        log("  ! 메인 세션이 측정 push 후 본 스크립트 재실행 필요.")
        log("  ! 탐색 패턴: experiments/results/{rq1_motivation,rq2_aware,...}/")
        log("    파일명에 '8m' + 'midsel|s010|s030' 포함 필요.")
        if args.check:
            return 0
        return 1
    log(f"  ✓ {len(files)} 파일 발견")

    if args.check:
        for f in files:
            log(f"  - {f.path.relative_to(REPO_ROOT)} (fmt={f.fmt}, sel={f.sel}, mode={f.mode})")
        return 0

    log("Phase 2 — 측정 데이터 로드 + cell 집계")
    cells = load_all_8m_midsel(files)
    if not cells:
        log("  ! cell 로드 실패. 파일 schema 확인.")
        return 1

    log("Phase 3 — Gradient 매트릭스 + 단조성 검증")
    matrix = build_gradient_matrix(cells)
    monotonicity = check_gradient_monotonicity(matrix)
    km_monotonicity = check_km20_monotonicity(matrix)
    sys20 = collect_sys20_cells(cells)
    log(f"  sys20 (8M SYSTEM-block) cell: {len(sys20)} sel")

    log("Phase 4 — 리포트 출력")
    print_report(files, cells, matrix, monotonicity)
    log("  --- KM20-only 단조성 (RAND20 부재 fallback) ---")
    for ds, m in km_monotonicity.items():
        if m.get("monotonic_strict"):
            v = "✓ 엄격 단조"
        elif m.get("monotonic_weak"):
            v = "○ 약 단조"
        else:
            v = f"~ inc={m.get('n_increase', 0)}/dec={m.get('n_decrease', 0)}"
        log(f"    {ds}: n={m.get('valid_n', 0)} {v}")
    if sys20:
        log("  --- 8M SYS20 (RQ1 cross-dataset 보강) ---")
        for sel in sorted(sys20.keys()):
            c = sys20[sel]
            ci_lo, ci_hi = c.ci_t_based
            log(
                f"    s={sel}: {fmt_pct(c.mean_diff_pct)} {fmt_ci(ci_lo, ci_hi)} "
                f"sig={c.n_significant_seeds}/{len(c.diff_pct_per_seed)}"
            )

    log("Phase 5 — 정리.md 갱신")
    changed = update_summary_md(
        SUMMARY_MD,
        cells,
        matrix,
        monotonicity,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        log(f"  [dry-run] 변경 예상: {changed}")
        return 0
    return 0 if changed else 1


if __name__ == "__main__":
    sys.exit(main())
