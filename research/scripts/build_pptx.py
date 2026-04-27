#!/usr/bin/env python3
"""
build_pptx.py -- Build all 18 slides of the Samsung Research portfolio PPT.
Modern Glass design language: gradient backgrounds, rounded cards, pill badges.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx_helpers import (
    new_presentation, add_blank_slide, set_slide_bg, set_gradient_bg,
    add_rect, add_rounded_rect, add_glass_card, add_accent_bar,
    add_gradient_bar, add_pill_badge,
    add_textbox, add_multiline_textbox,
    add_section_title, add_metric_card, add_implication_box, add_image_safe,
    DEEP_NAVY, NAVY, MID_NAVY, ACCENT_BLUE, SKY_BLUE,
    DARK_TEXT, GRAY, GRAY2, LIGHT_BG, CARD_BORDER, WARM_GRAY, WHITE, BLACK,
    SHADOW_COLOR, RED_TINT, GREEN_TINT, RED_TEXT, GREEN_TEXT,
    SLIDE_WIDTH, SLIDE_HEIGHT, MARGIN_L, MARGIN_R, MARGIN_T,
    FONT_TITLE, FONT_BODY, FONT_EN,
)

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


def img(name: str) -> str:
    return os.path.join(ASSETS, name)


# ============================================================================
# S1: Title Slide -- Gradient background + glass stat cards
# ============================================================================
def build_s1(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, MID_NAVY)

    # Simulate gradient: top band = DEEP_NAVY, bottom band = NAVY
    add_rect(slide, 0, 0, SLIDE_WIDTH, Inches(3.75), fill_color=DEEP_NAVY)
    add_rect(slide, 0, Inches(3.75), SLIDE_WIDTH, Inches(3.75), fill_color=NAVY)

    # Tagline
    add_textbox(slide, Inches(0.8), Inches(1.0), Inches(11.5), Inches(0.35),
                "SAMSUNG RESEARCH  \u00B7  SPATIAL AUDIO PORTFOLIO",
                font_size=10, font_color=ACCENT_BLUE, bold=True,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    # Title
    add_textbox(slide, Inches(0.8), Inches(1.6), Inches(11.5), Inches(1.6),
                "Spatial Audio Research &\nPerception-driven Quality Evaluation",
                font_size=32, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    # Glass stat strip: 4 cards in a row
    stat_top = Inches(3.6)
    stat_h = Inches(0.85)
    stat_w = Inches(2.5)
    gap = Inches(0.3)
    total_w = 4 * int(stat_w) + 3 * int(gap)
    start_x = Emu((int(SLIDE_WIDTH) - total_w) // 2)

    stats = [
        ("24", "SCI(E) Papers"),
        ("18", "h-index"),
        ("6", "Patents"),
        ("10+", "Awards"),
    ]
    for i, (num, lbl) in enumerate(stats):
        sx = start_x + Emu(i * (int(stat_w) + int(gap)))
        # Glass card with semi-transparent feel (white border on dark bg)
        add_rounded_rect(slide, sx, stat_top, stat_w, stat_h,
                         fill_color=RGBColor(0x1A, 0x30, 0xA5),
                         border_color=RGBColor(0x4D, 0x6D, 0xCC),
                         border_width_pt=0.75)
        add_textbox(slide, sx, stat_top + Inches(0.08), stat_w, Inches(0.45),
                    num, font_size=26, font_color=WHITE, bold=True,
                    alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                    font_name=FONT_EN)
        add_textbox(slide, sx, stat_top + Inches(0.5), stat_w, Inches(0.3),
                    lbl, font_size=10, font_color=RGBColor(0xB0, 0xC4, 0xEE),
                    alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    # Name
    add_textbox(slide, Inches(0.8), Inches(4.8), Inches(11.5), Inches(0.45),
                "Hyun In Jo, Ph.D.  (\uc870\ud604\uc778)",
                font_size=14, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    # Affiliation
    add_textbox(slide, Inches(0.8), Inches(5.3), Inches(11.5), Inches(0.35),
                "Samsung Research \u00B7 Visual Technology \u00B7 Display Innovation Lab \u00B7 Spatial Audio",
                font_size=11, font_color=WARM_GRAY, bold=False,
                alignment=PP_ALIGN.CENTER)

    # Contact
    add_textbox(slide, Inches(0.8), Inches(5.7), Inches(11.5), Inches(0.35),
                "best2012@naver.com  |  010-6387-8402  |  linkedin.com/in/hyunin-jo",
                font_size=10, font_color=WARM_GRAY, bold=False,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)


# ============================================================================
# S2: About Me
# ============================================================================
def build_s2(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(12),
                      "About Me",
                      "\uc870\ud604\uc778 (Hyun In Jo, Ph.D.) \u2014 \uacbd\ub825 \u00B7 \ud575\uc2ec \uc2e4\uc801 \u00B7 \uc804\ubb38\uc131")

    # --- Left: Career Timeline ---
    tl_left = Inches(0.8)
    tl_top = Inches(1.8)
    entries = [
        ("2013-2016", "B.S. \uac74\ucd95\uacf5\ud559, \ud55c\uc591\ub300 (\uc218\uc11d\uc878\uc5c5, \uc870\uae30\uc878\uc5c5)"),
        ("2016-2022", "Ph.D. \uac74\ucd95\uc74c\ud5a5, \ud55c\uc591\ub300 (\uc11d\ubc15\ud1b5\ud569, GPA 4.39/4.5)"),
        ("2022.03-08", "Post-doc, \ud55c\uad6d\uac74\uc124\uae30\uc220\uc5f0\uad6c\uc6d0"),
        ("2022.08-\ud604\uc7ac", "\ud604\ub300\uc790\ub3d9\ucc28 NVH \ucc45\uc784\uc5f0\uad6c\uc6d0"),
        ("NOW \u2192", "Samsung Research, Spatial Audio"),
    ]
    for i, (year, desc) in enumerate(entries):
        y = tl_top + Inches(i * 0.7)
        # Navy dot
        add_rounded_rect(slide, tl_left, y + Inches(0.07), Inches(0.13), Inches(0.13),
                         fill_color=NAVY)
        # Connecting line
        if i < len(entries) - 1:
            add_rect(slide, tl_left + Inches(0.055), y + Inches(0.2),
                     Inches(0.02), Inches(0.5), fill_color=ACCENT_BLUE)
        add_textbox(slide, tl_left + Inches(0.3), y, Inches(1.5), Inches(0.3),
                    year, font_size=10, font_color=ACCENT_BLUE, bold=True,
                    font_name=FONT_EN)
        add_textbox(slide, tl_left + Inches(1.9), y, Inches(3.5), Inches(0.4),
                    desc, font_size=10, font_color=DARK_TEXT)

    # --- Right: 4 glass metric cards ---
    card_left = Inches(7.0)
    card_w = Inches(2.8)
    card_h = Inches(0.85)
    cards = [
        ("SCI(E) 24\ud3b8", "\uc8fc\uc800\uc790 21\ud3b8, h-index 18"),
        ("EAA Best Paper", "ICA 2019, I-INCE Young Professional"),
        ("\ud2b9\ud5c8 6\uac74", "\uad6d\ub0b4+\ubbf8\uad6d, \uae30\uc220\uc774\uc804 5\ucc9c\ub9cc\uc6d0"),
        ("\uad6d\uc81c\uacf5\ub3d9\uc5f0\uad6c", "UCL\u00b7\uc18c\ub974\ubcf8, SATP 18\uac1c\uad6d \ud45c\uc900\ud654"),
    ]
    for i, (num, lbl) in enumerate(cards):
        cy = Inches(1.8) + Inches(i * 1.05)
        add_metric_card(slide, card_left, cy, card_w, card_h,
                        num, lbl, number_size=17, label_size=9)

    # --- Bottom: 4 navy competency boxes (rounded) ---
    box_w = Inches(2.85)
    box_h = Inches(0.7)
    box_top = Inches(6.2)
    parts = [
        ("Part I", "Spatial Audio &\nImmersive Rendering"),
        ("Part II", "Perception-driven\nQuality Evaluation"),
        ("Part III", "Research-to-Product\nExecution"),
        ("Part IV", "AI-driven Audio\nProcessing"),
    ]
    for i, (label, desc) in enumerate(parts):
        bx = Inches(0.6) + Inches(i * 3.1)
        add_rounded_rect(slide, bx, box_top, box_w, box_h, fill_color=NAVY)
        add_textbox(slide, bx + Inches(0.12), box_top + Inches(0.06),
                    box_w - Inches(0.24), Inches(0.2),
                    label, font_size=9, font_color=ACCENT_BLUE, bold=True,
                    font_name=FONT_EN)
        add_textbox(slide, bx + Inches(0.12), box_top + Inches(0.28),
                    box_w - Inches(0.24), Inches(0.38),
                    desc, font_size=10, font_color=WHITE)


# ============================================================================
# S3: Key Question
# ============================================================================
def build_s3(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)
    add_gradient_bar(slide, top=Inches(0), height=Pt(5))

    # Problem statement
    add_textbox(slide, Inches(0.8), Inches(0.6), Inches(11.5), Inches(1.0),
                "THD 0.01%, \uc8fc\ud30c\uc218 \uc751\ub2f5 \u00b10.5dB \u2014\n\uacf5\ud559 \uc2a4\ud399\uc774 \uc644\ubcbd\ud574\ub3c4 \uc0ac\uc6a9\uc790\uac00 \"\uc88b\ub2e4\"\uace0 \ub290\ub07c\uc9c0 \uc54a\uc744 \uc218 \uc788\ub2e4",
                font_size=15, font_color=GRAY, bold=False,
                alignment=PP_ALIGN.CENTER)

    # Highlight
    add_textbox(slide, Inches(0.8), Inches(1.7), Inches(11.5), Inches(0.5),
                "\uc2dc\uac01 \ub9e5\ub77d\ub9cc\uc73c\ub85c \uc624\ub514\uc624 \ub9cc\uc871\ub3c4\uac00 76% \uc88c\uc6b0\ub41c\ub2e4\uba74?",
                font_size=14, font_color=ACCENT_BLUE, bold=True,
                alignment=PP_ALIGN.CENTER)

    # Center glass card with navy bg
    ctr_w = Inches(9.0)
    ctr_h = Inches(2.2)
    ctr_l = Emu((int(SLIDE_WIDTH) - int(ctr_w)) // 2)
    ctr_t = Inches(2.5)
    add_glass_card(slide, ctr_l, ctr_t, ctr_w, ctr_h,
                   fill_color=NAVY, border_color=ACCENT_BLUE, shadow=True)
    add_textbox(slide, ctr_l, ctr_t, ctr_w, ctr_h,
                "\uc0ac\uc6a9\uc790\uac00 \uc9c4\uc9dc \ubab0\uc785\uc744 \ub290\ub07c\ub294\n3D Audio-Visual \uacbd\ud5d8\uc744\n\uc5b4\ub5bb\uac8c \uc124\uacc4\ud558\uace0 \uac80\uc99d\ud560 \uac83\uc778\uac00?",
                font_size=22, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE)

    # 4 roadmap glass cards
    card_w = Inches(2.6)
    card_h = Inches(1.2)
    card_top = Inches(5.2)
    parts = [
        "Part I\nSpatial Audio &\nImmersive Rendering",
        "Part II\nPerception-driven\nQuality Evaluation",
        "Part III\nResearch-to-Product\nExecution",
        "Part IV\nAI-driven Audio\nProcessing",
    ]
    for i, txt in enumerate(parts):
        cx = Inches(0.5) + Inches(i * 3.2)
        add_glass_card(slide, cx, card_top, card_w, card_h,
                       fill_color=WHITE, shadow=True)
        add_textbox(slide, cx + Inches(0.1), card_top + Inches(0.1),
                    card_w - Inches(0.2), card_h - Inches(0.2),
                    txt, font_size=10, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER,
                    anchor=MSO_ANCHOR.MIDDLE)
        if i < 3:
            ax = cx + card_w
            add_textbox(slide, ax, card_top + Inches(0.35), Inches(0.6), Inches(0.4),
                        "\u2192", font_size=18, font_color=ACCENT_BLUE, bold=True,
                        alignment=PP_ALIGN.CENTER, font_name=FONT_EN)


# ============================================================================
# S4: Soundscape Introduction
# ============================================================================
def build_s4(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(12),
                      "\uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504\ub780?",
                      "Noise Control \u2192 Soundscape \ud328\ub7ec\ub2e4\uc784 \uc804\ud658")

    # Two columns: Traditional (glass) vs Soundscape (navy glass)
    lw = Inches(5.0)
    lh = Inches(1.5)
    lt = Inches(1.8)

    add_glass_card(slide, Inches(0.6), lt, lw, lh, shadow=True)
    add_textbox(slide, Inches(0.8), lt + Inches(0.15), lw - Inches(0.4), Inches(0.3),
                "Traditional Noise Control", font_size=13, font_color=NAVY, bold=True)
    add_textbox(slide, Inches(0.8), lt + Inches(0.55), lw - Inches(0.4), Inches(0.7),
                '"\uc18c\uc74c\uc774 \uc5bc\ub9c8\ub098 \ud070\uac00?" dB \uce21\uc815',
                font_size=11, font_color=DARK_TEXT)

    add_textbox(slide, Inches(5.8), lt + Inches(0.4), Inches(1.2), Inches(0.5),
                "\u2192", font_size=28, font_color=ACCENT_BLUE, bold=True,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    add_glass_card(slide, Inches(7.2), lt, lw, lh,
                   fill_color=NAVY, border_color=ACCENT_BLUE, shadow=True)
    add_textbox(slide, Inches(7.4), lt + Inches(0.15), lw - Inches(0.4), Inches(0.3),
                "New Paradigm: Soundscape", font_size=13, font_color=WHITE, bold=True)
    add_textbox(slide, Inches(7.4), lt + Inches(0.55), lw - Inches(0.4), Inches(0.7),
                '"\uc18c\ub9ac\uac00 \uc5b4\ub5bb\uac8c \uacbd\ud5d8\ub418\ub294\uac00?" \uc778\uac04 \uc9c0\uac01 \uc911\uc2ec',
                font_size=11, font_color=WHITE)

    # ISO definition in glass card
    add_glass_card(slide, Inches(0.6), Inches(3.6), Inches(11.8), Inches(0.8), shadow=False)
    add_textbox(slide, Inches(0.8), Inches(3.7), Inches(11.4), Inches(0.6),
                'ISO 12913: "acoustic environment as perceived or experienced and/or understood '
                'by a person or people, in context"',
                font_size=11, font_color=GRAY, bold=False,
                alignment=PP_ALIGN.CENTER)

    # Pleasant-Eventful diagram
    add_image_safe(slide, img("proto_s5_img2.png"),
                   Inches(3.5), Inches(4.5), Inches(6.0), Inches(2.7),
                   placeholder_text="Pleasant-Eventful Diagram")


# ============================================================================
# S5: Soundscape -> Spatial Audio Bridge
# ============================================================================
def build_s5(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(12),
                      "\uc654 \uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504\uac00 Spatial Audio\uc5d0 \uc9c1\uacb0\ub418\ub294\uac00",
                      "")

    rows = [
        ("\uc18c\ub9ac\ub97c \uacbd\ud5d8\uc73c\ub85c \ud3c9\uac00\n(dB\uac00 \uc544\ub2cc \uc0ac\uc6a9\uc790 \uc9c0\uac01 \uc911\uc2ec)",
         "\ub80c\ub354\ub9c1 \ud488\uc9c8\uc744 THD\u00b7\uc8fc\ud30c\uc218\uc751\ub2f5\uc774 \uc544\ub2cc\n\uc0ac\uc6a9\uc790\uac00 \ub290\ub07c\ub294 \uacf5\uac04\uac10\u00b7\ubab0\uc785\uac10\uc73c\ub85c \ud3c9\uac00"),
        ("\uc624\ub514\uc624-\ube44\uc8fc\uc5bc \uc0c1\ud638\uc791\uc6a9\n(\uc2dc\uac01 \ub9e5\ub77d\uc774 \uccad\uac01 \uc9c0\uac01\uc744 \ucd5c\ub300 76% \uc88c\uc6b0)",
         "Display + Audio \ud1b5\ud569 \uc124\uacc4\nHolographic Displays \u00d7 Spatial Audio \uc2dc\ub108\uc9c0"),
        ("\uc7ac\uc0dd \ud658\uacbd\uc5d0 \ub530\ub77c \ub3d9\uc77c \uc74c\uc6d0 \uc9c0\uac01 \ubcc0\ud654",
         "\uac70\uc2e4\u00b7\uce68\uc2e4\u00b7\ucc28\ub7c9 \ub4f1 \uc7ac\uc0dd \uacf5\uac04\ubcc4\n\ub80c\ub354\ub9c1 \ucd5c\uc801\ud654"),
        ("\uac1c\uc778\ucc28 (\uc18c\uc74c \ubbfc\uac10\ub3c4\u00b7\uc131\uaca9\u00b7\uccad\ub825)",
         "Customized Audio \uac1c\uc778\ud654"),
        ("\ub300\uaddc\ubaa8 \uc9c0\uac01 \ud3c9\uac00 \ud504\ub85c\ud1a0\ucf5c\n(ISO 12913 + SATP 18\uac1c\uad6d, 134\uba85)",
         "Eclipsa Audio \ud488\uc9c8 \ubca4\uce58\ub9c8\ud0b9 \ubc0f\n\uc778\uc99d \uae30\uc900 \uc218\ub9bd"),
    ]

    col_w = Inches(5.2)
    row_h = Inches(0.85)
    left1 = Inches(0.6)
    left2 = Inches(7.0)
    arrow_l = Inches(5.9)

    for i, (left_t, right_t) in enumerate(rows):
        ry = Inches(1.5) + Inches(i * 0.95)
        bg_color = WHITE if i % 2 == 0 else LIGHT_BG
        add_glass_card(slide, left1, ry, col_w, row_h,
                       fill_color=bg_color, shadow=False)
        add_textbox(slide, left1 + Inches(0.15), ry + Inches(0.08),
                    col_w - Inches(0.3), row_h - Inches(0.16),
                    left_t, font_size=10, font_color=DARK_TEXT)
        add_textbox(slide, arrow_l, ry + Inches(0.15), Inches(1.0), Inches(0.5),
                    "\u2192", font_size=16, font_color=ACCENT_BLUE, bold=True,
                    alignment=PP_ALIGN.CENTER, font_name=FONT_EN)
        add_glass_card(slide, left2, ry, col_w, row_h,
                       fill_color=bg_color, shadow=False)
        add_textbox(slide, left2 + Inches(0.15), ry + Inches(0.08),
                    col_w - Inches(0.3), row_h - Inches(0.16),
                    right_t, font_size=10, font_color=DARK_TEXT)

    # Navy bottom bar (rounded)
    bar_top = Inches(6.5)
    add_rounded_rect(slide, Inches(0.6), bar_top, Inches(12.1), Inches(0.7),
                     fill_color=NAVY)
    add_textbox(slide, Inches(0.8), bar_top + Inches(0.1), Inches(11.7), Inches(0.5),
                '\uc2e0\ud638\ucc98\ub9ac\uac00 "\uc5b4\ub5bb\uac8c \uad6c\ud604\ud560 \uac83\uc778\uac00"\ub77c\uba74, \uc800\uc758 \uc804\ubb38\uc131\uc740 '
                '"\uc0ac\uc6a9\uc790\uac00 \uc5b4\ub5bb\uac8c \uacbd\ud5d8\ud560 \uac83\uc778\uac00"\ub97c \uc124\uacc4\ud558\uace0 \uac80\uc99d\ud558\ub294 \uac83\uc785\ub2c8\ub2e4',
                font_size=11, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)


# ============================================================================
# S6: Spatial Audio Overview -- VISUAL RESEARCH MAP
# ============================================================================
def build_s6(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(12),
                      "Part I. Spatial Audio \uae30\uc220 \uc5ed\ub7c9 \u2014 \uc5f0\uad6c \uccb4\uacc4\ub3c4",
                      "5\uac1c \uae30\uc220 \ucd95 + Eclipsa Audio \uc5f0\uacb0 \ub9f5")

    # Central navy pill
    hub_w = Inches(4.5)
    hub_h = Inches(0.75)
    hub_l = Emu((int(SLIDE_WIDTH) - int(hub_w)) // 2)
    hub_t = Inches(1.6)
    add_rounded_rect(slide, hub_l, hub_t, hub_w, hub_h, fill_color=NAVY)
    add_textbox(slide, hub_l, hub_t, hub_w, hub_h,
                "Spatial Audio Perception Research",
                font_size=15, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                font_name=FONT_EN)

    # 5 axis glass cards in a row
    axes = [
        ("\ucd951", "\uc2dc\uac01 \uc7ac\ud604", "77%", "APAC'22", "HMD\uc5d0\uc11c Presence \uc720\uc758 \uc99d\uac00", ACCENT_BLUE),
        ("\ucd952", "\uc7ac\uc0dd \ubc29\uc2dd", "2.2dBA", "APAC'19", "HP vs SP \ud5c8\uc6a9\ud55c\uacc4 \ucc28\uc774", ACCENT_BLUE),
        ("\ucd953", "\ubc14\uc774\ub178\ub7f4-\ube44\uc8fc\uc5bc", "77%", "B&E'19", "HRTF\uac00 \uacf5\uac04\uac10 \uc9c0\ubc30", SKY_BLUE),
        ("\ucd954", "\uc2dc\uccad\uac01 \uc815\ubcf4", "76%", "B&E'20", "Visual\uc774 \ub9cc\uc871\ub3c4 \uc88c\uc6b0", SKY_BLUE),
        ("\ucd955", "\uc0dd\ud0dc\ud559\uc801 \ud0c0\ub2f9\uc131", "VR\u2248In-situ", "SCS'21", "3\uac1c \ud504\ub85c\ud1a0\ucf5c \uc720\uc758\ucc28 \uc5c6\uc74c", RGBColor(0x0A, 0x7A, 0xB5)),
    ]

    card_w = Inches(2.3)
    card_h = Inches(3.3)
    row_top = Inches(2.7)
    gap = Inches(0.18)
    total = 5 * int(card_w) + 4 * int(gap)
    start_x = Emu((int(SLIDE_WIDTH) - total) // 2)

    for idx, (ax_label, ax_title, ax_metric, ax_ref, ax_finding, color) in enumerate(axes):
        cx = start_x + Emu(idx * (int(card_w) + int(gap)))

        # Connecting line from hub
        line_x = cx + Emu(int(card_w) // 2) - Inches(0.01)
        add_rect(slide, line_x, hub_t + hub_h, Inches(0.025),
                 row_top - hub_t - hub_h, fill_color=color)

        # Glass card
        add_glass_card(slide, cx, row_top, card_w, card_h, shadow=True)

        # Colored top strip
        add_rounded_rect(slide, cx, row_top, card_w, Inches(0.06), fill_color=color)

        # Axis label
        add_textbox(slide, cx + Inches(0.1), row_top + Inches(0.15),
                    card_w - Inches(0.2), Inches(0.22),
                    ax_label, font_size=11, font_color=color, bold=True, font_name=FONT_EN)

        # Title
        add_textbox(slide, cx + Inches(0.1), row_top + Inches(0.4),
                    card_w - Inches(0.2), Inches(0.25),
                    ax_title, font_size=11, font_color=NAVY, bold=True)

        # Big metric
        add_textbox(slide, cx + Inches(0.1), row_top + Inches(0.75),
                    card_w - Inches(0.2), Inches(0.55),
                    ax_metric, font_size=24, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                    font_name=FONT_EN)

        # Reference pill
        add_pill_badge(slide, cx + Inches(0.1), row_top + Inches(1.4),
                       ax_ref, font_size=8)

        # Finding
        add_textbox(slide, cx + Inches(0.1), row_top + Inches(1.85),
                    card_w - Inches(0.2), Inches(1.3),
                    ax_finding, font_size=9, font_color=DARK_TEXT)

    # Eclipsa Audio connection text
    ecl_top = Inches(6.3)
    add_rounded_rect(slide, Inches(2.0), ecl_top, Inches(9.3), Inches(0.55),
                     fill_color=NAVY)
    add_textbox(slide, Inches(2.2), ecl_top + Inches(0.05), Inches(8.9), Inches(0.45),
                "\u2192 Eclipsa Audio: HRTF \uac1c\uc778\ud654(77%) + A-V \ud1b5\ud569\uc124\uacc4(76%) + VR \ud488\uc9c8\ud3c9\uac00 \uc2e4\uc99d + 92.5% \ub9cc\uc871\ub3c4 \uc608\uce21",
                font_size=11, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)


# ============================================================================
# Helper for S7-S11 research axis slides
# ============================================================================
def _build_research_slide(prs, title, paper_ref, paper_journal, rq_text,
                          methodology_lines, figure_path, figure_label,
                          metrics, implications):
    """Build a two-column research slide with glass design."""
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    # Section title (left)
    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(7), title, "")

    # Paper pill badge (top right)
    add_pill_badge(slide, Inches(8.5), Inches(0.55), paper_ref, font_size=9)
    add_textbox(slide, Inches(8.5), Inches(0.9), Inches(4.2), Inches(0.25),
                paper_journal, font_size=9, font_color=GRAY, font_name=FONT_EN)

    # RQ glass card (full width)
    rq_top = Inches(1.25)
    add_glass_card(slide, Inches(0.6), rq_top, Inches(12.1), Inches(0.65), shadow=False)
    add_textbox(slide, Inches(0.8), rq_top + Inches(0.08), Inches(11.7), Inches(0.5),
                rq_text, font_size=12, font_color=NAVY, bold=True)

    # LEFT COLUMN: Research Question + Methodology
    left_x = Inches(0.6)
    meth_top = Inches(2.1)
    meth_w = Inches(5.8)

    add_glass_card(slide, left_x, meth_top, meth_w, Inches(3.2), shadow=True)
    add_textbox(slide, left_x + Inches(0.15), meth_top + Inches(0.1),
                meth_w - Inches(0.3), Inches(0.25),
                "Methodology", font_size=13, font_color=NAVY, bold=True)
    add_multiline_textbox(
        slide, left_x + Inches(0.15), meth_top + Inches(0.4),
        meth_w - Inches(0.3), Inches(2.7),
        methodology_lines, line_spacing=1.25)

    # RIGHT COLUMN: Figure
    fig_x = Inches(6.7)
    fig_top = Inches(2.1)
    add_textbox(slide, fig_x, fig_top, Inches(6.0), Inches(0.3),
                figure_label, font_size=11, font_color=GRAY, bold=True)
    add_image_safe(slide, img(figure_path),
                   fig_x, fig_top + Inches(0.35), Inches(6.0), Inches(3.0),
                   placeholder_text=figure_path)

    # BOTTOM: Metric cards + Implication strip
    mc_top = Inches(5.6)
    mc_h = Inches(0.85)
    mc_w = Inches(2.0)
    for i, (num, lbl) in enumerate(metrics):
        mx = Inches(0.6) + Emu(i * (int(mc_w) + int(Inches(0.25))))
        add_metric_card(slide, mx, mc_top, mc_w, mc_h, num, lbl,
                        number_size=24, label_size=9)

    # Implication strip
    add_implication_box(slide, Inches(7.5), mc_top, Inches(5.2), Inches(1.6),
                        implications, font_size=10, line_spacing=1.2)

    return slide


# ============================================================================
# S7: Axis 1 - Visual Reproduction
# ============================================================================
def build_s7(prs):
    _build_research_slide(
        prs,
        title="\ucd951: \uc2dc\uac01 \uc7ac\ud604 \ubc29\uc2dd",
        paper_ref="APAC 2022 \u00B7 Jo & Jeon",
        paper_journal="Applied Acoustics, IF 3.4",
        rq_text="RQ: \uac19\uc740 Spatial Audio\ub97c HMD vs \ubaa8\ub2c8\ud130\ub85c \ubcfc \ub54c, \uc0ac\uc6a9\uc790\uc758 \uc74c\ud658\uacbd \uc9c0\uac01\uc774 \uc5bc\ub9c8\ub098 \ub2ec\ub77c\uc9c0\ub294\uac00?",
        methodology_lines=[
            ("\uc2e4\ud5d8\uc124\uacc4: 40\uba85 \ud53c\ud5d8\uc790 \u00d7 8\uac1c \ub3c4\uc2dc \uc74c\ud658\uacbd", True, DARK_TEXT, 11),
            ("\uc2dc\uac01 \uc7ac\ud604: HMD (HTC VIVE Pro) vs 2D Monitor", False, DARK_TEXT, 10),
            ("\uc624\ub514\uc624: First-Order Ambisonics (FOA) + Head-tracking", False, DARK_TEXT, 10),
            ("\ud3c9\uac00: 14\uac1c semantic differential pairs", False, DARK_TEXT, 10),
            ("\ud1b5\uacc4: \ubc18\ubcf5\uce21\uc815 ANOVA, Bonferroni \uc0ac\ud6c4\uac80\uc815", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("\ud575\uc2ec \ubc1c\uacac:", True, ACCENT_BLUE, 11),
            ("  - HMD: \uacf5\uac04 \ud604\uc2e4\uac10(Presence) \uc720\uc758\ud558\uac8c \uc99d\uac00 (p < 0.05)", False, DARK_TEXT, 10),
            ("  - \ubaa8\ub2c8\ud130: \uc804\ubc18\uc801 \uc18c\uc74c \uc778\uc2dd \ub354 \ub192\uc74c", False, DARK_TEXT, 10),
            ("  - \uc2dc\uac01 \uc7ac\ud604 \ubc29\uc2dd\uc774 \uc624\ub514\uc624 \ud488\uc9c8 \ud310\ub2e8\uc744 \uccb4\uacc4\uc801\uc73c\ub85c \ubcc0\ud654\uc2dc\ud0b4", False, DARK_TEXT, 10),
        ],
        figure_path="apac2022_p6.png",
        figure_label="Result \u2014 Semantic Profile Comparison",
        metrics=[
            ("40 \u00d7 8", "\ud53c\ud5d8\uc790 \u00d7 \ud658\uacbd"),
            ("p < 0.05", "HMD Presence \uc720\uc758\ucc28"),
            ("14 pairs", "Semantic Differential"),
        ],
        implications=[
            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
            ("XR \ub514\ubc14\uc774\uc2a4 \ub300\uc751 \uc2dc, \uc2dc\uac01 \uc870\uac74 \ud1b5\uc81c\uac00", False, WHITE, 10),
            ("\uc624\ub514\uc624 \ud488\uc9c8 \ud3c9\uac00\uc758 \ud544\uc218 \uc804\uc81c \uc870\uac74", False, WHITE, 10),
            ("\u2192 Eclipsa Audio \ud488\uc9c8 \ud3c9\uac00 \ud504\ub85c\ud1a0\ucf5c\uc5d0", False, WHITE, 10),
            ("  \uc2dc\uac01 \uc7ac\ud604 \ubc29\uc2dd \ubcc0\uc218 \ubc18\ub4dc\uc2dc \ud3ec\ud568", False, WHITE, 10),
        ],
    )


# ============================================================================
# S8: Axis 2 - Headphone vs Speaker
# ============================================================================
def build_s8(prs):
    _build_research_slide(
        prs,
        title="\ucd952: \ud5e4\ub4dc\ud3f0 vs \uc2a4\ud53c\ucee4",
        paper_ref="APAC 2019 \u00B7 Jeon et al",
        paper_journal="Applied Acoustics, IF 3.4",
        rq_text="RQ: \ud5e4\ub4dc\ud3f0\uacfc \uc2a4\ud53c\ucee4 \uc7ac\uc0dd \ubc29\uc2dd\uc774 \ub3d9\uc77c \uc74c\uc6d0\uc5d0 \ub300\ud55c \uc0ac\uc6a9\uc790\uc758 \uc18c\ub9ac \ud488\uc9c8 \ud310\ub2e8\uc744 \uc5b4\ub5bb\uac8c \ubc14\uafb8\ub294\uac00?",
        methodology_lines=[
            ("4\uac00\uc9c0 \uc7ac\uc0dd \uc870\uac74:", True, DARK_TEXT, 11),
            ("  (1) Headphone only  (2) Speaker only", False, DARK_TEXT, 10),
            ("  (3) Headphone + HMD  (4) Speaker + HMD", False, DARK_TEXT, 10),
            ("\uc790\uadf9: LAeq 40-65 dB, 6\ub2e8\uacc4 \uc18c\uc74c \ub808\ubca8", False, DARK_TEXT, 10),
            ("\uc885\uc18d\ubcc0\uc218: \uc131\uac00\uc2ec(Annoyance), \ud5c8\uc6a9\ud55c\uacc4(Allowance)", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("\ud575\uc2ec \ubc1c\uacac:", True, ACCENT_BLUE, 11),
            ("  - Annoyance \ucc28\uc774: headphone vs speaker 8%", False, DARK_TEXT, 10),
            ("  - Allowance \ucc28\uc774: 6%", False, DARK_TEXT, 10),
            ("  - 50% annoyance level\uc5d0\uc11c SPL \ucc28\uc774: 2.2 dBA", False, DARK_TEXT, 10),
            ("  - Speaker + HMD = \uc2e4\uc81c \ud604\uc7a5\uc5d0 \uac00\uc7a5 \uadfc\uc811", False, DARK_TEXT, 10),
        ],
        figure_path="be2019a_p7.png",
        figure_label="Result \u2014 Annoyance vs SPL by Condition",
        metrics=[
            ("8%", "Annoyance \ucc28\uc774"),
            ("6%", "Allowance \ucc28\uc774"),
            ("2.2 dBA", "50% SPL \ucc28\uc774"),
        ],
        implications=[
            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
            ("\ud5e4\ub4dc\ud3f0(\ubc14\uc774\ub178\ub7f4) vs \uc2a4\ud53c\ucee4(\uba40\ud2f0\ucc44\ub110) \uc7ac\uc0dd \uc2dc", False, WHITE, 10),
            ("\uc0ac\uc6a9\uc790 \uc9c0\uac01 \ucc28\uc774\uac00 \uccb4\uacc4\uc801\uc73c\ub85c \ubc1c\uc0dd", False, WHITE, 10),
            ("\u2192 Eclipsa Audio \ub80c\ub354\ub9c1 \ud488\uc9c8 \ud3c9\uac00\uc5d0\uc11c", False, WHITE, 10),
            ("  \uc7ac\uc0dd \ub514\ubc14\uc774\uc2a4\ubcc4 \ubcf4\uc815 \uae30\uc900 \ud544\uc694", False, WHITE, 10),
            ("\u2192 Speaker+HMD\uac00 reference condition\uc73c\ub85c \uc801\ud569", False, WHITE, 10),
        ],
    )


# ============================================================================
# S9: Axis 3 - Binaural-Visual Interaction
# ============================================================================
def build_s9(prs):
    _build_research_slide(
        prs,
        title="\ucd953: \ubc14\uc774\ub178\ub7f4-\ube44\uc8fc\uc5bc \uc0c1\ud638\uc791\uc6a9",
        paper_ref="B&E 2019 \u00d7 2\ud3b8",
        paper_journal="Building and Environment, IF 7.4",
        rq_text="RQ: HRTF \ubc14\uc774\ub178\ub7f4 \ub80c\ub354\ub9c1\uacfc HMD \uc2dc\uac01 \uc7ac\ud604, \uc5b4\ub290 \uac83\uc774 \uc0ac\uc6a9\uc790 \uacf5\uac04 \uc9c0\uac01\uc5d0 \ub354 \uc9c0\ubc30\uc801\uc778\uac00?",
        methodology_lines=[
            ("2x2 Factorial Design:", True, DARK_TEXT, 11),
            ("  Factor A: HRTF (Individualized vs Generic)", False, DARK_TEXT, 10),
            ("  Factor B: HMD (VR 360 vs No Visual)", False, DARK_TEXT, 10),
            ("\ud53c\ud5d8\uc790: 40\uba85 \u00d7 8\uac1c \ub3c4\uc2dc \uc74c\ud658\uacbd = 320 data points", False, DARK_TEXT, 10),
            ("\uc7a5\ube44: Sennheiser HD-650 + HTC VIVE Pro", False, DARK_TEXT, 10),
            ("HRTF: CIPIC HRTF Database", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("\ud575\uc2ec \ubc1c\uacac:", True, ACCENT_BLUE, 11),
            ("  - HRTF\uac00 \uacf5\uac04\uac10 \uc9c0\uac01\uc758 77% \uc124\uba85 (\uc9c0\ubc30\uc801 \uc694\uc778)", False, DARK_TEXT, 10),
            ("  - HMD\ub294 23% \ubcf4\uc870\uc801 \uc5ed\ud560", False, DARK_TEXT, 10),
            ("  - VR \ud658\uacbd\uc5d0\uc11c \ud5c8\uc6a9\ud55c\uacc4 6\u007e7 dB \ud558\ub77d", False, DARK_TEXT, 10),
        ],
        figure_path="be2019a_p8.png",
        figure_label="Result \u2014 HRTF vs HMD Contribution",
        metrics=[
            ("77%", "HRTF \uacf5\uac04\uac10 \uae30\uc5ec"),
            ("23%", "HMD \uc2dc\uac01 \uae30\uc5ec"),
            ("6~7 dB", "VR \ud5c8\uc6a9\ud55c\uacc4 \ud558\ub77d"),
        ],
        implications=[
            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
            ("HRTF \uac1c\uc778\ud654 = \ub80c\ub354\ub7ec \ucd5c\uc801\ud654\uc758 \ucd5c\uc6b0\uc120 \uacfc\uc81c (77%)", False, WHITE, 10),
            ("\u2192 Eclipsa Audio HRTF \uac1c\uc778\ud654 \uc54c\uace0\ub9ac\uc998 \uac1c\ubc1c \uc2dc", False, WHITE, 10),
            ("  \uacf5\uac04\uac10 \ud5a5\uc0c1 \ud6a8\uacfc\uac00 \uc2dc\uac01 \uc7ac\ud604\ubcf4\ub2e4 3\ubc30 \uc774\uc0c1 \uc9c0\ubc30\uc801", False, WHITE, 10),
            ("\u2192 \uc81c\ud55c\ub41c \ub9ac\uc18c\uc2a4\uc5d0\uc11c HRTF\uc5d0 \uc9d1\uc911 \ud22c\uc790 \uadfc\uac70", False, WHITE, 10),
        ],
    )


# ============================================================================
# S10: Axis 4 - Audio-Visual Information
# ============================================================================
def build_s10(prs):
    _build_research_slide(
        prs,
        title="\ucd954: \uc2dc\uccad\uac01 \uc815\ubcf4 \uae30\uc5ec\ub3c4",
        paper_ref="B&E 2020 \u00B7 Jeon & Jo",
        paper_journal="Building and Environment, IF 7.4",
        rq_text="RQ: Audio \uc815\ubcf4\uc640 Visual \uc815\ubcf4\uac00 \uc804\uccb4 \ud658\uacbd \ub9cc\uc871\ub3c4\uc5d0 \uac01\uac01 \uc5bc\ub9c8\ub098 \uae30\uc5ec\ud558\ub294\uac00?",
        methodology_lines=[
            ("\uc624\ub514\uc624: FOA Ambisonics + HMD + Head-tracking", True, DARK_TEXT, 11),
            ("\ud658\uacbd: 8\uac1c \ub3c4\uc2dc \uc74c\ud658\uacbd (\uacf5\uc6d0, \ub3c4\ub85c, \uad11\uc7a5 \ub4f1)", False, DARK_TEXT, 10),
            ("3\uac00\uc9c0 \uc81c\uc2dc \uc870\uac74:", True, DARK_TEXT, 11),
            ("  (1) Audio-only  (2) Visual-only  (3) Audio+Visual", False, DARK_TEXT, 10),
            ("\uc885\uc18d\ubcc0\uc218: \ub9cc\uc871\ub3c4, \uc790\uc5f0\uc2a4\ub7ec\uc6c0, \ucf80\uc801\uc131", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("\ud575\uc2ec \ubc1c\uacac:", True, ACCENT_BLUE, 11),
            ("  - \ub9cc\uc871\ub3c4 \uae30\uc5ec: Audio 24% vs Visual 76%", False, DARK_TEXT, 10),
            ("  - \ub9cc\uc871\ub3c4 \uc608\uce21 \ubaa8\ub378 \uc124\uba85\ub825: R\u00b2 = 51%", False, DARK_TEXT, 10),
            ("  - \uc2dc\uac01\uc774 \uc9c0\ubc30\uc801\uc774\ub098, \uc624\ub514\uc624 \uc5c6\uc774\ub294 \uc790\uc5f0\uc2a4\ub7ec\uc6c0 \uc800\ud558", False, DARK_TEXT, 10),
        ],
        figure_path="be2020_p8.png",
        figure_label="Result \u2014 A/V Contribution to Satisfaction",
        metrics=[
            ("24%", "Audio \ub9cc\uc871\ub3c4 \uae30\uc5ec"),
            ("76%", "Visual \ub9cc\uc871\ub3c4 \uae30\uc5ec"),
            ("R\u00b2=51%", "\ub9cc\uc871\ub3c4 \ubaa8\ub378 \uc124\uba85\ub825"),
        ],
        implications=[
            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
            ("Display + Audio \ud1b5\ud569 \uc124\uacc4\uac00 \ub9cc\uc871\ub3c4\uc758 \ud575\uc2ec", False, WHITE, 10),
            ("\u2192 Holographic Displays x Spatial Audio \uc2dc\ub108\uc9c0:", False, WHITE, 10),
            ("  \uc2dc\uac01 76% + \uc624\ub514\uc624 24%\uc758 cross-modal \ud6a8\uacfc \uadf9\ub300\ud654", False, WHITE, 10),
            ("\u2192 \uc624\ub514\uc624 \ud488\uc9c8\ub9cc \uc62c\ub824\ub3c4 \uc790\uc5f0\uc2a4\ub7ec\uc6c0 \uac1c\uc120 \uac00\ub2a5", False, WHITE, 10),
        ],
    )


# ============================================================================
# S11: Axis 5 - Ecological Validity
# ============================================================================
def build_s11(prs):
    _build_research_slide(
        prs,
        title="\ucd955: \uc0dd\ud0dc\ud559\uc801 \ud0c0\ub2f9\uc131",
        paper_ref="SCS 2021 \u00B7 Jo & Jeon",
        paper_journal="Sustainable Cities and Society, IF 11.7",
        rq_text="RQ: VR \uc2e4\ud5d8\uc2e4\uc5d0\uc11c\uc758 \uc74c\ud658\uacbd \ud3c9\uac00\ub97c \uc2e4\uc81c \ud604\uc7a5(in-situ) \uacb0\uacfc\uc640 \ub3d9\uc77c\ud558\uac8c \uc2e0\ub8b0\ud560 \uc218 \uc788\ub294\uac00?",
        methodology_lines=[
            ("\ub300\uaddc\ubaa8 \uc2e4\ud5d8: 50\uba85 \ud53c\ud5d8\uc790 \u00d7 10\uac1c \ub3c4\uc2dc \uc74c\ud658\uacbd", True, DARK_TEXT, 11),
            ("ISO 12913-2 \ud45c\uc900 3\uac1c \ud504\ub85c\ud1a0\ucf5c \ube44\uad50:", True, DARK_TEXT, 11),
            ("  Method A: \ud604\uc7a5 \uc9c1\uc811 \ud3c9\uac00 (In-situ)", False, DARK_TEXT, 10),
            ("  Method B: \ud604\uc7a5 \ub179\uc74c \ud6c4 \uc2e4\ud5d8\uc2e4 \uc7ac\uc0dd", False, DARK_TEXT, 10),
            ("  Method C: VR (FOA Ambisonics + HMD + Head-tracking)", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("\ud575\uc2ec \ubc1c\uacac:", True, ACCENT_BLUE, 11),
            ("  - VR vs In-situ: \ud1b5\uacc4\uc801 \uc720\uc758\ucc28 \uc5c6\uc74c", False, DARK_TEXT, 10),
            ("  - P-E \ubaa8\ub378\uc774 3\uac1c \ud504\ub85c\ud1a0\ucf5c \ubaa8\ub450\uc5d0\uc11c \uc7ac\ud604", False, DARK_TEXT, 10),
            ("  - \uac00\uc7a5 \ub192\uc740 IF(11.7) \u2014 \uc5f0\uad6c \uc601\ud5a5\ub825 \uc785\uc99d", False, DARK_TEXT, 10),
        ],
        figure_path="scs2021_p5.png",
        figure_label="Result \u2014 Protocol Comparison (P-E Model)",
        metrics=[
            ("50 \u00d7 10", "\ud53c\ud5d8\uc790 \u00d7 \ud658\uacbd"),
            ("3 Protocols", "ISO 12913-2 A/B/C"),
            ("VR \u2248 In-situ", "\uc720\uc758\ucc28 \uc5c6\uc74c"),
        ],
        implications=[
            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
            ("VR \uc2e4\ud5d8\uc2e4\uc5d0\uc11c Eclipsa Audio \ub80c\ub354\ub9c1 \ud488\uc9c8 \ud3c9\uac00 \u2192", False, WHITE, 10),
            ("\uc2e4\uc0ac\uc6a9 \ud658\uacbd \uacb0\uacfc\uc640 \ub3d9\uc77c\ud558\uac8c \uc2e0\ub8b0 \uac00\ub2a5", False, WHITE, 10),
            ("\u2192 \uc81c\ud488 \ucd9c\uc2dc \uc804 VR \uae30\ubc18 \ub300\uaddc\ubaa8 \ud3c9\uac00 \ud504\ub808\uc784\uc6cc\ud06c", False, WHITE, 10),
            ("  \uad6c\ucd95 \uac00\ub2a5 (\ud604\uc7a5 \ud14c\uc2a4\ud2b8 \ube44\uc6a9 \ub300\ud3ed \uc808\uac10)", False, WHITE, 10),
        ],
    )


# ============================================================================
# S12: Multimodal Biosignal Modeling
# ============================================================================
def build_s12(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(7),
                      "Part II. \uba40\ud2f0\ubaa8\ub2ec \uc0dd\ub9ac\ubc18\uc751 \ubaa8\ub378\ub9c1", "")

    # Paper pills
    add_pill_badge(slide, Inches(8.0), Inches(0.55),
                   "SCS 2023 + SR 2022 + IJERPH 2024", font_size=8)
    add_textbox(slide, Inches(8.0), Inches(0.9), Inches(4.5), Inches(0.25),
                "3\ud3b8 \uc5f0\uc18d \ucd9c\ud310 \uc2dc\ub9ac\uc988 (IF 11.7+)", font_size=9, font_color=GRAY)

    # Experiment protocol glass card
    proto_top = Inches(1.2)
    add_glass_card(slide, Inches(0.6), proto_top, Inches(12.1), Inches(1.3), shadow=True)

    add_multiline_textbox(
        slide, Inches(0.8), proto_top + Inches(0.08), Inches(5.5), Inches(1.15),
        [
            ("\uc2e4\ud5d8 \uaddc\ubaa8: 60\uba85 \u00d7 9\ud658\uacbd \u00d7 2\uc77c", True, NAVY, 12),
            ("MAT (Montreal Arithmetic Task) \uc2a4\ud2b8\ub808\uc2a4 \uc720\ub3c4", False, DARK_TEXT, 10),
            ("Day1: \uc900\ube44\u2192\uc2a4\ud2b8\ub808\uc2a4\u2192\uc790\uadf9\u2192HRV+EEG (\u00d76 = 60min)", False, DARK_TEXT, 10),
            ("Day2: \uc900\ube44\u2192\uc790\uadf9\u2192\uc8fc\uad00\ud3c9\uac00 (\u00d76 = 42min)", False, DARK_TEXT, 10),
        ],
        line_spacing=1.25,
    )

    add_multiline_textbox(
        slide, Inches(6.5), proto_top + Inches(0.08), Inches(6.0), Inches(1.15),
        [
            ("\uce21\uc815 \uc7a5\ube44:", True, NAVY, 12),
            ("HRV: SA-3000NEW (5\uac1c \uc2dc\uac04/\uc8fc\ud30c\uc218 \ub3c4\uba54\uc778 \uc9c0\ud45c)", False, DARK_TEXT, 10),
            ("EEG: EMOTIV EPOC Flex 32ch, 128Hz sampling", False, DARK_TEXT, 10),
            ("Eye-tracking: Tobii Pro (\uc2dc\uc120 \uace0\uc815, \uc0b0\ub3d9 \ubd84\uc11d)", False, DARK_TEXT, 10),
        ],
        line_spacing=1.25,
    )

    # 4 LARGE metric cards
    mc_top = Inches(2.7)
    mc_w = Inches(2.85)
    mc_h = Inches(0.95)
    metrics = [
        ("CCA 0.80", "\ubb3c\ub9ac\uc74c\ud5a5 \u2194 \uc2ec\ub9ac\ubc18\uc751"),
        ("CCA 0.78", "\uc9c0\uac01\ud488\uc9c8 \u2194 \uc2ec\ub9ac\ubc18\uc751"),
        ("SDNN +14.6%", "\uc2a4\ud2b8\ub808\uc2a4 \uc800\ud56d\ub825 \u2191"),
        ("TSI -9.5%", "\uc2a4\ud2b8\ub808\uc2a4 \uc9c0\uc218 \u2193"),
    ]
    for i, (num, lbl) in enumerate(metrics):
        mx = Inches(0.6) + Emu(i * (int(mc_w) + int(Inches(0.2))))
        add_metric_card(slide, mx, mc_top, mc_w, mc_h, num, lbl,
                        number_size=22, label_size=10)

    # Two figures side by side
    fig_top = Inches(3.85)
    fig_h = Inches(2.4)
    add_textbox(slide, Inches(0.6), fig_top - Inches(0.25), Inches(5.8), Inches(0.25),
                "HRV Stress Recovery Analysis", font_size=10, font_color=GRAY, bold=True)
    add_image_safe(slide, img("scs2023_p9.png"),
                   Inches(0.6), fig_top, Inches(5.8), fig_h,
                   placeholder_text="scs2023_p9.png (HRV)")

    add_textbox(slide, Inches(6.7), fig_top - Inches(0.25), Inches(5.8), Inches(0.25),
                "Eye-tracking Heatmap Analysis", font_size=10, font_color=GRAY, bold=True)
    add_image_safe(slide, img("ijerph2024_p5.png"),
                   Inches(6.7), fig_top, Inches(5.8), fig_h,
                   placeholder_text="ijerph2024_p5.png (Eye)")

    # Implication strip (full width, rounded)
    imp_top = Inches(6.4)
    add_implication_box(slide, Inches(0.6), imp_top, Inches(12.1), Inches(0.9),
                        [
                            ("Samsung \uc2dc\uc0ac\uc810:  ", True, WHITE, 11),
                            ("(1) \uc0dd\ub9ac\uc2e0\ud638 \uae30\ubc18 \uac1d\uad00\uc801 \ud488\uc9c8 \ud3c9\uac00 \u2192 \uc8fc\uad00 \uc124\ubb38\uc758 \ud55c\uacc4 \ubcf4\uc644  "
                             "(2) EEG\u00b7HRV\ub85c \ub80c\ub354\ub9c1 \ud488\uc9c8 \ubcc0\ud654\uc5d0 \ub300\ud55c \uc2e0\uccb4 \ubc18\uc751 \uc815\ub7c9\ud654  "
                             "(3) Galaxy Watch\u00b7Buds \uc13c\uc11c\ub85c \uc2e4\uc2dc\uac04 \uac80\uc99d \ud30c\uc774\ud504\ub77c\uc778 \uad6c\ucd95 \uac00\ub2a5", False, WHITE, 9),
                        ],
                        font_size=10, line_spacing=1.3)


# ============================================================================
# S13: Soundscape Design Application
# ============================================================================
def build_s13(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(7),
                      "\uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504 \ub514\uc790\uc778 \uc751\uc6a9", "")

    add_pill_badge(slide, Inches(8.5), Inches(0.55),
                   "B&E 2021 + B&E 2022", font_size=9)
    add_textbox(slide, Inches(8.5), Inches(0.9), Inches(4.0), Inches(0.25),
                "Building and Environment, IF 7.4 \u00d7 2\ud3b8", font_size=9, font_color=GRAY)

    # RQ glass card
    rq_top = Inches(1.25)
    add_glass_card(slide, Inches(0.6), rq_top, Inches(12.1), Inches(0.65), shadow=False)
    add_textbox(slide, Inches(0.8), rq_top + Inches(0.08), Inches(11.7), Inches(0.5),
                "RQ: \uc624\ub514\uc624-\ube44\uc8fc\uc5bc \uc0c1\ud638\uc791\uc6a9\uc774 \uc2e4\ub0b4 \ud658\uacbd\uc758 \uc5c5\ubb34 \ud488\uc9c8\uacfc \uc0dd\uc0b0\uc131\uc5d0 \ubbf8\uce58\ub294 \uc601\ud5a5\uc740?",
                font_size=12, font_color=NAVY, bold=True)

    # LEFT: Two paper summaries in glass card
    left_x = Inches(0.6)
    meth_top = Inches(2.1)
    meth_w = Inches(5.8)

    add_glass_card(slide, left_x, meth_top, meth_w, Inches(3.5), shadow=True)
    add_multiline_textbox(
        slide, left_x + Inches(0.15), meth_top + Inches(0.1), meth_w - Inches(0.3), Inches(3.3),
        [
            ("B&E 2021 \u2014 SEM \uad6c\uc870\ubc29\uc815\uc2dd \ubaa8\ub378", True, NAVY, 12),
            ("  Audio \u2192 Visual \u2192 \ud658\uacbd\ub9cc\uc871\ub3c4 \uacbd\ub85c\uacc4\uc218 \uc815\ub7c9\ud654", False, DARK_TEXT, 10),
            ("  \uc624\ub514\uc624 \ud488\uc9c8\uc774 \uc2dc\uac01 \ucf80\uc801\uc131\uc5d0 \uac04\uc811\ud6a8\uacfc (cross-modal)", False, DARK_TEXT, 10),
            ("  Soundscape\u2192Overall satisfaction \uacbd\ub85c \uc720\uc758 (p<0.01)", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("B&E 2022 \u2014 \uc2e4\ub0b4 \uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504 \u2192 \uc5c5\ubb34 \ud488\uc9c8", True, NAVY, 12),
            ("  Audio-Visual \uc77c\uce58 \ucf58\ud150\uce20\uac00 \uc5c5\ubb34 \uc120\ud638\ub3c4\u00b7\uc0dd\uc0b0\uc131 \uc720\uc758 \ud5a5\uc0c1", False, DARK_TEXT, 10),
            ("  \uc790\uc5f0 \uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504: \uc9d1\uc911\ub3c4 +15%, \uc2a4\ud2b8\ub808\uc2a4 -12%", False, DARK_TEXT, 10),
            ("  \ub3c4\uc2dc \uc18c\uc74c: \uc5c5\ubb34 \uc815\ud655\ub3c4 -8% (\ubc29\ud574 \ud6a8\uacfc \uc815\ub7c9\ud654)", False, DARK_TEXT, 10),
        ],
        line_spacing=1.25,
    )

    # RIGHT: SEM figure (LARGE)
    fig_x = Inches(6.7)
    fig_top = Inches(2.1)
    add_textbox(slide, fig_x, fig_top, Inches(6.0), Inches(0.3),
                "SEM Path Model \u2014 Path Coefficients", font_size=11, font_color=GRAY, bold=True)
    add_image_safe(slide, img("be2021_p9.png"),
                   fig_x, fig_top + Inches(0.35), Inches(6.0), Inches(3.5),
                   placeholder_text="be2021_p9.png (SEM)")

    # BOTTOM: Metrics + Implication
    mc_top = Inches(5.8)
    mc_h = Inches(0.8)
    mc_w = Inches(2.5)
    metrics = [
        ("+15%", "\uc790\uc5f0 \uc0ac\uc6b4\ub4dc \uc9d1\uc911\ub3c4 \ud5a5\uc0c1"),
        ("-12%", "\uc2a4\ud2b8\ub808\uc2a4 \uac10\uc18c \ud6a8\uacfc"),
        ("p < 0.01", "SEM \uacbd\ub85c \uc720\uc758\uc131"),
    ]
    for i, (num, lbl) in enumerate(metrics):
        mx = Inches(0.6) + Emu(i * (int(mc_w) + int(Inches(0.2))))
        add_metric_card(slide, mx, mc_top, mc_w, mc_h, num, lbl,
                        number_size=22, label_size=9)

    add_implication_box(slide, Inches(8.4), mc_top, Inches(4.3), Inches(1.5),
                        [
                            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
                            ("Eclipsa Audio \uc7ac\uc0dd \uacf5\uac04\uc758 \uc2e4\ub0b4 \ud658\uacbd \uc124\uacc4:", False, WHITE, 10),
                            ("\u2192 TV\u00b7\uc0ac\uc6b4\ub4dc\ubc14 + \uc870\uba85\uc758 A-V \ud1b5\ud569 \ucd5c\uc801\ud654", False, WHITE, 10),
                            ("\u2192 Galaxy Home \ud658\uacbd \uc74c\ud5a5 \uc790\ub3d9 \ud29c\ub2dd \uadfc\uac70", False, WHITE, 10),
                        ],
                        font_size=10, line_spacing=1.25)


# ============================================================================
# S14: AVAS Soundscape Design
# ============================================================================
def build_s14(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(7),
                      "Part III. AVAS \uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504 \ub514\uc790\uc778", "")

    add_pill_badge(slide, Inches(8.5), Inches(0.55),
                   "HMG \ud2b9\ubcc4\uc0c1 + JASA (\uc2ec\uc0ac \uc911)", font_size=9)
    add_textbox(slide, Inches(8.5), Inches(0.9), Inches(4.0), Inches(0.25),
                "134\uba85 \ub300\uaddc\ubaa8 \uccad\uac10\ud3c9\uac00", font_size=9, font_color=GRAY)

    # Data overview bar (glass)
    data_top = Inches(1.2)
    add_glass_card(slide, Inches(0.6), data_top, Inches(12.1), Inches(0.5), shadow=False)
    add_textbox(slide, Inches(0.8), data_top + Inches(0.05), Inches(11.7), Inches(0.4),
                "17\uac1c EV \u00d7 43\uac1c AVAS \ubc14\uc774\ub178\ub7f4 \ub179\uc74c | 134\uba85 \uccad\uac10\ud3c9\uac00 | Binaural BHS II + GoPro Visual | 34\ub300 \uacbd\uc7c1 DB",
                font_size=11, font_color=DARK_TEXT, bold=True, alignment=PP_ALIGN.CENTER)

    # LEFT: Methodology + Results in glass card
    left_x = Inches(0.6)
    meth_top = Inches(1.9)
    meth_w = Inches(5.8)

    add_glass_card(slide, left_x, meth_top, meth_w, Inches(3.5), shadow=True)
    add_multiline_textbox(
        slide, left_x + Inches(0.15), meth_top + Inches(0.1), meth_w - Inches(0.3), Inches(3.3),
        [
            ("3\ub2e8\uacc4 \uac10\uc131\uc5b4\ud718 \uac1c\ubc1c:", True, NAVY, 12),
            ("  Stage 1: 272\uac1c \ud615\uc6a9\uc0ac \uc218\uc9d1", False, DARK_TEXT, 10),
            ("  Stage 2: \uc804\ubb38\uac00 \ucd95\uc18c \u2192 25\uc30d", False, DARK_TEXT, 10),
            ("  Stage 3: \uc694\uc778\ubd84\uc11d \ucd5c\uc885 18\uc30d", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("PCA \uacb0\uacfc \u2014 \uc2e0\uaddc \ud3c9\uac00\ucd95:", True, ACCENT_BLUE, 12),
            ("  \uae30\uc874: Pleasant-Eventful (\ud658\uacbd \uc0ac\uc6b4\ub4dc\uc2a4\ucf00\uc774\ud504)", False, DARK_TEXT, 10),
            ("  \uc2e0\uaddc: Comfort-Metallic (EV AVAS \ud2b9\ud654 \ucd95)", False, DARK_TEXT, 10),
            ("", False, DARK_TEXT, 6),
            ("\ube0c\ub79c\ub4dc \ud3ec\uc9c0\uc154\ub2dd:", True, ACCENT_BLUE, 12),
            ("  34\ub300 \uacbd\uc7c1 \ucc28\ub7c9 DB\ub85c \ube0c\ub79c\ub4dc\ubcc4 AVAS \uc74c\uc9c8 \ub9e4\ud551", False, DARK_TEXT, 10),
            ("  \ub9cc\uc871\ub3c4 \uc608\uce21 \ubaa8\ub378: \uc815\ud655\ub3c4 92.5%", False, DARK_TEXT, 10),
        ],
        line_spacing=1.2,
    )

    # RIGHT: PCA figure
    fig_x = Inches(6.7)
    fig_top = Inches(1.9)
    add_textbox(slide, fig_x, fig_top, Inches(6.0), Inches(0.3),
                "PCA \u2014 Comfort-Metallic Axes + Brand Positioning", font_size=10, font_color=GRAY, bold=True)
    add_image_safe(slide, img("hmg_s11_img1.png"),
                   fig_x, fig_top + Inches(0.35), Inches(6.0), Inches(3.3),
                   placeholder_text="PCA Figure: Comfort-Metallic Axes")

    # BOTTOM: Metrics + Implication
    mc_top = Inches(5.7)
    mc_h = Inches(0.8)
    mc_w = Inches(2.0)
    metrics = [
        ("92.5%", "\ub9cc\uc871\ub3c4 \uc608\uce21 \uc815\ud655\ub3c4"),
        ("18\uc30d", "\ucd5c\uc885 \uac10\uc131\uc5b4\ud718"),
        ("34\ub300", "\uacbd\uc7c1 DB \ubca4\uce58\ub9c8\ud06c"),
    ]
    for i, (num, lbl) in enumerate(metrics):
        mx = Inches(0.6) + Emu(i * (int(mc_w) + int(Inches(0.2))))
        add_metric_card(slide, mx, mc_top, mc_w, mc_h, num, lbl,
                        number_size=24, label_size=9)

    add_implication_box(slide, Inches(7.2), mc_top, Inches(5.5), Inches(1.55),
                        [
                            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
                            ("\ub300\uaddc\ubaa8 \uccad\uac10 \ud3c9\uac00 \ud504\ub808\uc784 \u2192 Eclipsa Audio \ud488\uc9c8 \uc778\uc99d \uc801\uc6a9", False, WHITE, 10),
                            ("\uac10\uc131\uc5b4\ud718 \uae30\ubc18 \ud3c9\uac00\ucd95 \u2192 \ub80c\ub354\ub9c1 \ud488\uc9c8 \ucc28\uc6d0 \ud655\uc7a5", False, WHITE, 10),
                            ("\uacbd\uc7c1 DB \ubca4\uce58\ub9c8\ud0b9 \u2192 \uc0bc\uc131 \uc624\ub514\uc624 \uc81c\ud488 \ud3ec\uc9c0\uc154\ub2dd", False, WHITE, 10),
                            ("92.5% \uc608\uce21 \ubaa8\ub378 \u2192 \ub80c\ub354\ub9c1 \ud488\uc9c8 \ud29c\ub2dd \uc790\ub3d9\ud654 \uadfc\uac70", False, WHITE, 10),
                        ],
                        font_size=10, line_spacing=1.2)


# ============================================================================
# S15: Research -> Production Execution
# ============================================================================
def build_s15(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(12),
                      "\uc5f0\uad6c \u2192 \uc591\uc0b0 \uc2e4\ud589\ub825",
                      "AVAS \ube0c\ub79c\ub4dc \uc0ac\uc6b4\ub4dc 2.0 \u2014 EV3, IONIQ 5 \uc591\uc0b0 \uc801\uc6a9")

    # 4-step process flow (glass cards with step numbers + arrows)
    steps = [
        ("\uc74c\ud5a5 \uc124\uacc4", "\uc18c\ub9ac \ud2b9\uc131 \uc815\uc758\n\ubaa9\ud45c \uc74c\uc9c8 \uc124\uc815\n\uac10\uc131\uc5b4\ud718 \uae30\ubc18 \ub514\uc790\uc778"),
        ("\uccad\ucde8 \ud3c9\uac00", "134\uba85 \ub300\uaddc\ubaa8 \uc2e4\ud5d8\n18\uc30d \uac10\uc131\uc5b4\ud718\nPCA \ub9cc\uc871\ub3c4 \ubaa8\ub378"),
        ("\uc2dc\uc2a4\ud15c \uac80\uc99d", "\uc2e4\ucc28 \ubc14\uc774\ub178\ub7f4 \ub179\uc74c\nBHS II + GoPro\n\uc8fc\ud589 \uc870\uac74\ubcc4 \uac80\uc99d"),
        ("\uc591\uc0b0 \uc801\uc6a9", "EV3 \uc591\uc0b0 \uc801\uc6a9\nIONIQ 5 \uc801\uc6a9\nShiny \uc6f9 \uc608\uce21 \ud234"),
    ]
    box_w = Inches(2.6)
    box_h = Inches(1.6)
    flow_top = Inches(1.55)
    for i, (title, detail) in enumerate(steps):
        bx = Inches(0.5) + Inches(i * 3.2)
        is_last = (i == 3)
        fc = WHITE if is_last else DARK_TEXT
        bg = NAVY if is_last else WHITE

        add_glass_card(slide, bx, flow_top, box_w, box_h,
                       fill_color=bg,
                       border_color=ACCENT_BLUE if is_last else CARD_BORDER,
                       shadow=True)

        # Step number badge
        badge_bg = ACCENT_BLUE if not is_last else WHITE
        badge_fc = WHITE if not is_last else NAVY
        add_rounded_rect(slide, bx + Inches(0.1), flow_top + Inches(0.08),
                         Inches(0.3), Inches(0.3), fill_color=badge_bg)
        add_textbox(slide, bx + Inches(0.1), flow_top + Inches(0.08),
                    Inches(0.3), Inches(0.3),
                    str(i + 1), font_size=12, font_color=badge_fc, bold=True,
                    alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, font_name=FONT_EN)
        # Title
        add_textbox(slide, bx + Inches(0.5), flow_top + Inches(0.08),
                    box_w - Inches(0.6), Inches(0.3),
                    title, font_size=13, font_color=fc, bold=True)
        # Detail
        add_textbox(slide, bx + Inches(0.15), flow_top + Inches(0.5),
                    box_w - Inches(0.3), Inches(1.0),
                    detail, font_size=10, font_color=fc if is_last else DARK_TEXT)
        # Arrow
        if i < 3:
            add_textbox(slide, bx + box_w, flow_top + Inches(0.55),
                        Inches(0.55), Inches(0.5),
                        "\u2192", font_size=20, font_color=ACCENT_BLUE, bold=True,
                        alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    # 4 achievement cards
    ac_top = Inches(3.4)
    ac_w = Inches(2.85)
    ac_h = Inches(0.95)
    achievements = [
        ("\ud2b9\ud5c8 6\uac74", "\uad6d\ub0b4 4\uac74 + \ubbf8\uad6d 2\uac74"),
        ("\uae30\uc220\uc774\uc804 5\ucc9c\ub9cc\uc6d0", "\uc0b0\uc5c5 \uc801\uc6a9 \u2192 \uc591\uc0b0 \uc2e4\ud604"),
        ("HMG \ud2b9\ubcc4\uc0c1", "\ud559\uc220\ub300\ud68c \uc5f0\uad6c \uc131\uacfc\uc0c1"),
        ("Shiny \uc6f9 \ud234", "\uc2e4\uc2dc\uac04 \ub9cc\uc871\ub3c4 \uc608\uce21"),
    ]
    for i, (num, lbl) in enumerate(achievements):
        ax = Inches(0.5) + Emu(i * (int(ac_w) + int(Inches(0.2))))
        add_metric_card(slide, ax, ac_top, ac_w, ac_h, num, lbl,
                        number_size=20, label_size=9)

    # Cross-department coordination (glass card)
    coord_top = Inches(4.6)
    add_glass_card(slide, Inches(0.5), coord_top, Inches(12.2), Inches(0.5), shadow=False)
    add_textbox(slide, Inches(0.7), coord_top + Inches(0.05), Inches(11.8), Inches(0.4),
                "\ubd80\uc11c \uac04 \ud611\uc5c5: Design (\uc0ac\uc6b4\ub4dc \uc544\uc774\ub374\ud2f0\ud2f0) \u00d7 Regulation (UN R138 \ubc95\uaddc \ub300\uc751) \u00d7 NVH (\uc2e4\ucc28 \uac80\uc99d) \u00d7 \uc591\uc0b0\ud300 (\uc801\uc6a9)",
                font_size=10, font_color=DARK_TEXT, bold=True, alignment=PP_ALIGN.CENTER)

    # Figure + Implication
    add_image_safe(slide, img("hmg_s17_img1.png"),
                   Inches(0.5), Inches(5.3), Inches(6.5), Inches(2.0),
                   placeholder_text="Production Process Figure")

    add_implication_box(slide, Inches(7.3), Inches(5.3), Inches(5.4), Inches(2.0),
                        [
                            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
                            ("", False, WHITE, 4),
                            ("\uc5f0\uad6c\u2192\uc591\uc0b0 end-to-end \uc2e4\ud589\ub825 \uc785\uc99d:", False, WHITE, 10),
                            ("  \uccad\uac10\ud3c9\uac00 \u2192 \ud2b9\ud5c8 \u2192 \uae30\uc220\uc774\uc804 \u2192 \uc591\uc0b0\uc758 \uc804 \uc8fc\uae30", False, WHITE, 10),
                            ("Samsung \uc801\uc6a9:", True, WHITE, 10),
                            ("  \ub80c\ub354\ub9c1 \uc54c\uace0\ub9ac\uc998\uc758 \uc81c\ud488 \uc801\uc6a9 \uc8fc\uae30 \ub2e8\ucd95", False, WHITE, 10),
                            ("  Eclipsa Audio \ud488\uc9c8 \uc778\uc99d \u2192 \uc81c\ud488 \ucd9c\uc2dc \ud30c\uc774\ud504\ub77c\uc778", False, WHITE, 10),
                        ],
                        font_size=10, line_spacing=1.2)


# ============================================================================
# S16: AI Audio Processing
# ============================================================================
def build_s16(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(7),
                      "Part IV. AI \uae30\ubc18 \uc624\ub514\uc624 \ucc98\ub9ac", "")

    add_pill_badge(slide, Inches(8.5), Inches(0.55),
                   "SENSORS 2021 + \ud2b9\ud5c8 2\uac74", font_size=9)
    add_textbox(slide, Inches(8.5), Inches(0.9), Inches(4.0), Inches(0.25),
                "\uae30\uc220\uc774\uc804 5\ucc9c\ub9cc\uc6d0 \ub2ec\uc131", font_size=9, font_color=GRAY)

    # Problem card (red-tinted glass)
    left_x = Inches(0.6)
    ps_top = Inches(1.2)
    ps_w = Inches(6.0)

    add_glass_card(slide, left_x, ps_top, ps_w, Inches(0.75),
                   fill_color=RED_TINT, border_color=RGBColor(0xE8, 0xC4, 0xC0), shadow=False)
    add_multiline_textbox(
        slide, left_x + Inches(0.15), ps_top + Inches(0.05), ps_w - Inches(0.3), Inches(0.65),
        [
            ("Problem: \ub370\uc774\ud130 \ud76c\uc18c\uc131", True, RED_TEXT, 12),
            ("  30\uba85 \uc804\ubb38\uac00 \u00d7 126\uac74 \uccad\uac10\ud3c9\uac00 \u2192 \uc2ec\uac01\ud55c \ub370\uc774\ud130 \ubd80\uc871 | \uc804\ubb38\uac00 \ud3c9\uac00: \ube44\uc6a9\u00b7\uc2dc\uac04 \uacfc\ub2e4", False, DARK_TEXT, 10),
        ],
        line_spacing=1.25,
    )

    # Solution card (green-tinted glass)
    sol_top = Inches(2.05)
    add_glass_card(slide, left_x, sol_top, ps_w, Inches(0.75),
                   fill_color=GREEN_TINT, border_color=RGBColor(0xB8, 0xDE, 0xC5), shadow=False)
    add_multiline_textbox(
        slide, left_x + Inches(0.15), sol_top + Inches(0.05), ps_w - Inches(0.3), Inches(0.65),
        [
            ("Solution: RIR Convolution Data Augmentation", True, GREEN_TEXT, 12),
            ("  8\uac1c \uc6d0\ubcf8 \u2192 RIR \ud569\uc131\uacf1 \u2192 43,000\uac1c\ub85c \ud655\uc7a5 (5,375\ubc30) | + Loudness ISO 532B + Energy Ratio", False, DARK_TEXT, 10),
        ],
        line_spacing=1.25,
    )

    # RIGHT: LSTM figure
    fig_x = Inches(6.9)
    fig_top = Inches(1.2)
    add_textbox(slide, fig_x, fig_top, Inches(5.8), Inches(0.25),
                "5-Layer LSTM Architecture", font_size=10, font_color=GRAY, bold=True)
    add_image_safe(slide, img("sensors2021_p5.png"),
                   fig_x, fig_top + Inches(0.3), Inches(5.8), Inches(2.3),
                   placeholder_text="sensors2021_p5.png (LSTM)")

    # AI vs 8 Pulmonologists comparison - 3 glass cards
    comp_top = Inches(3.1)
    add_textbox(slide, left_x, comp_top, Inches(6.0), Inches(0.3),
                "AI vs 8\uba85 \ud638\ud761\uae30\ub0b4\uacfc \uc804\ubb38\uc758 \ube44\uad50", font_size=12, font_color=NAVY, bold=True)

    comparisons = [
        ("Accuracy", "84.9%", "56.4%"),
        ("Sensitivity", "90.0%", "40.7%"),
        ("AUC", "0.84", "0.56"),
    ]
    cc_w = Inches(2.6)
    cc_h = Inches(1.2)
    cc_top = Inches(3.45)
    for i, (title, ai_val, expert_val) in enumerate(comparisons):
        cx = Inches(0.6) + Emu(i * (int(cc_w) + int(Inches(0.2))))
        add_glass_card(slide, cx, cc_top, cc_w, cc_h,
                       border_color=ACCENT_BLUE, shadow=True)
        add_textbox(slide, cx, cc_top + Inches(0.05), cc_w, Inches(0.25),
                    title, font_size=10, font_color=GRAY, bold=True,
                    alignment=PP_ALIGN.CENTER, font_name=FONT_EN)
        add_textbox(slide, cx, cc_top + Inches(0.3), cc_w, Inches(0.4),
                    f"AI  {ai_val}", font_size=20, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER, font_name=FONT_EN)
        add_textbox(slide, cx, cc_top + Inches(0.75), cc_w, Inches(0.35),
                    f"Expert avg  {expert_val}", font_size=11, font_color=GRAY,
                    alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    # IP box (right middle, glass card)
    ip_top = Inches(3.7)
    ip_w = Inches(4.6)
    add_glass_card(slide, Inches(8.2), ip_top, ip_w, Inches(1.0),
                   border_color=NAVY, shadow=True)
    add_multiline_textbox(
        slide, Inches(8.35), ip_top + Inches(0.08), ip_w - Inches(0.3), Inches(0.8),
        [
            ("IP & \uae30\uc220\uc774\uc804", True, NAVY, 12),
            ("KR \ud2b9\ud5c8 \ub4f1\ub85d + US \ud2b9\ud5c8 \ucd9c\uc6d0", False, DARK_TEXT, 10),
            ("\uae30\uc220\uc774\uc804: 5,000\ub9cc\uc6d0 (\ud604\ub300\uc790\ub3d9\ucc28 \u2192 \uc0b0\uc5c5\uccb4)", False, DARK_TEXT, 10),
        ],
        line_spacing=1.3,
    )

    # A-JEPA Vision box (PROMINENT, accent blue rounded)
    ajepa_top = Inches(4.9)
    ajepa_w = Inches(7.5)
    ajepa_h = Inches(1.15)
    add_rounded_rect(slide, Inches(0.6), ajepa_top, ajepa_w, ajepa_h,
                     fill_color=ACCENT_BLUE)
    add_multiline_textbox(
        slide, Inches(0.8), ajepa_top + Inches(0.1), ajepa_w - Inches(0.4), ajepa_h - Inches(0.2),
        [
            ("A-JEPA Vision \u2014 \ucc28\uc138\ub300 AI Audio \uc5f0\uad6c \ubc29\ud5a5", True, WHITE, 14),
            ("Meta Audio-JEPA \uc790\uae30\uc9c0\ub3c4 \ud559\uc2b5 + \uc74c\ud5a5 \ub3c4\uba54\uc778 \uc9c0\uc2dd \uacb0\ud569", False, WHITE, 11),
            ("\u2192 \ub77c\ubca8 \uc5c6\ub294 \ub300\uaddc\ubaa8 \uc624\ub514\uc624 \ub370\uc774\ud130\uc5d0\uc11c \uc74c\uc9c8 \ud45c\ud604 \uc790\ub3d9 \ud559\uc2b5", False, WHITE, 11),
            ("\u2192 Eclipsa Audio \ub80c\ub354\ub9c1 \ud488\uc9c8\uc758 end-to-end \uc790\ub3d9 \ud310\uc815 \ubaa9\ud45c", False, WHITE, 11),
        ],
        font_color=WHITE,
        line_spacing=1.2,
    )

    # Bottom right: Implication
    add_implication_box(slide, Inches(8.4), ajepa_top, Inches(4.3), Inches(2.3),
                        [
                            ("Samsung \uc2dc\uc0ac\uc810", True, WHITE, 12),
                            ("", False, WHITE, 4),
                            ("Eclipsa Audio \ub80c\ub354\ub9c1 \ud488\uc9c8\uc758", False, WHITE, 10),
                            ("\uc790\ub3d9 \ud310\uc815 \ud30c\uc774\ud504\ub77c\uc778 \uad6c\ucd95", False, WHITE, 10),
                            ("", False, WHITE, 4),
                            ("\ub300\uaddc\ubaa8 A/B \ud14c\uc2a4\ud2b8 \ube44\uc6a9 \uc808\uac10", False, WHITE, 10),
                            ("(\uc804\ubb38\uac00 8\uba85 \uc218\uc900 \u2192 AI 1\uac1c \ubaa8\ub378)", False, WHITE, 10),
                            ("", False, WHITE, 4),
                            ("A-JEPA\ub85c \ube44\uc9c0\ub3c4 \ud559\uc2b5 \ud655\uc7a5", False, WHITE, 10),
                        ],
                        font_size=10, line_spacing=1.1)


# ============================================================================
# S17: Contribution Plan
# ============================================================================
def build_s17(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, LIGHT_BG)

    add_section_title(slide, MARGIN_L, MARGIN_T, Inches(12),
                      "Contribution Plan",
                      "\uc0bc\uc131\ub9ac\uc11c\uce58 Spatial Audio \uae30\uc5ec \ub85c\ub4dc\ub9f5")

    # 3 timeline column headers (gradient light -> dark navy)
    cols = [
        ("\uc785\uc0ac ~ 6\uac1c\uc6d4 (\uc989\uc2dc \uae30\uc5ec)", ACCENT_BLUE),
        ("6\uac1c\uc6d4 ~ 2\ub144 (\uacfc\uc81c \ud655\uc7a5)", NAVY),
        ("2\ub144 ~ (Lab \ube44\uc804 \uc8fc\ub3c4)", DEEP_NAVY),
    ]
    col_w = Inches(3.45)
    col_h = Inches(0.45)
    label_w = Inches(1.9)
    hdr_top = Inches(1.55)

    for i, (title, color) in enumerate(cols):
        cx = label_w + Inches(0.15) + Emu(i * (int(col_w) + int(Inches(0.12))))
        add_rounded_rect(slide, cx, hdr_top, col_w, col_h, fill_color=color)
        add_textbox(slide, cx, hdr_top, col_w, col_h,
                    title, font_size=10, font_color=WHITE, bold=True,
                    alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # 4 row labels + cells
    row_labels = ["Eclipsa\nAudio", "AI \uc804\ud658", "\ud30c\ud2b8\n\uc2dc\ub108\uc9c0", "\uc778\uc99d\u00b7\ud45c\uc900"]
    row_h = Inches(1.1)
    row_start = hdr_top + col_h + Inches(0.08)

    grid = [
        [
            "\uccad\uac10 \ud3c9\uac00 \ud504\ub808\uc784 \uad6c\ucd95\n(ISO 12913 + SATP \ubc29\ubc95\ub860)\n\u2192 \uae30\uc874 \uc5f0\uad6c \uc989\uc2dc \uc801\uc6a9 \uac00\ub2a5",
            "HRTF \uac1c\uc778\ud654 \uc54c\uace0\ub9ac\uc998 \uac1c\ubc1c\n\ub80c\ub354\ub7ec \ud488\uc9c8 \ucd5c\uc801\ud654\n\u2192 77% \uacf5\uac04\uac10 \uae30\uc5ec\ub3c4 \ud65c\uc6a9",
            "\ucc28\uc138\ub300 Eclipsa Audio\n\ud488\uc9c8 \ud45c\uc900 \uc8fc\ub3c4\n\u2192 \uae00\ub85c\ubc8c de facto \ud45c\uc900 \ubaa9\ud45c",
        ],
        [
            "A-JEPA \ud504\ub85c\ud1a0\ud0c0\uc785 \uad6c\ucd95\n\uc74c\uc9c8 \uc790\ub3d9 \ud310\uc815 \ud30c\uc774\ud504\ub77c\uc778\n\u2192 LSTM 84.9% \uc815\ud655\ub3c4 \uae30\ubc18",
            "\uc0dd\ub9ac\uc2e0\ud638 \uae30\ubc18\n\uc2e4\uc2dc\uac04 \ud488\uc9c8 \ubaa8\ub2c8\ud130\ub9c1\n\u2192 Galaxy Watch \uc5f0\ub3d9",
            "AI \uccad\uac10 \ud3c9\uac00 \ud50c\ub7ab\ud3fc\n\uc790\ub3d9\ud654 \uc644\uc131\n\u2192 \ube44\uc9c0\ub3c4 \ud559\uc2b5 \ud655\uc7a5",
        ],
        [
            "Display\ud300 \ud611\uc5c5 \uc2dc\uc791\nA-V \ud1b5\ud569 \ud3c9\uac00 \uc124\uacc4\n\u2192 Visual 76% \uae30\uc5ec\ub3c4 \ud65c\uc6a9",
            "Holographic Display \u00d7\nSpatial Audio \uc2dc\ub108\uc9c0\n\u2192 cross-modal \ud6a8\uacfc \uadf9\ub300\ud654",
            "\ud06c\ub85c\uc2a4\ubaa8\ub2ec \uacbd\ud5d8 \uc124\uacc4\nLab \ube44\uc804 \uc81c\uc548\n\u2192 \ucc28\uc138\ub300 \uc81c\ud488 \uc804\ub7b5",
        ],
        [
            "Eclipsa Audio \uc778\uc99d \uae30\uc900\n\ucd08\uc548 \uc791\uc131\n\u2192 92.5% \uc608\uce21\ubaa8\ub378 \ud65c\uc6a9",
            "\uad6d\uc81c \ud45c\uc900\ud654 \uae30\uc5ec\n(IEC/ISO WG \ucc38\uc5ec)\n\u2192 SATP 18\uac1c\uad6d \ub124\ud2b8\uc6cc\ud06c",
            "\uc0bc\uc131 \uc8fc\ub3c4 \ud45c\uc900\nde facto \ud655\ub9bd\n\u2192 \uc0b0\uc5c5 \ub9ac\ub354\uc2ed \ud655\ubcf4",
        ],
    ]

    for r, (label, cells) in enumerate(zip(row_labels, grid)):
        ry = row_start + Emu(r * (int(row_h) + int(Inches(0.08))))
        # Row label (glass card)
        add_glass_card(slide, Inches(0.15), ry, label_w, row_h, shadow=False)
        add_textbox(slide, Inches(0.15), ry, label_w, row_h,
                    label, font_size=10, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # Cells (glass cards)
        for c, cell_text in enumerate(cells):
            cx = label_w + Inches(0.15) + Emu(c * (int(col_w) + int(Inches(0.12))))
            add_glass_card(slide, cx, ry, col_w, row_h, shadow=False,
                           border_color=CARD_BORDER)
            add_textbox(slide, cx + Inches(0.1), ry + Inches(0.05),
                        col_w - Inches(0.2), row_h - Inches(0.1),
                        cell_text, font_size=9, font_color=DARK_TEXT,
                        alignment=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

    # Bottom navy strip with tagline
    bar_top = Inches(6.55)
    add_rounded_rect(slide, Inches(0.15), bar_top, Inches(13.0), Inches(0.65),
                     fill_color=NAVY)
    add_textbox(slide, Inches(0.35), bar_top + Inches(0.1), Inches(12.6), Inches(0.45),
                "\uc2e0\ud638\ucc98\ub9ac\uac00 \ub9cc\ub4dc\ub294 \uae30\uc220 \uc704\uc5d0, \uc0ac\uc6a9\uc790\uac00 \uacbd\ud5d8\ud558\ub294 \ud488\uc9c8\uc744 \uc124\uacc4\ud569\ub2c8\ub2e4 "
                "\u2014 Perception-driven Spatial Audio Quality Engineering",
                font_size=12, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)


# ============================================================================
# S18: Thank You
# ============================================================================
def build_s18(prs):
    slide = add_blank_slide(prs)
    set_slide_bg(slide, MID_NAVY)

    # Gradient simulation
    add_rect(slide, 0, 0, SLIDE_WIDTH, Inches(3.75), fill_color=DEEP_NAVY)
    add_rect(slide, 0, Inches(3.75), SLIDE_WIDTH, Inches(3.75), fill_color=NAVY)

    # THANK YOU
    add_textbox(slide, Inches(0.8), Inches(2.0), Inches(11.5), Inches(1.0),
                "THANK YOU",
                font_size=40, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    add_textbox(slide, Inches(0.8), Inches(3.2), Inches(11.5), Inches(0.5),
                "\uacbd\uccad\ud574 \uc8fc\uc154\uc11c \uac10\uc0ac\ud569\ub2c8\ub2e4. \uc9c8\ubb38 \ubd80\ud0c1\ub4dc\ub9bd\ub2c8\ub2e4.",
                font_size=14, font_color=WARM_GRAY, bold=False,
                alignment=PP_ALIGN.CENTER)

    # Accent line
    line_w = Inches(3.3)
    line_l = Emu((int(SLIDE_WIDTH) - int(line_w)) // 2)
    add_rounded_rect(slide, line_l, Inches(4.0), line_w, Inches(0.04),
                     fill_color=ACCENT_BLUE)

    # Glass contact card
    card_w = Inches(7.0)
    card_h = Inches(1.6)
    card_l = Emu((int(SLIDE_WIDTH) - int(card_w)) // 2)
    card_t = Inches(4.3)
    add_glass_card(slide, card_l, card_t, card_w, card_h,
                   fill_color=RGBColor(0x1A, 0x30, 0xA5),
                   border_color=RGBColor(0x4D, 0x6D, 0xCC),
                   shadow=False)

    add_textbox(slide, card_l, card_t + Inches(0.15), card_w, Inches(0.4),
                "\uc870\ud604\uc778 (Hyun In Jo, Ph.D.)",
                font_size=14, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)

    add_textbox(slide, card_l, card_t + Inches(0.55), card_w, Inches(0.35),
                "Samsung Research \u00B7 Visual Technology \u00B7 Display Innovation Lab \u00B7 Spatial Audio",
                font_size=10, font_color=RGBColor(0xB0, 0xC4, 0xEE),
                alignment=PP_ALIGN.CENTER)

    add_textbox(slide, card_l, card_t + Inches(0.95), card_w, Inches(0.35),
                "best2012@naver.com  |  010-6387-8402  |  linkedin.com/in/hyunin-jo",
                font_size=10, font_color=WARM_GRAY, bold=False,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)


# ============================================================================
# Main
# ============================================================================
def main():
    prs = new_presentation()

    builders = [
        build_s1, build_s2, build_s3, build_s4, build_s5, build_s6,
        build_s7, build_s8, build_s9, build_s10, build_s11, build_s12,
        build_s13, build_s14, build_s15, build_s16, build_s17, build_s18,
    ]

    for fn in builders:
        fn(prs)

    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            "Portfolio_HyunInJo_v2.pptx")
    prs.save(out_path)
    print(f"Saved: {out_path} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
