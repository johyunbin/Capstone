# Worker INDEX — 5 worker 진입 가이드 + 의존성 그래프

> **manager 세션**: 2026-05-07 11:11 KST, Opus 4.7 1M
> **기반**: 5/7 narrative 정정 commit 8d079d3 / 1267b8a / 74d6aea / fc7e147
> **시간 제약**: 5/8 19:00 비대면 회의 D-1 (~7시간 30분 여유), 5/22 교수 미팅 D-15, 5/27 최종 발표 D-20

---

## 5 worker 임무 한눈에

| Worker | 임무 | 산출 | 시간 | 의존성 |
|--------|------|------|------|---------|
| **[A](worker_A_PPT_5월27일발표_20260507.md)** | 5/27 발표 PPT 14+1 slide (Academic v3 정정 + chat prompt 3종 + Q6 + Limitation 6-card) | `submission/_drafts/속도는벡터_5월27일발표_v3_academic.{pptx,pdf}` | 2-2.5h | D 와 sync (Slide 4 footnote figure) |
| **[B](worker_B_채림석사_자문메일_20260507.md)** | 채림 석사 자문 메일 final + PDF 6종 + 발송 prompt | `submission/_drafts/속도는벡터_자문메일_채림석사_final_20260515.md` + 자문첨부 6 PDF | 1.5h | 5/8 회의 합의 + Worker D figure |
| **[C](worker_C_지도교수_자문메일_20260507.md)** | 지도교수 자문 메일 final + 5/22 미팅 안건 1page + PDF 5종 | `submission/_drafts/속도는벡터_자문메일_지도교수_final_20260515.md` + 5/22 미팅 안건 + 자문첨부 5 PDF | 2h | 5/8 회의 합의 + Worker D figure + 5/22 미팅 일정 |
| **[D](worker_D_Phase6_7_figure_20260507.md)** | Phase 6/7 5-cell 비교 figure (Slide 4/6 footnote 보강) | `experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png` | 1-1.5h | 독립 (즉시 dispatch 가능) |
| **[E](worker_E_최종보고서_outline_20260507.md)** | 6/11 최종 보고서 outline v1 (8 section, 30-40p, 분담 plan) | `plans/최종보고서_outline_v1_20260507.md` | 2-3h | 5/8 회의 narrative final (deferred OK) |

**총 작업 시간 추정**: 9-11h (5 worker 직렬). 병렬 진행 시 3.5-4h (D + A 5/7 / B + C + E 5/8 후).

---

## 의존성 그래프

```
                    ┌─────────────────┐
                    │   manager (본)  │
                    │  4 commit + push│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌────────┐          ┌──────────┐         ┌─────────┐
   │ D (figure) │ ───▶ │ A (PPT)  │         │ E (보고서)│
   │ 5/7 즉시   │      │ 5/7 즉시 │         │ 5/8 후  │
   └────────────┘      │ ★ sync   │         └─────────┘
                       └──────────┘
                             │
                             │ (5/22 미팅 직전 최종)
                             │
                       ┌─────┴──────┐
                       ▼            ▼
                  ┌────────┐    ┌────────┐
                  │ B(채림) │    │ C(교수) │
                  │ 5/8 후  │    │ 5/8 후  │
                  └────────┘    └────────┘
                       │            │
                       ▼            ▼
                  5/15 발송     5/15 발송 + 5/22 미팅
```

---

## Dispatch 권장 순서

### 즉시 (5/7 11:30~)

1. **Worker D (figure)** — 독립, 1h. JSON read → matplotlib figure → commit → push
2. **Worker A (PPT)** — 독립 시작 가능 (Step 1 chat prompt 3종 발송) + Step 2 부터 D 와 sync. 1h chat → 30min Step 2 → 30min Step 3 → 30min Step 4 export

병렬 진행 가능. 사용자가 별도 세션 2개로 진입 권장 (A 와 D 가 동시에 진행되면 Slide 4 footnote 가 figure 출시 직후 sync 가능).

### 5/8 회의 후 (5/8 21:00~)

3. **Worker B (채림 자문)** — 5/8 회의 합의 사항 반영, 1.5h
4. **Worker C (지도교수 자문 + 5/22 미팅 안건)** — 합의 사항 반영, 2h
5. **Worker E (보고서 outline)** — narrative final 반영, 2-3h

