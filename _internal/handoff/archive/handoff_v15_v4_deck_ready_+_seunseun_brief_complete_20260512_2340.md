# Handoff v15 — 5/12 23:40 KST
## v4 deck 완성 (Capstone Design System, 20 slide) + 박세은/강재현 피드백 반영 + 임채림 SAP 5/28 plan

> **본 세션 5/12 12:13 ~ 23:40 (11h 27m) 산출**: (1) v3 storyline 정정 + (2) 박광현+임채림 사전보고 자료 1+2 page + (3) v3 deck 박세은/강재현 6건 피드백 반영 v4 으로 update (20 slide, PDF+PPTX+HTML export 완료) + (4) 임채림 SAP 5/28 활용 plan + (5) 서버 사용 정책 변경 (kde_parzen 중단, 서버 free)

---

## 0. TL;DR — 다음 세션 첫 30초

```bash
# 1. 본 handoff_v15 read

# 2. v4 deck PDF visual 검증 (이미 확인됨 — 20 slide 정상)
ls -la "submission/_drafts/속도는벡터 · Capstone Final 5_27 (Keynote v4)".*
# → PDF 713KB / PPTX 500KB / HTML 6.2MB standalone

# 3. 박세은 + 강재현 추가 피드백 카톡 wait
#    줄글 형식 답변 paste 완료 (사용자 22:55)

# 4. 박세은 임채림 SAP 5/28 정리 진행 wait
```

---

## 1. v4 deck 최종 status (★ 핵심 산출물)

### 1.1 file 위치 (submission/_drafts/)

| File | size | 내용 |
|---|---:|---|
| 속도는벡터 · Capstone Final 5_27 (Keynote v4).pdf | 713 KB | ★ 20 slide PDF |
| 속도는벡터 · Capstone Final 5_27 (Keynote v4).pptx | 500 KB | 편집 가능 PowerPoint |
| 속도는벡터 · Capstone Final 5_27 (Keynote v4).html | 6.2 MB | standalone bundled (React + JS embed) |
| (이전) 속도는벡터 · Capstone Final 5_27 (Keynote v3).pdf | 590 KB | 18 slide, 5/12 14:00 박세은 share 했던 버전 |

### 1.2 v4 20 slide storyline (사용자 14:23 + 박세은/강재현 피드백 반영)

| # | Slide | 내용 |
|---|---|---|
| 1 | Cover | "분포 인지형 stratification 으로 Exqutor 보강하기" + Skew-Aware Stratification 부제 |
| 2 | Section 1 / 배경 | SectionDivider |
| 3 | Exqutor 한계 | 큰 인용문 "분포 의존성" 강조 |
| 4 | 우리 주제 | 분포 알/모를 때 |
| 5 | Section 2 / 연구 질문 | SectionDivider |
| 6 | RQ1·RQ2·RQ3 | 3 column 질문 정리 |
| 7 | **★ RQ1 결과** | MAX 8.64% (SIFT sel=0.10) + 4 cells breakdown table |
| 8 | RQ2 결과 | Bern → Equal → Prop → Neyman → Anti bar chart (qe_trim 정의 caption) |
| 9 | RQ3 출발점 | 분포 모를 때 paradigm search 도입 |
| 10 | Section 3 / Portfolio | SectionDivider |
| 11 | **★ 8 paradigm × 56 method** | 각 paradigm 가정/조건 명시 |
| 12 | Section 4 / framework | SectionDivider |
| 13 | paper 재현 -4.3% | Fig.12 mean qe_trim 1.618 vs 1.69 + caption 명확화 |
| 14 | 대체 vs 증강 framework | est_final = est_method vs (est_b1+est_method)/2 |
| 15 | **★ paradigm rollup** | from→to + ratio + Q-error 직접 (28% 절감) 병기 |
| 16 | **★ 신규: 왜 replace 만으로는 안 되는가** | 3 column (BUDGET / ASSUMPTION / NEGATIVE CONTROL 0/493) |
| 17 | ★ 가장 우수 알고리즘 5선 | Parzen KDE / HLL / Chao / Sparse RP / Hilbert+Z-order |
| 18 | ★ Climax (대체 vs 증강) | 0/493 vs 92.5% paired better |
| 19 | Section 4 / Limitation | SectionDivider |
| 20 | Closer | "감사합니다" 거대 한국어 + 질문 환영 |

(v3 의 18 slide → S7 RQ1 확장 + S16 신규 replace 실패 분석 추가로 20 slide)

### 1.3 박세은 + 강재현 5/12 22:27-22:38 피드백 반영 (6건 모두)

| # | 피드백 | v4 반영 status |
|---|---|---|
| 강재현 1 | multi carry-over 명확화 | ✅ S11 / S14 caption 명시 |
| 강재현 2 | paradigm/method/cell/mode 정의 | ✅ S6 / S11 명확화 |
| 강재현 3 | 8 paradigm 가정 명시 | ✅ S11 portfolio 각 paradigm cell 안 가정 추가 |
| 강재현 4 | ensemble 비용 (latency/memory) | ✅ S19 Limitation slide 명시 (미측정) |
| 박세은 1 | 성능 표현법 (% → ratio/from→to/Q-error) | ✅ S15 모두 병기 |
| 박세은 2 | RQ1 +3.74% 출발점 너무 작음 | ✅ S7 cell-by-cell MAX 8.64% breakdown |

---

## 2. 박세은 + 강재현 카톡 답변 status

### 2.1 5/12 22:55 줄글 형식 답변 paste 완료

박세은 "답글로 달아주신 거 읽기가 어려워서 줄글 형식" 요청 반영. 자연 산문 12 paragraph 형태 카톡 paste.

