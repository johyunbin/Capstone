# 04_multi_vector_concat — 다중 벡터 결합(concatenation)

두 데이터셋의 벡터를 **이어붙인(concatenation) 다중 벡터** 컬럼에서의 16-method 측정.
단일 벡터(트랙 02)에서 확인한 결합 효과가 다중 테이블/다중 컬럼 상황에서도
일반화되는지 검증한다.

- file 357개 (3 concat 쌍 × sf × sel{0.001,0.01,0.10} × 16 method + B1)
- concat 조합:
  - `DEEP+SIFT_concat_sf{1,10,100}` — 96d + 128d = 224d
  - `DEEP+WIKI_concat_sf{1,10}` — 96d + 768d = 864d
  - `DEEP+YFCC_concat_sf{1,10}` — 96d + 192d = 288d
- 구조: `{A}+{B}_concat_sf{n}/sel{...}/{mode}/{파일}.json`
- 출처: server 측정 `concat_track_0537`

> sel 3종 모두 측정되어 트랙 03(sel sweep)의 다중 벡터 버전 역할도 겸한다.
