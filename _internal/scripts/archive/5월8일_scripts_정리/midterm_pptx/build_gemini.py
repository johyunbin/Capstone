"""
Premium Glassmorphism — _gemini.pptx
하이엔드 다크 모드 + 큰 타이포 + 글래스 카드 + 핵심 슬라이드 배경 차별화.
"""
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import build_navy
from common import (
    blank_slide, set_bg, add_text, add_paragraph, add_rect, add_round_rect,
    add_oval, add_figure, slide_number, SLIDE_W, SLIDE_H,
)
import content as C
from theme import PREMIUM, rgb

build_navy.TH = PREMIUM
TH = PREMIUM
TOTAL = build_navy.TOTAL

# 핵심 강조 슬라이드용 더 짙은 배경
DEEP_BG = rgb("#0F1729")    # slate-950 변형
HIGHLIGHT_BG = rgb("#1E293B")  # slate-800


def content_header_premium(slide, title, subtitle=None):
    """28pt 큰 타이틀 + 큰 간격 + 다크 배경."""
    set_bg(slide, TH.bg_light)
    # 상단 그라디언트 strip — 사각형 4 단으로 흉내
    add_rect(slide, Inches(0), Inches(0), Inches(3.3), Pt(4), TH.primary)
    add_rect(slide, Inches(3.3), Inches(0), Inches(3.3), Pt(4),
             rgb("#5B7FE0"))
    add_rect(slide, Inches(6.6), Inches(0), Inches(3.3), Pt(4), TH.accent)
    add_rect(slide, Inches(9.9), Inches(0), Inches(3.43), Pt(4),
             rgb("#8B5CF6"))

    # 큰 타이틀 (28pt)
    add_text(slide, Inches(0.7), Inches(0.35), Inches(11.7), Inches(0.8),
             title, size=28, bold=True, color=TH.text_white,
             font=TH.font_main)
    if subtitle:
        add_text(slide, Inches(0.7), Inches(1.1), Inches(12), Inches(0.4),
                 subtitle, size=12, color=TH.text_dim, font=TH.font_main)
    # 분리선
    add_rect(slide, Inches(0.7), Inches(1.55), Inches(12.1), Pt(1),
             TH.border)


build_navy.content_header = content_header_premium


