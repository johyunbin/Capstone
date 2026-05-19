# Handoff v5 — Phase 4 RQ3 신규 method 11건 + 메인 인계 (5/11 01:10 KST)

> 메인 세션 대기 중 인계. 본 handoff = Phase 4 별도 세션 (5/11 00:30~01:10) 결과 종합 + 즉시 액션 sequence.
> 사용자 명시 (5/11 01:05): "ㅇㅋ. 모두 다 진행할거라서. 순서대로 해도 무관. server scp는 메인 세션에서 진행. Q4 Tier 1 통합도 최종 handoff에서. 메인이 대기 중이라서."

---

## 0. TL;DR (메인 세션 즉시 액션 5단계)

1. SSH 검증: `ssh capstone2026@165.132.140.240 "date && pgrep -af measure_paper | wc -l"`
2. Phase 4 file 3건 scp (단일 명령):
   ```bash
   scp /Users/hyunbin/Capstone/_internal/scripts/method_phase4_extra.py \
       capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/method_phase4_extra.py
   ```
3. measure_paper_exact.py PATCH 적용 (§3 코드 verbatim) → scp
4. server smoke: `ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 method_phase4_extra.py"`
5. measurement launch: `./run_phase_b_phase4.sh --all` (tmux 분할 권고) — Q4 Tier 1 6 method 와 통합 → §7 권고 sequence

---

## 1. Phase 4 별도 세션 결과 요약

### 1.1 작업 (35분, 00:30 → 01:05 KST)

8 학술 카테고리 + 산업 codebase + arXiv 2020-25 systematic walkthrough → ~553 method 발굴 (신규 ~470). 14 필터 brainstorming → 7 critical filter cascade → **11 method 통과**. Implementation + smoke 11/11 PASS.

### 1.2 메인 chain bvf1k64kw 영향 0 확인

- ❌ server 측정 데이터 변경: 0건
- ❌ measure_paper_exact.py 패치 안 함 (로컬만 작성, server 미접촉)
- ❌ tmux/PG/cache: 0 영향
- ✅ 신규 module 로컬 작성 + smoke 로컬만

### 1.3 Cascade 단계별 drop count

| Stage | 잔존 | drop |
|---|---|---|
| Start (신규 only) | 470 | 0 |
| **G 정직성** | 282 | -188 (학술 alias / cosmetic / line-by-line ==) |
| **I Redundancy** | 142 | -140 (현재 46 portfolio 본질 동일) |
| **J Vector DB scope** | 95 | -47 (multi-table only / RL only / proprietary) |
| **B 공간 복잡도** | 73 | -22 (OOM risk N² matrix) |
| **A 시간 복잡도** | 50 | -23 (O(N³) / O(N²·D) infeasible) |
| **F Outperform 보장** | 18 | -32 (★ 4강 alias / inductive bias 약) |
| **E 학술 정합** | **11** | -7 (paradigm scope outside / Exqutor §V-B 부적합) |

---

## 2. Phase 4 11 ★ Method (최종 통과)

