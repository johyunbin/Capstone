# handoff 20260520 14:14 — 발표 deck v2 (raster image PPTX) 5축 vision 검증 완료 · fix 1·2·3 PASS · ship-ready

> 이전 handoff(`_internal/handoff/archive/handoff_20260520_133737_deck21장검증.md`) → 본 문서. 이 문서 하나만 읽으면 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 사용자가 claude.ai/design 에 수정 prompt 3 fix (fix 1 B16 4갈래 + fix 2 hero 그라데이션 + fix 3 한글 typeface) 복붙해 받아온 v2 PPTX (`속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx`, 1.20MB, 21장 raster image PPTX) 를 본 세션이 5축 vision sub-agent 5 (V-A~V-E, 모두 Opus 4.7) + 메인 cross-check 로 검증. 결과 = **critical 0 + major 0 + minor 11 + ship-ready**. **fix 1·2·3 모두 PASS** — fix 1 (B16 "비교 흐름 [기본 엔진 → 베이스라인 → 결합 → 정답]" 4갈래 도식 완벽, ψ-M1 v1 major 시정) + fix 2 (메인 hero navy→cyan 그라데이션 5/5 적용 — B1·B11·B15·B16·B21) + fix 3 (한글 21/21 깨짐 0건, raster burned-in). carry 18장 변동 0건. 정본 수치 catalog 23/23 = 100%. 다음 = 5/22 미팅·5/25 보고서 최종·5/26 PPTX·5/27 발표·5/28 포스터·6/11 보고서. **사용자 외출 중 → 맥북 동기화는 집 복귀 후, 본 세션은 커밋/푸시 까지만**.

---

## 0. 가장 먼저 — 정본·진입점

- **★ 승인된 본 세션 plan**: `~/.claude/plans/tidy-knitting-catmull.md` (raster image PPTX vision 검증 5축 + 커밋·푸시 + (deferred) 맥북 동기화). 본 세션 완료, 폐기 가능.
- **★ 라우팅·구조 정본**: 루트 `CLAUDE.md`. anchor 본 handoff 로 갱신 (line 23).
- **★ 검증 대상 v2 PPTX (21장, 1.20MB)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx`
- **★ 5축 vision 산출 6 file (정본)**: `_internal/cache/rq3/validation/deck_phase2/`
  - `v2_axis_a.md` (B1~B5 V-A 메인 직접) — PASS
  - `v2_axis_b.md` (B6~B10 V-B) — PASS
  - `v2_axis_c.md` (B11~B14 V-C) — WARN minor 5
  - `v2_axis_d.md` (★ B15·B16 V-D, 478 line, 34KB) — PASS ★
  - `v2_axis_e.md` (B17~B21 V-E) — PASS
  - `v2_verdict.md` (종합) — ship-ready
- **★ v2 PNG 정본 21장**: `_internal/cache/rq3/validation/deck_phase2/v2_images/B01.png ~ B21.png` (25~84KB)
- **★ 수정 prompt (3 fix carry)**: `submission/_drafts/속도는벡터_발표deck_수정프롬프트_20260520_133527.md`
- **★ v1 (직전 7축 base, carry)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` (1.05MB, native shape PPTX)
- **★ 19장 deck (carry base)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx`
- **★ 6/11 보고서 신본 (정본, _124200, carry)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_124200.{md,pdf,docx}`

## 1. 본 연구 framing (carry · 불변)

본 연구는 Exqutor 논문(arXiv:2512.09695v2) 재현이 아니라 **표본 선택(sample selection) 단계 하나**의 개입(무작위 Bernoulli → 분포 인지 stratification)이 추정 오차(Q-error)에 미치는 영향을 전 변인에 걸쳐 검증한 완전 실험 — 3-way matched B1(기존)·CaseA(완전 대체, 음성 대조군)·CaseB(결합, 산술평균). 발표물은 코드명(B1/CaseA/CaseB)·"영역" 필러·영어 메타 라벨·수식 노출 금지. 보고서는 코드명 사용 OK.

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치(13종 method 결합 = CaseB ×13)를 패치된 PostgreSQL(서버 55435)에 주입해 "추정치 → 실행 계획 → end-to-end latency" 고리를 닫는 실험. 4조건: 기본엔진(baseline) / 베이스라인(B1) / 결합(CaseB ×13) / 오라클(true_card).

