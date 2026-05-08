# Ultra-Review — 루트 + templates/ (5/8 22:30 KST)

## 1. 루트 inventory

루트 (15 항목 — 시스템 4 + 디렉토리 7 + 파일 4):

```
.DS_Store, .claude/, .git/, .gitignore         # 시스템 4
_internal/, experiments/, plans/, reference/,
research/, submission/, templates/             # 디렉토리 7 (research/ 정리 대상)
CLAUDE.md, README.md                           # 진입점 2
```

**튀어나온 파일 (잘못된 위치)**:

- `research/` — 빈 디렉토리 (`.DS_Store` + `node_modules/.DS_Store` 만, 24 KB). 4/27 디렉토리 재정비 commit `fa0b32d` 에서 빈 폴더로 남은 잔재. CLAUDE.md 의 "7 디렉토리" 명세에 들어있지 않음 (reference/ 와 혼동된 흔적). git untracked.
  - **조치**: `rm -rf research/` (git tracked X, 안전).
- 루트 .DS_Store — `.gitignore` 에 이미 포함, 영향 없음.

기타 mis-placed 파일·임시 파일·빌드 부산물 **없음**. 루트는 사실상 깨끗.

## 2. README.md update (4/27 → 5/8 22:00)

기존 README 는 4/27 작성 (4/28 마감 미완료, 17 page 보고서 narrative). 5/8 W1 sprint 종합 finalize 시점으로 업데이트.

**변경 범위 (총 ~50 line)**:

- **헤더**: "현 단계 (5/8 22:00)" 1-line summary 추가 (W1 sprint 완료 + Multi launch 대기).
- **팀원 진입 가이드 표**: 5 행 → 7 행 확장. 자문 메일 v3·보고서 outline v2·Slides.jsx·deck PDF link 추가.
- **핵심 결과 §**: 4/17 RQ1+RQ2 anchor → 5/8 RQ1+RQ2+RQ3 종합 (4강 도출 + multi 25× shrinkage + PDX confirmation).
- **일정 표**: 4/28 마감 → 4/28 ✅, 4/30 ✅, 5/8 ✅, **5/9~5/15 ← 현재** (자문 발송 + Adaptive launch).
- **디렉토리 트리**: 5/8 22:00 시점 현황 — 자문 메일 v3·deck source·outline v2·handoff_v14·_internal/cache/ 반영.
- **자주 쓰는 명령**: 사용 안 하는 `_build_docx_v0.py` 줄 제거.

## 3. templates/ 점검

총 46 파일 (forms/ 9 hwp + 1 docx + 1 xlsx, samples/ 23 pdf + 4 png + 2 pptx, README.md, .DS_Store 4). 학교 공식 양식 (`연구지도확인서.hwp`, `회의록 양식.hwp`, 캡스톤 sample PDF) **모두 보존**.

**naming 일관성**: 대부분 `{제목}_샘플{N}.pdf` 패턴, `중간발표1_sample1.pdf` (영어 sample) 만 변형. 학교 ground truth 명명 그대로 유지하는 것이 reference 가치 측면에서 더 옳음 — **변경 없음**.

## 4. .gitignore update

추가 patterns:
- `node_modules/` (any depth — research/ + academic-deck/ 잔재)
- `*.log`
- `_internal/temp/`

제거: `# research/papers/` 주석 (디렉토리 자체 제거됨)

`_internal/cache/` 는 이미 git tracked (5/8 sprint 측정 산출물 12 csv) 이므로 ignore 추가하지 않음 — 주석으로 명시.

## 5. commit hash

`15accbd` — ultra-review root + templates/ — README.md 5/8 update + 루트 정리

## 6. 요약

루트는 사실상 깨끗 — `research/` 빈 폴더 1개만 정리 (24 KB → 0). README.md 4/27 → 5/8 22:00 finalize 시점으로 5 section 업데이트. templates/ 학교 양식 46 파일 전수 보존, naming 변경 없음. .gitignore 에 node_modules/·log/·temp/ 추가 — 향후 잔재 방지.
