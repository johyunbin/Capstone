#!/usr/bin/env python3
"""
md2pdf.py — Markdown → PDF 변환 스크립트 (Capstone 학술 보고서 양식 v2)

사용법: python3 _internal/scripts/md2pdf.py <파일.md>
출력:   <같은 디렉토리>/<파일>.pdf
방식:   Markdown → HTML+CSS → Chrome CDP (DevTools Protocol) → PDF
폰트:   Apple SD Gothic Neo + Pretendard + Noto Sans KR (한영 혼용 가독성)

설계 (2026-05-14 v2):
  - Trading/src/npc_briefing_pdf.py 의 latest CSS (S43 v6, 5/13) 를 base 로 가져왔다.
  - navy primary (#1a2c4e) + orange accent (#b85c00) + Apple charcoal (#1d1d1f) 통일.
  - 학술 보고서 특화 보강:
      * margin 18mm (brief 14mm 보다 여유, 학술 표준)
      * font-size 본문 10.5pt (brief 10pt 보다 살짝 큼, 보고서 가독성)
      * H1 큰 배너 (22pt), H2 navy bg + 왼쪽 바, H3 단단한 weight
      * 표 (table) caption 표시 보강, 학술 비교 table 가독성 강조
      * 메타 블록 (**key**: value) 자동 감지 → .meta div 로 분리
      * 페이지 번호 footer (가운데), 빈 header
  - brief-specific feature 제거 (BRIEF_PAGE_LAYOUT, brief_lint, summary table 컬럼 고정 등).
"""

import base64
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import markdown
import websocket

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


