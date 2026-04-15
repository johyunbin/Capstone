Git 원클릭 동기화 커맨드.

인자에 따라 동작:

**`/sync` (인자 없음) — commit + push:**
```bash
cd ~/Capstone && git add -A && git commit -m "sync: $ARGUMENTS" && git push origin main
```
- $ARGUMENTS가 비어있으면 변경 파일 목록 기반으로 커밋 메시지 자동 생성

**`/sync pull` — pull:**
```bash
cd ~/Capstone && git pull --no-rebase origin main
```

커밋 메시지 규칙:
- 문서 작업: `sync: 논문분석 [N]번 추가` / `sync: 설계안 업데이트`
- 지침 작업: `sync: {지침명} Phase N 완료`
- 기타: `sync: {변경 요약}`
