"""
중간발표 콘텐츠 데이터 — 13 슬라이드 (10 분 발표용).
디자인 5 종은 이 데이터를 공유하고 시각만 달리 한다.

캡스톤 6 필수 항목:
1. 해결하고자 하는 문제           → S3
2. 기존 연구의 현황 및 한계점     → S4 + S5
3. 차별성 및 제안 연구의 중요성   → S6
4. 연구 및 실험 방법              → S7~S11
5. 진행 상황 및 향후 계획         → S12 + S13
6. 팀원별 역할 분담              → S14 (보고서 한정, 발표는 표지·끝맺음에 배치)
"""

# ─────────────────────────────────────────
# 표지 / 종료 메타
# ─────────────────────────────────────────
TITLE_MAIN = "Exqutor 벡터 카디널리티 추정의 단일 테이블 사각지대와 Skew-Aware Sampling"
TITLE_SUB = "Pivot A BERNOULLI 교체 + Pivot C KM20 Stratified — 3 데이터셋 5-seed CI 검증"
TEAM = "속도는벡터"
COURSE = "연세대학교 컴퓨터과학과 · 2026-1 캡스톤 디자인"
ADVISOR = "지도교수 박광현 · 지도연구원 임채림 석사"
MEMBERS = ["박세은 (팀장)", "강재현", "조현빈", "이동욱"]
DATE = "2026-04-28"

# ─────────────────────────────────────────
# 핵심 수치 (모든 디자인 공통, 5-seed CI 출처 일관)
# ─────────────────────────────────────────
KEY_METRICS = {
    "deep1m_50": {"value": "+1.64%", "ci": "[+1.11, +2.18]", "label": "DEEP 1M · s=0.500"},
    "deep8m_50": {"value": "+1.76%", "ci": "[+0.65, +2.86]", "label": "DEEP 8M · s=0.500"},
    "sift_50":   {"value": "+3.07%", "ci": "[+2.66, +3.48]", "label": "SIFT 1.5M · s=0.500"},
    "level2_1":  {"value": "+19.6%p", "ci": "Level 2 (공간 인식)", "label": "DEEP 1M · s=0.010"},
    "pivot_a":   {"value": "+9.6%", "ci": "p < 0.001", "label": "BERNOULLI vs SYSTEM · s=0.500"},
    "negative_8": {"value": "8/8", "ci": "|ρ| < 0.2", "label": "Skew 지표 모두 negative"},
}

# ─────────────────────────────────────────
# Slide 데이터
# ─────────────────────────────────────────

S1_COVER = {
    "title": TITLE_MAIN,
    "subtitle": TITLE_SUB,
    "team": TEAM,
    "course": COURSE,
    "advisor": ADVISOR,
    "members": MEMBERS,
    "date": DATE,
}

S2_TOC = {
    "title": "Table of Contents",
    "sections": [
        ("01", "Problem", "벡터 카디널리티 추정의 사각지대"),
        ("02", "Background", "Exqutor 의 두 해법과 한계"),
        ("03", "Our Approach", "Skew-Aware Sampling 의 차별성"),
        ("04", "Experiments", "RQ1 · RQ2 · RQ3 설계와 결과"),
        ("05", "Plan", "현재 진행 상황 및 향후 계획"),
    ],
}

S3_PROBLEM = {
    "title": "1. 해결하고자 하는 문제",
    "headline": "벡터 조건의 선택도를 시스템마다 \"고정 비율\"로 추정한다",
    "fixed_ratio": [
        ("pgvector",  "33.3%",  "PostgreSQL operator default"),
        ("VBASE",     "50.0%",  "fixed estimator"),
        ("DuckDB",    "100%",  "scan all rows"),
    ],
    "reality": [
        "실제 선택도는 query 에 따라 0.001% ~ 90% 의 광범위한 분포",
        "옵티마이저가 잘못된 실행 계획 선택 → nested loop ↔ hash join, index 사용 여부",
        "이미지 검색 / 추천 / RAG retrieval 등 단일 테이블 vector range query 에서 빈번",
    ],
    "tagline": "\"기술적으로 좋은 추정\" vs \"실행 계획에 진짜 도움 되는 추정\" — 이 간극을 어떻게 메울 것인가?",
}