→ 박세은 + 강재현 추가 피드백 wait (이미 답변 paste 한 후)

### 2.2 박세은 정리 → 임채림 SAP 5/28 활용

박세은이 임채림에게 "오늘~내일 정리해서 말씀" — 우리 1 page 자료 활용 가능:
- `submission/_drafts/박광현_5월15일_미팅/박광현+임채림_사전보고_간결_1page_20260512.pdf` ★
- v4 deck PDF (위 새 PDF 도 가능)

박세은 진행 wait — 다음 세션 박세은 status 카톡으로 확인 가능.

---

## 3. 본 세션 git commits (12 commits)

| Commit | 내용 |
|---|---|
| 54be265 | README/카톡 stat 5/12 02:50 실측 동기화 |
| ef58e36 | handoff_v13 + CLAUDE.md anchor + v8~v11 archive |
| 3218d6a | 박세은 12:27 → 사전보고 2 page |
| 1d4e674 | 키노트 prompt v3 storyline 정정 |
| 765c90d | 박세은 12:55 → 사전보고 1 page |
| 786c28b | handoff_v14 + 박세은 답장 가이드 |
| c76f1e7 | 박세은 14:27 4건 답변 + v3 정정 prompt + kde launch |
| 449776a | v3 deck 피드백 wait 기록 |
| 1b5bc73 | 임채림 SAP 5/28 + kde_parzen 중단 + 서버 정책 |
| a342972 | RQ1 cell breakdown + v3 정정 prompt v2 |
| cff690d | 박세은 22:50 줄글 형식 답변 |
| **9973a49** | **★ v4 최종 deck PDF+PPTX+HTML 완성 (20 slide)** |

---

## 4. 핵심 일정

| 일시 | event |
|---|---|
| 5/12 (화) 12:13 ~ 23:40 | 본 세션 11h 27m |
| 5/12 (화) 저녁 ~ 5/13 (수) | 박세은 정리 → 임채림 SAP 5/28 활용 |
| 5/13 (수) | 박세은 / 강재현 / 이동욱 추가 피드백 wait |
| 5/14 (목) | 박광현 미팅 D-1 자료 준비 |
| **5/15 (금) 14:00** | **박광현 교수 미팅 D-3 from now** |
| 5/16 (토) | claude.ai/design 사용 한도 reset (현재 80%) |
| 5/16 ~ 5/26 | deck finalize sprint (피드백 반영 추가 정정) |
| 5/26 (월) | finalize 마감 |
| **5/27 (화) 19:00** | **최종 발표 D-15** |
| **5/28 (목)** | **임채림 → SAP 미팅 (우리 캡스톤 내용 활용)** |

---

## 5. 다음 세션 mission

### 5.1 5/13 (수) morning

1. 박세은 + 강재현 추가 피드백 status check (어제 22:55 줄글 답변 paste 후)
2. 박세은 임채림 SAP 5/28 정리 진행 status
3. 이동욱 피드백 status (TBD)
4. 5/15 박광현 미팅 자료 4 file 최종 점검

### 5.2 5/13 ~ 5/14

피드백 받으면 v4 deck minor 정정 추가 (단 claude.ai/design 한도 80% — 5/16 토 reset 까지 제한적). 최종 정정 후 PDF/PPTX/HTML 재 export.

### 5.3 5/15 (금) 14:00 박광현 교수 미팅 D-3 → D-day

- 박세은 사전 자리 안내 (13:50)
- 자료 5 file: slide_draft + 예상질문 + update plan + README + 사전보고 1page/2page
- v4 deck PDF (스마트폰 또는 iPad 로 즉시 share 가능)
- confirm 요청 6건 진행

### 5.4 5/16 ~ 5/27

- claude.ai/design 한도 reset 후 추가 정정 진행
- 박세은/강재현/이동욱 검토 결과 반영
- 5/26 finalize → 5/27 19:00 최종 발표

---

## 6. 사용자 정책 (본 세션 verbatim)

- 12:36 "chrome 제어 열어놨으니까 남은 작업 또한 너가 전권 위임 받아서 진행하자"
- 13:04 "★3 Hilbert 정정 이런걸 왜넣어. RQ1, RQ2, RQ3, exqutor 재현 및 추가 이런 식으로 진행하면 되지"
- 13:04 storyline 7단계 verbatim
- 14:23 "예시 ARC: replace 시도 → 통계 확보 못함 → 증강 채택"
- 14:39 "추가 실험보다는 이제 내용 이해랑 정리, 방향성 결정"
- 16:07 "기록하고 대기하자"
- 20:46 박세은 "서버 사용 안 함" 동의
- 22:59 전권 위임
- 23:39 "3, 4, 5번 다 실행해서 다운 받았어. 옮겼어. 추가 카톡 대기하면서 해야 될 작업 있나?"

**핵심 원칙 (5/12 종료 시점 확정)**:
- v4 deck (20 slide, Capstone Design System) 가 5/27 발표 final base
- 추가 측정 X (서버 free, 5/16 토 한도 reset)
- 박세은/강재현/이동욱/박광현 피드백 받으면 minor 정정
- 임채림 SAP 5/28 활용 자료 박세은 진행 wait

---

## 7. END

작성: 2026-05-12 23:40 KST  
다음 세션: 5/13 (수) morning
- 박세은 + 강재현 + 이동욱 추가 피드백 wait
- 박세은 임채림 SAP 5/28 정리 status
- v4 deck minor 정정 (필요 시)
- 5/15 (금) 14:00 박광현 교수 미팅 D-3
- 5/26 finalize 마감 / 5/27 19:00 최종 발표 D-15 / 5/28 임채림 SAP 미팅
