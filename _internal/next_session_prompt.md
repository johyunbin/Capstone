# Next Session Resume — 2026-05-06 12:23 KST → 맥미니에서 재개

## 어디까지 했나 (5/6 오전 11:51 ~ 12:23 맥북에서)

### W1 sprint 시작 + 팀원 공유 문서 작성 + RQ1 SIFT × BERN 측정 완료

**완료**:
1. ✅ 기존 SIFT 데이터 audit (BERN s=0.5 단일점 → 5sel × 5seed 풀그리드 필요 확정)
2. ✅ SIFT D_target s∈{0.01, 0.05, 0.10, 0.30, 0.50} 5점 풀그리드 계산
   - 산출: `experiments/results/rq1_motivation/sift_rq1_2026_05_06/query_selectivity_sift_v2.parquet` (500 rows)
   - 산출: 동일 폴더 `sift_dtarget_multsel_v2.json`
3. ✅ SIFT measurement 스크립트 — `experiments/code/rq1/sift_rq1_native.py` (multi-seed × multi-sel × 두 모드 공용)
4. ✅ D_target 보강 스크립트 — `experiments/code/rq1/sift_dtarget_extend.py`
5. ✅ **SIFT × BERN 측정 완료** — 5sel × 5seed × 100q = 2500 rows
   - 산출: `experiments/results/rq1_motivation/sift_rq1_2026_05_06/sift_rq1_bernoulli.parquet`
   - 산출: 동일 폴더 `sift_rq1_bernoulli_meta.json`
   - 측정 시간: 1821s (≈30 min) on PG 55436
   - 핵심 수치 (median q_error, mean across 5 seed):
     | sel | mean | std |
     |---|---|---|
     | 0.01 | 1.4411 | 0.0000 |
     | 0.05 | 1.1966 | 0.0095 |
     | 0.10 | 1.1493 | 0.0263 |
     | 0.30 | 1.0684 | 0.0118 |
     | 0.50 | 1.0589 | 0.0071 |
