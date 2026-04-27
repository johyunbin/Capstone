#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate slide_versions_full.pdf with 3 complete versions of slide content.
Uses fpdf2 with AppleSDGothicNeo font for Korean text support.
"""

from fpdf import FPDF
import os

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
OUTPUT_PATH = "/Users/hyunbin/Research/slide_versions_full.pdf"

# Colors
NAVY = (10, 36, 99)
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 245)
DARK_GRAY = (60, 60, 60)
ACCENT_BLUE = (41, 128, 185)
LIGHT_BLUE = (214, 234, 248)


class SlidePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        # Add AppleSDGothicNeo font (TTC file - use index 0 for regular)
        self.add_font("AppleSDGothicNeo", "", FONT_PATH)
        self.add_font("AppleSDGothicNeo", "B", FONT_PATH)
        self.set_font("AppleSDGothicNeo", "", 10)

    def navy_header(self, title, subtitle=None):
        """Navy background header block"""
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        self.rect(0, self.get_y(), 210, 28 if subtitle else 20, 'F')
        y = self.get_y()
        self.set_xy(10, y + 4)
        self.set_font("AppleSDGothicNeo", "B", 14)
        self.cell(190, 7, title, ln=True, align='C')
        if subtitle:
            self.set_font("AppleSDGothicNeo", "", 9)
            self.set_x(10)
            self.cell(190, 5, subtitle, ln=True, align='C')
        self.set_y(y + (28 if subtitle else 20) + 3)
        self.set_text_color(*DARK_GRAY)

    def slide_header(self, slide_id, title):
        """Slide section header with slide number"""
        self.set_fill_color(*ACCENT_BLUE)
        self.set_text_color(*WHITE)
        y = self.get_y()
        self.rect(10, y, 190, 9, 'F')
        self.set_xy(12, y + 1)
        self.set_font("AppleSDGothicNeo", "B", 10)
        self.cell(186, 6, f"{slide_id}. {title}", ln=True, align='L')
        self.set_text_color(*DARK_GRAY)
        self.ln(2)

    def body_text(self, text, indent=0, bullet=False, bold=False, size=9):
        """Render body text with optional bullet"""
        self.set_font("AppleSDGothicNeo", "B" if bold else "", size)
        self.set_text_color(*DARK_GRAY)
        prefix = "• " if bullet else ""
        x = 10 + indent
        w = 190 - indent
        self.set_x(x)
        self.multi_cell(w, 5, prefix + text, ln=True)

    def label_value(self, label, value, indent=5):
        """Render label: value pair"""
        self.set_font("AppleSDGothicNeo", "B", 9)
        self.set_text_color(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2])
        self.set_x(10 + indent)
        # label
        label_w = self.get_string_width(label + " ") + 2
        self.cell(label_w, 5, label, ln=False)
        self.set_font("AppleSDGothicNeo", "", 9)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(190 - indent - label_w, 5, value, ln=True)

    def section_box(self, text, color=None):
        """Light blue box for implications/conclusions"""
        if color is None:
            color = LIGHT_BLUE
        y = self.get_y()
        self.set_fill_color(*color)
        self.set_draw_color(*ACCENT_BLUE)
        # measure height
        self.set_font("AppleSDGothicNeo", "", 9)
        lines = self.multi_cell(176, 5, text, dry_run=True, output='LINES')
        h = len(lines) * 5 + 6
        self.rect(10, y, 190, h, 'FD')
        self.set_xy(13, y + 3)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(184, 5, text, ln=True)
        self.set_draw_color(0, 0, 0)
        self.ln(2)

    def version_cover(self, version_num, version_title, description):
        """Full page version cover"""
        self.add_page()
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 297, 'F')
        self.set_text_color(*WHITE)

        # Version number
        self.set_font("AppleSDGothicNeo", "B", 32)
        self.set_xy(10, 80)
        self.cell(190, 20, f"Version {version_num}", ln=True, align='C')

        # Version title
        self.set_font("AppleSDGothicNeo", "B", 18)
        self.set_x(10)
        self.multi_cell(190, 10, version_title, align='C')

        # Description
        self.set_font("AppleSDGothicNeo", "", 12)
        self.set_xy(20, self.get_y() + 20)
        self.multi_cell(170, 7, description, align='C')

        # Slide count note
        self.set_font("AppleSDGothicNeo", "", 10)
        self.set_xy(10, 240)
        self.set_text_color(180, 200, 230)
        self.cell(190, 8, "S1 ~ S18 전체 슬라이드 내용 포함", align='C', ln=True)

        self.set_text_color(*DARK_GRAY)


def add_cover_page(pdf):
    """Main cover page"""
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(*WHITE)

    pdf.set_font("AppleSDGothicNeo", "B", 22)
    pdf.set_xy(10, 60)
    pdf.multi_cell(190, 12, "Spatial Audio Research\n& Perception-driven Quality Evaluation", align='C')

    pdf.set_font("AppleSDGothicNeo", "", 13)
    pdf.set_xy(10, 120)
    pdf.cell(190, 8, "슬라이드 버전 전체 사양서", align='C', ln=True)

    pdf.set_font("AppleSDGothicNeo", "", 11)
    pdf.set_xy(10, 145)
    pdf.cell(190, 7, "3개 버전 완전 수록 — 요약 없음, 전체 텍스트 기준", align='C', ln=True)

    pdf.set_font("AppleSDGothicNeo", "", 10)
    pdf.set_xy(10, 170)
    pdf.set_text_color(180, 200, 230)
    pdf.cell(190, 6, "버전 1: 전체 구성 종합 (초기 제안)", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 6, "버전 2: 디테일버전 (상세 방법론 + 수치 보강)", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 6, "버전 3: 최종 확정버전 (적절히 혼합)", align='C', ln=True)

    pdf.set_font("AppleSDGothicNeo", "B", 12)
    pdf.set_xy(10, 210)
    pdf.set_text_color(*WHITE)
    pdf.cell(190, 7, "조현인 (Hyun In Jo, Ph.D.)", align='C', ln=True)
    pdf.set_font("AppleSDGothicNeo", "", 10)
    pdf.set_x(10)
    pdf.cell(190, 6, "Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio", align='C', ln=True)

    pdf.set_text_color(*DARK_GRAY)


# ============================================================
# VERSION 1 CONTENT
# ============================================================
def add_version1(pdf):
    pdf.version_cover(
        1,
        "전체 구성 종합",
        "초기 제안\nS1~S18 전체 슬라이드 완전 기술\n각 슬라이드의 디자인 의도, 내용, Samsung Research 적용 시사점 포함"
    )

    # S1
    pdf.add_page()
    pdf.slide_header("S1", "Title Slide")
    pdf.body_text("디자인: Navy 풀 배경", bold=True)
    pdf.ln(1)
    pdf.label_value("제목:", "Spatial Audio Research & Perception-driven Quality Evaluation")
    pdf.label_value("부제:", "Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio")
    pdf.label_value("이름:", "조현인 (Hyun In Jo, Ph.D.)")
    pdf.label_value("현직:", "Senior Research Engineer, Hyundai Motor Company (NVH Division)")
    pdf.label_value("연락처:", "best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo")

    # S2
    pdf.ln(3)
    pdf.slide_header("S2", "About Me")
    pdf.body_text("좌측: 경력 타임라인 (세로 흐름)", bold=True)
    for item in [
        "2013-2016: B.S. 건축공학, 한양대 (수석졸업, 조기졸업)",
        "2016-2022: Ph.D. 건축음향, 한양대 (석박통합, GPA 4.39/4.5)",
        "2022.03-08: Post-doc, 한국건설기술연구원",
        "2022.08-현재: 현대자동차 NVH 책임연구원",
        "→ Samsung Research, Spatial Audio",
    ]:
        pdf.body_text(item, indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("우측: 핵심 실적 카드 4개", bold=True)
    for item in [
        "SCI(E) 24편 (주저자 21편), h-index 18",
        "EAA Best Paper Award (ICA 2019), I-INCE Young Professional Award",
        "특허 6건 (국내+미국), 기술이전 5천만원",
        "LEED AP, WELL AP 자격",
    ]:
        pdf.body_text(item, indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("하단: 핵심 전문성 4개 아이콘 행", bold=True)
    for item in [
        "① Spatial Audio Rendering",
        "② Perception-driven Evaluation",
        "③ Soundscape Design & ISO",
        "④ AI-driven Audio Analysis",
    ]:
        pdf.body_text(item, indent=5, bullet=True)

    # S3
    pdf.ln(3)
    pdf.slide_header("S3", "핵심 질문 제기")
    pdf.body_text("큰 텍스트 중앙 (핵심 메시지):", bold=True)
    pdf.section_box(
        '"기술적으로 좋은 오디오" vs "사용자가 진짜 좋다고 느끼는 오디오"\n→ 이 차이를 어떻게 메울 것인가?'
    )
    pdf.body_text("하단: 4개 Part 로드맵", bold=True)
    for item in [
        "Part I: Spatial Audio 기술 역량",
        "Part II: 지각 기반 평가 방법론",
        "Part III: 제품 적용 AVAS",
        "Part IV: AI 확장 + Contribution",
    ]:
        pdf.body_text(item, indent=5, bullet=True)

    # S4
    pdf.add_page()
    pdf.slide_header("S4", "사운드스케이프란?")
    pdf.body_text("상단 대비 구조:", bold=True)
    pdf.body_text("Traditional (Noise Control): \"소음이 얼마나 큰가?\"", indent=5, bullet=True)
    pdf.body_text("New Paradigm (Soundscape): \"소리가 어떻게 경험되는가?\"", indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("ISO 12913 정의:", bold=True)
    pdf.section_box(
        '"Acoustic environment as perceived or experienced and/or understood by a person or people, in context"'
    )
    pdf.body_text("하단: Pleasant-Eventful 2차원 모델 다이어그램", indent=5, bullet=True)

    # S5
    pdf.ln(2)
    pdf.slide_header("S5", "왜 사운드스케이프가 Spatial Audio에 직결되는가")
    pdf.body_text("5행 연결 테이블:", bold=True)
    rows = [
        ("1. 소리를 경험으로 평가",
         "렌더링 품질을 사용자가 느끼는 공간감·몰입감으로 평가"),
        ("2. 오디오-비주얼 상호작용",
         "Display + Audio 통합 설계, Holographic Displays × Spatial Audio 시너지"),
        ("3. 환경에 따라 같은 소리도 다르게 인식",
         "재생 환경별 적응형 렌더링 TV 2.0ch ~ 사운드바 11.1.4ch"),
        ("4. 개인차 (소음 민감도 등)",
         "Customized Audio 개인화"),
        ("5. ISO 표준 기반 평가 프로토콜",
         "오디오 품질 인증 프로그램 THX/TTA 연계"),
    ]
    for k, v in rows:
        pdf.body_text(k, indent=5, bold=True)
        pdf.body_text("→ " + v, indent=12)
        pdf.ln(1)
    pdf.ln(1)
    pdf.section_box(
        '"신호처리가 \'어떻게 만들 것인가\'라면, 사운드스케이프는 \'어떻게 평가하고 설계할 것인가\'"'
    )

    # S6
    pdf.add_page()
    pdf.slide_header("S6", "Spatial Audio 연구 체계도")
    pdf.body_text("5개 기술 축 다이어그램:", bold=True)
    axes = [
        ("축1: 시각 재현 방식 영향", "APAC'22"),
        ("축2: 재생 방식 영향", "APAC'19"),
        ("축3: 바이노럴-비주얼 상호작용", "B&E'19 ×2"),
        ("축4: 시청각 정보 영향", "B&E'20"),
        ("축5: 생태학적 타당성", "SCS'21"),
    ]
    for axis, paper in axes:
        pdf.label_value(axis + ":", paper, indent=5)
    pdf.ln(2)
    pdf.section_box(
        '"VR 환경에서 Spatial Audio의 각 기술 요소가 사용자 지각에 미치는 영향을 체계적으로 규명"'
    )

    # S7
    pdf.ln(2)
    pdf.slide_header("S7", "축1: 시각 재현 방식의 영향")
    pdf.label_value("논문:", "APAC_2022_Jo&Jeon (Applied Acoustics, IF 3.4)")
    pdf.label_value("RQ:", "같은 Spatial Audio를 HMD vs 모니터로 볼 때, 사용자 지각이 얼마나 달라지는가?")
    pdf.label_value("핵심 수치:", "40명 × 8환경 / HMD에서 부정·긍정 요소 모두 더 민감하게 인식 (p<0.05)")
    pdf.label_value("한 줄 결과:", "HMD = 공간 현실감↑ / 모니터 = 전반적 인식↑")
    pdf.section_box(
        "→ Eclipsa Audio: XR 디바이스 대응 시, 시각 조건 통제가 품질 평가의 전제"
    )

    # S8
    pdf.ln(2)
    pdf.slide_header("S8", "축2: 헤드폰 vs 스피커")
    pdf.label_value("논문:", "APAC_2019_Jeon et al (Applied Acoustics, IF 3.4)")
    pdf.label_value("RQ:", "헤드폰과 스피커 재생 방식이 사용자의 소리 품질 판단을 어떻게 바꾸는가?")
    pdf.label_value("핵심 수치:", "허용한계 6% 차이 / 성가심 8% 차이 / 50% 성가심 도달 SPL 2.2 dBA 차이")
    pdf.label_value("한 줄 결과:", "스피커+HMD 조합이 실제 환경에 가장 근접한 평가")
    pdf.section_box(
        "→ Eclipsa Audio: 헤드폰(바이노럴) vs 스피커(멀티채널) 재생 시 지각 차이 정량화 기준"
    )

    # S9
    pdf.add_page()
    pdf.slide_header("S9", "축3: 바이노럴-비주얼 상호작용")
    pdf.label_value("논문:", "B&E_2019_Jeon&Jo + B&E_2019_Jo et al (IF 7.4) — 2편")
    pdf.label_value("RQ:", "HRTF와 HMD, 어느 것이 사용자 공간 지각에 더 지배적인가?")
    pdf.label_value("핵심 수치:", "HRTF 77% vs HMD 23%")
    pdf.body_text("보조 결과:", bold=True, indent=5)
    pdf.body_text("HRTF+HMD 시 음상 외재화·몰입감 유의 증가", indent=10, bullet=True)
    pdf.body_text("VR에서 허용한계 6~7 dB 하락", indent=10, bullet=True)
    pdf.section_box(
        "→ Eclipsa Audio: HRTF 개인화 = 렌더러 최적화의 최우선 과제"
    )

    # S10
    pdf.ln(2)
    pdf.slide_header("S10", "축4: 시청각 정보의 지각 영향")
    pdf.label_value("대표 논문:", "B&E_2020_Jeon&Jo (IF 7.4)")
    pdf.label_value("RQ:", "Audio와 Visual 정보가 전체 만족도에 각각 얼마나 기여하는가?")
    pdf.label_value("핵심 수치:", "청각 24% vs 시각 76%")
    pdf.body_text("보조: 만족도 모델 설명력 51% / cross-modal effect", indent=5, bullet=True)
    pdf.body_text("참고: SEM 경로 모델은 B&E_2021_Jo&Jeon에서 발전적 제시", indent=5, bullet=True)
    pdf.section_box(
        "→ Eclipsa Audio: Display + Audio 통합 설계 → Holographic Displays 시너지"
    )

    # S11
    pdf.ln(2)
    pdf.slide_header("S11", "축5: 생태학적 타당성")
    pdf.label_value("논문:", "SCS_2021_Jo&Jeon (IF 11.7)")
    pdf.label_value("RQ:", "VR 실험실 평가 결과를 실제 현장(in-situ)과 동일하게 신뢰할 수 있는가?")
    pdf.label_value("핵심 수치:", "50명 × 10환경 / ISO 12913-2 3가지 프로토콜 모두에서 VR ≈ In-situ")
    pdf.label_value("한 줄 결과:", "FOA 바이노럴 + 헤드트래킹의 높은 생태학적 타당성 실증")
    pdf.section_box(
        "→ Eclipsa Audio: VR 기반 실험실에서 렌더링 품질 평가 → 실사용 환경 결과를 신뢰할 수 있음"
    )

    # S12
    pdf.add_page()
    pdf.slide_header("S12", "멀티모달 생리반응 모델링")
    pdf.label_value("논문:", "SCS_2023 (IF 11.7, 교신저자) + SR_2022 + IJERPH_2024")
    pdf.label_value("RQ:", "물리적 음향 파라미터로부터 사용자의 생리적 지각 반응을 예측할 수 있는가?")
    pdf.label_value("실험:", "60명 × 9환경 × 2일 / FOA + HMD + 헤드트래킹")
    pdf.label_value("측정:", "EEG (32ch) · HRV (5지표) · Eye-tracking")
    pdf.label_value("핵심 수치:", "CCA 0.80, CCA 0.78, SDNN +14.6%, TSI -9.5%")
    pdf.section_box(
        "→ Eclipsa Audio:\n"
        "  • EEG/HRV 프로토콜로 렌더링 품질 객관 검증\n"
        "  • 물리→지각 예측 모델로 자동 최적화 기초"
    )

    # S13
    pdf.ln(2)
    pdf.slide_header("S13", "사운드스케이프 디자인 응용")
    pdf.label_value("논문:", "B&E_2021_Jo&Jeon + B&E_2022_Jo&Jeon (IF 7.4)")
    pdf.label_value("RQ:", "오디오-비주얼 상호작용이 실내 환경의 업무 품질과 생산성에 미치는 영향은?")
    pdf.label_value("핵심 결과:", "SEM 모델로 Audio → Visual → 만족도 경로 정량화 / A-V 일치 시 업무 선호도·생산성 유의 향상")
    pdf.section_box(
        "→ Eclipsa Audio: TV·사운드바 실내 환경별 최적 렌더링 설계의 이론적 근거"
    )

    # S14
    pdf.ln(2)
    pdf.slide_header("S14", "AVAS 사운드스케이프 디자인")
    pdf.label_value("출처:", "HMG 학술대회 + JASA 논문 (심사 중)")
    pdf.label_value("배경:", "EV 시대 → AVAS가 도시 음환경의 새로운 요소")
    pdf.label_value("데이터:", "17개 EV × 43개 AVAS 바이노럴 레코딩 / 134명 대규모 청감평가")
    pdf.label_value("방법론:", "3단계 감성어휘 (272→25→18쌍) → PCA → Comfort-Metallic 신규 축")
    pdf.label_value("핵심 수치:", "만족도 예측 92.5%, 34대 경쟁 DB")
    pdf.section_box(
        "→ Eclipsa Audio: 물리지표→만족도 예측 자동 튜닝 / Eclipsa vs Dolby Atmos 경쟁 분석"
    )

    # S15
    pdf.add_page()
    pdf.slide_header("S15", "연구 → 양산 실행력")
    pdf.label_value("적용:", "AVAS 브랜드 사운드 2.0 → EV3, IONIQ 5 양산")
    pdf.label_value("프로세스:", "음향 설계 → 청취 평가 → 시스템 검증 → 양산 전과정 주도")
    pdf.label_value("성과:", "특허 6건, 기술이전 5천만원, HMG 특별상, 웹 예측 툴")
    pdf.section_box(
        "→ 삼성리서치: 선행연구→제품 사양 전환 실행력 / 디자인·법규·NVH 부서간 협업"
    )

    # S16
    pdf.ln(2)
    pdf.slide_header("S16", "AI 기반 오디오 처리")
    pdf.label_value("논문:", "SENSORS_2021 (SCI)")
    pdf.label_value("문제:", "학습 데이터 부족 (30명, 126건)")
    pdf.label_value("해결:", "RIR Convolution 증강 8→43,000건 / Loudness + Energy Ratio 신규 특징")
    pdf.label_value("핵심 수치:", "AI 84.9%/90.0%/0.84 vs 전문가 56.4%/40.7%/0.56")
    pdf.label_value("IP:", "국내+미국 특허, 기술이전 5천만원")
    pdf.label_value("A-JEPA 비전:", "Meta 자기지도 학습 + 음향 도메인 → 지능형 적응 렌더링")
    pdf.section_box(
        "→ Eclipsa Audio: RIR 증강→재생환경 학습데이터 / 도메인+AI 특징 설계"
    )

    # S17
    pdf.ln(2)
    pdf.slide_header("S17", "Contribution Plan (단기/중장기)")
    pdf.body_text("단기 | Eclipsa Audio 품질 검증", bold=True)
    items_short = [
        "TV 2.0ch ~ 사운드바 11.1.4ch 지각 기반 정량 평가",
        "HRTF 바이노럴 렌더러 검증 + 개인화",
        "Eclipsa vs Dolby Atmos 감성 평가 프레임워크",
        "THX/TTA 인증에 지각 평가 데이터 제공",
        "Holographic Displays × Spatial Audio 통합 지각 연구",
    ]
    for item in items_short:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.ln(2)
    pdf.body_text("중장기 | AI 기반 적응형 렌더링", bold=True)
    items_long = [
        "A-JEPA 기반 오디오 표현 학습 → 사용자 지각 대응",
        "재생 공간 자동 인식 + 렌더링 최적화",
        "Customized Audio 개인화",
        "IAMF 2.0 Object-based 지각 품질 가이드라인",
    ]
    for item in items_long:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.ln(2)
    pdf.section_box(
        '"목표는 \'기술적으로 우수한 오디오\'가 아니라, 사용자가 진정으로 몰입을 느끼는 3D Audio-Visual 경험을 만드는 것"'
    )

    # S18
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(*WHITE)
    pdf.slide_header("S18", "Thank You")
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 30, 210, 267, 'F')
    pdf.set_text_color(*WHITE)
    pdf.set_font("AppleSDGothicNeo", "B", 18)
    pdf.set_xy(10, 100)
    pdf.cell(190, 10, "경청해 주셔서 감사합니다.", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 10, "질문 부탁드립니다.", align='C', ln=True)
    pdf.set_font("AppleSDGothicNeo", "", 11)
    pdf.set_xy(10, 160)
    pdf.cell(190, 7, "조현인 (Hyun In Jo, Ph.D.)", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 7, "best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo", align='C', ln=True)
    pdf.set_text_color(*DARK_GRAY)


# ============================================================
# VERSION 2 CONTENT
# ============================================================
def add_version2(pdf):
    pdf.version_cover(
        2,
        "디테일버전",
        "상세 방법론 + 수치 보강\nS1~S6: 버전 1과 동일\nS7~S11: 상세 방법론 및 추가 수치 포함\nS12~S18: 버전 1과 동일"
    )

    # S1-S5: same as version 1 (re-rendered fully)
    # S1
    pdf.add_page()
    pdf.body_text("※ S1~S5는 버전 1과 동일한 전체 내용", bold=True)
    pdf.ln(2)
    pdf.slide_header("S1", "Title Slide")
    pdf.body_text("디자인: Navy 풀 배경", bold=True)
    pdf.label_value("제목:", "Spatial Audio Research & Perception-driven Quality Evaluation")
    pdf.label_value("부제:", "Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio")
    pdf.label_value("이름:", "조현인 (Hyun In Jo, Ph.D.)")
    pdf.label_value("현직:", "Senior Research Engineer, Hyundai Motor Company (NVH Division)")
    pdf.label_value("연락처:", "best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo")

    # S2
    pdf.ln(3)
    pdf.slide_header("S2", "About Me")
    pdf.body_text("좌측: 경력 타임라인 (세로 흐름)", bold=True)
    for item in [
        "2013-2016: B.S. 건축공학, 한양대 (수석졸업, 조기졸업)",
        "2016-2022: Ph.D. 건축음향, 한양대 (석박통합, GPA 4.39/4.5)",
        "2022.03-08: Post-doc, 한국건설기술연구원",
        "2022.08-현재: 현대자동차 NVH 책임연구원",
        "→ Samsung Research, Spatial Audio",
    ]:
        pdf.body_text(item, indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("우측: 핵심 실적 카드 4개", bold=True)
    for item in [
        "SCI(E) 24편 (주저자 21편), h-index 18",
        "EAA Best Paper Award (ICA 2019), I-INCE Young Professional Award",
        "특허 6건 (국내+미국), 기술이전 5천만원",
        "LEED AP, WELL AP 자격",
    ]:
        pdf.body_text(item, indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("하단: 핵심 전문성 4개 아이콘 행", bold=True)
    for item in [
        "① Spatial Audio Rendering",
        "② Perception-driven Evaluation",
        "③ Soundscape Design & ISO",
        "④ AI-driven Audio Analysis",
    ]:
        pdf.body_text(item, indent=5, bullet=True)

    # S3
    pdf.ln(3)
    pdf.slide_header("S3", "핵심 질문 제기")
    pdf.body_text("큰 텍스트 중앙 (핵심 메시지):", bold=True)
    pdf.section_box(
        '"기술적으로 좋은 오디오" vs "사용자가 진짜 좋다고 느끼는 오디오"\n→ 이 차이를 어떻게 메울 것인가?'
    )
    pdf.body_text("하단: 4개 Part 로드맵", bold=True)
    for item in [
        "Part I: Spatial Audio 기술 역량",
        "Part II: 지각 기반 평가 방법론",
        "Part III: 제품 적용 AVAS",
        "Part IV: AI 확장 + Contribution",
    ]:
        pdf.body_text(item, indent=5, bullet=True)

    # S4
    pdf.add_page()
    pdf.slide_header("S4", "사운드스케이프란?")
    pdf.body_text("상단 대비 구조:", bold=True)
    pdf.body_text("Traditional (Noise Control): \"소음이 얼마나 큰가?\"", indent=5, bullet=True)
    pdf.body_text("New Paradigm (Soundscape): \"소리가 어떻게 경험되는가?\"", indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("ISO 12913 정의:", bold=True)
    pdf.section_box(
        '"Acoustic environment as perceived or experienced and/or understood by a person or people, in context"'
    )
    pdf.body_text("하단: Pleasant-Eventful 2차원 모델 다이어그램", indent=5, bullet=True)

    # S5
    pdf.ln(2)
    pdf.slide_header("S5", "왜 사운드스케이프가 Spatial Audio에 직결되는가")
    pdf.body_text("5행 연결 테이블:", bold=True)
    rows = [
        ("1. 소리를 경험으로 평가",
         "렌더링 품질을 사용자가 느끼는 공간감·몰입감으로 평가"),
        ("2. 오디오-비주얼 상호작용",
         "Display + Audio 통합 설계, Holographic Displays × Spatial Audio 시너지"),
        ("3. 환경에 따라 같은 소리도 다르게 인식",
         "재생 환경별 적응형 렌더링 TV 2.0ch ~ 사운드바 11.1.4ch"),
        ("4. 개인차 (소음 민감도 등)",
         "Customized Audio 개인화"),
        ("5. ISO 표준 기반 평가 프로토콜",
         "오디오 품질 인증 프로그램 THX/TTA 연계"),
    ]
    for k, v in rows:
        pdf.body_text(k, indent=5, bold=True)
        pdf.body_text("→ " + v, indent=12)
        pdf.ln(1)
    pdf.section_box(
        '"신호처리가 \'어떻게 만들 것인가\'라면, 사운드스케이프는 \'어떻게 평가하고 설계할 것인가\'"'
    )

    # S6
    pdf.add_page()
    pdf.slide_header("S6", "Spatial Audio 연구 체계도")
    pdf.body_text("5개 기술 축 다이어그램:", bold=True)
    axes = [
        ("축1: 시각 재현 방식 영향", "APAC'22"),
        ("축2: 재생 방식 영향", "APAC'19"),
        ("축3: 바이노럴-비주얼 상호작용", "B&E'19 ×2"),
        ("축4: 시청각 정보 영향", "B&E'20"),
        ("축5: 생태학적 타당성", "SCS'21"),
    ]
    for axis, paper in axes:
        pdf.label_value(axis + ":", paper, indent=5)
    pdf.ln(2)
    pdf.section_box(
        '"VR 환경에서 Spatial Audio의 각 기술 요소가 사용자 지각에 미치는 영향을 체계적으로 규명"'
    )

    # S7 - DETAILED VERSION
    pdf.ln(2)
    pdf.slide_header("S7", "축1: 시각 재현 방식의 영향 [상세]")
    pdf.label_value("논문:", "APAC_2022_Jo&Jeon (Applied Acoustics, IF 3.4)")
    pdf.label_value("RQ:", "같은 Spatial Audio를 HMD vs 모니터로 볼 때, 사용자 지각이 얼마나 달라지는가?")
    pdf.ln(1)
    pdf.body_text("상세 방법론:", bold=True)
    methods = [
        "40명 × 8개 도시 환경",
        "HMD(360° VR) vs 모니터(2D) 비교",
        "동일 FOA Ambisonics + 헤드트래킹 적용",
        "Sennheiser HD-650 헤드폰",
        "4-channel ambisonic microphone (Soundfield SPS200)",
        "LAeq 57.2~79.4 dBA 범위의 8개 환경",
    ]
    for m in methods:
        pdf.body_text(m, indent=8, bullet=True)
    pdf.ln(1)
    pdf.body_text("핵심 결과:", bold=True)
    results = [
        "HMD 환경에서 부정 요소(인공물 소음)가 유의하게 높게 평가 (p<0.05)",
        "HMD: 공간 현실감(spatial presence)에 유리",
        "모니터: 전반적 환경 인식(overall awareness)에 유리",
        "LAeq 57.2~79.4 dBA 범위의 8개 환경에서 재현 방식별 지각 차이 체계적 검증",
    ]
    for r in results:
        pdf.body_text(r, indent=8, bullet=True)
    pdf.section_box(
        "Implication: XR 디바이스에서 Eclipsa Audio 평가 시 시각 재현 수준이 청각 판단을 변화시킴\n→ 평가 프로토콜에 반드시 통제 필요"
    )

    # S8 - DETAILED
    pdf.add_page()
    pdf.slide_header("S8", "축2: 헤드폰 vs 스피커 재생 방식 [상세]")
    pdf.label_value("논문:", "APAC_2019_Jeon et al (Applied Acoustics, IF 3.4)")
    pdf.label_value("RQ:", "헤드폰과 스피커 재생 방식이 사용자의 소리 품질 판단을 어떻게 바꾸는가?")
    pdf.ln(1)
    pdf.body_text("상세 방법론:", bold=True)
    methods = [
        "4가지 재생 환경 — 헤드폰 only / 스피커 only / 헤드폰+HMD / 스피커+HMD",
        "LAeq 40~65 dB 6단계",
        "Sennheiser HD-650 헤드폰",
        "Oculus Rift 2 HMD",
        "반무향실 배경소음 ~25 dBA",
    ]
    for m in methods:
        pdf.body_text(m, indent=8, bullet=True)
    pdf.ln(1)
    pdf.body_text("핵심 결과:", bold=True)
    results = [
        "HMD 유무에 따라 허용한계(allowance limit)와 성가심(annoyance) 평균 6%, 8% 차이",
        "50% 성가심 도달 음압레벨이 2.2 dBA 차이 (HMD 있을 때 더 민감)",
        "스피커+HMD 조합에서 가장 민감한 평가 → 실제 환경에 가장 근접",
    ]
    for r in results:
        pdf.body_text(r, indent=8, bullet=True)
    pdf.section_box(
        "Implication: Eclipsa Audio가 헤드폰 vs 스피커 재생 시 지각 차이를 정량화하는 프레임워크 제공"
    )

    # S9 - DETAILED
    pdf.ln(2)
    pdf.slide_header("S9", "축3: 바이노럴-비주얼 상호작용 [상세]")
    pdf.label_value("논문:", "B&E_2019_Jeon&Jo + B&E_2019_Jo et al (Building and Environment, IF 7.4) — 2편")
    pdf.label_value("RQ:", "HRTF와 HMD, 어느 것이 사용자 공간 지각에 더 지배적인가?")
    pdf.ln(1)
    pdf.body_text("상세 방법론:", bold=True)
    methods = [
        "2×2 요인설계 HRTF(유/무) × HMD(유/무) → 4개 조건",
        "도로교통소음 LAeq 40~65 dB + 층간소음 LAFmax 38~62 dB",
        "Sennheiser HD-650 헤드폰",
        "HTC VIVE Pro (도로소음) + Oculus Rift 2 (층간소음)",
        "CIPIC HRTF DB, azimuth 80°, elevation 0°",
    ]
    for m in methods:
        pdf.body_text(m, indent=8, bullet=True)
    pdf.ln(1)
    pdf.body_text("핵심 결과:", bold=True)
    results = [
        "HRTF 기여도 77% vs HMD 기여도 23% (도로소음)",
        "HMD 적용 시 저소음 환경에서 허용한계 6~7 dB 하락 (층간소음)",
        "HRTF+HMD 동시 적용 시 음상 외재화(externalization) 및 몰입감 유의하게 증가",
        "CIPIC HRTF DB 기반 바이노럴 합성 → 방향 인식·음폭 인식이 심리음향적 성가심의 주요 인자",
    ]
    for r in results:
        pdf.body_text(r, indent=8, bullet=True)
    pdf.section_box(
        "Implication: 바이노럴 렌더러 최적화 시 HRTF 개인화가 최우선 (77%) + Holographic Displays 시너지 근거"
    )

    # S10 - DETAILED
    pdf.add_page()
    pdf.slide_header("S10", "축4: 시청각 정보의 지각 영향 [상세]")
    pdf.label_value("대표 논문:", "B&E_2020_Jeon&Jo (Building and Environment, IF 7.4)")
    pdf.label_value("RQ:", "Audio와 Visual 정보가 전체 만족도에 각각 얼마나 기여하는가?")
    pdf.ln(1)
    pdf.body_text("상세 방법론:", bold=True)
    methods = [
        "FOA Ambisonics + HMD 헤드트래킹",
        "8개 도시 환경",
        "Audio-only, Visual-only, Audio-Visual 3개 평가 환경 비교",
    ]
    for m in methods:
        pdf.body_text(m, indent=8, bullet=True)
    pdf.ln(1)
    pdf.body_text("핵심 결과:", bold=True)
    results = [
        "Audio-Visual 만족도 기여: 청각 24% vs 시각 76%",
        "시각 정보 유무가 인공 소음·자연 소음 인지에 유의한 영향 (교차 감각 효과)",
        "오디오 정보가 landscape의 자연스러움(naturalness) 지각에 영향 — 새로운 발견",
        "만족도 모델: Audio-Visual 요소 기반 설명력 31%, Soundscape-Landscape 기반 설명력 51%",
    ]
    for r in results:
        pdf.body_text(r, indent=8, bullet=True)
    pdf.body_text("(참고: 구조방정식(SEM) 기반 경로 모델은 B&E_2021_Jo&Jeon에서 발전적으로 제시)", indent=5)
    pdf.section_box(
        "Implication: Spatial Audio 렌더링이 디스플레이 콘텐츠와 통합 설계되어야 만족도 극대화"
    )

    # S11 - DETAILED
    pdf.ln(2)
    pdf.slide_header("S11", "축5: 생태학적 타당성 (In-situ vs VR) [상세]")
    pdf.label_value("논문:", "SCS_2021_Jo&Jeon (Sustainable Cities and Society, IF 11.7)")
    pdf.label_value("RQ:", "VR 실험실 평가 결과를 실제 현장(in-situ)과 동일하게 신뢰할 수 있는가?")
    pdf.ln(1)
    pdf.body_text("상세 방법론:", bold=True)
    methods = [
        "50명 × 10개 다기능 도시 환경",
        "ISO 12913-2 Method A(설문), B(설문+개방형), C(서술 인터뷰) 비교",
        "VR vs In-situ 교차 검증",
        "4-channel FOA Ambisonics (Soundfield SPS200) + MixPre-6",
    ]
    for m in methods:
        pdf.body_text(m, indent=8, bullet=True)
    pdf.ln(1)
    pdf.body_text("핵심 결과:", bold=True)
    results = [
        "VR과 현장 평가에서 유사한 결과 확인 (음원 인식·감성 품질·전반적 선호도 일치)",
        "Pleasantness-Eventfulness 모델이 3가지 프로토콜 모두에서 재현",
        "Method C(인터뷰)에서 비음향 요인(맥락, 기대감, 장소감)의 지각 영향 추가 발견",
        "정량적 프로토콜 → 대규모·일반화 모델 / 정성적 프로토콜 → 심층 분석에 유리",
    ]
    for r in results:
        pdf.body_text(r, indent=8, bullet=True)
    pdf.section_box(
        "Implication: Eclipsa Audio 렌더링 품질을 VR 실험실에서 평가해도 실사용 환경 결과를 신뢰할 수 있음"
    )

    # S12-S18 same as V1
    pdf.add_page()
    pdf.body_text("※ S12~S18: 버전 1과 동일한 전체 내용 (수치 이미 포함)", bold=True)
    pdf.ln(2)

    pdf.slide_header("S12", "멀티모달 생리반응 모델링")
    pdf.label_value("논문:", "SCS_2023 (IF 11.7, 교신저자) + SR_2022 + IJERPH_2024")
    pdf.label_value("RQ:", "물리적 음향 파라미터로부터 사용자의 생리적 지각 반응을 예측할 수 있는가?")
    pdf.label_value("실험:", "60명 × 9환경 × 2일 / FOA + HMD + 헤드트래킹")
    pdf.label_value("측정:", "EEG (32ch) · HRV (5지표) · Eye-tracking")
    pdf.label_value("핵심 수치:", "CCA 0.80, CCA 0.78, SDNN +14.6%, TSI -9.5%")
    pdf.section_box(
        "→ Eclipsa Audio:\n"
        "  • EEG/HRV 프로토콜로 렌더링 품질 객관 검증\n"
        "  • 물리→지각 예측 모델로 자동 최적화 기초"
    )

    pdf.ln(2)
    pdf.slide_header("S13", "사운드스케이프 디자인 응용")
    pdf.label_value("논문:", "B&E_2021_Jo&Jeon + B&E_2022_Jo&Jeon (IF 7.4)")
    pdf.label_value("RQ:", "오디오-비주얼 상호작용이 실내 환경의 업무 품질과 생산성에 미치는 영향은?")
    pdf.label_value("핵심 결과:", "SEM 모델로 Audio → Visual → 만족도 경로 정량화 / A-V 일치 시 업무 선호도·생산성 유의 향상")
    pdf.section_box(
        "→ Eclipsa Audio: TV·사운드바 실내 환경별 최적 렌더링 설계의 이론적 근거"
    )

    pdf.add_page()
    pdf.slide_header("S14", "AVAS 사운드스케이프 디자인")
    pdf.label_value("출처:", "HMG 학술대회 + JASA 논문 (심사 중)")
    pdf.label_value("배경:", "EV 시대 → AVAS가 도시 음환경의 새로운 요소")
    pdf.label_value("데이터:", "17개 EV × 43개 AVAS 바이노럴 레코딩 / 134명 대규모 청감평가")
    pdf.label_value("방법론:", "3단계 감성어휘 (272→25→18쌍) → PCA → Comfort-Metallic 신규 축")
    pdf.label_value("핵심 수치:", "만족도 예측 92.5%, 34대 경쟁 DB")
    pdf.section_box(
        "→ Eclipsa Audio: 물리지표→만족도 예측 자동 튜닝 / Eclipsa vs Dolby Atmos 경쟁 분석"
    )

    pdf.ln(2)
    pdf.slide_header("S15", "연구 → 양산 실행력")
    pdf.label_value("적용:", "AVAS 브랜드 사운드 2.0 → EV3, IONIQ 5 양산")
    pdf.label_value("프로세스:", "음향 설계 → 청취 평가 → 시스템 검증 → 양산 전과정 주도")
    pdf.label_value("성과:", "특허 6건, 기술이전 5천만원, HMG 특별상, 웹 예측 툴")
    pdf.section_box(
        "→ 삼성리서치: 선행연구→제품 사양 전환 실행력 / 디자인·법규·NVH 부서간 협업"
    )

    pdf.ln(2)
    pdf.slide_header("S16", "AI 기반 오디오 처리")
    pdf.label_value("논문:", "SENSORS_2021 (SCI)")
    pdf.label_value("문제:", "학습 데이터 부족 (30명, 126건)")
    pdf.label_value("해결:", "RIR Convolution 증강 8→43,000건 / Loudness + Energy Ratio 신규 특징")
    pdf.label_value("핵심 수치:", "AI 84.9%/90.0%/0.84 vs 전문가 56.4%/40.7%/0.56")
    pdf.label_value("IP:", "국내+미국 특허, 기술이전 5천만원")
    pdf.label_value("A-JEPA 비전:", "Meta 자기지도 학습 + 음향 도메인 → 지능형 적응 렌더링")
    pdf.section_box(
        "→ Eclipsa Audio: RIR 증강→재생환경 학습데이터 / 도메인+AI 특징 설계"
    )

    pdf.add_page()
    pdf.slide_header("S17", "Contribution Plan (단기/중장기)")
    pdf.body_text("단기 | Eclipsa Audio 품질 검증", bold=True)
    for item in [
        "TV 2.0ch ~ 사운드바 11.1.4ch 지각 기반 정량 평가",
        "HRTF 바이노럴 렌더러 검증 + 개인화",
        "Eclipsa vs Dolby Atmos 감성 평가 프레임워크",
        "THX/TTA 인증에 지각 평가 데이터 제공",
        "Holographic Displays × Spatial Audio 통합 지각 연구",
    ]:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.ln(2)
    pdf.body_text("중장기 | AI 기반 적응형 렌더링", bold=True)
    for item in [
        "A-JEPA 기반 오디오 표현 학습 → 사용자 지각 대응",
        "재생 공간 자동 인식 + 렌더링 최적화",
        "Customized Audio 개인화",
        "IAMF 2.0 Object-based 지각 품질 가이드라인",
    ]:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.section_box(
        '"목표는 \'기술적으로 우수한 오디오\'가 아니라, 사용자가 진정으로 몰입을 느끼는 3D Audio-Visual 경험을 만드는 것"'
    )

    # S18
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(*WHITE)
    pdf.slide_header("S18", "Thank You")
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 30, 210, 267, 'F')
    pdf.set_text_color(*WHITE)
    pdf.set_font("AppleSDGothicNeo", "B", 18)
    pdf.set_xy(10, 100)
    pdf.cell(190, 10, "경청해 주셔서 감사합니다.", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 10, "질문 부탁드립니다.", align='C', ln=True)
    pdf.set_font("AppleSDGothicNeo", "", 11)
    pdf.set_xy(10, 160)
    pdf.cell(190, 7, "조현인 (Hyun In Jo, Ph.D.)", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 7, "best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo", align='C', ln=True)
    pdf.set_text_color(*DARK_GRAY)


# ============================================================
# VERSION 3 CONTENT
# ============================================================
def add_version3(pdf):
    pdf.version_cover(
        3,
        "최종 확정버전",
        "적절히 혼합\nS1~S18 전체 슬라이드 독립 완전 기술\n버전 1·2의 장점을 결합한 최종안"
    )

    # S1
    pdf.add_page()
    pdf.slide_header("S1", "Title Slide")
    pdf.body_text("디자인: Navy 풀 배경", bold=True)
    pdf.ln(1)
    pdf.label_value("제목:", "Spatial Audio Research & Perception-driven Quality Evaluation")
    pdf.label_value("부제:", "Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio")
    pdf.label_value("이름:", "조현인 (Hyun In Jo, Ph.D.)")
    pdf.label_value("현직:", "Senior Research Engineer, Hyundai Motor Company (NVH Division)")
    pdf.label_value("연락처:", "best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo")

    # S2
    pdf.ln(3)
    pdf.slide_header("S2", "About Me")
    pdf.body_text("좌측: 경력 타임라인", bold=True)
    for item in [
        "2013-2016: B.S. 건축공학, 한양대 (수석졸업, 조기졸업)",
        "2016-2022: Ph.D. 건축음향, 한양대 (석박통합, GPA 4.39/4.5)",
        "2022.03-08: Post-doc, 한국건설기술연구원",
        "2022.08-현재: 현대자동차 NVH 책임연구원",
        "→ Samsung Research, Spatial Audio",
    ]:
        pdf.body_text(item, indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("우측: 핵심 실적 카드 4개", bold=True)
    for item in [
        "SCI(E) 24편 (주저자 21편), h-index 18",
        "EAA Best Paper Award (ICA 2019), I-INCE Young Professional Award",
        "특허 6건 (국내+미국), 기술이전 5천만원",
        "UCL·소르본 등 국제공동연구, SATP 18개국 표준화 참여",
    ]:
        pdf.body_text(item, indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("하단: 핵심 전문성 4개 (Part와 1:1 대응)", bold=True)
    for item in [
        "① Spatial Audio & Immersive Rendering → Part I",
        "② Perception-driven Quality Evaluation → Part II",
        "③ Research-to-Product Execution → Part III",
        "④ AI-driven Audio Processing → Part IV",
    ]:
        pdf.body_text(item, indent=5, bullet=True)

    # S3
    pdf.add_page()
    pdf.slide_header("S3", "핵심 질문 제기")
    pdf.body_text("상단 (구체적 수치):", bold=True)
    pdf.body_text("THD 0.01%, 주파수 응답 ±0.5dB — 공학 스펙이 완벽해도 사용자가 '좋다'고 느끼지 않을 수 있다", indent=5, bullet=True)
    pdf.ln(1)
    pdf.body_text("중상단 (본인 연구 결과):", bold=True)
    pdf.body_text("시각 맥락만으로 오디오 만족도가 76% 좌우된다면? (본인 연구 결과)", indent=5, bullet=True)
    pdf.ln(1)
    pdf.body_text("중앙 (핵심 질문):", bold=True)
    pdf.section_box(
        '"사용자가 진짜 몰입을 느끼는 3D Audio-Visual 경험을 어떻게 설계하고 검증할 것인가?"'
    )
    pdf.body_text("하단 (4 Part 로드맵):", bold=True)
    for item in [
        "Part I: Spatial Audio 기술 역량 (8분)",
        "Part II: 지각 기반 평가 방법론 (3분)",
        "Part III: 제품 적용 AVAS (3분)",
        "Part IV: AI 확장 + Contribution (4분)",
    ]:
        pdf.body_text(item, indent=5, bullet=True)

    # S4
    pdf.ln(3)
    pdf.slide_header("S4", "사운드스케이프란?")
    pdf.body_text("상단 대비 구조:", bold=True)
    pdf.body_text("Traditional — \"소음이 얼마나 큰가?\" dB 기반", indent=5, bullet=True)
    pdf.body_text("Soundscape — \"소리가 어떻게 경험되는가?\" 인간 지각 중심", indent=5, bullet=True)
    pdf.ln(2)
    pdf.body_text("ISO 12913 정의:", bold=True)
    pdf.section_box(
        '"Acoustic environment as perceived or experienced and/or understood by a person or people, in context"'
    )
    pdf.body_text("하단: Pleasant-Eventful 2차원 모델 다이어그램", indent=5, bullet=True)

    # S5
    pdf.add_page()
    pdf.slide_header("S5", "왜 사운드스케이프가 Spatial Audio에 직결되는가")
    pdf.body_text("5행 연결 테이블:", bold=True)
    rows_v3 = [
        ("1. 소리를 경험으로 평가 (dB가 아닌 사용자 지각 중심)",
         "렌더링 품질을 THD·주파수응답 같은 공학 지표가 아닌 사용자가 느끼는 공간감·몰입감으로 평가"),
        ("2. 오디오-비주얼 상호작용 (시각 맥락이 청각 지각을 최대 76% 좌우)",
         "Display + Audio 통합 설계 — Holographic Displays × Spatial Audio 시너지의 지각적 근거"),
        ("3. 재생 환경에 따라 동일 음원의 지각이 달라짐",
         "거실·침실·차량 등 재생 공간별 렌더링 최적화 — 같은 원리, 다른 스케일"),
        ("4. 개인차 (소음 민감도·성격·청력 프로필)",
         "Customized Audio 개인화 — 사용자별 최적 렌더링의 이론적 근거"),
        ("5. 대규모 지각 평가 프로토콜 설계·실행 역량 (ISO 12913 + SATP 18개국, 134명)",
         "Eclipsa Audio 품질 벤치마킹 및 인증 기준 수립"),
    ]
    for k, v in rows_v3:
        pdf.body_text(k, indent=5, bold=True)
        pdf.body_text("→ " + v, indent=12)
        pdf.ln(1)
    pdf.section_box(
        '"신호처리가 \'어떻게 구현할 것인가\'라면, 저의 전문성은 \'사용자가 어떻게 경험할 것인가\'를 설계하고 검증하는 것입니다"'
    )

    # S6
    pdf.add_page()
    pdf.slide_header("S6", "Spatial Audio 연구 체계도 (Timeline Flow 버전)")
    pdf.body_text("5개 축이 좌→우 흐름, 상단: 방법론 카드, 중앙: 연결 노드, 하단: 핵심 수치+시사점", bold=True)
    pdf.ln(2)
    axes_v3 = [
        ("축1: 시각 재현 방식", "APAC'22, IF 3.4", "HMD vs Monitor, 40명×8환경", "p<0.05 → XR 대응"),
        ("축2: 헤드폰 vs 스피커", "APAC'19, IF 3.4", "4환경, LAeq 40-65dB", "2.2dBA → 지각 정량화"),
        ("축3: 바이노럴-비주얼", "B&E'19 ×2, IF 7.4", "2×2 HRTF×HMD, 320pts", "77% → HRTF 개인화"),
        ("축4: 시청각 정보", "B&E'20, IF 7.4", "A/V/AV 3조건, R²=51%", "76% → Display 시너지"),
        ("축5: 생태학적 타당성", "SCS'21, IF 11.7", "50×10, ISO A/B/C", "VR≈In-situ → 검증 파이프라인"),
    ]
    for name, paper, method, result in axes_v3:
        pdf.set_font("AppleSDGothicNeo", "B", 9)
        pdf.set_text_color(*ACCENT_BLUE)
        pdf.set_x(10)
        pdf.cell(60, 5, name, ln=False)
        pdf.set_font("AppleSDGothicNeo", "", 9)
        pdf.set_text_color(*DARK_GRAY)
        pdf.cell(40, 5, paper, ln=False)
        pdf.cell(55, 5, method, ln=False)
        pdf.cell(35, 5, result, ln=True)
        pdf.ln(1)
    pdf.ln(2)
    pdf.section_box(
        "→ Eclipsa Audio 렌더러 최적화\n"
        "→ Holographic Displays 시너지\n"
        "→ VR 품질 검증 파이프라인"
    )

    # S7
    pdf.ln(2)
    pdf.slide_header("S7", "축1: 시각 재현 방식의 영향")
    pdf.label_value("논문:", "APAC_2022_Jo&Jeon (Applied Acoustics, IF 3.4)")
    pdf.label_value("RQ:", "같은 Spatial Audio를 HMD vs 모니터로 볼 때, 사용자 지각이 얼마나 달라지는가?")
    pdf.label_value("핵심 수치:", "40명 × 8환경 / HMD에서 부정·긍정 요소 모두 더 민감하게 인식 (p<0.05)")
    pdf.label_value("한 줄 결과:", "HMD = 공간 현실감↑ / 모니터 = 전반적 인식↑ → 시각 재현 수준이 오디오 판단을 변화시킴")
    pdf.section_box(
        "→ Eclipsa Audio: XR 디바이스 대응 시, 시각 조건 통제가 품질 평가의 전제\n"
        "[그림] APAC_2022 논문 Fig"
    )

    # S8
    pdf.add_page()
    pdf.slide_header("S8", "축2: 헤드폰 vs 스피커")
    pdf.label_value("논문:", "APAC_2019_Jeon et al (Applied Acoustics, IF 3.4)")
    pdf.label_value("RQ:", "헤드폰과 스피커 재생 방식이 사용자의 소리 품질 판단을 어떻게 바꾸는가?")
    pdf.label_value("핵심 수치:", "허용한계 6% 차이 / 성가심 8% 차이 / 50% 성가심 도달 SPL 2.2 dBA 차이")
    pdf.label_value("한 줄 결과:", "스피커+HMD 조합이 실제 환경에 가장 근접 → 가장 민감한 반응")
    pdf.section_box(
        "→ Eclipsa Audio: 헤드폰(바이노럴) vs 스피커(멀티채널) 재생 시 지각 차이 정량화 기준\n"
        "[그림] APAC_2019 논문 Fig"
    )

    # S9
    pdf.ln(2)
    pdf.slide_header("S9", "축3: 바이노럴-비주얼 상호작용")
    pdf.label_value("논문:", "B&E_2019 × 2편 (Building and Environment, IF 7.4)")
    pdf.label_value("RQ:", "HRTF와 HMD, 어느 것이 사용자 공간 지각에 더 지배적인가?")
    pdf.body_text("핵심 수치 (크게): HRTF 77% vs HMD 23%", bold=True, indent=5)
    pdf.body_text("보조: HRTF+HMD 시 음상 외재화·몰입감 유의 증가, VR에서 허용한계 6~7 dB 하락", indent=8, bullet=True)
    pdf.section_box(
        "→ Eclipsa Audio: HRTF 개인화 = 렌더러 최적화의 최우선 과제 (지각 기여도 77%)\n"
        "[그림] B&E_2019 논문 Fig + 기존 PPT"
    )

    # S10
    pdf.ln(2)
    pdf.slide_header("S10", "축4: 시청각 정보의 지각 영향")
    pdf.label_value("대표 논문:", "B&E_2020_Jeon&Jo (Building and Environment, IF 7.4)")
    pdf.label_value("RQ:", "Audio와 Visual 정보가 전체 만족도에 각각 얼마나 기여하는가?")
    pdf.body_text("핵심 수치 (크게): 청각 24% vs 시각 76%", bold=True, indent=5)
    pdf.body_text("보조: 만족도 모델 설명력 51% / cross-modal effect on naturalness", indent=8, bullet=True)
    pdf.body_text("참고: SEM 경로 모델은 B&E_2021_Jo&Jeon에서 발전적 제시", indent=8, bullet=True)
    pdf.section_box(
        "→ Eclipsa Audio: Display + Audio 통합 설계가 만족도 극대화의 핵심 → Holographic Displays 시너지\n"
        "[그림] B&E_2020 논문 Fig"
    )

    # S11
    pdf.add_page()
    pdf.slide_header("S11", "축5: 생태학적 타당성 (In-situ vs VR)")
    pdf.label_value("논문:", "SCS_2021_Jo&Jeon (Sustainable Cities and Society, IF 11.7)")
    pdf.label_value("RQ:", "VR 실험실 평가 결과를 실제 현장(in-situ)과 동일하게 신뢰할 수 있는가?")
    pdf.label_value("핵심 수치:", "50명 × 10환경 / ISO 12913-2 3가지 프로토콜 모두에서 VR ≈ In-situ 유사 결과")
    pdf.label_value("한 줄 결과:", "FOA 바이노럴 + 헤드트래킹의 높은 생태학적 타당성 실증")
    pdf.section_box(
        "→ Eclipsa Audio: VR 기반 실험실에서 렌더링 품질 평가 → 실사용 환경 결과를 신뢰할 수 있음\n"
        "[그림] SCS_2021 논문 Appendix A"
    )

    # S12
    pdf.ln(2)
    pdf.slide_header("S12", "멀티모달 생리반응 모델링")
    pdf.label_value("논문:", "SCS_2023 (IF 11.7, 교신저자) + SR_2022 + IJERPH_2024")
    pdf.label_value("RQ:", "물리적 음향 파라미터로부터 사용자의 생리적 지각 반응을 예측할 수 있는가?")
    pdf.label_value("실험:", "60명 × 9환경 × 2일 / FOA + HMD + 헤드트래킹")
    pdf.label_value("측정:", "EEG (32ch, α/β ratio) · HRV (5지표) · Eye-tracking")
    pdf.body_text("핵심 수치 카드:", bold=True, indent=5)
    for val in ["CCA 0.80", "CCA 0.78", "SDNN +14.6%", "TSI -9.5%"]:
        pdf.body_text(val, indent=10, bullet=True)
    pdf.section_box(
        "→ Eclipsa Audio:\n"
        "  • EEG/HRV 프로토콜 → 렌더링 품질 객관 검증 (설문 의존 탈피)\n"
        "  • 물리 파라미터 → 지각 예측 모델 → 렌더링 자동 최적화 기초\n"
        "  • A-V 일치 시 회복 효과 → Display+Audio 통합의 생리적 근거\n"
        "[그림] SCS_2023 HRV 차트 + IJERPH_2024 Eye-tracking 히트맵"
    )

    # S13
    pdf.add_page()
    pdf.slide_header("S13", "사운드스케이프 디자인 응용")
    pdf.label_value("논문:", "B&E_2021_Jo&Jeon (IF 7.4) + B&E_2022_Jo&Jeon (IF 7.4)")
    pdf.label_value("RQ:", "오디오-비주얼 상호작용이 실내 환경의 업무 품질과 생산성에 미치는 영향은?")
    pdf.label_value("핵심 결과:", "SEM 모델로 Audio→Visual→만족도 경로 정량화 / A-V 일치 시 업무 선호도·생산성 유의 향상")
    pdf.section_box(
        "→ Eclipsa Audio: TV·사운드바 실내 환경별 최적 렌더링 설계의 이론적 근거\n"
        "[그림] B&E_2021 SEM 경로 모델"
    )

    # S14
    pdf.ln(2)
    pdf.slide_header("S14", "AVAS 사운드스케이프 디자인")
    pdf.label_value("출처:", "HMG 학술대회 특별상 + JASA 논문 (심사 중)")
    pdf.label_value("배경:", "EV 시대 → AVAS가 도시 음환경의 새로운 요소. 사운드스케이프 개념 최초 적용")
    pdf.label_value("데이터:", "17개 EV × 43개 AVAS 바이노럴 레코딩 DB / 134명 대규모 청감평가")
    pdf.label_value("방법론:", "3단계 감성어휘 선정 (272개 → 25쌍 → 18쌍) → PCA → 신규 감성축")
    pdf.label_value("핵심 수치:", "Comfort-Metallic 신규 평가축 / 만족도 예측 92.5% / 34대 경쟁 DB")
    pdf.section_box(
        "→ Eclipsa Audio:\n"
        "  • 물리지표→만족도 예측 → 렌더링 파라미터 자동 튜닝 기초\n"
        "  • 감성 평가 프레임워크 → Eclipsa vs Dolby Atmos 경쟁 분석\n"
        "  • 134명 대규모 청감평가 역량 → 디바이스 품질 인증 프로세스\n"
        "[그림] Comfort-Metallic PCA 브랜드 포지셔닝"
    )

    # S15
    pdf.add_page()
    pdf.slide_header("S15", "연구 → 양산 실행력")
    pdf.label_value("적용:", "AVAS 브랜드 사운드 2.0 → EV3, IONIQ 5 양산")
    pdf.label_value("프로세스:", "음향 설계 → 청취 평가 → 시스템 검증 → 양산 전 과정 주도")
    pdf.label_value("성과:", "특허 6건 (국내+미국), 기술이전 5천만원, HMG 학술대회 특별상, 웹 예측 툴")
    pdf.section_box(
        "→ 삼성리서치:\n"
        "  • 선행연구→제품 사양 전환→개발 일정·품질 기준 조율 실행력\n"
        "  • 디자인·법규·NVH 부서 간 AVAS 프로젝트 조율 → 파트 간 협업 역량\n"
        "[그림] 양산 적용 프로세스"
    )

    # S16
    pdf.ln(2)
    pdf.slide_header("S16", "AI 기반 오디오 처리")
    pdf.label_value("논문:", "SENSORS_2021 (SCI)")
    pdf.label_value("문제:", "AI 오디오 분류에서 학습 데이터 부족 (30명, 126건) + 기존 증강은 환경 음향 미반영")
    pdf.label_value("해결:", "RIR Convolution 기반 증강 8건→43,000건 / 새 특징: Loudness + Energy Ratio")
    pdf.body_text("핵심 수치 (AI vs 전문가 8명):", bold=True, indent=5)
    pdf.body_text("정확도 84.9% vs 56.4%", indent=10, bullet=True)
    pdf.body_text("민감도 90.0% vs 40.7%", indent=10, bullet=True)
    pdf.body_text("AUC 0.84 vs 0.56", indent=10, bullet=True)
    pdf.label_value("IP:", "국내 특허 + 미국 특허 + 기술이전 5천만원")
    pdf.body_text("A-JEPA 비전: Meta 자기지도 학습 + 음향 도메인 지식 → AI 오디오 표현 ↔ 사용자 지각 대응 → 지능형 적응 렌더링 기초", indent=5, bullet=True)
    pdf.section_box(
        "→ Eclipsa Audio:\n"
        "  • RIR 증강 → 다양한 재생 환경 학습 데이터 생성\n"
        "  • 음향 도메인 + AI → 물리적 특성 반영한 특징 설계\n"
        "  • 소량→대규모 학습셋 → 신규 디바이스 빠른 모델 적응\n"
        "[그림] 5층 LSTM 구조도 + ROC Curve/AUC"
    )

    # S17
    pdf.add_page()
    pdf.slide_header("S17", "Contribution Plan (3단계 타임라인)")

    pdf.body_text("[입사 ~6개월 / 즉시 기여]", bold=True)
    items_phase1 = [
        "Eclipsa Audio: TV~사운드바 지각 품질 벤치마킹 체계",
        "Eclipsa Audio: Eclipsa vs Dolby Atmos 비교 프레임워크",
        "AI 전환: 지각 평가 데이터 + AI 분석 파이프라인",
        "AI 전환: RIR 증강 재생환경 학습데이터",
        "파트 시너지: Holographic Displays 파트와 통합 A-V 지각 실험 설계",
        "인증·표준: THX/TTA 인증에 지각 평가 데이터 제공",
    ]
    for item in items_phase1:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.ln(2)

    pdf.body_text("[6개월 ~ 2년 / 과제 확장]", bold=True)
    items_phase2 = [
        "Eclipsa Audio: HRTF 바이노럴 개인화",
        "Eclipsa Audio: IAMF 2.0 지각 품질 가이드라인",
        "AI 전환: A-JEPA 기반 오디오 표현 학습 → 사용자 지각 대응",
        "AI 전환: 재생 공간 자동 인식 + 적응형 렌더링",
        "파트 시너지: 3D 시각 + Spatial Audio 동기화 프로토콜",
        "인증·표준: 사내 오디오 품질 인증 프로그램 체계화",
    ]
    for item in items_phase2:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.ln(2)

    pdf.body_text("[2년~ / Lab 비전 주도]", bold=True)
    items_phase3 = [
        "AI 전환: AI 기반 Customized Audio 개인화 시스템",
        "파트 시너지: Lab 통합 비전 — 홀로그래픽 디스플레이 + 공간 오디오 통합 설계 가이드라인 주도",
        "인증·표준: 국제 표준화 활동 (ISO/SATP 경험 활용)",
    ]
    for item in items_phase3:
        pdf.body_text(item, indent=8, bullet=True)
    pdf.ln(2)

    pdf.section_box(
        '"신호처리가 만드는 기술 위에, 사용자가 경험하는 품질을 설계합니다"'
    )

    # S18
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_text_color(*WHITE)
    pdf.slide_header("S18", "Thank You")
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 30, 210, 267, 'F')
    pdf.set_text_color(*WHITE)
    pdf.set_font("AppleSDGothicNeo", "B", 18)
    pdf.set_xy(10, 90)
    pdf.cell(190, 10, "경청해 주셔서 감사합니다.", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 10, "질문 부탁드립니다.", align='C', ln=True)
    pdf.set_font("AppleSDGothicNeo", "B", 12)
    pdf.set_xy(10, 150)
    pdf.cell(190, 7, "조현인 (Hyun In Jo, Ph.D.)", align='C', ln=True)
    pdf.set_font("AppleSDGothicNeo", "", 10)
    pdf.set_x(10)
    pdf.cell(190, 6, "best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo", align='C', ln=True)
    pdf.set_x(10)
    pdf.cell(190, 6, "Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio", align='C', ln=True)
    pdf.set_text_color(*DARK_GRAY)


def main():
    print("Generating PDF...")
    pdf = SlidePDF()

    # Cover page
    add_cover_page(pdf)

    # Version 1
    print("Adding Version 1...")
    add_version1(pdf)

    # Version 2
    print("Adding Version 2...")
    add_version2(pdf)

    # Version 3
    print("Adding Version 3...")
    add_version3(pdf)

    # Save
    pdf.output(OUTPUT_PATH)
    print(f"PDF saved to: {OUTPUT_PATH}")

    import os
    size = os.path.getsize(OUTPUT_PATH)
    print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
