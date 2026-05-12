# Handoff v8 — 세션 총정리 + 디렉토리 archive 임무 (5/11 17:34 KST)

> **새 메인 세션 mission**: 본 file 1건 read로 0% loss 인계 + 문서 총정리 + 디렉토리 archive 한글 명 정리 + 실험 완벽 점검.
> **권한**: Opus 4.7 1M Max Token Max Context. 다중 agent 호출. file mv/archive (사용자 confirm 후). code 수정.

---

## 0. TL;DR — 새 세션 첫 30초

```bash
# 본 file 1건 read 후:
1. SSH 검증: ssh capstone2026@165.132.140.240 "date && pgrep -af measure_paper_exact | wc -l"
2. REPORT v7 검토: cat /tmp/REPORT_v7.md | head -50 (또는 scp 최신)
3. figures 6건 verify: ls /Users/hyunbin/Capstone/experiments/figures/paper_exact_v7/
4. 총정리 plan 실행 (§4-7 단계별)
```

---

## 1. 현재 상태 (5/11 17:34 KST)

### 1.1 측정 완료 (paper review-grade ✓)
| 항목 | 값 |
|---|:-:|
| B1 baseline | 9/9 cells |
| CaseA measurements | 439 |
| CaseB measurements | 449 |
| Phase 4 11 method × 18 cells | **198/198 ✅** |
| RQ1 csv (DEEP/SIFT/SSN sf=100 + DEEP sf=1/10) | 5 |
| RQ2 csv (DEEP/SIFT × 5-way Bern/Equal/Prop/Neyman/Anti) | 2 |
| 총 JSON file | **898** |
| 미커버 (drop) | 233 cells (79.5% coverage) |

### 1.2 11 axis cross-verification 평균 7.6/10 (측정 자체 9.2-10/10 ✓)

| Axis | 영역 | 완벽도 | 핵심 |
|---|---|:-:|---|
| #1 B1+Fig 12 | **9.5** | Fig 12 영역 8 cells mean **1.6180 / paper 1.69 -4.26%** ✓ |
| #2 RQ2 | 6.0 | 🚨 Anti < Prop < Neyman paradox (σ_j range 좁음) |
| #3 RQ3 | 5.0 | 🚨 CaseA 0/437 통계 무효 + cells inflation 10→6 unique |
| #4 REPORT 환각 | 6.0 | "60%+" → 실제 92.9% under-selling 발견 |
| #5 storyline | 6.5 | CaseA 제거 권고 + Neyman 신화 부정 |
| **A JSON integrity** | **10** | 898 file 0 critical |
| **B Reproducibility** | **10** | 280/280 byte-identical |
| C Statistical | 6.4 | Cliff's δ + Hedges' g 미반영 (정정 완료) |
| **D Paper verbatim** | **9.2** | Eq 1-6 + hyperparam + queries + threshold 100% |
| E σ_j oracle | 7.5 | Neyman paradox root cause 명확 |
| F Method impl | 7.0 | M7/M9 simplification + ★3/★4 코드 정직 |
| G Drop root cause | 8.0 | 233 cells 9 카테고리 정직 분류 |
| H Method portfolio | 9.0 | 추가 method **0건** 권고 |
| I Coverage extension | 7.5 | A4-sel sel=0.001 fallback 발견 |
| J REPORT plan | 7.5→9.5 | analyze 확장 + figures 완료 |
| K Impl depth | 7.5 | ★3/★4 코드 차원 이미 정직 |

### 1.3 핵심 narrative findings

**🔥 강력 anchor (5/27 climax)**:
- **CaseB Cliff's δ large better 63.5% (284/447)** ⭐
- **CaseB Hedges' g large 56.4% (252/447)** ⭐
- **CaseB가 92.9% 케이스에서 CaseA보다 나음** (paper review-grade)
- **Paradigm rollup**: P10 Density -11.93% / P9 InfoTheoretic -10.22% / P3 Streaming -6.53% / P4 -5.92% / P2 -5.36% / **P1 +0.17% / P5 +1.47% / P6 +1.49%**
- Top 3 CaseB winners: pq @ A5-sf1 (g=-7.15) / sparse_rp @ A5-sf1 (g=-7.14) / vinecopula @ A5-sf1 (g=-7.05)

