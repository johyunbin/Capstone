# Phase 9: CLAUDE.md 통합 업데이트 프롬프트

## 목적

9대 지침 제작 완료 후, CLAUDE.md에 지침 트리거 테이블과 guideline/ 구조를 반영한다.

## 수행 내용

### 1. CLAUDE.md에 지침 트리거 섹션 추가

CLAUDE.md의 "세션 루틴" 섹션 아래에 다음을 추가:

```markdown
## 지침 시스템

guideline/ 폴더에 9대 지침이 auto.md + manual.md + .sh 3파일 세트로 존재.
사용자가 아래 키워드를 입력하면 해당 지침의 auto.md를 읽고 Phase 순서대로 자동 실행.

| 키워드 | 지침 파일 |
|--------|-----------|
| "점검", "헬스체크", "무결성" | guideline/00_점검지침_auto.md |
| "논문 분석", "총정리", "시리즈" | guideline/01_논문분석지침_auto.md |
| "실험", "벤치마크", "EXPLAIN" | guideline/02_실험지침_auto.md |
| "제출", "보고서", "마감", "연구제안서" | guideline/03_제출물지침_auto.md |
| "PDF", "문서 변환", "md2pdf" | guideline/04_문서생성지침_auto.md |
| "주간", "보고", "이번 주" | guideline/05_주간보고지침_auto.md |
| "미팅", "회의", "브리핑", "카톡" | guideline/06_미팅지침_auto.md |
| "발표", "PPT", "포스터", "슬라이드" | guideline/07_발표지침_auto.md |
| "설계", "기획", "연구 방향" | guideline/08_연구설계지침_auto.md |

수동 실행: `{지침명} 자동` 또는 `./guideline/NN_{지침명}_실행.sh`
```

### 2. 디렉토리 구조 업데이트

CLAUDE.md의 디렉토리 구조 섹션에 guideline/ 추가:

```
├── guideline/                  # 9대 지침 시스템
│   ├── prompts/                # 지침 제작 프롬프트 (원본)
│   ├── NN_{지침명}_auto.md      # 자동 실행용 (00~08)
│   ├── NN_{지침명}_manual.md    # 수동 참조용 (00~08)
│   └── NN_{지침명}_실행.sh      # bash 오케스트레이터 (00~08, 27파일)
```

### 3. 기존 스킬 정리 안내

6개 기존 스킬이 지침에 흡수됨을 기록:
- paper-analysis → 논문분석지침
- experiment-log → 실험지침
- submission-prep → 제출물지침
- project-health → 점검지침
- weekly-log → 주간보고지침
- progress-brief → 주간보고지침

스킬 폴더 삭제 여부는 사용자에게 확인.

### 4. 검증

- CLAUDE.md 트리거 테이블 9행 확인
- guideline/ 내 27파일(9×3) 존재 확인
- 디렉토리 구조 설명 일치 확인

## 완료 조건
- CLAUDE.md 업데이트 완료
- 트리거 키워드 → 지침 매핑 정상
- 디렉토리 구조 반영
