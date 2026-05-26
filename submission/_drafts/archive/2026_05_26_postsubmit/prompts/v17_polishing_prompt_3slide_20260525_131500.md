# v17 → v18 polishing prompt — 3 slide (2·3·5) 단일 복붙용

> 작성 2026-05-25 13:15 KST. 박세은 팀장님 2026-05-25 13:00 카톡 피드백 정합 반영. claude.ai/design "최종발표" 대화창에 그대로 복붙.

박세은 팀장님 카톡 원문:
1. slide 2: 분석가의 의도는 좀 더 자연어로 풀어 쓰는 게 좋을 듯. 의도가 약간 왜곡되더라도 청중들이 직관적으로 이해할 수 있는 수준으로 작성.
2. slide 3: 실제 쿼리 플랜 반영은 아주 좋음. 그런데 텍스트 말고 트리 그림으로 바꾸면 좀 더 좋을 것 같음. 채림님 슬라이드 15~16 처럼.
3. slide 5: Adaptive Sampling 이 한 쿼리에 대해 여러 번 추정하면서 샘플 개수 조절? 아니면 여러 쿼리에 대해 각 쿼리별 한 번씩만 샘플링? (질문 — slide 표현이 모호함)

채림님 reference (ICDE_Exqutor.pptx) slide 15~16 plan tree 시각 style 확인 결과:
- 노드 표기: **⋈ (bowtie)** Join + **σ (sigma)** Filter — DB 교과서 style
- Join 종류는 옆에 라벨: `⋈ Merge`, `⋈ Hash`, `⋈ Nested Loop`
- Scan 종류 옆에 라벨: `σ Seq Scan`, `σ Index Scan`
- Relation 이름: 굵게 (Partsupp, Lineitem, Orders)
- 트리 line: 점선 (dashed)
- 벡터 테이블 강조: **cyan 점선 타원** + "contains vectors" 라벨
- 박스: 잘못된 plan = 빨간 테두리 / 개선된 plan = 노란(orange) 테두리

---

## 단일 복붙 프롬프트 (▼ ~ ▲ 전체 복사)

▼

지금 v17 deck 의 slide 2, 3, 5 만 다음과 같이 정확히 수정해줘. 나머지 slide (1·4·6·7·8·9·10·11·12·13·14) 는 그대로 carry — 절대 손대지 마. design system 동결 (navy `#1E3A5F` 앵커 · cyan 강조 · 4 악센트 (cyan 배경 / violet 방법 / green 결과 / coral 적용) · Apple SD Gothic Neo + Inter + IBM Plex Sans KR · 가운데 정렬 · footer 텍스트 X · 페이지 번호 X · 별표 ★ 슬라이드 안 X). chapter badge (● 배경 / 방법 / 결과 / 적용) 도 그대로 carry.

---

### slide 2 (배경 — 벡터 증강 분석 쿼리 VAQ) 분석가 메시지 자연어화

**문제**: 현 slide 2 의 분석가 박스 텍스트가 SQL/TPC-H 용어 (HOUSEHOLD 세그먼트·lineitem·partsupp) 가 그대로 노출되어 청중이 한 번에 이해 어렵다.

**조치**: 분석가 박스 텍스트를 **청중 친화 자연어**로 다듬는다. 의도가 약간 왜곡되더라도 직관 우선. SQL 박스 (오른쪽 SELECT … FROM … WHERE …) + 라벨 (← 벡터 유사도 / ← 관계형 조건) + VAQ 결과 박스 + partsupp_deep 카드 등 나머지는 **그대로 carry**.

분석가 박스 텍스트 (왼쪽 말풍선) 교체:

기존: `HOUSEHOLD 시장 세그먼트 · 3월 14일 전 주문 & 후 배송된 lineitem 중 — 쿼리 부품과 유사한 partsupp 의 주문 TOP`

신본 (다음 둘 중 하나, 또는 비슷한 자연어 톤):

**옵션 A (한 줄, 가장 직관)**:
`이 부품 사진이랑 비슷한 부품들이 최근 가장 많이 팔린 주문은?`

**옵션 B (두 줄, 약간 더 맥락)**:
`가정용 카테고리에서 최근 빠르게 배송된 상품 중 —`
`이 부품 사진과 비슷한 부품의 주문 TOP 은?`

