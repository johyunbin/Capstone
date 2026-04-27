# 다음 세션 프롬프트 — 2026-04-27 16:50 KST 작성

## 🎯 목표

**4/28 (화) 23:59 LearnUs 마감 직전 최종 검증 + 보강.**

현재 산출물은 4/28 제출 가능 수준이지만, 사용자가 **Max Quality / Max Score / 인간 작업물로 보일 정도의 완벽함**을 요구함. 다음 세션은 **울트라리뷰 + figure A 등급 재생성 + 텍스트 AI 흔적 제거 + 최종 commit + LearnUs 업로드 준비**의 최종 마감 세션.

---

## 🔒 반드시 준수해야 할 캡스톤 공식 양식 (LearnUs 공지)

### 제출

- **마감**: 2026-04-28 (화) 23:59
- **방식**: 팀원 1 명이 대표로 LearnUs 분반 게시판에 업로드
- **파일명**: `속도는벡터_중간보고서.pdf`, `속도는벡터_중간발표.pdf` (PDF 만)

### 보고서·발표 모두 포함되어야 할 6 필수 항목

1. 해결하고자 하는 문제
2. 기존 연구의 현황 및 한계점
3. 기존 연구와의 차별성 및 제안하는 연구의 중요성
4. 연구 및 실험 방법
5. 현재까지의 진행 상황 및 향후 계획
6. **팀원별 역할 분담** (보고서만 해당)

### 발표 정보

- **일시 (택일)**: 4/29 (수) 15:00 ~ 15:50, 인종 D508 / 4/30 (목) 19:00 ~ 21:00, 인종 A428
- **시간**: 팀당 10 분 + Q&A 5 분
- **발표 후 자료 수정 불가**

---

## 📦 현재 작업본 (2026-04-27 16:45 기준)

### 최종 제출 파일 (`submission/_drafts/`)

| 파일 | 페이지 | 사이즈 | 비고 |
|---|---|---|---|
| `속도는벡터_중간발표.pdf` | 17 | 1.17M | Academic Light + Conclusion + 4-step About Team |
| `속도는벡터_중간발표.pptx` | — | 0.96M | PowerPoint 호환 백업 |
| `속도는벡터_중간보고서.pdf` | 19 | 1.34M | figure 8개 + 표 5개 + References 8건 |
| `속도는벡터_중간보고서.docx` | — | 1.06M | Word 백업 |

### 9 디자인 변형 백업 (`archive/midterm_v1_drafts/`)

academic / bold / editorial / gemini / glass / hub / navy / soft / swiss — 모두 pptx + pdf

### 현재까지 적용된 보강 (4/27)

1. ✅ Academic Light 디자인 채택 (Apple 클린, 흰 배경 + 청 강조)
2. ✅ figure 8 개 보고서 삽입
3. ✅ Conclusion 슬라이드 신설 (S16 — 4 핵심 발견 카드 + 인용)
4. ✅ About Team 4-step 카드 (S15 — 각자 highlight 강조)
5. ✅ References section (보고서 §6 — 8 건)
6. ✅ ↔ → "vs" 일괄 변경 (이모지 렌더링 방지)
7. ✅ RQ3 ID (A)(B)(C)(E)(F)(G)(H) → 1~7 번호
8. ✅ figure_1 (Phase 4 scatter) 2×2 격자 재생성 (X축 겹침 해소)
9. ✅ S6 Two-Level figure 제거 (텍스트 박스 충돌 해결)
10. ✅ S8 layout 재구성 (좌 표 + 우 figure 정사각)
11. ✅ 임채림 석사 표기 (이채림 → 임채림 전수 정정)
12. ✅ 수치 정합성 cross-check (4 라운드 딥리뷰 통과)

---

## 🚨 다음 세션 작업 우선순위

### Phase 1 — 울트라리뷰 / 심층 / 딥리뷰 (3-5 라운드)

**목표**: 4/28 마감 직전 마지막 결함 0 건 확인

**검토 축**:
- A. **6 필수 항목 매핑** — 보고서·발표 모두 명확히 다뤄지는가?
- B. **수치 정합성** — 보고서 ↔ 발표 ↔ 실험 raw data (`experiments/results/`) 의 cross-check
- C. **figure 품질** — A 등급 미만은 모두 재생성 (재생성 명단은 Phase 2 참조)
- D. **텍스트 가독성** — 발표자료 9pt 미만 본문 / 표 압축 / 캡션 잘림
- E. **AI 흔적 텍스트** — "본 연구는...", "흥미롭게도", "할 수 있습니다", 의문문/감탄문, 자동 생성 캡션의 어색함, AI 스러운 산문 톤
- F. **인용 정합성** — Cohen 1988 / Horvitz-Thompson / Neyman / Wilcoxon / Indyk-Motwani / JL / Acharya 본문 등장 위치 vs References 일치
- G. **학교 양식 준수** — 표지 / Contents / 1~5 (보고서) / 1~6 (발표) section 명시
- H. **그림·표 번호 일관성** — 차트 내부 "Figure N" vs 캡션 "그림 M" 불일치 잔존

