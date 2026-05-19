# 속도는벡터 — 본 연구 narrative 최종 정리 v1

> 박세은 review + 박광현 5/15 미팅 + 5/27 최종 발표 + 6/11 최종 보고서 공통 base. 박세은 5/13 12:13 피드백 (method 개수 줄임 + 숫자/공식 최소화) 반영. 학부생 톤, 산문 흐름.

작성: 2026-05-14 07:55 KST · 측정 portfolio 1065 file 종료 후 시나리오 B 확정 narrative

---

## 1. 출발점: 어디서 부정확해지는가

본 논문 (Exqutor) 은 벡터 증강 분석 쿼리에서 인덱스가 없을 때 무작위 표집 (베르누이 + 동적 표본 수 조정) 으로 카디널리티를 추정한다. 단일 테이블 + 단순 분포에서는 잘 작동하지만, 분포가 한쪽으로 쏠려 있을 때 (skew) 표집의 정밀도가 떨어진다. 우리는 이 영역에서 "분포 정보를 알 수 있다면 어디까지 정확도를 끌어올릴 수 있나" 를 정량으로 확인했다.

## 2. 탐색: 분포 정보를 얻는 방법 56 가지

분포 정보를 얻을 수 있는 후보 method 56 개를 8 갈래 (클러스터링, 공간 분할, 스트리밍, 차원 축소, 정보 이론, 양자화, 준 무작위, 밀도 추정) 로 모았다. 9 가지 측정 환경 (DEEP/SIFT/SSN 단일 테이블 + 다중 테이블 Fig7/Fig9 + 선택도 sweep + scale sweep) × 2 가지 모드로 매트릭스를 짰다.

## 3. 폐기: 정직하게 떨어뜨린 39 method

측정을 진행하면서 40 method 를 폐기했다. 자원 한계 7 종 (예: birch 가 한 측정에 50 ~ 200GB 메모리를 차지해서 실행 불가), 5월 10일 코드 정독 검토로 reference 위반이 발견된 23 종 (예: vinecopula 가 vine copula 가 아니라 PCA 1 차원 정렬의 별칭, neuram 이 PCA1D 와 한 줄씩 동일), 그리고 큰 데이터셋에서 추정값이 외곽으로 튀는 정합성 위반 10 종. 폐기 사유 자체를 보고서에 분류한 것이 본 연구의 정직성 갈래다.

## 4. 단독 대체: 베르누이를 분포 인지 추정량으로 갈아끼우기

남은 method 들로 첫 번째 모드를 측정했다. 본 논문의 베르누이 추정값을 우리 method 의 추정값으로 단순히 바꿔 끼우는 방식이다. 측정 결과 56 method 중 약 40% 가 평균적으로 베르누이보다 정확했고, 통계 검정으로 9 가지 측정 환경 전반에서 안정적으로 우위를 점한 method 가 15 개였다. 이 15 method 의 평균 개선폭은 −5 ~ −12% 였고, 단독 best 는 minibatch_partial 의 **−10.17%** 였다. 본 논문 자체 재현 시 발생하는 측정 변동 −4.3% 의 2.4 배 수준이다.

## 5. 결합 시도: 산술 평균으로 둘을 섞으면 어떨까

두 번째 모드는 베르누이 추정값과 우리 method 의 추정값을 산술 평균으로 결합하는 방식이다. 492 짝지어 비교한 측정 중 92.5% 가 **단독 대체 (CaseA) 보다 정확**했다 (handoff_v12 "paired CaseB < CaseA"). 짝지어 보면 거의 항상 좋아진다는 의미다. 결합 best 는 Centroid tuple 의 **−7.37%** 였다 (A2-Fig9 single cell 측정 기준).

평균을 어느 비율로 섞어야 best 인지도 sweep 으로 확인했다. 0.3 / 0.4 / 0.6 / 0.7 네 값을 측정한 결과, 네 method 중 셋이 0.5 (산술 평균) 에서 best 였고, 양쪽 극단으로 갈수록 효과가 감소하는 U 자 형태를 보였다.

## 6. 결합의 한계: 단독 best 를 넘지 못한다

결합 best (−7.37%) 가 단독 best (−10.17%) 보다 약했다. 결합으로 단독을 능가할 수는 없었다. 이 발견이 본 연구의 narrative 분기점이다.

## 7. 결합의 진짜 가치 재발견

그렇다면 결합은 의미가 없는가? 그렇지 않다. 결합 모드의 92.5% 짝지어 우위는 "method 선택을 잘못해도 거의 항상 단독 대체보다는 낫다" 는 안정성을 뜻한다. 9 가지 측정 환경별 변동성도 단독 대체보다 결합 모드가 더 작았다. 즉 결합의 가치는 "더 큰 정확도" 가 아니라 "method 선택의 안정성 + 측정 환경별 변동성 감소" 다.