| # | code | method_name (registry) | reference verbatim | paradigm | 예상 Δ% | priority |
|---|---|---|---|---|---|---|
| 1 | M1 | `chao_weighted` | Chao MT. *Biometrika* 1982; 69(3):653-656 | P3 weight | -3 ~ -7% | P0 |
| 2 | M2 | `lpm1_proper` | Grafström-Lundström-Schelin. *Biometrics* 2012; 68(2):514-520 | P2+P3 | -3 ~ -7% | **P0 (lpm2 misnomer rectify)** |
| 3 | M3 | `cum_sqrtf` | Dalenius-Hodges. *JASA* 1959; 54(285):88-101 | P5 | -2 ~ -5% | P1 |
| 4 | M4 | `lavallee_hidiroglou` | Lavallée-Hidiroglou. *Survey Method* 1988; 14(1):33-43 | P5+RQ2 | -2 ~ -5% | P1 |
| 5 | M5 | `idistance` | Jagadish-Ooi-Tan-Yu-Zhang. *TODS* 2005; 30(2):364-397 | P2 | -3 ~ -6% | P0 |
| 6 | M6 | `zorder_morton` | Morton GM. *IBM Tech Rep* 1966 | P2 (anchor) | -3 ~ -7% | **P0 (paradigm anchor)** |
| 7 | M7 | `skilling_hilbert` | Skilling J. *AIP Conf Proc* 2004; 707:381-387 | P2 (★3 rectify) | -3 ~ -7% | **P0 (Q1 (C))** |
| 8 | M8 | `ica_fastica` | Hyvärinen A. *IEEE NN* 1999; 10(3):626-634 | P4 | -2 ~ -6% | P1 |
| 9 | M9 | `kmeans_neyman` | Cochran 1977 §5 + Neyman 1934 *JRSS* | P1+RQ2 | -3 ~ -7% | **P0 (RQ2 plug-in)** |
| 10 | M10 | `rabitq_strat` | Gao-Lin. *PVLDB* 2024; 17(11):3252-3265 | P6 | -3 ~ -7% | P1 (2024 fresh) |
| 11 | M11 | `idistance_neyman` | Jagadish 2005 + Neyman 1934 (synthesis) | P2+RQ2 | -3 ~ -7% | **P0 (synthesis)** |

**Paradigm 강화**: 9 paradigm 중 6개 강화 (P1+RQ2 / P2 (3) / P2+RQ2 / P3 / P4 / P5+RQ2 / P6).

---

## 3. measure_paper_exact.py PATCH (line ~484 직후 삽입)

기존 Q4 Tier 1 분기 (line 471-483) 직후에 추가:

```python
    if method_name in (
        "chao_weighted", "lpm1_proper", "cum_sqrtf", "lavallee_hidiroglou",
        "idistance", "zorder_morton", "skilling_hilbert", "ica_fastica",
        "kmeans_neyman", "rabitq_strat", "idistance_neyman",
    ):
        # Phase 4 신규 11 method (cascade 7 stage 통과)
        # 출처: _internal/method_verification_20260510_phase4/_FINAL_LIST.md
        # 5/27 narrative 강화: P1+RQ2 / P2 (3) / P3 weight / P4 non-Gaussian / P5+RQ2 / P6 1-bit
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_phase4_extra import assign_phase4
        return assign_phase4(method_name, all_vecs, n_strata=n_strata, seed=seed)
```

### 3.1 추가 위치 정확 line (서버 측 file 기준)

```bash
# 패치 추가 위치 확인 (server)
ssh capstone "grep -n 'method_tier1_p9_p10' /mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py"
# 출력 line 직후 12 line 추가 (위 코드 verbatim)
```

### 3.2 patch 적용 sed/awk 또는 직접 Edit

권고 (메인 세션):
```bash
# 옵션 A: 로컬 file 패치 후 scp (안전)
# 1. measure_paper_exact.py read (line 471-490)
# 2. line 484 (return 직후) 위 코드 삽입
# 3. scp _internal/scripts/measure_paper_exact.py capstone:/mnt/hdd0/home/capstone2026/cache/rq3/

# 옵션 B: server 측 직접 vi/sed (덜 권고 — 검증 어려움)
```

---

## 4. Server scp 명령 (단일 sequence)

```bash
# 1. method_phase4_extra.py 신규 module scp
scp /Users/hyunbin/Capstone/_internal/scripts/method_phase4_extra.py \
    capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/method_phase4_extra.py

# 2. measure_paper_exact.py 패치 적용 후 scp (위 §3 코드 추가 후)
scp /Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py \
    capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py

# 3. launcher script scp
scp /Users/hyunbin/Capstone/_internal/scripts/run_phase_b_phase4.sh \
    capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/run_phase_b_phase4.sh

ssh capstone "chmod +x /mnt/hdd0/home/capstone2026/cache/rq3/run_phase_b_phase4.sh"
```

---

## 5. Server smoke test (scp 후 즉시)