S4_BACKGROUND = {
    "title": "2-Ⅰ. 기존 연구의 현황 — Exqutor 의 두 보완책",
    "subtitle": "arXiv:2512.09695v2 (2024) · 4/3 교수님 미팅에서 본 논문 채택",
    "solutions": [
        {
            "name": "ECQO",
            "headline": "HNSW 인덱스가 있을 때",
            "detail": "HNSW range query 를 직접 실행해 1~2ms 로 정확 카디널리티 산출",
            "metric": "1~2 ms",
            "metric_label": "정확 카디널리티",
        },
        {
            "name": "Adaptive Sampling",
            "headline": "인덱스가 없을 때",
            "detail": "모멘텀 기반 동적 샘플링 — sample size 를 점진 확장하며 분산 수렴 판정",
            "metric": "1000×",
            "metric_label": "pgvector 대비 최대",
        },
    ],
    "achievements": "pgvector 1000×, VBASE 10000×, DuckDB 1.5~37× 성능 향상 (논문 보고)",
}

S5_LIMITATION = {
    "title": "2-Ⅱ. Adaptive Sampling 의 한계 — 사각지대",
    "subtitle": "본 팀 4/14 소스 검증으로 첫 정량 확인",
    "findings": [
        {
            "tag": "Hook Trigger 사각지대",
            "code": "vector.c L243 · if (table_count > 2)",
            "detail": "단일 테이블 vector range query 가 hook 경로에서 배제 → 모든 query 가 PG default selectivity 1/3 로 fall-through",
        },
        {
            "tag": "Plan Replacement 부작용",
            "code": "hook 우회 시 outer query plan-tree → Sample Scan",
            "detail": "true=100,000 query 의 SELECT count(*) 가 sample 안 부분 카운트 32 로 격하",
        },
        {
            "tag": "Skew 지표 8 종 전수 negative",
            "code": "Phase 1·5 — 글로벌 4 + 로컬 4 = 8 지표",
            "detail": "Fisher γ, k-NN entropy, PCA EVR1 등 모든 지표 vs Q-error · Spearman |ρ| < 0.2 (4 지표 × 6 selectivity = 24 조합)",
        },
    ],
    "implication": "단일 테이블 vector range query (이미지 검색·추천·RAG) 는 Exqutor 가 **명시적으로 배제한** 사각지대",
}

S6_DIFFERENTIATOR = {
    "title": "3. 차별성 및 제안 연구의 중요성",
    "subtitle": "Skew-Aware Sampling — 분포 정보를 사용한 두 단계 보강",
    "lanes": [
        {
            "name": "Pivot A",
            "title": "Block-bias 제거",
            "detail": "vector.c L889 의 TABLESAMPLE SYSTEM(%f) → BERNOULLI(%f) 한 줄 교체",
            "role": "fair baseline 도구",
            "metric": "+9.6%",
            "metric_label": "s=0.500, p<0.001",
        },
        {
            "name": "Pivot C",
            "title": "Data-side k-means K=20",
            "detail": "vector.c +228 줄 native 구현 — stratum_id 사전 부여 + Horvitz-Thompson 가중 추정",
            "role": "공간 인식 sampling",
            "metric": "+1.64%",
            "metric_label": "DEEP 1M, 5-seed CI [+1.11, +2.18]",
        },
    ],
    "tagline": "두 Pivot 은 직교적 — SYSTEM × BERNOULLI × STRATIFIED 의 ablation matrix 로 각 기여 분리",
    "contribution": [
        "RQ1: 8 지표 negative 로 query-side feature 의 사전 layer 정의 불가능성을 정량 증명",
        "RQ2: KM20 stratified 가 BERNOULLI 위에서 추가 개선 — 5-seed CI 하한 양수",
        "RQ3 설계: 분포 미지 시 KM20 의 \"공간 인식 효과\" 를 Recovery Rate 프레임워크로 측정",
    ],
}

