#!/usr/bin/env python3
"""실엔진 latency 측정 harness — 엔진 적용 검증 실험 (Phase 1-2).

오프라인에서 검증된 카디널리티 추정치를 pg_hint_plan `Rows()` 힌트로 VAQ 실행 계획에
주입하고, end-to-end latency를 4조건으로 비교한다. 엔진은 고정, 주입 추정치만 변인.

  조건       주입                          의미
  baseline   힌트 없음                     플래너 default selectivity (개입 없음)
  B1         Rows(<벡터relid> #est_b1)     논문 무작위 Bernoulli 추정
  CaseB      Rows(<벡터relid> #est_caseB)  결합 추정 = (est_b1 + est_method)/2
  oracle     Rows(<벡터relid> #true_card)  참 카디널리티 (이론적 상한)

측정 = 실행 계획(operator tree) + end-to-end latency. 방법론 통제(plan 문서
swift-discovering-engelbart.md §방법론): 매 반복 variant 순서 무작위 셔플(캐시 교란
완화), variant·반복마다 새 세션(플랜 캐시 회피), statement_timeout 건은 censored 별도
집계, 1 warmup + N timed.

서버 실행 (5/19 아침 PostgreSQL 사용 허가 후):
    python3 measure_latency_realengine.py --family tpc_h --query q3 --dataset DEEP \\
        --sf 10 --sel 0.01 --query-id 0 \\
        --estimates latency/estimates_DEEP_sf10.parquet --output latency/

로컬 dry-run (서버 미접속 — SQL 변환·힌트 주입만 검증):
    python3 measure_latency_realengine.py --family tpc_h --query q3 --dataset DEEP --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

try:
    import psycopg  # 서버에서만 필요 — 로컬 dry-run 시 미사용
except ImportError:
    psycopg = None

# --- 경로 (repo 로컬 / 서버 양쪽 탐색) ---
REPO_ROOT = Path(__file__).resolve().parents[2]          # _internal/scripts/ → Capstone/
VAQ_SQL_DIRS = [
    REPO_ROOT / "reference" / "exqutor_query_plans",
    Path("/mnt/hdd0/home/capstone2026/exqutor_query_plans"),
]

# --- PG 접속 (서버 — measure_paper_exact.py와 동일, PORT=55435 명시) ---
PG_HOST, PG_PORT, PG_DB, PG_USER = "/tmp", 55435, "wns41559", "wns41559"

# --- 실험 상수 ---
DEFAULT_CASEB_METHODS = ("chao_weighted", "hilbert_real", "pca1d", "hyperloglog")
TRIM = 1                                                  # trimmed mean 양끝 제거 수

# --- VAQ 쿼리 family ---
TPC_H_QUERIES = ("q3", "q5", "q8", "q9", "q10", "q11", "q12", "q20")
TPC_DS_QUERIES = ("q07", "q12", "q19", "q20", "q42", "q72", "q98")
DS_TABLE_SHORT = {"DEEP": "deep", "SIFT": "sift", "SSN": "fb"}   # SQL partsupp_deep 치환용
DS_DIM = {"DEEP": 96, "SIFT": 128, "SSN": 256}


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# VAQ SQL 로드 + 변환 (서버 미접속에서도 동작 — dry-run 스모크 테스트 대상)
# ---------------------------------------------------------------------------

def load_vaq_sql(family: str, query: str) -> str:
    """reference/exqutor_query_plans/{family}/{query}.sql 로드 (로컬 우선, 서버 fallback)."""
    for base in VAQ_SQL_DIRS:
        p = base / family / f"{query}.sql"
        if p.exists():
            return p.read_text()
    raise FileNotFoundError(
        f"VAQ SQL 미발견: {family}/{query}.sql — 탐색 {[str(b) for b in VAQ_SQL_DIRS]}")


def vec_table_relid(family: str, dataset: str, sf: int) -> tuple[str, str]:
    """(SQL의 partsupp_deep을 치환할 실제 테이블명, Rows() 힌트 relid) 반환.

    TPC-H SQL은 `partsupp_deep` 무alias → relid = 실제 테이블명.
    TPC-DS SQL은 `item_deep AS i` → relid = 별칭 'i' (테이블명 치환 없음).
    """
    if family == "tpc_h":
        tbl = f"partsupp_{DS_TABLE_SHORT[dataset]}_{sf}"
        return tbl, tbl
    return "item_deep", "i"


def build_vaq_sql(family: str, query: str, dataset: str, sf: int,
                  qvec, D: float, injected_rows, *, explain: bool = True) -> str:
    """VAQ SQL 템플릿을 실측 가능한 쿼리로 변환.

    1) partsupp_deep → 실제 벡터 테이블 (TPC-H만)
    2) `<-> 'image_embedding' < <thr>` → `<-> '[vec]'::vector < D`
    3) ORDER BY의 잔여 'image_embedding' → '[vec]'::vector
    4) EXPLAIN(ANALYZE,BUFFERS,FORMAT JSON) + pg_hint_plan Rows() 힌트
       (injected_rows None이면 힌트 생략 = baseline 조건)
    """
    sql = load_vaq_sql(family, query).strip().rstrip(";").strip()

    actual_tbl, relid = vec_table_relid(family, dataset, sf)
    if family == "tpc_h":
        sql = re.sub(r"\bpartsupp_deep\b", actual_tbl, sql)

    qvec_str = "[" + ",".join(f"{float(v):.6f}" for v in qvec) + "]"
    vec_lit = f"'{qvec_str}'::vector"

    def _repl(m: re.Match) -> str:                    # 벡터 술어 + threshold 동시 치환
        return f"{m.group(1)}{vec_lit}{m.group(2)}{float(D):.6f}"

    sql, n_pred = re.subn(
        r"(<->\s*)'image_embedding'(\s*<\s*)[0-9.]+", _repl, sql)
    if n_pred != 1:
        raise ValueError(f"{family}/{query}: 벡터 술어 치환 {n_pred}건 (정확히 1건 기대)")
    sql = sql.replace("'image_embedding'", vec_lit)   # ORDER BY 잔여 placeholder

    prefix = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)\n" if explain else ""
    hint = "" if injected_rows is None else f"/*+ Rows({relid} #{int(injected_rows)}) */\n"
    return prefix + hint + sql


# ---------------------------------------------------------------------------
# 측정 (서버 — psycopg 필요)
# ---------------------------------------------------------------------------

def _connect():
    if psycopg is None:
        raise RuntimeError("psycopg 미설치 — 서버(165.132.140.240 capstone2026)에서 실행")
    return psycopg.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB,
                           user=PG_USER, autocommit=True)


def _run_once(sql: str, statement_timeout: str):
    """새 세션 1회 실행. (exec_ms, plan_dict) 반환 — timeout/에러 시 (None, None).

    조건·반복마다 새 세션 → 플랜 캐시 carryover 회피. statement_timeout 초과 시
    psycopg.errors.QueryCanceled 발생 → censored (None) 처리.
    """
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("LOAD 'pg_hint_plan'")
        cur.execute("SET pg_hint_plan.enable_hint = on")
        cur.execute("SET plan_cache_mode = force_custom_plan")
        cur.execute(f"SET statement_timeout = '{statement_timeout}'")
        try:
            row = cur.execute(sql).fetchone()
            obj = row[0][0]                  # FORMAT JSON: [ {"Plan":.., "Execution Time":..} ]
            return float(obj["Execution Time"]), obj["Plan"]
        except Exception as e:               # QueryCanceled(timeout) 포함
            print(f"[{kst()}]   ! {type(e).__name__}: {str(e)[:120]}")
            return None, None


def _trimmed_mean(vals: list[float], trim: int = TRIM):
    if not vals:
        return None
    if len(vals) <= 2 * trim:
        return float(statistics.fmean(vals))
    return float(statistics.fmean(sorted(vals)[trim:-trim]))


def _iqr(vals: list[float]):
    if len(vals) < 4:
        return None
    s = sorted(vals)
    return [float(s[len(s) // 4]), float(s[(3 * len(s)) // 4])]


def measure_cell(family, query, dataset, sf, sel, query_id, qvec, D, true_card,
                 est_b1, caseb_by_method, *, n_timed, n_warmup, statement_timeout,
                 seed=20260519) -> dict:
    """한 cell(query×dataset×sf×sel×query_id)의 전 variant 측정.

    variant = (condition, method). 매 반복 variant 순서를 무작위 셔플 — 같은 반복 내
    모든 variant를 인접 실행(matched/paired) + 캐시 워밍 순서 편향 완화.
    """
    # variant 정의: (condition, method, injected_card)
    variants = [("baseline", None, None), ("B1", None, est_b1),
                ("oracle", None, true_card)]
    for m, est in caseb_by_method.items():
        variants.append(("CaseB", m, est))

    sql_by_key = {(c, m): build_vaq_sql(family, query, dataset, sf, qvec, D, inj)
                  for (c, m, inj) in variants}
    keys = [(c, m) for (c, m, _) in variants]
    samples = {k: [] for k in keys}
    timeouts = {k: 0 for k in keys}
    plan_first = {k: None for k in keys}

    rng = random.Random(seed)
    for rep in range(n_warmup + n_timed):
        order = keys[:]
        rng.shuffle(order)
        for k in order:
            ms, plan = _run_once(sql_by_key[k], statement_timeout)
            if rep >= n_warmup:
                if ms is None:
                    timeouts[k] += 1
                else:
                    samples[k].append(ms)
            if plan_first[k] is None and plan is not None:
                plan_first[k] = plan
        print(f"[{kst()}]   rep {rep + 1}/{n_warmup + n_timed} 완료")

    out_variants = []
    for (c, m, inj) in variants:
        k = (c, m)
        vals = samples[k]
        qerr = None
        if inj is not None and true_card and inj > 0:
            qerr = max(inj / true_card, true_card / inj)
        out_variants.append({
            "condition": c, "method": m, "injected_card": inj, "q_error": qerr,
            "exec_ms": vals, "n_timeout": timeouts[k],
            "exec_ms_trimmed": _trimmed_mean(vals),
            "exec_ms_median": (statistics.median(vals) if vals else None),
            "exec_ms_iqr": _iqr(vals),
            "plan_first": plan_first[k],
        })
    return {
        "family": family, "query": query, "dataset": dataset, "sf": sf,
        "sel": sel, "query_id": query_id, "D": D, "true_card": true_card,
        "n_warmup": n_warmup, "n_timed": n_timed,
        "statement_timeout": statement_timeout,
        "variants": out_variants, "kst": kst(),
    }


def load_estimates(path: Path, dataset, sf, sel, query_id, methods):
    """gen_latency_estimates.py 산출 parquet에서 한 cell의 추정치 추출.

    Returns: (qvec, D, true_card, est_b1, {method: est_caseB})
    """
    import pyarrow.parquet as pq
    df = pq.read_table(path).to_pandas()
    sub = df[(df["dataset"] == dataset) & (df["sf"] == sf) &
             (np.isclose(df["sel"], sel)) & (df["query_id"] == query_id)]
    if len(sub) == 0:
        raise ValueError(f"추정치 미발견: {dataset} sf{sf} sel{sel} qid{query_id} @ {path}")
    r0 = sub.iloc[0]
    qvec = np.asarray(r0["qvec"], dtype=np.float32)
    caseb = {m: float(sub[sub["method"] == m].iloc[0]["est_caseB"])
             for m in methods if len(sub[sub["method"] == m])}
    return qvec, float(r0["D"]), float(r0["true_card"]), float(r0["est_b1"]), caseb


# ---------------------------------------------------------------------------
# dry-run (서버 미접속 — SQL 변환·힌트 주입 검증)
# ---------------------------------------------------------------------------

def _dry_run(args) -> None:
    dim = DS_DIM[args.dataset]
    qvec = np.random.default_rng(0).standard_normal(dim).astype(np.float32)
    D = 0.86 if args.family == "tpc_h" else 1.08
    print(f"=== dry-run: {args.family}/{args.query} dataset={args.dataset} "
          f"sf={args.sf} dim={dim} ===\n")
    for label, inj in [("baseline", None), ("B1", 123456),
                        ("CaseB", 118000), ("oracle", 130000)]:
        sql = build_vaq_sql(args.family, args.query, args.dataset, args.sf, qvec, D, inj)
        assert "'image_embedding'" not in sql, "placeholder 'image_embedding' 잔여"
        assert sql.count("::vector") == 2, f"::vector {sql.count('::vector')}개 (2 기대)"
        if inj is None:
            assert "/*+ Rows(" not in sql, "baseline에 힌트가 있음"
        else:
            assert f"#{inj}" in sql, "주입 카디널리티 누락"
        head = sql if len(sql) < 700 else sql[:700] + " …"
        print(f"--- {label} (injected={inj}) ---\n{head}\n")
    print("✓ dry-run 통과 — SQL 변환·힌트 주입·threshold 치환 정상")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="실엔진 latency 측정 harness")
    ap.add_argument("--family", choices=["tpc_h", "tpc_ds"], default="tpc_h")
    ap.add_argument("--query", required=True, help="q3 / q5 / q72 …")
    ap.add_argument("--dataset", choices=["DEEP", "SIFT", "SSN"], default="DEEP")
    ap.add_argument("--sf", type=int, default=10)
    ap.add_argument("--sel", type=float, default=0.01)
    ap.add_argument("--query-id", type=int, default=0)
    ap.add_argument("--estimates", type=Path,
                    help="gen_latency_estimates.py 산출 parquet (real run 필수)")
    ap.add_argument("--methods", nargs="+", default=list(DEFAULT_CASEB_METHODS),
                    help="CaseB 결합 method 목록")
    ap.add_argument("--n-timed", type=int, default=15)
    ap.add_argument("--n-warmup", type=int, default=1)
    ap.add_argument("--statement-timeout", default="600s",
                    help="Phase 0 baseline latency 측정 후 재산정")
    ap.add_argument("--output", type=Path, default=Path("latency"))
    ap.add_argument("--dry-run", action="store_true",
                    help="서버 미접속 — SQL 변환·힌트 주입만 검증")
    args = ap.parse_args()

    if args.dry_run:
        _dry_run(args)
        return

    if not args.estimates:
        ap.error("--estimates 필요 (real run) — 또는 --dry-run")

    qvec, D, true_card, est_b1, caseb = load_estimates(
        args.estimates, args.dataset, args.sf, args.sel, args.query_id, args.methods)
    print(f"[{kst()}] cell {args.family}/{args.query} {args.dataset} sf{args.sf} "
          f"sel{args.sel} qid{args.query_id}: D={D:.4f} true={true_card:.0f} "
          f"est_b1={est_b1:.0f} caseB={{{', '.join(f'{m}:{v:.0f}' for m, v in caseb.items())}}}")

    result = measure_cell(
        args.family, args.query, args.dataset, args.sf, args.sel, args.query_id,
        qvec, D, true_card, est_b1, caseb,
        n_timed=args.n_timed, n_warmup=args.n_warmup,
        statement_timeout=args.statement_timeout)

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / (f"latency_{args.family}_{args.query}_{args.dataset}"
                         f"_sf{args.sf}_sel{args.sel}_qid{args.query_id}.json")
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"[{kst()}] saved {out}")


if __name__ == "__main__":
    main()
