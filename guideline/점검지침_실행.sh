#!/bin/bash
# 점검지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/점검지침_실행.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/점검지침.log"

echo "=== 점검지침 시작: $(date) ===" | tee "$LOG_FILE"

# Phase 0: 인벤토리 수집
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 0: 인벤토리 수집 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

A_MD=$(ls research/analysis/*.md 2>/dev/null | wc -l | tr -d ' ')
A_PDF=$(ls research/analysis/*.pdf 2>/dev/null | wc -l | tr -d ' ')
S_MD=$(ls research/summaries/*.md 2>/dev/null | wc -l | tr -d ' ')
S_PDF=$(ls research/summaries/*.pdf 2>/dev/null | wc -l | tr -d ' ')
PAPERS=$(ls research/papers/*.pdf 2>/dev/null | wc -l | tr -d ' ')
SUBMISSION=$(ls submission/ 2>/dev/null | wc -l | tr -d ' ')
PLANS=$(ls plans/ 2>/dev/null | wc -l | tr -d ' ')

echo "analysis: ${A_MD} md, ${A_PDF} pdf" | tee -a "$LOG_FILE"
echo "summaries: ${S_MD} md, ${S_PDF} pdf" | tee -a "$LOG_FILE"
echo "papers: ${PAPERS}" | tee -a "$LOG_FILE"
echo "submission: ${SUBMISSION}" | tee -a "$LOG_FILE"
echo "plans: ${PLANS}" | tee -a "$LOG_FILE"

# Phase 1: 2종 세트 완성도 검증
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 1: 2종 세트 검증 ---" | tee -a "$LOG_FILE"
MISSING=0

cd "$PROJECT_ROOT/research/analysis"
for f in *.md; do
  pdf="${f%.md}.pdf"
  if [ ! -f "$pdf" ]; then
    echo "MISSING: analysis/$pdf" | tee -a "$LOG_FILE"
    MISSING=$((MISSING + 1))
  fi
done

cd "$PROJECT_ROOT/research/summaries"
for f in *.md; do
  pdf="${f%.md}.pdf"
  if [ ! -f "$pdf" ]; then
    echo "MISSING: summaries/$pdf" | tee -a "$LOG_FILE"
    MISSING=$((MISSING + 1))
  fi
done

echo "누락 파일: ${MISSING}건" | tee -a "$LOG_FILE"

# Phase 2: PDF 폰트 검증
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 2: PDF 폰트 검증 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

python3 -c "
import glob, os
try:
    import pypdf
except ImportError:
    print('pypdf 미설치 — pip3 install pypdf 필요')
    exit(0)

ok, bad, bad_list = 0, 0, []
for d in ['research/analysis', 'research/summaries']:
    for p in sorted(glob.glob(f'{d}/*.pdf')):
        try:
            reader = pypdf.PdfReader(p)
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

# Phase 3: 파일명 규칙 검증
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 3: 파일명 규칙 검증 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

python3 -c "
import re, os
a_pat = re.compile(r'^\(\d+\) .+\.(md|pdf)$')
s_pat = re.compile(r'^\[\d+\] .+ 총정리\.(md|pdf)$')
errors = 0

for f in sorted(os.listdir('research/analysis')):
    if f.startswith('.'):
        continue
    if not a_pat.match(f):
        print(f'analysis 비규격: {f}')
        errors += 1

for f in sorted(os.listdir('research/summaries')):
    if f.startswith('.'):
        continue
    if not s_pat.match(f):
        print(f'summaries 비규격: {f}')
        errors += 1

print(f'비규격 파일: {errors}건')
" 2>&1 | tee -a "$LOG_FILE"

# Phase 4: orphan 파일 검사
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 4: orphan 파일 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

ORPHAN=$(find . -path ./.git -prune -o \( -name "*.tmp" -o -name "*.bak" -o -name "*.swp" \) -print 2>/dev/null | wc -l | tr -d ' ')
DS=$(find . -path ./.git -prune -o -name ".DS_Store" -print 2>/dev/null | wc -l | tr -d ' ')

echo "orphan(.tmp/.bak/.swp): ${ORPHAN}건" | tee -a "$LOG_FILE"
echo ".DS_Store: ${DS}건" | tee -a "$LOG_FILE"

if grep -q "DS_Store" .gitignore 2>/dev/null; then
  echo ".gitignore: DS_Store 포함 OK" | tee -a "$LOG_FILE"
else
  echo "WARNING: .gitignore에 DS_Store 미포함" | tee -a "$LOG_FILE"
fi

# Phase 5: 원논문 ↔ 총정리 대응
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 5: 원논문 대응 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT/research/summaries"

UNIQUE_NUMS=$(ls *.md 2>/dev/null | grep -oP '^\[\K\d+' | sort -n | uniq | wc -l | tr -d ' ')
echo "summaries 고유 번호: ${UNIQUE_NUMS}" | tee -a "$LOG_FILE"
echo "papers 원논문: ${PAPERS}" | tee -a "$LOG_FILE"

# Phase 6: 종합 리포트
echo "" | tee -a "$LOG_FILE"
echo "--- 종합 리포트 ---" | tee -a "$LOG_FILE"
echo "인벤토리: analysis ${A_MD}md/${A_PDF}pdf, summaries ${S_MD}md/${S_PDF}pdf" | tee -a "$LOG_FILE"
echo "2종 세트 누락: ${MISSING}건" | tee -a "$LOG_FILE"
echo "orphan: ${ORPHAN}건" | tee -a "$LOG_FILE"
echo "summaries 번호: ${UNIQUE_NUMS}종 / papers: ${PAPERS}편" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== 점검지침 완료: $(date) ===" | tee -a "$LOG_FILE"
echo "상세 로그: ${LOG_FILE}"

# Claude Code 연동 (전체 Phase를 Claude에게 위임할 경우)
# claude --print "guideline/점검지침_auto.md 읽고 전체 Phase 실행" 2>&1 | tee -a "$LOG_FILE"
