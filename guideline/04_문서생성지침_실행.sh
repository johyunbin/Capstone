#!/bin/bash
# 문서생성지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/04_문서생성지침_실행.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/04_문서생성지침.log"

echo "=== 문서생성지침 시작: $(date) ===" | tee "$LOG_FILE"

# Phase 0: 환경 확인
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 0: 환경 확인 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

ENV_OK=true

python3 -c "import markdown; print('markdown OK')" 2>&1 | tee -a "$LOG_FILE" || {
  echo "markdown 미설치 — 설치 시도" | tee -a "$LOG_FILE"
  pip3 install markdown 2>&1 | tee -a "$LOG_FILE"
}

python3 -c "import websocket; print('websocket-client OK')" 2>&1 | tee -a "$LOG_FILE" || {
  echo "websocket-client 미설치 — 설치 시도" | tee -a "$LOG_FILE"
  pip3 install websocket-client 2>&1 | tee -a "$LOG_FILE"
}

if [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  echo "Chrome OK" | tee -a "$LOG_FILE"
else
  echo "ERROR: Chrome 미설치 — 변환 불가" | tee -a "$LOG_FILE"
  ENV_OK=false
fi

if [ -f scripts/md2pdf.py ]; then
  echo "md2pdf.py OK" | tee -a "$LOG_FILE"
else
  echo "ERROR: scripts/md2pdf.py 없음" | tee -a "$LOG_FILE"
  ENV_OK=false
fi

if [ "$ENV_OK" = false ]; then
  echo "환경 확인 실패 — 중단" | tee -a "$LOG_FILE"
  exit 1
fi

# Phase 1: 누락 PDF 탐지
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 1: 누락 PDF 탐지 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

MISSING_LIST=""
MISSING_COUNT=0

for d in research/analysis research/summaries plans; do
  [ ! -d "$d" ] && continue
  for f in "$d"/*.md; do
    [ ! -f "$f" ] && continue
    pdf="${f%.md}.pdf"
    if [ ! -f "$pdf" ]; then
      MISSING_LIST="$MISSING_LIST $f"
      MISSING_COUNT=$((MISSING_COUNT + 1))
      echo "누락: $pdf" | tee -a "$LOG_FILE"
    fi
  done
done

echo "누락 PDF: ${MISSING_COUNT}건" | tee -a "$LOG_FILE"

# Phase 2: PDF 변환 실행
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 2: PDF 변환 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

SUCCESS=0
FAIL=0
FAIL_LIST=""

if [ "$MISSING_COUNT" -eq 0 ]; then
  echo "누락 없음 — 변환 건너뜀" | tee -a "$LOG_FILE"
else
  for f in $MISSING_LIST; do
    echo "변환 중: $f" | tee -a "$LOG_FILE"
    if python3 scripts/md2pdf.py "$f" 2>&1 | tee -a "$LOG_FILE"; then
      SUCCESS=$((SUCCESS + 1))
    else
      FAIL=$((FAIL + 1))
      FAIL_LIST="$FAIL_LIST $f"
      echo "FAIL: $f" | tee -a "$LOG_FILE"
    fi
    # Chrome 포트 충돌 방지 — 변환 간 짧은 대기
    sleep 1
  done

  echo "변환 결과: 성공 ${SUCCESS}건, 실패 ${FAIL}건" | tee -a "$LOG_FILE"

  # 실패 파일 재시도 (Chrome 프로세스 정리 후)
  if [ "$FAIL" -gt 0 ]; then
    echo "실패 파일 재시도..." | tee -a "$LOG_FILE"
    pkill -f "chrome.*remote-debugging-port" 2>/dev/null || true
    sleep 2
    for f in $FAIL_LIST; do
      echo "재시도: $f" | tee -a "$LOG_FILE"
      if python3 scripts/md2pdf.py "$f" 2>&1 | tee -a "$LOG_FILE"; then
        SUCCESS=$((SUCCESS + 1))
        FAIL=$((FAIL - 1))
      fi
      sleep 1
    done
    echo "재시도 후: 성공 ${SUCCESS}건, 실패 ${FAIL}건" | tee -a "$LOG_FILE"
  fi
fi

# Phase 3: 품질 검증
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 3: 품질 검증 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

python3 -c "
import glob, os
try:
    import pypdf
except ImportError:
    print('pypdf 미설치 — pip3 install pypdf 필요')
    exit(0)

ok, bad, bad_list = 0, 0, []
for d in ['research/analysis', 'research/summaries', 'plans']:
    for p in sorted(glob.glob(f'{d}/*.pdf')):
        try:
            reader = pypdf.PdfReader(p)
            if len(reader.pages) == 0:
                bad += 1
                bad_list.append(f'{os.path.basename(p)} (0페이지)')
                continue
            fonts = set()
            for page in reader.pages:
                res = page.get('/Resources')
                if res and '/Font' in res:
                    for font in res['/Font'].values():
                        fo = font.get_object() if hasattr(font, 'get_object') else font
                        bf = str(fo.get('/BaseFont', 'Unknown'))
                        fonts.add(bf)
            has_real = any('Unknown' not in f for f in fonts) if fonts else False
            if has_real:
                ok += 1
            else:
                bad += 1
                bad_list.append(os.path.basename(p))
        except Exception as e:
            bad += 1
            bad_list.append(f'{os.path.basename(p)} (err: {e})')

print(f'정상: {ok}, 비정상: {bad}')
for f in bad_list:
    print(f'  WARNING: {f}')
" 2>&1 | tee -a "$LOG_FILE"

# 종합 리포트
echo "" | tee -a "$LOG_FILE"
echo "--- 종합 리포트 ---" | tee -a "$LOG_FILE"
echo "환경: OK" | tee -a "$LOG_FILE"
echo "누락 탐지: ${MISSING_COUNT}건 발견" | tee -a "$LOG_FILE"
echo "변환 결과: 성공 ${SUCCESS}건, 실패 ${FAIL}건" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== 문서생성지침 완료: $(date) ===" | tee -a "$LOG_FILE"
echo "상세 로그: ${LOG_FILE}"

# Claude Code 연동 (전체 Phase를 Claude에게 위임할 경우)
# claude --print "guideline/04_문서생성지침_auto.md 읽고 전체 Phase 실행" 2>&1 | tee -a "$LOG_FILE"
