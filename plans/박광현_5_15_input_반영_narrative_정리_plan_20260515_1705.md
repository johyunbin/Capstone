# 박광현 5/15 미팅 input 반영 — narrative v2 final 정리 plan

작성: 2026-05-15 17:05 KST
base: `_internal/records/kakaotalk/20260515_박광현미팅.md` + `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v2_draft.md`
사용자 지시 (5/15 16:45): "내러티브에서 제외된 내용은 아예 제거하고 future work 나 한계로 명시되는 부분 없도록"

---

## 1. 박광현 input 6 항목 → narrative 대응

| Input | 대응 |
|---|---|
| 1. 분포별 샘플링 방식 | 기존 §9 paradigm 8 매핑 유지 |
| 2. 논문에 갇히지 말고 결과 기반 재설정 | §0 paper §V-B anchor wording 완화 (anchor 자체는 유지, "Extending" 표현 약화) |
| 3. 분포 빠르게 catch | §10 자원 효율에 fittime 87 file 정량 source 추가 (sparse_rp 3.15s ~ hilbert_real 42.36s, 13.4× range) |
| 4. 엔진 통합 가능성 | 실측 없음 → narrative 에서 가설 시나리오 (RAG/OLTP/Mobile/Distributed) 전체 제거 |
| 5. uniform 만 = 공격받을 여지 | adversarial 실측 없음 → 미커버 영역으로 future work 두지 않고 narrative 에서 제거 |
| 6. 순서 정의 어려움 | §9.4 결합 가치 wording 유지 (plan robustness 표현은 채림 정리 후 적용) |

---

## 2. narrative v2 draft 에서 제거할 section (실측 없는 가설/future work)

| section | line | 사유 |
|---|---|---|
| §12.7 Neyman 가설 verify future work | 649-656 | future work 도피처 |
| §13.5 streaming Form 1 phase 1 미완 | 679-681 | 측정 미완 |
| §13.6 산업 적용 4 시나리오 (RAG/OLTP/Mobile/Distributed) | 685-738 | 가설 시나리오, 실측 없음 |
| §14 전체 (positioning + 측정 plan + publication + timeline + 박광현 align) | 742-914 | 측정 plan / future paper |
| §A 정직 disclosure 중 미커버 한계 항목 | 부록 | "한계" 명시 부분 |

남길 section: §0-§12 (단, §13.5 §13.6 §12.7 제외) + §13.1-§13.4 (실측 기반 단독/결합/자원/다중테이블 권장) + 부록 중 측정 evidence 만.

---

## 3. narrative 에 추가할 영역

### §10 자원 효율에 fittime 87 file 정량 source 추가

87 file 측정 결과 (5/15 launch 완료):

| Method | n | fit_time mean | range |
|---|---:|---:|---|
| sparse_rp | 15 | 3.15s | 0.35 ~ 8.38 |
| neuram | 16 | 5.88s | 0.62 ~ 17.61 |
| chao_weighted | 15 | 8.80s | 0.12 ~ 28.34 |
| pca1d | 17 | 19.86s | 0.81 ~ 68.18 |
| hilbert_real | 17 | 42.36s | 1.40 ~ 100.04 |

range = sparse_rp 3.15s ~ hilbert_real 42.36s = 13.4× 차이.
누락 7 file + A1-DEEP CaseB 누락 3 file = retry 10 file 측정 진행 중 (tmux `fittime_retry`).

---

## 4. 진행 순서

1. 박세은 정리본 받기 전: 회의록 + 본 plan 만 작성 (완료)
2. 박세은 정리본 도착 → input 6 항목별 fix/변경 final 확정
3. narrative v2 draft → v2 final 정리 (제거 + §10 fittime 강화 + §9.4 wording 확정)
4. 5/27 deck v7 update + 6/11 outline v4 update
5. commit + push

---

## 5. 주의

- "영역" 같은 의미 없는 word filler 반복 환각 발생 가능 → 문장 짧게, 추상 매핑 회피, 사실 위주
- narrative v2 draft 자체에 "영역" 단어 726 회 — 본 plan 적용 시 함께 정리 검토
