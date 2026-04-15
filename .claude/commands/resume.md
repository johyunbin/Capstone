지침 Phase 재개 커맨드.

1. `PHASE_STATE.json` 읽기 → `current_guideline`, `current_phase` 확인
2. 해당 지침의 `guideline/PHASE_STATE_NN_{지침명}.md` 읽기
3. 마지막 완료 Phase 다음 Phase부터 재개
4. 해당 지침의 manual.md 로드하여 Phase 내용 확인 후 실행

인자가 있으면 해당 지침으로 재개:
- `/resume 02_제출물지침` → 02 지침의 중단 지점부터
- `/resume` (인자 없음) → PHASE_STATE.json의 current_guideline 기준
