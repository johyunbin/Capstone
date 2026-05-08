"""
Soft Gradient — 트렌디 SaaS / 모던 스타트업.
은은한 보라/인디고 그라데이션 + 글래스 카드 + 둥근 모서리.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, add_oval, SLIDE_W,
)
import content as C
from theme import SOFT, rgb

build_navy.TH = SOFT
TH = SOFT


def s1_cover_soft(prs):
    """라이트 보라 배경 + 큰 글래스 카드 + 부드러운 그라데이션."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_light)

    # 우상단 큰 부드러운 원 (그라데이션 흉내)
    add_oval(s, Inches(9.5), Inches(-3.0), Inches(8), Inches(8),
             color=rgb("#E0E7FF"))    # indigo-100
    # 좌하단 부드러운 원
    add_oval(s, Inches(-2), Inches(5), Inches(6), Inches(6),
             color=rgb("#FAE8FF"))    # fuchsia-100

    # 카테고리 라벨
    add_round_rect(s, Inches(0.8), Inches(0.7), Inches(2.8), Inches(0.4),
                   color=rgb("#EDE9FE"))    # violet-100
    add_text(s, Inches(0.8), Inches(0.78), Inches(2.8), Inches(0.3),
             "CAPSTONE 2026-1  ·  MIDTERM",
             size=10, bold=True, color=TH.primary,
             align=PP_ALIGN.CENTER, font=TH.font_main)

    add_text(s, Inches(11), Inches(0.78), Inches(2), Inches(0.3),
             C.S1_COVER["date"], size=10, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)

    # 메인 타이틀 (큰)
    add_text(s, Inches(0.8), Inches(1.55), Inches(11.5), Inches(2.5),
             C.S1_COVER["title"], size=34, bold=True, color=TH.text,
             font=TH.font_main, line_spacing=1.25)

    # 부제 (라운드 박스)
    add_round_rect(s, Inches(0.8), Inches(4.0), Inches(11.5), Inches(0.6),
                   color=TH.card, border=TH.border, border_width=0.75)
    add_text(s, Inches(1.0), Inches(4.1), Inches(11.3), Inches(0.45),
             C.S1_COVER["subtitle"], size=12, color=TH.text,
             font=TH.font_main, line_spacing=1.3)

    # 글래스 메트릭 카드 4 개 (둥근 모서리, 라이트)
    metrics = [
        ("3", "데이터셋", "DEEP 1M / 8M · SIFT 1.5M"),
        ("5-seed", "신뢰구간", "외적 타당성 통계 보장"),
        ("+19.6%p", "Level 2", "공간 인식 단독 효과"),
        ("8/8", "negative", "skew 지표 |ρ|<0.2"),
    ]
    card_y = Inches(4.95)
    for i, (val, label, sub) in enumerate(metrics):
        x = Inches(0.8 + i * 3.06)
        # 큰 둥근 카드 (글래스 효과 — 흰 배경)
        rr = add_round_rect(s, x, card_y, Inches(2.86), Inches(1.4),
                            TH.card, border=TH.border, border_width=0.75)
        rr.adjustments[0] = 0.18  # 더 둥근 모서리
        add_text(s, x + Inches(0.2), card_y + Inches(0.10), Inches(2.6),
                 Inches(0.55), val, size=22, bold=True, color=TH.primary,
                 font=TH.font_main)
        add_text(s, x + Inches(0.2), card_y + Inches(0.65), Inches(2.6),
                 Inches(0.3), label, size=11, bold=True, color=TH.text,
                 font=TH.font_main)
        add_text(s, x + Inches(0.2), card_y + Inches(0.96), Inches(2.6),
                 Inches(0.4), sub, size=9, color=TH.text_dim,
                 font=TH.font_main)

    # 하단 메타 (단순한 둥근 박스)
    add_rect(s, Inches(0.8), Inches(6.6), Inches(11.5), Pt(1), TH.border)
    add_text(s, Inches(0.8), Inches(6.7), Inches(8), Inches(0.3),
             C.S1_COVER["team"], size=14, bold=True, color=TH.primary,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(7.05), Inches(8), Inches(0.3),
             "  ·  ".join(C.S1_COVER["members"]),
             size=10, color=TH.text_dim, font=TH.font_main)
    add_text(s, Inches(8), Inches(6.7), Inches(4.7), Inches(0.3),
             C.S1_COVER["advisor"], size=10, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)


build_navy.s1_cover = s1_cover_soft


def content_header_soft(slide, title, subtitle=None):
    """Soft — 라이트 보라 배경 + 둥근 모서리 강조."""
    set_bg(slide, TH.bg_light)
    # 우상단 부드러운 원
    add_oval(slide, Inches(11), Inches(-1.5), Inches(4), Inches(4),
             color=rgb("#EDE9FE"))
    # 작은 컬러 점
    add_oval(slide, Inches(0.8), Inches(0.55), Inches(0.18), Inches(0.18),
             TH.primary)
    add_text(slide, Inches(1.1), Inches(0.45), Inches(11.5), Inches(0.6),
             title, size=24, bold=True, color=TH.text, font=TH.font_main)
    if subtitle:
        add_text(slide, Inches(1.1), Inches(1.05), Inches(12), Inches(0.35),
                 subtitle, size=11, color=TH.text_dim, font=TH.font_main)
    # 둥근 분리선 대신 옅은 보라 라인
    add_rect(slide, Inches(0.6), Inches(1.5), Inches(12.1), Pt(1),
             TH.border)


build_navy.content_header = content_header_soft


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_soft.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
