"""
Version B — Modern Glass — 그라디언트 + 글래스 카드.
build_navy 의 본문 함수 재사용 + 표지 override.
"""
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_rect, add_round_rect, SLIDE_W,
)
import content as C
from theme import GLASS

build_navy.TH = GLASS  # 모든 함수가 글로벌 TH 를 참조 → 한 줄로 테마 변경
TH = GLASS


def s1_cover_glass(prs):
    """그라디언트 배경 + 글래스 카드 + 핵심 메트릭 4 개 강조."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_dark)

    # 그라디언트 효과를 흉내 — 진한 → 옅은 사각형 3 단
    add_rect(s, Inches(0), Inches(0), SLIDE_W, Inches(2.5), TH.primary)
    add_rect(s, Inches(0), Inches(2.5), SLIDE_W, Inches(2.5),
             build_navy.TH.bg_dark)
    # 우상단 큰 원 (디자인 강조)
    s.shapes.add_shape(1, Inches(10), Inches(-1.5), Inches(5),
                       Inches(5)).fill.background()

    # 좌상단 카테고리 라벨
    add_text(s, Inches(0.8), Inches(0.7), Inches(8), Inches(0.4),
             "CAPSTONE 2026-1  ·  MIDTERM  ·  연세대학교",
             size=11, bold=True, color=TH.accent, font=TH.font_main)

    # 메인 타이틀 (큰)
    add_text(s, Inches(0.8), Inches(1.3), Inches(11.5), Inches(2.2),
             C.S1_COVER["title"], size=34, bold=True, color=TH.text_white,
             font=TH.font_main, line_spacing=1.3)

    # 부제
    add_text(s, Inches(0.8), Inches(3.4), Inches(11.5), Inches(0.6),
             C.S1_COVER["subtitle"], size=14, color=TH.accent,
             font=TH.font_main, line_spacing=1.4)

    # Glass 카드: 핵심 메트릭 4 개
    metrics = [
        ("3", "데이터셋", "DEEP 1M / 8M, SIFT 1.5M"),
        ("5-seed", "신뢰구간", "외적 타당성 확보"),
        ("+19.6%p", "Level 2", "공간 인식 단독 효과"),
        ("8/8", "negative", "skew 지표 전수"),
    ]
    card_y = Inches(4.7)
    for i, (val, label, sub) in enumerate(metrics):
        x = Inches(0.8 + i * 3.05)
        # 글래스 카드
        add_round_rect(s, x, card_y, Inches(2.85), Inches(1.5),
                       TH.primary, border=TH.accent, border_width=1.0)
        add_text(s, x + Inches(0.2), card_y + Inches(0.10), Inches(2.6),
                 Inches(0.6), val, size=22, bold=True, color=TH.accent,
                 font=TH.font_main)
        add_text(s, x + Inches(0.2), card_y + Inches(0.7), Inches(2.6),
                 Inches(0.3), label, size=11, bold=True, color=TH.text_white,
                 font=TH.font_main)
        add_text(s, x + Inches(0.2), card_y + Inches(1.05), Inches(2.6),
                 Inches(0.4), sub, size=9, color=TH.text_dim,
                 font=TH.font_main)

    # 하단 메타
    add_text(s, Inches(0.8), Inches(6.5), Inches(8), Inches(0.3),
             f"{C.S1_COVER['team']}  ·  {' / '.join(C.S1_COVER['members'])}",
             size=11, bold=True, color=TH.text_white, font=TH.font_main)
    add_text(s, Inches(0.8), Inches(6.8), Inches(8), Inches(0.3),
             f"{C.S1_COVER['advisor']}  ·  {C.S1_COVER['date']}",
             size=10, color=TH.text_dim, font=TH.font_main)


# build_navy 의 표지 함수 교체
build_navy.s1_cover = s1_cover_glass


def s15_thanks_glass(prs):
    s = blank_slide(prs)
    set_bg(s, TH.bg_dark)
    add_rect(s, Inches(0), Inches(0), SLIDE_W, Inches(2.0), TH.primary)
    add_rect(s, Inches(5.0), Inches(2.4), Inches(3.3), Inches(3),
             color=None)
    add_text(s, Inches(0), Inches(2.85), SLIDE_W, Inches(1.2),
             C.S15_THANKS["title"], size=58, bold=True, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, Inches(0), Inches(4.1), SLIDE_W, Inches(0.6),
             C.S15_THANKS["subtitle"], size=18, color=TH.accent,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, Inches(0), Inches(5.5), SLIDE_W, Inches(0.4),
             C.S15_THANKS["team"], size=15, bold=True, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, Inches(0), Inches(5.95), SLIDE_W, Inches(0.4),
             " · ".join(C.S15_THANKS["members"]),
             size=11, color=TH.text_dim,
             align=PP_ALIGN.CENTER, font=TH.font_main)


build_navy.s15_thanks = s15_thanks_glass


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_glass.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
