# v16 deck polishing prompt — 5 slide (2·3·8·11·12) 단일 복붙용

> 작성 2026-05-25 11:42 KST. 사용자 5/25 polishing 피드백 정합 반영. claude.ai/design "최종발표" 대화창 (`/p/019e1a41-701c-7134-9ce1-1247262c1563?file=속도는벡터_12장_v16_deck.html`) 에 그대로 복붙.

---

## 단일 복붙 프롬프트 (아래 ▼ 부터 ▲ 까지 전부 복사)

▼

지금 v16 deck 의 slide 2, 3, 8, 11, 12 만 다음과 같이 정확히 수정해줘. 나머지 slide (1·4·5·6·7·9·10·13·14) 는 그대로 carry — 절대 손대지 마. design system 동결 (navy `#1E3A5F` 앵커 · cyan 강조 · 4 악센트 (cyan 배경 / violet 방법 / green 결과 / coral 적용) · Apple SD Gothic Neo + Inter + IBM Plex Sans KR · 가운데 정렬 · footer 텍스트 X · 페이지 번호 X · 별표 ★ 슬라이드 안 X). chapter badge (● 배경 / 방법 / 결과 / 적용) 도 그대로 carry.

---

### slide 2 (배경 — 벡터 증강 분석 쿼리 VAQ) 수정

**문제**: 지금 SQL 박스 안에 `:부품벡터` 같은 placeholder 가 어색함. 실험에서 실제로 사용한 TPC-H Q3 (VAQ 변형) 쿼리를 가져다 그대로 보이고, 옆에 짧은 설명 라벨만 덧붙여줘.

**교체 SQL** (실제 측정에서 쓴 `reference/exqutor_query_plans/tpc_h/q3.sql` 그대로, 단 자릿수 압축):

```sql
SELECT  l_orderkey, o_orderdate, o_shippriority
FROM    customer, orders, lineitem, partsupp_deep
WHERE   c_mktsegment = 'HOUSEHOLD'
  AND   c_custkey = o_custkey
  AND   l_orderkey = o_orderkey
  AND   o_orderdate < DATE '1995-03-14'
  AND   l_shipdate  > DATE '1995-03-14'
  AND   ps_partkey = l_partkey  AND  ps_suppkey = l_suppkey
  AND   ps_embedding  <->  '[ 쿼리 부품 벡터 ]'  <  0.86
ORDER BY ps_embedding  <->  '[ 쿼리 부품 벡터 ]'  ;
```

설명 라벨 (오른쪽 또는 아래 작게 배치):
- `ps_embedding <-> '[쿼리 부품 벡터]' < 0.86` 줄 옆 → **← 벡터 유사도 술어 (VAQ)**
- 나머지 `WHERE` 줄 옆 → **← 관계형 조건 (TPC-H)**
- SQL 박스 위 작은 캡션: `TPC-H Q3 변형 — 한 SQL 안에 관계형 JOIN + 벡터 유사도`

분석가 메시지 박스 (왼쪽) 도 narrative 정합으로 살짝 수정:
- 기존: "공급자 부품과 비슷한 부품들의 2024년 매출 분석"
- 신본: **"HOUSEHOLD 시장 세그먼트 · 3월 14일 전 주문 · 후 배송된 lineitem 중 쿼리 부품과 유사한 partsupp 의 주문 TOP"**

VAQ 결과 박스 (오른쪽) 의 customer / orders / lineitem 카드는 carry. 단 customer 아래 `partsupp_deep` 행 1개 추가 (벡터 테이블).

레이아웃: 분석가 (왼쪽) → SQL hero (가운데, 넓게) → VAQ 결과 (오른쪽). 모두 가운데 정렬 carry.

---

### slide 3 (배경 — 카디널리티 한 곳이 잘못되면 최대 1만 배 느려짐) 수정

**문제 1**: 빨간 박스의 `333,333 예측 (1/3)` 카디널리티 추정치를 **여기서 보일 필요 X** — 다음 slide 4 (pgvector 33.3% / VBASE 50% / DuckDB-vss 100%) 에서 더 자세히 나옴. slide 3 에서는 "잘못된 카디널리티 추정이 plan 선택에 어떻게 영향 미치는지" 만 강조.

**조치**: 빨간 박스 안 `333,333 예측 (1/3)` + `실제 추출 = 추정 큰 영역` 텍스트 + 우측 cyan 박스 안 `~100 실제 (작은 영역)` + `실제 추출 = 작은 영역 ~100 점` 텍스트 **모두 제거**. 박스 자체는 가볍게 유지하되 라벨만 `❌ 카디널리티 추정 틀림` / `✓ 카디널리티 추정 정확` 로 단순화.

