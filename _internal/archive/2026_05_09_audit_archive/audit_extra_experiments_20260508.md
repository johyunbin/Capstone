# Audit — 5/27 발표 전 추가 실험 priority + 디렉토리 hygiene

작성: 2026-05-08 21:55 KST · 잔여 D-19 · 작성자: 백그라운드 에이전트 V5

---

## A. 추가 실험 우선순위 표

| 실험 | 시간 | narrative 가치 | 5/27 전 가용성 | 권장 |
|---|---|---|---|---|
| **MinHash (P5 hashing 보강)** | ~0.5h | ⭐⭐⭐ — paradigm 검증 §5.3 LSH Wave 0 fail 의 직접 보강. P5 representative 정당화 강화 | ✅ 매우 가능 | **권장 (P1 즉시)** |
| **Adaptive×4강 Ensemble (mode B matched)** | ~5h | ⭐⭐⭐ — Adaptive_Sampling 분석 §2.3 "matched budget" sensitivity. 5/8 회의 mention | ✅ Phase 1+2 후 5/9 evening | **권장 (P2 5/9~5/10)** |
| **K-aware sweep 확장 (SIFT/SSN/WIKI/YFCC)** | ~15h | ⭐⭐ — DEEP 만 K=10/50/100/200 done. 4 dataset × 2 SF × 4 K = 32 cell. K=20 fixed 의 robustness 입증 (R-tree limitation §5.2 와 동일 belt). 발표 supplementary 1장 | △ 5/13~5/15 launch 가능, ~3일 | **선택 (P3 자문 회신 후)** |
| **per-stratum BERN per-K 분석** | ~2h (분석만) | ⭐⭐ — RQ1 boost. 기존 cache 재사용 → 측정 X. ceiling effect 직관 강화 | ✅ 매우 가능 | **권장 (P1 즉시)** |
| **Selectivity extreme low (0.001 / 0.005)** | ~3h | ⭐ — RQ1 BERN ceiling 추가 1점. 그러나 본 thesis 의 sel range 5종이 이미 충분 | △ 5/12 evening 가능 | 보류 |
| **SF100 (80M)** | ~60h+ | ⭐ — 채림 정본 합의 미정 + 5/27 전 부담 압도. 실패 위험 높음 | ❌ 회신 후 launch = 5/22 미팅 시점 결과 X | **연기** (자문 회신 + 6/11 보고서로) |
| **Sample size budget 4종 × 10 cell × 11 method** | ~30h | ⭐ — 본 thesis 는 budget = 385 fixed 명시 (Adaptive와 일치). sensitivity 입증은 Adaptive paired 가 sub-set 으로 cover | ❌ 시간 부담 | **연기** |
| **Multi SF1 setup + 측정** | ~5h+10h | ⭐⭐ — Multi 일반화 sample 확장. 단 multi 25× shrinkage 본 thesis 결론 자체는 변하지 않음 | △ 5/16 ~ 5/19 가능 | 선택 |
| **Distance shell + Importance Sampling fix** | ~4h | ⭐ — 5 paradigm 외 method 제외 정당 (검증 §6 19종 제외). 추가 측정해도 narrative 변화 X | ✅ | 보류 |
| **Tier 2 (birch, kde_pilot) narrative 정정** | ~0h (문서만) | ⭐⭐⭐ — 강재현 audit 결과 kde_pilot KM20 leak. master_v6 §10.5 정정 필요 | ✅ 즉시 | **권장 (P1 즉시)** |

---

## B. 디렉토리 cleanup 권장

### B.1 _internal/ 루트 (44 handoff/deck/worker stale)

| 파일 | 권장 |
|---|---|
| handoff_v3 ~ v8 (5/7 ~ 5/8 AM, 8개) | `_internal/archive/2026_05_07_dawn_chain/` 이동 |
| handoff_v9~v11 (5/8 AM~PM 3개) | `_internal/archive/2026_05_08_meeting_chain/` 새로 생성 후 이동 |
| handoff_v9_PDF + v10_PDF (1.7MB) | git 미트래킹이면 삭제, tracked 면 archive 이동 |
| handoff_*.md 5/6~5/7 7개 (P6, 8M, RQ3_7way, morning, A/B/integration/narrative) | archive/2026_05_07_dawn_chain/ 이동 |
| worker_A~L (12개, 5/7 작성) | archive/2026_05_07_dawn_chain/ 이동 — 이미 산출물 흡수됨 |
| deck_status_v2/final/review_*/followup (6개, 5/7 작성) | archive/ 이동 — Academic v3 finalize 완료 |
| _w4_partial_summary*.csv + .bak | archive/ 또는 삭제 (master_v6 흡수 완료) |
| rq1/rq2 _recovered.json (5/8 09:44 cache) | analyze_10cell_w4 재계산 결과로 대체됨 → 삭제 OK |
| yfcc_compare/distribution (5/8 09:44 cache) | 삭제 OK |
| 카톡_5월8일발송_*, 팀원공유_RQ_* 5/7 발신용 | archive/ 이동 |

