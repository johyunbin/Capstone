#!/usr/bin/env python3
"""render_slides.py — 슬라이드 HTML → PNG (Chrome headless screenshot).

사용법: python3 render_slides.py <input_dir> <output_dir> [width] [height] [scale]
input_dir 의 *.html 을 이름순으로 각각 <같은이름>.png 로 렌더.
기본 1920×1080 @2x → 3840×2160 PNG (YouTube 16:9).
"""

import glob
import os
import subprocess
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def render_one(html_path, png_path, w=1920, h=1080, scale=2):
    html_path = os.path.abspath(html_path)
    png_path = os.path.abspath(png_path)
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
            "--allow-file-access-from-files",
            f"--force-device-scale-factor={scale}",
            f"--window-size={w},{h}",
            f"--screenshot={png_path}",
            f"file://{html_path}",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python3 render_slides.py <input_dir> <output_dir> [w] [h] [scale]")
        sys.exit(1)
    in_dir, out_dir = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1080
    scale = int(sys.argv[5]) if len(sys.argv) > 5 else 2
    os.makedirs(out_dir, exist_ok=True)
    htmls = sorted(glob.glob(os.path.join(in_dir, "*.html")))
    if not htmls:
        print(f"✗ {in_dir} 에 .html 없음")
        sys.exit(1)
    for hp in htmls:
        name = os.path.splitext(os.path.basename(hp))[0]
        pp = os.path.join(out_dir, name + ".png")
        render_one(hp, pp, w, h, scale)
        print(f"✓ {pp}")
    print(f"— 총 {len(htmls)}장 ({w}×{h} @{scale}x)")