# ==============================================================================
# CSS — Capstone 학술 보고서 양식 v2 (Trading S43 v6 base + 학술 보강)
# ==============================================================================
CSS = """
/* Capstone 양식 v2 — primary navy #1a2c4e, accent orange #b85c00.
   학술 보고서 톤 (margin 넉넉 + 본문 10.5pt + line-height 1.75). */
@page { size: A4; margin: 18mm 18mm 18mm 18mm; }

body {
    font-family: 'Apple SD Gothic Neo', 'Pretendard', 'Noto Sans KR',
                 -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
    font-size: 10.5pt;
    line-height: 1.75;          /* Apple 표준, 학술 가독성 우선 */
    color: #1d1d1f;             /* Apple charcoal */
    background: #ffffff;
    max-width: 175mm;
    margin: 0 auto;
    word-break: keep-all;
    overflow-wrap: break-word;
    line-break: strict;
    hyphens: none;
    letter-spacing: -0.005em;
    -webkit-font-smoothing: antialiased;
}

p {
    margin: 8px 0;
    text-align: left;
    word-break: keep-all;
    overflow-wrap: break-word;
    line-break: strict;
    color: #1d1d1f;
}

li {
    margin: 4px 0;
    word-break: keep-all;
    overflow-wrap: break-word;
    line-height: 1.65;
}

/* H1 — 진네이비 배너 (문서 타이틀) */
h1 {
    font-size: 20pt;
    font-weight: 800;
    color: #ffffff;
    background: #1a2c4e;
    padding: 14px 20px;
    border-radius: 8px;
    margin: 0 0 18px 0;
    letter-spacing: -0.3px;
    line-height: 1.35;
}

/* H2 — Apple 스타일 (subtle bg + 좌측 navy 바) */
h2 {
    font-size: 14pt;
    font-weight: 700;
    color: #1a2c4e;
    background: #f5f5f7;
    border-left: 5px solid #1a2c4e;
    padding: 9px 16px;
    margin: 22px 0 10px 0;
    border-radius: 0 6px 6px 0;
    letter-spacing: -0.01em;
    page-break-after: avoid;
    break-after: avoid;
}

/* H3 — 단단한 weight + 좌측 얇은 회색 바 */
h3 {
    font-size: 12pt;
    font-weight: 700;
    color: #1a2c4e;
    border-left: 3px solid #b85c00;
    padding-left: 10px;
    margin: 16px 0 8px 0;
    letter-spacing: -0.005em;
}

/* H4 — 오렌지 악센트 (서브섹션) */
h4 {
    font-size: 11pt;
    font-weight: 700;
    color: #b85c00;
    margin: 12px 0 6px 0;
}

/* H5 — 본문 weight 강조 (보고서 깊이 5단계까지) */
h5 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1d1d1f;
    margin: 10px 0 4px 0;
}

strong { color: #1a2c4e; font-weight: 700; }
em { color: #1d1d1f; font-style: italic; }

/* 인용 — 연한 베이지 + 오렌지 좌측 바 (Apple 카드 스타일) */
blockquote {
    background: #fafaf7;
    border-left: 4px solid #b85c00;
    padding: 10px 16px;
    margin: 10px 0;
    border-radius: 6px;
    color: #1d1d1f;
    font-size: 10pt;
    line-height: 1.7;
    word-break: keep-all;
    overflow-wrap: break-word;
    line-break: strict;
    page-break-inside: avoid;
}
blockquote p {
    margin: 6px 0;
    color: #1d1d1f;
}
blockquote strong { color: #1a2c4e; }

/* 메타 (타이틀 직후 작성자/일자/목적) */
.meta {
    color: #546e7a;
    font-size: 9.5pt;
    line-height: 1.7;
    margin: -6px 0 16px 0;
    padding: 8px 14px;
    background: #f5f5f7;
    border-radius: 6px;
    border-left: 3px solid #b85c00;
}
.meta strong { color: #1a2c4e; }

/* 테이블 — 학술 비교 강조 (진네이비 헤더 + 줄무늬 + caption) */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9pt;
    border: 1px solid #1a2c4e;
    border-radius: 4px;
    overflow: hidden;
    table-layout: auto;
    page-break-inside: avoid;
}
th, td {
    word-break: keep-all;
    overflow-wrap: break-word;
    line-break: strict;
    hyphens: none;
}
th {
    background: #1a2c4e;
    color: #ffffff;
    font-weight: 700;
    padding: 7px 10px;
    border: 1px solid #1a2c4e;
    text-align: left;
    font-size: 9pt;
    line-height: 1.4;
}
td {
    padding: 6px 10px;
    border: 1px solid #cfd8dc;
    vertical-align: top;
    color: #222;
    line-height: 1.55;
}
/* 첫 컬럼 (라벨/순번) 짧게 — 자연스러운 폭 분배 */
td:nth-child(1) {
    white-space: nowrap;
    font-weight: 600;
    color: #1a2c4e;
}
/* 단, 첫 컬럼이 긴 텍스트인 경우 wrap 허용 — md 표 셀에 ::text-wrap class 활용은 추후 */
td.wrap, td:nth-child(1).wrap { white-space: normal; }
/* 긴 셀 최대 폭 제어 */
td {
    max-width: 240px;
}
tr:nth-child(even) td { background: #fafafa; }
tr:nth-child(odd) td { background: #ffffff; }
/* 표 caption (학술 보고서 특화) */
caption {
    caption-side: top;
    font-size: 9.5pt;
    font-weight: 600;
    color: #1a2c4e;
    text-align: left;
    padding: 4px 0 6px 0;
    margin-bottom: 0;
}

/* 리스트 — 학술 가독성 */
ul, ol {
    padding-left: 22px;
    margin: 6px 0;
}
li {
    margin: 3px 0;
    line-height: 1.65;
}
ul li::marker { color: #b85c00; font-weight: 700; }
ol li::marker { color: #b85c00; font-weight: 700; }
/* 중첩 리스트 */
li ul, li ol { margin: 2px 0; padding-left: 20px; }

/* 코드 (inline) */
code {
    background: #eceff1;
    padding: 1px 6px;
    border-radius: 3px;
    font-family: 'SF Mono', 'D2Coding', 'Menlo', monospace;
    font-size: 9.5pt;
    color: #c62828;
    word-break: keep-all;
}

/* 코드 (block) */
pre {
    background: #1d1d1f;
    color: #eceff1;
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 10px 0;
    font-size: 9pt;
    line-height: 1.55;
    page-break-inside: avoid;
}
pre code {
    background: none;
    color: inherit;
    padding: 0;
    font-size: 9pt;
    word-break: normal;
}

/* 수평선 — 섹션 구분 (학술 보고서는 hr 유지, brief 와 다름) */
hr {
    border: none;
    border-top: 1px solid #cfd8dc;
    margin: 20px 0;
}

/* 이미지 — 페이지 폭 넘지 않도록 + 중간 분할 방지 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 14px auto;
    page-break-inside: avoid;
    border-radius: 4px;
}

/* 페이지 구분 (수동 제어용) */
.page-break {
    page-break-before: always;
    break-before: page;
}
.page-break + h1,
.page-break + h2,
.page-break + h3,
.page-break + h4,
.page-break + p,
.page-break + table,
.page-break + blockquote { margin-top: 0; }

/* ─── 페이지 break 제어 (학술 보고서 톤) ─── */
/* 제목 + 직후 본문 묶기 (고아 제목 방지) */
h1, h2, h3, h4, h5 { page-break-after: avoid; break-after: avoid; }
h2, h3, h4, h5 { page-break-inside: avoid; break-inside: avoid; }
/* H1 직후 메타 묶기 */
h1 + .meta, h1 + p, h2 + p, h2 + table, h2 + blockquote, h2 + ul, h2 + ol,
h3 + p, h3 + table, h3 + blockquote, h3 + ul, h3 + ol,
h4 + p, h4 + table, h4 + blockquote, h4 + ul, h4 + ol {
    page-break-before: avoid;
    break-before: avoid;
}
/* 블록 보호 */
ul, ol, dl, table, blockquote, pre {
    page-break-inside: avoid;
    break-inside: avoid;
}
p, li, td { orphans: 3; widows: 3; }

/* H2 단위 keep-together 시도 (overflow 시 통째 다음 페이지) */
div.section-keep {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}
div.section-keep > * {
    break-before: avoid !important;
    page-break-before: avoid !important;
}
div.section-keep h2 {
    break-before: auto !important;
    page-break-before: auto !important;
}
"""


