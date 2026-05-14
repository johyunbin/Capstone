# 핸드오프 — 병렬 세션 (맥북) → 메인 세션, 2026-05-06 18:20 KST

> **이 문서가 메인 세션의 P6 진입점입니다.** 메인 세션 8M 보강 측정 끝나면 이 문서 읽고 다음 단계 결정.
> 작성: 병렬 세션 (조현빈 맥북, claude-opus-4-7) · 2026-05-06 18:20 KST

---

## ★ TL;DR (30초 안에 파악)

병렬 세션이 5/6 17:49~18:20 동안 다음 3개 산출:

1. **G. Distance-Shell** 측정 코드 — `experiments/code/rq3/online_weight/distance_shell.py` (350줄, P6-1 commit `c1b798a`)
2. **H. Importance Sampling** 측정 코드 (2x2 factorial) — `experiments/code/rq3/online_weight/importance_sampling.py` (317줄, P6-2 commit `ee6c24a`)
3. **rq3_analyze.py 분석 driver** — `experiments/code/local_analysis/rq3_analyze.py` (이 commit 에 포함, demo 검증 완료)

**메인 세션 다음 단계 (3 옵션)**:
- (A) **순차**: 8M 끝나면 G → 측정 + 분석 + 카톡 + commit → H 반복 (10h, narrative 매번 fresh)
- (B) **병렬-2개**: G + H 동시 launch (DEEP/SIFT 캐시 분리 conn → 충돌 없음), 끝나면 일괄 분석 (~6h, narrative 묶음)
- (C) **병렬-3개+**: G + H + 다른 누락 method (Hilbert, LSH 가 측정 미완료라면) 동시 (~6h, narrative 더 묶임)

**나의 추천: (B) G + H 병렬**. 서버 병렬 안전 (아래 §3 분석), 시간 ~4h 절약, 카톡 narrative 2건 묶기는 큰 부담 X.

---

## 1. 병렬 세션 산출물 상세

### 1.1 G. Distance-Shell — `experiments/code/rq3/online_weight/distance_shell.py`

**알고리즘 (per query)**:
1. cache flatten (KM20 cache 그대로 활용, 5/6 patterns 재사용)
2. pilot 50 uniform → 거리 quantile 5-shell 분할 (online, query-adaptive)
3. shell 별 σ_i = √(p(1-p)) (binary hit indicator 기반)
4. Neyman target_add ∝ N_i × σ_i (B_rem = 385 - 50 = 335 분배)
5. rejection-based sampling: pool 5×B_rem 에서 first target_add_i 채택
6. HT 결합: pilot + main 통합

**기대**: recovery_rate 25~50% (RQ재정립 §RQ3 사전 등록 — 단순 online 대비 KDE-pilot 의 절반 정도)

**서버 실행**:
```bash
scp experiments/code/rq3/online_weight/distance_shell.py capstone:/mnt/hdd0/home/capstone2026/cache/
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && nohup python3 -u distance_shell.py > distance_shell.log 2>&1 &"
```
산출: `cache/rq1/rq3_distance_shell.parquet` + `_meta.json`. 예상 측정 시간 ~4h (DEEP+SIFT, 5sel × 5seed × 100q × 2mode).

### 1.2 H. Importance Sampling — `experiments/code/rq3/online_weight/importance_sampling.py`

**알고리즘**:
- 비분할 (no partition), 단일 cache pool
- proposal q ∝ Gaussian KDE on pilot 거리 (Silverman bw)
- IS sample with replacement, weight = (1/n_cache) / q(x)
- 2x2 factorial: pilot_size {50, 200} × weight_clip {False, True} → 4 mode

**Mode 이름** (parquet 의 `mode` 컬럼):
- `is_p50_noclip`, `is_p50_clip`, `is_p200_noclip`, `is_p200_clip`
- 추가로 `--include-bernoulli` 시 `bernoulli` mode 포함 (default off, RQ3 다른 파일에 이미 RANDOM20 있음)

**기대**: 4 cell 모두 30~70% recovery. p200 가 p50 보다 정확 KDE → 약간 우세 가설. clip 은 variance 안정화.

**서버 실행**:
```bash
scp experiments/code/rq3/online_weight/importance_sampling.py capstone:/mnt/hdd0/home/capstone2026/cache/
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && nohup python3 -u importance_sampling.py --include-bernoulli > is.log 2>&1 &"
```
산출: `cache/rq1/rq3_importance_sampling.parquet`. 예상 ~6h (4 mode × 2 dataset × 5 sel × 5 seed × 100 query).

