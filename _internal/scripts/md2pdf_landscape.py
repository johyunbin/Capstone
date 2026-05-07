#!/usr/bin/env python3
"""md2pdf_landscape.py — 16:9 가로형 PPT 스타일 PDF.

회의용 자료 가독성 ↑ 위해 PPT 같은 가로형 layout (1280×720 비율).
- paperWidth=13.33", paperHeight=7.5" (16:9, slide deck 표준)
- max-width 늘림 (250mm), 두 column 친화 layout
- h1/h2 글씨 큼 (slide title 느낌)
- table 가독성 ↑

사용법: python3 _internal/scripts/md2pdf_landscape.py <파일.md>
출력:   같은 디렉토리에 .pdf
폰트:   Apple SD Gothic Neo
"""

import sys
import base64
import json
import os
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import markdown
import websocket

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: 13.33in 7.5in; }
body {
    font-family: 'Apple SD Gothic Neo', -apple-system, sans-serif;
    font-size: 11.5pt; line-height: 1.65; color: #1a202c;
    max-width: 320mm; margin: 0 auto;
    padding: 0 8mm;
}
h1 {
    font-size: 26pt; font-weight: 800; color: #1a202c;
    border-bottom: 4px solid #000000; padding-bottom: 14px;
    margin-top: 0; margin-bottom: 22px;
}
h2 {
    font-size: 19pt; font-weight: 700; color: #fff;
    background: #000000; padding: 12px 20px; border-radius: 8px;
    margin-top: 36px; margin-bottom: 18px;
}
h3 {
    font-size: 14.5pt; font-weight: 700; color: #000000;
    border-left: 5px solid #555555; padding-left: 14px;
    margin-top: 26px; margin-bottom: 12px;
}
h4 {
    font-size: 12.5pt; font-weight: 700; color: #000000;
    margin-top: 20px; margin-bottom: 10px;
}
p { margin: 8px 0; text-align: justify; }
strong { color: #000000; }
blockquote {
    background: #f5f5f5; border-left: 5px solid #555555;
    padding: 14px 20px; margin: 16px 0; border-radius: 0 8px 8px 0;
    font-style: normal; color: #2a4365;
}
blockquote p { margin: 4px 0; }
table {
    width: 100%; border-collapse: collapse;
    margin: 14px 0; font-size: 10pt;
}
th {
    background: #f0f0f0; color: #000000; font-weight: 700;
    padding: 9px 12px; border: 1px solid #cbd5e0; text-align: left;
}
td {
    padding: 8px 12px; border: 1px solid #e2e8f0;
    vertical-align: top;
}
tr:nth-child(even) { background: #f7fafc; }
code {
    background: #edf2f7; padding: 2px 7px; border-radius: 3px;
    font-family: 'D2Coding', 'SF Mono', monospace; font-size: 10pt;
    color: #c53030;
}
pre {
    background: #1a202c; color: #e2e8f0; padding: 14px 18px;
    border-radius: 8px; overflow-x: auto; margin: 14px 0;
    font-size: 9.5pt; line-height: 1.5;
}
pre code { background: none; color: inherit; padding: 0; font-size: 9.5pt; }
ul, ol { padding-left: 28px; margin: 8px 0; }
li { margin: 5px 0; }
hr {
    border: none; border-top: 2px solid #cbd5e0;
    margin: 32px 0;
}
.meta {
    color: #718096; font-size: 10.5pt; line-height: 1.6;
    margin-bottom: 28px;
}
img {
    max-width: 100%; height: auto; display: block;
    margin: 14px auto; page-break-inside: avoid;
}
.page-break { page-break-before: always; }
.page-break + h2, .page-break + h3, .page-break + h4,
.page-break + p, .page-break + table, .page-break + blockquote { margin-top: 0; }
h2, h3, h4 { page-break-after: avoid; }
pre, blockquote, table, li, p, div { page-break-inside: avoid; }
h2 + *, h3 + *, h4 + * { page-break-before: avoid; }
"""

FOOTER_TEMPLATE = (
    '<div style="font-size:10pt;color:#718096;width:100%;text-align:center;'
    "font-family:'Apple SD Gothic Neo',sans-serif;\">"
    '<span class="pageNumber"></span>'
    "</div>"
)
HEADER_TEMPLATE = "<span></span>"


def _find_free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _chrome_cdp_pdf(html_path, out_pdf):
    port = _find_free_port()
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--no-first-run", "--no-default-browser-check",
         "--remote-allow-origins=*",
         f"--remote-debugging-port={port}", f"file://{html_path}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(20):
            try:
                resp = urllib.request.urlopen(f"http://localhost:{port}/json")
                targets = json.loads(resp.read())
                for t in targets:
                    if t.get("type") == "page":
                        ws_url = t["webSocketDebuggerUrl"]
                        break
                if ws_url:
                    break
            except Exception:
                pass
            time.sleep(0.3)
        if not ws_url:
            raise RuntimeError("Chrome CDP 연결 실패")
        ws = websocket.create_connection(ws_url, timeout=15)

        def cdp_send(ws, method, params=None, cmd_id=None):
            msg = {"id": cmd_id or 1, "method": method}
            if params:
                msg["params"] = params
            ws.send(json.dumps(msg))
            while True:
                resp = json.loads(ws.recv())
                if resp.get("id") == msg["id"]:
                    return resp

        cdp_send(ws, "Page.enable", cmd_id=1)
        time.sleep(1)
        result = cdp_send(ws, "Page.printToPDF", params={
            "displayHeaderFooter": True,
            "headerTemplate": HEADER_TEMPLATE,
            "footerTemplate": FOOTER_TEMPLATE,
            "printBackground": True,
            "paperWidth": 13.33,   # 16:9 landscape (1280px @ 96dpi)
            "paperHeight": 7.5,
            "marginTop": 0.5,
            "marginBottom": 0.5,
            "marginLeft": 0.4,
            "marginRight": 0.4,
        }, cmd_id=2)
        if "result" not in result or "data" not in result["result"]:
            raise RuntimeError(f"PDF 생성 실패: {result}")
        with open(out_pdf, "wb") as f:
            f.write(base64.b64decode(result["result"]["data"]))
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def convert(md_path):
    md_path = Path(md_path)
    md_text = md_path.read_text(encoding="utf-8")
    lines = md_text.split("\n")
    meta_lines, body_lines = [], []
    in_meta, title_found = False, False
    for line in lines:
        s = line.strip()
        if not title_found and s.startswith("# "):
            title_found = True
            body_lines.append(line)
            in_meta = True
            continue
        if in_meta and s.startswith("**") and "**:" in s:
            meta_lines.append(s)
            continue
        if in_meta and s == "":
            if meta_lines:
                continue
        else:
            in_meta = False
        body_lines.append(line)
    meta_html = ""
    if meta_lines:
        parts = [m.replace("**", "") for m in meta_lines]
        meta_html = '<div class="meta">' + "<br>".join(parts) + "</div>"
    html_body = markdown.markdown("\n".join(body_lines),
        extensions=["tables", "fenced_code", "codehilite", "toc", "md_in_html"])
    if meta_html:
        html_body = html_body.replace("</h1>", "</h1>\n" + meta_html, 1)
    full_html = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                 f'<style>{CSS}</style></head><body>{html_body}</body></html>')
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html",
                                     delete=False, encoding="utf-8") as f:
        f.write(full_html)
        html_path = f.name
    out_pdf = md_path.with_suffix(".pdf")
    try:
        _chrome_cdp_pdf(html_path, out_pdf)
        print(f"✓ {out_pdf}")
    except Exception as e:
        print(f"✗ {e}")
        sys.exit(1)
    finally:
        os.unlink(html_path)
    return str(out_pdf)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 _internal/scripts/md2pdf_landscape.py <파일.md>")
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"파일 없음: {sys.argv[1]}")
        sys.exit(1)
    convert(sys.argv[1])