→ 옵션 A 우선 적용. 의도 정합 손실은 있어도 청중 한 번에 이해 가능.

박스 위 작은 캡션 `손가락 → SQL` carry. SQL 박스 위 캡션 `한 SQL 안에 — VAQ` + `TPC-H Q3 변형 — 한 SQL 안에 관계형 JOIN + 벡터 유사도` carry.

---

### slide 3 (배경 — 카디널리티 한 곳이 잘못되면 최대 1만 배 느려짐) plan tree 그림화

**문제**: 현 plan tree 가 monospace 텍스트 (Sort > Hash Join > Hash > Seq Scan ...) 라서 시각 무게가 약하다. 채림님 reference (ICDE_Exqutor) slide 15~16 처럼 **DB 교과서 그래픽 tree** 로 교체.

**시각 spec** (채림님 style verbatim):
- Join 노드: **⋈ (bowtie)** symbol — 노드 옆에 종류 라벨 (`⋈ Merge` · `⋈ Hash` · `⋈ Nested Loop`)
- Filter/Scan 노드: **σ (sigma)** symbol — 옆에 라벨 (`σ Seq Scan` · `σ Index Scan`)
- Relation 이름: 굵게 (**Partsupp** · **Lineitem** · **Orders** · **Customer**)
- 트리 연결선: **점선 (dashed lines)**
- 트리 root 가 위 (Sort), 잎이 아래 (각 Scan)
- **벡터 테이블** (partsupp_deep) 노드: **cyan 점선 타원** 으로 감싸기 + 옆에 작은 cyan 텍스트 `contains vectors` (또는 `← 벡터`)

**왼쪽 ❌ 잘못된 plan 박스 (빨간 테두리, 현 색 carry)**:
```
                  Sort
                  ⋈ Hash
                  / \
                 /   \
        ⋈ Hash       σ Seq Scan
        / \           Lineitem (~100만 행)
       /   \
  ⋈ Hash    (cyan 점선 타원)
   / \       σ Seq Scan
  /   \      Partsupp_deep ← contains vectors
 σ      σ    (333,333 행 통째 메모리)
 Seq    Seq
 Scan   Scan
 Customer Orders
```
하단 라벨: `큰 중간 테이블 누적 → 메모리·시간 폭주`

**오른쪽 ✓ 정확한 plan 박스 (cyan/blue 테두리, 현 색 carry)**:
```
                  Sort
                  ⋈ Nested Loop
                  / \
                 /   \
       ⋈ Nested      (cyan 점선 타원)
        Loop          σ Index Scan
        / \           Partsupp_deep ← contains vectors
       /   \          (~100 점만)
   ⋈ Nested  σ Index
    Loop     Scan
    / \      Lineitem
   /   \     (on l_orderkey)
  σ      σ
  Index  Index
  Scan   Scan
  Customer Orders (on c_custkey)
```
하단 라벨: `한 행씩 인덱스로 정확히 풀어냄`

**박스 위 라벨** carry: 왼쪽 `❌ 카디널리티 추정 틀림` (빨간) / 오른쪽 `✓ 카디널리티 추정 정확` (cyan).

**하단 carry**: `벡터 테이블 100만 행 · 같은 SQL · 같은 데이터` 가운데 정렬 · `10,000× 응답 시간 차이` hero + `TPC-H Q3 VAQ on DEEP` 메타.

**중요**: ⋈·σ symbol 은 polygonal SVG 아이콘으로 그리거나 유니코드 ⋈ U+22C8·σ U+03C3 사용. 채림님 reference 처럼 ⋈ 가 큰 bowtie 모양·σ 가 시그마 모양으로 명확히 보여야 함. 노드 라벨 (Merge·Hash·Nested Loop·Seq Scan·Index Scan) 은 노드 옆에 작은 sans-serif 텍스트.

레이아웃: 헤더 → ❌ 왼쪽 그래픽 tree + ✓ 오른쪽 그래픽 tree (점선 + ⋈/σ) → cyan 점선 타원으로 벡터 강조 → 10,000× hero (carry).

---

### slide 5 (배경 — Adaptive Sampling 5단계) 메커니즘 명확화

**문제**: 현 slide 5 가 "여러 쿼리에 대해 각 쿼리별 한 번씩 샘플링 → 무작위 베르누이" 인지 "한 쿼리 안에서 여러 번 추정하면서 샘플 개수 조절" 인지 모호하게 보임. 박세은 팀장님 질문 발생.

