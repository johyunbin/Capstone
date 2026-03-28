#!/usr/bin/env python3
"""
md2pdf.py — Markdown → PDF 변환 스크립트
사용법: python3 scripts/md2pdf.py plans/문서이름.md
출력:   plans/문서이름.pdf (같은 디렉토리)
방식:   Markdown → HTML+CSS → Chrome headless PDF
폰트:   Apple SD Gothic Neo (고정)
"""

import markdown
import subprocess
import sys
import os
import tempfile
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page {
    size: A4;
    margin: 25mm 20mm 20mm 20mm;
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        color: #718096;
        font-family: 'Apple SD Gothic Neo', -apple-system, sans-serif;
    }
}
body {
    font-family: 'Apple SD Gothic Neo', -apple-system, sans-serif;
    font-size: 11pt; line-height: 1.7; color: #1a202c;
    max-width: 170mm; margin: 0 auto;
}
h1 {
    font-size: 22pt; font-weight: 800; color: #1a202c;
    border-bottom: 3px solid #000000; padding-bottom: 12px;
    margin-top: 0; margin-bottom: 20px;
}
h2 {
    font-size: 16pt; font-weight: 700; color: #fff;
    background: #000000; padding: 10px 16px; border-radius: 6px;
    margin-top: 32px; margin-bottom: 16px;
}
h3 {
    font-size: 13pt; font-weight: 700; color: #000000;
    border-left: 4px solid #555555; padding-left: 12px;
    margin-top: 24px; margin-bottom: 10px;
}
h4 {
    font-size: 11.5pt; font-weight: 700; color: #000000;
    margin-top: 18px; margin-bottom: 8px;
}
p { margin: 8px 0; text-align: justify; }
strong { color: #000000; }
blockquote {
    background: #f5f5f5; border-left: 4px solid #555555;
    padding: 14px 18px; margin: 16px 0; border-radius: 0 6px 6px 0;
    font-style: normal; color: #2a4365;
}
blockquote p { margin: 4px 0; }
table {
    width: 100%; border-collapse: collapse;
    margin: 14px 0; font-size: 9.5pt;
}
th {
    background: #f5f5f5; color: #000000; font-weight: 700;
    padding: 8px 10px; border: 1px solid #cbd5e0; text-align: left;
}
td {
    padding: 7px 10px; border: 1px solid #e2e8f0;
    vertical-align: top;
}
tr:nth-child(even) { background: #f7fafc; }
code {
    background: #edf2f7; padding: 2px 6px; border-radius: 3px;
    font-family: 'D2Coding', 'SF Mono', monospace; font-size: 9.5pt;
    color: #e53e3e;
}
pre {
    background: #000000; color: #e2e8f0; padding: 14px 18px;
    border-radius: 6px; overflow-x: auto; margin: 14px 0;
    font-size: 9pt; line-height: 1.5;
}
pre code {
    background: none; color: inherit; padding: 0;
    font-size: 9pt;
}
ul, ol { padding-left: 24px; margin: 8px 0; }
li { margin: 4px 0; }
hr {
    border: none; border-top: 1px solid #e2e8f0;
    margin: 28px 0;
}
.meta {
    color: #718096; font-size: 9.5pt; line-height: 1.6;
    margin-bottom: 24px;
}
/* 페이지 구분 */
.page-break { page-break-before: always; }
/* 고아 제목 방지: 제목 뒤에 내용이 같이 와야 함 */
h2, h3, h4 { page-break-after: avoid; }
/* 블록 내부 짤림 방지 */
pre, blockquote { page-break-inside: avoid; }
table { page-break-inside: avoid; }
li { page-break-inside: avoid; }
"""


def convert(md_path):
    md_path = Path(md_path)
    md_text = md_path.read_text(encoding="utf-8")

    # 메타 정보 분리 (작성일, 목적 등 **key**: value 형태)
    lines = md_text.split("\n")
    meta_lines = []
    body_lines = []
    in_meta = False
    title_found = False

    for line in lines:
        stripped = line.strip()
        if not title_found and stripped.startswith("# "):
            title_found = True
            body_lines.append(line)
            in_meta = True
            continue
        if in_meta and stripped.startswith("**") and "**:" in stripped:
            meta_lines.append(stripped)
            continue
        if in_meta and stripped == "":
            if meta_lines:
                continue
        else:
            in_meta = False
        body_lines.append(line)

    # 메타를 별도 div로
    meta_html = ""
    if meta_lines:
        meta_parts = []
        for m in meta_lines:
            m = m.replace("**", "")
            meta_parts.append(m)
        meta_html = '<div class="meta">' + "<br>".join(meta_parts) + "</div>"

    # Markdown → HTML
    html_body = markdown.markdown(
        "\n".join(body_lines),
        extensions=["tables", "fenced_code", "codehilite", "toc"],
    )

    # 제목 뒤에 메타 삽입
    if meta_html:
        html_body = html_body.replace("</h1>", "</h1>\n" + meta_html, 1)

    full_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{CSS}</style>
</head><body>
{html_body}
</body></html>"""

    # 임시 HTML 저장
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(full_html)
        html_path = f.name

    # Chrome headless → PDF
    out_pdf = md_path.with_suffix(".pdf")
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={out_pdf}",
        "--print-to-pdf-no-header",
        f"file://{html_path}",
    ]

    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        print(f"✓ {out_pdf}")
    except FileNotFoundError:
        print(f"Chrome을 찾을 수 없습니다: {CHROME}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Chrome PDF 변환 타임아웃")
        sys.exit(1)
    finally:
        os.unlink(html_path)

    return str(out_pdf)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 scripts/md2pdf.py <파일.md>")
        sys.exit(1)

    md_file = sys.argv[1]
    if not os.path.exists(md_file):
        print(f"파일 없음: {md_file}")
        sys.exit(1)

    convert(md_file)
