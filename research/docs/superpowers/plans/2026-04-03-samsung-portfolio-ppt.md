# Samsung Research Portfolio PPT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an 18-slide portfolio PPT for Samsung Research Spatial Audio 1st interview using python-pptx, with images extracted from existing PPT and research papers.

**Architecture:** A modular Python build system: `pptx_helpers.py` defines the Samsung design system (colors, fonts, reusable layout functions), `extract_images.py` pulls figures from existing PPT/PDF sources into `assets/`, and `build_pptx.py` assembles all 18 slides using helpers and extracted assets. Each task adds a slide group and can be verified by opening the intermediate `.pptx`.

**Tech Stack:** python-pptx, pdf2image (poppler), Pillow, Python 3.9+

---

### Task 1: Design System Helpers

**Files:**
- Create: `/Users/hyunbin/Research/scripts/pptx_helpers.py`

- [ ] **Step 1: Create scripts directory and helpers module**

```python
# /Users/hyunbin/Research/scripts/pptx_helpers.py
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# === Samsung Design System ===
NAVY = RGBColor(0x13, 0x28, 0x9F)
ACCENT_BLUE = RGBColor(0x3D, 0x7D, 0xDE)
SKY_BLUE = RGBColor(0x06, 0x89, 0xD8)
DARK_TEXT = RGBColor(0x1A, 0x1A, 0x2E)
GRAY = RGBColor(0x5B, 0x71, 0x8D)
GRAY2 = RGBColor(0x75, 0x78, 0x7B)
LIGHT_BG = RGBColor(0xF0, 0xF4, 0xF8)
WARM_GRAY = RGBColor(0xE7, 0xE6, 0xE2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)

# Slide dimensions (16:9)
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# Margins
MARGIN_L = Inches(0.6)
MARGIN_R = Inches(0.6)
MARGIN_T = Inches(0.5)
CONTENT_W = SLIDE_W - MARGIN_L - MARGIN_R

# Font names
FONT_TITLE = "Pretendard"    # fallback: "맑은 고딕"
FONT_BODY = "Pretendard"
FONT_EN = "Segoe UI"


def new_presentation():
    """Create a blank 16:9 presentation."""
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def add_blank_slide(prs):
    """Add a blank slide layout."""
    layout = prs.slide_layouts[6]  # blank
    return prs.slides.add_slide(layout)


def set_slide_bg(slide, color):
    """Set solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text,
                font_size=12, font_color=DARK_TEXT, bold=False,
                alignment=PP_ALIGN.LEFT, font_name=None,
                anchor=MSO_ANCHOR.TOP):
    """Add a textbox with styled text."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.name = font_name or FONT_BODY
    p.alignment = alignment
    tf.paragraphs[0].space_after = Pt(0)
    tf.paragraphs[0].space_before = Pt(0)
    return txBox


def add_multiline_textbox(slide, left, top, width, height, lines,
                          font_size=12, font_color=DARK_TEXT,
                          line_spacing=1.2, font_name=None,
                          alignment=PP_ALIGN.LEFT):
    """Add textbox with multiple lines (list of (text, bold, color, size) tuples)."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    for i, line_data in enumerate(lines):
        if isinstance(line_data, str):
            text, bold, color, size = line_data, False, font_color, font_size
        elif len(line_data) == 2:
            text, bold = line_data
            color, size = font_color, font_size
        elif len(line_data) == 3:
            text, bold, color = line_data
            size = font_size
        else:
            text, bold, color, size = line_data

        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = font_name or FONT_BODY
        p.alignment = alignment
        p.space_after = Pt(2)
    return txBox


def add_rect(slide, left, top, width, height, fill_color, border=False):
    """Add a filled rectangle shape."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if not border:
        shape.line.fill.background()
    return shape


def add_accent_bar(slide, top=Inches(1.0)):
    """Add the Accent Blue top bar (section divider)."""
    return add_rect(slide, MARGIN_L, top, CONTENT_W, Pt(3), ACCENT_BLUE)


def add_section_title(slide, title, subtitle=None):
    """Add section title with accent bar."""
    add_accent_bar(slide, top=Inches(0.9))
    add_textbox(slide, MARGIN_L, Inches(0.35), CONTENT_W, Inches(0.5),
                title, font_size=24, font_color=NAVY, bold=True)
    if subtitle:
        add_textbox(slide, MARGIN_L, Inches(1.05), CONTENT_W, Inches(0.4),
                    subtitle, font_size=13, font_color=GRAY)


def add_metric_card(slide, left, top, width, height,
                    number_text, label_text):
    """Add a metric highlight card (Light BG box with big number)."""
    card = add_rect(slide, left, top, width, height, LIGHT_BG)
    add_textbox(slide, left + Inches(0.15), top + Inches(0.1),
                width - Inches(0.3), Inches(0.6),
                number_text, font_size=28, font_color=NAVY, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, left + Inches(0.15), top + Inches(0.65),
                width - Inches(0.3), Inches(0.5),
                label_text, font_size=10, font_color=GRAY,
                alignment=PP_ALIGN.CENTER)
    return card


def add_implication_box(slide, left, top, width, height, lines):
    """Add Navy background implication box with white text."""
    box = add_rect(slide, left, top, width, height, NAVY)
    add_multiline_textbox(slide, left + Inches(0.2), top + Inches(0.1),
                          width - Inches(0.4), height - Inches(0.2),
                          lines, font_size=11, font_color=WHITE)
    return box


def add_image_safe(slide, image_path, left, top, width=None, height=None):
    """Add image to slide, with error handling for missing files."""
    import os
    if not os.path.exists(image_path):
        # Add placeholder rect with text
        w = width or Inches(4)
        h = height or Inches(3)
        add_rect(slide, left, top, w, h, LIGHT_BG)
        add_textbox(slide, left, top + h // 2 - Inches(0.2), w, Inches(0.4),
                    f"[Image: {os.path.basename(image_path)}]",
                    font_size=10, font_color=GRAY, alignment=PP_ALIGN.CENTER)
        return None
    kwargs = {"left": left, "top": top}
    if width:
        kwargs["width"] = width
    if height:
        kwargs["height"] = height
    return slide.shapes.add_picture(image_path, **kwargs)
```

- [ ] **Step 2: Verify module imports correctly**

Run: `cd /Users/hyunbin/Research && python3 -c "from scripts.pptx_helpers import *; prs = new_presentation(); print(f'Slide size: {prs.slide_width}x{prs.slide_height}')"`

Expected: `Slide size: 12192000x6858000`

- [ ] **Step 3: Commit**

```bash
git add scripts/pptx_helpers.py
git commit -m "feat: add python-pptx design system helpers for Samsung brand"
```

---

### Task 2: Extract Images from Existing Sources

**Files:**
- Create: `/Users/hyunbin/Research/scripts/extract_images.py`
- Create: `/Users/hyunbin/Research/assets/` (directory for extracted images)

- [ ] **Step 1: Create image extraction script**

