# v3 → v4 PPTX 양식 fix 보정 prompt (만약 PowerPoint 에서도 fallback 발생 시 적용)

작성 2026-05-26 13:50 KST. **★ macOS PowerPoint 직접 open 검증 결과 fallback 발생 시 본 prompt 를 claude.ai/design (대화창 `019e1a41-...`) 에 그대로 복붙 → deck_v26.html 보정 → 새 PPTX export = v4_editable.pptx**

> ★ 사용자 명시 task: "스크린샷 PPT 랑, 편집가능한 PPT 랑 비교해서 편집가능한 pptx 양식들좀 정확하게 시각적으로 일치하게끔 작업" — 본 prompt 는 차이 5+1+1=7 slide 의 양식 fix 만 다룸. 디자인 시스템 (navy #1E3A5F · cyan #0EA5E9 · purple #8B5CF6 · Apple SD Gothic Neo · 흰 배경 · chapter badge · 슬라이드 구조 14개) 모두 동결 carry. 텍스트 내용 변경 X.

## 진단 — 14 slide 시각 정밀 비교 결과

스크린샷 모드 PPTX (HTML preview ground truth) vs 편집 가능 모드 PPTX (PowerPoint 렌더링) 차이 패턴 단 2 유형:

### A. Gradient text → navy 배경 박스 + 검정 텍스트 fallback (★ 5건, fix 필요)

- **slide 1**: hero "인덱스 부재 시 / Adaptive Sampling 개선" navy → cyan gradient text 가 PPTX export 시 단색 검정 또는 navy 박스 + 검정 텍스트로 fallback
- **slide 3**: hero "10,000× 응답 시간 차이" navy → cyan gradient → 동일 fallback
- **slide 10**: hero "89.1%" navy gradient → navy 박스 + 검정 텍스트로 가장 심각 변환
- **slide 12**: hero "5.70× 응답 시간 단축" navy → cyan gradient → 동일 fallback
- **slide 14**: 거대 hero "감사합니다" navy → cyan gradient → 가장 큰 사이즈로 가장 두드러진 fallback (slide 14 가 마지막 인상 슬라이드라 critical)

### C. RESEARCH QUESTION 박스 (slide 6) → 검정 배경 + 흰 텍스트 invert fallback (★ 1건)

- **slide 6**: RESEARCH QUESTION 박스 안 "카디널리티 추정을 더 잘할 수 있는 표본 추출 방식은 무엇일까?" 텍스트 영역이 PPTX 에서 검정 배경 + 흰 텍스트로 invert. 의도 = 흰/연한 박스 배경 + navy 텍스트

### D. slide 5 ②③④ STEP 박스 chart icons + 텍스트 누락 (★ 1건)

- **slide 5**: Adaptive Sampling 5 STEP pipeline 중 ① STEP (purple highlight 본 연구 집중 단계) 만 정상 렌더링. ②③④ STEP 박스 안 chart icons (small SVG inline) + 보조 텍스트가 PPTX export 시 누락됨

## 보정 prompt — claude.ai/design 동일 대화창에 복붙 (★ 광범위 fix · v2 2026-05-26 13:55)

사용자 PowerPoint 확인 결과 = **다수 fallback** + **fallback 위치 다양하게 섞여서 정확 식별 어려움**. 안전하게 전체 fix.

```
deck_v26.html 의 **PPTX export 호환성 광범위 fix** 진행. 디자인 시스템·텍스트 내용·슬라이드 구조 (14 slide) 모두 동결 carry, 단 다음 4 카테고리 fix:

★ Fix 1 (★★★ Critical): 모든 텍스트 폰트 PowerPoint 호환 강제 통일
현 deck 의 텍스트 일부가 PPTX export 시 PowerPoint 에서 필기체 또는 비호환 폰트로 fallback 발생. 모든 텍스트의 font-family 를 다음 우선순위 fallback chain 으로 강제:

font-family: "Apple SD Gothic Neo", "Pretendard", "Noto Sans KR", "Malgun Gothic", -apple-system, system-ui, sans-serif;

font-weight 은 macOS 기본 weight (300·400·600·700) 만 사용. Light = 300, Regular = 400, SemiBold = 600, Bold = 700. 100·200·500·800 같은 비표준 weight 사용 X. 추가로 numeric weight 대신 명시적 ("Regular", "Bold") 사용도 안전.

★ Fix 2 (★★★ Critical): Gradient text → 단색 navy fill 변경 (slide 1·3·10·12·14)
현 hero gradient text 가 PPTX export 시 navy 박스 + 검정 텍스트로 fallback 발생. 가장 안전한 fix = hero 텍스트 fill 을 **navy #1E3A5F 단색** 으로 통일. cyan accent 효과는 부제·하단 강조 chip 으로만 남김 (hero 본문에서 제거).

영향 받는 slide:
- slide 1: "인덱스 부재 시 / Adaptive Sampling 개선" → navy #1E3A5F 단색
- slide 3: "10,000× 응답 시간 차이" → navy #1E3A5F 단색
- slide 10: "89.1%" → navy #1E3A5F 단색
- slide 12: "5.70× 응답 시간 단축" → navy #1E3A5F 단색
- slide 14: "감사합니다" → navy #1E3A5F 단색

CSS gradient·background-clip·-webkit-text-fill-color·SVG <linearGradient> 모두 제거. 단순한 color: #1E3A5F 만 사용.

★ Fix 3 (★★ High): RESEARCH QUESTION 박스 fill invert fix (slide 6)
현 박스 fill 이 PPTX export 시 검정 배경 + 흰 텍스트로 invert. 의도 = 흰/연한 배경 + navy/purple 텍스트. 다음 변경:
- background-color: #FFFFFF 또는 매우 연한 purple #F5F3FF
- text color: navy #1E3A5F 또는 purple #6B46C1
- mix-blend-mode·backdrop-filter·filter·-webkit-text-fill-color invert 모두 제거
- box-shadow·border 는 유지 OK

★ Fix 4 (★★ High): slide 5 STEP 박스 chart icons + 보조 텍스트 (slide 5)
② STEP "카디널리티 추정" + ③ STEP "Q-error 측정" + ④ STEP "표본 크기 조정" 의 chart icons (small inline SVG) + 보조 텍스트가 PPTX export 시 누락.

가장 안전한 fix = 4 STEP 모두 ① box (purple highlight 본 연구 집중 단계) 와 동일한 구조·fill·텍스트 size 으로 통일. 단 STEP 1 만 ★ 표식 + purple #8B5CF6 stroke 강조 + 배경 fill 유지 (다른 3 STEP 은 흰 배경 + purple 텍스트로 통일).

chart icons (SVG <rect><circle><path>) 모두 제거하고 단순 navy color emoji 또는 유니코드 기호 (📊·📈·📉·⚙️) 사용. 또는 아예 icons 제거하고 텍스트만 (① 표본 추출 / ② 카디널리티 추정 / ③ Q-error 측정 / ④ 표본 크기 조정) 가운데 정렬.

★ 추가 안전 조치
- 모든 SVG inline 요소 (chart·icon·decorative shape) 의 fill·stroke 색상은 단순한 hex color 만 사용 (gradient·pattern·mask·filter 제거)
- 모든 텍스트의 letter-spacing·line-height 는 numeric value (px 또는 unitless) 사용, em 단위 회피
- 모든 box-shadow 는 단순한 (offset-x offset-y blur-radius color) 형식 사용, inset·spread·multiple shadows 회피

전체 14 slide 의 다른 부분 (chapter badge·표·도넛 그래프·plan 비교 다이어그램·footer·meta) 은 모두 carry. 디자인 시스템 (navy #1E3A5F · cyan #0EA5E9 · purple #8B5CF6 · green #10B981 · coral #F97316 · 흰 배경 · Apple SD Gothic Neo) 동결.

새 file 명: deck_v27.html → PPTX 양식 **편집 가능 모드** 으로 다시 export → 사용자에게 download link 제공.

★ Critical: PPTX export 옵션에서 "편집 가능 모드 (editable)" 선택. "스크린샷 모드 (screenshot)" 는 별 export 으로 받음.
```

## 옵션 평가 — 마감 압박 (5/26 23:59 까지 약 10h 남음)

| 옵션 | 소요 | 정확도 | 추천 |
|---|:--:|:--:|:--:|
| 옵션 1: **현 v3 그대로 LearnUs 업로드** (만약 PowerPoint 정상 = LibreOffice fallback 만 거짓 양성) | 5분 | 100% (만약 정상) | **★ 첫 번째 검증 후 결정** |
| 옵션 2: Claude Design 에 본 prompt 적용 → v4_editable.pptx → 재검증 | 1-2시간 | 90%+ | PowerPoint 에서 fallback 발생 시 |
| 옵션 3: PowerPoint manual 수정 (5+1+1=7 slide 의 hero text 만 사용자 직접 fix) | 30분 | 95%+ | 옵션 2 실패 또는 시간 부족 시 |
| 옵션 4: **스크린샷 모드 PPTX** (`v3_스크린샷.pptx`) 그대로 업로드 (단 텍스트 편집 불가, 시각 100% HTML preview 일치) | 5분 | 100% (시각) | LearnUs 가 편집 가능 요구 안 하면 best |

## ★ 다음 단계 분기

1. **사용자 PowerPoint v3.pptx 시각 확인 결과 == "정상"** (Apple SD Gothic Neo OK + gradient text 정상 렌더) → **옵션 1 = 그대로 LearnUs 업로드**
2. **결과 == "일부 fallback 발생 (slide 1·3·10·12·14 hero gradient)"** → **옵션 2 또는 옵션 3 분기 결정**
3. **결과 == "다수 fallback"** → **옵션 4 = 스크린샷 모드 업로드** (가장 안전, 시각 100% 일치)

★ LearnUs 가 PPTX 의 텍스트 편집 가능 여부 요구 X 인 경우 (단순 발표 자료 업로드) → **옵션 4 가 최우선** (시각 100% 일치 + 가장 빠름 + 마감 압박 대응).