**🚨 narrative 정정 (정확 입증)**:
- CaseA 단독 대체: **0/437 통계 무효** + Cliff's δ worsening 36.8% > better 14.4% (**무너짐**)
- RQ2 Neyman paradox: **Anti 1.540 < Prop 1.580 < Neyman 1.595** (paper §V-B 이론 위배, σ_j 1.3-1.6× narrow root cause)
- "92.9%" sign test 분모 추적: trial-level 71.8% / one-sided BH 45.0% / Δ<0 79.6% / valid-method 88.2%
- Cells inflation 10 명목 vs **6 unique** (A1-DEEP ≡ A5-sf100, A2-Fig9 ≡ A5-sf10 byte-identical)

### 1.4 일정 (확정)
| 일시 | 일정 |
|---|---|
| 5/15 (금) 14:00 | 박광현 교수님 미팅 (박세은 5/11 14:59 카톡 시간 확정) |
| 5/27 (수) | 최종발표 (D-16) |
| 6/11 (목) | 최종보고서 (D-31) |

---

## 2. 최종 산출물 (이번 세션 결과물)

### 2.1 code
- `/Users/hyunbin/Capstone/_internal/scripts/analyze_paper_exact.py` — 확장됨 (PARADIGM_MAP + 5 신규 함수 + §7-11 inject + RQ2 caveat + byte-identical caveat)
- `/Users/hyunbin/Capstone/_internal/scripts/figures_paper_exact.py` — 신규 (314 line, 6 figure 자동 생성)