**문제 2**: JOIN 되는 쿼리 플랜 트리가 너무 추상적 (Hash Join + Hash + Seq Scan 3 노드). 실제 측정 plan (TPC-H Q3 VAQ) 더 디테일하게 보여줘.

**교체 plan tree** (실제 측정 156 plan table 기반, `_internal/cache/rq3/latency/phase2/table_156plan_20260525_001258.md` 의 B1 vs CaseB plan signature 차용):

왼쪽 ❌ (잘못된 카디널리티 → Hash Join 폭주 plan):
```
Sort
 └ Hash Join
    ├ Hash
    │  └ Seq Scan  lineitem        ← 100만 행 전체 스캔
    └ Hash Join
       ├ Hash
       │  └ Seq Scan  partsupp_deep ← 벡터 (333,333 행 통째 메모리)
       └ Hash Join
          ├ Hash
          │  └ Seq Scan  customer
          └ Seq Scan  orders
```
하단 작은 텍스트: `큰 중간 테이블 누적 → 메모리·시간 폭주`

오른쪽 ✓ (정확한 카디널리티 → Nested Loop 정밀 plan):
```
Sort
 └ Nested Loop
    ├ Nested Loop
    │  ├ Index Scan  customer
    │  └ Index Scan  orders  (on c_custkey)
    └ Nested Loop
       ├ Index Scan  lineitem (on l_orderkey)
       └ Index Scan  partsupp_deep ← 벡터 (작은 영역 ~100 점만)
```
하단 작은 텍스트: `한 행씩 인덱스로 정확히 풀어냄`

**문제 3**: 하단 `벡터 테이블 100만 행 · 같은 SQL · 같은 데이터` 텍스트 + `10,000× 응답 시간 차이` hero + `TPC-H Q3 VAQ on DEEP` 메타 라벨 carry. 하지만 plan 트리가 위로 올라오면서 10,000× hero 와의 간격 조정 — 트리 아래 작은 화살표 또는 line 으로 hero 와 시각 연결.

레이아웃: 헤더 → ❌ 왼쪽 plan tree + ✓ 오른쪽 plan tree → 10,000× hero (하단 가운데).

---

### slide 8 (방법 — 1,508가지 조합으로 검증) 수정

**조치**: 기존 3 박스 (DATASETS 5 / VARIABLES 3 / COMBINATIONS 1,508) 그대로 carry. **하단에 4번째 박스 또는 가로 가운데 정렬 텍스트 블록 추가** — "측정 환경" 명시.

**추가 박스/블록 내용** (3 박스 아래 가운데 정렬, 보조 라벨 톤 — 약한 violet/회색):

```
MEASUREMENT ENVIRONMENT · 측정 환경
─────────────────────────────────────
서버      Intel Xeon Gold 6530 · 128 vCPU
메모리    1.0 TB RAM · NVMe SSD
GPU       4× NVIDIA RTX 6000 Ada
엔진      PostgreSQL 16 + pgvector 0.8 (HNSW)
반복      각 cell 15회 평균 · 2,880회 측정 · 180 paired
```

(또는 4 칸 grid 로 ENGINE / SERVER / MEMORY / REPLICATION 4 개 박스 — 단 기존 3 박스 톤과 시각 무게 맞춰 작게.)

레이아웃: 헤더 → 3 박스 (carry) → MEASUREMENT ENVIRONMENT 블록 (작게, 하단 가운데).

---

### slide 11 (적용 — 엔진 응답 시간 베이스라인 vs 결합) 핵심 수정

**문제 1 (가장 중요)**: 사용자가 헷갈림 — "저희 방법이 exqutor 보다 느린 거였어요?" / "latency 는 작을수록 좋은 건데 막대그래프가 거꾸로 보임".

**정확한 의미**:
- **pgvector 기본** = Adaptive Sampling 적용 X (논문 §V-B 없이 pgvector 그대로). 5,677 ms (가장 느림).
- **베이스라인 (exqutor 그대로)** = Adaptive Sampling 의 무작위 베르누이 (논문 §V-B verbatim 재현). 977.6 ms = **5.77× 빠름**.
- **결합 (본 연구)** = 베이스라인의 무작위 베르누이 + 분포 인지 method 13종 산술평균. 983.5 ms = **5.70× 빠름**.
- → **latency 만 보면 우리 결합이 exqutor 보다 0.07× 격차로 살짝 느림 (사실상 동등)**. 진짜 우위는 **plan 회복 robustness** (다음 시각화 carry — 91 vs 148 도넛).