```python
# /Users/hyunbin/Research/scripts/extract_images.py
"""
Extract figures from existing PPT and PDF sources for portfolio slides.
Outputs images to /Users/hyunbin/Research/assets/
"""
import os
import sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

ASSETS_DIR = "/Users/hyunbin/Research/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# === 1. Extract from existing Portfolio PPT ===
def extract_pptx_images(pptx_path, slide_indices, prefix):
    """Extract all images from specified slides of a PPTX file."""
    prs = Presentation(pptx_path)
    extracted = []
    for idx in slide_indices:
        slide = prs.slides[idx - 1]  # 1-indexed
        img_count = 0
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                img_count += 1
                blob = shape.image.blob
                ext = shape.image.content_type.split("/")[-1]
                if ext == "jpeg":
                    ext = "jpg"
                fname = f"{prefix}_s{idx}_img{img_count}.{ext}"
                fpath = os.path.join(ASSETS_DIR, fname)
                with open(fpath, "wb") as f:
                    f.write(blob)
                extracted.append(fpath)
                print(f"  Extracted: {fname} ({len(blob)} bytes)")
    return extracted


# === 2. Extract from PDF papers ===
def extract_pdf_pages(pdf_path, pages, prefix, dpi=200):
    """Render specific pages from a PDF as images."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("  pdf2image not installed, installing...")
        os.system(f"{sys.executable} -m pip install pdf2image")
        from pdf2image import convert_from_path

    extracted = []
    images = convert_from_path(pdf_path, dpi=dpi, first_page=min(pages),
                               last_page=max(pages))
    for i, page_num in enumerate(pages):
        page_idx = page_num - min(pages)
        if page_idx < len(images):
            fname = f"{prefix}_p{page_num}.png"
            fpath = os.path.join(ASSETS_DIR, fname)
            images[page_idx].save(fpath, "PNG")
            extracted.append(fpath)
            print(f"  Extracted: {fname}")
    return extracted


def main():
    print("=== Extracting images from existing Portfolio PPT ===")
    portfolio_path = "/Users/hyunbin/Research/Portfolio_HyunInJo.pptx"

    # S5 diagram (Pleasant-Eventful model) - from prototype slide 5
    extract_pptx_images(portfolio_path, [5], "proto")

    # S9 HRTF result figures - from prototype slides 10, 11, 18
    extract_pptx_images(portfolio_path, [10, 11, 18], "proto")

    # S15 Research overview images - from prototype slide 15
    extract_pptx_images(portfolio_path, [15], "proto")

    # S16 AI figures - from prototype slides 24, 25
    extract_pptx_images(portfolio_path, [24, 25], "proto")

    print("\n=== Extracting from HMG PPT ===")
    hmg_path = "/Users/hyunbin/Research/ETC/HMG 학술대회 발표자료_AVAS_사운드스케이프_MSV소음진동시험팀_조현인책임_충남대공유용.pptx"
    # AVAS PCA chart, brand positioning, production process
    extract_pptx_images(hmg_path, [10, 11, 12, 13, 17], "hmg")

    print("\n=== Extracting pages from research papers ===")
    paper_dir = "/Users/hyunbin/Research/Paper"

    # APAC_2022 - HMD vs Monitor results (figures typically in pages 5-8)
    extract_pdf_pages(
        f"{paper_dir}/APAC_2022_Jo&Jeon_Perception of urban soundscape and landscape using different visual environment reproduction methods in virtual reality.pdf",
        [5, 6, 7, 8], "apac2022"
    )

    # B&E_2020 - Audio-Visual satisfaction model (figures in later pages)
    extract_pdf_pages(
        f"{paper_dir}/B&E_2020_Jeon&Jo_Effects of audio-visual interactions on soundscape and landscape perception and their influence on satisfaction with the ur.pdf",
        [6, 7, 8, 9, 10], "be2020"
    )

    # SCS_2021 - VR vs In-situ comparison (appendix)
    extract_pdf_pages(
        f"{paper_dir}/SCS_2021_Jo&Jeon_Compatibility of quantitative and qualitative data-collection protocols for urban soundscape evaluation.pdf",
        [4, 5, 15, 16, 17], "scs2021"
    )

    # SCS_2023 - HRV results
    extract_pdf_pages(
        f"{paper_dir}/SCS_2023_Jeon et al_Psycho-physiological restoration with audio-visual interactions through virtual reality simulations of soundscape and land.pdf",
        [7, 8, 9, 10, 11], "scs2023"
    )

    # IJERPH_2024 - Eye-tracking heatmap
    extract_pdf_pages(
        f"{paper_dir}/IJERPH_2024_Jo&Jeon_Quantification of visual attention by using eye-tracking technology for soundscape assessment through physiological response.pdf",
        [4, 5, 6, 7], "ijerph2024"
    )

    # B&E_2021 - SEM model
    extract_pdf_pages(
        f"{paper_dir}/B&E_2021_Jo&Jeon_Overall environmental assessment in urban park_Modelling audio-visual interaction with a structural equation model based on.pdf",
        [8, 9, 10, 11], "be2021"
    )

    # SENSORS_2021 - LSTM architecture + ROC curve
    extract_pdf_pages(
        f"{paper_dir}/SENSORS_2021_Chung et al_Diagnosis of pneumonia by cough sounds analyzed with statistical features and AI.pdf",
        [3, 4, 5, 6, 7], "sensors2021"
    )

    # B&E_2019_Jeon&Jo - HRTF contribution
    extract_pdf_pages(
        f"{paper_dir}/B&E_2019_Jeon&Jo_Three-dimensional virtual reality-based subjective evaluation of road traffic noise in urban high-rise residential buildings.pdf",
        [5, 6, 7, 8, 9, 10], "be2019a"
    )

    print(f"\n=== Done. Total files in assets: {len(os.listdir(ASSETS_DIR))} ===")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run extraction script**

Run: `cd /Users/hyunbin/Research && python3 scripts/extract_images.py`

Expected: Multiple "Extracted: ..." lines, ending with total file count.

- [ ] **Step 3: Verify assets directory has images**

Run: `ls -la /Users/hyunbin/Research/assets/ | head -20`

Expected: PNG and image files from both PPT and PDF sources.

- [ ] **Step 4: Commit**

```bash
git add scripts/extract_images.py
git commit -m "feat: add image extraction script for portfolio figures"
```

---

### Task 3: Build S1-S3 (Intro Slides)

**Files:**
- Create: `/Users/hyunbin/Research/scripts/build_pptx.py`

- [ ] **Step 1: Create build script with intro slides**

```python
# /Users/hyunbin/Research/scripts/build_pptx.py
"""
Build Samsung Research Portfolio PPT (18 slides).
Run: python3 scripts/build_pptx.py
Output: /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from pptx_helpers import *

ASSETS = "/Users/hyunbin/Research/assets"
OUTPUT = "/Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx"


def build_s1_title(prs):
    """S1: Title Slide - Navy full background."""
    slide = add_blank_slide(prs)
    set_slide_bg(slide, NAVY)

    # Title
    add_textbox(slide, MARGIN_L, Inches(2.0), CONTENT_W, Inches(1.2),
                "Spatial Audio Research &\nPerception-driven Quality Evaluation",
                font_size=32, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.LEFT, font_name=FONT_EN)

    # Name
    add_multiline_textbox(slide, MARGIN_L, Inches(3.8), CONTENT_W, Inches(1.0), [
        ("조현인 (Hyun In Jo, Ph.D.)", True, WHITE, 14),
        ("Senior Research Engineer, Hyundai Motor Company (NVH Division)", False, WARM_GRAY, 11),
    ])

    # Org path
    add_textbox(slide, MARGIN_L, Inches(5.2), CONTENT_W, Inches(0.4),
                "Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio",
                font_size=11, font_color=WARM_GRAY, font_name=FONT_EN)

    # Contact
    add_textbox(slide, MARGIN_L, Inches(5.7), CONTENT_W, Inches(0.3),
                "best2012@naver.com  |  010-6387-8402  |  linkedin.com/in/hyunin-jo",
                font_size=10, font_color=WARM_GRAY, font_name=FONT_EN)

    # Top accent line
    add_rect(slide, MARGIN_L, Inches(1.7), Inches(2.0), Pt(3), ACCENT_BLUE)


def build_s2_about_me(prs):
    """S2: About Me - Timeline + Metrics + 4 Competencies."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "About Me",
                      "조현인 (Hyun In Jo, Ph.D.) — 경력 · 핵심 실적 · 전문성")

    # === Left: Career Timeline ===
    timeline_items = [
        ("2013–2016", "B.S. 건축공학, 한양대학교 (수석졸업, 조기졸업)"),
        ("2016–2022", "Ph.D. 건축음향, 한양대학교 (석박통합, GPA 4.39/4.5)"),
        ("2022.03–08", "Post-doc, 한국건설기술연구원"),
        ("2022.08–현재", "현대자동차 NVH 책임연구원, 남양연구소"),
        ("NOW →", "Samsung Research, Spatial Audio"),
    ]
    y = Inches(1.6)
    for period, desc in timeline_items:
        # Period (bold, navy)
        add_textbox(slide, MARGIN_L, y, Inches(1.5), Inches(0.25),
                    period, font_size=9, font_color=NAVY, bold=True)
        # Desc
        add_textbox(slide, Inches(2.2), y, Inches(3.5), Inches(0.25),
                    desc, font_size=9, font_color=DARK_TEXT)
        # Dot
        add_rect(slide, Inches(2.05), y + Pt(4), Pt(6), Pt(6), ACCENT_BLUE)
        # Line
        if period != "NOW →":
            add_rect(slide, Inches(2.07), y + Pt(12), Pt(2), Inches(0.22), WARM_GRAY)
        y += Inches(0.32)

    # === Right: Metric Cards ===
    card_data = [
        ("SCI(E) 24편", "주저자 21편, h-index 18"),
        ("EAA Best Paper", "ICA 2019, I-INCE Young Professional"),
        ("특허 6건", "국내+미국, 기술이전 5천만원"),
        ("국제공동연구", "UCL·소르본, SATP 18개국 표준화"),
    ]
    cx = Inches(6.5)
    cy = Inches(1.6)
    cw = Inches(2.8)
    ch = Inches(1.0)
    for num_text, label_text in card_data:
        add_metric_card(slide, cx, cy, cw, ch, num_text, label_text)
        cy += Inches(1.15)

    # === Bottom: 4 Core Competencies ===
    comp_y = Inches(5.8)
    comp_w = Inches(2.8)
    competencies = [
        ("Part I", "Spatial Audio &\nImmersive Rendering"),
        ("Part II", "Perception-driven\nQuality Evaluation"),
        ("Part III", "Research-to-Product\nExecution"),
        ("Part IV", "AI-driven\nAudio Processing"),
    ]
    for i, (part, name) in enumerate(competencies):
        x = MARGIN_L + i * (comp_w + Inches(0.2))
        add_rect(slide, x, comp_y, comp_w, Inches(0.8), LIGHT_BG)
        add_textbox(slide, x + Inches(0.1), comp_y + Inches(0.05),
                    comp_w - Inches(0.2), Inches(0.2),
                    part, font_size=8, font_color=ACCENT_BLUE, bold=True)
        add_textbox(slide, x + Inches(0.1), comp_y + Inches(0.28),
                    comp_w - Inches(0.2), Inches(0.45),
                    name, font_size=10, font_color=DARK_TEXT, bold=True)