S7_RQ1 = {
    "title": "4-Ⅰ. RQ1 — Skew 지표는 Q-error 를 예측하지 못한다",
    "subtitle": "Phase 1 (글로벌) + Phase 5 (로컬) = 8 지표 전수 검증, 총 3000 측정",
    "setup": [
        ("데이터셋", "DEEP 1M subset · 96d"),
        ("쿼리", "100 query × 6 selectivity × 5 seed = 3000"),
        ("지표 (글로벌)", "Fisher γ, log-Fisher γ, P99/P50 tail ratio, Bowley skew"),
        ("지표 (로컬)", "k-NN entropy, PCA EVR1, KDE modality, NN clustering"),
    ],
    "findings": [
        "12 조합 모두 Q-error ratio ≈ 1.0 (skewed/non-skewed 그룹 차이 없음)",
        "글로벌 24 + 로컬 24 = 48 조합 모두 Spearman |ρ| < 0.2 (Cohen 1988 small-effect 미달)",
        "100 query 전부 Fisher γ < 0 (left-skewed) — 고차원 거리 집중 현상",
    ],
    "interpretation": "고차원 벡터에서 query-side feature 로 layer 를 사전 정의하는 것은 불가능 — 본 연구의 Motivation 첫 줄",
}

S8_RQ2_BERNOULLI = {
    "title": "4-Ⅱ. RQ2 (1) — BERNOULLI 가 SYSTEM 의 block-bias 를 제거",
    "subtitle": "100 query × 6 selectivity × 1 seed × 2 mode = 1200 측정 · paired Wilcoxon",
    "table_headers": ["selectivity", "SYS median", "BERN median", "diff%", "p-value", "유의"],
    "table_rows": [
        ("0.001", "2.597", "2.597",  "+0.0",  "0.596",  "—"),
        ("0.010", "1.558", "1.299",  "+20.0", "0.240",  "—"),
        ("0.050", "1.203", "1.195",  "+0.7",  "0.0009", "★★"),
        ("0.100", "1.212", "1.132",  "+7.0",  "<0.001", "★★★"),
        ("0.300", "1.210", "1.079",  "+12.0", "<0.001", "★★★"),
        ("0.500", "1.153", "1.052",  "+9.6",  "<0.001", "★★★"),
    ],
    "takeaways": [
        "4 selectivity 구간 (s=0.05~0.5) 에서 p<0.001 — block sampling bias 는 통계적으로 유의한 구조적 약점",
        "vector.c 한 줄 교체로 Exqutor 카디널리티 추정 개선 경로 확보",
        "단, 이는 Pivot C 의 fair baseline 도구이지 단독 기여가 아님",
    ],
}

S9_RQ2_KM20 = {
    "title": "4-Ⅲ. RQ2 (2) — KM20 Stratified 가 BERNOULLI 위에서 추가 개선",
    "subtitle": "5-seed 신뢰구간으로 외적 타당성 확보 · vector.c +228 줄 native 구현",
    "table_headers": ["selectivity", "5-seed 평균", "95% CI", "유의 seed"],
    "table_rows": [
        ("50%", "+1.64%", "[+1.11, +2.18]", "5/5"),
        ("30%", "+2.62%", "[+1.45, +3.80]", "5/5 (p<0.001)"),
        ("10%", "+4.19%", "[+0.72, +7.66]", "5/5 (p<0.004)"),
        ("5%",  "+1.85%", "1-seed (W5 보충)", "3/5"),
        ("1%",  "+8.93%", "1-seed (W5 보충)", "4/5"),
    ],
    "takeaways": [
        "50% / 30% / 10% 세 구간 모두 95% CI 가 0 을 포함하지 않음 — real effect 통계적 확정",
        "s=0.500 1-seed p=4.01e-05 (Bonferroni 통과) → 5-seed 재현으로 우연 가능성 배제",
        "BERNOULLI 위에서 추가 개선 — 누적 vs SYSTEM 은 +12.5% (s=0.500)",
    ],
}

