# RQ3 설계안: Distribution-Agnostic 층화 샘플링

> 2026-04-16 확정. 7가지 방법 전수 비교.

---

## 연구 질문

**RQ3**: 데이터 분포를 사전에 모를 때, 공간 인식 층화 샘플링(KM20)의 이점을 얼마나 회수할 수 있는가?

## 가설

> **H3**: Distribution-agnostic 방법들은 사전 클러스터링(KM20) 대비 유의미한 비율의 개선 효과를 회수하면서도, 사전 학습 불필요 또는 극소 비용이라는 운영 이점을 제공한다.

## 핵심 지표: Recovery Rate

```
recovery_rate = (방법X - RANDOM20) / (KM20 - RANDOM20)
```

- 1.0 = KM20과 동일 (oracle 수준)
- 0.0 = RANDOM20과 동일 (공간 인식 없음)
- 음수 = RANDOM20보다 나쁨

---

## 3가지 패러다임 × 7가지 방법

### 패러다임 1: Offline Partition (데이터 로드 시 1회 계산)

#### C. Random Projection
- **이론**: Johnson-Lindenstrauss lemma — 랜덤 방향 사영이 거리를 ε 이내로 보존
- **메커니즘**: 랜덤 단위벡터 r 생성 → 각 벡터 v의 사영값 v·r 계산 → K등분
- **구현**: 내적 1회, 가장 단순
- **기대 recovery**: 10~40% (1D로 다차원 구조 포착 한계, RANDOM20과 차이 없을 수도)
- **역할**: 최단순 하한선

#### A. LSH (Locality-Sensitive Hashing)
- **이론**: 해시 충돌 확률이 거리에 반비례 → 가까운 벡터가 같은 버킷
- **메커니즘**: 랜덤 하이퍼플레인 p개 → 2^p 버킷 → 비례 배분
- **구현**: 해시 함수 ~30줄
- **기대 recovery**: 30~60%
- **역할**: 확률적 공간 포착

#### E. Hilbert Curve (Space-Filling Curve)
- **이론**: Hilbert 곡선은 d차원 → 1D 매핑에서 공간 인접성을 최대한 보존. R-tree, 공간 DB에서 30년간 검증.
- **메커니즘**: 벡터 양자화 → Hilbert index 계산 → index 기준 K등분
- **구현**: hilbertcurve 라이브러리 + 양자화
- **기대 recovery**: 20~60% (고차원에서 curse of dimensionality로 하향 가능)
- **역할**: 결정론적 공간 포착. 벡터 카디널리티 추정에 최초 적용.
- **주의**: 96d/128d에서 locality 보존이 약해질 수 있음 → negative finding도 기여

#### F. Mini-batch K-means
- **이론**: Sculley 2010 — 데이터의 1~5%만 보고 근사 클러스터링
- **메커니즘**: sklearn MiniBatchKMeans → 센트로이드 학습 → 나머지 O(d·K) 할당
- **구현**: sklearn 한 줄
- **기대 recovery**: 75~95% (근사 k-means이므로 KM20에 근접)
- **역할**: "얼마만큼의 사전 학습으로 충분한가"에 대한 답. 비용-효과 상한선.

### 패러다임 2: Online Query-Adaptive (쿼리 시점 동적 적응)

#### G. Distance-Shell
- **이론**: 쿼리 벡터 중심 동심원 분할. 카디널리티 조건 충족 행이 내부 shell에 집중.
- **메커니즘**: pilot 샘플(~385개) → 거리 분위수로 K개 shell → shell별 비례 배분 본 샘플
- **구현**: 2-pass (pilot → 본 샘플)
- **기대 recovery**: 25~50%
- **역할**: 단순 적응형. B(KDE)의 단순화 버전.

#### B. KDE-pilot (Kernel Density Estimation)
- **이론**: Silverman bandwidth로 비모수 밀도 추정 → Neyman 최적 배분
- **메커니즘**: pilot 샘플 → KDE로 거리 분포 밀도 추정 → 밀도 높은 영역에 더 많은 샘플 배분
- **구현**: scipy KDE + 2-pass
- **기대 recovery**: 50~80% (쿼리별 최적화이므로 이론적으로 가장 정교)
- **역할**: 정교한 적응형. 이론적 상한.

