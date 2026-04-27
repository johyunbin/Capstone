"""
Version D — Bold Cards — sky-tone 강한 색 카드 + 큰 대비.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, add_oval, SLIDE_W,
)
import content as C
from theme import BOLD

build_navy.TH = BOLD
TH = BOLD


def s1_cover_bold(prs):
    """단일 컬럼 — 큰 컬러 패널 상단 + 본문 하단 (잡지 인상 제거)."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_light)

    # 상단 큰 컬러 영역 (40% 높이)
    add_rect(s, Inches(0), Inches(0), Inches(13.333), Inches(3.0), TH.primary)
    # 우상단 accent 라인
    add_rect(s, Inches(0.8), Inches(0.55), Inches(2.5), Pt(3), TH.accent)
    add_text(s, Inches(0.8), Inches(0.7), Inches(8), Inches(0.35),
             "CAPSTONE 2026-1  ·  MIDTERM PRESENTATION  ·  연세대학교",
             size=11, bold=True, color=TH.accent, font=TH.font_main)
    # 우상단 날짜
    add_text(s, Inches(11), Inches(0.7), Inches(2), Inches(0.35),
             C.S1_COVER["date"], size=11, color=TH.accent,
             align=PP_ALIGN.RIGHT, font=TH.font_main)

    # 메인 타이틀 (큰 사이즈)
    add_text(s, Inches(0.8), Inches(1.3), Inches(11.5), Inches(1.5),
             C.S1_COVER["title"], size=28, bold=True, color=TH.text_white,
             font=TH.font_main, line_spacing=1.25)

    # 부제 (상단 영역 하단)
    add_text(s, Inches(0.8), Inches(2.55), Inches(11.5), Inches(0.4),
             C.S1_COVER["subtitle"], size=13, color=TH.accent,
             font=TH.font_main)

    # 하단 본문 (60% 높이)
    # 팀 + 멤버
    add_rect(s, Inches(0.8), Inches(3.6), Inches(2.0), Pt(3), TH.primary)
    add_text(s, Inches(0.8), Inches(3.75), Inches(8), Inches(0.5),
             C.S1_COVER["team"], size=24, bold=True, color=TH.text,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(4.35), Inches(8), Inches(0.35),
             "  ·  ".join(C.S1_COVER["members"]),
             size=12, color=TH.text_dim, font=TH.font_main)

    # 메타 (4 줄)
    meta = [
        ("COURSE", C.S1_COVER["course"]),
        ("ADVISOR", C.S1_COVER["advisor"]),
        ("TOPIC", "Exqutor 기반 벡터 증강 분석 쿼리 (VAQ) 의 카디널리티 추정"),
        ("METHOD", "Skew-Aware Sampling — Pivot A (BERNOULLI) + Pivot C (KM20)"),
    ]
    for i, (label, val) in enumerate(meta):
        y = Inches(5.1 + i * 0.55)
        add_text(s, Inches(0.8), y, Inches(1.5), Inches(0.3),
                 label, size=10, bold=True, color=TH.primary, font=TH.font_main)
        add_text(s, Inches(2.4), y + Inches(0.02), Inches(10.5), Inches(0.32),
                 val, size=11, color=TH.text, font=TH.font_main)


build_navy.s1_cover = s1_cover_bold


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_bold.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
