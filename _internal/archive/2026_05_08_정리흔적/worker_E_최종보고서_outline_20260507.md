# Worker E — 6/11 최종 보고서 outline 작성

> **임무**: 6/11 최종 보고서 (D-35) 의 outline 작성. 중간보고서 (4/28 제출본) + 종합 master + 5/27 발표 outline 통합 → 6/11 보고서 구조 + 분량 + 핵심 figure/table.
> **세션 진입**: 본 핸드오프 첫 read → 입력 4종 read → outline 작성.
> **manager 세션**: 2026-05-07 11:20 KST, Opus 4.7 1M.

---

## 1. 입력 자료

| 파일 | 위치 | 활용 |
|------|------|------|
| 중간보고서 (4/28 제출본) | `submission/_drafts/속도는벡터_중간보고서_*.{docx,pdf}` | 기존 구조 + scope 보존 |
| Master 종합 | [experiments/results/RQ1_RQ2_RQ3_종합_master.md](../experiments/results/RQ1_RQ2_RQ3_종합_master.md) | contribution 7 + Limitations 6 + 통계 결과 |
| 5/27 slide outline | [submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md](../submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md) | narrative flow + figure list |
| RQ3 16-method 종합 | [experiments/results/rq3_agnostic/RQ3_16method_종합.md](../experiments/results/rq3_agnostic/RQ3_16method_종합.md) | RQ3 detail |
| RQ1_RQ2 정리 | [experiments/results/RQ1_RQ2 실험 결과 정리.md](../experiments/results/RQ1_RQ2%20실험%20결과%20정리.md) | RQ1+RQ2 detail |
| 학교 양식 | `templates/` | 페이지 spec |

## 2. 작업 단계

### Step 1 (30분) — 중간보고서 구조 분석

```bash
# 중간보고서 PDF read 후 section / 페이지 분량 / figure 위치 파악
open submission/_drafts/속도는벡터_중간보고서_*.pdf
```

본 분석으로:
- 이미 작성된 section (introduction, related work, methodology) → 보존
- 갱신 필요 section (results, discussion) → 5/7 narrative 반영

### Step 2 (1h) — outline 작성

권장 구조 (학술 보고서 표준 + 캡스톤 학교 양식 결합):

```
# 6/11 최종 보고서 outline

## 0. Front matter (2-3p)
- Title page (학교 양식)
- Abstract (한글 250자 / 영문 200 words)
- Table of contents
- 그림/표 목차

## 1. Introduction (3-4p)
- 1.1 연구 배경 (Vector DB + Exqutor)
- 1.2 문제 정의 (BERN 부정확성 — Selectivity-dependent)
- 1.3 연구 질문 RQ1/RQ2/RQ3 (5/5 재정립 narrative)
- 1.4 본 연구의 기여 (contribution 7종 preview)
- 1.5 보고서 구성

## 2. Background & Related Work (3-4p)
- 2.1 Vector DB indexing — IVF / PQ / HNSW
- 2.2 Stratified Sampling — Neyman / Anti-Neyman / Proportional
- 2.3 Exqutor 분석 — ECQO + Adaptive Sampling (선행 연구)
- 2.4 본 연구의 위치 — 단일 테이블 정확성 layer

## 3. Methodology (4-5p)
- 3.1 측정 환경 (서버 + dataset + query pool)
- 3.2 RQ1 measurement design — Block vs Row × Normal vs Skew 2x2
  - Phase 6 (SQL D, vector.c hook, production-near) vs Phase 7 (numpy D, simulation)
  - methodology robustness sub-contribution motivation
- 3.3 RQ2 measurement design — 5 mode (BERN / Equal / Proportional / Neyman / Anti-Neyman)
  - KM20 oracle baseline (K-means K=20, PG 직접 query 일치 확인)
  - sample size sensitivity (4 ssize × 2 dataset × 5 sel)
- 3.4 RQ3 measurement design — 22 method 4 paradigm
  - Offline cluster (KM20 / minibatch / minibatch_partial / hdbscan / gmm / birch / spectral)
  - Locality (hilbert / zorder / hybrid)
  - Projection (random_proj / sparse_rp / pca1d)
  - Tree (kdtree / pq)
  - Online weight (kde_pilot / distance_shell / IS variants)

## 4. Results (10-12p, 핵심 section)
- 4.1 RQ1 — Selectivity Gradient 단조성 통계 입증
  - Figure 1: 2x2 (Block vs Row × Normal vs Skew) 결과
  - Figure 2: 5-sel KM20-BERN gradient (Phase 6 production-near)
  - Table 1: per-seed Spearman ρ (DEEP-KM20 / DEEP-RAND / SIFT-KM20 / SIFT-RAND)
  - **Sub 4.1.1**: Phase 6/7 5-cell 격차 (옵션 2 정직 reporting, 5/7 W2)
    - Figure 3: Phase 6 vs Phase 7 bar chart (Worker D 산출)
    - Table 2: 5-cell delta + per-seed ρ
- 4.2 RQ2 — KM20 oracle robustness + Allocation ablation
  - Figure 4: 40 cell heatmap (4 ssize × 2 dataset × 5 sel)
  - Figure 5: 5-mode allocation 비교 (BERN / Equal / Prop / Neyman / Anti-Neyman)
  - Table 3: Anti-Neyman vs Proportional CI (DEEP / SIFT × 5 sel)
- 4.3 RQ3 — 22 method distribution-agnostic 비교
  - Figure 6: 22 method bar chart (4강 ★)
  - Figure 7: Hilbert vs Z-order locality mechanism (inverse Manhattan / stratum compactness)
  - Figure 8: Method orthogonality ARI matrix (16 method)
  - Figure 9: Per-query rank scatter (어려운 query routing 가치)
  - Table 4: Cohen's d + paired CI (22 method)
  - Table 5: Negative control (PQ / Sobol / IS)

## 5. Discussion (4-5p)
- 5.1 본 연구의 주 contribution 7종 학술 위치 (자문 의견 반영)
  - RQ1 단조성 통계 입증 (publishable contribution)
  - RQ1-sub Measurement Methodology Robustness
  - RQ2 KM20 sample-size robustness
  - RQ3 4강 (Hilbert / partial / HDBSCAN / Hybrid)
  - RQ3 negative control 가치
- 5.2 Honest Limitations 6종 + 향후 보강
- 5.3 Production deployment 권고 (OLTP partial_fit + learning-free Hilbert)

## 6. Conclusion + Future Work (1-2p)
- 6.1 결론 (한 문단)
- 6.2 Future work 우선순위
  - 단일 → 멀티 (Exqutor multi-relation)
  - vector.c integration
  - Distribution shift 적응
  - Phase 6/7 root cause 정량 (5/7 NEW)

## 7. References (1-2p)
- Exqutor (arXiv:2512.09695v2)
- pgvector / VBASE / DuckDB
- Stratified sampling 표준 reference
- Hilbert curve / Z-order indexing
- HDBSCAN / GMM clustering
- 자문 의견 반영 references

## 8. Appendix (3-5p, 선택)
- A. 측정 raw 결과 표 (모든 cell)
- B. ARI matrix full (16 method)
- C. 코드 architecture summary
- D. 자문 의견 (채림 석사 + 지도교수) 직접 인용
```

