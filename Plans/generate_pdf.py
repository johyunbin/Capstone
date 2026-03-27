#!/usr/bin/env python3
"""
연구방향 설계안 MD → PDF (3가지 폰트 버전)
Markdown → HTML(CSS 폰트 지정) → Chrome headless PDF
"""

import markdown
import subprocess
import tempfile
from pathlib import Path

MD_PATH = Path(__file__).parent / "연구방향_설계안.md"
OUT_DIR = Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

md_text = MD_PATH.read_text(encoding="utf-8")
html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "codehilite", "toc"],
)

FONTS = [
    {
        "key": "AppleNeo",
        "label": "Apple SD Gothic Neo",
        "family": "'Apple SD Gothic Neo', 'AppleSDGothicNeo', sans-serif",
        "heading_weight": "800",
    },
]


def make_html(body: str, font_family: str, heading_weight: str, label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>연구방향 설계안 — {label}</title>
<style>
@page {{
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
}}

body {{
    font-family: {font_family};
    font-size: 10pt;
    line-height: 1.75;
    color: #1a1a1a;
    word-break: keep-all;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}

h1 {{
    font-size: 20pt;
    font-weight: {heading_weight};
    color: #111;
    border-bottom: 2.5px solid #222;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 16px;
}}

h2 {{
    font-size: 14pt;
    font-weight: 700;
    color: #1a1a1a;
    margin-top: 28px;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1.2px solid #ddd;
    page-break-before: always;
}}

h1 + hr + h2 {{
    page-break-before: auto;
}}

h2:first-of-type {{
    page-break-before: auto;
}}

h3 {{
    font-size: 12pt;
    font-weight: 700;
    color: #333;
    margin-top: 22px;
    margin-bottom: 8px;
    page-break-after: avoid;
}}

h4 {{
    page-break-after: avoid;
}}

h4 {{
    font-size: 11pt;
    font-weight: 600;
    color: #444;
    margin-top: 16px;
    margin-bottom: 6px;
}}

p {{
    margin: 6px 0;
}}

blockquote {{
    margin: 16px 0;
    padding: 14px 20px;
    border-left: 4px solid #4a90d9;
    background: #f0f5fb;
    color: #2a2a2a;
    font-size: 9.5pt;
    border-radius: 0 4px 4px 0;
}}

blockquote p {{
    margin: 4px 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
}}

th {{
    background: #2c3e50;
    color: #fff;
    font-weight: 600;
    padding: 8px 10px;
    text-align: left;
    border: 1px solid #2c3e50;
}}

td {{
    padding: 7px 10px;
    border: 1px solid #ddd;
    vertical-align: top;
}}

tr:nth-child(even) td {{
    background: #f8f9fa;
}}

code {{
    font-family: 'D2Coding', 'D2Coding ligature', 'Menlo', 'Consolas', monospace;
    font-size: 9pt;
    background: #f4f4f4;
    padding: 1px 5px;
    border-radius: 3px;
    color: #c7254e;
}}

pre {{
    background: #282c34;
    color: #abb2bf;
    padding: 16px 18px;
    border-radius: 6px;
    font-size: 8.5pt;
    line-height: 1.55;
    overflow-x: auto;
    margin: 12px 0;
    page-break-inside: avoid;
}}

table {{
    page-break-inside: avoid;
}}

blockquote {{
    page-break-inside: avoid;
}}

pre code {{
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
}}

ul, ol {{
    margin: 6px 0;
    padding-left: 24px;
}}

li {{
    margin: 3px 0;
}}

hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 24px 0;
}}

strong {{
    font-weight: 700;
}}

a {{
    color: #4a90d9;
    text-decoration: none;
}}
</style>
</head>
<body>
{body}
</body>
</html>"""


for cfg in FONTS:
    html = make_html(html_body, cfg["family"], cfg["heading_weight"], cfg["label"])

    # HTML을 임시파일에 저장
    tmp_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp_html.write(html)
    tmp_html.close()

    out_pdf = OUT_DIR / "연구방향_설계안.pdf"

    print(f"  {cfg['label']}...", end=" ", flush=True)
    result = subprocess.run([
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--print-to-pdf=" + str(out_pdf),
        "--no-pdf-header-footer",
        tmp_html.name,
    ], capture_output=True, text=True, timeout=30)

    Path(tmp_html.name).unlink()

    if out_pdf.exists():
        size_kb = out_pdf.stat().st_size / 1024
        print(f"OK ({size_kb:.0f}KB)")
    else:
        print(f"FAIL: {result.stderr[:200]}")

print("\n완료!")
