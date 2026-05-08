# 실험지침 (AUTO)

> 대상: Capstone 프로젝트 | 모드: 자동 실행 (전권 위임)
> 마지막 실행: 2026-05-08 22:00 (RQ1+RQ2+RQ3 100% finalize, Adaptive 비교 framework 추가)

## 5/8 22:00 finalize 후 핵심 패턴 (W2~W3 active)

본 RQ1/RQ2/RQ3 측정 framework 가 완성되었으므로 W2 자문 회신 후 launch 할 추가 측정은 **chain_unified.py CELLS dict + monkey-patch 패턴**을 따른다. 신규 method 측정 시:

1. `_internal/scripts/measure_multi_paradigm.py` (5 paradigm 11 method) 또는 `measure_multi_adaptive_sampling.py` (Adaptive Sampling 본 논문) 와 같은 dedicated 측정기를 작성. CELLS dict 직접 정의 X — `chain_unified.py.CELLS` 를 import + filter 후 monkey-patch.
2. **silent skip risk** 방지: 측정기 도입부에 `assert len(CELLS) >= N` + `print(list(CELLS.keys()))` 로 cell 목록 확인 (5/7 STAGE 2 silent skip 사고 재발 방지).
3. paired 측정 시 query_id alignment 필수 — `analyze_multi_paradigm.py` 의 query_id paired Δ% 패턴 따름.
4. 측정 결과는 `experiments/results/multi_{tag}_*.csv` 로 저장, 이후 `analyze_multi_paradigm.py` 또는 `master_v6_fill_partial.py` 가 fill 한다.

## 실험지침의 범위

**IS (이 지침이 하는 것):**
- PostgreSQL + pgvector 설치/설정 상태 확인 및 구축
- Exqutor 소스 클론, 빌드, pgvector 패치 적용
- DuckDB 설치 + VSS(Vector Similarity Search) 확장 구성
- Python + FAISS + NumPy 환경 검증
- 데이터셋(SIFT1M, GloVe-100, Deep10M, GIST1M 등) 다운로드/검증/적재
- DB 테이블 생성, 인덱스(HNSW/IVFFlat) 구축
- EXPLAIN ANALYZE 실행 및 실행 계획 캡처
- 벤치마크 스크립트 작성/실행 (선택도 sweep, Recall@k, QPS, latency)
- Exqutor 적용 전/후 비교 실행 (RQ3 4강 vs Adaptive Sampling paired Δ%)
- 결과 수집 → CSV/JSON 구조화 → 비용 추정 오차 계산
- matplotlib/seaborn 차트 생성
- 실험 로그 md 작성 (날짜/환경/데이터셋/목적/결과)
- **5 paradigm framework 11 method × 4강 selection paired alignment** (5/8 RQ3 확정 후)

**IS NOT (이 지침이 하지 않는 것 → 담당 지침):**
- 실험 설계서 작성(데이터셋 선정, 지표 설정, 비교축 설계) → 연구설계지침
- 실험 결과 보고서 md→PDF 변환 → 문서생성지침
- 실험 결과를 중간/최종 보고서에 편입 → 제출물지침
- 파일 무결성 점검, PDF 폰트 검증 → 점검지침

---

## Phase 구성

### Phase 0: 환경 확인 (3분)

기존 설치 상태를 확인하고 누락된 구성 요소를 식별한다.

- [ ] PostgreSQL 설치 및 버전 확인 (`psql --version`)
- [ ] pgvector 확장 설치 여부 (`psql -c "SELECT extversion FROM pg_extension WHERE extname='vector'"`)
- [ ] DuckDB 설치 및 버전 확인 (`duckdb --version` 또는 Python `import duckdb`)
- [ ] Python 패키지 확인: numpy, faiss-cpu, psycopg2, matplotlib, seaborn
- [ ] Exqutor 클론 상태 확인 (`ls ~/Capstone/exqutor/` 또는 지정 경로)
- [ ] 디스크 여유 공간 확인 (`df -h .` — 데이터셋용 최소 10GB 권장)
- [ ] 결과 저장 디렉토리 존재 확인 (`experiments/` 폴더)

