# MASTER_README.md — 단일 진입점

> ⚠️ **이력 문서 (2026-05-19 archive)** — 2026-05-11 시점 스냅샷. 측정은 v13으로 완료됐고(3-way 1508), 프로젝트 진입점 역할은 루트 `CLAUDE.md` + `_internal/handoff/active/` 최신 handoff가 대체했다. 현 수치 정본 = `_internal/cache/rq3/v13_summary.md`. 이하 본문은 계획 시점 이력으로만 참조.
>
> 작성: 2026-05-11 02:00 KST  
> **새 세션 / 인수자가 본 file 1건만 read 해도 0% loss 인계 보장**.  
> 사용자 명시 (5/11 01:15): "여러 세션 작업물 뒤엉킴 → 한 세션에서 ultraplan 통해 모두 정리. 완벽하게 정리하는 한 세션."

---

## 0. 즉시 액션 (새 세션 5분)

```bash
# 1. SSH 검증 (ed25519 등록됨, password 불필요)
ssh capstone2026@165.132.140.240 "date && pgrep -af measure_paper | wc -l"

# 2. 측정 진행
ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"

# 3. tmux + sigma + RQ2 진행
ssh capstone "tmux ls; tail -10 /mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_*.log"

# 4. 자동 chain monitor (task bdrhrddyb) — 측정+sigma 완료 시 분석+RQ2 launch+분석 자동
# 5. Phase 4 server scp + measurement launch (handoff_v5 § 0, 사용자 4 confirm 완료)
```

---

## 1. 본 _internal/ 디렉토리 구조

```
_internal/
├── MASTER_README.md           ★ 이 file (단일 진입점)
├── MASTER_HANDOFF.md          ★ handoff 통합 v0~v5 + validation + Phase 4
├── METHOD_REGISTRY.md         ★ 57 method × 10 paradigm
├── EXPERIMENT_REGISTRY.md     ★ 9 cells × 57 methods × 3 modes matrix
├── SERVER_REGISTRY.md         ★ port/cache/log/PG/tmux inventory
├── CHANGELOG.md               ★ 5/10~5/11 timeline
├── _BEFORE_INVENTORY.md       baseline (정리 전)
├── _CLEANUP_LOG.md            정리 mv log
├── naming_convention.md       file naming 규칙
├── README.md                  (기존, 활성)
│
├── handoff/
│   ├── active/    (v2/v4/v5 + main_session_FULL_STATE + back_validation, 5건)
│   └── archive/   (v0/v0.bak/v1/v3 + validation_statistics, 5건)
│
├── method_audit/
│   ├── 20260510_initial/   (P1-P6 8 agent audit, 11 file, 5,777 lines)
│   └── 20260511_phase4/    (Phase 4 11 method, 5 file)
│
├── scripts/
│   ├── (active 32건)
│   │   ├── measure_paper_exact.py   ★ 메인 측정 (1100+ lines)
│   │   ├── _measure_common.py       ★ 공통 inf
│   │   ├── analyze_paper_exact.py   ★ Phase D 분석
│   │   ├── compute_stratum_sigma_paper_exact.py
│   │   ├── method_phase4_extra.py   ★ Phase 4 11 method
│   │   ├── method_tier1_p9_p10.py   (Q4 Tier 1 6 method)
│   │   ├── method_hilbert_real.py
│   │   ├── PATCH_phase4_registry.md
│   │   ├── PATCH_hilbert_real_registry.md
│   │   ├── measure_multi_vec_patch.md
│   │   ├── run_phase_b_phase4.sh
│   │   ├── run_phase_b_q1q4.sh
│   │   ├── run_phase_a2fig8_tier1.sh
│   │   ├── md2pdf.py / md2docx.py / _build_docx_v1.py
│   │   ├── methods/  (extra2 20 method 별 module)
│   │   └── midterm_pptx/
│   └── archive/   (43건 — 이전 측정 끝난 script)
│
├── validation/    (4-layer audit + data/319, 그대로)
├── state/         (12 file, dynamic state)
├── archive/       (4 sub-dir — history 보존)
├── cache/         (analysis 결과 cache)
├── guideline/     (5 active set + archive)
├── learning/      (kr/us + 클로드코드활용지침)
├── records/       (kakaotalk/51 + weekly/3)
└── server_wrappers_backup_20260507/
```

---

## 2. 핵심 file 5건 (이 순서로 read)

