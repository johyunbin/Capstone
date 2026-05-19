"""
Version E — Hub-Spoke Spatial — 5축 다이어그램형 표지.
S6 차별성 슬라이드에 hub-spoke 다이어그램 적용.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, add_oval,
    add_line, SLIDE_W, SLIDE_H,
)
import content as C
from theme import HUB

build_navy.TH = HUB
TH = HUB


def s1_cover_hub(prs):
    """중앙 hub + 4 개 spoke 카드 (RQ1, RQ2, RQ3, External Validity)."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_dark)

    # 상단 카테고리
    add_text(s, Inches(0.8), Inches(0.5), Inches(8), Inches(0.4),
             "CAPSTONE 2026-1  ·  MIDTERM PRESENTATION",
             size=11, bold=True, color=TH.accent, font=TH.font_main)
    # 우측 날짜
    add_text(s, Inches(11), Inches(0.5), Inches(2), Inches(0.4),
             C.S1_COVER["date"], size=11, color=TH.accent,
             align=PP_ALIGN.RIGHT, font=TH.font_main)

    # 메인 타이틀 (좌측)
    add_text(s, Inches(0.8), Inches(1.3), Inches(7), Inches(2.5),
             C.S1_COVER["title"], size=22, bold=True, color=TH.text_white,
             font=TH.font_main, line_spacing=1.3)
    add_text(s, Inches(0.8), Inches(3.7), Inches(7), Inches(0.5),
             C.S1_COVER["subtitle"], size=12, color=TH.accent,
             font=TH.font_main)

    # 우측 hub-spoke 다이어그램
    cx, cy = Inches(10.3), Inches(3.5)
    # 중앙 허브
    add_oval(s, cx - Inches(1.0), cy - Inches(0.55), Inches(2.0),
             Inches(1.1), TH.accent)
    add_text(s, cx - Inches(1.0), cy - Inches(0.4), Inches(2.0), Inches(0.45),
             "Skew-Aware", size=12, bold=True, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, cx - Inches(1.0), cy - Inches(0.0), Inches(2.0), Inches(0.4),
             "Sampling", size=11, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)

    # 4 spoke
    spoke_data = [
        ("RQ1", "8 지표 negative", -2.0, -1.5),
        ("RQ2", "+1.64% (CI)", 2.0, -1.5),
        ("RQ3", "Recovery Rate", -2.0, 1.5),
        ("Validity", "3 데이터셋", 2.0, 1.5),
    ]
    for label, val, dx, dy in spoke_data:
        sx = cx + Inches(dx) - Inches(0.7)
        sy = cy + Inches(dy) - Inches(0.4)
        # 연결선
        add_line(s, cx, cy, sx + Inches(0.7), sy + Inches(0.4),
                 TH.text_dim, width=1.0)
        # spoke 카드
        add_round_rect(s, sx, sy, Inches(1.4), Inches(0.8),
                       TH.card, border=TH.accent, border_width=1.0)
        add_text(s, sx, sy + Inches(0.05), Inches(1.4), Inches(0.35),
                 label, size=11, bold=True, color=TH.primary,
                 align=PP_ALIGN.CENTER, font=TH.font_main)
        add_text(s, sx, sy + Inches(0.4), Inches(1.4), Inches(0.35),
                 val, size=8, color=TH.text_dim,
                 align=PP_ALIGN.CENTER, font=TH.font_main)

    # 하단 분리선 + 팀 정보
    add_rect(s, Inches(0.8), Inches(6.2), Inches(11.5), Pt(1), TH.text_dim)
    add_text(s, Inches(0.8), Inches(6.4), Inches(8), Inches(0.4),
             C.S1_COVER["team"], size=18, bold=True, color=TH.text_white,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(6.85), Inches(8), Inches(0.3),
             "  ·  ".join(C.S1_COVER["members"]) +
             f"  ·  {C.S1_COVER['advisor']}",
             size=10, color=TH.text_dim, font=TH.font_main)


build_navy.s1_cover = s1_cover_hub