S10_EXTERNAL_VALIDITY = {
    "title": "4-Ⅳ. External Validity — 3 데이터셋 교차 검증",
    "subtitle": "DEEP 1M · DEEP 8M · SIFT 1.5M — D_target 데이터셋별 재계산",
    "metrics": [
        {"label": "DEEP 1M (96d)",  "value": "+1.64%", "ci": "CI [+1.11, +2.18]", "cv": "CV 0.234", "color": "blue"},
        {"label": "DEEP 8M (96d)",  "value": "+1.76%", "ci": "CI [+0.65, +2.86]", "cv": "CV 0.234", "color": "blue"},
        {"label": "SIFT 1.5M (128d)","value": "+3.07%", "ci": "CI [+2.66, +3.48]", "cv": "CV 0.394", "color": "orange"},
    ],
    "key_findings": [
        "DEEP 1M ↔ 8M : CI 겹침 (CONSISTENT) — 8 배 규모에서 동일 효과 재현",
        "SIFT 1.5M : CI 가 DEEP 과 겹치지 않음 (~2 배 효과) — 통계적 구별",
        "쏠림도 (CV) DEEP 0.234 vs SIFT 0.394 (68% 높음) — 쏠림 ↑ ⇒ 공간 인식 가치 ↑",
    ],
    "interpretation": "데이터가 더 쏠려 있을수록 공간 인식 샘플링의 가치가 크다 — 가설이 정량 지표와 단조 관계로 재확인",
}

S10B_INTERPRETATION = {
    "title": "4-Ⅴ. 결과 해석 — 데이터 쏠림과 공간 인식 효과",
    "subtitle": "Two-Level Decomposition + 클러스터 쏠림도 (HHI / CV) 정량",
    "two_level": {
        "headline": "KM20 개선 = Level 1 (비례 배분) + Level 2 (공간 인식)",
        "rows": [
            ("s = 50%",  "+1.64%", "+2.20%",   "~0",    "비례만"),
            ("s = 30%",  "+2.62%", "+0.26%",   "+2.4%p", "Level 2"),
            ("s = 10%",  "+4.19%", "+1.74%",   "+2.5%p", "Level 2"),
            ("s = 5%",   "+1.85%", "+0.79%",   "+1.1%p", "Level 2"),
            ("s = 1%",   "+8.93%", "−10.67%",  "+19.6%p", "★ 공간 인식 단독"),
        ],
        "headers": ["selectivity", "KM20", "RANDOM20", "격차 (Level 2)", "지배 요인"],
    },
    "skew": {
        "headline": "데이터셋 쏠림도 — DEEP CV 0.234 vs SIFT CV 0.394 (68% 높음)",
        "items": [
            "SIFT 최대 클러스터 14.8 만 (기대값 7.5 만의 2 배)",
            "상위 2 클러스터가 전체 19% 점유",
            "KM20 효과 SIFT +3.07% (DEEP +1.64% 의 약 2 배)",
        ],
    },
    "tagline": "쏠림 ↑ ⇒ Level 2 (공간 인식) 단독 효과 ↑ — 본 가설 단조 관계 재확인",
}


S11_RQ3_DESIGN = {
    "title": "4-Ⅴ. RQ3 (설계) — 분포를 모를 때의 Recovery Rate 프레임워크",
    "subtitle": "3 패러다임 × 7 방법 — W5~W7 실험 예정",
    "framework": "Recovery Rate = (방법X − RANDOM20) / (KM20 − RANDOM20)",
    "paradigms": [
        {
            "name": "Offline Partition (4 방법)",
            "methods": ["A. LSH Random Hyperplane",
                        "C. Random Projection (JL)",
                        "E. Hilbert Curve",
                        "F. Mini-batch K-means"],
            "rationale": "1회 사전 처리 — KM20 와 비용 동등",
        },
        {
            "name": "Online Query-Adaptive (2 방법)",
            "methods": ["G. Distance-Shell",
                        "B. KDE-pilot (Neyman)"],
            "rationale": "Query 도착 시점 학습 — D_target 의존성 제거",
        },
        {
            "name": "Weight-based (1 방법)",
            "methods": ["H. Importance Sampling"],
            "rationale": "Sample 후 재가중 — partition 자체 불필요",
        },
    ],
    "evaluation": "DEEP 1M · 8M · SIFT 1.5M 3 데이터셋 × 5 seed × 5 selectivity 동일 조건",
    "expected": "최소 1 방법이 RR ≥ 0.5 → 분포 미지 시에도 KM20 의 절반 효과 회수",
}