### 2.2 REPORT v7 (server)
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` — 1259 line, 11 section
- local mirror: `/tmp/REPORT_v7.md`

### 2.3 storyline draft v2
- `/Users/hyunbin/Capstone/plans/5_27_storyline_draft_20260511_1410.md` — 4건 정정 (§2 Neyman→prop / §3.2 통계 / §4 5단계 / §5 7단계)

### 2.4 figures (6건)
`/Users/hyunbin/Capstone/experiments/figures/paper_exact_v7/`:
- F1_paradigm_rollup_caseB.png
- F2_cliffs_delta_bucket.png
- F3_caseA_vs_caseB_violin.png
- F4_top_winners_caseB.png
- F5_effect_size_scatter.png
- F6_narrative_diagram.png

⚠️ Korean font 경고 (DejaVu Sans missing Korean glyph) — Apple SD Gothic Neo 적용 필요 (5/27 closer)

### 2.5 일정 정정 file 5건
- memory `project_schedule.md` (5/15 14:00 박광현 미팅)
- `_internal/state/_schedule.md`
- `_internal/MASTER_README.md` §11
- `_internal/state/_next.md` (outdated 헤더 추가)
- `_internal/CHANGELOG.md` (향후 일정)

---

## 3. 새 세션 mission — 문서 총정리 + 디렉토리 archive

### 3.1 핵심 목표

> Capstone 루트부터 각 디렉토리 돌면서 **최신 문서만 두고 나머지 archive**.
> archive 디렉토리는 **한글 폴더명** (기능/내용 기반, "academic_deck_v3_source" X → "발표자료 v3 source" ✓).
> 통합 가능 문서는 한 file로 통합.
> 지침 file (CLAUDE.md, README.md 등)에도 반영.

### 3.2 디렉토리별 정리 우선순위 (8 영역)

#### A. `/Users/hyunbin/Capstone/_internal/` (최대 우선)

**현재 file 분포**:
- handoff/active/ : 5-6 file (v2, v4, v5, v6, v8 신규, main_session_FULL_STATE, back_validation)
- handoff/archive/ : 5 file (v0, v0.bak, v1, v3, validation_statistics)
- MASTER_README.md / MASTER_HANDOFF.md / METHOD_REGISTRY.md / EXPERIMENT_REGISTRY.md / SERVER_REGISTRY.md / CHANGELOG.md / naming_convention.md (7건)
- _BEFORE_INVENTORY.md / _CLEANUP_LOG.md (2건, 5/11 정리 흔적)
- state/ : _schedule.md / _current.md / _next.md / _artifacts.md / _roadmap.md / _consolidation_*.md / _kakaotalk_*.md / _method_portfolio_v9_*.md / _data_scope_*.md / archive/
- method_audit/20260510_initial/ + 20260511_phase4/
- scripts/ + scripts/archive/
- slide_redesign_v2_20260508.md / claude_design_prompt_storyline_20260508.md / RQ3_paradigm_심층검증_20260508.md (3건, 5/8 시점 outdated — Achlioptas 정정 X)
- 기타 다수

**정리 plan**:
1. handoff v0-v6는 archive/로 (v8만 active에 유지)
2. state/ 안 5/8-5/9 시점 file은 archive/로 (현재는 _schedule.md만 active)
3. 5/8 시점 outdated docs 3건은 archive/ (Achlioptas 2003 정정 미반영, slide_redesign_v2 등)
4. method_audit 2 dir (5/10 initial + 5/11 phase4)은 통합 또는 그대로 유지
5. archive 한글 폴더명:
   - `archive/` → 분리 X (이미 archive)
   - 새 한글 명: 예) `_internal/문서_archive/이전_handoff/` / `_internal/문서_archive/audit_보고서/` 등

#### B. `/Users/hyunbin/Capstone/plans/`

**현재**:
- `5_27_storyline_draft_20260511_1410.md` ✅ 최신 (v2 정정 완료)
- `RQ재정립_20260505_2122.md` (5/5 시점)
- `RQ재정립_v7_evidence_20260509_1820.md` (5/9 시점)
- `5_8_19시_회의_outline.md` (5/8 시점)
- `최종보고서_outline_v2_20260508.md` (5/8 시점)
- `archive/`, `_drafts/`

**정리 plan**:
1. 최신 active: storyline_draft_v2 (5/11) + 최종보고서_outline_v2 (5/8 base) 유지
2. RQ재정립 5/5/5/9 → archive/ (한글: `plans/이전_RQ_재정립/`)
3. 5_8_19시_회의_outline → archive/ (한글: `plans/회의_outline/`)
4. archive/ 안 한글 명 재구성

#### C. `/Users/hyunbin/Capstone/submission/`

사용자 명시 **submission/_drafts/는 최신 파일만**, 나머지는 archive (각 file 기능/내용에 따른 한글 폴더명).

**현재 (_drafts/) 추정 file**:
- 연구제안서, 수행계획서, 중간보고서, 자문메일 v3/v4/v5, 발표 slide 등 다수

**정리 plan**:
1. 각 file 종류 별 분류:
   - 연구제안서/수행계획서 (4/2 마감 완료)
   - 중간보고서/발표 (4/28~4/30 완료)
   - 자문메일 v3/v4/v5 (박성원 멘토)
   - 발표 slide source / pdf
   - 연구지도확인서 (5/5)
2. 최신 버전만 _drafts/에 유지
3. archive 한글 폴더 명:
   - `submission/_drafts/archive/연구제안서_초안/`
   - `submission/_drafts/archive/중간보고서_초안/`
   - `submission/_drafts/archive/자문메일_v3_v4/` (v5만 active)
   - `submission/_drafts/archive/발표자료_v1_v2_source/` (v3 source만 active)
   - `submission/_drafts/archive/연구지도확인서_v1/`
4. 제출완료/ 폴더는 그대로 (외부 발송)

#### D. `/Users/hyunbin/Capstone/experiments/`

**현재**:
- code/rq1/ + code/rq2/ + code/rq3/ + code/local_analysis/
- results/rq1_motivation/ + rq2_aware/
- figures/ (figures/paper_exact_v7/ 신규 6건)
- config/

**정리 plan**:
1. figures/ 안 paper_exact_v7/ (5/11 신규) + 이전 figure dir → archive 또는 통합
2. results/ 안 5/8 이전 시점 data → archive
3. code/ 안 사용 안 하는 script → archive

#### E. `/Users/hyunbin/Capstone/reference/`

**현재**:
- papers/ (69편)
- summaries/ (82편)
- analysis/
- exqutor_query_plans/ (Exqutor github clone)

**정리 plan**: 큰 변경 X. 단 사용 안 하는 paper / summary 분류 가능.

#### F. `/Users/hyunbin/Capstone/templates/`

캡스톤 학교 양식. 변경 X.

#### G. `/Users/hyunbin/Capstone/records/`

`_internal/records/`로 이미 이동? 확인 필요. 한 곳만 유지.

#### H. 루트 file
- `README.md` (팀원 진입점)
- `CLAUDE.md` (Claude Code 컨텍스트, 라우팅)

**정리 plan**:
1. CLAUDE.md update — 새 세션 인계 + 본 file 1건 read 명시
2. README.md update — 5/15 박광현 미팅 + 5/27 발표 진행 상태

### 3.3 archive 한글 폴더명 mapping (사용자 명시 "기능/내용에 따라")

| 영문/암호 명 (X) | 한글 명 (✓) |
|---|---|
| `academic_deck_v3_source` | `발표자료 v3 source (5/27 base)` |
| `claude_design_prompt_storyline_20260508` | `5/8 storyline 설계 프롬프트` |
| `RQ3_paradigm_심층검증_20260508` | `5/8 RQ3 paradigm 심층검증` |
| `slide_redesign_v2_20260508` | `5/8 slide redesign v2` |
| `_consolidation_20260510_1215` | `5/10 state 통합` |
| `_kakaotalk_narrative_method_table_20260510_0030` | `5/10 카톡 narrative method 표` |
| `_method_portfolio_v9_extreme_20260509_2335` | `5/9 method portfolio v9` |
| `_data_scope_decision_20260510_0114` | `5/10 data scope 결정` |
| 등 | (각 file 내용 read 후 한글 명 결정) |

### 3.4 실험 완벽 점검 + 서버 추가 실험 필요성

새 세션은 11 axis 결과 base로 추가 실험 필요성 검증:

| 추가 실험 후보 | 가치 | 비용 | 권고 |
|---|---|---|---|
| **A4-sel sel=0.001 정정** (Axis D/I 발견) | HIGH — paper Fig 13 sweep 재현 신뢰성 | ~6h server | 정정 권고 (또는 REPORT caveat) |
| **★3 hilbert_real 12 cells 추가** (Axis K) | MED — paradigm anchor 보강 | ~30분 server | 권고 |
| **★4 sparse_rp reference 정정** (Axis K) | HIGH — 학회 reviewer risk 제거 | 5분 | 즉시 진행 |
| Phase 4 n_queries=1000 통일 (Axis I) | MED — narrative 일관성 | ~5-8h | 후순위 |
| SSN RQ2 5-way 추가 | LOW — σ range narrow, 결과 차별성 미미 | ~3h | 폐기 |
| A2-Fig8 multi-vector | LOW — paper §V-A scope | ~3-5h | 폐기 |
| A3-TPCDS ECQO fix | LOW — paper §V-A scope, PG segfault | ~1d | 폐기 |

### 3.5 narrative final 정합성 검증

새 세션이 추가 cross-verify 항목:
1. REPORT v7 vs storyline draft v2 vs figures 6건 narrative 일치?
2. CLAUDE.md / MASTER_README.md / handoff_v8 narrative 일치?
3. 5/15 박광현 미팅 narrative + 5/27 발표 narrative 차이 (timeline 진행 단계)?
4. limitation honest disclosure 충분 (drop list 233 / ★3/★4 정정 / Neyman paradox)?

### 3.6 출력 (새 세션 final)

#### A. 정리된 디렉토리 구조 표
- 각 디렉토리 active file list + archive 분류
- archive 한글 폴더명 mapping

#### B. 통합된 문서 list
- 통합된 file 명 + 출처 file
- 통합 전후 line count

#### C. CLAUDE.md + README.md update content
- 5/15 박광현 미팅 + 5/27 발표 진행 상태
- 새 인계 안내

#### D. 추가 실험 결정
- A4-sel sel=0.001 정정 / ★3 hilbert_real / ★4 reference 정정 진행 여부 + 결과

#### E. 5/15 박광현 미팅 slide draft (선택)
- storyline draft v2 base 1-2 slide 한국어 학술 산문

---

## 4. 새 세션 진행 단계 (권고)

### Phase 1 (30분) — 인계 + 검증
1. handoff_v8 1 file read 완료
2. SSH 검증 + figures 6건 확인
3. REPORT v7 검토 (1259 line 11 section)
4. storyline draft v2 검토

### Phase 2 (1-2h) — 디렉토리 8 영역 정리
1. `_internal/` 정리 (handoff archive + state archive + outdated 5/8 docs)
2. `plans/` 정리 (RQ재정립 archive + storyline v2 유지)
3. `submission/_drafts/` 정리 (최신 + archive 한글 명)
4. `experiments/` 정리 (figures + results archive)
5. CLAUDE.md + README.md update

### Phase 3 (30분-1h) — 추가 실험 결정 + 실행
1. ★4 sparse_rp reference 정정 (5분)
2. ★3 hilbert_real 12 cells launch (30분)
3. A4-sel sel=0.001 정정 (사용자 confirm 후)

### Phase 4 (30분) — final cross-verification + 보고
1. REPORT v8 재생성 (★3 데이터 통합)
2. figures v8 재생성 (필요 시)
3. 5/15 박광현 미팅 slide draft
4. 사용자 final 보고

---

## 5. 권한 / 룰 (handoff_v6 §0.5 절대 룰 유지)

### 5.1 server 절대 룰
- ❌ PG port 55432, 55433 (다른 사용자) 절대 X
- ✅ 우리 port 55435 (active) / 55436 (Exqutor patched, idle)
- ❌ 다른 사용자 procs kill X
- ✅ 우리 작업 dir `/mnt/hdd0/home/capstone2026/`만

### 5.2 file 룰
- 파괴적 작업 (rm/mv) **사용자 confirm 후**
- archive는 mv (delete X)
- 한글 폴더명 use (사용자 명시)
- 일관 naming convention (handoff_v6 §2 + `_internal/naming_convention.md`)

### 5.3 narrative 정합성
- paper §V-B 영역 한정 (사용자 명시 "Exqutor 외 X")
- ECQO (§V-A) drop 정당화
- limitation 정직 명시 (drop 233 cells + ★3/★4 + Neyman paradox)
- 5/27 storyline 7단계 정정 후 narrative 일치

---

## 6. 핵심 file paths (새 세션 1 file read만으로 모두 접근)

### 6.1 신규 (이번 세션 작성)
- `_internal/handoff/active/handoff_v8_session_total_cleanup_20260511_1734.md` ← **본 file**
- `_internal/scripts/analyze_paper_exact.py` (확장)
- `_internal/scripts/figures_paper_exact.py` (신규)
- `experiments/figures/paper_exact_v7/F1~F6.png` (6 figure)
- `plans/5_27_storyline_draft_20260511_1410.md` (v2 정정)

### 6.2 server
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` (v7 1259 line)
- `/mnt/hdd0/home/capstone2026/cache/rq3/analyze_paper_exact.py` (확장)
- `/mnt/hdd0/home/capstone2026/cache/rq3/figures_paper_exact.py` (신규)