def build_s3_key_question(prs):
    """S3: Key Question - Problem statement + 4 Part roadmap."""
    slide = add_blank_slide(prs)

    # Problem statement (top)
    add_textbox(slide, MARGIN_L, Inches(0.8), CONTENT_W, Inches(0.8),
                "THD 0.01%, 주파수 응답 ±0.5dB —\n공학 스펙이 완벽해도 사용자가 \"좋다\"고 느끼지 않을 수 있다",
                font_size=16, font_color=GRAY, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, MARGIN_L, Inches(1.8), CONTENT_W, Inches(0.4),
                "시각 맥락만으로 오디오 만족도가 76% 좌우된다면? (본인 연구 결과)",
                font_size=14, font_color=ACCENT_BLUE, bold=True,
                alignment=PP_ALIGN.CENTER)

    # Key question (center, large)
    add_rect(slide, Inches(1.0), Inches(2.6), SLIDE_W - Inches(2.0), Inches(1.5), NAVY)
    add_textbox(slide, Inches(1.5), Inches(2.8), SLIDE_W - Inches(3.0), Inches(1.1),
                "사용자가 진짜 몰입을 느끼는\n3D Audio-Visual 경험을\n어떻게 설계하고 검증할 것인가?",
                font_size=22, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)

    # 4 Part roadmap (bottom)
    parts = [
        ("Part I", "Spatial Audio\n기술 역량", "8분"),
        ("Part II", "지각 기반\n평가 방법론", "3분"),
        ("Part III", "제품 적용\nAVAS", "3분"),
        ("Part IV", "AI 확장\n+ Contribution", "4분"),
    ]
    pw = Inches(2.6)
    py = Inches(4.8)
    for i, (part, name, time) in enumerate(parts):
        px = MARGIN_L + Inches(0.3) + i * (pw + Inches(0.3))
        add_rect(slide, px, py, pw, Inches(1.4), LIGHT_BG)
        add_textbox(slide, px + Inches(0.1), py + Inches(0.1),
                    pw - Inches(0.2), Inches(0.2),
                    part, font_size=9, font_color=ACCENT_BLUE, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, px + Inches(0.1), py + Inches(0.35),
                    pw - Inches(0.2), Inches(0.6),
                    name, font_size=12, font_color=DARK_TEXT, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, px + Inches(0.1), py + Inches(1.0),
                    pw - Inches(0.2), Inches(0.25),
                    time, font_size=9, font_color=GRAY,
                    alignment=PP_ALIGN.CENTER)
        # Arrow between parts
        if i < 3:
            arrow_x = px + pw + Inches(0.05)
            add_textbox(slide, arrow_x, py + Inches(0.5), Inches(0.2), Inches(0.3),
                        "→", font_size=16, font_color=ACCENT_BLUE, bold=True,
                        alignment=PP_ALIGN.CENTER)