| # | File | line | 내용 |
|---|---|---|---|
| 1 | **MASTER_HANDOFF.md** | ~500 | handoff v0~v5 + validation + Phase 4 통합 / 5단계 narrative / 측정 진행 / 자동 chain |
| 2 | **METHOD_REGISTRY.md** | ~300 | 57 method × 10 paradigm 분류 / 폐기/rename / Phase 4 11 method 상세 |
| 3 | **EXPERIMENT_REGISTRY.md** | ~250 | 9 cells × 57 methods × 3 modes matrix / RQ1/RQ2 paper exact |
| 4 | **SERVER_REGISTRY.md** | ~250 | server SSH / 작업 dir / NPY cache / log / tmux / 자원 룰 |
| 5 | **CHANGELOG.md** | ~200 | 5/10~5/11 timeline 시계열 |

추가 (필요 시):
- **handoff/active/handoff_v5_phase4_brainstorm_20260511_0110.md** (latest, Phase 4 launch instruction)
- **method_audit/20260511_phase4/_FINAL_LIST.md** (11 method 상세 spec)

---

## 3. 사용자 + 팀 + 프로젝트

- **사용자**: 조현빈 (Capstone 팀 가장 형, peer-to-peer 톤)
- **팀명**: 속도는벡터 (연세대 컴공)
- **팀원**: 박세은 (팀장), 강재현, 조현빈, 이동욱
- **지도**: 박광현 교수 (BDAI) / 임채림 석사 (서버 admin) / 박성원 멘토 (삼성 AI센터)
- **본 논문**: Exqutor (arXiv:2512.09695v2, BDAI 박광현 교수 본 논문)

---

## 4. 5단계 narrative (사용자 명시) — 정리 작업 직전 상태

| # | 단계 | 검증 (5/11 01:10 KST) |
|---|---|---|
| 1 | RQ1, RQ2, RQ3 검증 | ✅ RQ1 5%, RQ2 9% 격차 |
| 2 | Exqutor 100% 정확 재현 | ✅ Fig 12 영역 8 cells mean qe_trim **1.618** (paper 1.69 vs **−4.3%**) |
| 3 | CaseA: 우리 method **대체** | ⚠️ minibatch_partial **-10.17%** method-mean (단독 narrative 약함) |
| 4 | CaseB: 우리 method **증강** | ✅ 6 methods 모두 -2~-7% outperform / 44.7% 통계 유의 |
| 5 | 최종 비교 B1 vs CaseA vs CaseB | ✅ CaseB > CaseA > B1 robust (CaseB 79.6% outperform) |

---

## 5. SSN ↔ FB ↔ SimSearchNet++ alias (놓치지 말 것)

⚠️ **결정적 detail** (handoff_main §3.2):

| 코드 alias | paper | server table | dim |
|---|---|---|---|
| **SSN = FB** | SimSearchNet++ | **partsupp_fb_{1,10,100}** | 256 |

- query_pool 파일: `query_pool_SSN_sf*.parquet` (SSN 사용)
- 우리 코드: `dataset="SimSearchNet++"`, `table="partsupp_fb_{sf}"`, alias map `"SimSearchNet++": "SSN"`

---

## 6. 측정 진행 상태 (5/11 01:25 KST = handoff_v6 기준)

- ✅ Phase A B1: 9/9 cells (paper Fig 12 영역 −4.3% 일치)
- ✅ Phase B/C Tier 1 Legacy 11 method × 9 × 2 = 198 cells
- 🔄 Phase B/C extra 28 NEW method × 9 × 2 = 504 cells (**cnt=440/702 = 62%**)
- 🔄 Q4 Tier 1 6 method × 9 × 2 = 108 cells
- ✅ **Phase 4 11 method launch 완료** (11 tmux: pb_p4_chao_weighted ~ pb_p4_idistance_neyman) — handoff_v5 §0 server scp + smoke 11/11 PASS 모두 완료
- ⏳ A2-Fig8 (multi-vector) post-fix
- ⏳ A3-TPCDS (ECQO mode) post-fix

**현재 procs 31** (메인 20 + Phase 4 11), **mem available 56 GB**

**Smart coordinator v3** (handoff_v6 §2 + §8.5-§8.7) — 새 세션 인계용:
- 30s polling + auto-fix (RSS > 30GB kill / mem < 10GB emergency / stuck 30min+ kill)
- **auto-relaunch** (5분 주기) — kill된 method 재 launch → 결국 모든 method 완료 보장
- Trigger: main_act=0 + cnt>650 → main_chain_post launch (analyze 1차 + sigma + RQ2 5-way + analyze 2차) → 모두 끝 → analyze 3차 → 🎉 COMPLETE
- ⚠️ **birch × SF=100 cells** = 메모리 폭증 (50-200GB RSS) — 5/11 01:34 emergency kill 사례 (mem 8GB → 320GB 회복)

