#!/usr/bin/env python3
"""render_poster.py — HTML → 대형 PDF (Chrome CDP printToPDF).

사용법: python3 render_poster.py <input.html> <output.pdf> [width_mm] [height_mm]
기본 900×1200mm (캡스톤 전시회 포스터 규격).
md2pdf.py 의 _chrome_cdp_pdf 패턴 차용 — margin 0, printBackground, header/footer 없음.
"""

import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

import websocket

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MM_PER_IN = 25.4


def _free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def render(html_path, out_pdf, width_mm=900.0, height_mm=1200.0):
    html_path = os.path.abspath(html_path)
    out_pdf = os.path.abspath(out_pdf)
    port = _free_port()
    proc = subprocess.Popen(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-first-run", "--no-default-browser-check",
            "--allow-file-access-from-files",
            "--remote-allow-origins=*", f"--remote-debugging-port={port}",
            f"file://{html_path}",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        ws_url = None
        for _ in range(30):
            try:
                resp = urllib.request.urlopen(f"http://localhost:{port}/json")
                for t in json.loads(resp.read()):
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

        ws = websocket.create_connection(ws_url, timeout=30)

        def send(method, params=None, cid=1):
            msg = {"id": cid, "method": method}
            if params:
                msg["params"] = params
            ws.send(json.dumps(msg))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == cid:
                    return r

        send("Page.enable", cid=1)
        time.sleep(1.8)  # 폰트·레이아웃 안정

        result = send(
            "Page.printToPDF",
            params={
                "displayHeaderFooter": False,
                "printBackground": True,
                "preferCSSPageSize": False,
                "paperWidth": width_mm / MM_PER_IN,
                "paperHeight": height_mm / MM_PER_IN,
                "marginTop": 0, "marginBottom": 0,
                "marginLeft": 0, "marginRight": 0,
            },
            cid=2,
        )
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


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python3 render_poster.py <input.html> <output.pdf> [width_mm] [height_mm]")
        sys.exit(1)
    w = float(sys.argv[3]) if len(sys.argv) > 3 else 900.0
    h = float(sys.argv[4]) if len(sys.argv) > 4 else 1200.0
    render(sys.argv[1], sys.argv[2], w, h)
    print(f"✓ {sys.argv[2]}  ({w:.0f}×{h:.0f}mm)")