**Agent 호출 권장**: general-purpose subagent_type 으로 4 PDF (academic / 보고서) + experiments/results/RQ1_RQ2 정리.md 비교 + AI 톤 검수.

발견된 CRITICAL/HIGH 모두 해소 후 재검증 (반복).

### Phase 2 — figure A 등급 재생성 (현재 미달 4 종)

**현재 등급** (3 라운드 딥리뷰 결과):
- A 등급: figure_7 (selectivity gradient), figure_8 (cross_dataset bar)
- A- ~ B+ 등급: figure_2, figure_6, vector_c snippet, figure_1 (방금 재생성)
- **B-/C+ 등급 (재생성 권장)**:
  - **figure_9 (two_level_decomposition)** — 좌 panel s=0.05 라벨 겹침, s=0.01 "Total +8.93%" 잘림
  - figure_10 (cluster_skew) — 0.394 라벨이 brace 와 겹침, (b) HHI panel 시각 임팩트 약함
  - figure_2 (phase6 box) — y축 log 명시 없음, s=0.001 line 형태
  - figure_6 (phase5 heatmap) — colorbar 범위 ±0.3 인데 실제 값 좁음 (시각 임팩트)

**재생성 지침**:
- raw data: `experiments/results/rq1_motivation/*.parquet` + `experiments/results/RQ1_RQ2 실험 결과 정리.md`
- 도구: matplotlib (Apple SD Gothic Neo 폰트, 한글 OK)
- 스크립트 예시: `/tmp/regen_phase4_v2.py` (figure_1 재생성, 2×2 격자, dpi=180)
- **A 등급 기준**:
  - PDF 100% zoom 에서 모든 라벨/통계박스 가독
  - 라벨 겹침 0
  - 캡션과 figure 내부 텍스트 정합 (차트 내부 "Figure N" 헤더 제거 권장)
  - 색상·범례·축 라벨 일관성

### Phase 3 — 차트 헤더 통일 (선택)

**문제**: 8 figure 모두 차트 내부 "Figure N" 영문 헤더 vs PDF 캡션 "그림 M" 한국어 — 번호 충돌
- 해결책 A: 모든 figure 재생성 시 차트 헤더 제거
- 해결책 B: PDF 캡션을 "그림 M (실험 노트 식별자: figure_N)" 형태로 명시

시간 허락 시 A 선호. 시간 부족 시 B 로 양식 통과.

### Phase 4 — 텍스트 AI 흔적 제거

**점검 패턴** (grep):
```bash
grep -nE "흥미롭게도|아마도|어쩌면|것 같습니다|할 수 있습니다|놀랍게도|굉장히|살펴보겠습니다|먼저 살펴|이 점을 강조|중요한 점은" content.py _build_docx_v1.py
grep -nE "\?$|할까\?|뭘까\?" content.py _build_docx_v1.py
```

이미 1차 점검에서 AI 스러운 표현 거의 없음 확인. 단 자동 생성 캡션 톤 (예: "그림 5. 외적 타당성 — DEEP 1M / DEEP 8M / SIFT 1.5M 의 KM20 s = 0.500 효과") 의 자연성 재검토.

학술 산문 톤: "본 연구는 / 본 보고서는 / 본 발표는" + 서술어 "측정하였다 / 확인하였다 / 검증하였다" 일관 사용.

### Phase 5 — 최종 빌드 + LearnUs 업로드 준비

1. 보강 사항 모두 반영하여 academic + 보고서 v1 재빌드
2. `submission/_drafts/속도는벡터_중간발표.pdf` + `속도는벡터_중간보고서.pdf` 최종 카피
3. 페이지 수 확인 (발표 ≤ 17p, 보고서 ≤ 20p 권장)
4. PDF 100% zoom 으로 사용자 직접 확인
5. (사용자 직접) 4/28 23:59 까지 LearnUs 업로드

---

## 🔧 빌드 환경

### 발표 (Academic Light)
```bash
cd /Users/hyunbin/Capstone/_internal/scripts/midterm_pptx
python3 build_academic.py /Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_academic.pptx
./convert_pdf.sh /Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_academic.pptx
cp 속도는벡터_중간발표_academic.{pdf,pptx} → 속도는벡터_중간발표.{pdf,pptx}
```

### 보고서
```bash
python3 /Users/hyunbin/Capstone/_internal/scripts/_build_docx_v1.py
osascript << 'EOF'
tell application "Microsoft Word"
  activate
  open POSIX file "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간보고서_v1.docx"
  delay 3
  set theDoc to active document
  save as theDoc file name "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간보고서_v1.pdf" file format format PDF
  delay 2
  close theDoc saving no
end tell
EOF
mv 속도는벡터_중간보고서_v1.{docx,pdf} → 속도는벡터_중간보고서.{docx,pdf}
```

