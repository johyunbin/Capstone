# 다음 단계 (5/9 morning trigger checklist)

1. **⭐⭐⭐ 5/9 morning 4 측정 회수 + 분석** (~30분, 본 §0 진입 즉시)
   - flag 점검: `ssh capstone "ls /tmp/*_done.flag"` (4 flag 기대)
   - 결과 회수: Multi paradigm 11 method (33 csv) + Multi SF10 Adaptive + YFCC sf10 K-sweep (4 parquet) + Multi SF1 setup (3-6 parquet)
   - `analyze_multi_paradigm.py` 실행 → master_v6 §10.6 fill (agent 위임)
   - master_v6 §10.5 의 YFCC sf10 row update (K-sweep 보강)

2. **⭐⭐⭐ 자문 메일 v4 박성원 멘토 finalize + 발송 ready** (~10분, 5/9 morning)
   - `submission/_drafts/속도는벡터_자문메일_박성원멘토_20260508_v4.md` 의 §2 Multi 결과 fill
   - PDF 변환: `python3 scripts/md2pdf.py`
   - 사용자 review → 5/15~5/20 박성원 멘토 발송 결정

3. **⭐⭐ P1 즉시 task 4종** (5/10 일, ~3h 합산)
   - MinHash 측정 (P5 hashing 보강, ~0.5h) — LSH Wave 0 fail 의 직접 보강
   - per-stratum BERN per-K 재분석 (~2h, 분석만, 기존 cache 재사용)
   - Tier 2 (birch, kde_pilot) narrative 정정 (~0h, 문서만) — 강재현 audit 결과 kde_pilot KM20 leak
   - Adaptive 회수 + 4강 paired Δ% 점검 (~10분)

4. **⭐⭐ 5/27 발표 준비** (W3~W4, 5/13 ~ 5/26)
   - Slide redesign 안 적용: `_internal/slide_redesign_v2_20260508.md` (515 lines, 16→18 page, S6.5/S10.5 신규)
   - Adaptive×4강 Ensemble (matched-budget mode B, ~5h, 5/13 evening)
   - K-aware sweep 확장 (SIFT/SSN/WIKI/YFCC × 2 SF × 4K = 32 cell, ~15h, 자문 회신 후)
   - 5/22 박광현 교수님 미팅 reflection

5. **⭐ SF100 (80M) 실험 = scope 제외** (5/8 22:16 사용자 결정) — SF1/SF10 만으로 본 연구 narrative 완결, SF100 은 future work 으로 보고서 limitation 명시

6. **⭐ 6/11 최종보고서 drafting** (W5~W6, 5/29 ~ 6/10, ~40h)
   - Outline v2 base (`plans/최종보고서_outline_v2_20260508.md`, 516 lines)
   - 4 팀원 분담 (박세은 통합 / 조현빈 §3 §4.1 / 이동욱 §2 §4.2 / 강재현 §4.3)