## 2. 본 세션(5/20 13:51~14:14)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 직전 handoff 정독·ultraplan | ✅ | `handoff_20260520_133737_deck21장검증.md` 흡수 → `~/.claude/plans/tidy-knitting-catmull.md` 승인. |
| ★ 결정적 발견: v2 = raster image PPTX | ✅ | sanity check 단계 (python-pptx + unzip) → v2 shape 카운트 모두 PICTURE 1개 (image-N-1.png full-slide stretch). v1 native shape 와 형식 다름. **XML 검증 불가, vision 검증만 가능**. 검증 방식 전환 결정. |
| v2 PNG 21장 정본화 | ✅ | `/tmp/v2_unzip/ppt/media/image-{1..21}-1.png` → `_internal/cache/rq3/validation/deck_phase2/v2_images/B{01..21}.png` 복사. |
| Phase 1 — 5축 vision sub-agent 5 launch | ✅ | 단일 메시지 multi-tool, 모두 Opus 4.7. V-A·V-B·V-C·V-D·V-E. 약 6분 만에 5 산출. |
| 메인 sanity cross-check | ✅ | B15·B16·B11·B19·B21 + B1·B2·B3·B4·B5 메인 직접 Read vision. V-A agent file 미생성 → 메인이 v2_axis_a.md 직접 작성. |
| Phase 2 — 종합 verdict 작성 | ✅ | `_internal/cache/rq3/validation/deck_phase2/v2_verdict.md` — 5축 verdict 종합 + fix 1·2·3 PASS + minor 11 + ship-ready 판정. |
| Phase 3 — handoff 갱신 | ✅ | 본 file + 새세션 복붙 프롬프트 + 직전 handoff archive 이동 + CLAUDE.md anchor 갱신. |
| Phase 4 — 커밋/푸시 | (진행 예정) | 미커밋 carry (직전 handoff 의 34건) + 본 세션 산출 (v2_*.md 6 + v2_images/ 21 PNG + v2 PPTX + 수정 prompt + handoff 4 변동) 같이 commit · push. |
| Phase 5 — 맥북 동기화 | **deferred** | **사용자 외출 중 → 집 복귀 후 별도 진행**. git pull (Capstone) + rsync (.claude) 양방향. |
| Phase 6 — Close + 최종 보고 | ✅ | TaskList completed + 사용자 보고. |

## 3. ★★★ 본 세션 결과 — 다음 세션이 반드시 흡수할 정본

### 3.1 5축 vision 검증 결과

| 축 | 담당 슬라이드 | verdict | crit | maj | min | 핵심 발견 |
|---|---|:--:|:--:|:--:|:--:|---|
| **V-A** | B1~B5 (표지·Sky) | **PASS** | 0 | 0 | 1 | B1 hero "속도는벡터" 그라데이션·Sky badge·한글 깨끗. B2 "33.3%→33%" 소수점 표기 minor (양극단 도식 design 무결성 영향 0). |
| **V-B** | B6~B10 (Violet) | **PASS** | 0 | 0 | 2 | 한글 5/5·Violet badge 5/5·carry 5/5·수치 11/11. hero 부재 (도식 위주) → fix 2 검증 대상 외 (PASS 우회). |
| **V-C** | B11~B14 (Emerald) | **WARN** | 0 | 0 | 5 | B11 "89.1%" 그라데이션 ✓ + 1508·1344·4.4% carry ✓. **B13 hero "13/16" 단색 minor**. B14 5축 multi-axis 11/11 정합. 코드명 노출 0. |
| **V-D** ★ | B15·B16 (★ fix 1·2·3 정밀) | **PASS** ★ | 0 | 0 | 2 | **fix 1 PASS ★★★** — B16 "비교 흐름 [기본 엔진→베이스라인→결합→정답]" 4갈래 도식 완벽 (위치=제목 underline 아래·full width 가로 띠·결합 청록+정답 그린 강조). **fix 2 PASS** — B15·B16 hero navy→cyan 그라데이션 burned-in. **fix 3 PASS** — 한글 자연 렌더. **정본 수치 23/23 = 100%**. 환각 회피 (B16 메시지 "실행 시간 거의 같다·결합 가치=견고함") 정합. |
| **V-E** | B17~B21 (Orange·결론·종결) | **PASS** | 0 | 0 | 1 | B21 "감사합니다" navy→cyan 그라데이션 명확. Orange (B17·B18·B20) / Emerald (B19 결론) / 없음 (B21) 색상 분기 정확. 19장 deck +2 shift carry 5/5. B19 §2 막대 "35%/89%" 정수 반올림 minor (구두 보강 권장). |