def main():
    prs = new_presentation()

    build_s1_title(prs)
    build_s2_about_me(prs)
    build_s3_key_question(prs)

    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run build script and verify**

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py`

Expected: `Saved: /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx (3 slides)`

- [ ] **Step 3: Open and visually verify S1-S3**

Run: `open /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx`

Check: Navy title slide, About Me with timeline+cards, Key Question with roadmap.

- [ ] **Step 4: Commit**

```bash
git add scripts/build_pptx.py
git commit -m "feat: build S1-S3 intro slides (title, about me, key question)"
```

---

### Task 4: Build S4-S5 (Soundscape Bridge)

**Files:**
- Modify: `/Users/hyunbin/Research/scripts/build_pptx.py`

- [ ] **Step 1: Add S4-S5 builder functions**

Add the following functions to `build_pptx.py` before `main()`:

```python
def build_s4_soundscape(prs):
    """S4: What is Soundscape? - Paradigm shift + ISO definition."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "사운드스케이프란?",
                      "Noise Control → Soundscape 패러다임 전환")

    # Left: Traditional
    add_rect(slide, MARGIN_L, Inches(1.5), Inches(5.5), Inches(1.5), LIGHT_BG)
    add_textbox(slide, MARGIN_L + Inches(0.2), Inches(1.55), Inches(5.0), Inches(0.3),
                "Traditional: Noise Control", font_size=13, font_color=GRAY, bold=True)
    add_textbox(slide, MARGIN_L + Inches(0.2), Inches(1.9), Inches(5.0), Inches(0.8),
                '"소음이 얼마나 큰가?"\ndB 기반 물리적 측정, 단일 지표',
                font_size=11, font_color=DARK_TEXT)

    # Right: Soundscape
    add_rect(slide, Inches(6.8), Inches(1.5), Inches(5.8), Inches(1.5), NAVY)
    add_textbox(slide, Inches(7.0), Inches(1.55), Inches(5.4), Inches(0.3),
                "New Paradigm: Soundscape (ISO 12913)", font_size=13,
                font_color=WHITE, bold=True)
    add_textbox(slide, Inches(7.0), Inches(1.9), Inches(5.4), Inches(0.8),
                '"소리가 어떻게 경험되는가?"\n인간 지각 중심 다차원 평가\n심리음향 + 시청각 + 생리지표',
                font_size=11, font_color=WHITE)

    # Arrow between
    add_textbox(slide, Inches(5.9), Inches(1.9), Inches(0.8), Inches(0.5),
                "→", font_size=28, font_color=ACCENT_BLUE, bold=True,
                alignment=PP_ALIGN.CENTER)

    # ISO definition
    add_rect(slide, MARGIN_L, Inches(3.3), CONTENT_W, Inches(0.9), LIGHT_BG)
    add_textbox(slide, MARGIN_L + Inches(0.3), Inches(3.4), CONTENT_W - Inches(0.6), Inches(0.7),
                '"Acoustic environment as perceived or experienced\n'
                'and/or understood by a person or people, in context"\n— ISO 12913-1',
                font_size=12, font_color=DARK_TEXT, alignment=PP_ALIGN.CENTER)

    # Pleasant-Eventful diagram image
    img_path = os.path.join(ASSETS, "proto_s5_img1.png")
    add_image_safe(slide, img_path, Inches(3.0), Inches(4.4),
                   width=Inches(7.0))


def build_s5_bridge(prs):
    """S5: Why Soundscape → Spatial Audio connection table."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "왜 사운드스케이프가 Spatial Audio에 직결되는가")

    rows = [
        ("소리를 경험으로 평가\n(dB가 아닌 사용자 지각 중심 다차원 평가)",
         "렌더링 품질을 THD·주파수응답이 아닌\n사용자가 느끼는 공간감·몰입감으로 평가"),
        ("오디오-비주얼 상호작용\n(시각 맥락이 청각 지각을 최대 76% 좌우)",
         "Display + Audio 통합 설계\nHolographic Displays × Spatial Audio 시너지"),
        ("재생 환경에 따라 동일 음원의 지각 변화\n(실내/실외/공간 특성)",
         "거실·침실·차량 등 재생 공간별\n렌더링 최적화 — 같은 원리, 다른 스케일"),
        ("개인차 (소음 민감도·성격·청력 프로필)",
         "Customized Audio 개인화\n사용자별 최적 렌더링의 이론적 근거"),
        ("대규모 지각 평가 프로토콜 설계·실행\n(ISO 12913 + SATP 18개국, 134명)",
         "Eclipsa Audio 품질 벤치마킹 및\n인증 기준 수립 — 체계적 평가 설계 역량"),
    ]

    y = Inches(1.5)
    left_w = Inches(5.3)
    right_w = Inches(5.3)
    row_h = Inches(0.85)

    # Column headers
    add_textbox(slide, MARGIN_L, Inches(1.2), left_w, Inches(0.3),
                "사운드스케이프 관점", font_size=11, font_color=NAVY, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, Inches(7.0), Inches(1.2), right_w, Inches(0.3),
                "Spatial Audio 적용", font_size=11, font_color=NAVY, bold=True,
                alignment=PP_ALIGN.CENTER)

    for i, (left_text, right_text) in enumerate(rows):
        ry = y + i * (row_h + Inches(0.1))
        bg_color = LIGHT_BG if i % 2 == 0 else WHITE

        add_rect(slide, MARGIN_L, ry, left_w, row_h, bg_color)
        add_textbox(slide, MARGIN_L + Inches(0.15), ry + Inches(0.08),
                    left_w - Inches(0.3), row_h - Inches(0.16),
                    left_text, font_size=10, font_color=DARK_TEXT)

        add_textbox(slide, Inches(6.2), ry + Inches(0.2), Inches(0.6), Inches(0.4),
                    "→", font_size=16, font_color=ACCENT_BLUE, bold=True,
                    alignment=PP_ALIGN.CENTER)

        add_rect(slide, Inches(7.0), ry, right_w, row_h, bg_color)
        add_textbox(slide, Inches(7.15), ry + Inches(0.08),
                    right_w - Inches(0.3), row_h - Inches(0.16),
                    right_text, font_size=10, font_color=DARK_TEXT)

    # Bottom tagline
    add_rect(slide, MARGIN_L, Inches(6.4), CONTENT_W, Inches(0.7), NAVY)
    add_textbox(slide, MARGIN_L + Inches(0.3), Inches(6.45),
                CONTENT_W - Inches(0.6), Inches(0.6),
                '신호처리가 "어떻게 구현할 것인가"라면,\n'
                '저의 전문성은 "사용자가 어떻게 경험할 것인가"를 설계하고 검증하는 것입니다',
                font_size=13, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)
```

- [ ] **Step 2: Add S4-S5 to main() and run**

Update `main()` to add `build_s4_soundscape(prs)` and `build_s5_bridge(prs)` calls after S3.

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py`

Expected: `Saved: ... (5 slides)`

- [ ] **Step 3: Visually verify S4-S5**

Run: `open /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx`

Check: Paradigm shift layout, ISO definition, 5-row bridge table, Navy tagline box.

- [ ] **Step 4: Commit**

```bash
git add scripts/build_pptx.py
git commit -m "feat: build S4-S5 soundscape bridge slides"
```

---

### Task 5: Build S6-S11 (Part I - Spatial Audio)

**Files:**
- Modify: `/Users/hyunbin/Research/scripts/build_pptx.py`

- [ ] **Step 1: Add reusable research slide builder**

Add this helper function to `build_pptx.py`:

