#!/usr/bin/env python3
"""실엔진 latency 측정 harness — 엔진 적용 검증 실험 (Phase 1-2).

오프라인에서 검증된 카디널리티 추정치를 Exqutor 패치 GUC `vector.injected_card`로 VAQ
실행에 주입하고, end-to-end latency를 4조건으로 비교한다. 엔진(서버 PostgreSQL 55435)은
고정, 주입 추정치만 유일 변인.

  조건       주입 GUC                              의미
  baseline   vector.disable_estimation=on          플래너 default selectivity (개입 없음)
  B1         vector.injected_card=<est_b1>          논문 무작위 Bernoulli 추정
  CaseB      vector.injected_card=<est_caseB>       결합 추정 (est_b1 + est_method)/2
  oracle     vector.injected_card=<true_card>       참 카디널리티 (이론적 상한)

주입 메커니즘 (서버 vector.c 패치 — 2026-05-20 recon 으로 확정):
  · Exqutor 는 **실행 시점 2-pass**다. planner_hook 은 pass-1(기본 selectivity) 플랜만
    만들고, ExecutorRun 훅이 벡터 술어를 탐지 → check_for_vector_search 가 카디널리티를
    확정 → 재plan → pass-2 실행. `injected_card>=0`이면 샘플링을 건너뛰고 그 값을 쓴다.
  · ★ 주입은 벡터 테이블이 pass-1 플랜에서 **SeqScan**으로 접근될 때만 발동한다
    (check_for_vector_search 의 SeqScan 분기). pkey IndexScan 경로는 주입을 건너뛴다.
    sf10/sf100 join 은 보통 partsupp 를 SeqScan 하나 보장은 없다 → 측정마다 Exqutor 의
    "Estimated cardinality" 로그를 포착해 injection_fired 플래그로 검증한다.
  · 순수 EXPLAIN 은 실행을 안 하므로 영원히 pass-1 플랜만 본다 → latency 는 실쿼리 직접
    실행 + perf_counter, 플랜은 auto_explain(실행 후 pass-2 플랜이 client notice 로 도착).
  · GUC 는 vector 확장 라이브러리가 정의 — shared_preload_libraries 가 비어 있어
    모든 세션이 첫 statement 로 `LOAD 'vector'` 를 해야 한다.
  · 서버 테이블은 전부 `<name>_<sf>` suffix → 세션마다 임시 VIEW(partsupp_deep + base 7종)
    를 만들어 VAQ 템플릿을 무수정 실행한다 (문자열 치환은 q8·q9 의 `nation` 컬럼 alias
    때문에 위험).

서버 실행:
    python3 measure_latency_realengine.py --query q3 --dataset DEEP --sf 10 --sel 0.01 \\
        --query-id 0 --estimates latency/estimates_DEEP_sf10.parquet --output latency/

로컬 dry-run (서버 미접속 — SQL 변환·GUC·임시 VIEW DDL 검증):
    python3 measure_latency_realengine.py --query q3 --dataset DEEP --sf 10 --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import time
import uuid
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
    REPO_ROOT / "reference" / "exqutor_query_plans" / "tpc_h",
    Path("/mnt/hdd0/home/capstone2026/exqutor_query_plans/tpc_h"),
]

# --- PG 접속 (서버 55435 — 우리 패치 바이너리) ---
PG_HOST, PG_PORT, PG_DB, PG_USER = "/tmp", 55435, "wns41559", "wns41559"

# --- 실험 상수 ---
# 강한 method 13종 (v13_summary §4.4 — 불안정 클러스터링 3종 gmm·minibatch_partial·faiss_ivf 제외)
DEFAULT_CASEB_METHODS = (
    "hilbert_real", "skilling_hilbert", "chao_weighted", "ica_fastica", "pca1d",
    "zorder_morton", "hyperloglog", "cum_sqrtf", "lavallee_hidiroglou", "rsvd",
    "sparse_rp", "mhist2", "rabitq_strat",
)
TRIM = 1                                                  # trimmed mean 양끝 제거 수
MIN_INJECT = 1.0                                          # injected_card 하한 (0 주입 시 rel->rows=0 비정상 플랜 회피)

# --- VAQ 쿼리 + 테이블 (TPC-H 전용 — TPC-DS 는 서버 스키마 부재로 사장) ---
TPC_H_QUERIES = ("q3", "q5", "q8", "q9", "q10", "q11", "q12", "q20")
TPCH_BASE_TABLES = ("customer", "orders", "lineitem", "supplier", "nation", "region", "part")
DS_TABLE_SHORT = {                                        # VAQ 템플릿 partsupp_deep 치환용
    "DEEP": "deep", "SIFT": "sift", "SSN": "fb",          # 단일 3종 sf=1/10/100 적재
    "WIKI": "wiki", "YFCC": "yfcc",                       # 단일 2종 sf=1/10 (sf=100 미적재 honest exception)
    "DEEP_SIFT": "deep_sift", "DEEP_WIKI": "deep_wiki",   # 다중 2종 sf=10 적재 (DEEP+YFCC/CC3M 별도 build 필요)
}
DS_DIM = {
    "DEEP": 96, "SIFT": 128, "SSN": 256,
    "WIKI": 768, "YFCC": 192,
    "DEEP_SIFT": 224, "DEEP_WIKI": 864,
}


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# VAQ SQL 로드 + 변환 (서버 미접속에서도 동작 — dry-run 검증 대상)
# ---------------------------------------------------------------------------

def load_vaq_sql(query: str) -> str:
    """reference/exqutor_query_plans/tpc_h/{query}.sql 로드 (로컬 우선, 서버 fallback)."""
    for base in VAQ_SQL_DIRS:
        p = base / f"{query}.sql"
        if p.exists():
            return p.read_text()
    raise FileNotFoundError(
        f"VAQ SQL 미발견: {query}.sql — 탐색 {[str(b) for b in VAQ_SQL_DIRS]}")


def vec_table_name(dataset: str, sf: int) -> str:
    """VAQ 템플릿 partsupp_deep 이 가리킬 실제 벡터 테이블명 (서버는 SF suffix)."""
    return f"partsupp_{DS_TABLE_SHORT[dataset]}_{sf}"


def temp_view_ddls(dataset: str, sf: int) -> list[str]:
    """세션별 임시 VIEW DDL — VAQ 템플릿의 무suffix 테이블명을 SF 테이블에 매핑.

    템플릿이 쓰는 이름(partsupp_deep + base 7종)으로 임시 VIEW 를 만들어 SQL 을
    무수정 실행한다. 임시 VIEW 는 세션 종료 시 자동 소멸 — 타 사용자 무영향.
    """
    ddls = [f"CREATE TEMP VIEW partsupp_deep AS SELECT * FROM {vec_table_name(dataset, sf)}"]
    ddls += [f"CREATE TEMP VIEW {t} AS SELECT * FROM {t}_{sf}" for t in TPCH_BASE_TABLES]
    return ddls


def build_vaq_sql(query: str, qvec, D: float, *, marker: str | None = None) -> str:
    """VAQ SQL 템플릿을 실행 가능 SELECT 로 변환 — qvec·threshold 만 치환.

    테이블명은 손대지 않는다 (임시 VIEW 가 partsupp_deep + base 7종 을 제공).
    1) `<-> 'image_embedding' < <thr>` → `<-> '[vec]'::vector < D`
    2) ORDER BY 의 잔여 'image_embedding' → '[vec]'::vector
    3) marker 지정 시 선두에 주석 삽입 (auto_explain 로그에서 우리 쿼리 식별용)
    """
    sql = load_vaq_sql(query).strip().rstrip(";").strip()

    qvec_str = "[" + ",".join(f"{float(v):.6f}" for v in qvec) + "]"
    vec_lit = f"'{qvec_str}'::vector"

    def _repl(m: re.Match) -> str:                    # 벡터 술어 + threshold 동시 치환
        return f"{m.group(1)}{vec_lit}{m.group(2)}{float(D):.6f}"

    sql, n_pred = re.subn(
        r"(<->\s*)'image_embedding'(\s*<\s*)[0-9.]+", _repl, sql)
    if n_pred != 1:
        raise ValueError(f"{query}: 벡터 술어 치환 {n_pred}건 (정확히 1건 기대)")
    sql = sql.replace("'image_embedding'", vec_lit)   # ORDER BY 잔여 placeholder

    if marker:
        sql = f"/* {marker} */\n{sql}"
    return sql


# ---------------------------------------------------------------------------
# GUC — 조건별 주입 (서버 vector.c 패치)
# ---------------------------------------------------------------------------

def gucs_for(condition: str, injected_card) -> list[str]:
    """조건별 SET 문 목록. 전 조건 공통으로 update_sample_size 를 끈다."""
    g = ["SET vector.update_sample_size = off"]
    if condition == "baseline":
        g.append("SET vector.disable_estimation = on")
    else:                                             # B1 / CaseB / oracle
        g.append("SET vector.disable_estimation = off")
        card = max(float(injected_card), MIN_INJECT)
        g.append(f"SET vector.injected_card = {card:.6f}")
    return g


# ---------------------------------------------------------------------------
# 측정 (서버 — psycopg 필요)
# ---------------------------------------------------------------------------

def _connect():
    if psycopg is None:
        raise RuntimeError("psycopg 미설치 — 서버(165.132.140.240 capstone2026)에서 실행")
    return psycopg.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB,
                           user=PG_USER, autocommit=True)


def _prepare_session(cur, view_ddls: list[str], *, auto_explain: bool = False) -> None:
    """세션 공통 준비 — 라이브러리 로드 + 임시 VIEW 생성.

    ★ LOAD 순서가 중요하다 — auto_explain 을 vector 보다 **먼저** 로드해야 한다.
    vector 를 먼저 로드하면 ExecutorEnd 훅 체인이 explain→pgvector 순이 되어, Exqutor
    2-pass(pgvector_ExecutorRun 내부에서 standard_ExecutorEnd 직접 호출) 시 auto_explain
    의 ExecutorEnd 가 우회돼 pass-2 플랜이 로깅되지 않는다. auto_explain 을 먼저 로드하면
    pgvector 의 prev_ExecutorEnd 가 explain_ExecutorEnd 가 되어 2-pass 양쪽 다 로깅된다
    (서버 실측 확인 — pass-1 dur≈0 / pass-2 real, 블록 2개).
    """
    if auto_explain:
        cur.execute("LOAD 'auto_explain'")
    cur.execute("LOAD 'vector'")
    # ★ 자원 점유 cap (5/20 carry — 다른 user 작업 점유 회피 + 측정 안정성)
    cur.execute("SET work_mem = '256MB'")                  # default 4MB → 256MB (sort/hash 메모리)
    cur.execute("SET max_parallel_workers_per_gather = 2") # default 2 (query 당 max worker 3 = leader + 2)
    for ddl in view_ddls:
        cur.execute(ddl)


def _run_timed(sql: str, view_ddls: list[str], condition: str, injected_card,
               statement_timeout: str):
    """새 세션 1회 — 실쿼리 직접 실행 + perf_counter timing. (exec_ms) 반환.

    timeout/에러 시 None (censored). EXPLAIN 미사용 — 2-pass 오버헤드 포함 정직한 값.
    """
    try:
        with _connect() as conn:
            cur = conn.cursor()
            _prepare_session(cur, view_ddls)
            for g in gucs_for(condition, injected_card):
                cur.execute(g)
            cur.execute("SET plan_cache_mode = force_custom_plan")
            cur.execute(f"SET statement_timeout = '{statement_timeout}'")
            t0 = time.perf_counter()
            cur.execute(sql)
            cur.fetchall()                            # 결과 전송까지 — end-to-end
            return (time.perf_counter() - t0) * 1000.0
    except Exception as e:                            # QueryCanceled(timeout) 포함
        print(f"[{kst()}]   ! {type(e).__name__}: {str(e)[:120]}")
        return None


_INJECT_LOG_RE = re.compile(
    r"Estimated cardinality for range query on table\s+\S+:\s*([0-9.]+)")
_DURATION_RE = re.compile(r"duration:\s*([0-9.]+)\s*ms")


def _parse_capture(notices: list[str], marker: str):
    """auto_explain client notice 파싱 → (plan_json, plan_dur_ms, injection_fired, card_seen).

    injected 조건은 블록 2개(pass-1 dur≈0 / pass-2 real)가 온다 → 최대 duration = pass-2.
    """
    plans = []                                        # (duration_ms, plan_dict)
    injection_fired = False
    card_seen = None
    for msg in notices:
        mi = _INJECT_LOG_RE.search(msg)
        if mi:
            injection_fired = True
            card_seen = float(mi.group(1))
            continue
        if "plan:" not in msg or marker not in msg:
            continue
        md = _DURATION_RE.search(msg)
        dur = float(md.group(1)) if md else -1.0
        try:
            obj = json.loads(msg.split("plan:", 1)[1].strip())
        except Exception:
            continue
        if isinstance(obj, list):                     # EXPLAIN-style 배열 방어
            obj = obj[0] if obj else {}
        plan = obj.get("Plan", obj) if isinstance(obj, dict) else obj
        plans.append((dur, plan))
    plan_json, plan_dur = None, None
    if plans:
        plans.sort(key=lambda x: x[0])
        plan_dur, plan_json = plans[-1]               # 최대 duration = pass-2 실행 플랜
    return plan_json, plan_dur, injection_fired, card_seen


def _capture_plan(query: str, qvec, D: float, view_ddls: list[str],
                  condition: str, injected_card, statement_timeout: str,
                  *, analyze: bool = False) -> dict:
    """새 세션 1회 — auto_explain 으로 pass-2 실행 플랜 캡처.

    auto_explain LOG 를 client_min_messages=log 로 클라이언트에 받아 파싱한다.
    실패해도 치명적이지 않다 (latency 가 1차 지표) — plan_json=None 으로 반환.

    analyze=True 면 auto_explain.log_analyze/log_timing 을 켜 노드별 Actual Total Time·
    Actual Rows 가 plan_json 에 포함된다. ★ 단 instrumentation 오버헤드가 실행시간을
    부풀리므로 이 캡처의 plan_duration_ms 는 정직한 latency 가 아니다 — 노드 시간 '분해'
    용으로만 쓰고, latency 수치는 별도 비-analyze timed 측정(_run_timed)을 쓴다.
    """
    marker = f"cap_{uuid.uuid4().hex[:12]}"
    sql = build_vaq_sql(query, qvec, D, marker=marker)
    notices: list[str] = []
    try:
        with _connect() as conn:
            conn.add_notice_handler(
                lambda diag: notices.append(diag.message_primary or ""))
            cur = conn.cursor()
            _prepare_session(cur, view_ddls, auto_explain=True)
            cur.execute("SET client_min_messages = 'log'")
            cur.execute("SET auto_explain.log_min_duration = 0")
            cur.execute("SET auto_explain.log_format = 'json'")
            cur.execute("SET auto_explain.log_nested_statements = 'off'")
            if analyze:
                cur.execute("SET auto_explain.log_analyze = on")
                cur.execute("SET auto_explain.log_timing = on")
                cur.execute("SET auto_explain.log_buffers = on")
            else:
                cur.execute("SET auto_explain.log_analyze = off")
            for g in gucs_for(condition, injected_card):
                cur.execute(g)
            cur.execute("SET plan_cache_mode = force_custom_plan")
            cur.execute(f"SET statement_timeout = '{statement_timeout}'")
            cur.execute(sql)
            cur.fetchall()
    except Exception as e:
        print(f"[{kst()}]   ! _capture_plan {type(e).__name__}: {str(e)[:120]}")
        return {"plan_json": None, "plan_duration_ms": None,
                "injection_fired": False, "injected_card_seen": None}
    plan_json, plan_dur, fired, seen = _parse_capture(notices, marker)
    return {"plan_json": plan_json, "plan_duration_ms": plan_dur,
            "injection_fired": fired, "injected_card_seen": seen}


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


def measure_cell(query, dataset, sf, sel, query_id, qvec, D, true_card,
                 est_b1, caseb_by_method, *, n_timed, n_warmup, statement_timeout,
                 seed=20260520, analyze_plans=False, capture_only=False) -> dict:
    """한 cell(query×dataset×sf×sel×query_id)의 전 variant 측정.

    variant = (condition, method). 매 반복 variant 순서를 무작위 셔플 — 같은 반복 내
    모든 variant 인접 실행(matched) + 캐시 워밍 순서 편향 완화. 플랜 캡처는 timed 루프
    밖에서 variant 당 1회 (auto_explain 오버헤드가 timing 을 오염하지 않도록 분리).

    analyze_plans=True 면 플랜 캡처를 EXPLAIN ANALYZE 모드로 — 노드별 Actual Total Time
    포함 (Phase 3b 노드 분해용). capture_only=True 면 timed 루프를 건너뛰고 플랜만 캡처
    (latency 무측정 — exec_ms 빈 리스트).
    """
    sql = build_vaq_sql(query, qvec, D)
    view_ddls = temp_view_ddls(dataset, sf)
    vec_tbl = vec_table_name(dataset, sf)

    # variant 정의: (condition, method, injected_card)
    variants = [("baseline", None, None), ("B1", None, est_b1),
                ("oracle", None, true_card)]
    for m, est in caseb_by_method.items():
        variants.append(("CaseB", m, est))
    keys = [(c, m) for (c, m, _) in variants]
    inj_by_key = {(c, m): inj for (c, m, inj) in variants}

    # --- 플랜 캡처 (variant 당 1회 — 캐시 워밍도 겸함) ---
    captured: dict[tuple, dict] = {}
    for (c, m, inj) in variants:
        captured[(c, m)] = _capture_plan(query, qvec, D, view_ddls, c, inj,
                                         statement_timeout, analyze=analyze_plans)
        cap = captured[(c, m)]
        print(f"[{kst()}]   plan-capture {c}/{m or '-'}: "
              f"injection_fired={cap['injection_fired']} "
              f"card_seen={cap['injected_card_seen']}")

    # --- timed 반복 ---
    samples = {k: [] for k in keys}
    timeouts = {k: 0 for k in keys}
    rng = random.Random(seed)
    if capture_only:
        print(f"[{kst()}]   capture-only — timed 루프 생략")
    for rep in range(0 if capture_only else n_warmup + n_timed):
        order = keys[:]
        rng.shuffle(order)
        for k in order:
            c, m = k
            ms = _run_timed(sql, view_ddls, c, inj_by_key[k], statement_timeout)
            if rep >= n_warmup:
                if ms is None:
                    timeouts[k] += 1
                else:
                    samples[k].append(ms)
        print(f"[{kst()}]   rep {rep + 1}/{n_warmup + n_timed} 완료")

    # --- 집계 ---
    out_variants = []
    for (c, m, inj) in variants:
        k = (c, m)
        vals = samples[k]
        cap = captured[k]
        qerr = None
        if inj is not None and true_card and inj > 0:
            qerr = max(inj / true_card, true_card / inj)
        out_variants.append({
            "condition": c, "method": m, "injected_card": inj, "q_error": qerr,
            "exec_ms": vals, "n_timeout": timeouts[k],
            "exec_ms_trimmed": _trimmed_mean(vals),
            "exec_ms_median": (statistics.median(vals) if vals else None),
            "exec_ms_iqr": _iqr(vals),
            "plan_json": cap["plan_json"],
            "plan_duration_ms": cap["plan_duration_ms"],
            "injection_fired": cap["injection_fired"],
            "injected_card_seen": cap["injected_card_seen"],
        })
    return {
        "family": "tpc_h", "query": query, "dataset": dataset, "sf": sf,
        "sel": sel, "query_id": query_id, "D": D, "true_card": true_card,
        "vec_table": vec_tbl, "n_warmup": n_warmup, "n_timed": n_timed,
        "statement_timeout": statement_timeout,
        "variants": out_variants, "kst": kst(),
    }


def load_estimates(path: Path, dataset, sf, sel, query_id, methods):
    """gen_latency_estimates.py 산출 parquet 에서 한 cell 의 추정치 추출.

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
# dry-run (서버 미접속 — SQL 변환·GUC·임시 VIEW DDL 검증)
# ---------------------------------------------------------------------------