확인 스크립트:
```bash
cd ~/Capstone
echo "=== 환경 확인 ==="
echo "PostgreSQL: $(psql --version 2>/dev/null || echo '미설치')"
echo "pgvector: $(psql -c "SELECT extversion FROM pg_extension WHERE extname='vector'" 2>/dev/null || echo '미설치')"
echo "DuckDB: $(python3 -c "import duckdb; print(duckdb.__version__)" 2>/dev/null || echo '미설치')"
echo "NumPy: $(python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo '미설치')"
echo "FAISS: $(python3 -c "import faiss; print(faiss.__version__)" 2>/dev/null || echo '미설치')"
echo "matplotlib: $(python3 -c "import matplotlib; print(matplotlib.__version__)" 2>/dev/null || echo '미설치')"
echo "디스크: $(df -h . | tail -1 | awk '{print $4}') 남음"
```

Phase 0 결과를 바탕으로:
- 모두 설치됨 → Phase 1 스킵, Phase 2로 이동
- 미설치 항목 있음 → Phase 1 실행

---

### Phase 1: 환경 구축 (첫 실행 시만) (30분)

Phase 0에서 미설치 항목이 있을 때만 실행한다.

- [ ] PostgreSQL 설치 (`brew install postgresql@16` 또는 기존 버전 사용)
- [ ] pgvector 확장 설치 (`brew install pgvector` 또는 소스 빌드)
- [ ] Exqutor 클론 및 빌드
  ```bash
  git clone https://github.com/BDAI-Research/Exqutor.git ~/Capstone/exqutor
  cd ~/Capstone/exqutor
  # 빌드 방법은 Exqutor README 참조
  ```
- [ ] Exqutor 패치를 pgvector에 적용 (README 지침 따름)
- [ ] DuckDB + VSS 확장 설치
  ```bash
  pip3 install duckdb
  # VSS 확장은 DuckDB 내에서: INSTALL vss; LOAD vss;
  ```
- [ ] Python 패키지 설치
  ```bash
  pip3 install numpy faiss-cpu psycopg2-binary matplotlib seaborn pandas
  ```
- [ ] 테스트 쿼리로 기본 동작 확인
  ```sql
  -- pgvector 테스트
  CREATE TABLE test_vec (id serial, embedding vector(3));
  INSERT INTO test_vec (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
  SELECT * FROM test_vec ORDER BY embedding <-> '[3,1,2]' LIMIT 1;
  DROP TABLE test_vec;
  ```
- [ ] 실험 디렉토리 구조 생성
  ```bash
  mkdir -p ~/Capstone/experiments/{data,results,scripts,logs,figures}
  ```

---

### Phase 2: 데이터셋 준비 (15분)

설계안에 명시된 데이터셋을 다운로드하고 DB에 적재한다.

- [ ] 최신 설계안 확인 (`ls plans/연구_설계안_*.md | tail -1`)
- [ ] 대상 데이터셋 목록 확인 (설계안 기준)
- [ ] 데이터셋 다운로드
  - SIFT1M: ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz
  - GloVe-100: Stanford NLP 사이트
  - 기타: 설계안 명시 경로
- [ ] 다운로드 파일 검증 (행 수, 차원, 파일 크기)
  ```python
  import numpy as np
  data = np.fromfile("sift_base.fvecs", dtype=np.float32)
  dim = int(data[0])
  n = len(data) // (dim + 1)
  print(f"SIFT1M: {n}행 × {dim}차원")
  ```
- [ ] DB 테이블 생성 및 데이터 적재
  ```sql
  CREATE TABLE sift1m (
    id serial PRIMARY KEY,
    embedding vector(128),
    label int  -- 필터 컬럼
  );
  -- COPY 또는 Python psycopg2로 벌크 적재
  ```
- [ ] 인덱스 생성
  ```sql
  CREATE INDEX ON sift1m USING hnsw (embedding vector_l2_ops)
    WITH (m = 16, ef_construction = 200);
  ```
- [ ] 적재 검증: 행 수, 인덱스 상태 확인

---

### Phase 3: 벤치마크 실행 (30분+)