```python
def build_research_slide(prs, title, paper_ref, rq, metrics, result_line,
                         implication, img_path=None):
    """Generic builder for research axis slides (S7-S11 pattern).

    Args:
        title: Slide title (e.g. "축1: 시각 재현 방식의 영향")
        paper_ref: Paper reference string
        rq: Research question string
        metrics: List of (number, label) tuples for metric cards
        result_line: One-line key result string
        implication: "→ Eclipsa Audio" text
        img_path: Optional path to figure image
    """
    slide = add_blank_slide(prs)
    add_section_title(slide, title, paper_ref)

    # RQ
    add_rect(slide, MARGIN_L, Inches(1.3), CONTENT_W, Inches(0.6), LIGHT_BG)
    add_textbox(slide, MARGIN_L + Inches(0.2), Inches(1.35),
                CONTENT_W - Inches(0.4), Inches(0.5),
                f"RQ: {rq}", font_size=11, font_color=DARK_TEXT)

    # Metric cards
    num_metrics = len(metrics)
    card_w = min(Inches(2.8), (CONTENT_W - Inches(0.3) * (num_metrics - 1)) // num_metrics)
    card_h = Inches(1.1)
    card_y = Inches(2.1)
    total_cards_w = card_w * num_metrics + Inches(0.3) * (num_metrics - 1)
    start_x = MARGIN_L

    for i, (num_text, label) in enumerate(metrics):
        cx = start_x + i * (card_w + Inches(0.3))
        add_metric_card(slide, cx, card_y, card_w, card_h, num_text, label)

    # Result line
    add_textbox(slide, MARGIN_L, Inches(3.4), CONTENT_W, Inches(0.4),
                result_line, font_size=12, font_color=DARK_TEXT, bold=True)

    # Image (if provided)
    if img_path:
        add_image_safe(slide, img_path, MARGIN_L, Inches(3.9),
                       width=Inches(6.0), height=Inches(2.5))

    # Implication box
    impl_y = Inches(6.5) if img_path else Inches(4.2)
    add_implication_box(slide, MARGIN_L, impl_y, CONTENT_W, Inches(0.7),
                        [f"→ Eclipsa Audio: {implication}"])

    return slide
```

- [ ] **Step 2: Add S6 Overview slide**

```python
def build_s6_overview(prs):
    """S6: Spatial Audio Research Overview - 5 axes diagram."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "Part I. Spatial Audio 기술 역량",
                      "5개 기술 축 연구 체계도")

    # Central label
    add_rect(slide, Inches(4.5), Inches(1.8), Inches(4.5), Inches(0.6), NAVY)
    add_textbox(slide, Inches(4.7), Inches(1.85), Inches(4.1), Inches(0.5),
                "Spatial Audio Perception Research",
                font_size=14, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)

    # 5 axis cards
    axes = [
        ("축1", "시각 재현\n방식 영향", "APAC'22"),
        ("축2", "재생 방식\n영향", "APAC'19"),
        ("축3", "바이노럴-비주얼\n상호작용", "B&E'19 ×2"),
        ("축4", "시청각 정보\n영향", "B&E'20"),
        ("축5", "생태학적\n타당성", "SCS'21"),
    ]
    aw = Inches(2.2)
    ah = Inches(1.8)
    ay = Inches(3.2)
    total_w = aw * 5 + Inches(0.25) * 4
    start_x = (SLIDE_W - total_w) // 2

    for i, (num, name, ref) in enumerate(axes):
        ax = start_x + i * (aw + Inches(0.25))
        add_rect(slide, ax, ay, aw, ah, LIGHT_BG)
        add_textbox(slide, ax + Inches(0.1), ay + Inches(0.1),
                    aw - Inches(0.2), Inches(0.25),
                    num, font_size=10, font_color=ACCENT_BLUE, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, ax + Inches(0.1), ay + Inches(0.4),
                    aw - Inches(0.2), Inches(0.7),
                    name, font_size=12, font_color=DARK_TEXT, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, ax + Inches(0.1), ay + Inches(1.2),
                    aw - Inches(0.2), Inches(0.3),
                    ref, font_size=9, font_color=GRAY,
                    alignment=PP_ALIGN.CENTER)
        # Connector line to center
        add_rect(slide, ax + aw // 2 - Pt(1), Inches(2.4), Pt(2), Inches(0.8),
                 ACCENT_BLUE)

    # Bottom summary
    add_textbox(slide, MARGIN_L, Inches(5.5), CONTENT_W, Inches(0.5),
                "VR 환경에서 Spatial Audio의 각 기술 요소가 사용자 지각에 미치는 영향을 체계적으로 규명",
                font_size=13, font_color=DARK_TEXT, alignment=PP_ALIGN.CENTER)
```

- [ ] **Step 3: Add S7-S11 research axis slides**

```python
def build_s7_axis1(prs):
    build_research_slide(prs,
        title="축1: 시각 재현 방식의 영향",
        paper_ref="APAC_2022_Jo&Jeon (Applied Acoustics, IF 3.4)",
        rq="같은 Spatial Audio를 HMD vs 모니터로 볼 때, 사용자 지각이 얼마나 달라지는가?",
        metrics=[
            ("40명 × 8환경", "실험 규모"),
            ("p < 0.05", "HMD에서 더 민감한 인식"),
        ],
        result_line="HMD = 공간 현실감↑ / 모니터 = 전반적 인식↑ → 시각 재현 수준이 오디오 판단을 변화시킴",
        implication="XR 디바이스 대응 시, 시각 조건 통제가 품질 평가의 전제",
        img_path=os.path.join(ASSETS, "apac2022_p6.png"))


def build_s8_axis2(prs):
    build_research_slide(prs,
        title="축2: 헤드폰 vs 스피커",
        paper_ref="APAC_2019_Jeon et al (Applied Acoustics, IF 3.4)",
        rq="헤드폰과 스피커 재생 방식이 사용자의 소리 품질 판단을 어떻게 바꾸는가?",
        metrics=[
            ("6%", "허용한계 차이"),
            ("8%", "성가심 차이"),
            ("2.2 dBA", "50% 성가심 SPL 차이"),
        ],
        result_line="스피커+HMD 조합이 실제 환경에 가장 근접 → 가장 민감한 반응",
        implication="헤드폰(바이노럴) vs 스피커(멀티채널) 재생 시 지각 차이 정량화 기준",
        img_path=os.path.join(ASSETS, "be2019a_p7.png"))


def build_s9_axis3(prs):
    build_research_slide(prs,
        title="축3: 바이노럴-비주얼 상호작용",
        paper_ref="B&E_2019 × 2편 (Building and Environment, IF 7.4)",
        rq="HRTF와 HMD, 어느 것이 사용자 공간 지각에 더 지배적인가?",
        metrics=[
            ("HRTF 77%", "공간감의 지배적 요인"),
            ("HMD 23%", "시각 디바이스 보조 역할"),
            ("6~7 dB↓", "VR 환경 허용한계 하락"),
        ],
        result_line="HRTF+HMD 동시 적용 시 음상 외재화·몰입감 유의 증가",
        implication="HRTF 개인화 = 렌더러 최적화의 최우선 과제 (지각 기여도 77%)",
        img_path=os.path.join(ASSETS, "be2019a_p8.png"))


def build_s10_axis4(prs):
    build_research_slide(prs,
        title="축4: 시청각 정보의 지각 영향",
        paper_ref="B&E_2020_Jeon&Jo (Building and Environment, IF 7.4)",
        rq="Audio와 Visual 정보가 전체 만족도에 각각 얼마나 기여하는가?",
        metrics=[
            ("청각 24%", "만족도 기여 (Audio)"),
            ("시각 76%", "만족도 기여 (Visual)"),
            ("설명력 51%", "만족도 모델"),
        ],
        result_line="오디오가 landscape 자연스러움 지각에도 영향 (cross-modal effect)",
        implication="Display + Audio 통합 설계가 만족도 극대화의 핵심 → Holographic Displays 시너지",
        img_path=os.path.join(ASSETS, "be2020_p8.png"))


def build_s11_axis5(prs):
    build_research_slide(prs,
        title="축5: 생태학적 타당성 (In-situ vs VR)",
        paper_ref="SCS_2021_Jo&Jeon (Sustainable Cities and Society, IF 11.7)",
        rq="VR 실험실 평가 결과를 실제 현장(in-situ)과 동일하게 신뢰할 수 있는가?",
        metrics=[
            ("50명 × 10환경", "실험 규모"),
            ("3 프로토콜", "ISO 12913-2 A/B/C"),
            ("VR ≈ In-situ", "유사 결과 확인"),
        ],
        result_line="FOA 바이노럴 + 헤드트래킹의 높은 생태학적 타당성 실증",
        implication="VR 기반 실험실에서 렌더링 품질 평가 → 실사용 환경 결과를 신뢰할 수 있음",
        img_path=os.path.join(ASSETS, "scs2021_p5.png"))
```