```bash
# 1. import 검증 + 11 method dispatch
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  python3 -c 'from method_phase4_extra import ASSIGN_FN_MAP; print(len(ASSIGN_FN_MAP), list(ASSIGN_FN_MAP.keys()))'"

# 2. smoke (10K × 32d, 11 method 모두)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 method_phase4_extra.py"

# 예상 출력:
# === Smoke test (10000 × 32) ===
#   ✓ chao_weighted             elapsed=  0.01s unique_sids= 20/20
#   ✓ lpm1_proper               elapsed=  7.38s unique_sids= 20/20
#   ✓ cum_sqrtf                 elapsed=  0.00s unique_sids= 20/20
#   ... (11/11 PASS — 로컬에서 이미 검증)

# 3. measure_paper_exact.py registry 검증 (1-cell smoke)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  python3 measure_paper_exact.py --rq 3 --phase B --cell A1-DEEP \
    --mode CaseA --method idistance --n_queries 10 --trials 2"
# ETA ~ 5 min (smoke)
```

---

## 6. Measurement launch (smoke PASS 후)

### 6.1 11 method × 9 cells × 2 modes = 198 cells

ETA:
- Sequential 단일 procs: ~120-180 h (~5-7일)
- Parallel 4 tmux × 50 cells: ~30-45 h (~1.5-2일)

### 6.2 Launch script 사용법

```bash
# 옵션 A: 모두 sequential (단일 tmux)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  tmux new-session -d -s pb_phase4 './run_phase_b_phase4.sh --all'"

# 옵션 B: 4 tmux 병렬 (P0 6 method × 9 cells × 2 modes = 108 cells / P1 5 method × 9 × 2 = 90 cells)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  tmux new-session -d -s pb_p4_m1m5 './run_phase_b_phase4.sh --method chao_weighted'"
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  tmux new-session -d -s pb_p4_m6m7 './run_phase_b_phase4.sh --method idistance'"
# (M2/M3/M4/M8/M10/M11/zorder_morton/skilling_hilbert/kmeans_neyman 분리 launch)
```

### 6.3 사용자 명시 — 순서 무관, 모두 진행

병렬 4-6 tmux 권고. monitor 30-60 s 간격.

---

## 7. Q4 Tier 1 6 method 통합 (handoff_v3 §6 Q4)

### 7.1 통합 method (이미 measure_paper_exact.py 분기 존재 line 471-483)

| method_name | reference | paradigm |
|---|---|---|
| `dbscan` | Ester KDD 1996 | P1 (HDBSCAN 비교) |
| `kde_parzen` | Parzen 1962 | **P10 새** (narrative anchor) |
| `mhist2` | Poosala VLDB 1997 | P10 (factor_join 대체) |
| `hyperloglog` | Flajolet AofA 2007 | **P9 새** |
| `rsvd` | Halko SIAM 2011 | P4 (PCA1D 강화) |
| `wavelet_hist` | Matias SIGMOD 1998 | P10 |

### 7.2 통합 launch (Phase 4 + Q4 = 17 method × 9 × 2 = 306 cells)

```bash
# Q4 Tier 1 launcher (server 측 method_tier1_p9_p10.py 가 이미 있는지 확인)
ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/method_tier1_p9_p10.py 2>&1"

# 있으면 통합 launch
# 없으면 method_tier1_p9_p10.py 별도 작성 + scp 후 launch
```

**권고**: Phase 4 11 method 우선 launch (smoke + 1-cell verify) 후, Q4 Tier 1 6 method 별도 launch.

ETA 통합:
- 17 × 9 × 2 = 306 cells
- Sequential: ~180-280 h
- Parallel 6 tmux: ~30-50 h

---

## 8. 산출물 위치 (메인 세션 read 권고)

### 8.1 Phase 4 분석 보고서 (5 file)