def _dry_run(args) -> None:
    dim = DS_DIM[args.dataset]
    qvec = np.random.default_rng(0).standard_normal(dim).astype(np.float32)
    D = 0.86
    print(f"=== dry-run: {args.query} dataset={args.dataset} sf={args.sf} dim={dim} ===\n")

    print("--- 임시 VIEW DDL (세션마다 생성) ---")
    for ddl in temp_view_ddls(args.dataset, args.sf):
        print(f"  {ddl}")

    print("\n--- 조건별 GUC ---")
    for cond, inj in [("baseline", None), ("B1", 123456), ("CaseB", 0.0),
                      ("oracle", 130000)]:
        print(f"  {cond:<9}: {'; '.join(gucs_for(cond, inj))}")

    sql = build_vaq_sql(args.query, qvec, D)
    assert "'image_embedding'" not in sql, "placeholder 'image_embedding' 잔여"
    assert sql.count("::vector") == 2, f"::vector {sql.count('::vector')}개 (2 기대)"
    assert "EXPLAIN" not in sql.upper(), "EXPLAIN 잔여"
    assert "/*+" not in sql, "pg_hint_plan 힌트 잔여"
    cap_sql = build_vaq_sql(args.query, qvec, D, marker="cap_test")
    assert "/* cap_test */" in cap_sql, "marker 주석 누락"

    head = sql if len(sql) < 800 else sql[:800] + " …"
    print(f"\n--- 실행 SELECT ({args.query}) ---\n{head}")
    print("\n✓ dry-run 통과 — SQL 변환·GUC·임시 VIEW·marker 정상")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="실엔진 latency 측정 harness (TPC-H)")
    ap.add_argument("--query", required=True, choices=TPC_H_QUERIES, help="q3 / q5 / …")
    ap.add_argument("--dataset",
                    choices=["DEEP", "SIFT", "SSN", "WIKI", "YFCC",
                             "DEEP_SIFT", "DEEP_WIKI"],
                    default="DEEP")
    ap.add_argument("--sf", type=int, default=10)
    ap.add_argument("--sel", type=float, default=0.01)
    ap.add_argument("--query-id", type=int, default=0)
    ap.add_argument("--estimates", type=Path,
                    help="gen_latency_estimates.py 산출 parquet (real run 필수)")
    ap.add_argument("--methods", nargs="+", default=list(DEFAULT_CASEB_METHODS),
                    help="CaseB 결합 method 목록 (기본: 강한 13종)")
    ap.add_argument("--n-timed", type=int, default=15)
    ap.add_argument("--n-warmup", type=int, default=1)
    ap.add_argument("--statement-timeout", default="180s",
                    help="cell timeout — sf=100 IO bound base 600s→180s 단축 (5/20 22:53). "
                         "censoring 도달 시 None(None_count 기록)")
    ap.add_argument("--output", type=Path, default=Path("latency"))
    ap.add_argument("--analyze-plans", action="store_true",
                    help="플랜 캡처를 EXPLAIN ANALYZE 모드로 (노드별 Actual Total Time) — "
                         "출력 파일명에 _analyze suffix")
    ap.add_argument("--capture-only", action="store_true",
                    help="timed 루프 생략 — 플랜만 캡처 (latency 무측정)")
    ap.add_argument("--dry-run", action="store_true",
                    help="서버 미접속 — SQL 변환·GUC·임시 VIEW DDL 검증")
    args = ap.parse_args()

    if args.dry_run:
        _dry_run(args)
        return

    if not args.estimates:
        ap.error("--estimates 필요 (real run) — 또는 --dry-run")

    qvec, D, true_card, est_b1, caseb = load_estimates(
        args.estimates, args.dataset, args.sf, args.sel, args.query_id, args.methods)
    print(f"[{kst()}] cell tpc_h/{args.query} {args.dataset} sf{args.sf} "
          f"sel{args.sel} qid{args.query_id}: D={D:.4f} true={true_card:.0f} "
          f"est_b1={est_b1:.0f} caseB={{{', '.join(f'{m}:{v:.0f}' for m, v in caseb.items())}}}")

    result = measure_cell(
        args.query, args.dataset, args.sf, args.sel, args.query_id,
        qvec, D, true_card, est_b1, caseb,
        n_timed=args.n_timed, n_warmup=args.n_warmup,
        statement_timeout=args.statement_timeout,
        analyze_plans=args.analyze_plans, capture_only=args.capture_only)

    args.output.mkdir(parents=True, exist_ok=True)
    suffix = "_analyze" if (args.analyze_plans or args.capture_only) else ""
    out = args.output / (f"latency_tpc_h_{args.query}_{args.dataset}"
                         f"_sf{args.sf}_sel{args.sel}_qid{args.query_id}{suffix}.json")
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"[{kst()}] saved {out}")


if __name__ == "__main__":
    main()
