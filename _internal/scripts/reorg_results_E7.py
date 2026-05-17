#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E7 측정 데이터 재정리 — 복사 기반 안전 모드 (raw 원본 절대 보존).

소스 2개 (서로 다른 측정 캠페인):
  experiments/results/raw/            691 json — paper-exact portfolio (CaseB 56 method + B1)
  _internal/cache/rq3/server_sync/   1241 json — 확장 측정 v6~v10 (CaseB 16 method + B1)

타깃: experiments/results/ 아래 측정 트랙 6 + _summary + _archive 2

설계 원칙:
  - cell 코드 -> 의미명 ({데이터셋}_{sf}); cell 이 의미명 충돌 시 cell 코드 자체로 disambiguate
  - sel / K / alpha 는 JSON 에 없고 디렉토리 경로에만 — 경로에서 추출해 트랙 분기
  - raw 의 RQ3_CaseB / RQ1_baseline 은 paper_main / _shared_B1 의 byte-identical 사본 -> 스킵
  - 16 method 외 + CaseA -> _archive_미사용method
  - A2-Fig8(DEEP+CC3M), TPCDS -> _archive_scope외

사용법:
  python3 _internal/scripts/reorg_results_E7.py          # dry-run
  python3 _internal/scripts/reorg_results_E7.py --apply  # 실제 복사