### 6.3 memory
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` (index)
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_schedule.md` (5/15 14:00)
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/feedback_method_audit_findings.md`

### 6.4 archive 후보 (5/8 시점 outdated)
- `_internal/slide_redesign_v2_20260508.md` (Achlioptas 2003 정정 X)
- `_internal/claude_design_prompt_storyline_20260508.md`
- `_internal/RQ3_paradigm_심층검증_20260508.md`
- `_internal/state/_consolidation_20260510_1215.md`
- `_internal/state/_kakaotalk_narrative_method_table_20260510_0030.md`
- `_internal/state/_method_portfolio_v9_extreme_20260509_2335.md`
- `_internal/state/_data_scope_decision_20260510_0114.md`
- `plans/RQ재정립_20260505_2122.md`
- `plans/RQ재정립_v7_evidence_20260509_1820.md`
- `plans/5_8_19시_회의_outline.md`

---

## 7. END

작성: 2026-05-11 17:34 KST  
다음 단계: 새 메인 세션이 본 file 1건 read → 8 디렉토리 총정리 + 5/15 박광현 미팅 준비

**핵심**: 본 file은 0% loss 인계 anchor. 이번 세션 측정 + 11 axis 검증 + REPORT v7 + storyline v2 + figures 6건 + narrative findings + 일정 + 다음 미션 모두 포함. 새 세션이 즉시 작업 진행 가능.