---

## 7. 5/27 발표 storyline 7단계 (handoff_v5 §9 + handoff_main §11.6)

| # | 단계 | paradigm × method anchor |
|---|---|---|
| 1 | 단일 random sampling skew 무너짐 | RANDOM20 baseline + chao_weighted M1 (P3 weight) |
| 2 | **분포 알면 Neyman 답** | **kmeans_neyman M9 (P1+RQ2) / cum_sqrtf M3 (P5) / lavallee_hidiroglou M4 (P5) / idistance_neyman M11 (P2+RQ2)** |
| 3 | 분포 모르니까 추정 활용 | sparse_rp ★4 (P4) / mb_partial ★2 (P1) / lpm1_proper M2 (P2) / idistance M5 / zorder_morton M6 |
| 4 | 단일 -8% 격차 입증 | mb_partial -10.17% method-mean (CaseA) |
| 5 | multi-table 0/66 | (이전 narrative — multi 측정 進中) |
| **6 신규 method 발굴** | **Phase 4 11 (M1-M11)** + Q4 Tier 1 6 |
| **7 Adaptive vs Adaptive+ensemble climax** | **M9/M11 RQ2 plug-in** + ★4 sparse_rp anchor |

---

## 8. 학술 contribution claim (handoff_v5 §9.1)

1. **★3 hilbert defect rectify** = M6 zorder_morton + M7 skilling_hilbert
   - "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 효과 분리 검증" = paper 학술 finding
2. **RQ2 + RQ3 결합 4건** (M9/M11 + M3/M4) = "분포 정보 추정 방식 × Neyman σ allocation" 2D ablation
3. **2024-25 SIGMOD/VLDB 인용**: M10 RaBitQ (VLDB 2024) + Q4 PRICE (VLDB 2024) + LpBound rename + PDX (SIGMOD 2025)

---

## 9. 자원 활용 룰 (사용자 + 채림님)

- **PG port 55435-55436만** (다른 인스턴스 55432/55433 절대 X)
- 작업 dir = `/mnt/hdd0/home/capstone2026/`
- GPU 사용 OK (다른 사용자 idle 시) — 채림님 자제 룰 사용자 override
- tmux 다중 OK (현재 23+ tmux + Phase 4 launch 시 32+)
- VPN keep-alive (~/.ssh/config + `/tmp/capstone_keepalive.sh` 60s ping)
- 30-60s monitor + stuck 정의 (mtime 5분+ + CPU<50%)

---

## 10. 사용자 명시 핵심 (verbatim)

| 일시 | 사용자 명시 |
|---|---|
| 5/10 14:03 | "RQ1, RQ2, RQ3 검증 → Exqutor 100% 정확 재현 → CaseA 대체 → CaseB 증강 → 최종 비교" |
| 5/10 18:49 | "하나도 빠짐없이 갈거야 완벽 논문 재현 + 우리 기존 논문의 한계를 보완하거나 극복하는 내러티브" |
| 5/10 20:45 | 목표 ① Exqutor 완벽 재현 ② RQ3 방법 동원 adaptive 대체 ③ 대체 불가 시 전처리 개선 |
| 5/11 01:05 | "ㅇㅋ. 모두 다 진행할거라서. 순서대로 해도 무관. server scp는 메인 세션에서 진행. Q4 Tier 1 통합도 최종 handoff에서. 메인이 대기 중이라서." (Phase 4 4 confirm 완료) |
| 5/11 01:15 | "여러 세션 작업물 뒤엉킴 — Tier S/A/B/Q1/Q4/Phase 4 분류 의미 X. 한 세션에서 ultraplan 통해 서버/Capstone/문서/스크립트/파일/디렉토리 모두 정리." |

---

## 11. 일정

⚠️ **2026-05-11 02:14 KST 정정** (사용자 명시): 박광현 미팅 5/22 → **5/15** / 5/13 "Adaptive×4강 Ensemble" 일정 **폐기** (사용자 명시 X) / "4강" framing **확정 X** (★1 hdbscan 측정 미포함, ★3 hilbert defect rectify)
⚠️ **2026 calendar 검증**: 5/11 월 / 5/13 수 / 5/15 금 / 5/22 금 / 5/27 수 / 6/11 목

