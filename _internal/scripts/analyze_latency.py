#!/usr/bin/env python3
"""엔진 적용 검증 실험 분석 — latency 비교 + 실행 계획 변화 + Q-error↔latency.

measure_latency_realengine.py 산출 JSON(cell별)을 모아 요약 표와 figure를 생성한다.

  · latency 비교      조건별 trimmed-mean latency, baseline 대비 speedup
  · 실행 계획 변화    pass-2 operator tree 시그니처 diff (조건 간 플랜이 바뀌었나)
  · Q-error↔latency   주입 추정치 정확도와 실측 latency의 관계
  · injection 검증    Exqutor 주입이 실제로 발동했는지 (injection_fired)

★ injection_fired=false 인 비-baseline variant 는 주입이 발동하지 않은 것(벡터 테이블이
  pass-1 플랜에서 SeqScan 되지 않음) — 그 측정은 기본 selectivity 플랜이라 무효로 본다.

서버/로컬 실행 (결과 JSON만 있으면 됨):
    python3 analyze_latency.py --input latency/ --output latency/figures/

로컬 self-test (서버 미접속 — 합성 데이터로 분석 로직 검증):
    python3 analyze_latency.py --self-test
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np
    # 한글 폰트 명시 — Apple SD Gothic Neo (macOS 기본) → fallback NanumGothic·AppleGothic
    plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "NanumGothic", "AppleGothic", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
except ImportError:
    plt = None
    np = None

try:
    from scipy.stats import wilcoxon
except ImportError:
    wilcoxon = None

import csv
import math
import statistics

CONDITION_ORDER = ["baseline", "B1", "CaseB", "oracle"]

BOOTSTRAP_N = 2000  # paired diff(ms) bootstrap 회수


# ---------------------------------------------------------------------------
# 로드 + 집계
# ---------------------------------------------------------------------------

def load_results(input_dir: Path) -> list[dict]:
    """latency_*.json 전수 로드."""
    results = []
    for p in sorted(input_dir.glob("latency_*.json")):
        try:
            results.append(json.loads(p.read_text()))
        except Exception as e:
            print(f"[warn] {p.name} 로드 실패: {e}")
    return results


def cell_label(r: dict) -> str:
    return (f"{r['family']}/{r['query']} {r['dataset']} sf{r['sf']} "
            f"sel{r['sel']} qid{r['query_id']}")


def _variant_label(v: dict) -> str:
    return v["condition"] if v["method"] is None else f"CaseB:{v['method']}"


def plan_signature(plan: dict | None) -> tuple:
    """실행 계획 operator tree를 pre-order Node Type 튜플로 압축."""
    if not plan:
        return ()
    sig = [plan.get("Node Type", "?")]
    for child in plan.get("Plans", []):
        sig.extend(plan_signature(child))
    return tuple(sig)


def _plan_changed(base_sig: tuple, sig: tuple):
    """baseline 대비 pass-2 플랜 변화 판정. 양쪽 플랜이 다 잡혔을 때만 True/False,
    한쪽이라도 캡처 실패(빈 시그니처)면 None(불명) — 빈 시그니처를 '변화'로 오판하지 않는다."""
    if not base_sig or not sig:
        return None
    return sig != base_sig


def summarize(results: list[dict]) -> list[dict]:
    """cell × variant 요약 행 — latency, speedup, q_error, timeout, 플랜 변화, 주입 검증."""
    out = []
    for r in results:
        by = {_variant_label(v): v for v in r["variants"]}
        base = by.get("baseline")
        base_ms = base["exec_ms_trimmed"] if base else None
        base_sig = plan_signature(base["plan_json"]) if base else None
        for v in r["variants"]:
            lab = _variant_label(v)
            ms = v["exec_ms_trimmed"]
            speedup = (base_ms / ms) if (base_ms and ms) else None
            sig = plan_signature(v["plan_json"])
            out.append({
                "cell": cell_label(r), "variant": lab,
                "exec_ms_trimmed": ms, "exec_ms_median": v["exec_ms_median"],
                "n_timeout": v["n_timeout"], "q_error": v["q_error"],
                "speedup_vs_baseline": speedup,
                "plan_changed_vs_baseline": _plan_changed(base_sig or (), sig),
                "injection_fired": v.get("injection_fired", False),
            })
    return out


def print_summary(results: list[dict]) -> None:
    rows = summarize(results)
    print(f"\n{'='*100}\n엔진 적용 검증 latency 요약 — {len(results)} cell\n{'='*100}")
    hdr = (f"{'cell':<44}{'variant':<18}{'lat(ms)':>10}{'speedup':>9}"
           f"{'q-err':>8}{'TO':>4}{'plan':>6}{'inj':>5}")
    print(hdr + "\n" + "-" * 100)
    miss = 0
    for s in rows:
        ms = f"{s['exec_ms_trimmed']:.1f}" if s["exec_ms_trimmed"] is not None else "—"
        sp = f"{s['speedup_vs_baseline']:.2f}x" if s["speedup_vs_baseline"] else "—"
        qe = f"{s['q_error']:.3f}" if s["q_error"] is not None else "—"
        pc = {True: "≠", False: "=", None: "?"}[s["plan_changed_vs_baseline"]]
        is_base = s["variant"] == "baseline"
        inj = "—" if is_base else ("ok" if s["injection_fired"] else "MISS")
        if not is_base and not s["injection_fired"]:
            miss += 1
        print(f"{s['cell']:<44}{s['variant']:<18}{ms:>10}{sp:>9}{qe:>8}"
              f"{s['n_timeout']:>4}{pc:>6}{inj:>5}")
    print("-" * 100)
    print("speedup>1 = baseline보다 빠름 · plan ≠ = baseline 대비 pass-2 플랜 변화 · "
          "plan ? = 플랜 미캡처로 불명 · TO = timeout 수")
    print("inj = Exqutor 주입 발동 (MISS = 주입 미발동 → 기본 selectivity 플랜, 측정 무효)")
    if miss:
        print(f"⚠️  injection MISS {miss}건 — 해당 variant 는 벡터 테이블이 pass-1 에서 "
              f"SeqScan 되지 않아 주입이 건너뛰어졌다. 분석서 제외/주석 필요.")


def _bootstrap_ci_paired_diff(a, b, n_boot: int = BOOTSTRAP_N,
                              rng_seed: int = 7) -> tuple[float, float]:
    """a − b paired diff (ms) 의 percentile bootstrap 95% CI.

    a, b: 같은 길이 list/array, paired (i 번째 rep 의 같은 epoch).
    return: (ci_lo, ci_hi) — 2.5 / 97.5 percentile. 표본 < 5 시 (nan, nan).
    """
    if np is None or len(a) < 5 or len(b) < 5:
        return float("nan"), float("nan")
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    diff = aa - bb
    n = len(diff)
    rng = np.random.default_rng(rng_seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot_means = np.mean(diff[idx], axis=1)
    return (float(np.percentile(boot_means, 2.5)),
            float(np.percentile(boot_means, 97.5)))


def _hedges_g_paired(a, b) -> float:
    """Hedges' g (paired): mean(a − b) / sd(a − b), 작은 표본 보정 j = 1 − 3/(4n − 9).

    sd 가 0 인 경우 0.0. 표본 < 2 시 nan.
    """
    if np is None or len(a) < 2 or len(b) < 2:
        return float("nan")
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    diff = aa - bb
    n = len(diff)
    sd = float(np.std(diff, ddof=1))
    if sd == 0.0:
        return 0.0
    d = float(np.mean(diff)) / sd
    j = 1.0 - 3.0 / (4 * n - 9) if (4 * n - 9) > 0 else 1.0
    return d * j


def _cliffs_delta_paired(a, b) -> float:
    """Cliff's δ (paired): (#a > b − #a < b) / n. 범위 [−1, 1].

    같은 짝(i 번째 rep) 비교 — independent 2-sample (cartesian) 아님.
    """
    if np is None or len(a) < 1 or len(b) < 1:
        return float("nan")
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    gt = int(np.sum(aa > bb))
    lt = int(np.sum(aa < bb))
    return (gt - lt) / len(aa)


def paired_stats(results: list[dict]) -> list[dict]:
    """cell × (anchor, variant) paired diff + Wilcoxon signed-rank + 효과크기·CI.

    measure_latency_realengine.py 는 매 rep 마다 16 variant 를 fixed-seed shuffle 로
    1회씩 측정 → exec_ms[i] 는 같은 epoch (같은 OS state) 의 i 번째 측정. paired test 적합.

    anchor:
      · baseline → 각 비-baseline variant (15) : speedup 유의성
      · B1       → 각 비-B1, 비-baseline variant (14) : CaseB·oracle 의 B1 대비 가치
    holm 보정은 anchor 군 내에서. 효과크기는 anchor − variant 의 paired diff 기반:
      · Hedges' g (paired): mean(diff)/sd(diff), 작은 표본 보정
      · Cliff's δ (paired): (#a>b − #a<b) / n
      · bootstrap CI: paired diff 의 mean 에 대한 2.5/97.5 percentile
    """
    if wilcoxon is None:
        return []
    rows = []
    for r in results:
        by = {_variant_label(v): v for v in r["variants"]}
        cell = cell_label(r)
        valid = {lab: v["exec_ms"] for lab, v in by.items()
                 if v.get("exec_ms") and len(v["exec_ms"]) >= 2}
        for anchor in ("baseline", "B1"):
            if anchor not in valid:
                continue
            a = valid[anchor]
            for lab, b in valid.items():
                if lab == anchor or (anchor == "B1" and lab == "baseline"):
                    continue
                n = min(len(a), len(b))
                if n < 2:
                    continue
                diffs = [a[i] - b[i] for i in range(n)]
                med_diff = statistics.median(diffs)
                try:
                    w, p = wilcoxon(a[:n], b[:n], alternative="two-sided",
                                    zero_method="wilcox")
                    w, p = float(w), float(p)
                except Exception:
                    w, p = float("nan"), float("nan")
                ci_lo, ci_hi = _bootstrap_ci_paired_diff(a[:n], b[:n])
                hedges_g = _hedges_g_paired(a[:n], b[:n])
                cliffs_d = _cliffs_delta_paired(a[:n], b[:n])
                rows.append({
                    "cell": cell, "anchor": anchor, "variant": lab, "n_pairs": n,
                    "median_diff_ms": med_diff,
                    "anchor_med_ms": statistics.median(a[:n]),
                    "variant_med_ms": statistics.median(b[:n]),
                    "w_stat": w, "p_value": p,
                    "ci_lo_ms": ci_lo, "ci_hi_ms": ci_hi,
                    "hedges_g": hedges_g, "cliffs_delta": cliffs_d,
                })
    # holm 보정 (anchor 별 분리)
    for anchor in ("baseline", "B1"):
        sub = [r for r in rows if r["anchor"] == anchor]
        sub_sorted = sorted(sub, key=lambda r: (r["p_value"] if r["p_value"] == r["p_value"] else 2.0))
        n = len(sub_sorted)
        prev = 0.0
        for rank, r in enumerate(sub_sorted, 1):
            if r["p_value"] != r["p_value"]:  # NaN
                r["p_holm"] = float("nan"); r["holm_rank"] = rank
                continue
            adj = min(1.0, r["p_value"] * (n - rank + 1))
            adj = max(adj, prev)              # 단조증가 강제
            prev = adj
            r["p_holm"] = adj
            r["holm_rank"] = rank
    return rows


def print_paired_stats(rows: list[dict]) -> None:
    if not rows:
        print("\n[skip] paired stats — scipy 미설치 또는 데이터 부족")
        return
    print(f"\n{'='*128}\npaired Wilcoxon signed-rank (anchor vs variant)\n{'='*128}")
    hdr = (f"{'cell':<44}{'anchor':<10}{'variant':<22}{'n':>3}"
           f"{'med_diff':>10}{'anc_med':>10}{'var_med':>10}{'p_value':>11}{'p_holm':>11}")
    print(hdr + "\n" + "-" * 128)
    for r in sorted(rows, key=lambda r: (r["cell"], r["anchor"], r["variant"])):
        med = f"{r['median_diff_ms']:.1f}"
        am = f"{r['anchor_med_ms']:.1f}"
        bm = f"{r['variant_med_ms']:.1f}"
        pv = f"{r['p_value']:.2e}" if r["p_value"] == r["p_value"] else "—"
        ph = f"{r['p_holm']:.2e}" if r["p_holm"] == r["p_holm"] else "—"
        print(f"{r['cell'][:42]:<44}{r['anchor']:<10}{r['variant'][:20]:<22}{r['n_pairs']:>3}"
              f"{med:>10}{am:>10}{bm:>10}{pv:>11}{ph:>11}")
    print("-" * 128)
    sig_b = sum(1 for r in rows if r["anchor"] == "baseline" and r["p_holm"] < 0.05)
    sig_B = sum(1 for r in rows if r["anchor"] == "B1" and r["p_holm"] < 0.05)
    tot_b = sum(1 for r in rows if r["anchor"] == "baseline")
    tot_B = sum(1 for r in rows if r["anchor"] == "B1")
    print(f"  baseline-vs-* 유의 (p_holm<0.05): {sig_b}/{tot_b}")
    print(f"  B1-vs-*       유의 (p_holm<0.05): {sig_B}/{tot_B}")
    print("  med_diff > 0 = anchor 가 더 느림 (variant 가 빠름).")
    # effect size 분포 (Hedges' g · Cliff's δ) — anchor 별 분리
    if np is not None:
        for anchor in ("baseline", "B1"):
            sub = [r for r in rows if r["anchor"] == anchor]
            if not sub:
                continue
            g_arr = [r["hedges_g"] for r in sub if r["hedges_g"] == r["hedges_g"]]
            d_arr = [r["cliffs_delta"] for r in sub if r["cliffs_delta"] == r["cliffs_delta"]]
            ci_arr = [r for r in sub
                      if r["ci_lo_ms"] == r["ci_lo_ms"] and r["ci_hi_ms"] == r["ci_hi_ms"]]
            n_large_g = sum(1 for g in g_arr if abs(g) >= 0.8)
            n_med_g = sum(1 for g in g_arr if 0.5 <= abs(g) < 0.8)
            n_small_g = sum(1 for g in g_arr if abs(g) < 0.5)
            n_large_d = sum(1 for d in d_arr if abs(d) >= 0.474)
            n_med_d = sum(1 for d in d_arr if 0.33 <= abs(d) < 0.474)
            n_small_d = sum(1 for d in d_arr if abs(d) < 0.33)
            n_ci_excludes_zero = sum(1 for r in ci_arr
                                     if r["ci_lo_ms"] * r["ci_hi_ms"] > 0)
            print(f"  [{anchor:<8}] Hedges' g: large(|g|≥0.8)={n_large_g} / "
                  f"medium(0.5≤|g|<0.8)={n_med_g} / small(|g|<0.5)={n_small_g}")
            print(f"  [{anchor:<8}] Cliff's δ: large(|δ|≥0.474)={n_large_d} / "
                  f"medium(0.33≤|δ|<0.474)={n_med_d} / small(|δ|<0.33)={n_small_d}")
            print(f"  [{anchor:<8}] bootstrap 95% CI ∌ 0 (효과 비제로): "
                  f"{n_ci_excludes_zero}/{len(ci_arr)}")


def export_paired_csv(rows: list[dict], out_path: Path) -> None:
    if not rows:
        return
    cols = ["cell", "anchor", "variant", "n_pairs", "median_diff_ms",
            "anchor_med_ms", "variant_med_ms", "w_stat", "p_value",
            "p_holm", "holm_rank",
            "ci_lo_ms", "ci_hi_ms", "hedges_g", "cliffs_delta"]
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["cell"], r["anchor"], r["variant"])):
            w.writerow({k: r.get(k) for k in cols})
    print(f"  saved {out_path}")


def report_plan_changes(results: list[dict]) -> None:
    """조건 간 pass-2 실행 계획 operator tree 변화 카탈로그 (Exqutor Fig.11 아날로그)."""
    print(f"\n{'='*100}\n실행 계획(pass-2) 변화 카탈로그\n{'='*100}")
    for r in results:
        by = {_variant_label(v): plan_signature(v["plan_json"]) for v in r["variants"]}
        base = by.get("baseline") or ()
        changed = [lab for lab, sig in by.items()
                   if lab != "baseline" and _plan_changed(base, sig) is True]
        unknown = [lab for lab, sig in by.items()
                   if lab != "baseline" and _plan_changed(base, sig) is None]
        parts = []
        if changed:
            parts.append("변화 → " + ", ".join(changed))
        if unknown:
            parts.append("불명(미캡처) → " + ", ".join(unknown))
        mark = " · ".join(parts) if parts else "전 조건 동일 플랜"
        print(f"  {cell_label(r):<48} {mark}")


def _timed_variants(r: dict) -> list[dict]:
    """latency 막대용 — censored(전 회 timeout) variant 는 제외."""
    return [v for v in r["variants"] if v["exec_ms_trimmed"] is not None]


def plot_latency(results: list[dict], out_dir: Path) -> None:
    if plt is None:
        print("[skip] matplotlib 미설치 — latency figure 생략")
        return
    for r in results:
        vs = _timed_variants(r)
        if not vs:
            print(f"[skip] {cell_label(r)} — 전 variant censored, latency figure 생략")
            continue
        labels = [_variant_label(v) for v in vs]
        vals = [v["exec_ms_trimmed"] for v in vs]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(range(len(labels)), vals)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_ylabel("end-to-end latency (ms, trimmed mean)")
        n_cens = len(r["variants"]) - len(vs)
        title = cell_label(r) + (f"  (censored {n_cens})" if n_cens else "")
        ax.set_title(title)
        fig.tight_layout()
        out = out_dir / (f"latency_{r['family']}_{r['query']}_{r['dataset']}"
                         f"_sf{r['sf']}_sel{r['sel']}_qid{r['query_id']}.png")
        fig.savefig(out, dpi=120)
        plt.close(fig)
        print(f"  saved {out}")


def plot_qerror_vs_latency(results: list[dict], out_dir: Path) -> None:
    if plt is None:
        print("[skip] matplotlib 미설치 — Q-error↔latency figure 생략")
        return
    xs, ys, cs = [], [], []
    for r in results:
        for v in r["variants"]:
            if v["q_error"] is not None and v["exec_ms_trimmed"] is not None:
                xs.append(v["q_error"])
                ys.append(v["exec_ms_trimmed"])
                cs.append(CONDITION_ORDER.index(v["condition"])
                          if v["condition"] in CONDITION_ORDER else 0)
    if not xs:
        print("[skip] Q-error↔latency — 데이터 없음")
        return
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(xs, ys, c=cs, cmap="viridis", alpha=0.7)
    ax.set_xlabel("injected estimate Q-error (1 = exact)")
    ax.set_ylabel("end-to-end latency (ms)")
    ax.set_title("Q-error vs latency")
    fig.tight_layout()
    out = out_dir / "qerror_vs_latency.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  saved {out}")


# ---------------------------------------------------------------------------
# 신규 발행용 figure 3종 (Phase 3 §5.3·5.4·5.5)
# ---------------------------------------------------------------------------

_NON_BASELINE_ORDER = [
    "B1", "oracle",
    "CaseB:chao_weighted", "CaseB:hilbert_real", "CaseB:skilling_hilbert",
    "CaseB:ica_fastica", "CaseB:pca1d", "CaseB:zorder_morton",
    "CaseB:hyperloglog", "CaseB:cum_sqrtf", "CaseB:lavallee_hidiroglou",
    "CaseB:rsvd", "CaseB:sparse_rp", "CaseB:mhist2", "CaseB:rabitq_strat",
]


def _short_cell_label(cell: str) -> str:
    """`tpc_h/q3 DEEP sf10 sel0.001 qid0` → `q3/qid0` 식 짧은 라벨."""
    parts = cell.split()
    q = parts[0].split("/")[-1] if parts else "?"
    qid = next((p for p in parts if p.startswith("qid")), "")
    sel = next((p for p in parts if p.startswith("sel")), "")
    return f"{q}·{sel}·{qid}" if sel and qid else f"{q}·{qid}"


def _short_variant(label: str) -> str:
    if label.startswith("CaseB:"):
        return label[len("CaseB:"):]
    return label


def plot_speedup_heatmap(results: list[dict], out_dir: Path) -> None:
    """fig5_2 — cell × non-baseline variant 의 baseline 대비 speedup heatmap.

    색: RdBu_r, midpoint=1.0 (LogNorm 대신 TwoSlopeNorm).
    값은 trimmed-mean exec_ms 비율 (baseline_ms / variant_ms).
    """
    if plt is None or np is None:
        print("[skip] matplotlib/numpy 미설치 — speedup heatmap 생략")
        return
    cells = [cell_label(r) for r in results]
    if not cells:
        print("[skip] speedup heatmap — 데이터 없음")
        return
    M = np.full((len(cells), len(_NON_BASELINE_ORDER)), np.nan)
    for i, r in enumerate(results):
        by = {_variant_label(v): v for v in r["variants"]}
        base_ms = by.get("baseline", {}).get("exec_ms_trimmed")
        if not base_ms:
            continue
        for j, vlab in enumerate(_NON_BASELINE_ORDER):
            v = by.get(vlab)
            if v and v.get("exec_ms_trimmed"):
                M[i, j] = base_ms / v["exec_ms_trimmed"]
    fig_h = max(4.5, len(cells) * 0.45)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    vmax = float(np.nanmax(M)) if not np.isnan(M).all() else 8.0
    vmin = float(np.nanmin(M)) if not np.isnan(M).all() else 0.5
    norm = mcolors.TwoSlopeNorm(vmin=min(vmin, 0.8), vcenter=1.0,
                                vmax=max(vmax, 1.2))
    im = ax.imshow(M, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_xticks(range(len(_NON_BASELINE_ORDER)))
    ax.set_xticklabels([_short_variant(l) for l in _NON_BASELINE_ORDER],
                       rotation=45, ha="right")
    ax.set_yticks(range(len(cells)))
    ax.set_yticklabels([_short_cell_label(c) for c in cells])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:.1f}", ha="center", va="center",
                        fontsize=7, color="black")
    ax.set_title("baseline 대비 speedup — cell × variant")
    fig.colorbar(im, ax=ax, label="speedup (baseline_ms / variant_ms)")
    fig.tight_layout()
    out = out_dir / "fig5_2_speedup_heatmap.png"
    fig.savefig(out, dpi=140)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    print(f"  saved {out}")


def plot_plan_recovery_matrix(results: list[dict], out_dir: Path) -> None:
    """fig5_3 — cell × non-baseline variant 의 plan 회복(oracle plan 와 동일 여부) matrix.

    값: 3 카테고리
      · 'oracle' plan 와 동일       → 1 (그린)
      · plan 잡혔으나 oracle 와 다름 → 0.5 (옐로우)
      · plan 미캡처 / injection MISS → 0 (그레이, hatch)
    """
    if plt is None or np is None:
        print("[skip] matplotlib/numpy 미설치 — plan recovery matrix 생략")
        return
    cells = [cell_label(r) for r in results]
    if not cells:
        print("[skip] plan recovery matrix — 데이터 없음")
        return
    M = np.zeros((len(cells), len(_NON_BASELINE_ORDER)))
    MISS = np.zeros_like(M, dtype=bool)
    for i, r in enumerate(results):
        by = {_variant_label(v): v for v in r["variants"]}
        orc_sig = plan_signature(by.get("oracle", {}).get("plan_json"))
        for j, vlab in enumerate(_NON_BASELINE_ORDER):
            v = by.get(vlab)
            if not v:
                MISS[i, j] = True
                continue
            sig = plan_signature(v.get("plan_json"))
            if not v.get("injection_fired", True) and vlab != "oracle":
                MISS[i, j] = True
                continue
            if not orc_sig or not sig:
                continue
            M[i, j] = 1.0 if sig == orc_sig else 0.5
    fig_h = max(4.5, len(cells) * 0.45)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    cmap = mcolors.ListedColormap(["#cccccc", "#f4d35e", "#5cab7d"])
    bounds = [-0.5, 0.25, 0.75, 1.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(M, cmap=cmap, norm=norm, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if MISS[i, j]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           hatch="///", fill=False,
                                           edgecolor="#888", linewidth=0))
            elif M[i, j] == 1.0:
                ax.text(j, i, "●", ha="center", va="center", fontsize=10,
                        color="white")
    ax.set_xticks(range(len(_NON_BASELINE_ORDER)))
    ax.set_xticklabels([_short_variant(l) for l in _NON_BASELINE_ORDER],
                       rotation=45, ha="right")
    ax.set_yticks(range(len(cells)))
    ax.set_yticklabels([_short_cell_label(c) for c in cells])
    ax.set_title("실행 계획 회복 — oracle 과 동일 plan 여부")
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 0.5, 1.0])
    cbar.ax.set_yticklabels(["미캡처/MISS", "≠oracle", "=oracle ●"])
    fig.tight_layout()
    out = out_dir / "fig5_3_plan_recovery.png"
    fig.savefig(out, dpi=140)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    print(f"  saved {out}")


def plot_paired_significance(rows: list[dict], out_dir: Path) -> None:
    """fig5_4 — anchor=B1 sub 의 cell × variant heatmap, color = -log10(p_holm).

    p_holm < 0.05 셀에 별표(★). B1-vs-* 통계 의의 시각화.
    """
    if plt is None or np is None or not rows:
        print("[skip] matplotlib/numpy 미설치 또는 paired stats 없음 — significance 생략")
        return
    sub = [r for r in rows if r["anchor"] == "B1"]
    if not sub:
        print("[skip] paired significance — B1 anchor 데이터 없음")
        return
    cells = sorted({r["cell"] for r in sub})
    variants = [v for v in _NON_BASELINE_ORDER if v != "B1"]
    M = np.full((len(cells), len(variants)), np.nan)
    SIG = np.zeros_like(M, dtype=bool)
    DIFF = np.full_like(M, np.nan)
    cell_idx = {c: i for i, c in enumerate(cells)}
    var_idx = {v: j for j, v in enumerate(variants)}
    for r in sub:
        i = cell_idx.get(r["cell"])
        j = var_idx.get(r["variant"])
        if i is None or j is None:
            continue
        p = r.get("p_holm")
        if p is not None and p == p and p > 0:
            M[i, j] = -math.log10(max(p, 1e-6))
            SIG[i, j] = p < 0.05
        DIFF[i, j] = r.get("median_diff_ms", float("nan"))
    fig_h = max(4.5, len(cells) * 0.45)
    fig, ax = plt.subplots(figsize=(11, fig_h))
    im = ax.imshow(M, cmap="PuRd", aspect="auto", vmin=0,
                   vmax=max(2.0, float(np.nanmax(M)) if not np.isnan(M).all() else 2.0))
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if SIG[i, j]:
                ax.text(j, i, "★", ha="center", va="center",
                        fontsize=10, color="black")
            elif not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:.1f}", ha="center", va="center",
                        fontsize=7, color="#333")
    ax.set_xticks(range(len(variants)))
    ax.set_xticklabels([_short_variant(l) for l in variants], rotation=45, ha="right")
    ax.set_yticks(range(len(cells)))
    ax.set_yticklabels([_short_cell_label(c) for c in cells])
    ax.set_title("B1 vs 비-B1 variant — paired Wilcoxon p_holm 의 -log10")
    fig.colorbar(im, ax=ax, label="-log10(p_holm)  ★ = p_holm<0.05")
    fig.tight_layout()
    out = out_dir / "fig5_4_wilcoxon_significance.png"
    fig.savefig(out, dpi=140)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    print(f"  saved {out}")


# ---------------------------------------------------------------------------
# self-test (합성 데이터)
# ---------------------------------------------------------------------------

def _mock_results() -> list[dict]:
    """합성 cell 2개 — 분석 로직 검증용. 플랜 변화·timeout·injection MISS 케이스 포함."""
    def plan(node, *children):
        return {"Node Type": node, "Plans": list(children)}
    scan = plan("Seq Scan")

    def variant(cond, method, inj, qe, ms, plan_json, *, n_to=0, fired=True):
        timed = [ms] * 15 if ms is not None else []
        return {
            "condition": cond, "method": method, "injected_card": inj,
            "q_error": qe, "exec_ms": timed, "n_timeout": n_to,
            "exec_ms_trimmed": (ms if ms is not None else None),
            "exec_ms_median": (ms if ms is not None else None),
            "exec_ms_iqr": ([ms - 10, ms + 10] if ms is not None else None),
            "plan_json": plan_json, "plan_duration_ms": (ms or 0.0),
            "injection_fired": (False if cond == "baseline" else fired),
            "injected_card_seen": (inj if (cond != "baseline" and fired) else None),
        }
    return [
        {"family": "tpc_h", "query": "q5", "dataset": "DEEP", "sf": 10,
         "sel": 0.01, "query_id": 0, "D": 0.42, "true_card": 80000,
         "vec_table": "partsupp_deep_10", "n_warmup": 1, "n_timed": 15,
         "statement_timeout": "600s", "kst": "test",
         "variants": [
             variant("baseline", None, None, None, 900.0,
                     plan("Hash Join", plan("Hash Join", scan, scan), scan)),
             variant("B1", None, 95000, 1.19, 600.0,
                     plan("Hash Join", plan("Nested Loop", scan, scan), scan)),
             variant("CaseB", "chao_weighted", 82000, 1.025, 430.0,
                     plan("Nested Loop", plan("Nested Loop", scan, scan), scan)),
             variant("CaseB", "hilbert_real", 81000, 1.012, 425.0,
                     plan("Nested Loop", plan("Nested Loop", scan, scan), scan)),
             variant("oracle", None, 80000, 1.0, 410.0,
                     plan("Nested Loop", plan("Nested Loop", scan, scan), scan)),
         ]},
        {"family": "tpc_h", "query": "q11", "dataset": "SIFT", "sf": 10,
         "sel": 0.10, "query_id": 3, "D": 0.91, "true_card": 800000,
         "vec_table": "partsupp_sift_10", "n_warmup": 1, "n_timed": 15,
         "statement_timeout": "600s", "kst": "test",
         "variants": [
             variant("baseline", None, None, None, None,
                     plan("Hash Join", scan, scan), n_to=15),
             variant("B1", None, 1050000, 1.31, 2200.0, plan("Nested Loop", scan, scan)),
             variant("CaseB", "chao_weighted", 815000, 1.019, 1500.0,
                     plan("Nested Loop", scan, scan)),
             # injection MISS — 주입 미발동(pkey IndexScan 경로) 케이스
             variant("CaseB", "pca1d", 808000, 1.010, 2150.0,
                     plan("Hash Join", scan, scan), fired=False),
             variant("oracle", None, 800000, 1.0, 1480.0, plan("Nested Loop", scan, scan)),
         ]},
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="엔진 적용 검증 실험 분석 (Phase 3)")
    ap.add_argument("--input", type=Path, default=Path("latency"),
                    help="measure_latency_realengine.py 산출 JSON 디렉토리")
    ap.add_argument("--output", type=Path, default=Path("latency/figures"))
    ap.add_argument("--self-test", action="store_true",
                    help="서버 미접속 — 합성 데이터로 분석 로직 검증")
    args = ap.parse_args()

    if args.self_test:
        results = _mock_results()
        print(f"[self-test] 합성 cell {len(results)}개로 분석 로직 검증")
    else:
        results = load_results(args.input)
        if not results:
            print(f"결과 JSON 없음: {args.input}/latency_*.json")
            return

    print_summary(results)
    report_plan_changes(results)

    if args.self_test:
        print("\n✓ self-test 통과 — summarize·plan_signature·plan diff·injection 정상")
        return

    args.output.mkdir(parents=True, exist_ok=True)
    rows = paired_stats(results)
    print_paired_stats(rows)
    export_paired_csv(rows, args.output / "paired_stats.csv")
    plot_latency(results, args.output)
    plot_qerror_vs_latency(results, args.output)
    plot_speedup_heatmap(results, args.output)
    plot_plan_recovery_matrix(results, args.output)
    plot_paired_significance(rows, args.output)


if __name__ == "__main__":
    main()