### Figure 재생성
```bash
python3 /tmp/regen_*.py  # 또는 새 스크립트 작성
# 결과: experiments/figures/{rq1_motivation,rq2_aware}/figure_*.png
```

---

## 📚 핵심 참고 (다음 세션에서 자주 봐야 할 파일)

- `experiments/results/RQ1_RQ2 실험 결과 정리.md` — 모든 수치의 ground truth
- `experiments/results/rq1_motivation/phase4_compare.json` / `phase4_*.parquet` — Phase 4 raw
- `experiments/results/rq1_motivation/phase5_local_skew_spearman.json` — RQ1 negative result raw
- `experiments/results/rq1_motivation/phase6_multiseed_summary.json` — RQ2 5-seed CI
- `plans/RQ3설계안_20260416_213500.md` — RQ3 7-way 정식 명칭
- `_internal/scripts/midterm_pptx/content.py` — 모든 슬라이드 텍스트 데이터 단일 소스
- `_internal/scripts/_build_docx_v1.py` — 보고서 빌드 스크립트
- `submission/_drafts/archive/midterm_v1_drafts/` — 9 디자인 변형 백업

---

## 🚀 다음 세션 도입부에 복붙할 프롬프트

```
2026-04-27 16:45 KST 직전 세션에서 마무리한 상태에서 이어가자. _internal/next_session_prompt.md 를 먼저 읽고 다음 작업 진행.

현재 상태:
- submission/_drafts/속도는벡터_중간발표.pdf (Academic Light, 17p) + .pptx
- submission/_drafts/속도는벡터_중간보고서.pdf (19p, figure 8 + 표 5 + References) + .docx
- 4/28 (화) 23:59 LearnUs 마감 D-1

작업 목표 (Max Token, Max Time, Max Quality, Max Score, 인간 작업물 수준):

1. **Phase 1 — 울트라리뷰 / 심층 / 딥리뷰**: Agent 호출로 6 필수 항목 매핑 + 수치 정합성 + figure 품질 + 텍스트 가독성 + AI 흔적 + 인용 정합성 + 학교 양식 + 그림·표 번호 일관성 — 8 축 검증. CRITICAL/HIGH 0 건 될 때까지 반복.

2. **Phase 2 — figure A 등급 재생성**: figure_9 (two_level 라벨 겹침), figure_10 (cluster_skew), figure_2 (phase6 box), figure_6 (phase5 heatmap) — 모두 A 등급 (PDF 100% zoom 가독, 라벨 겹침 0).

3. **Phase 3 — 차트 헤더 통일**: 8 figure 차트 내부 "Figure N" 영문 헤더 제거 (또는 캡션 식별자 명시).

4. **Phase 4 — 텍스트 AI 흔적 제거**: 자동 생성 캡션 자연성 + 학술 산문 톤 일관성 재검토.

5. **Phase 5 — 최종 빌드 + 사용자 검증**: 모든 보강 반영하여 재빌드, 페이지 수 확인, 사용자가 PDF 100% zoom 으로 직접 검증, 4/28 23:59 LearnUs 업로드 준비.

전권 위임. 무한 반복 OK. 1 시간 이상 소요 OK. 인간이 손대지 않아도 될 완벽한 수준으로.

먼저 next_session_prompt.md 의 Phase 1~5 점검 후, Phase 1 (울트라리뷰) 부터 시작.
```

---

## ⚠️ 4/27 작업 회고 (이 세션에서 한 것)

- Research/ 디렉토리 (조현인 박사 자료) 디자인 패턴 추출
- 9 디자인 발표자료 변형 빌드 (navy / glass / editorial / bold / hub / gemini / academic / swiss / soft)
- 보고서 v1 — figure 8 개 + 표 5 개 + References section 8 건 + Method/Results/Implication 산문
- 발표 — Conclusion 슬라이드 + 4-step About Team 카드 + 인용 footer
- 5 라운드 딥리뷰 (3 차 + 1 cross-check + 1 figure 점검) 통과: CRITICAL 4 + HIGH 11 + 표 번호 + Swiss 표지 + Phase 4 X축 + ↔ → vs + RQ3 ID 1~7 + 임채림 석사 일괄 정정 모두 해소
- figure_1 (Phase 4 scatter) matplotlib 으로 2×2 격자 재생성 (1757×1490, 통계박스 폰트 10pt)
- Academic Light 최종 채택 (3 라운드 딥리뷰 A+ 등급)
- 4/27 16:00 commit `a4681ad` push + 맥북 동기화 완료
- 4/27 16:45 commit (이번 세션 마무리) push + 맥북 동기화 진행 중

다음 세션은 4/28 마감 직전 마지막 보강 + 사용자 검증 + LearnUs 업로드.