| 일시 | 요일 | 일정 | 상태 |
|---|---|---|---|
| ~~5/13~~ | ~~(수)~~ | ~~Adaptive×4강 Ensemble~~ — **폐기 (사용자 명시 X, 4강 확정 X)** | — |
| **5/15 14:00** | **금** | **★ 박광현 교수님 미팅 (박세은 5/11 14:59 카톡 시간 확정)** | 예정 |
| **5/27** | **수** | **최종발표** (storyline 7단계 finalize) | 준비 中 (D-16) |
| **6/11** | **목** | **최종보고서** (outline v2 base + 4 팀원 분담) | 준비 中 (D-31) |

---

## 12. 정리 작업 요약 (5/11 01:25~02:00 본 세션 산출)

### 12.1 작성된 file (8건)
1. **MASTER_README.md** (이 file) — 단일 진입점
2. **MASTER_HANDOFF.md** — handoff 통합
3. **METHOD_REGISTRY.md** — 57 method paradigm
4. **EXPERIMENT_REGISTRY.md** — matrix
5. **SERVER_REGISTRY.md** — server inventory
6. **CHANGELOG.md** — timeline
7. **_BEFORE_INVENTORY.md** — baseline (정리 전)
8. **naming_convention.md** — naming 규칙

### 12.2 정리 (Phase 4 mv 후)
- handoff/{active,archive}/ 분리
- method_audit/{20260510_initial,20260511_phase4}/ 통합
- scripts/{,archive}/ 분리
- _CLEANUP_LOG.md 작성

### 12.3 메인 세션 영향 = 0
- ❌ server 측정 데이터 변경: 0건
- ❌ measure_paper_exact.py / _measure_common.py 변경: 0건
- ❌ tmux/PG/cache: 0 영향
- ❌ chain monitor `bdrhrddyb`: 0 영향
- ❌ Phase 4 11 tmux launch: 영향 0 (별도 server scp 대기)
- ✅ 로컬 _internal/ 정리만

---

## 13. 새 세션 시작 복붙 프롬프트

```
@_internal/MASTER_README.md 부터 정확히 read.
+ @_internal/MASTER_HANDOFF.md
+ @_internal/METHOD_REGISTRY.md
+ @_internal/EXPERIMENT_REGISTRY.md
+ @_internal/SERVER_REGISTRY.md
+ @_internal/CHANGELOG.md

(latest handoff — 새 세션 인계 코드 포함)
+ @_internal/handoff/active/handoff_v6_smart_coordinator_handoff_20260511_0125.md
+ @_internal/method_audit/20260511_phase4/_FINAL_LIST.md

🚨 사용자 명시 (5/11 01:05 + 01:15 + 01:24 + 01:33-36 verbatim):
- Phase 4 11 method 진행 완료 (5/11 01:25 launch 끝)
- 정리 작업 후 새 세션 인계 (메인 세션 context 한도)
- "내일 아침까지 자율 진행 — kill되어도 재 launch 결국 모든 실험 완료"
- Smart coordinator v3 = 자원 최대 활용 + auto-relaunch

새 세션 즉시 액션 5단계:
1. SSH 검증: ssh capstone "date && pgrep -af measure_paper_exact | wc -l"
2. 측정 진행: ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"
   현재 5/11 01:25 기준 cnt=440/702 (62%) — 진행 中
3. tmux 진행: ssh capstone "tmux ls | head -20" (메인 + pb_p4_* 11개)
4. Smart coordinator v3 launch (handoff_v6 §2 + §8.5-§8.7 코드 verbatim Monitor 도구로 복붙)
   - 30s polling + auto-fix + auto-relaunch
   - Trigger: main_act=0 + cnt>650 → main_chain_post → final analysis → COMPLETE
5. 자율 진행 — 내일 아침 결과 확인 (REPORT_paper_exact.md 최종 갱신)

5단계 narrative 검증 (5/11 01:25 기준):
1 ✅ 2 ✅ 3 ⚠️ 4 ✅ 5 ✅

⚠️ birch × SF=100 cells = 메모리 폭증 (50-200GB RSS) → v3 high-mem auto-kill 적용
```

---

## 14. END

작성: 2026-05-11 02:00 KST  
**핵심 검증**: 새 세션이 본 file 1건 read 만으로 모든 진행 상태 / 사용자 명시 / 측정 / paradigm method / server 자원 / 자동 chain 모두 파악 가능. 0% loss 인계.

다음 단계: Phase 4 (mv + cleanup log) → 메인 세션 보고