전체 분량 추정: **30-40p** (학교 양식 따름).

### Step 3 (30분) — 분담 plan + W3 sprint plan

각 section 의 작업 분담 (4 팀원):
- 박세은 (팀장): Introduction + Conclusion + 보고서 통합 / 검토
- 조현빈: RQ1 + RQ1-sub (Phase 6/7) + Methodology + Results 4.1
- 강재현: RQ3 + Methodology + Results 4.3
- 이동욱: RQ2 + Background + Results 4.2

W3 sprint (5/29~6/4): 각 section drafting
W4 sprint (6/5~6/10): 통합 + 검토 + figure 통일 + 양식 적용
6/11: 최종 검토 + 제출

### Step 4 (15분) — outline commit

```bash
git add plans/최종보고서_outline_v1_20260507.md
git commit -m "6/11 최종 보고서 outline v1 — 8 section, 30-40p, contribution 7종 + Limitations 6종 반영"
git push
```

## 3. 산출 spec

| 산출 | 위치 | 형식 |
|------|------|------|
| Outline v1 | `plans/최종보고서_outline_v1_20260507.md` | 8 section + 분담 plan + W3/W4 sprint |
| (선택) skeleton draft | `submission/_drafts/속도는벡터_최종보고서_skeleton_v0_20260611.md` | section 별 placeholder + 첨부 figure list |

## 4. 검증 기준

- [ ] 학교 양식 (templates/) 호환성 (페이지 분량 + 폰트 + 양식 명시)
- [ ] contribution 7종 + Limitations 6종 narrative 일관 (master.md 1:1)
- [ ] 5/27 발표 narrative flow 와 보고서 narrative flow 의 정합 (RQ1→RQ2→RQ3)
- [ ] 자문 의견 (채림 석사 + 지도교수) 반영 위치 명시 (5.1, 6.2)
- [ ] 분담 plan (4 팀원) + W3/W4 sprint plan

## 5. 의존성

- **5/8 회의**: narrative final 합의 (옵션 2 + contribution 7종)
- **5/22 미팅**: 지도교수 자문 (자문 의견 반영 위치 가이드)
- **5/27 발표**: 발표 narrative final → 보고서 narrative 일관
- **Worker A**: 발표 deck export → 보고서 figure 일부 재사용 가능
- **Worker B/C**: 자문 의견 반영 (5.1 학술 위치, 6.2 future work 우선순위)

## 6. 예상 시간

총 2-3h (outline + skeleton draft).
- outline only: 1.5h
- skeleton draft 포함: 2.5-3h

## 7. 본 worker 가 만들지 말 것

- 본문 직접 작성 (W3 sprint 의 분담 작업)
- 새 contribution 임의 추가 (master.md 7종 보존)
- 양식 임의 변경 (학교 양식 templates/ 보존)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 11:20 KST
**기반**: 중간보고서 (4/28) + master commit 74d6aea + slide outline + 5/5 회의 RQ 재정립
