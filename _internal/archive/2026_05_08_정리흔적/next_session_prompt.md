# Next Session — 2026-05-06 17:30 KST → 새 세션에서 RQ3 시작

> **이 문서가 다음 세션의 진입점입니다. 새 Claude 세션 열면 이 파일부터 읽으세요.**
> 이번 세션은 RQ1+RQ2 마감, RQ3 (7-way distribution-agnostic) 는 깨끗한 context 로 새 세션에서.

---

## ★ TL;DR (30초 안에 파악)

- **현재 단계**: 5/6 W1 sprint 진행 중. **RQ1 + RQ2 모두 완료** (실험 #1, #2+#3, #4).
- **즉시 다음**: **RQ3 7개 실험 (#5~#11)** — 7-way distribution-agnostic 비교, ~28h 분량.
- **마감**: **5/8 (금) 19:00 — 비대면 회의 + 실험 마감, D-2**.
- **카톡 공유**: 각 실험 시작·종료 시마다 톡방에 §3.1 (시작) + §3.2 (완료) 발송.

---

## 1. 어디까지 했나 (5/6 W1 sprint 결과)

### 1.1 실험 #1 — RQ1 SIFT × SYSTEM(block) baseline ✅ (commit cce2246)

- 측정 28.6초, 2500 rows. 4단계 narrative 완료.
- **H1 정량 입증**: SIFT(skew) 의 SYSTEM-BERN 격차가 모든 sel 에서 DEEP(normal) 보다 큼.
  - s=0.01: SIFT +10.27% vs DEEP +4.66% (격차 +5.61%p)
  - s=0.05: SIFT +17.32% vs DEEP +12.61% (격차 +4.71%p)
  - paired Wilcoxon p ≤ 1e-4 ~ 1e-49 (BH-FDR 보정 후에도 robust)
- 부수: q_error sanity 의심 해소 (PG setseed 정상, discrete + low-variance 자연스러운 결과)
- 산출: `experiments/results/rq1_motivation/sift_rq1_2026_05_06/`

### 1.2 실험 #2+#3 — RQ2 Allocation method 비교 ✅ (commit 9d08e82)

- 5 mode (BERN/Equal/Proportional/Neyman/Anti-Neyman) × DEEP/SIFT × 5 sel × 5 seed × 100 query = 25,000 rows.
- 측정 17.1초 (Python 시뮬레이션, vector.c 패치 buggy 라 우회).
- **모든 stratified > BERN** (DEEP -1.3~-7.0%, SIFT -3.7~-10.5%, p ≤ 1e-7 ~ 1e-50).
- **Neyman vs Equal — 부분 입증**: SIFT × 좁은 sel 에서만 유의 (s=0.01 -11.9%, p_BH=0.024).
- **Anti-Neyman vs Proportional — 반증**: 모든 case 통계적 유의 X. σ_i 신호가 N_i 보다 약함.
- **새 발견**: SIFT × Equal × s=0.01 anomaly (1.85 > BERN 1.69) — cluster 비균질성에서 Equal 한계.
- 산출: `experiments/results/rq2_aware/2026_05_06_alloc/rq2_alloc.parquet`

### 1.3 실험 #4 — RQ2 Sample size sensitivity ✅ (commit 0f48f18)

- 4 ssize × 2 dataset × 5 sel (보강) × 5 seed × 100 query × 2 mode = 40,000 rows.
- 측정 22.7초 + 28.4초 = 51.1초.
- **H2-S 단조 감소 — 미입증**: DEEP s=0.05 만 부분 단조, 다른 case non-monotonic.
- **새 발견**: KM20 의 sample_size robustness — 모든 40 조합에서 KM20 > BERN 일관 (Δ% -1.09 ~ -13.50%).
- 산출: `rq2_size_sensitivity_5sel.parquet`

### 1.4 보강 작업 (BH-FDR + figures + DEEP query difficulty) ✅ (이번 세션 마지막 commit)

- BH-FDR 다중 비교 보정 — 모든 핵심 결과 robust 유지.
- 5 figures PNG: `experiments/figures/rq1_rq2_w1_sprint/`.
- DEEP query difficulty 분석 — 박세은 질문 ("DEEP system 절대값 큼") 강화 답변. SIFT q_error>2 query 39.4% vs DEEP 9%.

---

## 2. ★ 즉시 해야 할 작업 — RQ3 #5~#11 (7-way distribution-agnostic)

### 2.1 핵심 metric — Recovery Rate

```
recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)
```

- 1.0 → KM20 oracle 수준 회수
- 0.0 → RANDOM20 (공간 인식 없음) 수준
- 분모 붕괴 (|KM20 − RANDOM20| ≤ 1%p) 시 절대 Q-error (방법X − BERN) 으로 fall back

### 2.2 7-way 실험 — 우선순위 순

| # | 실험 | 패러다임 | 시간 | 우선순위 | 기대 recovery |
|---|------|---------|------|---------|--------|
| #8 | F. MiniBatch K-means | Offline (학습 1~5%) | ~1h | ★★★ 1순위 | 75~95% |
| #5 | C. Random Projection | Offline (단순 하한) | ~2h | ★★ 2순위 | 10~40% |
| #7 | E. Hilbert Curve | Offline (결정론) | ~4h | ★★ 3순위 | 20~60% (contribution 후보) |
| #6 | A. LSH | Offline (확률) | ~4h | ★ 4순위 | 30~60% |
| #10 | B. KDE-pilot | Online (정교) | ~6h | ★ 5순위 | 50~80% (이론 상한) |
| #9 | G. Distance-Shell | Online (단순) | ~4h | ★ 6순위 | 25~50% |
| #11 | H. Importance Sampling | 비분할 (가중치) | ~6h | ★ 7순위 (2x2 factorial) | 30~70% |

총 ~27h. 5/8 19:00 까지 ~50h 가용. RQ3 1~3 (F, C, E) 절대 사수, 4~7 가능한 선까지.

### 2.3 측정 패턴 — 이미 검증됨

기존 Python 시뮬레이션 패턴 (`experiments/code/rq2/rq2_alloc_python.py`) 그대로 활용:
1. cluster 별 LIMIT 500 sample 캐시 (fresh conn per cluster, 누수 회피)
2. allocation 결정 (각 방법 X 의 stratum_id 정의)
3. HT estimator (cluster 별 random sample + weighted sum)

각 방법 (F/C/E/A/B/G/H) 마다:
- stratum_id 부여 알고리즘 다름 (KM 대신 MiniBatch / RandProj / Hilbert / LSH / KDE / 거리 shell / weight)
- 측정 stage 는 동일 (cluster sample 캐시 + Python estimation)

→ **방법별 ~30 분~1h** (사전 학습 + stratum_id 부여 + 측정 + 분석).

---

## 3. ★ 카톡 톡방 공유 템플릿

### 3.1 실험 시작 시 (시작 직전)

```
[실험 #N 시작] HH:MM

실험명: ___
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~Nh

[기획 의도]
- ___

[측정 목표 + 가설]
- H3-X: ___
- 정량: ___

[기대치]
- recovery_rate ___%

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- sample_size 385 고정

진행 후 결과 다시 공유드리겠습니다 🙏
```

### 3.2 실험 종료 시 (4단계 narrative)

```
[실험 #N 완료] HH:MM (소요 ~Nh)

실험명: ___
산출 위치: ___

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — ...
(b) 가설 — H3-X: ...
(c) 예상 결과 — recovery_rate ___%
(d) 실제 결과 — ___ + 가설 확인 / 반증 + 예상 일치 / 불일치

═══ 의의 + 다음 ═══
- ___ narrative 강화
- 다음 실험 #N+1 진행

자동 git commit + push 완료
```

---

## 4. 작업 흐름 (반복 절차)

```
[실험 #N 시작]
  ① 카톡 §3.1 메시지 출력 (사용자 톡방 발송)
  ② Python 시뮬레이션 — stratum_id 부여 알고리즘 작성
  ③ scp 서버 → 측정 (~30분~1h)

[측정 진행]
  ④ 결과 raw 데이터 회수 (parquet + meta json)

[실험 #N 완료]
  ⑤ Recovery rate + paired Wilcoxon 분석
  ⑥ 4단계 narrative md 자동 생성
  ⑦ 카톡 §3.2 메시지 출력
  ⑧ RQ1_RQ2 정리.md (또는 RQ3 정리.md) 갱신

[git commit + push] (산출물 보존)
  ⑨ git add experiments/results/...
  ⑩ git commit -m "experiment #N: ___"
  ⑪ git push origin main

[실험 #N+1 시작] ... 반복
```

---

## 5. 주의사항 (이번 세션에서 발견된 함정)

### 5.1 vector.c 패치 시도 → buggy → BERN 원복 + Python 시뮬레이션 사용 ★

5/6 vector.c Neyman/Anti-Neyman 패치 시도 시:
- 빌드 OK, GUC 설정 OK
- 그러나 stratified 모드 측정 시 **PG memory leak + invalid memory alloc request**
- BERN 빌드로 원복 (md5 7cdc... → 4c947f...) 후 Python 시뮬레이션으로 우회
- vector.c 통합은 future work

→ **RQ3 도 Python 시뮬레이션으로 측정**. vector.c 안 건드림. 더 안전.

### 5.2 PG vector::real[] cast 메모리 누수

여러 cluster 의 vector 를 한 connection 으로 fetch 시 **누적 메모리 leak**. 해결: **cluster 마다 fresh connection** (`with psycopg.connect(...) as c:` 패턴).

LIMIT 500 까지는 단일 conn OK, 그 이상에서 unstable. RQ3 의 사전 학습은 작은 sample 로.

### 5.3 caffeinate 휴면 방지 + sudo pmset -c sleep 0

이번 세션에서 적용 완료. AC 전원 유지하면 휴면 안 들어감. 새 세션 시작 시:
```bash
pgrep -lf caffeinate    # caffeinate 살아있는지 확인
nohup caffeinate -dimsu >/dev/null 2>&1 & disown    # 없으면 다시 띄움
```

### 5.4 query pool 위치 (서버)

- DEEP: `/mnt/hdd0/home/capstone2026/cache/rq1/query_pool.parquet` + `query_selectivity.parquet`
- SIFT: `/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_sift.parquet` + `query_selectivity_sift_v2.parquet`

### 5.5 KM20 stratum 데이터 (서버)

- DEEP: `partsupp_deep_10_subset_1m` (stratum_id smallint, indexed)
- SIFT: `customer_sift_10_phase7_noidx_subset` (stratum_id smallint, indexed)

RQ3 의 다른 방법 (F/C/E/A 등) 은 stratum_id 를 다른 알고리즘으로 재정의 → 새 컬럼 (예: `stratum_id_minibatch`) 또는 in-memory 만 (Python 측정).

---

## 6. 자료 위치 맵 (정확히)

### 6.1 설계·계획
- `plans/RQ재정립_20260505_2122.md` — RQ 구조 v6 (5/5 회의 채택, 변경 없음)
- `_internal/실험_진행_프롬프트_템플릿.md` — 11종 시작/완료 프롬프트 (#5~#11 부분 참조)

### 6.2 측정 결과 (5/6 W1 sprint)
- `experiments/results/rq1_motivation/sift_rq1_2026_05_06/` — RQ1 #1
- `experiments/results/rq2_aware/2026_05_06_alloc/` — RQ2 #2+#3, #4, BH-FDR 분석
- `experiments/figures/rq1_rq2_w1_sprint/` — 5 PNG figures
- `experiments/results/RQ1_RQ2 실험 결과 정리.md` — 통합 정리 (W1 sprint 갱신)

### 6.3 측정 코드
- `experiments/code/rq1/sift_rq1_native.py` — RQ1 SIFT 측정
- `experiments/code/rq2/compute_stratum_sigma.py` — σ_i 사전 계산
- `experiments/code/rq2/rq2_alloc_python.py` — RQ2 5-mode allocation
- `experiments/code/rq2/rq2_size_sensitivity.py` — RQ2 sample size sensitivity
- (RQ3 측정 코드는 `experiments/code/rq3/` 에 새로 작성 예정)

### 6.4 서버
- 호스트: `165.132.140.240` (capstone2026, ssh capstone)
- 작업 디렉토리: `/mnt/hdd0/home/capstone2026`
- PG 포트: 55436 (Exqutor, vector module)
- DB/USER: wns41559
- 캐시: `/mnt/hdd0/home/capstone2026/cache/rq1/` (RQ1/RQ2 산출), `/mnt/hdd0/home/capstone2026/cache/` (스크립트)

---

## 7. 마감 카운트다운

| 마감 | 산출물 | 비고 |
|------|--------|------|
| **5/8 (금) 19:00** | **★ RQ1+RQ2+RQ3 실험 마감 + 비대면 회의** | **D-2** |
| ~5/15 | 자문 요청 발송 (채림 석사 + 교수님) | D-9 |
| ~5/21 | 발표자료 초안 마감 | D-15 |
| 5/22 | 교수님 미팅 | D-16 |
| 5/26 | 발표자료 최종 마감 | D-20 |
| **5/27** | **★ 최종 발표** | **D-21** |
| 5/28 | 전시회 자료 마감 | D-22 |
| **6/11** | **★ 최종 보고서** | **D-36** |

---

## 8. 새 세션 시작 절차

```bash
cd ~/Capstone
git pull --no-rebase origin main    # 최신 동기화 (이번 세션 commit 까지)
claude                                # 새 세션 시작
```

세션 시작 시 SessionStart hook 자동 출력. 첫 메시지 권장:

```
@_internal/next_session_prompt.md 읽고 RQ3 진행하자.
실험 #8 (F. MiniBatch K-means) 부터 우선순위 순으로 7개 자동 진행.
```

이러면 이 문서가 컨텍스트에 로드되고 §2 우선순위 그대로 진입 가능.

---

## 9. 박세은 회신 / 의문 사항 (이번 세션 처리 완료)

- 16:47 박세은: "DEEP system vs SIFT system 의 q-error 직접 비교는 불가능?"
  → 답변: 절대값 비교 가능하나 query pool / sampling fraction / q_error 비대칭 noise 영향 큼.
    Δ% (격차%) 가 cross-dataset 비교에 안정적. 모든 sel 에서 SIFT > DEEP 일관 (H1 입증).
  → 추가: DEEP 의 q_error > 2 query 비율 9% vs SIFT 39.4% — 본질적 difficulty 는 SIFT 가 큼.
  → 답변 카톡 출력 완료, narrative 보강 완료 (정리.md 의 "W1 Sprint 보강 작업" 섹션).

---

**작성**: 조현빈 · 2026-05-06 17:32 KST · 이번 세션 마감 직전
**다음 트리거**: 새 Claude 세션 시작 → 본 파일 진입 → RQ3 #8 (F. MiniBatch K-means) 부터.