**현재 v12 (5/8 20:30) + v13 (5/8 21:10) 만 active**, 나머지 retain X.

### B.2 _internal/scripts/ (49 files)

`_build_docx_v0/v1/v2.py` + `_build_docx_4_28.py` (4개) 의 중복: v2 만 남기고 archive 이동. `*.bak.20260508_*` 4개도 archive 이동.

### B.3 _internal/server_wrappers_backup_20260507/ (124K)

`_internal/archive/` 로 이동 — 5/7 백업 이력으로만 의미.

### B.4 submission/_drafts/archive/W4_5월6일~7일_pre회의/

20개 (5/6~5/7 W4 사전 자료) — 이미 archive 안에 있음. **clean**, 추가 이동 X.

### B.5 권장 archive 위치

```
_internal/archive/
  2026_05_07_dawn_chain/   # 기존 (handoff/worker dawn)
  2026_05_08_meeting_chain/ # 신규 — v9~v11 + 회의 자료
  scripts_legacy/           # 신규 — _build_docx_v0/v1, .bak
```

cleanup 효과: _internal/ 루트 96 entries → ~25 entries, 다음 세션 진입 가독성 ↑.

---

## C. CLAUDE.md update 권장 사항

1. **현재 단계 첫 줄**: "5/8 21:10 RQ3 paradigm framework 확정 + Adaptive launch ready" → "5/8 22:00 Adaptive overnight launch, 5/9 morning 회수" 로 갱신
2. **W2 자문 칸**: "Adaptive 비교 측정 launch" → "Adaptive 결과 회수 + Multi 광범위 launch"
3. **다음 단계 priority**: 1번 Adaptive 비교 → ① P1 즉시 4종 (MinHash + Tier 2 narrative 정정 + per-K 재분석 + 4강 paired Δ%) ② P2 Ensemble matched ③ P3 K-sweep 확장 자문 회신 후
4. **W1 Sprint 산출** 4강 표기: "★4 sparse_rp" → "★4 sparse RP (Achlioptas 2003 PODS, P4 Hybrid 대체)"
5. **산출물 위치** 추가: `_internal/RQ3_paradigm_심층검증_20260508.md`, `_internal/Adaptive_Sampling_method_분석_20260508.md`
6. **5/9 morning 카드** 신규 추가: "Adaptive flag + 7 parquet 회수 → 4강 paired Δ% 분석"

---

## D. 결론 — 5/27 발표 전 추가 launch 3개 (priority)

1. **P1 (5/9 morning, 즉시 가능, ~3h)**: ① Adaptive baseline 회수 + 4강 paired Δ% 분석 (이미 launch 대기) ② MinHash 0.5h 추가 측정 (P5 representative 보강) ③ per-stratum BERN per-K 재분석 (cache 재사용) ④ Tier 2 (birch, kde_pilot) narrative 정정.
2. **P2 (5/9 ~ 5/10, ~10h)**: Multi 광범위 (3 cell × 11 method) launch — handoff_v13 §6 Step 3 원안. 추가로 Adaptive×4강 Ensemble matched-budget sensitivity (~5h) 5/10 evening overnight.
3. **P3 (5/13 ~ 5/15, 자문 회신 후, ~15h)**: K-aware sweep 확장 SIFT/SSN/WIKI/YFCC × SF1·SF10 × K{10,50,100,200} = 32 cell. 자문 합의 후 launch. 발표 supplementary 1장.

**연기**: SF100 (~60h+) — 6/11 최종보고서로. Sample size budget sensitivity — Adaptive paired sub-set 으로 cover 인정.

핵심 시각: P1 의 4종 (즉시) 이 narrative 영향 최대. K-sweep 은 자문 회신을 통해 "robustness 입증 supplementary" 로 위치 선정 후 launch 결정.
