# 실험지침 (MANUAL)

> 사람이 직접 수행하거나 Claude에게 개별 요청할 때 참조

## 언제 실행하나?

- **실험 환경 최초 구축 시** — pgvector, DuckDB, Exqutor를 처음 설치할 때
- **새 데이터셋 추가 시** — 다운로드 → 검증 → DB 적재 → 인덱스 생성
- **벤치마크 실행 시** — EXPLAIN ANALYZE 캡처, 선택도 sweep 등
- **실험 결과 정리 시** — CSV 집계, 차트 생성, 실험 로그 작성
- **Exqutor 패치 업데이트 시** — 새 버전 빌드 후 재벤치마크

## 단계별 가이드

### Step 1: 환경 확인

실험 전에 모든 구성 요소가 정상인지 확인:

```bash
cd ~/Capstone
# PostgreSQL + pgvector
psql --version
psql -c "SELECT extversion FROM pg_extension WHERE extname='vector'"

# DuckDB
python3 -c "import duckdb; print(duckdb.__version__)"

# Python 패키지
python3 -c "import numpy, faiss, matplotlib, seaborn, psycopg2; print('OK')"

# Exqutor
ls ~/Capstone/exqutor/
```

하나라도 실패하면 Claude에게 요청:
> "실험 환경 구축해줘 — pgvector/DuckDB/Exqutor 설치"

### Step 2: 데이터셋 준비

1. 최신 설계안 확인:
   ```bash
   ls ~/Capstone/plans/연구_설계안_*.md | tail -1
   ```
2. 설계안에 명시된 데이터셋 목록 확인
3. 다운로드 및 검증:
   ```bash
   # 예: SIFT1M
   cd ~/Capstone/experiments/data
   wget ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz
   tar xzf sift.tar.gz
   ```
4. DB 적재:
   ```sql
   -- 테이블 생성
   CREATE TABLE sift1m (
     id serial PRIMARY KEY,
     embedding vector(128),
     label int
   );
   -- Python으로 벌크 적재
   ```
5. 인덱스 생성:
   ```sql
   CREATE INDEX ON sift1m USING hnsw (embedding vector_l2_ops)
     WITH (m = 16, ef_construction = 200);
   ```

Claude에게 요청할 경우:
> "SIFT1M 데이터셋 다운로드하고 pgvector에 적재해줘"

### Step 3: 벤치마크 실행

1. 벤치마크 스크립트 위치: `experiments/scripts/benchmark.py`
2. 실행:
   ```bash
   cd ~/Capstone
   python3 experiments/scripts/benchmark.py \
     --dataset sift1m \
     --selectivity 0.001,0.01,0.1,0.5,0.9 \
     --repeat 10 \
     --output experiments/results/benchmark_$(date +%Y%m%d_%H%M%S).csv
   ```
3. EXPLAIN ANALYZE 수동 확인:
   ```sql
   EXPLAIN ANALYZE
   SELECT id, embedding <-> '[쿼리벡터]' AS dist
   FROM sift1m
   WHERE label < 100
   ORDER BY dist LIMIT 10;
   ```

Claude에게 요청할 경우:
> "SIFT1M에서 선택도 sweep 벤치마크 실행해줘"

### Step 4: 결과 분석 및 시각화

1. 결과 CSV 확인:
   ```bash
   ls ~/Capstone/experiments/results/*.csv
   ```
2. 차트 생성:
   ```bash
   python3 experiments/scripts/visualize.py \
     --input experiments/results/최신결과.csv \
     --output experiments/figures/
   ```
3. 실험 로그 작성 (`experiments/logs/YYYYMMDD_제목.md`)

Claude에게 요청할 경우:
> "최신 벤치마크 결과로 차트 만들고 실험 로그 작성해줘"

### Step 5: Exqutor 전/후 비교

1. Exqutor 비활성 상태에서 벤치마크 실행 (baseline)
2. Exqutor 패치 활성화
3. 동일 쿼리셋으로 재실행
4. speedup ratio 계산 및 차트 생성

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| 인덱스 없이 벤치마크 실행 | 인덱스 생성 후 `VACUUM ANALYZE` 실행 |
| 선택도 계산 오류 | `SELECT COUNT(*) FROM table WHERE 조건` 으로 실제 선택도 검증 |
| cold cache에서 측정 | 첫 실행은 warmup으로 버리고, 이후 반복 측정 |
| 결과를 구조화하지 않음 | 반드시 CSV/JSON으로 저장 — 수동 메모 금지 |
| 실행 계획을 텍스트로만 저장 | `EXPLAIN (ANALYZE, FORMAT JSON)` 으로 JSON 형태도 저장 |
| 환경 정보 미기록 | 실험 로그에 PostgreSQL 버전, pgvector 버전, 하드웨어 스펙 필수 |
| 데이터셋 무검증 적재 | 행 수/차원/형식을 반드시 확인 후 적재 |
| Exqutor 패치 미적용 확인 | `SHOW` 명령으로 Exqutor 관련 GUC 파라미터 확인 |

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 연구설계지침 | 실험 설계서(데이터셋, 지표, 비교축)를 받아서 실행 |
| 문서생성지침 | 실험 결과 보고서 md → PDF 변환 위임 |
| 제출물지침 | 실험 결과를 중간/최종 보고서에 편입 |
| 점검지침 | 실험 관련 파일 무결성은 점검지침 범위 |
| 주간보고지침 | 실험 진행 상태를 주간 보고에 반영 |