병렬 진행 권장. 사용자가 3 세션으로 진입.

### 5/22 미팅 후 (5/22 21:00~)

- B/C 자문 final 보강 (지도교수 미팅 피드백 반영)
- E outline v2 (지도교수 합의 narrative 반영)
- A 발표 deck v2 (5/22 피드백 → 5/26 마감 반영)

---

## 새 worker 세션 진입 prompt template

```
@_internal/worker_{X}_*_20260507.md 읽고 작업.

[자동 진행]
1. 핸드오프 §1 입력 자료 확인
2. §2 작업 단계 sequential 진행
3. §3 산출 spec 검증
4. §4 검증 기준 통과 확인
5. commit + push

[제약]
- master.md narrative 변경 X (manager 4 commit 보존)
- contribution 7종 + Limitations 6종 일관 유지
- 한글 폰트 Apple SD Gothic Neo
- §5 의존성 다른 worker 와 sync 시점 준수
- §7 본 worker 가 만들지 말 것 list 준수

manager 세션 (5/7 11:11) 산출 핸드오프 4 commit:
- 8d079d3 narrative 일관성 보강 (DEEPcluster=20 + 자문 메일 5/7 갱신)
- 1267b8a RQ2/3 딥리뷰 보강 + manager handoff
- 74d6aea narrative 옵션 2 정직 reporting 일관 정정
- fc7e147 자동 chain 운영 산출 archive
```

---

## 충돌 / 중복 영역 + 통합 룰

| 영역 | 룰 |
|------|------|
| `master.md` | **manager 세션 단일 책임 (이미 commit 완료)**. Worker 변경 X |
| `slide outline` | **Worker A 단일 책임** (Academic v3 정정). Worker D 는 figure 만, 본문 X |
| `자문 메일 채림석사` | **Worker B 단일 책임**. Worker C 는 지도교수 메일만 |
| `자문 메일 지도교수` + `5/22 미팅 안건` | **Worker C 단일 책임** |
| `Phase 6/7 figure` | **Worker D 단일 책임**. Worker A/B/C 는 figure 활용만 |
| `최종 보고서 outline` | **Worker E 단일 책임** |

---

## 본 manager 세션 이후 deferred 작업

- **σ table reproducibility 회복** (DEEP 1M / SIFT σ 재계산) — W2 권고. 5/8 회의 후 dispatch 권장. compute_stratum_sigma.py 의 unconditional DELETE → conditional 변경 후 재실행.
- **NMI / AMI metric 추가** (16 method real data) — RQ3 robustness check. W3 sprint.
- **Real DEEP 1M / SIFT data ARI** (16 method × 2 ds) — RQ3 narrative 강화. W3 sprint.
- **8M sensitivity 16 method 확장** (현재 5 method) — W3 sprint.
- **vector.c integration** — future work (5/6 patch memory leak).
- **Phase 6/7 root cause 정량** (numpy estimator sampling-population scope 통일 + vector.c 측정 path 일관화) — future work.

---

## 예상 결과 (5/8 회의 19:00 D-1 ready 상태)

5/7 11:30 ~ 5/7 18:00 사이 (Worker D + A 진행) 후:
- ✓ 5/27 발표 deck v1 export ready
- ✓ Phase 6/7 figure 산출 (자문 메일 첨부 + Slide 4 footnote)

5/8 19:00 회의 자료:
- ✓ 1page summary (commit 74d6aea)
- ✓ master.md (commit 8d079d3, 7 contribution + 6 Limitations)
- ✓ slide outline (commit 74d6aea)
- ✓ 카톡 narrative 메시지 1/2/3 (commit 74d6aea)
- ✓ 자문 메일 초안 2종 (commit 8d079d3, 5/7 갱신)

5/8 회의 합의 후:
- → Worker B/C/E dispatch
- → 5/15 자문 발송
- → 5/22 미팅
- → 5/27 발표
- → 6/11 보고서

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 11:25 KST
**다음 트리거**: 사용자가 worker 세션 dispatch (D / A 우선, B/C/E 5/8 후)
