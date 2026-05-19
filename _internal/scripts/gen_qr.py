#!/usr/bin/env python3
"""gen_qr.py — YouTube(또는 임의) URL → QR 코드 SVG/PNG.

사용법: python3 gen_qr.py <URL> <output.svg|png> [scale]
- 소개 동영상을 YouTube에 업로드한 뒤, 그 URL로 실행해 포스터용 QR을 만든다.
- SVG 출력은 무한 확대 가능(900×1200mm 포스터 인쇄에 적합).
- error-correction H — 모듈 30% 손상까지 복원, 인쇄·전시 환경에 안전.
- 모듈색은 deck navy(#1E3A5F) — 흰 배경 대비 약 11:1로 스캔 안정.

포스터 삽입(영상 업로드 후):
  1) python3 _internal/scripts/gen_qr.py "<youtube_url>" _internal/포스터영상_build/poster/qr.svg
  2) poster/poster.html 의 QR placeholder 블록을 <img src="qr.svg"> 로 교체
  3) python3 _internal/scripts/render_poster.py poster/poster.html 속도는벡터_포스터.pdf
"""

import sys

import segno


def gen(url, out, scale=12):
    qr = segno.make(url, error="h")
    kind = "svg" if out.lower().endswith(".svg") else "png"
    qr.save(
        out, kind=kind, scale=scale, border=4,
        dark="#1E3A5F", light="#FFFFFF",
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python3 gen_qr.py <URL> <output.svg|png> [scale]")
        sys.exit(1)
    url, out = sys.argv[1], sys.argv[2]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    gen(url, out, scale)
    print(f"✓ {out}  ←  {url}")