# ==============================================================================
# 페이지 footer / header (Chrome CDP 옵션)
# ==============================================================================
FOOTER_TEMPLATE = (
    '<div style="font-size:8.5pt;color:#90a4ae;width:100%;text-align:center;'
    "font-family:'Apple SD Gothic Neo','Pretendard',sans-serif;padding:0 12mm;\">"
    '<span class="pageNumber"></span> / <span class="totalPages"></span>'
    "</div>"
)

HEADER_TEMPLATE = "<span></span>"


# ==============================================================================
# Chrome CDP PDF 생성
# ==============================================================================
def _find_free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _chrome_cdp_pdf(html_path, out_pdf):
    """Chrome CDP 로 PDF 생성 — headless 모드 + 페이지 번호 footer."""
    port = _find_free_port()

    proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-allow-origins=*",
            f"--remote-debugging-port={port}",
            f"file://{html_path}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

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
            except (OSError, json.JSONDecodeError):
                pass
            time.sleep(0.3)

        if not ws_url:
            raise RuntimeError("Chrome CDP 연결 실패")

        ws = websocket.create_connection(ws_url, timeout=15)

        def cdp_send(ws, method, params=None, cmd_id=1):
            msg = {"id": cmd_id, "method": method}
            if params:
                msg["params"] = params
            ws.send(json.dumps(msg))
            while True:
                resp = json.loads(ws.recv())
                if resp.get("id") == cmd_id:
                    return resp

        cdp_send(ws, "Page.enable", cmd_id=1)
        time.sleep(1.0)

        result = cdp_send(
            ws,
            "Page.printToPDF",
            params={
                "displayHeaderFooter": True,
                "headerTemplate": HEADER_TEMPLATE,
                "footerTemplate": FOOTER_TEMPLATE,
                "printBackground": True,
                "paperWidth": 8.27,       # A4
                "paperHeight": 11.69,
                "marginTop": 0.71,        # 18mm
                "marginBottom": 0.71,     # 18mm
                "marginLeft": 0.71,       # 18mm
                "marginRight": 0.71,      # 18mm
            },
            cmd_id=2,
        )

        if "result" not in result or "data" not in result["result"]:
            raise RuntimeError(f"PDF 생성 실패: {result}")

        pdf_data = base64.b64decode(result["result"]["data"])
        with open(out_pdf, "wb") as f:
            f.write(pdf_data)

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# ==============================================================================
# Markdown → HTML 전처리
# ==============================================================================
def _extract_meta_block(md_text: str) -> tuple[str, str]:
    """첫 H1 직후 메타 블록 (`**key**: value` line) 을 추출해서 .meta div 로 변환.

    Returns:
        (body_md, meta_html) — body_md 는 메타 line 이 제거된 md, meta_html 은 div 문자열.
    """
    lines = md_text.split("\n")
    out_lines: list[str] = []
    meta_lines: list[str] = []
    in_meta = False
    title_found = False

    for line in lines:
        stripped = line.strip()
        # 첫 # H1 찾기 → meta 수집 모드 진입
        if not title_found and stripped.startswith("# ") and not stripped.startswith("## "):
            title_found = True
            out_lines.append(line)
            in_meta = True
            continue
        if in_meta:
            # 빈 줄 = meta 영역 계속 (다음 line 까지)
            if stripped == "" and not meta_lines:
                # H1 직후 빈 줄 — 유지하되 meta mode 는 계속
                out_lines.append(line)
                continue
            # **key**: value 패턴 = meta line
            if stripped.startswith("**") and "**:" in stripped:
                meta_lines.append(stripped)
                continue
            # 그 외 빈 줄 = meta 영역 종료
            if stripped == "":
                # meta line 이 1개 이상 수집된 경우 — meta 영역 종료
                if meta_lines:
                    in_meta = False
                    out_lines.append(line)
                    continue
                out_lines.append(line)
                continue
            # 그 외 내용 = meta 영역 종료, 일반 본문 시작
            in_meta = False
        out_lines.append(line)

    # meta_html 빌드
    meta_html = ""
    if meta_lines:
        meta_parts = []
        for m in meta_lines:
            # **key**: value → <strong>key</strong>: value
            converted = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", m)
            meta_parts.append(converted)
        meta_html = '<div class="meta">' + "<br>".join(meta_parts) + "</div>"

    return "\n".join(out_lines), meta_html