# S6 차별성 슬라이드를 hub-spoke 형태로 override
def s6_differentiator_hub(prs):
    s = blank_slide(prs)
    build_navy.content_header(s, C.S6_DIFFERENTIATOR["title"],
                              C.S6_DIFFERENTIATOR["subtitle"])
    build_navy.slide_number(s, 6, build_navy.TOTAL, TH.text_dim)

    # 중앙 hub: 본 연구
    cx, cy = Inches(6.665), Inches(3.85)
    add_oval(s, cx - Inches(1.3), cy - Inches(0.65), Inches(2.6),
             Inches(1.3), TH.primary)
    add_text(s, cx - Inches(1.3), cy - Inches(0.45), Inches(2.6), Inches(0.5),
             "본 연구", size=13, bold=True, color=TH.accent,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, cx - Inches(1.3), cy - Inches(0.05), Inches(2.6), Inches(0.5),
             "Skew-Aware Sampling", size=14, bold=True, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, cx - Inches(1.3), cy + Inches(0.35), Inches(2.6), Inches(0.4),
             "Pivot A + Pivot C 직교 결합", size=10, color=TH.accent,
             align=PP_ALIGN.CENTER, font=TH.font_main)

    # 좌측 spoke: Pivot A
    lane = C.S6_DIFFERENTIATOR["lanes"][0]
    sx, sy = Inches(0.8), Inches(2.4)
    add_round_rect(s, sx, sy, Inches(3.5), Inches(2.9),
                   TH.card, border=TH.border)
    add_rect(s, sx, sy, Inches(3.5), Inches(0.4), TH.primary)
    add_text(s, sx + Inches(0.2), sy + Inches(0.05), Inches(3.1), Inches(0.3),
             lane["name"] + " — " + lane["title"], size=12, bold=True,
             color=TH.text_white, font=TH.font_main)
    add_text(s, sx + Inches(0.2), sy + Inches(0.55), Inches(3.1), Inches(1.0),
             lane["detail"], size=10, color=TH.text, font=TH.font_main,
             line_spacing=1.4)
    add_text(s, sx + Inches(0.2), sy + Inches(1.7), Inches(3.1), Inches(0.5),
             lane["metric"], size=22, bold=True, color=TH.primary,
             font=TH.font_main)
    add_text(s, sx + Inches(0.2), sy + Inches(2.3), Inches(3.1), Inches(0.4),
             lane["metric_label"], size=9, color=TH.text_dim, font=TH.font_main)

    # 우측 spoke: Pivot C
    lane = C.S6_DIFFERENTIATOR["lanes"][1]
    sx = Inches(9.05)
    add_round_rect(s, sx, sy, Inches(3.5), Inches(2.9),
                   TH.card, border=TH.border)
    add_rect(s, sx, sy, Inches(3.5), Inches(0.4), TH.accent)
    add_text(s, sx + Inches(0.2), sy + Inches(0.05), Inches(3.1), Inches(0.3),
             lane["name"] + " — " + lane["title"], size=12, bold=True,
             color=TH.text_white, font=TH.font_main)
    add_text(s, sx + Inches(0.2), sy + Inches(0.55), Inches(3.1), Inches(1.0),
             lane["detail"], size=10, color=TH.text, font=TH.font_main,
             line_spacing=1.4)
    add_text(s, sx + Inches(0.2), sy + Inches(1.7), Inches(3.1), Inches(0.5),
             lane["metric"], size=22, bold=True, color=TH.primary,
             font=TH.font_main)
    add_text(s, sx + Inches(0.2), sy + Inches(2.3), Inches(3.1), Inches(0.4),
             lane["metric_label"], size=9, color=TH.text_dim, font=TH.font_main)

    # 연결선 두 spoke → hub
    add_line(s, Inches(4.3), Inches(3.85), cx - Inches(1.3), Inches(3.85),
             TH.accent, width=1.5)
    add_line(s, cx + Inches(1.3), Inches(3.85), Inches(9.05), Inches(3.85),
             TH.accent, width=1.5)

    # 하단 핵심 기여
    add_text(s, Inches(0.6), Inches(5.55), Inches(12.1), Inches(0.35),
             "본 연구의 핵심 기여", size=11, bold=True, color=TH.primary,
             font=TH.font_main)
    contribs = C.S6_DIFFERENTIATOR["contribution"]
    for i, c in enumerate(contribs):
        y = Inches(5.9 + i * 0.32)
        add_oval(s, Inches(0.7), y + Inches(0.07), Inches(0.12), Inches(0.12),
                 TH.accent)
        add_text(s, Inches(0.95), y, Inches(11.8), Inches(0.32),
                 c, size=10, color=TH.text, font=TH.font_main, line_spacing=1.3)


build_navy.s6_differentiator = s6_differentiator_hub


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_hub.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