**5축 합산**: critical **0** · major **0** · minor **11** + **ship-ready 판정**.

### 3.2 fix 1·2·3 verdict 최종 (★ 본 세션 검증 핵심)

| fix | 대상 | verdict | 출처 |
|---|---|:--:|---|
| **fix 1** (B16 4갈래 도식) | B16 hero 아래 | **PASS ★★★** (ψ-M1 v1 major 시정) | V-D + 메인 sanity |
| **fix 2** (hero navy→청록 그라데이션) | 21장 메인 hero | **PASS** (B1·B11·B15·B16·B19·B21 6/6 메인 hero ✓) — sub-hero 단색 design 일관성 minor 2 (B13·B19 §2) | V-D + V-C + V-E + 메인 |
| **fix 3** (한글 Apple SD Gothic Neo) | 21장 한글 | **PASS** (21/21 깨짐 0건, raster burned-in 자연 렌더) — σ-C1 v1 시정 완료 | 5축 모두 |

**v1 의 major 1건 (ψ-M1) + carry-frozen XML 결함 2건 (σ-C1·σ-M1) → v2 에서 모두 시정 완료**.

### 3.3 정본 수치 catalog 23/23 = 100% (V-D 검증)

기존 엔진(B2): 33%(33.3%)·100% / B11~B14: 89.1%·1,508·1,344·35.2%·−4.38%·4.4%·13/16·5축 multi-axis 11항 / B15(14b): 3~7×·5.7×·2,880·12·16·15·4단계·Q3 7.0×·Q9 3.0×·Q10·Q12 6.0×·DEEP 8천만·180·100% / B16(14c): 94.9%·148/156·7/12·58%·0:0/4·1:4/4·2:3/4·8건·13×12·148/8.

### 3.4 carry 18장 변동 0건 (5축 모두 PASS)

B1↔A1·B2~B4↔A2~A4·B5~B10↔A5~A10·B11~B14↔A11~A14·B17↔A15·B18↔A16·B19↔A17·B20↔A18·B21↔A19. B15·B16 = 신설 14b/14c. 의미 단위 / 본문 / 수치 / layout 변동 0건.

### 3.5 minor 11건 — 모두 ship-ready 영향 0 (carry-frozen 또는 design 일관성)

상세 6 file: `v2_axis_{a,b,c,d,e}.md` + `v2_verdict.md` §6.

**5/27 발표 전 (선택) 결정 권고** (모두 발표 무결성 영향 0):
- (low) B13 "13/16" 그라데이션 적용 — design 일관성
- (low) B19 §2 막대 정수→소수점 — 구두 보강 가능
- (low) B2 "33.3%" 소수점 복구 — 양극단 도식 무결성 영향 0

→ **추가 수정 prompt 발행 불요**. v2 그대로 5/22 미팅 / 5/27 발표 / 5/28 포스터 base 활용.

## 4. ★ 다음 세션 task (5/22 미팅 · 5/25 보고서 최종 · 5/26 PPTX · 5/27 발표 · 5/28 포스터 · 6/11 최종)

1. **[★최우선·사용자 집 복귀 후] 맥북 동기화**:
   - `cd ~/Capstone && git pull --no-rebase origin main` (Capstone repo: 본 세션 push 받아오기)
   - `.claude` rsync 양방향 (sync.md 룰): 맥미니→맥북 push + 맥북→맥미니 pull
   - `~/.claude/rules/sync.md` 의 "동기화 해줘" 절차 그대로