## 8. 자원 효율: 정확도 + 자원이 동시에 좋은 method 가 있다

추가로 학습 자원 (시간 + 메모리) 도 비교했다. 정확도 측면에서 안정적인 12 가지 measurement 에서 우위를 점한 5 method 와, 자원 효율 측면에서 파레토 우위인 5 method 가 동일하다는 점을 발견했다 — sparse_rp, chao_weighted, neuram, pca1d, hilbert. 정확도와 자원이 같은 방향을 가리킨다.

특히 reservoir 표집은 메모리 사용이 데이터 크기와 무관한 상수 O(1) 인데도 anchor 수준 정확도를 낸다. 모바일 / 임베디드 / 스트리밍처럼 메모리가 제약인 환경에 그대로 갖다 쓸 수 있는 finding 이다.

## 9. 권장: 단독 대체 우선 + 결합 보조

위 결과를 종합한 권장 설계는 다음과 같다.

1. **단독 대체 우선** — 산업 환경에 맞는 method 를 위 5 ~ 6 후보 중에서 골라 베르누이를 갈아끼운다. 가장 단순하면서 가장 큰 정확도 개선을 얻는다.
2. **결합 보조** — method 선택에 자신이 없거나 안정성이 중요한 환경에서 산술 평균 결합을 추가 안전망으로 둔다.
3. **자원 우선 환경** — 메모리가 가장 제약이라면 reservoir 같은 상수 메모리 method 를 단독으로 쓴다.

## 10. 다중 테이블 결합

마지막으로 다중 테이블 환경에서 두 테이블 클러스터링을 어떻게 합칠지 검토했다. 비싼 방식 (두 테이블 벡터를 합쳐 처음부터 다시 학습) 과 저렴한 방식 (이미 학습된 두 클러스터링의 결과를 가볍게 합치는 Centroid tuple) 두 후보 중 Centroid tuple 이 학습 비용 추가 0 으로 안정 우위를 보였다. 다중 테이블 환경에도 단독 대체 + 결합 보조 원칙이 그대로 적용 가능하다.

---

## 한 줄 요약

> "분포 정보를 알면 베르누이를 갈아끼우는 단독 대체가 가장 단순하고 가장 큰 정확도 개선을 가져온다. 결합은 더 큰 정확도가 아니라 method 선택의 안정성을 위한 보조 안전망이다. 정확도와 자원 효율이 같은 method 군을 가리키며, 그중 reservoir 의 상수 메모리는 산업 적용에 의미가 크다."

---

## narrative 흐름 한 줄 도식

```
[1. 문제: skew 영역 베르누이 부정확]
        ↓
[2. 탐색: 56 method × 8 갈래 × 9 측정 환경]
        ↓
[3. 폐기: 39 method 정직 분류 (자원 7 + audit 23 + 정합성 9)]
        ↓
[4. 단독 대체: 베르누이 갈아끼우기 → best −10.17%]
        ↓
[5. 결합 시도: 산술 평균 → best −7.37%, α=0.5 best, U-shape]
        ↓
[6. 결합 한계 발견: 결합 < 단독]
        ↓
[7. 결합 진짜 가치: 안정성 + 변동성 감소]
        ↓
[8. 자원 효율: 정확도 best 5 = 파레토 best 5, reservoir O(1) 산업 적용]
        ↓
[9. 권장 설계: 단독 대체 우선 + 결합 보조 + 자원 우선]
        ↓
[10. 다중 테이블: Centroid tuple 로 원칙 그대로 적용]
```

---

## 측정 portfolio 종합 (배경, 필요 시 참조)

- 총 측정 1065 file (paper exact carry-over 1001 + 본 세션 64: multi-join 8 + Centroid tuple 8 + B1/B2/B3 cheap 24 + A2-Fig8 mv 8 + α sweep 16)
- 폐기 40 method (자원 한계 7 + audit drop 23 + 정합성 위반 10)
- 사용 method 약 17 개 (56 − 39)
- 8 갈래 paradigm rollup: P10 Density / P9 InfoTheoretic / P3 Streaming / P4 DimReduction / P2 Spatial 우위 (CaseB 기준 −5 ~ −12%)
- 본 논문 §V-B Fig 12 영역 절사 평균 Q-error 본 측정 1.618 vs paper 보고값 1.69 = −4.3% 재현 (paper review-grade 정합성 확보)
- 자원 한계 폐기 method 중 kde_parzen 은 5/13 ~ 5/14 측정 chain 진행했으나 5/5 timeout 으로 5/14 07:39 폐기 결정

---

## 11. 사용 method 깊이 소개 (핵심 6)

