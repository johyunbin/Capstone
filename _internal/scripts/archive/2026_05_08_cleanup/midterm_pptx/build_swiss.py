"""
Swiss Minimal — 매거진 / 저널 스타일.
EDITORIAL 베이스 + 비대칭 여백 + 강한 빨강 포인트 + 큰 타이포.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, SLIDE_W,
)
import content as C
from theme import SWISS

build_navy.TH = SWISS
TH = SWISS


def s1_cover_swiss(prs):
    """매거진 표지 — 비대칭 여백 + 분할 타이포 (수식어 + 메인) + 빨강 hairline."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_light)

    # 상단 빨강 hairline
    add_rect(s, Inches(0.8), Inches(0.7), Inches(0.6), Pt(3), TH.accent)
    add_text(s, Inches(0.8), Inches(0.9), Inches(8), Inches(0.4),
             "ISSUE 02  /  CAPSTONE 2026-1  /  MIDTERM",
             size=10, bold=True, color=TH.accent, font=TH.font_main)
    add_text(s, Inches(11), Inches(0.9), Inches(2), Inches(0.4),
             "2026.04",
             size=10, color=TH.text_dim, align=PP_ALIGN.RIGHT,
             font=TH.font_main)

    # 수식어 (작게)
    add_text(s, Inches(0.8), Inches(1.9), Inches(12), Inches(0.5),
             "Exqutor 벡터 카디널리티 추정의",
             size=24, color=TH.text_dim,
             font=TH.font_main)

    # 메인 타이틀 (대형) — 한 줄 안에 들어가는 길이
    add_text(s, Inches(0.8), Inches(2.6), Inches(12), Inches(1.5),
             "단일 테이블 사각지대와",
             size=44, bold=True, color=TH.text,
             font=TH.font_main, line_spacing=1.15)
    add_text(s, Inches(0.8), Inches(3.85), Inches(12), Inches(1.2),
             "Skew-Aware Sampling",
             size=44, bold=True, color=TH.accent,
             font=TH.font_main, line_spacing=1.15)

    # 빨강 포인트 박스 (작은 부호)
    add_rect(s, Inches(0.8), Inches(5.45), Inches(0.5), Inches(0.06),
             TH.accent)
    add_text(s, Inches(0.8), Inches(5.55), Inches(12), Inches(0.5),
             C.S1_COVER["subtitle"], size=12, color=TH.text,
             font=TH.font_main, line_spacing=1.4)

    # 굵은 분리선
    add_rect(s, Inches(0.8), Inches(6.3), Inches(11.5), Pt(2), TH.text)

    # 하단: 좌 (큰 팀명) + 우 (날짜 큰 숫자)
    add_text(s, Inches(0.8), Inches(6.5), Inches(7), Inches(0.5),
             C.S1_COVER["team"], size=24, bold=True, color=TH.accent,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(7.05), Inches(8), Inches(0.3),
             "  /  ".join(C.S1_COVER["members"]),
             size=10, color=TH.text, font=TH.font_main)

    add_text(s, Inches(8), Inches(6.5), Inches(4.7), Inches(0.5),
             "04 . 28",
             size=24, bold=True, color=TH.text,
             align=PP_ALIGN.RIGHT, font=TH.font_main)
    add_text(s, Inches(8), Inches(7.05), Inches(4.7), Inches(0.3),
             C.S1_COVER["advisor"], size=10, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)


build_navy.s1_cover = s1_cover_swiss


def content_header_swiss(slide, title, subtitle=None):
    """Swiss 톤 — 좌측 라인 + 큰 좌측 정렬 타이틀 + spacing 보강."""
    set_bg(slide, TH.bg_light)
    # 굵은 검정 좌측 라인
    add_rect(slide, Inches(0.6), Inches(0.5), Inches(0.08), Inches(0.95),
             TH.text)
    add_text(slide, Inches(0.85), Inches(0.45), Inches(11.5), Inches(0.55),
             title, size=24, bold=True, color=TH.text, font=TH.font_main)
    if subtitle:
        # 빨강 작은 표시 + spacing
        add_rect(slide, Inches(0.85), Inches(1.10), Inches(0.3), Pt(2),
                 TH.accent)
        add_text(slide, Inches(0.85), Inches(1.20), Inches(12), Inches(0.32),
                 subtitle, size=10, color=TH.text_dim, font=TH.font_main)
    add_rect(slide, Inches(0.6), Inches(1.65), Inches(12.1), Pt(1.0),
             TH.text)


build_navy.content_header = content_header_swiss


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_swiss.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