2. **[★시각 렌더 검증·사용자 PowerPoint·Keynote 로 직접·5/22 미팅 전]**:
   - v2 PPTX (`속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx`) 를 PowerPoint·Keynote 로 열어 시각 확인
   - ⓐ 21장 raster image 모두 렌더 정상?
   - ⓑ Hero number 그라데이션 시각 명확?
   - ⓒ 페이지 번호 부재가 발표 흐름에 영향?
   - 결함 발견 시 → 추가 수정 prompt (선택)
3. **[필수·5/25 까지] 보고서 _124200 신본 팀원 최종 검토** (carry):
   - §5 검토 (조현빈 집필, 다른 팀원 검토)
   - PDF 46p 확인 — 학교 양식 "본문 14~22p" 기준
4. **[토요일 이후·사용자 직접] 포스터·팜플렛·소개영상 신본 작업** (carry):
   - 포스터: `submission/_drafts/속도는벡터_포스터_claudedesign_Phase2반영_20260520_100319.md`
   - 팜플렛: `submission/_drafts/속도는벡터_팜플렛_claudedesign_Phase2반영_20260520_100340.md`
   - 소개영상: `submission/_drafts/속도는벡터_소개영상_claudedesign_Phase2반영_20260520_100403.md`
   - 산출 받아온 후 별도 세션에서 main 검증 (5/28 마감 backstop)
5. **[후속] 통계 보강** (carry):
   - `analyze_latency.py` Cohen d + Cliff δ + bootstrap CI
   - 4 엔진 통합 PoC

## 5. 서버 접속·실행 (carry, 불변)