### 1.3 분석 driver — `experiments/code/local_analysis/rq3_analyze.py`

**용도**: parquet 회수 직후 자동 recovery rate + BH-FDR + narrative md skeleton 생성.

**사용** (각 method 측정 종료 후):
```bash
# 1) parquet 회수 (서버 → 로컬)
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_distance_shell.parquet \
    experiments/results/rq3_agnostic/

# 2) 분석 driver 실행
python3 experiments/code/local_analysis/rq3_analyze.py \
    --method distance_shell \
    --rq3-parquet experiments/results/rq3_agnostic/rq3_distance_shell.parquet
```

**산출** (자동, `experiments/results/rq3_agnostic/distance_shell/`):
- `distance_shell_summary.csv` — dataset×sel cell-level recovery rate + denom_pct + fall-back metric
- `distance_shell_significance.csv` — paired Wilcoxon BH-FDR (vs bernoulli, vs km20)
- `distance_shell_analysis.md` — 4-stage narrative skeleton + 결과 표 자동 채움 + 카톡 §3.2 메시지 (수동 narrative 부분만 placeholder, 머리만 빈칸)

**factorial method (importance_sampling)**: 4 cell 각각 분석:
```bash
for m in is_p50_noclip is_p50_clip is_p200_noclip is_p200_clip; do
  python3 experiments/code/local_analysis/rq3_analyze.py \
      --method $m \
      --rq3-parquet experiments/results/rq3_agnostic/rq3_importance_sampling.parquet
done
```

**Demo 검증 완료**: `python3 ... --demo --method demo_method` 통과 (synthetic 15000 rows, recovery 0.653, 5 cells BH-FDR 유의).

---

## 2. 메인 세션 진행 방안 (3 옵션)

> 8M 보강 측정 끝나는 시점 t_0. 5/8 19:00 마감 t_end. 가용 = t_end - t_0.

### 옵션 A — 완전 순차 (보수적, narrative 깔끔)

```
t_0 → G launch (4h) → G 측정 종료 → analyze G → 카톡 §3.2 G → commit G
   → H launch (6h) → H 측정 종료 → analyze H × 4 cell → 카톡 §3.2 H → commit H
   → 누락된 P3 hilbert / P4 LSH 측정 (이미 코드 존재 — git ls-files 확인 필요)
```

총 ≥10h (G+H 만), 추가로 hilbert/LSH 등 보강 시 ≥6h 더.

**장점**: 매 측정마다 카톡 narrative fresh, 박세은이 추적 쉬움
**단점**: 시간 더 걸림. 5/8 마감에 빠듯할 수 있음

### 옵션 B — G + H 병렬 (★ 추천)

```
t_0 → G + H 동시 launch (max(4h, 6h) = 6h)
   → 둘 다 종료 후 analyze 일괄 → 카톡 §3.2 묶음 (G + H 함께) → commit 묶음
   → 누락된 method 보강 (필요 시 또 병렬)
```

총 ~6h (G+H), 4h 절약.

**장점**: 시간 절약, 1회 narrative 정리
**단점**: 모니터링 복잡 (둘 중 하나 fail 시 발견 늦음 — `tail -f` 양쪽 다 봐야)

### 옵션 C — 3+ 병렬 (공격적)

P3 hilbert, P4 LSH 도 미측정이면 G + H + LSH (또는 + Hilbert) 동시 launch. 서버 자원 충분.

**리스크**: 파일 4개 동시 측정 시 PG 동시 conn ~80 (각 method 의 N_STRATA=20 fresh conn × 4 = 80). PG default `max_connections=100`. 한계 근접. 만약 PG 가 conn 거부하면 cache_cluster_samples 단계에서 exception → 측정 망가짐.

**추천하지 않음**. (B) 까지만.

---

## 3. 서버 병렬 가능성 정밀 분석

### 3.1 자원 측면

| 자원 | 단일 method | 2개 병렬 | 안전 한계 |
|------|------------|---------|----------|
| CPU | 1 core (numpy distance, single-thread) | 2 core | 서버 cores ≥ 4 |
| RAM | ~5 MB (cache 10000 × 96d × 4B) | ~10 MB | 충분 |
| PG conn (peak) | 20 (fresh per cluster) | 40 | max_connections 100 OK |
| Disk I/O | parquet write 한 번 (작음) | 2번 (작음) | 무관 |

**결론**: G + H 병렬 안전. 3+ 는 PG conn 한계 접근 → (B) 까지만 추천.

### 3.2 데이터 측면