**문제 2**: 막대그래프가 거꾸로 — 지금은 "몇× 성능" 을 막대 길이로 보여서 5.77× 가 가장 김. **latency 값 자체** 를 막대 길이로 (pgvector 기본 5,677 ms 가 가장 김, 우리 결합·베이스라인 짧음). 그 위에 ×배수는 작은 숫자 라벨로.

**조치 (막대그래프 재설계)**:

```
pgvector 기본                ████████████████████████████████  5,677 ms   (1.0×)
베이스라인 (exqutor 그대로)  █████                                977.6 ms   (5.77× ↑)
결합 (본 연구)               █████                                983.5 ms   (5.70× ↑)
```

- 막대 길이 = ms 값 자체 (pgvector 5,677 가 가장 김, 베이스라인·결합 비슷하게 짧음)
- 막대 끝 오른쪽 라벨: `5,677 ms` / `977.6 ms` / `983.5 ms` (큼지막)
- 그 옆에 작은 ×배수: `(1.0×)` / `(5.77× ↑)` / `(5.70× ↑)` — ↑ 화살표로 "빨라짐" 명시
- 색: pgvector 기본 = 회색 (대조군), 베이스라인 = navy, 결합 = cyan (carry)

**문제 3**: "inject" 라는 단어가 의미 불명. **모두 제거**.
- `베이스라인 inject` → `베이스라인 (exqutor 그대로)`
- `결합 inject` → `결합 (본 연구)`

**문제 4**: 하단 `12 cell × 13 method = 156 plan · 평균 latency` 텍스트 → carry. plan 회복 도넛 (91 / 156 vs 148 / 156) carry. 단 오른쪽 격차 박스 텍스트 조정:
- 기존: `남은 0.07× 격차 · 8 plan · 결합이 못 회복한 8 plan 에서 발생 · 5.77 → 5.70 = 0.07× 차이`
- 신본: **"latency 는 사실상 동등 (0.07× 격차). 진짜 우위는 plan 회복 — 91 → 148 plan (+57)"**

레이아웃: 헤더 → 막대그래프 3행 (latency 값 + ×배수 라벨) → plan 회복 도넛 2개 + 격차 의미 박스.

---

### slide 12 (적용 — 본 측정 plan 개선 + 엔진 확장 가능성) 수정

**문제**: 왼쪽 CURRENT 박스의 `7/12` 와 `148/156` 이 무엇 분의 무엇인지 의미가 명확하지 않음.

**조치 (CURRENT 박스 라벨 정밀화)**:

기존:
```
7/12          →     148/156
CELL                PLAN · 94.9%
베이스라인 단독      결합 13 method
```

신본:
```
베이스라인이 정답 plan 회복한 측정 cell        결합 13 method 가 정답 plan 회복한 plan 시도
       7 / 12 cell                  →           148 / 156 plan  (94.9%)
       (= 58.3 %)                                (= 12 cell × 13 method 중 148)
```

또는 각 숫자 위에 작은 메타 라벨:
- `7 / 12` 위에: **"12 측정 cell 중 7 cell — 베이스라인이 정답 plan 회복 한 cell 수"**
- `148 / 156` 위에: **"156 plan 시도 (12 cell × 13 method) 중 148 plan — 결합이 정답 plan 회복"**

하단 캡션:
- 기존: `결합 13 method 가 베이스라인이 놓친 정답 plan 을 폭넓게 회복`
- 신본 (좀 더 명시): `베이스라인이 12 cell 중 5 cell 에서 plan 회복 실패 (오답 plan) → 결합 13 method 적용 시 156 plan 시도 중 148 plan (94.9%) 정답 회복`

오른쪽 FUTURE 박스 (sf=100 · sel≥0.5 · 다중 벡터 · 다른 엔진) carry — 변경 X.

레이아웃: 헤더 → CURRENT 박스 (왼쪽, 라벨 정밀화) + FUTURE 박스 (오른쪽, carry).

---

### 공통 추가 지시 (모든 5 slide 적용)

1. **색·폰트·간격 design system 동결** — 임의 변경 X.
2. **chapter badge (● 배경/방법/적용)** carry — 색 동일.
3. **가운데 정렬·여백** carry — 좌·우 균형.
4. **footer 텍스트 (TPC-H Q3·Q9·Q10·Q12 · DEEP 8천만 ··· 등) 모두 제거** carry.
5. **별표 ★·페이지 번호 X** carry.
6. **이름·약어 통일** — "베이스라인" / "결합" / "단독 대체" 한국어 carry · "B1·CaseA·CaseB" 코드명 X.

5 slide 수정 후 14 slide 그대로 carry. v17 으로 저장.

▲

(여기까지가 복붙용 단일 prompt. claude.ai/design "최종발표" 대화창에 그대로 붙여넣으면 됨.)