- [ ] **Step 4: Add S6-S11 to main() and run**

Update `main()` to call all six functions after S5.

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py`

Expected: `Saved: ... (11 slides)`

- [ ] **Step 5: Visually verify Part I slides**

Run: `open /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx`

Check: Overview diagram, 5 research axis slides with metric cards + images + implication boxes.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_pptx.py
git commit -m "feat: build S6-S11 Spatial Audio research slides (Part I)"
```

---

### Task 6: Build S12-S13 (Part II - Perception)

**Files:**
- Modify: `/Users/hyunbin/Research/scripts/build_pptx.py`

- [ ] **Step 1: Add S12-S13 builder functions**

```python
def build_s12_multimodal(prs):
    """S12: Multimodal Biosignal Modeling - EEG/HRV/Eye-tracking."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "Part II. 멀티모달 생리반응 모델링",
                      "SCS_2023 (IF 11.7, 교신저자) + SR_2022 + IJERPH_2024")

    # Experiment info
    add_textbox(slide, MARGIN_L, Inches(1.3), CONTENT_W, Inches(0.4),
                "60명 × 9환경 × 2일  |  EEG (32ch) · HRV (5지표) · Eye-tracking  |  FOA + HMD + 헤드트래킹",
                font_size=11, font_color=GRAY)

    # 4 Metric cards
    metrics = [
        ("CCA 0.80", "물리음향 ↔ 심리반응"),
        ("CCA 0.78", "지각품질 ↔ 심리반응"),
        ("SDNN +14.6%", "스트레스 저항력↑"),
        ("TSI -9.5%", "스트레스 지수↓"),
    ]
    cw = Inches(2.7)
    cy = Inches(1.9)
    for i, (num, label) in enumerate(metrics):
        cx = MARGIN_L + i * (cw + Inches(0.25))
        add_metric_card(slide, cx, cy, cw, Inches(1.1), num, label)

    # Figure area
    img1 = os.path.join(ASSETS, "scs2023_p9.png")
    img2 = os.path.join(ASSETS, "ijerph2024_p5.png")
    add_image_safe(slide, img1, MARGIN_L, Inches(3.3),
                   width=Inches(5.5), height=Inches(2.2))
    add_image_safe(slide, img2, Inches(6.8), Inches(3.3),
                   width=Inches(5.5), height=Inches(2.2))

    # Implication
    add_implication_box(slide, MARGIN_L, Inches(5.8), CONTENT_W, Inches(1.2), [
        ("→ EEG/HRV 프로토콜 → 렌더링 품질 객관 검증 (설문 의존 탈피)", False, WHITE, 10),
        ("→ 물리 파라미터 → 지각 예측 모델 → 렌더링 자동 최적화 기초", False, WHITE, 10),
        ("→ A-V 일치 시 회복 효과 → Display+Audio 통합의 생리적 근거", False, WHITE, 10),
    ])


def build_s13_soundscape_design(prs):
    """S13: Soundscape Design Application - SEM model."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "사운드스케이프 디자인 응용",
                      "B&E_2021 + B&E_2022 (Building and Environment, IF 7.4)")

    # RQ
    add_rect(slide, MARGIN_L, Inches(1.3), CONTENT_W, Inches(0.6), LIGHT_BG)
    add_textbox(slide, MARGIN_L + Inches(0.2), Inches(1.35),
                CONTENT_W - Inches(0.4), Inches(0.5),
                "RQ: 오디오-비주얼 상호작용이 실내 환경의 업무 품질과 생산성에 미치는 영향은?",
                font_size=11, font_color=DARK_TEXT)

    # Results
    add_textbox(slide, MARGIN_L, Inches(2.1), CONTENT_W, Inches(0.6),
                "SEM 모델로 Audio → Visual → 만족도 경로 정량화\n"
                "A-V 일치 시 업무 선호도·생산성 유의 향상",
                font_size=12, font_color=DARK_TEXT, bold=True)

    # SEM figure
    img = os.path.join(ASSETS, "be2021_p9.png")
    add_image_safe(slide, img, Inches(2.0), Inches(2.9),
                   width=Inches(9.0), height=Inches(3.0))

    # Implication
    add_implication_box(slide, MARGIN_L, Inches(6.2), CONTENT_W, Inches(0.8), [
        ("→ Eclipsa Audio: TV·사운드바가 놓이는 실내 환경별 최적 렌더링 설계의 이론적 근거",
         False, WHITE, 11),
    ])
```