- 각 method script 는 **읽기만** (PG SELECT), **쓰기 없음** → 충돌 없음
- 출력 parquet 파일명 다름 (`rq3_distance_shell.parquet` vs `rq3_importance_sampling.parquet`) → 덮어쓰기 없음
- numpy random seed 는 method 별 독립 → 결과 결정론

### 3.3 모니터링

병렬 시 양쪽 로그 동시 추적:
```bash
ssh capstone "tail -f /mnt/hdd0/home/capstone2026/cache/{distance_shell.log,is.log}"
```
또는 tmux split-pane.

처음 5분 후 cache load 단계 통과하는지 확인 (PG conn 누수 / OOM 위험은 cache 단계 — 통과하면 안전).

---

## 4. 카톡 §3.1 (시작) 메시지 — 사전 작성

서버 실험 launch 직전 톡방 발송용 (사용자가 시각·실제 가설 채워서 발송).

### 4.1 G 시작 메시지

```
[실험 #9 (G) 시작] HH:MM

실험명: RQ3 G. Distance-Shell (Online 5-shell + Neyman)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~4h

[기획 의도]
- query 시점에 pilot 50개로 거리 분포 추정 → 5개 동심원 shell 분할
- shell 별 σ_i 추정 후 Neyman 가중치 적용 (variance-optimal)
- 분포 사전 학습 없이 query-adaptive 한 단순 online 방법 — KDE-pilot (B) 의 단순 버전

[측정 목표 + 가설]
- H3-G: recovery_rate 25~50% (KM20 oracle 의 1/4~1/2 회수)
- 정량: paired Wilcoxon (vs bernoulli, vs km20) BH-FDR

[기대치]
- recovery_rate 25~50%

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query
- pilot=50, n_shells=5, sample_size 385

진행 후 결과 다시 공유드리겠습니다 🙏
```

### 4.2 H 시작 메시지 (병렬 시 G 와 함께 발송)

```
[실험 #11 (H) 시작] HH:MM

실험명: RQ3 H. Importance Sampling 비분할 (2x2 factorial)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~6h

[기획 의도]
- 분할 없이 (no partition) 단일 pool 위에서 importance weighting 만으로 차별화
- proposal q ∝ pilot 거리 KDE → query-near 강조
- weight = (1/n_cache) / q(x) 로 unbiased 보정
- 2x2 factorial: pilot_size {50, 200} × weight_clip {yes, no} = 4 cell

[측정 목표 + 가설]
- H3-H: recovery_rate 30~70% (4 cell 모두). pilot 200 > pilot 50 (KDE 정확도) 가설.
       weight_clip 은 variance 안정화 (약간 bias 도입)
- 정량: 2x2 factorial main effects (pilot 효과, clip 효과)

[기대치]
- 4 cell recovery_rate 30~70%, p200 > p50 ~5%

[측정 조건]
- DEEP/SIFT, 5 sel × 5 seed × 100 query × 4 mode (+ bernoulli 옵션)
- sample_size 385 고정

진행 후 결과 다시 공유드리겠습니다 🙏
```

### 4.3 G + H 병렬 시작 통합 메시지 (옵션 B 선택 시)

```
[실험 #9 G + #11 H 병렬 시작] HH:MM

서버 병렬 launch (CPU·RAM·PG conn 모두 안전 확인 — 핸드오프 §3 분석).
G: 4h, H: 6h → max 6h 후 일괄 분석 + 카톡 §3.2 묶음 발송 예정.

[G. Distance-Shell] H3-G: recovery_rate 25~50%
[H. Importance Sampling 2x2] H3-H: recovery_rate 30~70%

진행 후 두 실험 묶어 결과 공유드리겠습니다 🙏
```

---

## 5. P3-P5, P7, P8 연관 작업 점검

> 병렬 세션이 본 작업을 시작할 때 main 의 head 가 이미 P5 까지 진행됨 (commits 39cfc3a~ef5efcc, 1f468cf, 7008beb, 2b7cb57). 다음 항목은 **메인 세션이 직접 확인** 필요.

