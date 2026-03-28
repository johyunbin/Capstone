#!/bin/bash
# Stop hook: /clear 또는 세션 종료 시 상태 저장 + 메모리 업데이트 리마인더
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

python3 -c "
import json
from datetime import datetime
from pathlib import Path
import subprocess

root = Path('$PROJECT_ROOT')
research = root / 'Research'

state = {
    'timestamp': datetime.now().isoformat(),
    'session_type': 'stop_save',
}

md_count = len(list(research.glob('*.md'))) if research.exists() else 0
pdf_count = len(list(research.glob('*.pdf'))) if research.exists() else 0
state['research_md'] = md_count
state['research_pdf'] = pdf_count

try:
    branch = subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip()
    uncommitted = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip()
    state['git_branch'] = branch
    state['git_uncommitted'] = len(uncommitted.splitlines()) if uncommitted else 0
except:
    pass

state_file = root / 'session_state.json'
with open(state_file, 'w') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
" 2>/dev/null

echo '{"systemMessage": "⚠️ 세션 종료 전 메모리 업데이트 확인: 이번 세션 작업 내용이 memory/ 파일에 반영됐나요? 반영 안 됐다면 /clear 전에 먼저 업데이트 요청하세요."}'
