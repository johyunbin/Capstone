# Handoff v27 — narrative v5 + 박세은 5/15 20:49 정리 + 전체 산출물 (5/15 21:35)

> 5/15 박광현 D-Day 미팅 (14:00) + 박세은 5/15 20:49 정리본 종합 반영. narrative v2 → v3 → v4 → v5 로 4 단계 진화. 핵심: 데이터셋 4 type + dynamic method selection axis.

---

## 1. 본 세션 5/15 14:00 ~ 21:35 (7h 35m) commit chain

| commit | 시점 | 영역 |
|---|---|---|
| 313b9a4 | 17:00 | 회의록 + plan 재작성 (환각 revert 후) |
| 340f834 | 17:00 | narrative v2 정리 1차 (-243 line) |
| 8c8e5bb | 17:10 | handoff v26 + storyline v3 + outline v4 + CLAUDE.md |
| d18b0ac | 18:10 | claude.ai/design prompt v8 |
| 4879999 | 20:30 | narrative v3 (main theme 재설정) |
| f77cf57 | 20:40 | narrative v4 outline |
| ad8bc43 | 20:50 | narrative v4 본문 |
| 6f5892a | 21:00 | narrative v5 outline (박세은 정리 반영) |
| **fdb9e04** | **21:10** | **narrative v5 본문 (현재 HEAD)** |

본 commit 으로 추가 산출물:
- 추가 측정 plan: `plans/추가측정plan_v5_narrative_20260515_2115.md`
- 5/27 storyline v4: `plans/5_27_발표/5_27_storyline_v4_20260515_2120.md`
- claude.ai/design prompt v9: `submission/_drafts/속도는벡터_5_27_키노트_prompt_v9_20260515_2125.md`
- 6/11 outline v5 update: `plans/6_11_보고서/6_11_보고서_outline_v5_update_20260515_2130.md`

---

## 2. 박세은 5/15 20:49 정리 (★ narrative v5 의 핵심 source)

```
1. 분포를 안다 모른다로 구분하지 않기
2. 데이터셋이 들어오면 최대한 빨리 분포를 파악해서 대응하기
   (여기에 우리 예전 rq3에서 썼던 메소드들 사용하면 될 것 같습니다)
3. 분포를 알게 된 데이터셋에 대해서 가장 적합한 샘플링 방식 제안하기.
   이때 분포 분류는 2~3가지 정도로 나누면 될 듯?
```

사용자 의도 해석:
- 우리 method (클러스터링 등) 자체가 분포 파악 도구 → "분포 안다/모른다" binary 의미 없음
- 분포 분류 기준 = 데이터셋 특성별 method 적합성 분류 = **데이터셋 4 type**

---

## 3. narrative v5 핵심 (commit fdb9e04, 269 line, 11 section + 부록 §A 7)

### §0 main theme (reframing)
"Measurement-driven Distribution-aware Cardinality Estimation for VAQ"
- paper §V-B base reference only (anchor 약화)
- 우리 method 자체가 분포 파악 도구
- binary "분포 안다/모른다" 폐기

### §3 ★ 데이터셋 4 type + Type 별 적합 method

| Type | 정의 | cells | 적합 method | Δ% best | fit_time |
|---|---|---|---|---:|---:|
| Type 1 | small single sf=1 (0.1M, 96d) | A5-sf1 | **chao_weighted K=20** | **-14.11%** ★ | 9.40s |
| Type 2 | medium single sf=10 (1M) | A5-sf10 | sweet spot 약함 | -6.00% | 9.40s |
| Type 3 | large single sf=100 저-중차원 | 5 cells | chao_weighted / sparse_rp K=20 | -11~-12% | 3.67~9.40s |
| Type 4a | large multi 288d | A2-Fig7 | hilbert_real K=30 | (Pareto Top 5) | 43.50s |
| Type 4b | large multi 864d | A2-Fig9 | **Centroid tuple** | **-7.37%** ★ | 학습 비용 0 |

### §7 Dynamic method selection flow
```
데이터셋 진입 → profile (rows/structure/dim) → Type 판별 → Type 별 권장 method → CaseB or CaseA
```

### 결론 finding 5
1. 분포 catch speed 11.9× (fit_time)
2. **데이터셋 4 type + dynamic method selection** ★ 신규
3. 정확도 paired 92.5%
4. plan robustness 9 환경 + selectivity paradox
5. Pareto Top 5 (정확도 + 자원 동시 best)

---

## 4. 추가 측정/실험 plan (★ 사용자 결정 필요)

`plans/추가측정plan_v5_narrative_20260515_2115.md` 영역 정리. priority:

