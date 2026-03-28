#!/bin/bash
# PreCompact hook: 압축 전 세션 상태 저장
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

python3 -c "
import json, os
from datetime import datetime
from pathlib import Path

root = Path('$PROJECT_ROOT')
research = root / 'research' / 'summaries'

state = {
    'timestamp': datetime.now().isoformat(),
    'session_type': 'pre_compact_save',
}

# 문서 현황
md_count = len(list(research.glob('*.md'))) if research.exists() else 0
pdf_count = len(list(research.glob('*.pdf'))) if research.exists() else 0
state['research_md'] = md_count
state['research_pdf'] = pdf_count

# Git 상태
import subprocess
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

echo '{"hookSpecificOutput": {"hookEventName": "PreCompact", "additionalContext": "세션 상태 저장됨 (session_state.json)"}}'