```
_internal/method_verification_20260510_phase4/
├── _BRAINSTORM_FULL.md     (~1,200 line, 16 카테고리, 553 method 발굴)
├── _FILTER_BRAINSTORM.md   (14 필터 + 7 critical selection)
├── _FILTER_ANALYSIS.md     (cascade 7 stage 단계별 drop 사유 verbatim)
├── _FINAL_LIST.md          (11 method 상세 spec — 사용자 read 권고)
└── _BRAINSTORM_REPORT.md   (메인 보고용 ~1,000 단어)
```

### 8.2 코드 (3 file)

```
_internal/scripts/
├── method_phase4_extra.py        (660 line, 11 assign functions, smoke 11/11 PASS)
├── PATCH_phase4_registry.md      (measure_paper_exact.py 패치 instruction §1-§5)
└── run_phase_b_phase4.sh         (launch script, dry-run PASS, --all/--method/--cell/--dry-run)
```

---

## 9. 5/27 발표 + 6/11 보고서 narrative 강화

| storyline 단계 | Phase 4 method 강화 |
|---|---|
| 1 RQ1 random sampling skew 무너짐 | M1 chao_weighted (random과 다른 weight bias) |
| **2 분포 알면 Neyman 답** | **M9 kmeans_neyman / M3 cum_sqrtf / M4 lavallee / M11 idistance_neyman** |
| 3 분포 모르니까 추정 활용 | M2 lpm1_proper / M5 idistance / M6 zorder_morton |
| 4 단일 -8% 격차 입증 | (paper exact 측정 진행 중 — 메인 chain) |
| 5 multi-table 0/66 | (multi 측정 진행 중) |
| **6 신규 method 발굴** | **모든 11 method P0/P1** |
| **7 Adaptive vs Adaptive+ensemble climax** | **M9/M11 RQ2 plug-in 직접 강화** |

### 9.1 핵심 학술 contribution (5/27 paper 작성 시)

1. **★3 hilbert defect rectify** = M6 zorder_morton (paradigm anchor) + M7 skilling_hilbert (true high-D Hilbert)
   - "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 효과 분리 검증" = paper 학술 finding
2. **RQ2 + RQ3 결합 4건** (M9/M11 + M3/M4) = "분포 정보 추정 방식 × Neyman σ allocation" 2D ablation
3. **2024-25 SIGMOD/VLDB 인용**: M10 RaBitQ (Gao-Lin VLDB 2024) + Q4 PRICE (Zeng 2024) + LpBound rename (lp_bound → l2_quantile, SIGMOD 2025 Best Paper LpBound 충돌 회피)

---

## 10. 진행 상태 (5/11 01:05 KST)

### 10.1 메인 chain bvf1k64kw 진행 (handoff_v4 §1-§7)
- 측정: ~316/702 (45%) ETA 5/11 02-03시 KST
- sigma builder (5/10 22:06 kill 후 자동 chain monitor 재구성)
- 자동 chain: 측정+sigma 완료 시 분석 + RQ2 launch + 분석 2차 (4단계)

### 10.2 Phase 4 별도 세션 (본 handoff)
- ✅ Phase 1-3 완료 (35분, 00:30 → 01:05 KST)
- ⏳ Server scp + measurement launch — 메인 confirm 후 진행

---

## 11. 새 세션 시작 복붙 프롬프트 (메인 세션 / 새 세션 모두 사용 가능)