"""
import os, re, json, sys, shutil, hashlib
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW  = os.path.join(ROOT, "experiments/results/raw")
SRV  = os.path.join(ROOT, "_internal/cache/rq3/server_sync")
DST  = os.path.join(ROOT, "experiments/results")
APPLY = "--apply" in sys.argv

# ---- 본 트랙 16 method ----
M16 = ['minibatch_partial','gmm','faiss_ivf','hilbert_real','zorder_morton','skilling_hilbert',
       'chao_weighted','sparse_rp','pca1d','rsvd','ica_fastica','cum_sqrtf','lavallee_hidiroglou',
       'rabitq_strat','mhist2','hyperloglog']
M16S = set(M16)

# ---- cell -> (데이터셋 라벨, sf) ; single/multi 는 데이터셋명으로 판별 ----
CELLMAP = {
 'A1-DEEP':('DEEP',100),  'A1-SIFT':('SIFT',100),  'A1-SSN':('SSN',100),
 'A2-Fig7':('YFCC',10),   'A2-Fig9':('DEEP+WIKI',10),
 'A5-scale-sf1':('DEEP',1), 'A5-scale-sf10':('DEEP',10), 'A5-scale-sf100':('DEEP',100),
 'A6-WIKI-sf1':('WIKI',1), 'A6-WIKI-sf10':('WIKI',10),
 'A7-YFCC-sf1':('YFCC',1),
 'A8-DEEP+SIFT-sf10':('DEEP+SIFT',10),
 'A4-sel':('DEEP',100),
 'A2-Fig8':('DEEP+CC3M',None),
}
for sf in (1,10,100):
    for ds in ('SIFT','SSN'):
        CELLMAP[f'A5-scale-sf{sf}-{ds}']=(ds,sf)
for ds in ('SIFT','SSN'):
    for k in (10,30):
        CELLMAP[f'A1-{ds}_K{k}']=(ds,100)
CONCAT_PFX = {('DEEP','SIFT'):9, ('DEEP','WIKI'):10, ('DEEP','YFCC'):11}
for (a,b),p in CONCAT_PFX.items():
    for sf in ((1,10,100) if b=='SIFT' else (1,10)):
        CELLMAP[f'A{p}-{a}+{b}-concat-sf{sf}']=(f'{a}+{b}',sf)

# 의미명 충돌 cell: 같은 (데이터셋,sf) 인 cell 들은 cell 코드로 구분
#   A1-DEEP / A4-sel / A5-scale-sf100  모두 DEEP sf100  ->  의미명에 측정맥락 suffix
CELL_DISAMBIG = {
 'A1-DEEP':'DEEP_sf100',          # Fig 5/6/12 baseline
 'A4-sel':'DEEP_sf100_Fig13sel',  # Fig 13 단일 sel cell (sel sweep 아님)
 'A5-scale-sf100':'DEEP_sf100_scaleaxis',  # Fig 14 scale axis
}

def dsname(cell):
    """cell -> 디렉토리 의미명. 충돌 cell 은 disambiguated."""
    if cell in CELL_DISAMBIG:
        return CELL_DISAMBIG[cell]
    ds,sf = CELLMAP[cell]
    base = re.sub(r'_K\d+$','',cell)  # K-suffix 제거 후
    if 'concat' in cell:
        a,b = ds.split('+')
        return f"{a}+{b}_concat_sf{sf}"
    return f"{ds}_sf{sf}"

def walk_json(root):
    out=[]
    for dp,dn,fn in os.walk(root):
        for f in fn:
            if f.endswith(".json"): out.append(os.path.join(dp,f))
    return sorted(out)

def parse_mode_method(bn):
    m=re.search(r'_(CaseA|CaseB)_(.+)$',bn)
    if m: return m.group(1),m.group(2)
    if bn.endswith("_B1") or "B1_paper" in bn or bn.endswith("B1_paper_baseline"):
        return "B1","baseline"
    return "OTHER",bn

def jmeta(f):
    try:
        d=json.load(open(f))
        return (d.get('cell'),d.get('dataset'),d.get('sf'),
                d.get('mode'),d.get('method'),d.get('selectivity'))
    except Exception:
        return (None,)*6

def fhash(f):
    return hashlib.md5(open(f,'rb').read()).hexdigest()

# canonical paper_main / _shared_B1 file 의 hash 집합 (byte-dup 판정용)
_CANON_HASHES = None
def canon_hashes():
    global _CANON_HASHES
    if _CANON_HASHES is None:
        _CANON_HASHES=set()
        for f in walk_json(RAW):
            rel=os.path.relpath(f,ROOT)
            if ('_paper_main/' in rel or '_shared_B1' in rel) \
               and '_RQ3_CaseB/' not in rel and '_RQ1_baseline/' not in rel \
               and '_archive_underscore_duplicates' not in rel:
                _CANON_HASHES.add(fhash(f))
    return _CANON_HASHES

def route(src):
    """반환: (track, subdir, newname) 또는 None(스킵)"""
    rel = os.path.relpath(src, ROOT)
    bn  = os.path.basename(src)[:-5]
    cell, ds_meta, sf_meta, mode, method, sel_meta = jmeta(src)
    pmode, pmethod = parse_mode_method(bn)
    mode   = mode or pmode
    method = method or pmethod

    if cell not in CELLMAP:
        return ('_UNROUTED', 'cell='+str(cell), bn+'.json')

    # raw 내부 중복 archive 스킵
    if '_archive_underscore_duplicates' in rel:
        return None
    # raw RQ3_CaseB / RQ1_baseline: paper_main / _shared_B1 와 byte-identical 인 것만 스킵.
    #   (대부분 5/15 reorg 사본이나 일부 cell — 예: A2-Fig9 RQ3_CaseB — 은 독립 측정이라 보존)
    if '_RQ3_CaseB/' in rel or '_RQ1_baseline/' in rel:
        if fhash(src) in canon_hashes():
            return None
        # 독립 측정 — RQ3_CaseB detail 트랙으로 보존

    is_srv = 'server_sync' in rel
    is16 = (mode == 'B1') or (method in M16S)
    is_caseA = (mode == 'CaseA')
    dn = dsname(cell)        # 디렉토리 의미명

    # ---- scope 외 (A2-Fig8 DEEP+CC3M, paper §V-A multi-vector) ----
    if cell == 'A2-Fig8':
        # raw 에 두 sub-folder (multi_vector_paper_main / paper_main) 존재 — 둘 다 보존
        origin = 'multi_vector_paper_main' if 'multi_vector_paper_main' in rel else 'paper_main'
        return ('_archive_scope외', f'DEEP+CC3M_multi-vector/{origin}', bn+'.json')

    # ---- raw alpha_sweep 직속(loose) 파일: alpha_0.X 구조 이전 5/14 stale 사본 -> archive ----
    if '/A2-Fig9_alpha_sweep/' in rel and not re.search(r'alpha_0\.\d', rel):
        return ('_archive_미사용method', '06_부가측정/alpha_sweep/_stale_pre5_15_loose', bn+'.json')

    # ---- 경로에서 sel / K / alpha 추출 ----
    sel=None
    if 'sel0.001' in rel: sel='0.001'
    elif 'sel0.10' in rel: sel='0.10'
    elif 'sel0.01' in rel: sel='0.01'
    elif sel_meta is not None: sel=('%g'%sel_meta)

    # K: 경로 디렉토리명 어디든 'K=10' / 'K10' / '_K30' 형태
    K=None
    mK=re.search(r'K=(\d+)', rel)
    mK2=re.search(r'_K(\d+)(?:[_/]|$)', rel)
    mK3=re.search(r'/K(\d+)/','/'+rel)
    if mK:    K=mK.group(1)
    elif mK2: K=mK2.group(1)
    elif mK3: K=mK3.group(1)

    malpha=re.search(r'alpha_(0\.\d)', rel)
    alpha=malpha.group(1) if malpha else None

    fnmeth = method if mode!='B1' else None
    def mkname(prefix):
        return f"{prefix}_{mode}_{method}.json" if mode!='B1' else f"{prefix}_B1.json"

    # ================= 04 multi_vector concat =================
    if 'concat' in cell:
        sub=f"{dn}/sel{sel}/{mode}"
        nn=mkname(dn.replace('_concat_','_concat_'))
        if is16 and not is_caseA:
            return ('04_multi_vector_concat', sub, nn)
        return ('_archive_미사용method', f"04_multi_vector_concat/{sub}", nn)

    # ================= 03 selectivity sweep (sel 0.001 / 0.10) =================
    if sel in ('0.001','0.10'):
        ksuf=f"_K{K}" if K else ""
        sub=f"{dn}{ksuf}/sel{sel}/{mode}"
        nn=mkname(f"{dn}{ksuf}")
        if is16 and not is_caseA:
            return ('03_selectivity_sweep', sub, nn)
        return ('_archive_미사용method', f"03_selectivity_sweep/{sub}", nn)

    # ================= 05 K granularity (K 지정, sel=0.01 base) =================
    if K is not None:
        prov = 'run-v6-v10' if is_srv else 'run-paper-exact'
        sub=f"{dn}/K{K}/{prov}/{mode}"
        nn=mkname(f"{dn}_K{K}")
        if is16 and not is_caseA:
            return ('05_K_granularity', sub, nn)
        return ('_archive_미사용method', f"05_K_granularity/{sub}", nn)

    # ================= 06 부가측정 =================
    if alpha is not None:
        sub=f"alpha_sweep/{dn}/alpha_{alpha}/{mode}"
        nn=mkname(f"{dn}_alpha{alpha}")
        t='06_부가측정' if (is16 and not is_caseA) else '_archive_미사용method'
        return (t, sub if t=='06_부가측정' else f"06_부가측정/{sub}", nn)
    if 'cheap_approximation' in rel:
        variant=rel.split('cheap_approximation/')[1].split('/')[0]
        sub=f"cheap_approximation/{dn}/{variant}/{mode}"
        nn=mkname(f"{dn}_{variant}")
        t='06_부가측정' if (is16 and not is_caseA) else '_archive_미사용method'
        return (t, sub if t=='06_부가측정' else f"06_부가측정/{sub}", nn)
    if 'multi_join' in rel:
        sub=f"multi_join_restratification/{dn}/{mode}"
        nn=mkname(f"{dn}_multijoin")
        t='06_부가측정' if (is16 and not is_caseA) else '_archive_미사용method'
        return (t, sub if t=='06_부가측정' else f"06_부가측정/{sub}", nn)

    # ================= 01 B1 baseline (paper §V-B) =================
    if mode == 'B1':
        # raw _shared_B1 = paper §V-B 9 cell 정준 baseline
        # server_sync B1 (sel=0.01 base, v6~v10) = 확장 측정 baseline
        prov='run-v6-v10' if is_srv else 'run-paper-exact'
        sub=f"{dn}/{prov}"
        return ('01_baseline_paper재현', sub, f"{dn}_B1.json")

    # ================= 02 본실험 single, sel=0.01 base =================
    if is_srv:
        prov='run-v6-v10'
    elif '_RQ3_CaseB/' in rel:
        prov='run-rq3-detail'   # raw RQ3_CaseB 독립 측정 (paper_main 과 별개 run)
    else:
        prov='run-paper-exact'
    sub=f"{dn}/{prov}/{mode}"
    nn=mkname(dn)
    if is16 and not is_caseA:
        return ('02_single_vector_본실험', sub, nn)
    return ('_archive_미사용method', f"02_single_vector_본실험/{sub}", nn)

# ---- 실행 ----
def main():
    raw=walk_json(RAW); srv=walk_json(SRV)
    allf=raw+srv
    print(f"소스: raw {len(raw)} + server_sync {len(srv)} = {len(allf)} json\n")

    track_count=Counter()
    coll=defaultdict(list)
    skipped=[]
    for src in allf:
        r=route(src)
        if r is None:
            skipped.append(src); continue
        track,sub,nn=r
        d=os.path.join(DST,track,sub,nn)
        coll[d].append(src)
        track_count[track]+=1

    # 충돌 해소
    final=[]
    coll_n=0
    coll_detail=[]
    for d,srcs in coll.items():
        if len(srcs)==1:
            final.append((srcs[0],d))
        else:
            for i,s in enumerate(sorted(srcs)):
                if i==0: final.append((s,d))
                else:
                    base,ext=os.path.splitext(d)
                    final.append((s,f"{base}__r{i+1}{ext}")); coll_n+=1
            coll_detail.append((d,srcs))

    print("=== 트랙별 라우팅 ===")
    for k,v in sorted(track_count.items()):
        print(f"  {k}: {v}")
    print(f"\n  스킵(raw 중복 사본 RQ3_CaseB/RQ1_baseline/내부archive): {len(skipped)}")
    print(f"  잔여 충돌 (__r suffix): {coll_n}  케이스 {len(coll_detail)}")
    print(f"  총 복사: {len(final)}")
    print(f"  검산: 복사 {len(final)} + 스킵 {len(skipped)} = {len(final)+len(skipped)}  (소스 {len(allf)})")

    if coll_detail:
        print("\n  [잔여 충돌 케이스 — 검토]")
        for d,srcs in coll_detail[:12]:
            print(f"   {os.path.relpath(d,DST)}")
            for s in srcs: print(f"     <- {os.path.relpath(s,ROOT)}")

    if not APPLY:
        print("\n[DRY-RUN] --apply 로 실제 복사")
        return final

    copied=0
    for s,d in final:
        os.makedirs(os.path.dirname(d),exist_ok=True)
        shutil.copy2(s,d)
        copied+=1
    print(f"\n[APPLY] {copied} file 복사 완료.")
    return final

if __name__=="__main__":
    main()
