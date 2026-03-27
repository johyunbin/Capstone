#!/usr/bin/env python3
"""
md2pdf.py — Markdown → PDF 변환 스크립트
사용법: python3 scripts/md2pdf.py Research/문서이름.md
출력:   Research/문서이름.pdf (같은 디렉토리)
폰트:   NanumSquare OTF (고정)
"""

import re
import sys
import os
from fpdf import FPDF

# ─── 폰트 설정 (NanumSquare OTF 고정) ───
FONT_REGULAR = os.path.expanduser("~/Library/Fonts/NanumSquareOTF_acR.otf")
FONT_BOLD = os.path.expanduser("~/Library/Fonts/NanumSquareOTF_acB.otf")
FONT_NAME = "Nanum"


# ─── PDF 클래스 ───
class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.font_name = FONT_NAME
        self.add_font(FONT_NAME, "", FONT_REGULAR)
        self.add_font(FONT_NAME, "B", FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=20)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"{self.page_no()}", align="C")

    # ─── 텍스트 출력 헬퍼 ───
    def title_text(self, text):
        self.set_font(self.font_name, "B", 16)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, text, align="C")
        self.ln(4)

    def h2(self, text):
        self.ln(4)
        self.set_font(self.font_name, "B", 13)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 8, text)
        self.ln(2)

    def h3(self, text):
        self.ln(3)
        self.set_font(self.font_name, "B", 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 7, text)
        self.ln(1)

    def h4(self, text):
        self.ln(2)
        self.set_font(self.font_name, "B", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, text)
        self.ln(1)

    def body(self, text):
        self.set_font(self.font_name, "", 9.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def bold_body(self, text):
        self.set_font(self.font_name, "B", 9.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def blockquote(self, text):
        self.set_font(self.font_name, "", 9.5)
        self.set_text_color(60, 60, 60)
        x0 = self.l_margin
        self.set_x(x0 + 8)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.8)
        y_start = self.get_y()
        self.multi_cell(self.w - self.l_margin - self.r_margin - 16, 6, text)
        y_end = self.get_y()
        self.line(x0 + 4, y_start, x0 + 4, y_end)
        self.ln(2)

    def code_block(self, text):
        self.set_font(self.font_name, "", 8)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(245, 245, 245)
        for line in text.split("\n"):
            x0 = self.l_margin + 4
            self.set_x(x0)
            self.cell(
                self.w - self.l_margin - self.r_margin - 8,
                5,
                line,
                fill=True,
                new_x="LMARGIN",
                new_y="NEXT",
            )
        self.ln(2)

    def bullet(self, text, level=0):
        self.set_font(self.font_name, "", 9.5)
        self.set_text_color(30, 30, 30)
        indent = 6 + level * 6
        b = "-" if level == 0 else ">"
        self.set_x(self.l_margin + indent)
        self.cell(5, 6, b)
        self.multi_cell(
            self.w - self.l_margin - self.r_margin - indent - 5, 6, text
        )

    def hr(self):
        self.ln(3)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)

    def table(self, header_cells, data_rows):
        n = len(header_cells)
        w = (self.w - self.l_margin - self.r_margin) / n
        self.set_font(self.font_name, "B", 8)
        self.set_fill_color(230, 230, 230)
        for h in header_cells:
            self.cell(w, 6, h, border=1, fill=True, align="C")
        self.ln()
        self.set_font(self.font_name, "", 7.5)
        for row_cells in data_rows:
            y0 = self.get_y()
            x0 = self.get_x()
            for j, c in enumerate(row_cells[:n]):
                self.set_xy(x0 + j * w, y0)
                self.multi_cell(w, 5, c, border=1)
            self.set_y(max(self.get_y(), y0 + 6))
        self.ln(2)


# ─── 마크다운 정리 ───
def clean(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text


# ─── 테이블 파서 ───
def parse_table(lines, start):
    header_cells = [c.strip() for c in lines[start].split("|") if c.strip()]
    idx = start + 1
    if idx < len(lines) and all(
        set(c.strip()) <= set("-:|") for c in lines[idx].split("|") if c.strip()
    ):
        idx += 1
    data_rows = []
    while idx < len(lines) and "|" in lines[idx] and lines[idx].strip().startswith("|"):
        cells = [c.strip() for c in lines[idx].split("|") if c.strip()]
        if not all(set(c.strip()) <= set("-:") for c in cells):
            data_rows.append(cells)
        idx += 1
    return header_cells, data_rows, idx


# ─── 메인 변환 ───
def convert(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    pdf = MarkdownPDF()
    pdf.add_page()
    lines = content.split("\n")
    i = 0
    in_code = False
    code_buf = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 코드 블록
        if stripped.startswith("```"):
            if in_code:
                pdf.code_block("\n".join(code_buf))
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # 테이블
        if "|" in stripped and stripped.startswith("|"):
            hdr, rows, end = parse_table(lines, i)
            if hdr:
                pdf.table(hdr, rows)
            i = end
            continue

        # 제목
        if stripped.startswith("# ") and not stripped.startswith("## "):
            pdf.title_text(clean(stripped[2:]))
            i += 1; continue
        if stripped.startswith("## "):
            pdf.h2(clean(stripped[3:]))
            i += 1; continue
        if stripped.startswith("### "):
            pdf.h3(clean(stripped[4:]))
            i += 1; continue
        if stripped.startswith("#### "):
            pdf.h4(clean(stripped[5:]))
            i += 1; continue

        # 수평선
        if stripped == "---":
            pdf.hr()
            i += 1; continue

        # 인용
        if stripped.startswith("> "):
            q = [stripped[2:]]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith(">"):
                q.append(lines[j].strip().lstrip("> "))
                j += 1
            pdf.blockquote(clean("\n".join(q)))
            i = j; continue

        # 불릿
        if stripped.startswith("- ") or stripped.startswith("* "):
            pdf.bullet(clean(stripped[2:]), level=0)
            i += 1; continue
        if line.startswith("  -") or line.startswith("  *") or line.startswith("    -"):
            pdf.bullet(clean(stripped.lstrip("-* ")), level=1)
            i += 1; continue

        # 굵은 줄
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            pdf.bold_body(clean(stripped))
            i += 1; continue

        # 빈 줄
        if stripped == "":
            pdf.ln(2)
            i += 1; continue

        # 일반 문단
        para = [stripped]
        j = i + 1
        while j < len(lines):
            ns = lines[j].strip()
            if (ns == "" or ns.startswith("#") or ns.startswith("---") or
                ns.startswith("```") or ns.startswith("- ") or ns.startswith("* ") or
                ns.startswith("> ") or (ns.startswith("|") and "|" in ns[1:]) or
                (ns.startswith("**") and ns.endswith("**"))):
                break
            para.append(ns)
            j += 1
        pdf.body(clean(" ".join(para)))
        i = j

    out_path = md_path.rsplit(".", 1)[0] + ".pdf"
    pdf.output(out_path)
    print(f"✓ {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 scripts/md2pdf.py <파일.md>")
        sys.exit(1)

    md_file = sys.argv[1]

    if not os.path.exists(md_file):
        print(f"파일 없음: {md_file}")
        sys.exit(1)

    convert(md_file)