- [ ] **Step 2: Add to main() and run**

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py`

Expected: `Saved: ... (13 slides)`

- [ ] **Step 3: Commit**

```bash
git add scripts/build_pptx.py
git commit -m "feat: build S12-S13 perception methodology slides (Part II)"
```

---

### Task 7: Build S14-S15 (Part III - AVAS)

**Files:**
- Modify: `/Users/hyunbin/Research/scripts/build_pptx.py`

- [ ] **Step 1: Add S14-S15 builder functions**

```python
def build_s14_avas(prs):
    """S14: AVAS Soundscape Design."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "Part III. AVAS 사운드스케이프 디자인",
                      "HMG 학술대회 특별상 + JASA 논문 (심사 중)")

    # Background
    add_textbox(slide, MARGIN_L, Inches(1.3), CONTENT_W, Inches(0.5),
                "EV 시대 → AVAS가 도시 음환경의 새로운 요소. 사운드스케이프 개념 최초 적용",
                font_size=11, font_color=GRAY)

    # Data overview
    add_textbox(slide, MARGIN_L, Inches(1.8), CONTENT_W, Inches(0.4),
                "17개 EV × 43개 AVAS 바이노럴 레코딩  |  134명 대규모 청감평가  |  3단계 감성어휘 (272→25→18쌍)",
                font_size=10, font_color=DARK_TEXT)

    # 3 Metric cards
    metrics = [
        ("Comfort–Metallic", "기존 축으로 구분 불가\n→ 신규 평가축 제안"),
        ("92.5%", "만족도 예측 정확도\n물리지표만으로 자동 예측"),
        ("34대 경쟁 DB", "전 브랜드 벤치마킹\n체계 구축"),
    ]
    cw = Inches(3.6)
    cy = Inches(2.3)
    for i, (num, label) in enumerate(metrics):
        cx = MARGIN_L + i * (cw + Inches(0.3))
        add_metric_card(slide, cx, cy, cw, Inches(1.3), num, label)

    # PCA figure
    img = os.path.join(ASSETS, "hmg_s11_img1.png")
    add_image_safe(slide, img, Inches(1.5), Inches(3.9),
                   width=Inches(5.0), height=Inches(2.3))

    # Implication
    add_implication_box(slide, Inches(7.0), Inches(3.9), Inches(5.3), Inches(2.3), [
        ("→ 물리지표→만족도 예측 → 렌더링\n   파라미터 자동 튜닝 기초", False, WHITE, 10),
        ("→ 감성 평가 프레임워크 → Eclipsa\n   vs Dolby Atmos 경쟁 분석", False, WHITE, 10),
        ("→ 134명 청감평가 역량 → 디바이스\n   품질 인증 프로세스", False, WHITE, 10),
    ])


def build_s15_execution(prs):
    """S15: Research → Production Execution."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "연구 → 양산 실행력",
                      "AVAS 브랜드 사운드 2.0 — EV3, IONIQ 5 양산 적용")

    # Process flow
    steps = ["음향 설계", "청취 평가", "시스템 검증", "양산 적용"]
    sw = Inches(2.5)
    sy = Inches(1.8)
    for i, step in enumerate(steps):
        sx = MARGIN_L + Inches(0.3) + i * (sw + Inches(0.4))
        color = NAVY if i == 3 else LIGHT_BG
        text_color = WHITE if i == 3 else DARK_TEXT
        add_rect(slide, sx, sy, sw, Inches(0.7), color)
        add_textbox(slide, sx, sy + Inches(0.15), sw, Inches(0.4),
                    step, font_size=14, font_color=text_color, bold=True,
                    alignment=PP_ALIGN.CENTER)
        if i < 3:
            add_textbox(slide, sx + sw + Inches(0.05), sy + Inches(0.1),
                        Inches(0.3), Inches(0.4),
                        "→", font_size=18, font_color=ACCENT_BLUE, bold=True)

    # Achievement cards
    achievements = [
        ("특허 6건", "국내 + 미국"),
        ("기술이전 5천만원", "실용화 실적"),
        ("HMG 특별상", "학술대회 논문상"),
        ("웹 예측 툴", "Shiny 기반 사내 적용"),
    ]
    aw = Inches(2.7)
    ay = Inches(3.0)
    for i, (title, sub) in enumerate(achievements):
        ax = MARGIN_L + i * (aw + Inches(0.25))
        add_rect(slide, ax, ay, aw, Inches(0.9), LIGHT_BG)
        add_textbox(slide, ax + Inches(0.1), ay + Inches(0.1),
                    aw - Inches(0.2), Inches(0.3),
                    title, font_size=14, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, ax + Inches(0.1), ay + Inches(0.5),
                    aw - Inches(0.2), Inches(0.3),
                    sub, font_size=10, font_color=GRAY,
                    alignment=PP_ALIGN.CENTER)

    # Production figure
    img = os.path.join(ASSETS, "hmg_s17_img1.png")
    add_image_safe(slide, img, Inches(1.0), Inches(4.2),
                   width=Inches(5.5), height=Inches(2.5))

    # SR implication
    add_implication_box(slide, Inches(7.0), Inches(4.2), Inches(5.3), Inches(2.5), [
        ("→ 선행연구 → 제품 사양 전환 →\n   개발 일정·품질 기준 조율 실행력", False, WHITE, 11),
        ("→ 디자인·법규·NVH 부서 간\n   AVAS 프로젝트 조율 → 파트 간 협업", False, WHITE, 11),
    ])
```

- [ ] **Step 2: Add to main() and run**

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py`

Expected: `Saved: ... (15 slides)`

- [ ] **Step 3: Commit**

```bash
git add scripts/build_pptx.py
git commit -m "feat: build S14-S15 AVAS product application slides (Part III)"
```

---

### Task 8: Build S16-S18 (Part IV - AI + Contribution + Thank You)

**Files:**
- Modify: `/Users/hyunbin/Research/scripts/build_pptx.py`

- [ ] **Step 1: Add S16 AI slide**

```python
def build_s16_ai(prs):
    """S16: AI-driven Audio Processing + A-JEPA vision."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "Part IV. AI 기반 오디오 처리",
                      "SENSORS_2021 (SCI) — 특허 2건, 기술이전 5천만원")

    # Problem → Solution
    add_textbox(slide, MARGIN_L, Inches(1.3), Inches(5.5), Inches(0.7),
                "문제: 학습 데이터 부족 (30명, 126건)\n"
                "해결: RIR Convolution 증강 8건 → 43,000건\n"
                "새 특징: Loudness + Energy Ratio (도메인 지식 기반)",
                font_size=10, font_color=DARK_TEXT)

    # AI vs Expert cards
    comparisons = [
        ("정확도", "AI 84.9%", "전문가 56.4%"),
        ("민감도", "AI 90.0%", "전문가 40.7%"),
        ("AUC", "AI 0.84", "전문가 0.56"),
    ]
    cw = Inches(3.5)
    cy = Inches(2.3)
    for i, (metric, ai_val, expert_val) in enumerate(comparisons):
        cx = MARGIN_L + i * (cw + Inches(0.25))
        add_rect(slide, cx, cy, cw, Inches(1.0), LIGHT_BG)
        add_textbox(slide, cx + Inches(0.1), cy + Inches(0.05),
                    cw - Inches(0.2), Inches(0.2),
                    metric, font_size=9, font_color=GRAY, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, cx + Inches(0.1), cy + Inches(0.3),
                    cw - Inches(0.2), Inches(0.3),
                    ai_val, font_size=18, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, cx + Inches(0.1), cy + Inches(0.7),
                    cw - Inches(0.2), Inches(0.2),
                    expert_val, font_size=10, font_color=GRAY,
                    alignment=PP_ALIGN.CENTER)

    # LSTM figure
    img = os.path.join(ASSETS, "sensors2021_p5.png")
    add_image_safe(slide, img, MARGIN_L, Inches(3.6),
                   width=Inches(5.5), height=Inches(2.0))

    # Eclipsa implications
    add_implication_box(slide, Inches(6.5), Inches(3.6), Inches(5.8), Inches(1.2), [
        ("→ RIR 증강 → 다양한 재생 환경 학습 데이터", False, WHITE, 10),
        ("→ 도메인+AI → 물리적 특성 반영 특징 설계", False, WHITE, 10),
        ("→ 소량→대규모 학습셋 → 빠른 모델 적응", False, WHITE, 10),
    ])

    # A-JEPA vision box
    add_rect(slide, Inches(6.5), Inches(5.0), Inches(5.8), Inches(1.5), ACCENT_BLUE)
    add_multiline_textbox(slide, Inches(6.7), Inches(5.1),
                          Inches(5.4), Inches(1.3), [
        ("A-JEPA 비전", True, WHITE, 12),
        ("Meta A-JEPA 자기지도 학습 + 음향 도메인 지식", False, WHITE, 10),
        ("→ AI 오디오 표현 ↔ 사용자 지각 대응 연구", False, WHITE, 10),
        ("→ 지능형 적응 렌더링의 기초", False, WHITE, 10),
    ])
```

- [ ] **Step 2: Add S17 Contribution Plan**

