---
name: experiment-log
description: "실험 결과 기록 및 분석. '실험 기록', 'EXPLAIN ANALYZE 분석', '벤치마크 결과' 등에 반응."
---

# 실험 로그 스킬

pgvector/DuckDB 실험 결과를 구조화하여 기록하고 분석한다.

## 기록 구조

```markdown
# 실험 로그: [실험명]

**날짜**: YYYY-MM-DD
**환경**: [DB 종류 + 버전, 하드웨어 스펙]
**데이터셋**: [이름, 차원, 행 수]
**목적**: [실험 목적 한 줄]

---

## 실험 조건

| 파라미터 | 값 |
|----------|-----|
| 선택도 | X% |
| HNSW M | 16 |
| HNSW ef_search | 400 |
| 거리 임계값 D | X |

## EXPLAIN ANALYZE 결과

```sql
-- 쿼리
-- EXPLAIN ANALYZE 출력 전문 붙여넣기
```

## 측정 결과

| 메트릭 | 값 |
|--------|-----|
| 실행 시간 | Xms |
| 추정 카디널리티 | X |
| 실제 카디널리티 | X |
| Q-error | X |
| 조인 방식 | Hash/Nested Loop/... |
| 스캔 방식 | Seq/Index/... |

## 분석 및 인사이트

[서사적 분석]

## 다음 실험 제안

[후속 실험 방향]
```

## 저장 위치

- `Experiments/YYYY-MM-DD_실험명.md`
- 동일 이름으로 .pdf 생성
