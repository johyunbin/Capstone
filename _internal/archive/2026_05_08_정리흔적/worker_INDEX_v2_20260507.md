# Worker INDEX v2 — 8 worker 진입 가이드 (5/7 12:05 갱신)

> **manager 세션**: 2026-05-07 12:05 KST, Opus 4.7 1M
> **기반**: 5/7 narrative 정정 + 통합 commit 9개 (74d6aea / 1267b8a / fc7e147 / 8d079d3 / 1475814 / edbcfd3 / 592b022 / 984be3b / 80f48d1)
> **추가 (v2)**: 5/5 회의 옵션 (B) Toy 검증 + 8M baseline + 8M sel 5단계 확장 worker 3종 추가
> **시간 제약**: 5/8 19:00 비대면 회의 D-1 / 5/22 교수 미팅 / 5/27 최종 발표 D-20 / 6/11 보고서 D-35

---

## 8 worker 임무 한눈에

### 5/8 회의 직전 worker (5종, 기존 v1)

| Worker | 임무 | 산출 | 시간 | dispatch 시점 |
|---|---|---|---|---|
| **[A](worker_A_PPT_5월27일발표_20260507.md)** | 5/27 발표 PPT 14+1 slide (Academic v3 정정) | `속도는벡터_5월27일발표_v3_academic.{pptx,pdf}` | 2-2.5h | 5/7 즉시 |
| **[B](worker_B_채림석사_자문메일_20260507.md)** | 채림 석사 자문 메일 final + 6 PDF 첨부 | `자문메일_채림석사_final_20260515.md` | 1.5h | 5/8 회의 후 |
| **[C](worker_C_지도교수_자문메일_20260507.md)** | 지도교수 자문 메일 + 5/22 미팅 안건 1page | `자문메일_지도교수_final_20260515.md` | 2h | 5/8 회의 후 |
| **[D](worker_D_Phase6_7_figure_20260507.md)** | Phase 6/7 5-cell 비교 figure | `phase6_vs_phase7_5sel.png` | 1-1.5h | 5/7 즉시 (A와 sync) |
| **[E](worker_E_최종보고서_outline_20260507.md)** | 6/11 보고서 outline v1 | `최종보고서_outline_v1_20260507.md` | 2-3h | 5/8 회의 후 |

### W2 측정 보강 worker (3종, v2 신규)

| Worker | 임무 | 산출 | 시간 | dispatch 시점 |
|---|---|---|---|---|
| **[F](worker_F_8M_baseline_확장_20260507.md)** | DEEP 8M baseline 3개 (KM20 + RANDOM20 + BERN) | `rq3_8m_{km20,random20,bernoulli}.parquet` (22 method 완성) | 3-4h | **5/7 즉시** (서버 idle) |
| **[G](worker_G_8M_sel_5단계_확장_20260507.md)** | DEEP 8M sel 5단계 확장 (19 method × 3 추가 sel) | `rq3_8m_5sel_cross_scale.{csv,md}` | 5-7h | 5/7 즉시 (병렬) |
| **[H](worker_H_멀티테이블_Toy검증_20260507.md)** | 멀티 테이블 Toy 검증 — 단일→multi 4강 method 일반화 입증 | `multi_table_toy_validation.md` | 8-12h (1~2일) | 5/8~5/22 (W2~W3) |

**총 작업 시간**: 25-35h (직렬) / 12-18h (병렬). worker F+G는 5/7 dispatch 가능 (서버 idle). worker H는 5/22 미팅 직전 결과 ready.

---

## 의존성 그래프

```
                    ┌─────────────────┐
                    │   manager (본)  │
                    │  9 commit + push│
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
    [5/7 즉시]         [5/8 회의 후]       [W2~W3]
   ┌────┬────┬────┐  ┌────┬────┬────┐    ┌────┐
   │ A  │ D  │ F  │  │ B  │ C  │ E  │    │ H  │
   │PPT │fig │8M  │  │채림│교수│보고│    │멀티│
   │    │    │base│  │    │    │서  │    │테이│
   └────┴────┴────┘  └────┴────┴────┘    │블  │
        │                  │              │Toy │
        │              [5/22 미팅 후]      └────┘
        │                  │                │
        │              ┌───┴───┐            │
        │              │ B/C/E │            │
        │              │ final │            │
        │              └───────┘            │
        │                                   │
        └────[Worker G — 5/7 즉시 병렬]─────┘
                  (8M sel 5단계 확장)
```

---

## Dispatch 권장 순서

### 즉시 (5/7 12:00~)

