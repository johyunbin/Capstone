"""
Version C — Editorial Mono — 흑백 + 빨강 1 강조.
잡지/저널 스타일, 큰 타이포, 절제된 디자인.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, SLIDE_W,
)
import content as C
from theme import EDITORIAL

build_navy.TH = EDITORIAL
TH = EDITORIAL


def s1_cover_editorial(prs):
    """잡지 표지 — 큰 타이포 + 빨강 헤어라인 + 미니멀 메타."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_light)

    # 상단 빨강 hairline
    add_rect(s, Inches(0.8), Inches(0.6), Inches(2.2), Pt(2), TH.accent)
    add_text(s, Inches(0.8), Inches(0.75), Inches(8), Inches(0.4),
             "CAPSTONE 2026-1  /  MIDTERM PRESENTATION  /  연세대학교",
             size=10, bold=True, color=TH.accent, font=TH.font_main)

    # Issue number 같은 라벨
    add_text(s, Inches(11.2), Inches(0.75), Inches(1.5), Inches(0.4),
             "VOL. 02 — 2026.04",
             size=10, color=TH.text_dim, align=PP_ALIGN.RIGHT,
             font=TH.font_main)

    # 메인 타이틀 (매우 큰)
    add_text(s, Inches(0.8), Inches(2.0), Inches(11.5), Inches(2.5),
             C.S1_COVER["title"], size=44, bold=True, color=TH.text,
             font=TH.font_main, line_spacing=1.2)

    # 부제 (작게, 빨강 라인 위)
    add_rect(s, Inches(0.8), Inches(4.7), Inches(0.8), Pt(2), TH.accent)
    add_text(s, Inches(0.8), Inches(4.85), Inches(11.5), Inches(0.5),
             C.S1_COVER["subtitle"], size=14, color=TH.text,
             font=TH.font_main, line_spacing=1.4)

    # 하단: 좌(팀+멤버) / 우(날짜)
    add_rect(s, Inches(0.8), Inches(6.0), Inches(11.5), Pt(1), TH.text)

    add_text(s, Inches(0.8), Inches(6.2), Inches(8), Inches(0.4),
             C.S1_COVER["team"], size=22, bold=True, color=TH.accent,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(6.65), Inches(10), Inches(0.3),
             "  ·  ".join(C.S1_COVER["members"]),
             size=10, color=TH.text, font=TH.font_main)

    add_text(s, Inches(8.5), Inches(6.2), Inches(4.3), Inches(0.4),
             C.S1_COVER["date"], size=20, bold=True, color=TH.text,
             align=PP_ALIGN.RIGHT, font=TH.font_main)
    add_text(s, Inches(8.5), Inches(6.65), Inches(4.3), Inches(0.3),
             C.S1_COVER["advisor"], size=10, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)


build_navy.s1_cover = s1_cover_editorial


# Editorial 톤의 content_header — 검정 좌측 라인 + 큰 타이틀
def content_header_editorial(slide, title, subtitle=None):
    set_bg(slide, TH.bg_light)
    # 좌측 빨강 라인
    add_rect(slide, Inches(0.6), Inches(0.5), Inches(0.06), Inches(0.9),
             TH.accent)
    add_text(slide, Inches(0.85), Inches(0.5), Inches(11.5), Inches(0.55),
             title, size=22, bold=True, color=TH.text, font=TH.font_main)
    if subtitle:
        add_text(slide, Inches(0.85), Inches(1.05), Inches(12), Inches(0.35),
                 subtitle, size=10, color=TH.text_dim, font=TH.font_main)
    add_rect(slide, Inches(0.6), Inches(1.45), Inches(12.1), Pt(1), TH.text)


build_navy.content_header = content_header_editorial


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_editorial.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
