# Capstone — 속도는벡터

연세대학교 2026-1학기 인공지능종합설계

## 연구 주제

**Skew-Aware Stratified Sampling for Vector-Augmented Analytical Query Optimization**

Exqutor 논문(arXiv:2512.09695v2) 기반 — 벡터 데이터의 공간 밀도 비균일성(쏠림)이 uniform sampling의 카디널리티 추정 정확도를 저하시키는 문제를 실증하고, 공간 인식 stratified sampling(KM20)으로 이를 개선한다.

### 핵심 결과

- **RANDOM20 Selectivity Gradient**: 공간 인식 KM20 vs 무작위 RANDOM20 비교 시, query 범위가 좁을수록(=데이터가 특정 영역에 집중될수록) 공간 인식의 중요성이 급증 (s=0.010에서 19.6%p 차이)
- **Two-Level Decomposition**: stratified sampling의 개선 메커니즘을 proportional allocation(보편적) + spatial awareness(selectivity-dependent)로 분리·정량화
- **KM20 Stratified**: BERN 대비 +1.64% CI [1.25, 2.02] (5-seed, p<0.004)

## 팀원

| 이름 | 역할 | GitHub |
|------|------|--------|
| 박세은 (팀장) | | [@triangle-park](https://github.com/triangle-park) |
| 강재현 | | [@newagency](https://github.com/newagency) |
| 조현빈 | | [@johyunbin](https://github.com/johyunbin) |
| 이동욱 | | [@dlee004](https://github.com/dlee004) |

**지도교수**: 박광현 교수님 (BDAI 연구실)
**멘토**: 박성원

## 디렉토리 구조

```
experiments/          실험 코드, 결과, 시각화
  code/rq1/           서버 실행 스크립트 (Phase 4~7, RANDOM20, HHI)
  results/rq1_motivation/  실험 결과 (JSON, parquet, 분석 md)
  figures/             시각화 (boxplot, heatmap)
research/
  papers/              원논문 PDF (69편)
  summaries/           논문별 총정리 (82편)
  analysis/            심층분석 시리즈 (01)~(12)
plans/                 연구 설계안 (v3→v4→재설계안)
records/
  kakaotalk/           카카오톡 회의록 + 톡방 공유
  weekly/              주간보고
submission/            제출물 (보고서, 슬라이드, 자문이메일)
templates/             캡스톤 양식 + 예시 PDF
scripts/               md2pdf, 데이터 전처리 (Stage 1~5)
```

## 일정

| 마감 | 제출물 | 상태 |
|------|--------|------|
| 4/28 | **중간발표 + 중간보고서** | 준비 중 |
| 5/27~29 | 최종발표 + 전시회 | |
| 6/11 | 최종보고서 | |

## 참고

- [Exqutor 논문](https://arxiv.org/abs/2512.09695v2)
- [Exqutor GitHub](https://github.com/BDAI-Research/Exqutor)
- [캡스톤 사이트](https://capstone.cs.yonsei.ac.kr/capstone/)
- [팀 Notion](https://www.notion.so/306db4d4869b8039affeca0b0fa4d2fa)