**정확한 Exqutor §V-B 메커니즘** (reference/analysis/(01) Exqutor 상세분석.md verbatim):
- **한 쿼리** = N개 sample 한 번 추출 → 무작위 베르누이로 카디널리티 추정 → Q-error 계산 (max(추정/실제, 실제/추정))
- **50 쿼리 batch 마다 (UPDATE PERIOD)**: 누적 Q-error 로 조정 인자 δ → 모멘텀 m=0.9 (급변동 방지) → 학습률 η 감쇠 → **다음 batch 의 N 갱신**
- 초기 N=385 (식 1, 통계 신뢰도)
- DEEP·SimSearchNet++: 시간 지나며 N 감소 (안정적) · SIFT: 더 복잡한 분포 → N 증가

**조치**: 현 slide 5 의 ①표본추출 ★ 강조 + 무작위 베르누이 점 시각 carry. 다만 **"한 쿼리 = 한 번 sample → 50 쿼리 batch 마다 N 동적 조정" 메커니즘을 작은 시각 도식으로 추가**.

**추가 도식 spec** (5단계 흐름 하단 또는 옆, 작게 가운데 정렬):

```
Query 1  ─ N₀=385 sample 1회 ─→ Q-error₁
Query 2  ─ N₀=385 sample 1회 ─→ Q-error₂
   ⋮
Query 50 ─ N₀=385 sample 1회 ─→ Q-error₅₀
           ────────────────────────────────
           ↓ 누적 Q-error · 모멘텀 m=0.9 · 학습률 η 감쇠
           ↓ N 갱신 (UPDATE PERIOD = 50 쿼리)
Query 51 ─ N₁ sample 1회 ─→ Q-error₅₁
   ⋮
```

또는 가로 시각 (시간 축):

```
                          ┌─ UPDATE PERIOD = 50 쿼리 ─┐
Query →  1  2  3  ... 50 │ 51  52  53 ...    100 │ 101 ...
N (sample)  N₀ N₀ N₀ ... N₀│  N₁  N₁  N₁  ...  N₁ │ N₂  ...
              ↑                 ↑                    ↑
              초기 N₀=385      누적 Q-error          누적 Q-error
                              로 N₁ 갱신            로 N₂ 갱신
```

**작은 캡션 (도식 하단)**: 
`한 쿼리 = N개 sample 한 번 추출. 50 쿼리 batch 마다 N 자체가 동적 조정됨 (모멘텀 m=0.9 · 학습률 η 감쇠).`

**5단계 흐름 (carry, 변경 X)**: ①표본추출 강조 (purple 굵은 + ★ "본 연구 집중 단계") + 무작위 베르누이 점 (빨간) + 5단계 흐름도. 단 ① 단계 옆 작은 보조 라벨 추가: `한 쿼리당 N=385 sample 1회 추출 (초기) → 50 쿼리마다 N 갱신`.

**중요**: 박세은 팀장님 후자 해석 ("여러 쿼리에 대해 각 쿼리별 한 번씩만 샘플링") 이 정확하며, 추가로 50 쿼리 batch 단위로 N 자체가 갱신된다는 점이 핵심. 이 점이 slide 안에 명확히 드러나야 함.

레이아웃: 헤더 → 5단계 흐름도 (carry · ①표본추출 ★ 강조) → 무작위 베르누이 점 (carry) → **신규 도식: Query ─ sample 1회 → Q-error / UPDATE PERIOD = 50 쿼리 / N 갱신**.

---

### 공통 추가 지시 (모든 3 slide 적용)

1. design system 동결 — 임의 변경 X
2. chapter badge (● 배경) carry — slide 2·3·5 모두 ● 배경 (cyan)
3. 가운데 정렬·여백 carry
4. footer 텍스트 모두 X · 별표 ★ 슬라이드 안 X · 페이지 번호 X carry
5. 이름·약어 통일 — 베이스라인·결합·단독 대체 한국어 carry · B1·CaseA·CaseB 코드명 X
6. ⋈·σ symbol 정확 (slide 3) — 채림님 ICDE_Exqutor slide 15~16 verbatim style

3 slide 수정 후 14 slide 그대로 carry. v18 으로 저장.

▲

(여기까지 복붙용 단일 prompt.)