| Phase | 코드 commit | 측정 parquet | 분석 md | 비고 |
|-------|------------|-------------|--------|------|
| P1 분석 lib | ✅ 7008beb | — | — | recovery_rate.py + rq3_figures.py |
| P2 offline_simple (F + C) | ✅ 39cfc3a | ⚠️ 확인 필요 | ⚠️ 확인 필요 | minibatch + random_proj |
| P3 Hilbert (E) | ✅ da8563f | ⚠️ 확인 필요 | ⚠️ 확인 필요 | hilbert_curve.py |
| P4 LSH (A) | ✅ (이번 P6-2 commit 에 포함) ee6c24a | ❌ 미측정 추정 | ❌ | lsh.py + run_lsh.py 코드만 존재 |
| P5 KDE-pilot (B) | ✅ ef5efcc | ⚠️ 확인 필요 | ⚠️ 확인 필요 | kde_pilot.py monolithic |
| P6 Distance-Shell (G) | ✅ c1b798a (이번) | ❌ 미측정 | ❌ | 본 핸드오프 §1.1 |
| P6 Importance Sampling (H) | ✅ ee6c24a (이번) | ❌ 미측정 | ❌ | 본 핸드오프 §1.2 |
| P7 자문 초안 | ✅ 2b7cb57 | — | — | 비실험 |
| P8 8M 보강 | ⚠️ 진행 중 | ⚠️ 진행 중 | ⚠️ 진행 중 | 메인 세션 현재 작업 |

**메인 세션 첫 행동 권장**:
```bash
# 1. 로컬 parquet 존재 확인
ls experiments/results/rq3_agnostic/

# 2. 서버 cache 의 RQ3 parquet 확인
ssh capstone "ls -la /mnt/hdd0/home/capstone2026/cache/rq1/rq3_*.parquet 2>/dev/null"
```

**미측정 method 가 발견되면** (P2 ~ P5 중) 본 핸드오프 §2 의 옵션과 동일한 병렬/순차 결정 적용.

---

## 6. 메인 세션 권장 시나리오 (추천)

```
[t=0  ] 8M 측정 종료
[t=0  ] 본 핸드오프 읽고 §5 의 P2~P5 측정 상태 확인
[t=0  ] (A안: 순차) G launch — 4h
[t=4h ] G 종료 → analyze G → commit + push (narrative 일부 placeholder 채움)
[t=4h ] H launch — 6h
[t=10h] H 종료 → analyze H × 4 cell → commit + push
[t=10h] hilbert / LSH / kde_pilot 미측정 시 launch
... etc
[t=20h] 모두 측정 종료 → 통합 분석 (rq3_figures.py) → 정리 md 갱신 → 자문 초안 보강
[t=24h] 5/7 자정 시점 정리.md / figures 마감 — 5/8 19:00 회의 자료 준비 완료
```

★★★ 또는 옵션 B (G + H 병렬):

```
[t=0  ] G + H 동시 launch
[t=6h ] 둘 다 종료 → analyze 일괄 → commit 묶음
... (이후 동일)
```

---

## 7. 위험 요소

1. **PG conn 누수 재발 가능성**
   - 5/6 vector.c 패치 시 발견된 PG memory leak. 본 코드들은 모두 fresh conn per cluster 패턴 적용.
   - 그러나 cache load 단계 무한 hang 발생 시 → ssh 로 PG `pg_stat_activity` 확인, 좀비 conn kill.

2. **driver 의 column schema 가정**
   - `rq3_analyze.py` 는 `mode`, `dataset`, `selectivity`, `seed`, `query_id`, `q_error` 컬럼 가정.
   - 6/H 의 importance_sampling.py 는 추가로 `pilot_size`, `weight_clip` 가짐 — driver 는 이 컬럼들을 무시하고 mode 만 사용 (factorial 셀별로 method 이름 다르므로 OK).

3. **lsh.py 의 비정상 commit**
   - P6-2 commit `ee6c24a` 에 `lsh.py` 가 함께 포함됨 (의도치 않게). lsh.py 자체는 정상 P4 코드. commit message 와 내용 mismatch 만 이슈.
   - 이미 push 완료 → amend 권장 X. 별도 follow-up commit 으로 lsh.py 출처 명시 가능.

4. **caffeinate 휴면 방지**
   - 서버는 영향 없음. 로컬 분석 시 맥북 휴면 방지: `nohup caffeinate -dimsu >/dev/null 2>&1 & disown` (이미 적용 중인지 `pgrep -lf caffeinate` 로 확인).

---

## 8. 본 commit 의 산출

이 commit (병렬 세션 마무리) 는 다음을 포함:
- `experiments/code/local_analysis/rq3_analyze.py` (분석 driver, 신규)
- `_internal/handoff_P6_to_main_20260506_1820.md` (본 문서, 신규)

**P6 코드 commits** (이미 push 됨):
- `c1b798a` G distance_shell.py
- `ee6c24a` H importance_sampling.py (+ 의도치 않은 lsh.py)

---

**작성**: 조현빈 병렬 세션 (맥북) · 2026-05-06 18:20 KST
**다음 트리거**: 메인 세션 8M 보강 측정 종료 → 본 문서 진입 → §6 권장 시나리오로 RQ3 P6 (G+H) 진행.