### 패러다임 3: Weight-based (파티션 없이 가중치 조정)

#### H. Importance Sampling
- **이론**: 최적 importance weight는 f(x)/g(x)에 비례. 층 분할 없이 각 샘플의 가중치를 조정하여 분산 감소.
- **메커니즘**: BERNOULLI로 샘플 추출 → 각 샘플의 로컬 밀도 추정 → 밀도 역수 가중치로 보정된 카디널리티 추정
- **구현**: hook_est 반환 공식 수정 (가중 평균)
- **기대 recovery**: 30~70% (가중치 추정 정확도에 의존)
- **역할**: 비분할 패러다임 대표. 층화와 근본적으로 다른 접근.

---

## 9-way 비교 체계

```
보정 없음           BERNOULLI (Exqutor 원본)
                     │
무의미 하한          RANDOM20 (무작위 분할)
                     │
Offline Partition    ├── C. Random Projection (최단순)
                     ├── A. LSH (확률적)
                     ├── E. Hilbert Curve (결정론적)
                     ├── F. Mini-batch KM (근사 학습)
                     │
Online Adaptive      ├── G. Distance-Shell (단순 적응)
                     ├── B. KDE-pilot (정교한 적응)
                     │
Weight-based         └── H. Importance Sampling (비분할)
                     │
오라클 상한          KM20 (사전 클러스터링)
```

예상 순서: RANDOM20 ≤ C ≤ {A, E, G} ≤ {B, H} ≤ F ≤ KM20

---

## 실험 설계

### 데이터셋
- DEEP 1M (96d) — 상대적으로 균일
- SIFT 1.5M (128d) — 더 skewed

### Selectivity
- 1%, 5%, 10%, 30%, 50% (RQ1/RQ2와 동일 5점)

### 반복
- 5-seed × 100 query (RQ1/RQ2와 동일)

### 측정 지표
- Q-error (hook_est vs true_card)
- paired Wilcoxon p-value
- Recovery Rate

---

## 구현 계획

### Week 1 (4/28~5/4): Offline Partition 3종
- C (RandProj): 구현 ~2시간, 실험 ~2시간
- A (LSH): 구현 ~4시간, 실험 ~2시간
- E (Hilbert): 구현 ~4시간, 실험 ~2시간
- F (MiniBatch): 구현 ~1시간, 실험 ~2시간

### Week 2 (5/5~5/11): Online + Weight
- G (DistShell): 구현 ~4시간, 실험 ~3시간
- B (KDE-pilot): 구현 ~6시간, 실험 ~4시간
- H (Importance): 구현 ~6시간, 실험 ~3시간

### Week 3 (5/12~5/18): 분석
- Recovery Rate 비교 그래프
- 패러다임 간 cross-analysis
- 비용-효과 분석 (사전 학습 시간 vs recovery)

### Week 4 (5/19~5/27): 최종 발표 준비
- 최종 보고서 작성
- 발표 슬라이드
- 포스터

---

## 논문 기여 3가지

1. **체계적 비교**: 벡터 카디널리티 추정에서 distribution-agnostic 7가지 방법의 최초 체계적 비교
2. **Recovery Rate 프레임워크**: oracle(KM20) 대비 회수율 개념 도입, 비용-효과 정량 평가
3. **Hilbert Curve 최초 적용**: 공간 DB 기법(space-filling curve)을 벡터 카디널리티 추정에 적용

---

## 맹점 점검 완료 사항

- 층화 프레임 갇힘 → H(가중치)로 커버
- 실험 세팅 특수성 → B/G의 2-pass는 Python에서 해결
- 방법 간 조합 → 개별 먼저, 조합은 후속 연구
- 기대 효과 과대평가 → Hilbert/RandProj는 고차원 한계 가능, negative도 기여
- Feedback 기반 → Exqutor Adaptive가 커버, Phase 7 negative로 제외 근거
- 7가지 외 독립 방법 부재 확인 (I/J/K/LHS/Tree/Balanced/Coreset/MAB 전부 기존 7가지의 변형 또는 범위 밖)
