# Multi 4강 분석 sub-agent 호출 prompt (STAGE 3 완료 즉시)

> 5/8 19:00 회의까지 ~2h 미만. STAGE 3 (multi_join deep_wiki) 완료 → 즉시 호출.

---

## Sub-agent 호출 prompt

```
multi_4kang_supplement 측정 결과 분석 + master_v6 §multi 보강 + PPT slide 11 hardcoded update.

Context: 5/8 19:00 비대면 회의 finalize 자료 준비. 단일 100% 측정 완료 (10 cell × 31 method × 5 sel). multi 4강 method 측정이 STAGE 3 (multi_join deep_wiki) 완료된 직후. 회의 narrative = "단일 일관 → multi 검증" 이며, multi 결과는 부록 자료.

데이터 source (서버 capstone):
- /mnt/hdd0/home/capstone2026/cache/rq3/multi_4kang_partsupp_deep_sift_10.parquet (이미 완료)
- /mnt/hdd0/home/capstone2026/cache/rq3/multi_4kang_partsupp_deep_wiki_10.parquet (15:04 완료)
- /mnt/hdd0/home/capstone2026/cache/rq3/multi_4kang_multi_join_deep_wiki.parquet (STAGE 3 완료 직후)
- bernoulli baseline = 같은 cell 의 BERN method row (이미 측정됨, rq2_alloc_*_5mode.parquet 또는 multi_4kang 의 BERN row)

Task:
1. 서버에서 3 parquet read → 4강 method (hdbscan/hilbert/hybrid/mb_partial) × 5 sel × paired Δ% vs bernoulli 계산
   - paired alignment = query_id 기준
   - Δ% = (qerr_method - qerr_bern) / qerr_bern * 100
   - sel=0.10 우선 (회의 narrative core)

2. master_v6 § multi 보강 (line 641~690 기존 = km20 모드 ablation):
   - 현재 §multi 끝 (line 689 근처) 에 §multi-2 추가 신설
   - 새 표: 4강 method × 3 multi cell × 5 sel paired Δ% vs bernoulli
   - 핵심 narrative 1~3 줄: "4강 multi 일반화 — 부호·크기 일관성 검증 결과"
   - 단일 sweet spot 결과 (-7~-32%) 와 multi 결과 비교

3. master_v6 §10.6 (line 841~855) update:
   - 기존 표기 "[현재 측정 진행 중 — agent Y4]" → 측정 결과 narrative 로 교체
   - "4강 multi 일반화" 결과 1~2 줄 narrative
   - "단일 정확성은 multi 정확성의 *필요조건만* 성립" narrative 강화

4. /Users/hyunbin/Capstone/_internal/scripts/build_native_pptx_5_8.py:1541~1563 Slide 11 hardcoded update:
   - 기존 표 (km20_concat/product 모드 결과):
     ["partsupp_deep_sift_10", "96+128", "−0.35%", "−1.15%"]
     ["partsupp_deep_wiki_10", "96+768", "−0.30%", "+0.53%"]
     ["partsupp_deep_10 ⨝ part_wiki_10", "TPC-H", "+1.51%"]
   - 새 표 (4강 method × 3 multi cell, sel=0.10):
     - 형식 예시: ["cell", "dim", "Hilbert", "MB_partial", "Hybrid", "HDBSCAN"]
     - 또는 narrative 강조용 압축 형식 결정 (sub-agent 판단)
   - column header + caption 도 4강 narrative 로 update

5. build_charts_5_8.py 의 build_s11() 함수 업데이트 (선택):
   - 현재 S11.png = km20_emb1/emb2/concat/product × 3 multi cell grouped bar
   - 4강 method × 3 multi cell grouped bar 으로 update 가능 시 진행 (시간 여유 시)
   - 시간 부족 시 PPT slide 11 hardcoded 만 update + S11.png 그대로 유지

6. 검증:
   - 부호 일관성: 4 method × 3 cell = 12 measurement 의 sign distribution
   - 단일 sweet spot 매칭: SIFT/WIKI/YFCC 단일에서 -% improve → multi 에서도 일관?

절대 변경 금지:
- 단일 10 cell × 4강 paired Δ% 표 (master_v6 §2)
- Tier 1 17종 / Sweet Spot boundary
- PDX (SIGMOD 2025) confirmation 4 곳 reference
- 채림 정본 (partsupp_yfcc_{1,10}) DROP 절대 X

Output:
- master_v6 line range 변경 사항 + 추가 narrative
- build_native_pptx_5_8.py:1541~1563 변경 사항
- 부호 일관성 검증 결과 (12 measurement)
- 회의 narrative 1~3 줄 요약 (사용자 회의 진행 가이드 update 용)

Time budget: ~30분 이내. 측정 데이터만 있으면 빠르게 진행 가능.
```

---

## Sub-agent 호출 후 follow-up actions (사용자 또는 메인 세션)

### 즉시 (sub-agent 완료 직후)
1. 변경 사항 검토 + 의견 반영
2. PDF 6 파일 재변환:
   ```bash
   cd /Users/hyunbin/Capstone
   python3 _internal/scripts/md2pdf.py submission/_drafts/팀원_이해용_종합_20260508.md
   python3 _internal/scripts/md2pdf.py experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md
   python3 _internal/scripts/md2pdf.py submission/_drafts/속도는벡터_자문메일초안_W4_20260508.md
   python3 _internal/scripts/md2pdf.py experiments/results/10cell_narrative_종합_20260508.md
   python3 _internal/scripts/md2pdf.py submission/_drafts/속도는벡터_5월27일발표_plan_20260508.md
   python3 _internal/scripts/md2pdf.py _internal/handoff_v10_session_20260508_PM.md
   ```
3. PPT 재빌드:
   ```bash
   python3 _internal/scripts/build_charts_5_8.py
   python3 _internal/scripts/build_native_pptx_5_8.py
   ```
4. PPT 재검증 (메인 세션 = unzip + Read PNG)
5. git commit + push

### 회의 18:30 직전
1. 카톡 공유 (사용자 직접) — `_internal/20260508_회의직전_카톡_초안.md` v1 또는 v2 복사
2. PPT 화면 공유 (Keynote 또는 PowerPoint 회의 사용)

---

## 비상 plan (STAGE 3 완료 지연 시, ~17:30 이후)

- multi 4강 결과 없이 회의 진행 가능 (handoff §0 명시: 단일 100% finalize 가 회의 narrative 핵심)
- master_v6 §10.6 = "agent Y4 진행 중" 그대로 유지
- PPT slide 11 = km20 모드 결과 그대로 (current PPT 상태)
- multi 결과 도착 시 회의 중 / 회의 후 합의로 narrative 확장
