# 박광현 5/15 미팅 input 반영 — narrative v2 final update plan (preliminary)

> **작성**: 2026-05-15 16:40 KST · 박광현 미팅 (14:00) 후 2.7h · 박세은 정리 대기 중 (저녁쯤)
> **status**: preliminary (박세은 정리 받기 전), 박세은 + 임채림 input 종합 후 final plan 확정
> **base**: `_internal/records/kakaotalk/20260515_박광현미팅_방향재정립.md` 회의록 §2 매핑
> **target**: `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v2_draft.md` → v2 final

---

## 0. 본 plan 의 목적

박광현 미팅 (5/15 14:00) 영역 6 input 영역 본 narrative v2 draft 영역 영역 영역 update 영역 plan 영역 영역. 본 plan 영역 박세은 (+ 임채림) 정리 (저녁쯤 영역) 영역 영역 영역 영역 영역 final 확정 영역 영역 영역, 사용자 (조현빈) 영역 영역 영역 영역 영역 영역 영역 작업 영역 영역 영역 영역.

본 plan 영역 영역 5/27 발표 deck v7 update + 6/11 보고서 outline v4 영역 영역 영역 영역 영역 영역.

---

## 1. fix 영역 (확정, 박광현 input 영역 영역 영역 영역)

| narrative 영역 | line | 영역 |
|---|---|---|
| §1 출발점 (paper §V-B 영역 영역 영역 부정확) | 43-53 | paper §V-B Bernoulli 가정 영역 정량 측정 |
| §2 탐색 (8 paradigm 56 method) | 57-65 | paradigm 8 매핑 영역 영역 base |
| §3 폐기 (40 method 정직 분류) | 69-81 | audit 영역 영역 영역 evidence |
| §9 단독 대체 + 결합 batch baseline (paired 92.5%) | 409-484 | 영역 paper-grade evidence (Cliff's δ 63%, Hedges' g 56%) |
| §10 자원 효율 Pareto frontier (5 method) | 487-499 | fit_time 13× range (5s ~ 67s) align |
| §11 K granularity SF axis | 503-578 | method-dependent K best 패턴 + SF axis 영역 일관 |

위 6 영역 영역 영역 박광현 input 영역 영역 영역 영역 영역 영역 영역 ✓ align 확인 영역, **wording 변경 X**.

---

## 2. 변경 가능 영역 (박세은 정리 후 확정)

### 2.1 §0 main theme + paper §V-B anchor (line 13-39) — Input 2 영역 영역

**현재 wording**:
> "Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework"

**박광현 input 2**: "꼭 논문에 갇히기 보단 결과에 맞게 문제상황 재설정"

**가능한 변경 영역**:
| Option | wording 영역 | scope |
|---|---|---|
| A. paper §V-B anchor 유지 + "결과 기반 reframing" 영역 영역 영역 영역 | "Extending Exqutor's §V-B Framework with Distribution-aware Stratification" | minimal |
| B. paper §V-B anchor 완화 + 결과 기반 main theme | "Distribution-aware Cardinality Estimation for VAQ: A Measurement-driven Reframing of Adaptive Sampling" | medium |
| C. paper §V-B anchor 폐기 + 결과 기반 main theme | "Plan-robust Cardinality Estimation for VAQ across Distribution and Workload Variability" | large |

**박세은 정리 영역 영역 영역 영역**: paper §V-B anchor 영역 영역 영역 영역 영역 (박세은 9 자문 영역 영역 영역 paper §V-B anchor 영역 영역 영역) vs 박광현 의도 (paper frame 풀기) 영역 영역 영역.

**preliminary 권장**: Option A (paper §V-B anchor 유지 + 결과 기반 reframing 영역 영역) — paper exact 영역 영역 영역 evidence 영역 영역 영역 영역 영역 영역 영역 영역 영역.

---

### 2.2 §13 권장 설계 + §14.3 측정 plan (line 659-741, 766-791) — Input 4 영역 영역

**현재 wording**:
- §13.6.1 ~ §13.6.4: 시나리오 A/B/C/D (RAG / OLTP / Mobile / Distributed)
- §14.3: 측정 plan (Agent E + F + G + H)

