# 학습정리지침 (AUTO)

> 대상: Capstone/learning/ 학습 자료 | 모드: 자동 실행 (전권 위임)
> 트리거: "학습 정리", "스크립트 분석", "learning 정리"

## 학습정리지침의 범위

**IS (이 지침이 하는 것):**
- learning/ 내 스크립트(txt) 전수 읽기 및 주제별 분석
- Claude Code 사용법, 팁, 워크플로우 관련 내용 추출
- 분석 결과를 Apple Notes (Claude 폴더)에 Trading 양식으로 저장
- 메모리(memory/)에 핵심 참조 정보 저장
- 전역 CLAUDE.md에 프로젝트 공통 활용 원칙 반영

**IS NOT (이 지침이 하지 않는 것 → 담당 지침):**
- 논문 분석 → 논문분석지침
- 실험 관련 학습 → 실험지침
- 코드 수정, 서비스 실행 — 수행하지 않음

---

## Phase 구성

### Phase 0: 인벤토리 수집 (1분)

learning/ 내 스크립트 파일 현황을 파악한다.

- [ ] learning/ 하위 폴더별 파일 수 카운트
- [ ] 언어별 분류 (kr/, us/ 등)
- [ ] 총 줄 수 및 파일 크기 확인

```bash
cd ~/Capstone
echo "=== learning/ 구조 ==="
find learning/ -type f -name "*.txt" | wc -l
for d in learning/*/; do echo "$d: $(find "$d" -type f | wc -l) files"; done
wc -l learning/**/*.txt 2>/dev/null | tail -1
```

---

### Phase 1: 전수 읽기 (10~15분)

모든 스크립트를 빠짐없이 읽는다. **대충 읽거나 키워드만 보지 않는다.**

- [ ] 대상 폴더 내 모든 .txt 파일을 Bash `cat`으로 전문 읽기
- [ ] 파일이 10KB 이상이면 persisted output 경로로 저장됨 → 해당 경로도 확인
- [ ] 읽은 파일 수를 카운트하여 Phase 0 인벤토리와 대조

읽기 전략:
- 5개씩 병렬 Bash로 `cat` 실행 (파일명 특수문자 주의 — 작은따옴표 사용)
- 파일명에 따옴표/이모지 포함 시 `cd` 후 glob 패턴 활용

---

### Phase 2: 주제별 분류 및 핵심 추출 (5분)

Phase 1에서 읽은 전체 내용을 바탕으로 주제별로 분류한다.

분류 기준:
- [ ] A. 핵심 철학 + 병렬 개발 (보리스 체니, CEO 마인드셋)
- [ ] B. CLAUDE.md + 컨텍스트 관리 (Lazy Loading, /memory, 토큰)
- [ ] C. 워크플로우 + Plan 모드 (TDD, WAT, SDD, TODO.md)
- [ ] D. Skills + Subagents (스킬 구조, 에이전트 병렬, Ralph Loop)
- [ ] E. 커맨드 + Hooks + 단축키 (커스텀 커맨드, 훅, 키보드)
- [ ] F. Cowork + MCP + 고급 기법 (음성입력, VS Code, NotebookLM)

각 분류마다:
- 출처 스크립트 제목 기록
- 직접 인용문 ("..." — 누구) 보존
- 구체적 명령어/설정값 보존 (추상적 요약 지양)

---

### Phase 3: Apple Notes 저장 (3분)

Trading 폴더 양식에 맞춰 Claude 폴더에 주제별 노트를 생성한다.

**양식 규칙:**
```
제목: 이모지 + 짧은 제목 (예: 🧠 핵심 철학 + 병렬 개발)
h1:   <b><span style="font-size: 16px">이모지 제목</span></b>
부제: <i><font face="Courier-Oblique"><span style="font-size: 8px">설명</span></font></i>
섹션: <b><span style="font-size: 12px">이모지 섹션명</span></b>
본문: <font face="Courier"><span style="font-size: 8px"><tt>내용</tt></span></font>
```

- [ ] 분류 A~F 각각 1개 노트 생성 (총 6개)
- [ ] 기존에 동일 제목 노트가 있으면 update_note_content로 갱신
- [ ] 생성된 노트 목록 출력

---

### Phase 4: 메모리 + 전역 지침 반영 (2분)

- [ ] memory/에 참조 메모리 파일 저장 (reference 타입)
  - 파일명: `reference_claude_code_kr_mastery.md`
  - 내용: 학습 자료 출처, 핵심 섹션 구조, Apple Notes 노트 목록
- [ ] MEMORY.md 인덱스에 항목 추가
- [ ] 전역 CLAUDE.md (`~/.claude/CLAUDE.md`)에 "Claude Code 활용 원칙" 섹션 존재 확인
  - 없으면 추가, 있으면 갱신 필요 여부 판단

---

### Phase 5: 완료 보고 (1분)

사용자에게 결과를 보고한다.

- [ ] 읽은 파일 수 / 총 줄 수
- [ ] 생성/갱신된 Apple Notes 노트 목록
- [ ] 메모리 파일 경로
- [ ] 전역 지침 반영 여부
- [ ] 다음 단계 제안 (us 폴더 분석, 특정 주제 심화 등)

---

## 실행 조건

| 조건 | 값 |
|------|-----|
| 전권 위임 | ✅ Phase 순서대로 자동 실행 |
| 사용자 확인 필요 | ❌ 없음 (보고만) |
| 예상 소요 | 20~25분 |
| 의존 도구 | Bash, Read, Apple Notes MCP, Write |