def _wrap_section_keep(html: str) -> str:
    """각 H2 ~ 다음 H2 직전까지 <div class="section-keep"> 로 wrap.

    Trading npc_briefing_pdf 와 동일 — H2 section 이 페이지 중간에 잘리지 않고
    overflow 시 통째로 다음 페이지로 push 됨 (CSS break-inside: avoid 가
    div 통째 적용). 학술 보고서에서도 섹션 단위 가독성 향상.
    """
    parts = re.split(r"(<h2(?:\s[^>]*)?>)", html, flags=re.IGNORECASE)
    if len(parts) < 3:
        return html
    result = [parts[0]]
    for i in range(1, len(parts), 2):
        h2_tag = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        result.append(f'<div class="section-keep">{h2_tag}{body}</div>')
    return "".join(result)


def _md_to_html(md_text: str) -> str:
    """Markdown → HTML 변환 (GFM 테이블·코드블록·codehilite·toc 지원) + section keep."""
    html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc", "md_in_html"],
    )
    html = _wrap_section_keep(html)
    return html


# ==============================================================================
# CLI
# ==============================================================================
def convert(md_path):
    md_path = Path(md_path)
    md_text = md_path.read_text(encoding="utf-8")
    if not md_text.strip():
        print(f"✗ 빈 파일: {md_path}", file=sys.stderr)
        sys.exit(1)

    body_md, meta_html = _extract_meta_block(md_text)
    html_body = _md_to_html(body_md)

    # 메타 블록 삽입 (첫 </h1> 직후)
    if meta_html:
        html_body = html_body.replace("</h1>", "</h1>\n" + meta_html, 1)

    title = md_path.stem
    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(full_html)
        html_path = f.name

    out_pdf = md_path.with_suffix(".pdf")

    try:
        _chrome_cdp_pdf(html_path, out_pdf)
        print(f"✓ {out_pdf}")
    except Exception as e:
        print(f"✗ CDP 실패: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        os.unlink(html_path)

    return str(out_pdf)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 _internal/scripts/md2pdf.py <파일.md>")
        sys.exit(1)

    md_file = sys.argv[1]
    if not os.path.exists(md_file):
        print(f"파일 없음: {md_file}")
        sys.exit(1)

    convert(md_file)
