"""
디자인 5 종 컬러·타이포 토큰. Research/build_presentation_v2.py +
design_samples.html + s6_redesign.html 의 시각 패턴에서 도출.
"""
from dataclasses import dataclass
from pptx.dml.color import RGBColor


def rgb(hex_str: str) -> RGBColor:
    s = hex_str.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


@dataclass
class Theme:
    name: str               # display name
    code: str               # filename suffix
    description: str        # 한 줄 디자인 설명

    # 코어 팔레트
    primary: RGBColor       # 가장 진한 브랜드 색
    accent: RGBColor        # 강조 (호버·하이라이트)
    bg_dark: RGBColor       # 어두운 배경 (표지)
    bg_light: RGBColor      # 흰/회색 본문 배경
    card: RGBColor          # 카드 배경
    border: RGBColor        # 보더
    text: RGBColor          # 본문
    text_dim: RGBColor      # 부제·각주
    text_white: RGBColor    # 어두운 배경 위
    success: RGBColor       # 통계 유의 강조 (별표)
    warn: RGBColor          # boundary / 주의

    # 타이포
    font_main: str = "Apple SD Gothic Neo"
    font_mono: str = "Menlo"
    font_serif: str = "Apple SD Gothic Neo"

    # 디자인 토큰 (선택)
    layout_style: str = "header_bar"  # header_bar | side_nav | gradient_glass | hub_spoke | editorial


# ─────────────────────────────────────────
# A. Navy Corporate — Samsung Research 정통
# ─────────────────────────────────────────
NAVY = Theme(
    name="Navy Corporate",
    code="navy",
    description="Samsung Research 정통 — 어두운 표지 + 흰 본문 + 파란 헤더 바",
    primary=rgb("#13289F"),
    accent=rgb("#3D7DDE"),
    bg_dark=rgb("#0A0F1E"),
    bg_light=rgb("#FFFFFF"),
    card=rgb("#F0F4F8"),
    border=rgb("#E7E6E2"),
    text=rgb("#1A1A2E"),
    text_dim=rgb("#5B718D"),
    text_white=rgb("#FFFFFF"),
    success=rgb("#0F766E"),
    warn=rgb("#C2410C"),
    layout_style="header_bar",
)

# ─────────────────────────────────────────
# B. Modern Glass — 그라디언트 + 글래스 카드
# ─────────────────────────────────────────
GLASS = Theme(
    name="Modern Glass",
    code="glass",
    description="딥 인디고 그라디언트 표지 + 글래스 카드 + 큰 메트릭 숫자",
    primary=rgb("#1E1B4B"),     # indigo-950
    accent=rgb("#8B5CF6"),      # violet-500
    bg_dark=rgb("#0F172A"),     # slate-900
    bg_light=rgb("#F8FAFC"),    # slate-50
    card=rgb("#FFFFFF"),
    border=rgb("#E2E8F0"),
    text=rgb("#0F172A"),
    text_dim=rgb("#64748B"),
    text_white=rgb("#F1F5F9"),
    success=rgb("#10B981"),
    warn=rgb("#F59E0B"),
    layout_style="gradient_glass",
)

# ─────────────────────────────────────────
# C. Editorial Mono — 흑백 + 1 강조
# ─────────────────────────────────────────
EDITORIAL = Theme(
    name="Editorial Mono",
    code="editorial",
    description="잡지·저널 스타일 — 흑백 + 빨강 1 강조 + 큰 타이포",
    primary=rgb("#171717"),     # near black
    accent=rgb("#DC2626"),      # red-600
    bg_dark=rgb("#0A0A0A"),
    bg_light=rgb("#FAFAF9"),
    card=rgb("#FFFFFF"),
    border=rgb("#D4D4D4"),
    text=rgb("#171717"),
    text_dim=rgb("#737373"),
    text_white=rgb("#FAFAF9"),
    success=rgb("#16A34A"),
    warn=rgb("#EA580C"),
    layout_style="editorial",
)

# ─────────────────────────────────────────
# D. Bold Cards — 강한 색 카드 그리드
# ─────────────────────────────────────────
BOLD = Theme(
    name="Bold Cards",
    code="bold",
    description="좌측 dot navigation + 진한 색 카드 + 강한 대비",
    primary=rgb("#0C4A6E"),     # sky-900
    accent=rgb("#0EA5E9"),      # sky-500
    bg_dark=rgb("#082F49"),
    bg_light=rgb("#F0F9FF"),
    card=rgb("#FFFFFF"),
    border=rgb("#BAE6FD"),
    text=rgb("#0C4A6E"),
    text_dim=rgb("#475569"),
    text_white=rgb("#F0F9FF"),
    success=rgb("#15803D"),
    warn=rgb("#B45309"),
    layout_style="side_nav",
)

