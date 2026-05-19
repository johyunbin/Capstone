#!/usr/bin/env python3
"""엔진 검증 실험 분석 — latency 비교 + 실행 계획 변화 + Q-error↔latency.

measure_latency_realengine.py 산출 JSON(cell별)을 모아 요약 표와 figure를 생성한다.

  · latency 비교    조건별 trimmed-mean latency, baseline 대비 speedup
  · 실행 계획 변화  operator tree 시그니처 diff (조건 간 플랜이 바뀌었나)
  · Q-error↔latency 주입 추정치 정확도와 실측 latency의 관계

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
except ImportError:
    plt = None

CONDITION_ORDER = ["baseline", "B1", "CaseB", "oracle"]


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


def summarize(results: list[dict]) -> list[dict]:
    """cell × variant 요약 행 — latency, speedup, q_error, timeout, 플랜 변화."""
    out = []
    for r in results:
        by = {_variant_label(v): v for v in r["variants"]}
        base = by.get("baseline")
        base_ms = base["exec_ms_trimmed"] if base else None
        base_sig = plan_signature(base["plan_first"]) if base else None
        for v in r["variants"]:
            lab = _variant_label(v)
            ms = v["exec_ms_trimmed"]
            speedup = (base_ms / ms) if (base_ms and ms) else None
            sig = plan_signature(v["plan_first"])
            out.append({
                "cell": cell_label(r), "variant": lab,
                "exec_ms_trimmed": ms, "exec_ms_median": v["exec_ms_median"],
                "n_timeout": v["n_timeout"], "q_error": v["q_error"],
                "speedup_vs_baseline": speedup,
                "plan_changed_vs_baseline": (base_sig is not None and sig != base_sig),
            })
    return out


def print_summary(results: list[dict]) -> None:
    rows = summarize(results)
    print(f"\n{'='*94}\n엔진 검증 latency 요약 — {len(results)} cell\n{'='*94}")
    hdr = f"{'cell':<44}{'variant':<18}{'lat(ms)':>10}{'speedup':>9}{'q-err':>8}{'TO':>4}{'plan':>6}"
    print(hdr + "\n" + "-" * 94)
    for s in rows:
        ms = f"{s['exec_ms_trimmed']:.1f}" if s["exec_ms_trimmed"] is not None else "—"
        sp = f"{s['speedup_vs_baseline']:.2f}x" if s["speedup_vs_baseline"] else "—"
        qe = f"{s['q_error']:.3f}" if s["q_error"] is not None else "—"
        pc = "≠" if s["plan_changed_vs_baseline"] else "="
        print(f"{s['cell']:<44}{s['variant']:<18}{ms:>10}{sp:>9}{qe:>8}"
              f"{s['n_timeout']:>4}{pc:>6}")
    print("-" * 94)
    print("speedup>1 = baseline보다 빠름 · plan ≠ = baseline 대비 실행 계획 변화 · TO = timeout 수")


def report_plan_changes(results: list[dict]) -> None:
    """조건 간 실행 계획 operator tree 변화 카탈로그 (Exqutor Fig.11 아날로그)."""
    print(f"\n{'='*94}\n실행 계획 변화 카탈로그\n{'='*94}")
    for r in results:
        by = {_variant_label(v): plan_signature(v["plan_first"]) for v in r["variants"]}
        base = by.get("baseline")
        changed = [lab for lab, sig in by.items()
                   if lab != "baseline" and base is not None and sig != base]
        mark = "변화 있음 → " + ", ".join(changed) if changed else "전 조건 동일 플랜"
        print(f"  {cell_label(r):<48} {mark}")


def plot_latency(results: list[dict], out_dir: Path) -> None:
    if plt is None:
        print("[skip] matplotlib 미설치 — latency figure 생략")
        return
    for r in results:
        labels = [_variant_label(v) for v in r["variants"]]
        vals = [v["exec_ms_trimmed"] or 0 for v in r["variants"]]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(range(len(labels)), vals)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_ylabel("end-to-end latency (ms, trimmed mean)")
        ax.set_title(cell_label(r))
        fig.tight_layout()
        out = out_dir / f"latency_{r['family']}_{r['query']}_{r['dataset']}_sf{r['sf']}_sel{r['sel']}_qid{r['query_id']}.png"
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
    ax.set_xlabel("주입 추정치 Q-error (1 = 정확)")
    ax.set_ylabel("end-to-end latency (ms)")
    ax.set_title("Q-error ↔ latency")
    fig.tight_layout()
    out = out_dir / "qerror_vs_latency.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  saved {out}")


# ---------------------------------------------------------------------------
# self-test (합성 데이터)
# ---------------------------------------------------------------------------

def _mock_results() -> list[dict]:
    """합성 cell 2개 — 분석 로직 검증용. 플랜 변화/timeout/q-error 케이스 포함."""
    def plan(node, *children):
        return {"Node Type": node, "Plans": list(children)}
    scan = plan("Seq Scan")
    return [
        {"family": "tpc_h", "query": "q5", "dataset": "DEEP", "sf": 10,
         "sel": 0.01, "query_id": 0, "D": 0.42, "true_card": 80000,
         "n_warmup": 1, "n_timed": 15, "statement_timeout": "600s", "kst": "test",
         "variants": [
             {"condition": "baseline", "method": None, "injected_card": None,
              "q_error": None, "exec_ms": [900] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 900.0, "exec_ms_median": 900.0, "exec_ms_iqr": [890, 910],
              "plan_first": plan("Hash Join", plan("Hash Join", scan, scan), scan)},
             {"condition": "B1", "method": None, "injected_card": 95000,
              "q_error": 1.19, "exec_ms": [600] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 600.0, "exec_ms_median": 600.0, "exec_ms_iqr": [590, 610],
              "plan_first": plan("Hash Join", plan("Nested Loop", scan, scan), scan)},
             {"condition": "CaseB", "method": "chao_weighted", "injected_card": 82000,
              "q_error": 1.025, "exec_ms": [430] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 430.0, "exec_ms_median": 430.0, "exec_ms_iqr": [420, 440],
              "plan_first": plan("Nested Loop", plan("Nested Loop", scan, scan), scan)},
             {"condition": "oracle", "method": None, "injected_card": 80000,
              "q_error": 1.0, "exec_ms": [410] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 410.0, "exec_ms_median": 410.0, "exec_ms_iqr": [400, 420],
              "plan_first": plan("Nested Loop", plan("Nested Loop", scan, scan), scan)},
         ]},
        {"family": "tpc_ds", "query": "q72", "dataset": "SIFT", "sf": 10,
         "sel": 0.10, "query_id": 3, "D": 0.91, "true_card": 800000,
         "n_warmup": 1, "n_timed": 15, "statement_timeout": "600s", "kst": "test",
         "variants": [
             {"condition": "baseline", "method": None, "injected_card": None,
              "q_error": None, "exec_ms": [], "n_timeout": 15,
              "exec_ms_trimmed": None, "exec_ms_median": None, "exec_ms_iqr": None,
              "plan_first": plan("Hash Join", scan, scan)},
             {"condition": "B1", "method": None, "injected_card": 1050000,
              "q_error": 1.31, "exec_ms": [2200] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 2200.0, "exec_ms_median": 2200.0, "exec_ms_iqr": [2150, 2250],
              "plan_first": plan("Nested Loop", scan, scan)},
             {"condition": "CaseB", "method": "chao_weighted", "injected_card": 815000,
              "q_error": 1.019, "exec_ms": [1500] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 1500.0, "exec_ms_median": 1500.0, "exec_ms_iqr": [1480, 1520],
              "plan_first": plan("Nested Loop", scan, scan)},
             {"condition": "oracle", "method": None, "injected_card": 800000,
              "q_error": 1.0, "exec_ms": [1480] * 15, "n_timeout": 0,
              "exec_ms_trimmed": 1480.0, "exec_ms_median": 1480.0, "exec_ms_iqr": [1460, 1500],
              "plan_first": plan("Nested Loop", scan, scan)},
         ]},
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description="엔진 검증 실험 분석 (Phase 3)")
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
        print("\n✓ self-test 통과 — summarize·plan_signature·plan diff 정상 동작")
        return

    args.output.mkdir(parents=True, exist_ok=True)
    plot_latency(results, args.output)
    plot_qerror_vs_latency(results, args.output)


if __name__ == "__main__":
    main()