S12_PROGRESS = {
    "title": "5-Ⅰ. 현재 진행 상황 (W1~W4)",
    "weeks": [
        {
            "id": "W1",  "period": "3/2~4/4",
            "status": "✓",
            "title": "Scope · 환경 세팅",
            "items": ["주제 확정 (3/3)", "Exqutor 채택 (4/3)", "서버 수령 + Docker (4/14)", "코드·데이터 수령 (4/7~)"],
        },
        {
            "id": "W2", "period": "4/11~4/15",
            "status": "✓",
            "title": "RQ1 Motivation",
            "items": ["Phase 1 가설 H1 기각 (4/14)", "Phase 5 로컬 4 지표 negative (4/15)", "Design Constraint 발견 (4/14)"],
        },
        {
            "id": "W3", "period": "4/15~4/16",
            "status": "✓",
            "title": "RQ2 Aware",
            "items": ["Phase 4 Pivot A native (4/14~15)", "Phase 6 Step 4 KM20 1-seed (4/15)", "5-seed CI · DEEP 1M/8M/SIFT (4/16)"],
        },
        {
            "id": "W4", "period": "4/17~4/28",
            "status": "▶",
            "title": "보강 + 발표",
            "items": ["Two-Level 분해 +19.6%p (4/16)", "HHI/CV 정량 (4/17)", "RQ3 7-way 설계 (4/16)", "중간보고서 + 발표 (4/28)"],
        },
    ],
    "summary": "RQ1 + RQ2 본선 + 5-seed 외적 타당성 + RQ3 설계 — 학기 중간 시점 완료",
}

S13_PLAN = {
    "title": "5-Ⅱ. 향후 계획 (W5~W10)",
    "weeks": [
        ("W5",  "4/29~5/6",  "RQ3-A Offline Partition", "Random K=20, Subspace decile, LSH 3 방법 — DEEP 1M 1-seed"),
        ("W6",  "5/7~5/13",  "RQ3-A 5-seed",            "선별된 1~2 방법 5-seed × 3 데이터셋 — Recovery Rate 산출"),
        ("W7",  "5/14~5/20", "RQ3-B + Layer K sweep",   "Online + Weight 패러다임 + K=10/20/30/50 sweep"),
        ("W8",  "5/21~5/27", "심화 + 최종발표 준비",      "per-stratum BERN 최적화, sample_size sensitivity"),
        ("W9",  "5/28~6/4",  "최종발표 + 전시회",         "5/27~29 발표, 6/5 전시회"),
        ("W10", "6/5~6/11",  "최종보고서 작성",            "RQ1 + RQ2 + RQ3 통합 + 실험 재현 가이드"),
    ],
    "deliverables": ["최종발표 PDF (5/27~29)", "전시회 포스터 (6/5)", "최종보고서 PDF (6/11)"],
}

S14_ROLES = {
    "title": "5-Ⅲ. 팀원별 역할 분담",
    "rows": [
        ("박세은", "팀장", "전체 일정 관리 · 자문 회신 정리 · 발표·보고서 총괄"),
        ("강재현", "주 발표자", "중간발표 주 발표 · 슬라이드 검수 · Q&A 사회"),
        ("조현빈", "실험·문서화", "RQ1/RQ2 실험 · vector.c native 구현 · 보고서 작성"),
        ("이동욱", "분석·작도", "통계 분석 (CI · Two-Level) · 그림 작성 · RQ3 설계"),
    ],
    "shared": "Q&A 응답 — 통계·CI 는 이동욱, 실험 디테일은 조현빈, 일정·체크포인트는 박세은 분담 (4 인 합의 후 진행)",
}

