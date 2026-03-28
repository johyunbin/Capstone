# Phase 2: 실험지침 제작 프롬프트

## 지침 개요

**실험 = 환경 구축부터 결과 시각화까지 전 파이프라인.** pgvector/DuckDB에서
EXPLAIN ANALYZE 기반 벤치마크를 실행하고, Exqutor 적용 전/후를 비교 분석한다.

## IS / IS NOT

**IS:**
- pgvector, DuckDB, FAISS 환경 설치/설정
- Exqutor 소스 빌드 + pgvector 패치 적용
- 데이터셋(SIFT1M, GloVe, Deep10M 등) 다운로드/검증/적재
- EXPLAIN ANALYZE 실행 및 실행 계획 분석
- 벤치마크 스크립트 작성 및 실행
- 결과 수집, 분석, 시각화 (차트/그래프)
- 실험 로그 기록 (날짜/환경/데이터셋/목적/결과)

**IS NOT:**
- 실험 설계서(데이터셋 선정, 지표 설정, 비교축 설계) → 연구설계지침
- 실험 결과 보고서 PDF 변환 → 문서생성지침
- 실험 결과를 중간/최종 보고서에 편입 → 제출물지침

## 읽어야 할 프로젝트 파일

1. `CLAUDE.md` — 실험 설계 초안, 데이터셋 후보, 평가 지표, 대상 시스템
2. `.claude/skills/experiment-log/` — 기존 스킬 (흡수 대상)
3. `plans/연구_설계안_*.md` — 최신 설계안 (실험 범위 결정)
4. Exqutor GitHub: https://github.com/BDAI-Research/Exqutor — 빌드 방법

## Phase 구성 가이드

### Phase 0: 환경 확인 (3분)
- PostgreSQL + pgvector 설치 상태
- DuckDB 설치 상태
- Python + FAISS + NumPy 설치 상태
- Exqutor 클론/빌드 상태
- 디스크 여유 공간 (데이터셋 용)

### Phase 1: 환경 구축 (첫 실행 시만) (30분)
- pgvector 확장 설치 + Exqutor 패치 적용
- DuckDB 설치 + VSS 확장
- 데이터셋 다운로드 스크립트 작성
- 테스트 쿼리로 기본 동작 확인

### Phase 2: 데이터셋 준비 (15분)
- 대상 데이터셋 다운로드 (설계안 기준)
- 차원/행수/형식 검증
- DB 테이블 생성 + 데이터 적재
- 인덱스(HNSW/IVFFlat) 생성

### Phase 3: 벤치마크 실행 (30분+)
- EXPLAIN ANALYZE로 실행 계획 캡처
- 선택도 sweep (0.1% → 1% → 10% → 50% → 90%)
- Recall@k, QPS, latency(p50/p99) 측정
- Exqutor 적용 전/후 비교

### Phase 4: 결과 수집 + 분석 (15분)
- 결과를 구조화된 CSV/JSON으로 저장
- 비용 추정 오차 계산
- 실행 계획 비교 (Seq Scan vs Index Scan 전환점 등)

### Phase 5: 시각화 + 로그 기록 (10분)
- matplotlib/seaborn으로 차트 생성
- 실험 로그 md 작성 (날짜/환경/데이터셋/목적/결과)

## 완료 조건
- 실험 환경 정상 동작 확인
- EXPLAIN ANALYZE 결과 최소 1개 캡처
- 실험 로그 md 작성 완료
