"""
Academic Light — Apple 스타일 화이트 + 블루.
NAVY 베이스 + 흰 본문 + 선명한 블루 액센트.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, add_oval, SLIDE_W,
)
import content as C
from theme import ACADEMIC

build_navy.TH = ACADEMIC
TH = ACADEMIC


def s1_cover_academic(prs):
    """Apple 클린 — 흰 배경 + 정교한 타이포 + 작은 블루 액센트 라인."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_light)

    # 좌상단 작은 컬러 점 + 라벨
    add_oval(s, Inches(0.8), Inches(0.85), Inches(0.18), Inches(0.18),
             TH.primary)
    add_text(s, Inches(1.1), Inches(0.78), Inches(8), Inches(0.35),
             "CAPSTONE 2026-1  ·  MIDTERM PRESENTATION",
             size=11, bold=True, color=TH.text, font=TH.font_main)
    add_text(s, Inches(11), Inches(0.78), Inches(2), Inches(0.35),
             C.S1_COVER["date"], size=11, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)

    # 메인 타이틀 (대형, 좌측 정렬, 흰 배경)
    add_text(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(2.5),
             C.S1_COVER["title"], size=36, bold=True, color=TH.text,
             font=TH.font_main, line_spacing=1.25)

    # 좌측 컬러 라인 + 부제
    add_rect(s, Inches(0.8), Inches(4.6), Inches(0.06), Inches(0.55),
             TH.primary)
    add_text(s, Inches(1.0), Inches(4.6), Inches(11.5), Inches(0.55),
             C.S1_COVER["subtitle"], size=14, color=TH.text_dim,
             font=TH.font_main, line_spacing=1.4)

    # 분리선
    add_rect(s, Inches(0.8), Inches(5.9), Inches(11.5), Pt(1), TH.border)

    # 하단: 좌(팀+멤버) / 우(메타)
    add_text(s, Inches(0.8), Inches(6.1), Inches(8), Inches(0.4),
             C.S1_COVER["team"], size=22, bold=True, color=TH.primary,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(6.6), Inches(10), Inches(0.3),
             "  ·  ".join(C.S1_COVER["members"]),
             size=11, color=TH.text, font=TH.font_main)
    add_text(s, Inches(0.8), Inches(6.95), Inches(10), Inches(0.3),
             C.S1_COVER["course"], size=10, color=TH.text_dim,
             font=TH.font_main)
    add_text(s, Inches(8.5), Inches(6.95), Inches(4.3), Inches(0.3),
             C.S1_COVER["advisor"], size=10, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)


build_navy.s1_cover = s1_cover_academic


# Academic content_header — 큰 타이틀 + 얇은 분리선
def content_header_academic(slide, title, subtitle=None):
    set_bg(slide, TH.bg_light)
    # 좌측 큰 컬러 사각형 (작은 4×0.6)
    add_rect(slide, Inches(0.8), Inches(0.55), Inches(0.06), Inches(0.85),
             TH.primary)
    add_text(slide, Inches(1.0), Inches(0.45), Inches(11.5), Inches(0.6),
             title, size=24, bold=True, color=TH.text, font=TH.font_main)
    if subtitle:
        add_text(slide, Inches(1.0), Inches(1.05), Inches(12), Inches(0.35),
                 subtitle, size=11, color=TH.text_dim, font=TH.font_main)
    add_rect(slide, Inches(0.6), Inches(1.45), Inches(12.1), Pt(1),
             TH.border)


build_navy.content_header = content_header_academic


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_academic.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