```
@_internal/handoff_v5_phase4_brainstorm_20260511_0110.md 부터 정확히 read.
+ @_internal/method_verification_20260510_phase4/_FINAL_LIST.md
+ @_internal/method_verification_20260510_phase4/_BRAINSTORM_REPORT.md (~1,000 단어)
+ @_internal/scripts/PATCH_phase4_registry.md (server scp + 패치 instruction)
+ @_internal/handoff_v4_session_20260510_2144.md (메인 chain 자동 monitor)
+ @_internal/handoff_main_session_FULL_STATE_20260510_2045.md (16 sections, paper exact context)

🚨 사용자 명시 (5/11 01:05 verbatim):
- "ㅇㅋ. 모두 다 진행할거라서. 순서대로 해도 무관."
- "server scp는 메인 세션에서 진행."
- "Q4 Tier 1 통합도 최종 handoff에서. 메인이 대기 중이라서."

→ Phase 4 11 method (cascade 통과) + Q4 Tier 1 6 method = 17 method × 9 cells × 2 modes = 306 cells
→ ETA: parallel 6 tmux ~30-50 h (1.5-2일)

새 세션 즉시 액션 5단계:
1. SSH 검증: ssh capstone "date && pgrep -af measure_paper | wc -l"
2. Phase 4 file 3건 scp (handoff §4):
   scp _internal/scripts/method_phase4_extra.py capstone:/mnt/hdd0/home/capstone2026/cache/rq3/
   scp _internal/scripts/measure_paper_exact.py capstone:... (PATCH 적용본, handoff §3)
   scp _internal/scripts/run_phase_b_phase4.sh capstone:... (chmod +x)
3. Server smoke (handoff §5):
   ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 method_phase4_extra.py"
   → 11/11 PASS 확인 (로컬에서 이미 PASS)
4. 1-cell verify:
   ssh capstone "python3 measure_paper_exact.py --rq 3 --phase B --cell A1-DEEP --mode CaseA --method idistance --n_queries 10 --trials 2"
5. Full launch — 사용자 명시 "모두 다, 순서 무관":
   ssh capstone "tmux new-session -d -s pb_phase4 'cd /mnt/hdd0/home/capstone2026/cache/rq3 && ./run_phase_b_phase4.sh --all'"
   또는 6 tmux 병렬 분할 (handoff §6.2)

11 method (cascade 통과 — handoff §2):
M1 chao_weighted / M2 lpm1_proper / M3 cum_sqrtf / M4 lavallee_hidiroglou /
M5 idistance / M6 zorder_morton / M7 skilling_hilbert (★3 rectify) /
M8 ica_fastica / M9 kmeans_neyman (RQ2 plug-in) / M10 rabitq_strat / M11 idistance_neyman

Q4 Tier 1 6 method (handoff §7, 통합 launch):
dbscan / kde_parzen (P10 새 anchor) / mhist2 / hyperloglog (P9 새) / rsvd / wavelet_hist
→ 통합 launch 시 method_tier1_p9_p10.py server 측 존재 확인 필요

5/27 발표 narrative 강화:
- ★3 hilbert defect rectify = M6 + M7 (paradigm anchor + true high-D Hilbert)
- RQ2 + RQ3 결합 4건 = M9/M11/M3/M4
- 2024-25 SIGMOD/VLDB 인용: M10 RaBitQ + Q4 PRICE + LpBound rename

monitor 권고:
- 30-60 s 간격 ssh polling (handoff_main §10.2 stuck 정의: mtime 5분+ + CPU<50%)
- 메인 chain bvf1k64kw 와 충돌 0 (Phase 4 별도 측정 — server resource 공유)
- 1시간 timeout 시 monitor re-arm

산출물 위치 (handoff §8):
- _internal/method_verification_20260510_phase4/ (5 file)
- _internal/scripts/method_phase4_extra.py + PATCH + run_phase_b_phase4.sh

확인 필요 0건 — 사용자 4건 confirm 완료 (5/11 01:05).
즉시 진행 가능.
```

---

## 12. END

작성: 2026-05-11 01:10 KST (Phase 4 별도 세션, 35분 작업 완료)
사용자 confirm: 4건 모두 OK (Phase 4 scope / 순서 무관 / scp 메인 / Q4 통합)
다음 step: 메인 세션이 본 handoff 통독 → §0 5단계 즉시 액션 → 11 + 6 = 17 method launch

**핵심 결과**:
- Phase 1: ~553 method 발굴 (신규 ~470, 게이트 ≥200 통과)
- Phase 2: cascade 7 stage → 11 method 통과
- Phase 3: smoke 11/11 PASS, server scp 준비 완료
- 메인 chain bvf1k64kw 영향 0 확인
- 시간 budget: 3-6 h 중 ~35 분 사용

**메인 세션 인계**: 본 handoff + §11 복붙 프롬프트로 0% loss 인계.