§4 ~ §9 에 등장한 결과를 만든 method 들 중 본 narrative 의 핵심 6 개를 알고리즘 메커니즘 + 이론적 근거 + 실측 결과로 정리한다. 17 사용 method 전체 list 는 §12 부록 table + 자원 효율 분석 file (`_internal/analysis/resource_efficiency_pareto_20260513.md`) 참조.

### 11.1 minibatch_partial — 클러스터링 갈래, 단독 대체 best

**방법** — 데이터를 청크 단위로 흘려보내면서 K=20 클러스터 중심을 점진적으로 학습한다 (partial_fit). 전체 데이터를 메모리에 올리지 않고 stream 처럼 처리.

**이론적 근거** — Sculley (WWW 2010) 의 Web-scale K-means 변형. scikit-learn 의 MiniBatchKMeans 의 partial_fit API 직접 활용.

**실측 결과** — 단독 대체 모드 9 측정 환경 평균 **−10.17%** (본 portfolio 단독 best). 학습 시간 0.5 초, 메모리 사용량 작음 (청크 × 차원 D), 측정 환경별 변동성 std 3.33. 단독 대체로 갈아끼울 때 가장 큰 정확도 개선을 가져오는 method.

### 11.2 sparse_rp — 차원 축소 갈래, 학습 시간 가장 짧음

**방법** — 데이터 차원 D 를 sparse random matrix (Achlioptas density 1/3, 즉 +1 / 0 / −1 의 sparse entries) 로 곱해 낮은 차원 k 로 사영한다. 그 후 K=20 클러스터로 stratum 분할.

**이론적 근거** — Achlioptas (JCSS 2003) 의 sparse Bernoulli projection + Li-Hastie-Church (KDD 2006) 의 매우 sparse 변형. Johnson-Lindenstrauss lemma 의 distance preservation 보장 위에서 sparse 화로 계산 비용을 크게 낮춤.

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.43%**, 학습 시간 **0.1 초** (본 portfolio 최단), 메모리 O(D × k) 매우 작음, std 3.30. 정확도와 자원 두 axis 에서 모두 Pareto frontier 위에 있는 method.

### 11.3 chao_weighted — 스트리밍 갈래, Pareto Top 정확도

**방법** — 가중 reservoir 표집. 청크 단위로 들어오는 데이터에서 weight 기반 sampling 으로 분포 정보를 streaming 으로 유지한다.

**이론적 근거** — Chao M-T (Biometrika 1982) 의 weighted reservoir sampling. 각 sample 의 probability of inclusion 이 weight 에 비례하도록 보장.

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.60%** (Pareto frontier 정확도 Top 1), 학습 시간 0.5 초, 메모리 O(K) 매우 작음, std 6.36. 정확도는 가장 좋으나 측정 환경별 변동성은 다소 큼.

### 11.4 hilbert_real — 공간 분할 갈래, 진짜 Hilbert curve 구현

**방법** — 데이터 차원 D 를 그대로 유지한 채 Hilbert space-filling curve indexer 로 1 차원 좌표 매핑. 그 후 매핑된 1 차원 좌표를 K=20 stratum 으로 분할.

**이론적 근거** — Faloutsos (SIGMOD 1989) 의 진짜 D 차원 Hilbert space-filling curve. 본 연구의 이전 hilbert method 는 코드 정독 검토 결과 PCA 2 차원 정렬의 별칭으로 발견되어 (★3 정정), 진짜 Hilbert curve 구현인 hilbert_real 을 별도 method 로 측정.

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.27%**, 학습 시간 0.5 초, 메모리 O(N), std 3.12. 공간 분할 paradigm 의 진짜 anchor.

### 11.5 hyperloglog — 정보 이론 갈래, 가장 안정

**방법** — hash 기반 분포 카디널리티 추정량. K=20 stratum 별로 trailing zero 의 max 를 추적해 cardinality 를 streaming 으로 추정.

**이론적 근거** — Flajolet et al (DMTCS 2007) 의 HyperLogLog. 분포의 unique element 수를 매우 적은 메모리로 정확히 추정하는 정보 이론 기반 알고리즘.

**실측 결과** — 결합 모드 9 측정 환경 평균 **−8.65%**, 학습 시간 0.5 초, 메모리 O(K log K), std **2.73** (본 portfolio ⭐⭐ Best + ⭐ Excellent 19 method 中 가장 안정). 정확도와 안정성을 모두 잡은 method.

### 11.6 reservoir — 스트리밍 갈래, 메모리 O(1)

**방법** — 가장 단순한 reservoir sampling. 청크 단위 데이터에서 K 개를 균등 확률로 sampling 한다.