**박광현 input 4**: "다이나믹 방식을 실제로 엔진에 넣어서 활용할 수 있는지 (더 좋은 성적)"

**가능한 변경 영역**:
| Option | scope |
|---|---|
| A. §13.7 영역 영역 "엔진 통합 POC" 영역 영역 영역 (~50 line) | PG/DuckDB integration sketch + 영역 영역 영역 영역 |
| B. §13.7 신규 section + §14.3.1 영역 영역 측정 plan (~100 line) | 측정 plan 영역 영역 영역 통합 plan |
| C. §13.7 + §14.3.1 + §15 영역 paper-grade publication path 영역 영역 (~200 line) | 영역 영역 paper-grade vision |

**preliminary 권장**: Option B (§13.7 신규 + §14.3.1 영역 영역) — 박광현 input 4 영역 영역 영역 영역 영역 영역 영역 영역.

**§13.7 신규 section draft outline**:
1. **PG/DuckDB integration POC scope** — Form 1 Component A+B+C+D 영역 영역 영역 PG planner 영역 영역 영역 영역 영역
2. **integration mode** — sampling routine (paper §V-B 영역 영역 영역) 영역 영역 swap-in
3. **measurement** — TPC-H VAQ Q1-Q22 영역 영역 영역 영역 영역 영역 plan 영역 영역
4. **measurement axis** — plan accuracy + plan robustness across table size + value range
5. **expected evidence** — 영역 영역 영역 영역 영역 영역 영역 영역 영역

---

### 2.3 §3 + §10 + §14.5 — Input 5 영역 영역 (adversarial)

**현재 wording**:
- §3 (line 69-81): 40 method 폐기 정직 분류
- §10 (line 487-499): Pareto frontier robustness
- §14.5 (line 808-826): paper-grade publication path

**박광현 input 5**: "uniform한거만 찾으면 공격받을 여지가 많음"

**가능한 변경 영역**:
| Option | scope |
|---|---|
| A. §10 + §14.5 영역 영역 adversarial 미커버 영역 명시 (~10 line) | minimal disclosure |
| B. §11.6 영역 영역 "adversarial scenario" 영역 영역 영역 영역 future work (~30 line) | adversarial workload 영역 영역 영역 plan |
| C. §14.8 신규 section 영역 adversarial measurement plan (~50 line) | adversarial workload generation + 측정 plan |

**preliminary 권장**: Option B (§11.6 영역 영역 future work 영역 영역) — 박광현 input 5 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역.

**§11.6 future work draft**:
- 본 연구 영역 9 cell 영역 모두 real-world dataset (DEEP / SIFT / SSN / YFCC / DEEP+WIKI)
- adversarial workload (e.g., uniform 영역 영역 영역 영역 영역 영역 영역, skew exploit, byzantine query distribution) 영역 영역 미측정
- Form 1 phase 2 영역 영역 또는 paper-grade publication 영역 영역 영역 adversarial measurement plan 영역 영역
- 우리 분포 인지 stratification 영역 영역 영역 영역 영역 영역 영역 영역 영역 paper §V-B Bernoulli 영역 영역 영역 영역 영역 evidence

---

### 2.4 §9.4 결합 진짜 가치 reformulate (line 454-458) — Input 6 영역 영역

**현재 wording**:
> "결합의 가치는 '더 큰 정확도' 가 아니라 method 선택의 안정성 + 측정 환경별 변동성 감소다"

**박광현 input 6**: "순서가 바뀌지 않을 정도라는 거도 사실 정의하기 쉽지 않음 (테이블 사이즈가 엄청 클때, 작을 때, 숫자 등 변수가 너무 많음)"

**가능한 변경 영역**:
| Option | wording 영역 |
|---|---|
| A. 영역 영역 wording 유지 + caveat 영역 영역 ("단, 안정성 영역 영역 영역 영역 영역 영역") | minimal |
| B. wording reformulate — "결합의 가치 = plan robustness across measurement environment variability" | medium |
| C. wording reformulate + 정량 metric 도입 — "결합 모드의 plan inversion rate (paper-grade definition)" | large |