```python
def build_s17_contribution(prs):
    """S17: 3-stage Contribution Plan timeline."""
    slide = add_blank_slide(prs)
    add_section_title(slide, "Contribution Plan",
                      "삼성리서치 Spatial Audio 파트 기여 로드맵")

    # 3 timeline columns
    phases = [
        ("입사 ~6개월", "즉시 기여", ACCENT_BLUE),
        ("6개월 ~ 2년", "과제 확장", NAVY),
        ("2년~", "Lab 비전 주도", RGBColor(0x0B, 0x1D, 0x6F)),
    ]
    col_w = Inches(3.7)
    col_x_start = MARGIN_L + Inches(0.1)

    for i, (period, keyword, color) in enumerate(phases):
        cx = col_x_start + i * (col_w + Inches(0.25))
        # Header
        add_rect(slide, cx, Inches(1.3), col_w, Inches(0.6), color)
        add_textbox(slide, cx + Inches(0.1), Inches(1.33), col_w - Inches(0.2), Inches(0.25),
                    period, font_size=10, font_color=WHITE, bold=True,
                    alignment=PP_ALIGN.CENTER)
        add_textbox(slide, cx + Inches(0.1), Inches(1.58), col_w - Inches(0.2), Inches(0.25),
                    keyword, font_size=12, font_color=WHITE, bold=True,
                    alignment=PP_ALIGN.CENTER)

    # Row labels and content
    row_labels = ["Eclipsa Audio", "AI 전환", "파트 시너지", "인증·표준"]
    row_content = [
        # Eclipsa Audio
        ["TV~사운드바 지각 품질\n벤치마킹 체계 구축\nEclipsa vs Dolby Atmos 비교",
         "HRTF 바이노럴 개인화\nIAMF 2.0 지각 품질\n가이드라인",
         ""],
        # AI
        ["지각 평가 데이터 +\nAI 분석 파이프라인\nRIR 재생환경 학습데이터",
         "A-JEPA 오디오 표현학습\n재생 공간 자동 인식\n적응형 렌더링",
         "AI 기반 Customized\nAudio 개인화 시스템"],
        # Synergy
        ["Holographic Displays\n통합 A-V 지각 실험",
         "3D 시각 + Spatial Audio\n동기화 프로토콜",
         "Lab 통합 비전:\n홀로그래픽+공간오디오\n설계 가이드라인 주도"],
        # Standards
        ["THX/TTA 인증\n지각 평가 데이터 제공",
         "사내 오디오 품질 인증\n프로그램 체계화",
         "국제 표준화 활동\n(ISO/SATP 경험)"],
    ]

    ry = Inches(2.1)
    rh = Inches(1.1)
    label_w = Inches(1.3)

    for r, label in enumerate(row_labels):
        row_y = ry + r * (rh + Inches(0.1))
        # Row label
        add_rect(slide, MARGIN_L, row_y, label_w, rh, LIGHT_BG)
        add_textbox(slide, MARGIN_L + Inches(0.05), row_y + Inches(0.1),
                    label_w - Inches(0.1), rh - Inches(0.2),
                    label, font_size=8, font_color=NAVY, bold=True,
                    alignment=PP_ALIGN.CENTER)
        # 3 cells
        for c in range(3):
            cell_x = col_x_start + c * (col_w + Inches(0.25))
            add_textbox(slide, cell_x + Inches(0.1), row_y + Inches(0.05),
                        col_w - Inches(0.2), rh - Inches(0.1),
                        row_content[r][c], font_size=8, font_color=DARK_TEXT)

    # Bottom quote
    add_rect(slide, MARGIN_L, Inches(6.6), CONTENT_W, Inches(0.6), NAVY)
    add_textbox(slide, MARGIN_L + Inches(0.3), Inches(6.65),
                CONTENT_W - Inches(0.6), Inches(0.5),
                "신호처리가 만드는 기술 위에, 사용자가 경험하는 품질을 설계합니다",
                font_size=14, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)
```

- [ ] **Step 3: Add S18 Thank You**

```python
def build_s18_thankyou(prs):
    """S18: Thank You - Navy background, mirror of S1."""
    slide = add_blank_slide(prs)
    set_slide_bg(slide, NAVY)

    add_textbox(slide, MARGIN_L, Inches(2.0), CONTENT_W, Inches(0.8),
                "THANK YOU",
                font_size=36, font_color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER, font_name=FONT_EN)

    add_textbox(slide, MARGIN_L, Inches(3.0), CONTENT_W, Inches(0.5),
                "경청해 주셔서 감사합니다. 질문 부탁드립니다.",
                font_size=14, font_color=WARM_GRAY,
                alignment=PP_ALIGN.CENTER)

    # Accent line
    add_rect(slide, Inches(5.0), Inches(3.8), Inches(3.3), Pt(3), ACCENT_BLUE)

    add_multiline_textbox(slide, MARGIN_L, Inches(4.2), CONTENT_W, Inches(1.5), [
        ("조현인 (Hyun In Jo, Ph.D.)", True, WHITE, 14),
        ("best2012@naver.com  |  010-6387-8402", False, WARM_GRAY, 11),
        ("linkedin.com/in/hyunin-jo", False, WARM_GRAY, 11),
        ("Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio",
         False, WARM_GRAY, 10),
    ], alignment=PP_ALIGN.CENTER)
```

- [ ] **Step 4: Update main() with all 18 slides**

```python
def main():
    prs = new_presentation()

    # Intro
    build_s1_title(prs)
    build_s2_about_me(prs)
    build_s3_key_question(prs)
    # Bridge
    build_s4_soundscape(prs)
    build_s5_bridge(prs)
    # Part I: Spatial Audio
    build_s6_overview(prs)
    build_s7_axis1(prs)
    build_s8_axis2(prs)
    build_s9_axis3(prs)
    build_s10_axis4(prs)
    build_s11_axis5(prs)
    # Part II: Perception
    build_s12_multimodal(prs)
    build_s13_soundscape_design(prs)
    # Part III: AVAS
    build_s14_avas(prs)
    build_s15_execution(prs)
    # Part IV: AI + Contribution
    build_s16_ai(prs)
    build_s17_contribution(prs)
    build_s18_thankyou(prs)

    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT} ({len(prs.slides)} slides)")
```

- [ ] **Step 5: Run full build**

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py`

Expected: `Saved: /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx (18 slides)`

- [ ] **Step 6: Visually verify all 18 slides**

Run: `open /Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx`

Check: All 18 slides present, Navy theme consistent, metric cards visible, images loaded (or placeholders shown).

- [ ] **Step 7: Commit**

```bash
git add scripts/build_pptx.py
git commit -m "feat: complete all 18 slides (AI, contribution plan, thank you)"
```

---

### Task 9: Polish and Final Review

**Files:**
- Modify: `/Users/hyunbin/Research/scripts/build_pptx.py`
- Modify: `/Users/hyunbin/Research/scripts/extract_images.py` (if image paths need adjustment)

- [ ] **Step 1: Review each slide for visual issues**

Open the PPTX in PowerPoint/Keynote and check:
- Text overflow or truncation on any slide
- Image positioning and sizing
- Color consistency (Navy, Accent Blue, Light BG)
- Font rendering (Pretendard fallback to 맑은 고딕 if needed)

- [ ] **Step 2: Fix any font fallback issues**

If Pretendard is not installed, update `pptx_helpers.py`:

```python
# Check if Pretendard is available, fallback to system fonts
import subprocess
result = subprocess.run(["fc-list", ":family"], capture_output=True, text=True)
if "Pretendard" in result.stdout:
    FONT_TITLE = "Pretendard"
    FONT_BODY = "Pretendard"
else:
    FONT_TITLE = "맑은 고딕"
    FONT_BODY = "맑은 고딕"
```

- [ ] **Step 3: Adjust image paths based on actual extracted files**

Run: `ls /Users/hyunbin/Research/assets/`

Compare actual filenames with paths used in `build_pptx.py`. Update any mismatches.

- [ ] **Step 4: Rebuild and final verify**

Run: `cd /Users/hyunbin/Research && python3 scripts/build_pptx.py && open Portfolio_HyunInJo_v2.pptx`

- [ ] **Step 5: Commit final version**

```bash
git add scripts/ assets/
git commit -m "feat: finalize Samsung Research portfolio PPT v2 (18 slides)"
```
