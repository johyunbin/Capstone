# Next Session — 2026-05-06 16:04 KST → 맥북에서 W1 sprint 이어가기

> **이 문서가 다음 세션의 진입점입니다. 맥북에서 새 Claude 세션 열면 이 파일부터 읽으세요.**
> 맥미니는 Trading 등 다른 작업으로 분리, 캡스톤은 맥북에서 단독 진행.

---

## ★ TL;DR (30초 안에 파악)

- **현재 단계**: 5/6 W1 sprint 진행 중. RQ1 SIFT × BERN 측정 완료 (5/6 11:51 측정).
- **즉시 다음**: **실험 #1 — SIFT × SYSTEM(block) baseline 측정** (~50 min, 자취방 이동 후 진행).
- **마감**: **5/8 (금) 19:00 — 비대면 회의 + 실험 마감, D-2**.
- **남은 실험**: 11종 중 1종 완료, 10종 (#1 SYSTEM + #2~#11) 남음. 약 28h 분량.
- **카톡 공유**: 각 실험 시작·종료 시마다 톡방에 §3 템플릿대로 발송.

---

## 1. 어디까지 했나 (5/6 오전 ~ 16:04)

### 1.1 5/5 (화) 비대면 회의 → RQ 전면 재정립
- 박세은 팀장 제안 채택. 새 RQ 구조:
  - **RQ1**: 기존 방식이 skew 에서 얼마나 나쁜가 (block/row × normal/skew 2x2)
  - **RQ2**: 분포 알 때 최적 (KM20 + Proportional/Neyman/Anti-Neyman)
  - **RQ3**: 분포 모를 때 최적 (7-way, 3 패러다임, Recovery Rate)
- 회의록: `_internal/records/kakaotalk/20260505_RQ재정립_회의.md`
- 설계안 v6: `plans/RQ재정립_20260505_2122.md`

### 1.2 5/6 오전 — 회의 시간 확정 + sprint 시작 안내 (카톡)
- 5/8 (금) **19:00** 비대면 회의 시간 확정 (강재현 제안 → 전원 동의).
- 회의록: `_internal/records/kakaotalk/20260506_W1_sprint_시작_카톡.md`

### 1.3 5/6 오전~오후 (맥북 11:51~12:23) — RQ1 SIFT × BERN 측정 완료
1. ✅ 기존 SIFT 데이터 audit (BERN s=0.5 단일점 → 5sel × 5seed 풀그리드 필요 확정)
2. ✅ SIFT D_target s∈{0.01, 0.05, 0.10, 0.30, 0.50} 5점 풀그리드 계산
   - 산출: `experiments/results/rq1_motivation/sift_rq1_2026_05_06/query_selectivity_sift_v2.parquet` (500 rows)
3. ✅ SIFT measurement 스크립트 — `experiments/code/rq1/sift_rq1_native.py` (multi-seed × multi-sel × 두 모드 공용)
4. ✅ D_target 보강 — `experiments/code/rq1/sift_dtarget_extend.py`
5. ✅ **SIFT × BERN 측정 완료** — 5sel × 5seed × 100q = 2500 rows
   - 산출: `experiments/results/rq1_motivation/sift_rq1_2026_05_06/sift_rq1_bernoulli.parquet` + meta json
   - 측정 시간: 1821s (≈30 min) on PG 55436
   - 핵심 수치 (median q_error, mean across 5 seed):
     | sel | mean | std |
     |-----|------|-----|
     | 0.01 | 1.4411 | 0.0000 ★ sanity 의심 (5seed 동일) |
     | 0.05 | 1.1966 | 0.0095 |
     | 0.10 | 1.1493 | 0.0263 |
     | 0.30 | 1.0684 | 0.0118 |
     | 0.50 | 1.0589 | 0.0071 |
6. ✅ 팀원 공유 문서 — `_internal/records/kakaotalk/20260506_W1_sprint_팀원공유_프롬프트.md`

### 1.4 5/6 16:00~16:04 — 맥미니 → 맥북 환경 이전
- 맥미니에서 5/6 카톡 회의록 commit + push (HEAD: `7d43d67`).
- 맥북 git pull 완료 + .claude/Capstone rsync 동기화 완료.
- 맥미니는 Trading 등 분리 작업으로 매듭. **여기부터 맥북.**

### 1.5 서버 상태 (165.132.140.240, capstone2026)
- PG 55436 (Exqutor) 가동 중
- `vector.c md5 = 7cdc780cff5ae1357bc243064a1167b8` — **현재 BERN 컴파일 상태** (L940: `TABLESAMPLE BERNOULLI(%f)`)
- `vector.so md5 = 4c947fc81bfcf6e915a5971d98e915de`
- 작업 디렉토리: `/mnt/hdd0/home/capstone2026/cache/`
- 백업 `vector.c.bak.20260414_1934_before_bernoulli` 는 SYSTEM + 구버전 (stratified 코드 없음 — **그대로 쓰지 말 것**)

---

## 2. ★ 즉시 해야 할 작업 — 실험 #1 (SIFT × SYSTEM block baseline, ~50 min)

### 2.1 왜 이게 1순위인가
- RQ1 의 2x2 표 (DEEP/SIFT × SYSTEM/BERN) 4 cell 중 **마지막 1 cell**.
- 박세은 팀장 제기 동기 ("normal에선 잘 되던 random이 skew에선 안 됐다") 의 정량 증거.
- 가장 짧음, 끝나면 RQ1 narrative 즉시 완성.

### 2.2 진행 절차 (서버 명령 그대로 복붙)

> **계획**: 단일 sed 패치로 L940 BERNOULLI → SYSTEM. 빌드 후 같은 측정 스크립트 (`sift_rq1_native.py`) 를 `--mode system` 으로 실행. 끝나고 BERN 복원 (다음 RQ2/RQ3 실험 baseline 보호).

```bash
# step 0: 톡방에 §3.1 시작 메시지 발송 ★ (아래 §3.1 템플릿 참조)

# step 1: SSH (맥북에서)
ssh capstone

# step 2: 현재 BERN 빌드 백업
cd /mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector/src
cp vector.c vector.c.bak.20260506_BERN_compiled

# step 3: SYSTEM 패치 (single line)
sed -i 's|TABLESAMPLE BERNOULLI(%f)|TABLESAMPLE SYSTEM(%f)|' vector.c
grep -n 'TABLESAMPLE' vector.c    # 확인: L940 SYSTEM

# step 4: 빌드
cd /mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector
PG_BIN=/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin
make PG_CONFIG=$PG_BIN/pg_config install

# step 5: PG restart
$PG_BIN/pg_ctl restart -D /mnt/hdd0/home/capstone2026/exqutor_sf10 \
  -l /mnt/hdd0/home/capstone2026/log/postgres_exqutor.log

# step 6: 검증 (Sampling Method: 'system' 인지 EXPLAIN 으로 확인)
$PG_BIN/psql -h /tmp -p 55436 -U wns41559 -d wns41559 -c "SHOW vector.sampling_method"

# step 7: SYSTEM 측정 (~30 min) — python3 -u 로 unbuffered ★
# (5/6 오전 buffered 로 30분간 진행 안보임 문제 있었음 — 반드시 -u)
cd /mnt/hdd0/home/capstone2026/cache
python3 -u sift_rq1_native.py --mode system 2>&1 | tee /tmp/sift_rq1_system.log

# step 8: BERN 복원 ★ 잊지 말 것 (다음 실험 위해)
cd /mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector/src
cp vector.c.bak.20260506_BERN_compiled vector.c
grep -n 'TABLESAMPLE' vector.c    # 확인: L940 BERNOULLI
md5sum vector.c                   # 7cdc780cff5ae1357bc243064a1167b8 일치 확인
cd ..
make PG_CONFIG=$PG_BIN/pg_config install
$PG_BIN/pg_ctl restart -D /mnt/hdd0/home/capstone2026/exqutor_sf10 \
  -l /mnt/hdd0/home/capstone2026/log/postgres_exqutor.log

# step 9: 결과 회수 (맥북 로컬로)
exit
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/sift_rq1_system.parquet \
    ~/Capstone/experiments/results/rq1_motivation/sift_rq1_2026_05_06/
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/sift_rq1_system_meta.json \
    ~/Capstone/experiments/results/rq1_motivation/sift_rq1_2026_05_06/
```

### 2.3 측정 후 — 4단계 브리핑 (~30 min, Claude 가 자동)

Claude Code 새 세션에 복붙:
```
[실험 #1 완료] SIFT × SYSTEM/BERN RQ1 측정 결과 정리해줘.
raw: experiments/results/rq1_motivation/sift_rq1_2026_05_06/
양식: _internal/실험_진행_프롬프트_템플릿.md 공통 완료 프롬프트 (4단계: 동기·가설·예상·실제).

핵심 수치 (직접 본 것):
  - SIFT × SYSTEM: s=0.01 ___, s=0.05 ___, s=0.10 ___, s=0.30 ___, s=0.50 ___
  - SIFT × BERN (5/6 측정): s=0.01 1.4411, s=0.05 1.1966, s=0.10 1.1493, s=0.30 1.0684, s=0.50 1.0589
  - DEEP × SYSTEM (phase4): s=0.01 1.694, s=0.30 1.242
  - DEEP × BERN (phase4): s=0.01 1.618, s=0.30 1.089

분석 요청:
  - SIFT BERN vs SYSTEM paired Wilcoxon (selectivity 별)
  - mean ± std 표 + p-value
  - DEEP 1M 4 cell 과 cross-dataset 2x2 비교
  - Selectivity Gradient narrative 강화
```

### 2.4 톡방 공유 → §3.2 완료 메시지 발송 → git commit + push

```bash
cd ~/Capstone
git add experiments/results/rq1_motivation/sift_rq1_2026_05_06/sift_rq1_system.* \
        experiments/results/RQ1_RQ2*.md
git commit -m "experiment #1: SIFT × SYSTEM(block) baseline — RQ1 2x2 cell 완성"
git push origin main
```

### 2.5 (선택) 팀원 공유 문서 발송
- `_internal/records/kakaotalk/20260506_W1_sprint_팀원공유_프롬프트.md` §0 텍스트 확인 후 톡방 발송
- 노션 캡스톤 일정 DB 에 W1 8 항목 + 마감 추가

---

## 3. ★ 카톡 톡방 공유 템플릿 (실험 시작/종료 시 그대로 복붙)

### 3.1 실험 시작 시 톡방 메시지 (시작 직전 발송)

```
[실험 #1 시작] HH:MM

실험명: RQ1 SIFT × SYSTEM(block) baseline
RQ: RQ1 (기존 방식이 skew 에서 얼마나 나쁜가)
예상 시간: ~50 min (빌드 변경 5분 + 측정 30분 + 복원 5분 + 분석 10분)

[기획 의도]
- 박세은 팀장 제기 의문: "Normal vs Skew BERN baseline 직접 비교 부재".
- 4/30 중간발표는 KM20 vs BERN 비교에만 집중 → 데이터 분포 자체가
  random sampling 정확도에 미치는 영향을 정량화 못 했음.
- 박세은 동기 ("normal에선 잘 되던 random이 skew에선 안 됐다") 의 정량 증거가 필요.

[측정 목표]
- RQ1 의 2x2 표 (DEEP/SIFT × SYSTEM/BERN) 마지막 cell 완성.
- H1: skew 데이터일수록 random sampling 의 q-error 가 악화되며,
       block 단위가 row 단위보다 편향이 더 심하다.

[기대치]
- SIFT SYSTEM > SIFT BERN > DEEP SYSTEM > DEEP BERN 순으로 q_error 클 것.
- SIFT 안에서 SYSTEM-BERN 격차 > DEEP 안 격차 (skew 가 block 편향 증폭).
- 좁은 selectivity (s=1%) 에서 격차 가장 큼.

[측정 조건]
- 데이터셋: SIFT 1.5M
- 샘플링: TABLESAMPLE SYSTEM (block 단위)
- selectivity: 1%, 5%, 10%, 30%, 50% (5점)
- seed: 5 / query: 100 / sample_size: 385

진행 후 결과 다시 공유드리겠습니다 🙏
```

### 3.2 실험 종료 시 톡방 메시지 (4단계 narrative)

```
[실험 #1 완료] HH:MM (소요 ~Nh)

실험명: RQ1 SIFT × SYSTEM(block) baseline
산출 위치: experiments/results/rq1_motivation/sift_rq1_2026_05_06/sift_rq1_system.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══

(a) 동기 — 왜 이 실험을 시작했나
   · 박세은 팀장이 "Normal vs Skew BERN baseline 직접 비교 부재" 의문 제기
   · 4/30 중간발표는 KM20 vs BERN 에만 집중 → 데이터 분포 자체의 영향 정량화 못함
   · "normal에선 잘 되던 random이 skew에선 안 됐다"의 정량 증거가 필요했음

(b) 가설 — 확인하고자 한 것
   · H1: skew 데이터일수록 random sampling q-error 가 악화되며, block > row 편향
   · 정량: SIFT SYSTEM 의 q_error mean / median, paired Wilcoxon p-value vs BERN

(c) 예상 결과 — 진행 전 기대값
   · SIFT SYSTEM > SIFT BERN > DEEP SYSTEM > DEEP BERN 순
   · SIFT 안 SYSTEM-BERN 격차 > DEEP 안 격차 (skew 가 block 편향 증폭)
   · 좁은 selectivity (s=1%) 에서 격차 가장 큼

(d) 실제 결과 — 측정값
   · ___ (raw 수치 + paired Wilcoxon p-value)
   · 가설 확인 / 반증 (어느 쪽인지)
   · 예상 일치 / 불일치 — "왜 그런지"

═══ 의의 + 다음 ═══
- RQ1 narrative 완성 — 박세은 의문 1번 정량 증거 확보
- 발표/보고서 RQ1 섹션 / Selectivity Gradient narrative 강화
- 다음 실험 #2 (Neyman Allocation, RQ2 핵심) 진행

의문/수정 사항 있으시면 카톡 부탁드려요!
```

### 3.3 모든 실험 완료 시 (5/8 19:00 회의 직전)

`_internal/실험_진행_프롬프트_템플릿.md` 의 **마지막 "최종 종합 프롬프트"** 사용 — Claude 가 11종 통합 narrative + RQ별 4단계 + 발표/보고서 흐름 + 자문 요청 초안까지 일괄 생성.

---

## 4. 실험 #2 이후 (#2~#11) — 우선순위 순

| # | 실험 | RQ | 시간 | 우선순위 | 시작 프롬프트 |
|---|------|----|----|---------|---|
| #2 | Neyman Allocation | RQ2 | ~4h | ★ 필수 | 템플릿 §#2 |
| #3 | Anti-Neyman ablation | RQ2 | ~포함 | ★ 필수 (#2와 묶음) | 템플릿 §#3 |
| #4 | Sample size sensitivity | RQ2 | ~3h | ★ 필수 | 템플릿 §#4 |
| #8 | F. MiniBatch K-means | RQ3 | ~1h | RQ3 1순위 (효과 가장 큼) | 템플릿 §#8 |
| #5 | C. Random Projection | RQ3 | ~2h | RQ3 2순위 (단순 하한) | 템플릿 §#5 |
| #7 | E. Hilbert Curve | RQ3 | ~4h | RQ3 3순위 (contribution 후보) | 템플릿 §#7 |
| #6 | A. LSH | RQ3 | ~4h | RQ3 4순위 | 템플릿 §#6 |
| #10 | B. KDE-pilot | RQ3 | ~6h | RQ3 5순위 (이론적 상한) | 템플릿 §#10 |
| #9 | G. Distance-Shell | RQ3 | ~4h | RQ3 6순위 | 템플릿 §#9 |
| #11 | H. Importance Sampling | RQ3 | ~6h | RQ3 7순위 (2x2 factorial, 가장 복잡) | 템플릿 §#11 |

**총 ~28h. 5/8 19:00 마감까지 ~51h 가용.** RQ1+RQ2 (#1~#4) 절대 사수, RQ3 는 우선순위 순.

---

## 5. 작업 흐름 (반복 절차)

```
[실험 #N 시작]
  ① 카톡 §3.1 메시지 발송 (톡방)
  ② 새 Claude 세션 + 템플릿 §#N 시작 프롬프트 복붙
  ③ 서버 SSH 접속 → 스크립트 실행 (~Nh)

[측정 진행]
  ④ 결과 raw 데이터 receive (parquet + meta json)

[실험 #N 완료]
  ⑤ Claude 에 공통 완료 프롬프트 + 핵심 수치 전달
     → 4단계 narrative 자동 생성
  ⑥ 카톡 §3.2 메시지 발송 (톡방)

[git commit + push] (산출물 보존)
  ⑦ git add experiments/results/...
  ⑧ git commit -m "experiment #N: ___ — 핵심수치"
  ⑨ git push origin main

[실험 #N+1 시작] ... 반복
```

---

## 6. 주의사항 (반복하면 안 되는 실수)

### 6.1 SSH 인증 (맥북에서 GitHub 접근 시)
- **첫 git pull/push 가 hang** 될 수 있음 (오늘 5/6 16:01 발생).
- 해결: `ssh -A` (agent forward) 또는 맥북에서 `ssh-add ~/.ssh/id_ed25519` 후 git 명령.
- 또는 맥북 `~/.ssh/config` 에 `IdentityFile` 명시.

### 6.2 vector.c 빌드 변경 (실험 #1 에서 필요)
- L940 의 sampling clause 가 SYSTEM/BERNOULLI 결정.
- GUC `vector.sampling_method` 만으로는 안 됨 — **빌드된 path 와 일치해야** 함.
- 빌드 변경 시 **PG 재시작 필수** (port 55436).
- **실험 끝나면 BERN 복원** (다음 RQ2/RQ3 실험 위해).
- 백업 파일명: `vector.c.bak.20260506_BERN_compiled`.

### 6.3 python3 -u (unbuffered) 필수
- 5/6 오전 buffered 로 30분간 진행 안보임 문제 있었음.
- 반드시 `python3 -u sift_rq1_native.py --mode system 2>&1 | tee log` 형태.

### 6.4 q_error sanity 의심
- 5/6 BERN 측정에서 s=0.01 의 5seed 가 모두 정확히 1.4411 동일 — sanity 의심.
- SYSTEM 측정 시 같은 패턴이면 PG setseed 가 sampling 단계에서 안 작동하는 것일 수 있음.
- 발견 시 즉시 디버깅 (sample row 직접 비교 + setseed 동작 확인).

### 6.5 측정 시간 budget
- 11종 합 ~28h. 5/8 19:00 까지 ~51h.
- 잠/식사/이동 빼면 실제 ~30h 가용.
- RQ1+RQ2 (#1~#4) 는 절대 사수, RQ3 는 우선순위 순.

---

## 7. 자료 위치 맵 (정확히)

### 7.1 설계·계획
- `plans/RQ재정립_20260505_2122.md` — **새 RQ 구조 v6** (5/5 회의 채택).
- `plans/연구재설계안_20260415_131400.md` — v5 (이전, 참고용).
- `submission/_drafts/속도는벡터_연구지도확인서_20260505.md` — 채림 석사 메일 보고용.

### 7.2 실험 진행 프롬프트 + 회의록
- `_internal/실험_진행_프롬프트_템플릿.md` — **11종 시작/완료 프롬프트** (각 §#1~§#11 + 최종 종합).
- `_internal/records/kakaotalk/20260505_RQ재정립_회의.md` — 5/5 비대면 회의.
- `_internal/records/kakaotalk/20260506_W1_sprint_시작_카톡.md` — 5/6 카톡 (회의 시간 5/8 19:00 확정).
- `_internal/records/kakaotalk/20260506_W1_sprint_팀원공유_프롬프트.md` — 카톡 발송용 + 자체완결 시작 프롬프트.

### 7.3 실험 결과
- `experiments/results/RQ1_RQ2 실험 결과 정리.md` — 4/27 정리 + W1 측정 추가 예정.
- `experiments/results/rq1_motivation/sift_rq1_2026_05_06/` — **5/6 측정 SIFT × BERN** (sift_rq1_bernoulli.parquet).
- `experiments/results/rq1_motivation/phase4_*` — 기존 DEEP × SYSTEM/BERN.
- `experiments/results/rq1_motivation/phase7_sift_bern.parquet` — 이전 SIFT × BERN (단일점 s=0.5, deprecated).

### 7.4 측정 코드
- `experiments/code/rq1/sift_rq1_native.py` — **5/6 작성** SIFT 측정 스크립트 (multi-seed × multi-sel × 두 모드).
- `experiments/code/rq1/sift_dtarget_extend.py` — D_target 보강 (s={0.01,0.05,0.10,0.30,0.50}).
- `experiments/code/rq1/phase4_native.py` — DEEP 원본 (참고용).

### 7.5 서버
- 호스트: `165.132.140.240` (capstone2026)
- 작업 디렉토리: `/mnt/hdd0/home/capstone2026`
- PG 포트: 55436
- DB/USER: wns41559
- 캐시: `/mnt/hdd0/home/capstone2026/cache/rq1/`
- 로그: `/mnt/hdd0/home/capstone2026/log/postgres_exqutor*.log`
- 상세: `~/.claude/projects/-Users-hyunbin-Capstone/memory/reference_server.md`

---

## 8. 마감 카운트다운

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

## 9. 맥북에서 새 Claude 세션 시작 절차

```bash
cd ~/Capstone
git pull --no-rebase origin main    # 최신 동기화 확인 (HEAD 7d43d67 또는 그 이후)
claude                                # 새 세션 시작
# (또는) claude --rc                  # Remote Control 활성화 모드
```

세션 시작 시 SessionStart hook 이 자동으로 상태 출력. 첫 메시지 권장:

```
@_internal/next_session_prompt.md 읽고 W1 sprint 이어가자.
다음은 실험 #1 (SIFT × SYSTEM block baseline) 진행.
```

이러면 이 문서가 컨텍스트에 로드되고 §2 절차 그대로 진입 가능.

---

## 10. 메모리 갱신 권장 (실험 #1 Close 단계에)

다음 세션 종료 (실험 #1 완료) 시 갱신할 메모리:
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_capstone.md` — RQ1 SIFT 2x2 표 완성 시점 추가.
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_schedule.md` — 5/8 19:00 회의 시간 확정 반영 (이미 됨).
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` — 위 항목 한 줄 요약 갱신.

---

**작성**: 조현빈 · 2026-05-06 16:04 KST · 맥미니 → 맥북 handoff
**다음 트리거**: 자취방 이동 후 맥북 `~/Capstone` 에서 새 Claude 세션 시작.
**CLAUDE.md 입구**: 본 파일 위치 `_internal/next_session_prompt.md` — 세션 시작 시 자동 참조 권장.