S15_THANKS = {
    "title": "감사합니다",
    "subtitle": "질문 부탁드립니다",
    "team": TEAM,
    "members": MEMBERS,
}

ALL_SLIDES = [
    S1_COVER, S2_TOC, S3_PROBLEM, S4_BACKGROUND, S5_LIMITATION, S6_DIFFERENTIATOR,
    S7_RQ1, S8_RQ2_BERNOULLI, S9_RQ2_KM20, S10_EXTERNAL_VALIDITY, S11_RQ3_DESIGN,
    S12_PROGRESS, S13_PLAN, S14_ROLES, S15_THANKS,
]


# ─────────────────────────────────────────
# Figure 매핑 — 보고서·발표에 활용 가능한 실험 결과 이미지
# ─────────────────────────────────────────
FIGURE_DIR = "/Users/hyunbin/Capstone/experiments/figures"

FIGURES = {
    # RQ1
    "vector_c": f"{FIGURE_DIR}/rq1_motivation/slide6_vector_c_snippet.png",
    "phase5_heatmap": f"{FIGURE_DIR}/rq1_motivation/figure_6_phase5_heatmap.png",
    "python_native": f"{FIGURE_DIR}/rq1_motivation/figure_5_python_native_table.png",
    # RQ2
    "phase4_scatter": f"{FIGURE_DIR}/rq1_motivation/figure_1_phase4_scatter.png",
    "phase6_box": f"{FIGURE_DIR}/rq1_motivation/figure_2_phase6_box.png",
    "layer_compare": f"{FIGURE_DIR}/rq1_motivation/figure_3_phase6_layer_compare.png",
    "phase7_heatmap": f"{FIGURE_DIR}/rq1_motivation/figure_4_phase7_heatmap.png",
    "selectivity_grad": f"{FIGURE_DIR}/rq2_aware/figure_7_selectivity_gradient.png",
    "cross_dataset": f"{FIGURE_DIR}/rq2_aware/figure_8_cross_dataset_bar.png",
    "two_level": f"{FIGURE_DIR}/rq2_aware/figure_9_two_level_decomposition.png",
    "cluster_skew": f"{FIGURE_DIR}/rq2_aware/figure_10_cluster_skew.png",
}

FIGURE_CAPTIONS = {
    "vector_c": "vector.c L243 — table_count > 2 hook trigger 사각지대",
    "phase5_heatmap": "Phase 5 — 로컬 4 지표 × 6 selectivity = 24 조합 모두 |ρ| < 0.2",
    "phase4_scatter": "Phase 4 — SYS vs BERN paired Q-error 4 panel (s=0.05/0.10/0.30/0.50)",
    "phase6_box": "Phase 6 Step 4 — BERNOULLI vs STRATIFIED (KM20) 100 query boxplot",
    "cross_dataset": "외적 타당성 — DEEP 1M / 8M / SIFT 1.5M, KM20 s=0.500 효과 95% CI",
    "two_level": "Two-Level Decomposition — Level 1 (비례) + Level 2 (공간 인식) 분해",
    "cluster_skew": "클러스터 쏠림도 — DEEP CV 0.234 vs SIFT CV 0.394 (HHI 정량)",
    "selectivity_grad": "selectivity 별 KM20 효과 gradient — 좁은 selectivity ↑ 효과 ↑",
    "layer_compare": "Layer 비교 (PCA decile / KM10 / KM20) — KM20 가 가장 넓은 적용 범위",
    "phase7_heatmap": "Phase 7 — DEEP 8M / SIFT 1.5M boundary 분석 heatmap",
    "python_native": "Python 재구현 vs Exqutor native — Q-error 측정 동치성 검증",
}
