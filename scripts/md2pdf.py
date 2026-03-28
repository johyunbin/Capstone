#!/usr/bin/env python3
"""
md2pdf.py — Markdown → PDF 변환 스크립트 (Chrome headless 방식)
사용법: python3 scripts/md2pdf.py Research/문서이름.md
출력:   Research/문서이름.pdf (같은 디렉토리)
폰트:   Apple SD Gothic Neo (시스템 폰트, Chrome이 직접 렌더링)
"""

import re
import sys
import os
import subprocess
import tempfile
import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def md_to_html(md_text):
    """마크다운을 스타일링된 HTML로 변환"""
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"],
    )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: A4;
    margin: 20mm 18mm 25mm 18mm;
}}

/* ── 섹션 단위 페이지 분리 ── */
/* h2(##) 앞에서 항상 새 페이지 시작 — 첫 번째 h2는 제외 */
h2 {{
    page-break-before: always;
    break-before: always;
}}

/* h1 바로 뒤의 첫 h2는 같은 페이지에 유지 (제목 페이지) */
h1 + h2, h1 + p + h2, h1 + hr + h2 {{
    page-break-before: avoid;
    break-before: avoid;
}}

/* 제목 뒤에 최소 내용 확보 (제목만 달랑 남는 것 방지) */
h1, h2, h3, h4 {{
    page-break-after: avoid;
    break-after: avoid;
}}

/* h3(###)도 바로 앞에서 짤리지 않도록 — 내용과 함께 유지 */
h3, h4 {{
    page-break-before: auto;
    break-before: auto;
}}

/* ── 블록 내부 짤림 방지 ── */
p, li, pre, blockquote {{
    page-break-inside: avoid;
    break-inside: avoid;
    orphans: 3;
    widows: 3;
}}

table {{
    page-break-inside: auto;
    break-inside: auto;
}}

tr {{
    page-break-inside: avoid;
    break-inside: avoid;
}}

thead {{
    display: table-header-group;
}}

body {{
    font-family: "Apple SD Gothic Neo", -apple-system, sans-serif;
    font-size: 10pt;
    line-height: 1.65;
    color: #000000;
    max-width: 100%;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

h1 {{
    font-size: 18pt;
    font-weight: 700;
    text-align: center;
    margin: 0 0 12pt 0;
    padding-bottom: 8pt;
    border-bottom: 2px solid #000;
    color: #000;
}}

h2 {{
    font-size: 13pt;
    font-weight: 700;
    margin: 18pt 0 6pt 0;
    padding-bottom: 3pt;
    border-bottom: 1px solid #ccc;
    color: #000;
}}

h3 {{
    font-size: 11pt;
    font-weight: 700;
    margin: 14pt 0 4pt 0;
    color: #111;
}}

h4 {{
    font-size: 10pt;
    font-weight: 700;
    margin: 10pt 0 3pt 0;
    color: #222;
}}

p {{
    margin: 4pt 0;
}}

ul, ol {{
    margin: 4pt 0;
    padding-left: 20pt;
}}

li {{
    margin: 2pt 0;
}}

blockquote {{
    margin: 8pt 0 8pt 0;
    padding: 8pt 12pt;
    border-left: 3px solid #999;
    color: #333;
    background: #fafafa;
}}

pre {{
    background: #f5f5f5;
    padding: 8pt 10pt;
    border-radius: 3px;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    overflow-x: auto;
    border: 1px solid #e0e0e0;
}}

code {{
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 8.5pt;
    background: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2px;
}}

pre code {{
    background: none;
    padding: 0;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0;
    font-size: 9pt;
}}

th {{
    background: #f0f0f0;
    font-weight: 700;
    text-align: center;
    padding: 5pt 6pt;
    border: 1px solid #ccc;
}}

td {{
    padding: 4pt 6pt;
    border: 1px solid #ccc;
    vertical-align: top;
}}

hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 14pt 0;
}}

strong {{
    font-weight: 700;
}}

/* 페이지 번호 (Chrome print에서는 CSS로 추가) */
@page {{
    @bottom-center {{
        content: counter(page);
        font-size: 8pt;
        color: #999;
    }}
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # h2 앞의 <hr>을 제거 (h2가 page-break-before로 섹션을 나누므로 hr 불필요)
    html = re.sub(r'<hr\s*/?\s*>\s*(<h2)', r'\1', html)
    return html


def html_to_pdf(html_path, pdf_path):
    """Chrome headless로 HTML을 PDF로 변환"""
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-software-rasterizer",
        f"--print-to-pdf={os.path.abspath(pdf_path)}",
        "--print-to-pdf-no-header",
        os.path.abspath(html_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"Chrome 에러: {result.stderr}", file=sys.stderr)
        return False
    return True


def convert(md_path):
    from datetime import datetime

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 파일명에 타임스탬프가 있으면 현재 시간으로 갱신
    # 패턴: 연구방향_설계안_YYYYMMDD_HHMMSS.md
    dir_name = os.path.dirname(md_path)
    base_name = os.path.basename(md_path)
    now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    ts_pattern = re.compile(r'(\d{8}_\d{6})')
    if ts_pattern.search(base_name):
        new_base = ts_pattern.sub(now_ts, base_name)
        new_md_path = os.path.join(dir_name, new_base) if dir_name else new_base
        os.rename(md_path, new_md_path)
        md_path = new_md_path
        print(f"  → md 파일명 갱신: {new_base}")

    html_content = md_to_html(md_text)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(html_content)
        tmp_html = tmp.name

    pdf_path = md_path.rsplit(".", 1)[0] + ".pdf"

    try:
        if html_to_pdf(tmp_html, pdf_path):
            print(f"✓ {pdf_path}")
            return pdf_path
        else:
            print(f"✗ PDF 생성 실패: {md_path}", file=sys.stderr)
            return None
    finally:
        os.unlink(tmp_html)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 scripts/md2pdf.py <파일.md>")
        sys.exit(1)

    md_file = sys.argv[1]

    if not os.path.exists(md_file):
        print(f"파일 없음: {md_file}")
        sys.exit(1)

    convert(md_file)