**preliminary 권장**: Option B (wording reformulate 영역 영역 영역 영역 영역) — Option C 영역 영역 plan inversion rate 영역 영역 영역 영역 영역 영역 영역 영역 영역 paper-grade definition 영역 영역 영역 영역.

**§9.4 reformulate draft**:
> "그렇다면 결합은 의미가 없는가? 그렇지 않다. 결합 모드 영역 영역 92.5% 짝지어 우위 영역 'method 선택을 잘못해도 거의 항상 단독 대체보다는 낫다' 영역 영역 영역 plan robustness 영역 영역 영역. 9 측정 환경 (테이블 영역 영역, 영역 영역 영역, 영역 영역 영역, 영역 영역 변수) 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 결합 모드 영역 영역 영역 영역 영역 영역 영역. 즉 결합의 가치 영역 영역 영역 정확도 영역 영역, **measurement environment variability 영역 영역 영역 plan robustness** 영역."

---

## 3. 신규 section plan (variability)

### 3.1 §13.7 엔진 통합 POC section (Input 4 반영)
- **scope**: ~100 line, PG/DuckDB integration sketch + measurement plan
- **dependency**: 박세은 + 임채림 input 영역 영역 영역 영역 (PG/DuckDB 영역 영역 영역 영역 영역 영역 영역)
- **timeline**: 5/27 발표 영역 영역 영역 (D-12) — 박세은 정리 받은 후 진행

### 3.2 §14.8 adversarial future work section (Input 5 반영)
- **scope**: ~50 line, adversarial workload generation + measurement plan + future work
- **dependency**: 박세은 + 임채림 input 영역 영역 (adversarial 영역 영역 영역 영역 영역 영역 영역)
- **timeline**: 6/11 보고서 영역 영역 영역 (D-27) — 박세은 정리 받은 후 진행

---

## 4. 진행 영역 영역 (5/15 16:40 ~ 5/27 D-12)

### Phase 1 (박세은 정리 받은 후 ~ 5/16 영역)
1. fix/변경 영역 영역 확정 (박세은 + 임채림 input 종합)
2. §0 paper §V-B anchor 영역 영역 영역 영역 (Option A 또는 영역) 확정
3. §9.4 결합 진짜 가치 reformulate (Option B draft)
4. §11.6 adversarial future work 영역 영역 (Option B draft)

### Phase 2 (5/16 ~ 5/20 영역)
1. §13.7 엔진 통합 POC section 영역 영역 (Option B, ~100 line)
2. 5/27 발표 deck v7 update — 변경 영역 영역 영역
3. 5/27 발표 deck v7 영역 영역 영역 영역 (박세은 + 강재현 영역 영역)

### Phase 3 (5/20 ~ 5/27 D-7)
1. fittime 측정 90 file 완료 시 §10 영역 영역 정량 source 영역 (preliminary 영역 영역 final 영역)
2. 6/11 보고서 outline v4 update — 변경 영역 영역 영역
3. 5/27 발표 D-Day rehearsal

### Phase 4 (5/27 ~ 6/11 D-15)
1. §14.8 adversarial future work section 영역 영역 (Option B, ~50 line)
2. 6/11 보고서 본문 작성 + PDF 영역 영역

---

## 5. risk + mitigation

### 5.1 risk: 박세은 정리 영역 영역 박광현 input 영역 영역 영역 영역 영역
- mitigation: 본 plan 영역 preliminary 영역 영역 영역 영역 — 박세은 정리 받은 후 fix/변경 영역 final 확정

### 5.2 risk: 5/27 영역 영역 narrative 변경 영역 영역 영역 영역 영역 영역
- mitigation: Phase 1 (fix/변경 확정) 영역 5/16 영역 영역 — 5/17 ~ 5/20 영역 deck update + 영역 영역 영역 영역 영역

### 5.3 risk: 박광현 본업 영역 align (RELOAD / CANNON / DFLOP) 영역 영역 영역 영역
- mitigation: §14.7 영역 영역 영역 영역 영역 영역 — 박세은 + 임채림 input 영역 영역 정확 영역 영역 영역 영역

---

작성: 2026-05-15 16:40 KST · 박광현 5/15 미팅 input 6 영역 영역 narrative v2 draft update plan (preliminary) · 박세은 + 임채림 정리 받은 후 final 확정