핵심 실험 — EXPLAIN ANALYZE 기반 실행 계획 캡처 및 성능 측정.

- [ ] 벤치마크 스크립트 작성 (`experiments/scripts/benchmark.py`)
  - 입력: 데이터셋, 선택도, 반복 횟수
  - 출력: CSV (쿼리, 선택도, latency, 실행계획)
- [ ] 선택도 sweep 실행
  - 대상 선택도: 0.1%, 1%, 10%, 50%, 90%
  - 각 선택도별 최소 10회 반복
  ```sql
  EXPLAIN ANALYZE
  SELECT id, embedding <-> '[쿼리벡터]' AS dist
  FROM sift1m
  WHERE label < [임계값]  -- 선택도 조절
  ORDER BY dist
  LIMIT 10;
  ```
- [ ] 측정 지표 수집
  - Recall@k (k=1, 10, 100)
  - QPS (Queries Per Second)
  - Latency: p50, p99
  - 비용 추정 오차 (estimated_cost vs actual_time)
- [ ] Exqutor 적용 전/후 비교
  - 기본 pgvector (baseline)
  - Exqutor ECQO 활성화 상태
  - 동일 쿼리셋으로 실행
- [ ] DuckDB 비교 실행 (VSS 확장 사용)
- [ ] 실행 계획 diff 기록
  - Seq Scan → Index Scan 전환점 식별
  - 비용 추정값 vs 실제 실행 시간 비교

---

### Phase 4: 결과 수집 + 분석 (15분)

- [ ] 결과 파일 정리
  ```
  experiments/results/
  ├── benchmark_YYYYMMDD_HHMMSS.csv    # 원시 결과
  ├── summary_YYYYMMDD.json            # 집계 통계
  └── explain_plans/                   # 실행 계획 텍스트
  ```
- [ ] 집계 통계 계산
  - 데이터셋별, 선택도별 평균/중앙값/p99
  - Exqutor 적용 전/후 속도 비율 (speedup ratio)
  - 비용 추정 오차율: `|estimated - actual| / actual`
- [ ] 실행 계획 비교 분석
  - 선택도별 plantype 전환점 (Seq Scan ↔ Index Scan)
  - Exqutor가 올바른 계획을 선택한 비율

---

### Phase 5: 시각화 + 로그 기록 (10분)

- [ ] matplotlib/seaborn 차트 생성
  ```
  experiments/figures/
  ├── latency_vs_selectivity.png       # 선택도별 latency 비교
  ├── speedup_ratio.png                # Exqutor 적용 전/후 speedup
  ├── cost_estimation_error.png        # 비용 추정 오차 분포
  └── plan_type_transition.png         # 실행 계획 전환점
  ```
- [ ] 차트 스타일 규칙
  - 폰트: 시스템 기본 (차트는 영문 라벨 사용)
  - 색상: baseline(회색), Exqutor(파랑), DuckDB(주황)
  - 해상도: 300 DPI, figsize=(10, 6)
- [ ] 실험 로그 md 작성 (`experiments/logs/YYYYMMDD_실험제목.md`)
  ```markdown
  # 실험 로그: [제목]
  - 날짜: YYYY-MM-DD
  - 환경: PostgreSQL 16 + pgvector 0.7 + Exqutor
  - 데이터셋: SIFT1M (1M × 128d)
  - 목적: 선택도별 실행 계획 비교
  - 결과 요약: ...
  - 주요 발견: ...
  - 차트: ../figures/[파일명].png
  ```

---

## 완료 조건

- [ ] Phase 0 환경 확인 완료 (모든 항목 체크)
- [ ] Phase 1 환경 구축 완료 또는 스킵 (이미 설치됨)
- [ ] 데이터셋 최소 1개 DB 적재 + 인덱스 생성 완료
- [ ] EXPLAIN ANALYZE 결과 최소 1개 캡처
- [ ] 벤치마크 결과 CSV 최소 1개 생성
- [ ] 시각화 차트 최소 1개 생성
- [ ] 실험 로그 md 작성 완료
- [ ] `> 마지막 실행:` 라인에 현재 날짜+시각 업데이트