- 접속: `ssh capstone` (165.132.140.240, capstone2026, 무암호). PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559`.
- 55435 = 우리 패치 바이너리. `vector.injected_card` 기본 −1 = 평소 동작.
- 서버 작업 dir `/mnt/hdd0/home/capstone2026/cache/rq3/`. harness 3종 + `_measure_common.py` + `measure_paper_exact.py` + 산출물 `latency/{phase2,phase3}/`.
- ⚠️ **`build_custom.sh`/`apply_patch.sh` 절대 금지** — 재빌드 필요 시 직접 빌드.
- ★ **서버 권한 5/21 (수) 까지** — 본 세션 추가 실험 trigger 없음.

## 6. 산출물 경로

| 산출물 | 경로 | 상태 |
|---|---|---|
| 승인 본 세션 plan | `~/.claude/plans/tidy-knitting-catmull.md` | 정본 (완료, 폐기 가능) |
| **★ 5축 vision 산출 6 file** | `_internal/cache/rq3/validation/deck_phase2/v2_axis_{a,b,c,d,e}.md` + `v2_verdict.md` | 정본 |
| **★ v2 PNG 정본 21장** | `_internal/cache/rq3/validation/deck_phase2/v2_images/B{01..21}.png` | 정본 |
| **★ v2 PPTX (검증 대상, ship-ready)** | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` | ★ 정본 (1.20MB, 5/20 13:49) |
| v1 PPTX (직전 검증 base, native shape, carry) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` | carry (1.05MB) |
| 19장 PPTX (carry base) | `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx` | carry (1.02MB) |
| 수정 prompt (3 fix carry) | `submission/_drafts/속도는벡터_발표deck_수정프롬프트_20260520_133527.md` | carry |
| 6/11 보고서 신본 (carry) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_124200.{md,pdf,docx}` | 정본 |
| v1 7축 verdict (carry, native shape XML 검증) | `_internal/cache/rq3/validation/deck_phase2/verdict.md` + `axis_*.md` 7 | carry |
| Phase 2/A 측정 정본 (carry, 불변) | `_internal/cache/rq3/latency/{phase2,phase3}/` | 정본 |
| archive 이동 (본 세션) | `_internal/handoff/archive/handoff_20260520_133737_*` + 새세션_복붙_프롬프트_20260520_133737.md` | 완료 |

CLAUDE.md anchor 갱신 (line 23): 직전 anchor `handoff_20260520_133737_deck21장검증.md` → **본 handoff (`handoff_20260520_141449_deck_v2_vision검증.md`)**.

## 7. carry-forward / 보류 / 미커밋 (본 세션 직후)

- **★ 미커밋 변경** (본 세션 phase 1~3):
  - `_internal/cache/rq3/validation/deck_phase2/v2_*.md` 6 file + `v2_images/B*.png` 21 file (신규)
  - `_internal/handoff/active/handoff_20260520_141449_*` 2 file (신규)
  - `_internal/handoff/active/handoff_20260520_133737_*` 2 file → archive 이동 (mv)
  - CLAUDE.md anchor 갱신
- **미커밋 carry** (직전 세션 _133737, 본 세션이 같이 commit):
  - 6/11 보고서 _124200 신본 + figure 9 + build_report_figures_20260519.py
  - 수정 prompt _133527
  - v1 PPTX (속도는벡터_최종발표_슬라이드_phase2반영.pptx)
  - v2 PPTX (속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx)
  - 직전 handoff archive (_100812, _124250)
  - 6_11 보고서 _093500 archive 3 file
- **deferred tool 로드 패턴**: 새 세션은 `ToolSearch select:TaskCreate,EnterPlanMode,ExitPlanMode,Monitor,TaskUpdate,TaskList` 선제 로드.
- **★ Phase 5 맥북 동기화 deferred**: 사용자 외출 중 → 집 복귀 후 별도 진행. `~/.claude/rules/sync.md` 절차 그대로.

## 8. ★ 환각 회피 룰 (carry, 5축 검증과 정합)

- 정본 수치 정합 = `_internal/cache/rq3/latency/{phase2,phase3}/figures/paired_stats.csv` + 직전 handoff §3.2 fix log + 본 handoff §3.3 fix.
- **B1 plan 회복은 qid 의존 fragile (7/12)** — qid=0 만으로 generalize 금지. (B16 좌측 0:0/4·1:4/4·2:3/4 carry PASS)
- **CaseB > B1 latency 측면 우열은 없음** (paired Wilcoxon 7.7% 만 유의). plan 회복 robustness 측면 우위만 강조. → **B16 의 메시지 "실행 시간 거의 같다 / 결합 가치 = 견고함" 정합 PASS** (V-D 환각 회피).
- **core 4 cell sel=0.001 한정** — sel 일반화 금지.
- **plan_signature 정의 = Node Type pre-order 튜플 (1-tuple)** — 보고서 정정 완료 (carry).
- **q9 sel=0.1 honest exception** — plan ≠ baseline 인데 speedup < 1.0. 보고서 §5.6 + §6.4 (1) 갈래 carry.
- vector.c·`build_custom.sh`/`apply_patch.sh` 손대지 말 것.
- **보고서 코드명(B1/CaseA/CaseB) 사용 OK / 발표물 코드명 노출 금지** — 발표물은 한국어 라벨(기본 엔진/베이스라인 방식/정답/결합 방식). 5축 검증 결과 코드명 노출 0건.
- 이전 세션 (v11/v12) 수치 generalize 금지 — RQ3 portfolio (1508건) 와 「엔진 적용 검증」 latency (2880회 + Phase A 1920회) 는 별개.
- **★ 본 세션 신규 carry**: v2 PPTX = **raster image PPTX 통째 변환** (native shape XML 검증 불가, vision 만). 직전 19장 deck 와 같은 형식. claude.ai/design 의 PPTX export 가 raster 화하는 패턴 carry — 다음 deck rebuild 시 PPTX 형식 사전 확인 권장.
- **★ 본 세션 신규 carry**: fix 2 그라데이션은 메인 hero 만 적용된 design 의도 — sub-hero (B2 "33%·100%" · B13 "13/16" · B19 §2 막대) 단색 carry. 5/27 발표 전 추가 적용은 선택.

---

작성: 2026-05-20 14:14 KST — 본 세션 (v2 raster image vision 검증 5축) 완료. fix 1·2·3 PASS · minor 11 · ship-ready. → 다음 = 사용자 집 복귀 후 맥북 동기화 + 5/22·5/25·5/26·5/27·5/28·6/11 마감.
