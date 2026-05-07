#!/usr/bin/env python3
"""md2pdf_academic.py — Academic v3 톤 (navy accent) variant of md2pdf.py.

5/27 발표 deck Academic v3 (#1B365D navy + Apple SD Gothic Neo) 와 일관 톤으로
회의용 자료 PDF 생성. 기존 md2pdf.py 의 CSS 만 override.

사용법: python3 _internal/scripts/md2pdf_academic.py <파일.md>
출력:   같은 디렉토리에 .pdf
폰트:   Apple SD Gothic Neo
색:     navy #1B365D + light #F5F7FA + gray #6B7280
"""

import sys
from pathlib import Path

# md2pdf import
sys.path.insert(0, str(Path(__file__).parent))
import md2pdf

NAVY = "#1B365D"
LIGHT = "#F5F7FA"
GRAY = "#6B7280"

ACADEMIC_CSS = f"""
@page {{ size: A4; }}
body {{
    font-family: 'Apple SD Gothic Neo', -apple-system, sans-serif;
    font-size: 11pt; line-height: 1.7; color: #1a202c;
    max-width: 170mm; margin: 0 auto;
}}
h1 {{
    font-size: 22pt; font-weight: 800; color: {NAVY};
    border-bottom: 3px solid {NAVY}; padding-bottom: 12px;
    margin-top: 0; margin-bottom: 20px;
}}
h2 {{
    font-size: 16pt; font-weight: 700; color: #fff;
    background: {NAVY}; padding: 10px 16px; border-radius: 6px;
    margin-top: 32px; margin-bottom: 16px;
}}
h3 {{
    font-size: 13pt; font-weight: 700; color: {NAVY};
    border-left: 4px solid {NAVY}; padding-left: 12px;
    margin-top: 24px; margin-bottom: 10px;
}}
h4 {{
    font-size: 11.5pt; font-weight: 700; color: {NAVY};
    margin-top: 18px; margin-bottom: 8px;
}}
p {{ margin: 8px 0; text-align: justify; }}
strong {{ color: {NAVY}; }}
blockquote {{
    background: {LIGHT}; border-left: 4px solid {NAVY};
    padding: 14px 18px; margin: 16px 0; border-radius: 0 6px 6px 0;
    font-style: normal; color: {NAVY};
}}
blockquote p {{ margin: 4px 0; }}
table {{
    width: 100%; border-collapse: collapse;
    margin: 14px 0; font-size: 9.5pt;
}}
th {{
    background: {NAVY}; color: #fff; font-weight: 700;
    padding: 8px 10px; border: 1px solid {NAVY}; text-align: left;
}}
td {{
    padding: 7px 10px; border: 1px solid #e2e8f0;
    vertical-align: top;
}}
tr:nth-child(even) {{ background: {LIGHT}; }}
code {{
    background: #edf2f7; padding: 2px 6px; border-radius: 3px;
    font-family: 'D2Coding', 'SF Mono', monospace; font-size: 9.5pt;
    color: #c53030;
}}
pre {{
    background: {NAVY}; color: #e2e8f0; padding: 14px 18px;
    border-radius: 6px; overflow-x: auto; margin: 14px 0;
    font-size: 9pt; line-height: 1.5;
}}
pre code {{
    background: none; color: inherit; padding: 0;
    font-size: 9pt;
}}
ul, ol {{ padding-left: 24px; margin: 8px 0; }}
li {{ margin: 4px 0; }}
hr {{
    border: none; border-top: 2px solid {NAVY};
    margin: 28px 0;
}}
.meta {{
    color: {GRAY}; font-size: 9.5pt; line-height: 1.6;
    margin-bottom: 24px;
}}
img {{
    max-width: 100%; height: auto; display: block;
    margin: 14px auto; page-break-inside: avoid;
}}
.page-break {{ page-break-before: always; }}
.page-break + h2, .page-break + h3, .page-break + h4,
.page-break + p, .page-break + table, .page-break + blockquote {{ margin-top: 0; }}
h2, h3, h4 {{ page-break-after: avoid; }}
pre, blockquote {{ page-break-inside: avoid; }}
table {{ page-break-inside: avoid; }}
li {{ page-break-inside: avoid; }}
p {{ page-break-inside: avoid; }}
div {{ page-break-inside: avoid; }}
h2 + *, h3 + *, h4 + * {{ page-break-before: avoid; }}
"""

md2pdf.CSS = ACADEMIC_CSS

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 _internal/scripts/md2pdf_academic.py <파일.md>")
        sys.exit(1)
    md_file = sys.argv[1]
    if not Path(md_file).exists():
        print(f"파일 없음: {md_file}")
        sys.exit(1)
    md2pdf.convert(md_file)