# ─────────────────────────────────────────
# E. Hub-Spoke Spatial — 5축 다이어그램형
# ─────────────────────────────────────────
HUB = Theme(
    name="Hub-Spoke Spatial",
    code="hub",
    description="중앙 hub + 5 spoke 카드 + 흐름 다이어그램",
    primary=rgb("#0B1D6F"),
    accent=rgb("#0689D8"),
    bg_dark=rgb("#0B1D6F"),
    bg_light=rgb("#FAFBFD"),
    card=rgb("#FFFFFF"),
    border=rgb("#E7E6E2"),
    text=rgb("#1A1A2E"),
    text_dim=rgb("#5B718D"),
    text_white=rgb("#FFFFFF"),
    success=rgb("#0F766E"),
    warn=rgb("#C2410C"),
    layout_style="hub_spoke",
)


# ─────────────────────────────────────────
# F. Premium Glassmorphism — 하이엔드 다크 모드
# ─────────────────────────────────────────
PREMIUM = Theme(
    name="Premium Glass",
    code="gemini",
    description="하이엔드 다크 모드 + 블루/인디고 그라디언트 + 글래스 카드 + 큰 타이포",
    primary=rgb("#3B82F6"),     # blue-500
    accent=rgb("#6366F1"),      # indigo-500
    bg_dark=rgb("#050505"),     # pure black
    bg_light=rgb("#0A0A0A"),    # deep slate (전체 다크)
    card=rgb("#111827"),        # slate-900
    border=rgb("#1F2937"),      # slate-800
    text=rgb("#F9FAFB"),        # gray-50
    text_dim=rgb("#9CA3AF"),    # gray-400
    text_white=rgb("#FFFFFF"),
    success=rgb("#10B981"),
    warn=rgb("#F59E0B"),
    layout_style="premium_glass",
)


# ─────────────────────────────────────────
# G. Academic Light — Apple 스타일 화이트 + 블루
# ─────────────────────────────────────────
ACADEMIC = Theme(
    name="Academic Light",
    code="academic",
    description="Apple 클린 스타일 — 흰 배경 + 정교한 타이포 + 선명한 블루 액센트",
    primary=rgb("#2563EB"),     # blue-600
    accent=rgb("#3B82F6"),      # blue-500
    bg_dark=rgb("#0F172A"),     # 표지 어두운 강조 (slate-900)
    bg_light=rgb("#FFFFFF"),
    card=rgb("#F8FAFC"),        # slate-50
    border=rgb("#E2E8F0"),      # slate-200
    text=rgb("#0F172A"),
    text_dim=rgb("#64748B"),    # slate-500
    text_white=rgb("#FFFFFF"),
    success=rgb("#059669"),
    warn=rgb("#D97706"),
    layout_style="header_bar",
)


# ─────────────────────────────────────────
# H. Swiss Minimal — 매거진 (세리프 + 레드)
# ─────────────────────────────────────────
SWISS = Theme(
    name="Swiss Minimal",
    code="swiss",
    description="매거진 / 저널 스타일 — 세리프 + 레드 포인트 + 비대칭 여백",
    primary=rgb("#171717"),     # near black
    accent=rgb("#DC2626"),      # red-600
    bg_dark=rgb("#0A0A0A"),
    bg_light=rgb("#FAFAF9"),
    card=rgb("#FFFFFF"),
    border=rgb("#D4D4D4"),
    text=rgb("#0A0A0A"),
    text_dim=rgb("#737373"),
    text_white=rgb("#FAFAF9"),
    success=rgb("#16A34A"),
    warn=rgb("#EA580C"),
    font_main="Apple SD Gothic Neo",  # 본문은 동일 (한국어)
    font_serif="Apple SD Gothic Neo",
    layout_style="editorial",
)


# ─────────────────────────────────────────
# I. Soft Gradient — 트렌디 SaaS
# ─────────────────────────────────────────
SOFT = Theme(
    name="Soft Gradient",
    code="soft",
    description="트렌디 SaaS / 모던 스타트업 — 라이트 보라 배경 + 글래스 카드 + 둥근 모서리",
    primary=rgb("#6366F1"),     # indigo-500
    accent=rgb("#8B5CF6"),      # violet-500
    bg_dark=rgb("#312E81"),     # indigo-900
    bg_light=rgb("#F5F3FF"),    # 연한 보라
    card=rgb("#FFFFFF"),
    border=rgb("#DDD6FE"),      # violet-200
    text=rgb("#1E1B4B"),        # indigo-950
    text_dim=rgb("#6B7280"),
    text_white=rgb("#FFFFFF"),
    success=rgb("#10B981"),
    warn=rgb("#F59E0B"),
    layout_style="gradient_glass",
)


THEMES = {
    "navy": NAVY,
    "glass": GLASS,
    "editorial": EDITORIAL,
    "bold": BOLD,
    "hub": HUB,
    "gemini": PREMIUM,
    "academic": ACADEMIC,
    "swiss": SWISS,
    "soft": SOFT,
}