6. ✅ **팀원 공유 문서** — `_internal/records/kakaotalk/20260506_W1_sprint_팀원공유_프롬프트.md`
   - §0 카톡 발송 메시지 (그대로 복붙용 — 박세은 timeline 5/7+5/8 반영)
   - §1 5/5 21:12 회의 정리 verbatim + 21:10 timeline 갱신 노트
   - §2 11항목 분담 카드 (#1~#11, 동기·확인·예상·조건·구현 명시)
   - §3 자율 분담 표
   - §4 자체완결 시작 프롬프트
   - §5 완료 보고 양식

**서버 상태 (165.132.140.240, capstone2026)**:
- PG 55436 (Exqutor) 가동 중
- vector.c md5 = `7cdc780cff5ae1357bc243064a1167b8` — **현재 BERN 컴파일 상태** (L940: `TABLESAMPLE BERNOULLI(%f)`)
- vector.so md5 = `4c947fc81bfcf6e915a5971d98e915de`
- 작업 디렉토리: `/mnt/hdd0/home/capstone2026/cache/`
- 백업: `vector.c.bak.20260414_1934_before_bernoulli` 는 SYSTEM 라인 + 구버전 (stratified 코드 없음 — **그대로 쓰지 말 것**)

---

## 맥미니에서 재개할 작업

### 0. 세션 시작 (5분)

```bash
cd ~/Capstone
git pull --no-rebase origin main
```

### 1. SYSTEM 빌드 + 측정 + BERN 복원 (총 ~50 min)

**계획**: 단일 sed 패치로 L940 BERNOULLI → SYSTEM (1934 백업은 stratified 코드 없어 사용 불가). 빌드 후 같은 측정 스크립트 (`sift_rq1_native.py`) 를 `--mode system` 으로 실행. 끝나고 BERN 복원 (다음 RQ2/RQ3 실험을 위한 baseline 보호).

```bash
# step 1: SSH
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
$PG_BIN/pg_ctl restart -D /mnt/hdd0/home/capstone2026/exqutor_sf10 -l /mnt/hdd0/home/capstone2026/log/postgres_exqutor.log

# step 6: 검증 (Sampling Method: 'system' 인지 EXPLAIN 으로 확인)
$PG_BIN/psql -h /tmp -p 55436 -U wns41559 -d wns41559 -c "SHOW vector.sampling_method"

# step 7: SYSTEM 측정 (~30 min) — python3 -u 로 unbuffered (5/6 오전 buffered 로 30분간 진행 안보임 문제 있었음)
cd /mnt/hdd0/home/capstone2026/cache
python3 -u sift_rq1_native.py --mode system 2>&1 | tee /tmp/sift_rq1_system.log

# step 8: BERN 복원
cd /mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector/src
cp vector.c.bak.20260506_BERN_compiled vector.c
grep -n 'TABLESAMPLE' vector.c    # 확인: L940 BERNOULLI
md5sum vector.c                   # 7cdc780cff5ae1357bc243064a1167b8 일치 확인
cd ..
make PG_CONFIG=$PG_BIN/pg_config install
$PG_BIN/pg_ctl restart -D /mnt/hdd0/home/capstone2026/exqutor_sf10 -l /mnt/hdd0/home/capstone2026/log/postgres_exqutor.log

# step 9: 결과 회수 (맥미니 로컬)
exit
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/sift_rq1_system.parquet \
    ~/Capstone/experiments/results/rq1_motivation/sift_rq1_2026_05_06/
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/sift_rq1_system_meta.json \
    ~/Capstone/experiments/results/rq1_motivation/sift_rq1_2026_05_06/
```

### 2. 결과 분석 + 4단계 브리핑 (~30 min)

Claude Code 새 세션 프롬프트:
```
[실험 #1 완료] SIFT × SYSTEM/BERN RQ1 측정 결과 정리해줘.
raw: experiments/results/rq1_motivation/sift_rq1_2026_05_06/
양식: _internal/실험_진행_프롬프트_템플릿.md 공통 완료 프롬프트 (4단계: 동기·가설·예상·실제).
```

**비교 분석 핵심**:
- BERN vs SYSTEM 의 paired Wilcoxon (selectivity 별)
- mean ± std 표 + p-value
- DEEP 1M 4 cell 결과와 cross-dataset 비교
- Selectivity Gradient narrative 강화 (s=0.01 에서 BERN q_e 1.44 → SYSTEM 어느 정도?)

기존 DEEP 1M 참고:
- DEEP s=0.01: SYSTEM 1.694 / BERN 1.618 (+19.96% diff_pct)
- DEEP s=0.30: SYSTEM 1.242 / BERN 1.089 (+12.04% diff_pct)

### 3. 팀원 공유 문서 발송 결정 (~5 min)

`_internal/records/kakaotalk/20260506_W1_sprint_팀원공유_프롬프트.md` §0 텍스트 확인 후:
- 톡방 발송 (또는 수정 후 발송)
- 노션 캡스톤 일정 DB 에 W1 8 항목 + 마감 추가

### 4. (선택) #2 Neyman 시작

5/7 RQ2 마감 압박 — RQ1 분석 마치면 #2 Neyman 구현 + 측정 시작 권장.

시작 프롬프트: `_internal/실험_진행_프롬프트_템플릿.md` `### #2 — RQ2: Neyman Allocation`

---

## 현재 sprint 일정 (재확인)

- **5/7 (목)** — RQ1 + RQ2 실험 마감 (박세은 제안)
- **5/8 (금) 19:00** — 비대면 회의 (RQ3 진행 상황 공유)
- 5/15 — 자문 요청 발송
- 5/22 — 교수님 미팅
- 5/27 — 최종 발표
- 6/11 — 최종 보고서

---

**작성**: 조현빈 5/6 (수) 12:23 KST 맥북 → 맥미니 재개용
**이전 next_session_prompt** (4/29 리허설 + 4/30 중간발표) 은 종료된 일정 — 본 파일이 덮어씀.