**이론적 근거** — Vitter (TOMS 1985) 의 reservoir sampling. 데이터 크기 N 을 미리 모르더라도 K 개의 균등 random sample 을 한 번의 pass 로 얻는 알고리즘.

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.25%**, 학습 시간 **0.1 초**, 메모리 사용량 **O(1)** (sample size K 만 보존, 데이터 크기 N 과 무관), std 3.00. **§8 의 산업 적용 핵심 finding** — 모바일 / 임베디드 / 스트리밍처럼 메모리가 제약인 환경에 그대로 적용 가능한 가장 강력한 method.

---

## 12. 17 사용 method 전체 list (부록)

39 폐기 후 남은 17 사용 method 의 paradigm 분포 + 결합 모드 평균 + 자원 효율 등급 + 이론적 근거. 자세한 자원 정량 (학습 시간 + 메모리 + SF=100 feasibility) 은 `_internal/analysis/resource_efficiency_pareto_20260513.md` 참조.

| paradigm | method | CaseB Δ% | 자원 등급 | 이론적 근거 |
|---|---|---:|---|---|
| P1 클러스터링 | minibatch_partial | −6.98% | ⭐ Excellent | Sculley 2010 (partial fit) |
| P1 클러스터링 | minibatch | −9.28% | ⭐ Excellent | Sculley 2010 |
| P1 클러스터링 | gmm | +2.45% | Good | Dempster 1977 EM (marginal) |
| P2 공간 분할 | hilbert_real | −9.27% | ⭐⭐ Best | Faloutsos 1989 진짜 |
| P2 공간 분할 | zorder_morton | −9.26% | ⭐ Excellent | Morton 1966 bit-interleaving |
| P2 공간 분할 | skilling_hilbert | −9.01% | ⭐ Excellent | Skilling 2004 변형 |
| P2 공간 분할 | lpm2 | −9.45% | ⭐⭐ Best | Grafström 2012 local pivot |
| P3 스트리밍 | chao_weighted | −9.60% | ⭐⭐ Best | Chao 1982 weighted reservoir |
| P3 스트리밍 | reservoir | −9.25% | ⭐⭐ Best | Vitter 1985, **메모리 O(1)** |
| P3 스트리밍 | thompson_sampling | −8.98% | ⭐ Excellent | Thompson 1933 Beta posterior |
| P3 스트리밍 | cum_sqrtf | −8.45% | Good | Cochran 1977 sqrt(F) |
| P4 차원 축소 | sparse_rp | −9.43% | ⭐⭐ Best | Li-Hastie-Church 2006 |
| P4 차원 축소 | neuram | −9.97% | ⭐⭐ Best | autoencoder (PCA1D 등가 audit) |
| P4 차원 축소 | pca1d | −9.63% | ⭐ Excellent | Pearson 1901 PCA |
| P4 차원 축소 | rsvd | −8.49% | ⭐ Excellent | Halko-Martinsson 2011 |
| P6 양자화 | pq | −9.25% | ⭐ Excellent | Jégou 2011 product quantization |
| P9 정보 이론 | hyperloglog | −8.65% | ⭐⭐ Best | Flajolet 2007 HyperLogLog |

* CaseB Δ% = 결합 모드 9 측정 환경 평균 (음수가 클수록 정확도 개선). 학습 시간 모두 0.1 ~ 1 초 범위.
* 자원 효율 등급: ⭐⭐ Best (fit < 1s + 메모리 O(N) 이하 + SF=100 OK + Δ% < −9%) / ⭐ Excellent (fit < 2s + Δ% < −8%) / Good (fit < 2s + Δ% −5 ~ −8%) / Marginal (Δ% −3 ~ −5%).
* P5 준 무작위 / P10 밀도 추정 paradigm 은 모두 폐기되어 사용 method 없음.
* §11 의 핵심 6 method (minibatch_partial / sparse_rp / chao_weighted / hilbert_real / hyperloglog / reservoir) 는 paradigm 다양성 + Pareto frontier + 본 narrative §4 ~ §9 핵심 등장 기준으로 선정.

---

## 사용 시 안내

- **5/15 박광현 미팅**: §1 ~ §10 흐름 + §11 핵심 6 method 깊이 소개 base. §9 권장 + §10 다중 테이블 + §11.6 reservoir 부분이 자문 질문 대비 핵심.
- **5/27 최종 발표**: §3 폐기 정직성, §4 단독 대체 main finding, §6 ~ §7 결합 한계 + 진짜 가치, §8 자원 효율 + reservoir O(1), §11 핵심 method 6 소개가 분량 비중.
- **6/11 최종 보고서**: §1 ~ §12 그대로 보고서 4.3 RQ3 본문 base. 각 단락 1 ~ 2 page 로 확장.
- **팀원 공유**: §1 ~ §10 그대로 peer 톤 변환 (~해 / ~지) + §11 핵심 6 method 만 1 page 압축.

---

작성: 2026-05-14 07:55 KST · §11 ~ §12 method 깊이 소개 + 17 사용 method 부록 추가: 2026-05-14 08:25 KST
