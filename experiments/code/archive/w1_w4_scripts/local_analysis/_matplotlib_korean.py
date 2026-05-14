#!/usr/bin/env python3
"""
matplotlib 한글 폰트 설정 helper.

import 시 자동 적용:
    from _matplotlib_korean import enable_korean
    enable_korean()
"""
from __future__ import annotations

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt


KOREAN_FONT_PRIORITY = [
    "Apple SD Gothic Neo",     # macOS preferred
    "AppleGothic",
    "Nanum Gothic",
    "NanumGothic",
    "Malgun Gothic",            # Windows
]


def enable_korean() -> str | None:
    """matplotlib 의 default font 를 사용 가능한 한글 폰트로 설정.

    Returns: 적용된 font name (없으면 None).
    """
    available = {f.name for f in fm.fontManager.ttflist}
    chosen = None
    for name in KOREAN_FONT_PRIORITY:
        if name in available:
            chosen = name
            break
    if chosen:
        matplotlib.rcParams["font.family"] = chosen
        # minus 부호 깨짐 방지
        matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen


if __name__ == "__main__":
    chosen = enable_korean()
    if chosen:
        print(f"[matplotlib_korean] applied: {chosen}")
    else:
        print(f"[matplotlib_korean] no Korean font found in: {KOREAN_FONT_PRIORITY}")
