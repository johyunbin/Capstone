#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate slide_content_versions.pdf with Korean text support using fpdf2
and AppleSDGothicNeo.ttc from macOS system fonts.
"""

from fpdf import FPDF

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
OUTPUT_PATH = "/Users/hyunbin/Research/slide_content_versions.pdf"


class KoreanPDF(FPDF):
    def header(self):
        pass  # no automatic header

    def footer(self):
        self.set_y(-12)
        self.set_font("Korean", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"- {self.page_no()} -", align="C")
        self.set_text_color(0, 0, 0)


def add_title_page(pdf):
    pdf.add_page()
    pdf.set_font("KoreanBold", size=20)
    pdf.set_fill_color(30, 60, 114)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.ln(80)
    pdf.multi_cell(0, 12, "삼성리서치 포트폴리오 PPT", align="C")
    pdf.ln(4)
    pdf.set_font("Korean", size=14)
    pdf.multi_cell(0, 10, "슬라이드 내용 구성 버전 비교", align="C")
    pdf.ln(10)
    pdf.set_font("Korean", size=11)
    pdf.multi_cell(0, 8, "버전 1 · 버전 2 · 버전 3", align="C")
    pdf.set_text_color(0, 0, 0)


def section_heading(pdf, text, level=1):
    if level == 1:
        pdf.set_fill_color(30, 60, 114)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("KoreanBold", size=14)
        pdf.ln(4)
        pdf.multi_cell(0, 10, f"  {text}", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
    elif level == 2:
        pdf.set_fill_color(220, 230, 245)
        pdf.set_text_color(30, 60, 114)
        pdf.set_font("KoreanBold", size=12)
        pdf.ln(3)
        pdf.multi_cell(0, 9, f"  {text}", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)
    elif level == 3:
        pdf.set_font("KoreanBold", size=11)
        pdf.set_text_color(50, 80, 140)
        pdf.ln(3)
        pdf.multi_cell(0, 8, f"[{text}]")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)


def body_text(pdf, text, indent=0):
    pdf.set_font("Korean", size=10)
    pdf.set_text_color(40, 40, 40)
    x_margin = 15 + indent
    pdf.set_x(x_margin)
    pdf.multi_cell(0, 7, text)
    pdf.set_text_color(0, 0, 0)


def bullet(pdf, text, indent=4):
    pdf.set_font("Korean", size=10)
    pdf.set_text_color(40, 40, 40)
    x_margin = 15 + indent
    pdf.set_x(x_margin)
    pdf.multi_cell(0, 7, f"• {text}")
    pdf.set_text_color(0, 0, 0)


def add_version1(pdf):
    pdf.add_page()
    section_heading(pdf, "버전 1: 초기 상세버전 (디테일 중심)", level=1)

    section_heading(pdf, "도입부 S1-S3", level=3)
    bullet(pdf, 'S1 Title: "Spatial Audio Research & Perception-driven Quality Evaluation"')
    bullet(pdf, "S2 About Me: 경력 타임라인 + 4 실적카드 (SCI 24편, EAA Best Paper, 특허 6건, LEED/WELL AP)")
    bullet(pdf, "  전문성 4개: Spatial Audio Rendering / Perception-driven Evaluation / Soundscape Design & ISO / AI-driven Audio Analysis", indent=8)
    bullet(pdf, 'S3 핵심 질문: "기술적으로 좋은 오디오 vs 사용자가 진짜 좋다고 느끼는 오디오" + 4 Part 로드맵')

    section_heading(pdf, "브릿지 S4-S5", level=3)
    bullet(pdf, "S4 사운드스케이프: Traditional vs Soundscape 패러다임, ISO 12913, Pleasant-Eventful 다이어그램")
    bullet(pdf, "S5 연결 테이블 5행:")
    bullet(pdf, "경험평가 → 렌더링품질", indent=8)
    bullet(pdf, "A-V 상호작용 → 통합설계", indent=8)
    bullet(pdf, "맥락 → 적응형 렌더링", indent=8)
    bullet(pdf, "개인차 → 개인화", indent=8)
    bullet(pdf, "ISO표준 → THX/TTA인증", indent=8)

    section_heading(pdf, "Part I: S6-S11", level=3)
    bullet(pdf, "S6: 5축 Overview")
    bullet(pdf, "S7 축1 시각재현: APAC_2022, 40명×8환경, HMD vs Monitor, FOA+headtracking")
    bullet(pdf, "  14 semantic pairs, LAeq 57.2-79.4 dBA, p<0.05", indent=8)
    bullet(pdf, "S8 축2 헤드폰vs스피커: APAC_2019, 4가지 재생환경, LAeq 40-65dB")
    bullet(pdf, "  허용한계 6% / 성가심 8% / 2.2dBA", indent=8)
    bullet(pdf, "S9 축3 바이노럴-비주얼: B&E_2019 ×2, 2×2 HRTF×HMD, 40×8=320pts, CIPIC HRTF, 77%/23%, 6-7dB↓")
    bullet(pdf, "S10 축4 시청각정보: B&E_2020, 8환경, A-only/V-only/AV, 청각 24% / 시각 76%, 설명력 51%")
    bullet(pdf, "  ※SEM을 B&E_2020에 잘못 포함", indent=8)
    bullet(pdf, "S11 축5 생태학적타당성: SCS_2021, 50명×10환경, ISO 12913-2 A/B/C, VR≈In-situ")

    section_heading(pdf, "Part II: S12-S13", level=3)
    bullet(pdf, "S12 생리반응: SCS_2023+SR_2022+IJERPH_2024, 60명×9환경×2일, EEG/HRV/Eye-tracking")
    bullet(pdf, "  CCA 0.80/0.78, SDNN +14.6%, TSI -9.5%", indent=8)
    bullet(pdf, "S13 사운드스케이프디자인: B&E_2021+B&E_2022, SEM 경로모델")

    section_heading(pdf, "Part III: S14-S15", level=3)
    bullet(pdf, "S14 AVAS: 17EV×43AVAS, 134명, Comfort-Metallic, 만족도예측 92.5%, 34대 DB")
    bullet(pdf, "S15 양산실행력: EV3/IONIQ5, 특허 6건, 기술이전 5천만원")

    section_heading(pdf, "Part IV: S16-S18", level=3)
    bullet(pdf, "S16 AI: RIR 8→43,000, LSTM, AI 84.9% vs 전문가 56.4%, A-JEPA 비전")
    bullet(pdf, "S17 Contribution: 단기/중장기 2단계")
    bullet(pdf, "S18 Thank You")


def add_version2(pdf):
    pdf.add_page()
    section_heading(pdf, "버전 2: 수정버전 (간결화 + 정확한 인용)", level=1)

    section_heading(pdf, "핵심 변경사항", level=3)
    bullet(pdf, '각 연구 슬라이드를 "RQ 한 줄 + 핵심 수치 2-3개 + Implication 한 줄"로 압축')
    bullet(pdf, "방법론 디테일은 Q&A 대비용으로만 준비")
    bullet(pdf, "S10의 SEM을 B&E_2021로 올바르게 분리")

    section_heading(pdf, "S7-S11 변경 내용", level=3)
    bullet(pdf, "S7: RQ + (40명×8환경, p<0.05) + \"HMD=현실감↑, 모니터=인식↑\" + XR 대응")
    bullet(pdf, "S8: RQ + (6%, 8%, 2.2dBA) + \"스피커+HMD 가장 근접\" + 지각차이 정량화")
    bullet(pdf, "S9: RQ + (77%, 23%, 6-7dB↓) + \"음상외재화·몰입감 증가\" + HRTF 개인화")
    bullet(pdf, "S10: RQ + (24%, 76%, 51%) + \"cross-modal\" + Display+Audio 통합")
    bullet(pdf, "  ★ SEM은 B&E_2021로 분리", indent=8)
    bullet(pdf, "S11: RQ + (50명×10환경, 3프로토콜) + \"VR≈In-situ\" + VR 평가 신뢰")


def add_version3(pdf):
    pdf.add_page()
    section_heading(pdf, "버전 3: 최종 확정버전 (개선 사항 반영)", level=1)
    body_text(pdf, "버전 2 대비 핵심 변경:")

    section_heading(pdf, "S2 개선", level=2)
    body_text(pdf, "전문성 4개를 발표 Part와 1:1 대응으로 재구성:")
    bullet(pdf, "1. Spatial Audio & Immersive Rendering → Part I")
    bullet(pdf, "2. Perception-driven Quality Evaluation → Part II")
    bullet(pdf, "3. Research-to-Product Execution → Part III  ★ \"Soundscape Design & ISO\" 제거")
    bullet(pdf, "4. AI-driven Audio Processing → Part IV")
    bullet(pdf, "LEED/WELL AP 제거 → 국제공동연구(UCL·소르본, SATP 18개국) 카드로 교체")

    section_heading(pdf, "S3 개선", level=2)
    bullet(pdf, '추상적 질문 → 구체적 공학 수치로 시작: "THD 0.01%, 주파수 응답 ±0.5dB"')
    bullet(pdf, '"시각 맥락만으로 오디오 만족도가 76% 좌우" 수치 명시')
    bullet(pdf, '"사용자가 진짜 몰입을 느끼는 3D Audio-Visual 경험을 어떻게 설계하고 검증할 것인가?"')

    section_heading(pdf, "S5 테이블 개선", level=2)
    bullet(pdf, 'Row 1: "THD·주파수응답 같은 공학 지표가 아닌" 명시')
    bullet(pdf, 'Row 2: "76% 좌우" 수치 추가')
    bullet(pdf, 'Row 3: "도시 맥락" → "재생 환경(거실·침실·차량)"')
    bullet(pdf, 'Row 5: "ISO→THX" → "프로토콜 설계 역량 자체를 강점으로"')
    bullet(pdf, '하단: "사운드스케이프" → "저의 전문성은 \'사용자가 어떻게 경험할 것인가\'를 설계하고 검증하는 것"')

    section_heading(pdf, "S10 수정", level=2)
    bullet(pdf, "SEM(구조방정식)이 B&E_2021임을 명확히 분리")

    section_heading(pdf, "S17 Contribution Plan 개선", level=2)
    bullet(pdf, "2단계(단기/중장기) → 3단계 구성:")
    bullet(pdf, "① 입사~6개월", indent=8)
    bullet(pdf, "② 6개월~2년", indent=8)
    bullet(pdf, "③ 2년~", indent=8)
    bullet(pdf, "4행: Eclipsa Audio / AI 전환 / 파트 시너지 / 인증·표준")
    bullet(pdf, "AI를 즉시기여부터 포함으로 승격")
    bullet(pdf, '"신호처리가 만드는 기술 위에, 사용자가 경험하는 품질을 설계합니다"')

    section_heading(pdf, "Q&A 대비 추가", level=2)
    bullet(pdf, "동료: HRTF 개인화, Eclipsa vs Dolby 메트릭, A-JEPA 적용, 공간구조분석")
    bullet(pdf, "임원: 건축음향 차별가치, 이직 이유, 갈등해결, 2년 성과, AI전환 기여")


def main():
    pdf = KoreanPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=15, top=15, right=15)

    # Register fonts (AppleSDGothicNeo.ttc has multiple faces; index 0 = Regular, 1 = Bold)
    pdf.add_font("Korean", "", FONT_PATH)
    pdf.add_font("KoreanBold", "", FONT_PATH)

    add_title_page(pdf)
    add_version1(pdf)
    add_version2(pdf)
    add_version3(pdf)

    pdf.output(OUTPUT_PATH)
    print(f"PDF saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