def s1_cover_gemini(prs):
    """그라디언트 흉내 표지 + 글래스 메트릭 카드."""
    s = blank_slide(prs)
    set_bg(s, TH.bg_dark)

    # 그라디언트 효과 — 다단계 사각형
    add_rect(s, Inches(0), Inches(0), SLIDE_W, Inches(3.5),
             rgb("#0F1729"))
    add_rect(s, Inches(0), Inches(3.5), SLIDE_W, Inches(2.0),
             rgb("#0A1020"))

    # 우상단 큰 글로우 (원형 그림자)
    add_oval(s, Inches(9.5), Inches(-2.5), Inches(7), Inches(7),
             color=rgb("#1E40AF"))

    # 카테고리 라벨
    add_rect(s, Inches(0.8), Inches(0.7), Inches(0.4), Pt(2), TH.primary)
    add_text(s, Inches(1.3), Inches(0.6), Inches(8), Inches(0.4),
             "CAPSTONE 2026-1  /  MIDTERM  /  연세대학교 컴퓨터과학과",
             size=11, bold=True, color=TH.primary, font=TH.font_main)

    # 우상단 날짜
    add_text(s, Inches(11), Inches(0.6), Inches(2), Inches(0.4),
             C.S1_COVER["date"], size=11, color=TH.accent,
             align=PP_ALIGN.RIGHT, font=TH.font_main)

    # 메인 타이틀 (매우 큰)
    add_text(s, Inches(0.8), Inches(1.4), Inches(11.5), Inches(2.4),
             C.S1_COVER["title"], size=36, bold=True, color=TH.text_white,
             font=TH.font_main, line_spacing=1.25)

    # 부제 + 좌측 컬러 라인
    add_rect(s, Inches(0.8), Inches(3.85), Inches(0.06), Inches(0.55),
             TH.accent)
    add_text(s, Inches(1.0), Inches(3.85), Inches(11.5), Inches(0.55),
             C.S1_COVER["subtitle"], size=14, color=TH.text_dim,
             font=TH.font_main, line_spacing=1.4)

    # 글래스 메트릭 카드 4 개
    metrics = [
        ("3", "데이터셋", "DEEP 1M / 8M · SIFT 1.5M"),
        ("5-seed", "신뢰구간", "외적 타당성 통계 보장"),
        ("+19.6%p", "Level 2", "공간 인식 단독 효과"),
        ("8/8", "negative", "skew 지표 |ρ|<0.2"),
    ]
    card_y = Inches(4.85)
    for i, (val, label, sub) in enumerate(metrics):
        x = Inches(0.8 + i * 3.06)
        add_round_rect(s, x, card_y, Inches(2.86), Inches(1.4),
                       TH.card, border=TH.primary, border_width=0.75)
        add_text(s, x + Inches(0.2), card_y + Inches(0.10), Inches(2.6),
                 Inches(0.55), val, size=22, bold=True, color=TH.primary,
                 font=TH.font_main)
        add_text(s, x + Inches(0.2), card_y + Inches(0.65), Inches(2.6),
                 Inches(0.3), label, size=11, bold=True, color=TH.text_white,
                 font=TH.font_main)
        add_text(s, x + Inches(0.2), card_y + Inches(0.96), Inches(2.6),
                 Inches(0.4), sub, size=9, color=TH.text_dim,
                 font=TH.font_main)

    # 하단 메타 (한 줄)
    add_rect(s, Inches(0.8), Inches(6.55), Inches(11.7), Pt(1), TH.border)
    add_text(s, Inches(0.8), Inches(6.65), Inches(8), Inches(0.3),
             C.S1_COVER["team"], size=14, bold=True, color=TH.text_white,
             font=TH.font_main)
    add_text(s, Inches(0.8), Inches(7.0), Inches(8), Inches(0.3),
             "  ·  ".join(C.S1_COVER["members"]),
             size=10, color=TH.text_dim, font=TH.font_main)
    add_text(s, Inches(8), Inches(6.65), Inches(4.7), Inches(0.3),
             C.S1_COVER["advisor"], size=10, color=TH.text_dim,
             align=PP_ALIGN.RIGHT, font=TH.font_main)


build_navy.s1_cover = s1_cover_gemini


def s15_thanks_gemini(prs):
    s = blank_slide(prs)
    set_bg(s, TH.bg_dark)
    # 글로우
    add_oval(s, Inches(4), Inches(1), Inches(5.5), Inches(5.5),
             color=rgb("#1E3A8A"))

    add_rect(s, Inches(5.65), Inches(2.5), Inches(2.0), Pt(3), TH.accent)
    add_text(s, Inches(0), Inches(2.85), SLIDE_W, Inches(1.2),
             C.S15_THANKS["title"], size=64, bold=True, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, Inches(0), Inches(4.2), SLIDE_W, Inches(0.6),
             C.S15_THANKS["subtitle"], size=18, color=TH.primary,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, Inches(0), Inches(5.6), SLIDE_W, Inches(0.4),
             C.S15_THANKS["team"], size=15, bold=True, color=TH.text_white,
             align=PP_ALIGN.CENTER, font=TH.font_main)
    add_text(s, Inches(0), Inches(6.05), SLIDE_W, Inches(0.4),
             " · ".join(C.S15_THANKS["members"]),
             size=11, color=TH.text_dim,
             align=PP_ALIGN.CENTER, font=TH.font_main)


build_navy.s15_thanks = s15_thanks_gemini


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_중간발표_gemini.pptx")
    prs = build_navy.build()
    prs.save(out)
    print(f"saved: {out}")