| Priority | 측정 | file 수 | server time | 가치 |
|---|---|---:|---|---|
| ★★★ P1+P2+P3 | Type evidence 보강 (SF axis SIFT/SSN + multi-table 추가) | 66 file | 6-12h | Type 1/2/4 evidence cell 1→3 |
| ★★ P4 | A4-sel sel sweep (paper Fig 13 완성) | 222 file | 10-15h | sel axis plan robustness |
| ★★ P5 | K granularity dataset 확장 (SIFT/SSN K=10/30) | 96 file | 5-8h | K pattern dataset 일관 |
| (post-narrative) | 박광현 input 4 엔진 통합 POC | 측정 10-20h + dev 20-40h | 30-60h | 사용자 향후 실험 진행 |

권장: **P1+P2+P3 즉시 launch (66 file)** — 가장 효율적, Type evidence 보강 핵심.

---

## 5. claude.ai/design deck v9 update (★ 사용자 직접 paste 필요)

prompt v9: `submission/_drafts/속도는벡터_5_27_키노트_prompt_v9_20260515_2125.md`

deck v8 (14 slide) → v9 (15 slide) 변경:
- slide 3 문제 reframing (binary 폐기)
- **slide 8 데이터셋 4 type 분류 (신규)**
- **slide 9 Type 별 적합 method 매핑 (신규)**
- **slide 13 Dynamic method selection flow (신규)**
- slide 14 결론 finding 4 → 5
- slide 15 정정 룰 7 (A-5 신규 추가)

사용자 직접 진행:
1. claude.ai/design Capstone project Keynote_Capstone conversation 새 message
2. prompt v9 paste → deck v9 generate

---

## 6. 보류 영역 (박세은 + 임채림 추가 input 받은 후 final)

- v5 부록 §B-§M (v2 carry-over 검토 — 박세은 9 답변 form / Agent A-J 결과 등)
- v5 §0 main theme wording 미세 조정
- 정정 룰 7 → 7+ (임채림 추가 자문)
- §3 4 type 의 sub-type (Type 4a / 4b 분리 vs 통합) 사용자 확인

---

## 7. 다음 세션 action

### 즉시
1. 사용자 추가 측정 launch 결정 (P1+P2+P3 = 66 file 권장)
2. 사용자 claude.ai/design deck v9 paste
3. 박세은 + 임채림 final input 받은 후 narrative v5 → v5 final

### 5/16 ~ 5/20
1. 추가 측정 회수 + 결과 분석
2. v5 final + deck v9 final
3. 5/27 발표 rehearsal

### 5/27 발표 후
1. 박광현 input 4 엔진 통합 POC (Phase 1)
2. 6/11 보고서 §1-§10 본격 drafting

---

## 8. 환각 회피 룰 (5/15 17:04 영구 룰)

1. "영역" 의미 없는 반복 금지 — token 부족 또는 word filler 깨짐 패턴
2. 추상적 매핑 / 시뮬레이션 회피 — 사실 위주, 짧은 문장
3. 큰 블록 한 번에 작성 X — 작은 단위 Edit 으로 정확 매칭
4. commit 전 grep -c "영역" 으로 검증 — 비정상 횟수 시 멈춤

---

## 9. 서버 + measurement portfolio

- server: 165.132.140.240 (capstone2026), `/mnt/hdd0/home/capstone2026`
- tmux: 없음 (fittime_retry 17:01 종료)
- 측정 portfolio: **1352 file** (paper exact 1001 + 추가 351)
- fittime 90 file 직접 측정: Pareto Top 5 × 9 cell × 2 mode (5/15 launch ~ 17:01 retry 완료)
- 추가 측정 P1+P2+P3 launch ready (66 file, 6-12h)

---

## 10. 박세은 + 박광현 input → narrative v5 최종 mapping

| input | v5 section |
|---|---|
| 박세은 1 binary 폐기 | §0 main theme + §A-5 |
| 박세은 2 빠른 catch | §2 fit_time 11.9× |
| 박세은 3 분포 분류 + 매핑 | §3 4 type + §7 dynamic |
| 박광현 1 분포별 sampling | §3 |
| 박광현 2 결과 기반 재설정 | §0 + §1 |
| 박광현 3 분포 catch speed | §2 |
| 박광현 6 plan robustness | §5 |
| 박광현 4 엔진 통합 | post-narrative (v5 안 포함, 사용자 향후 실험) |
| 박광현 5 adversarial | 제외 (측정 evidence X) |

---

작성: 2026-05-15 21:35 KST · 본 세션 5/15 14:00 ~ 21:35 (7h 35m) 종합 · narrative v2 → v5 4 단계 진화 · 박세은 5/15 20:49 정리 + 박광현 D-Day 미팅 input 종합 완료