| 우선순위 | Worker | 이유 |
|---|---|---|
| ★★★ | **F (8M baseline 3개)** | 짧은 측정 (3-4h), 서버 idle, 22 method 완성 narrative 강화 |
| ★★★ | **G (8M sel 5단계)** | F와 병렬, 5-7h, cross-scale 외적 타당성 보강 |
| ★★ | **A (PPT)** | 회의 + 5/22 미팅 자료 준비, D와 sync |
| ★ | **D (Phase 6/7 figure)** | A와 sync (Slide 4 footnote) |

병렬 진행 권장: 사용자가 4 세션 (또는 본 manager에서 background dispatch)

### 5/8 회의 후 (5/8 21:00~)

| 우선순위 | Worker | 이유 |
|---|---|---|
| ★★ | B / C | 자문 메일 final, 5/15 발송 |
| ★★ | E | 6/11 보고서 outline |
| ★★★ | **H (멀티 Toy 검증)** | 본 연구 마무리 단계, W2~W3 |

병렬 진행: 4 세션 (B / C / E / H)

### 5/22 미팅 직전 (5/19~5/21)

- F/G 결과 → master.md 갱신 → 5/22 미팅 자료
- H 결과 → Toy 검증 narrative → 지도교수 자문
- A deck → 미팅 직전 review 후 5/26 마감

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
- master.md narrative 변경 X (manager session 책임)
- contribution 7종 + Limitations 6종 일관 유지
- 한글 폰트 Apple SD Gothic Neo
- §5 의존성 다른 worker와 sync 시점 준수
- §7 본 worker가 만들지 말 것 list 준수

manager 세션 (5/7 12:05) 산출 핸드오프 9 commit + 8 worker handoff:
- 80f48d1 팀원공유 PDF 섹션 hierarchy + cell 정량 검증
- 984be3b 팀원공유 PDF 스타일 정정 (실험진행공유 톤)
- 592b022 팀원공유 RQ 진행 정리 (구어체)
- edbcfd3 팀원공유 자료 (PDF + Claude Design prompt)
- 1475814 5 worker handoff
- 8d079d3 narrative 일관성 보강
- fc7e147 chain archive
- 1267b8a 딥리뷰 보강 + handoff
- 74d6aea narrative 옵션 2 정직 reporting
```

---

## 충돌 / 중복 영역 + 통합 룰

| 영역 | 룰 |
|---|---|
| `master.md` | **manager 세션 단일 책임 (이미 commit 완료)**. Worker 변경 X. F/G/H 결과는 별도 파일 + commit message에 명시 |
| `slide outline` | **Worker A 단일 책임** (Academic v3 정정) |
| `자문 메일 채림석사` / `지도교수` | **Worker B / C 단일 책임** |
| `Phase 6/7 figure` | **Worker D 단일 책임** |
| `최종 보고서 outline` | **Worker E 단일 책임** |
| `8M baseline 3개` | **Worker F 단일 책임** |
| `8M sel 5단계` | **Worker G 단일 책임** (F와 sel/method 분리) |
| `멀티 테이블 Toy` | **Worker H 단일 책임** |

---

## 본 manager 세션 이후 deferred 작업

- **σ table reproducibility** (DEEP 1M / SIFT σ 재계산) — W2 권고
- **NMI / AMI metric 추가** (16 method real data) — W3
- **Real DEEP 1M / SIFT data ARI** (16 method × 2 ds) — W3
- **vector.c integration** — future work (5/6 patch memory leak)
- **Phase 6/7 root cause 정량** — future work
- **TPC-H 정식 multi-table benchmark** — future work (Toy 검증 후)

---

## 5/7 12:00 시점 ready 상태

5/8 회의 자료 모두 ready:
- ✅ 1page summary (commit 74d6aea)
- ✅ master.md 7+6 narrative
- ✅ slide outline 정정본
- ✅ 카톡 narrative 메시지 1/2/3
- ✅ 자문 메일 초안 2종 (5/7 갱신)
- ✅ 팀원 공유 PDF 세로형 (commit 80f48d1, 923K)
- ✅ 팀원 공유 PDF 가로형 16:9 (931K)
- ✅ 5/5 회의록 + RQ 재정립안

5/7 12:00 ~ 18:00 사이 진행 권장:
- ✓ Worker F + G dispatch (서버 측정)
- ✓ Worker A + D dispatch (PPT + figure)

5/8 19:00 회의 진입.

5/8 회의 후:
- ✓ Worker B + C + E + H dispatch
- ✓ 5/15 자문 발송 / 5/22 미팅 / 5/27 발표 / 6/11 보고서

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:05 KST
**다음 트리거**: 사용자가 worker 세션 dispatch (F+G+A+D 5/7 / B+C+E+H 5/8 후)
